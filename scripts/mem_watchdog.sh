#!/bin/bash
# mem_watchdog.sh — MAPLAB 純本機記憶體守門狗 (不經 Claude/API)
# 每 4 分由 launchd 觸發: 接近耗盡就「只卸載 Ollama/llama-server」釋放記憶體。
# 目的: 即使 API 斷、Claude 跑不動, 這支照樣自動解壓 → 免核心 reap 網路 daemon → 免重開機。
# 守則: 只動 Ollama/llama-server, 絕不碰 Owner 其他 app。可回退: launchctl bootout 卸載本 agent。
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# --- 門檻 (保守: 只在接近耗盡才動) ---
AVAIL_MIN_MB=1500      # 可用記憶體低於此 → 危險
SWAPFREE_MIN_MB=700    # swap 剩餘低於此 → 危險
COOLDOWN_SEC=600       # 兩次自動釋放至少間隔 10 分, 避免抖動

# 內接碟優先(launchd 背景 agent 對 /Volumes 外接碟常因 TCC 無寫入權;且危機時外接碟可能卸載)
# 因此以「實際可寫」為準: 先試內接, 內接必可寫; 若外接也可寫則額外鏡射一份。
LOG_INTERNAL="/Users/pagemacmini/maplab-ai-handbook/logs/mem-watchdog.log"
LOG_EXTERNAL="/Volumes/MacExternal/MAPLAB_WORKSPACE/state/mem-watchdog.log"
STATE="/Users/pagemacmini/maplab-ai-handbook/state/.mem_watchdog_last_action"
mkdir -p "$(dirname "$LOG_INTERNAL")" "$(dirname "$STATE")" 2>/dev/null
LOG="$LOG_INTERNAL"
MIRROR=""
if ( : >> "$LOG_EXTERNAL" ) 2>/dev/null; then MIRROR="$LOG_EXTERNAL"; fi
ts(){ date "+%F %T"; }
logline(){ local L="$(ts),$*"; echo "$L" >> "$LOG"; [ -n "$MIRROR" ] && echo "$L" >> "$MIRROR" 2>/dev/null; return 0; }

# 與 janitor 共用鎖(mkdir 原子鎖, macOS 無 flock CLI)。拿不到就跳過本輪(4 分後再來)。
LOCKDIR=/tmp/maplab_mem.lock.d
# 清除陳舊鎖(持有者崩潰): 超過 5 分鐘的鎖視為失效
if [ -d "$LOCKDIR" ]; then
  find "$LOCKDIR" -maxdepth 0 -mmin +5 -exec rmdir {} \; 2>/dev/null
fi
if ! mkdir "$LOCKDIR" 2>/dev/null; then logline "SKIP,reason=locked_by_janitor"; exit 0; fi
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT

read_avail_mb(){
  local PS f i s p
  PS=$(sysctl -n hw.pagesize)
  eval "$(vm_stat | awk -F':' '
    /Pages free/{gsub(/[^0-9]/,"",$2); f=$2}
    /Pages inactive/{gsub(/[^0-9]/,"",$2); i=$2}
    /Pages speculative/{gsub(/[^0-9]/,"",$2); s=$2}
    /Pages purgeable/{gsub(/[^0-9]/,"",$2); p=$2}
    END{printf "f=%d;i=%d;s=%d;p=%d", f,i,s,p}')"
  echo $(( (f+i+s+p)*PS/1048576 ))
}
read_swapfree_mb(){
  sysctl -n vm.swapusage | awk '{for(k=1;k<=NF;k++) if($k=="free"){v=$(k+2); gsub(/M/,"",v); print int(v)}}'
}

AVAIL_MB=$(read_avail_mb)
SWAPFREE_MB=$(read_swapfree_mb); SWAPFREE_MB=${SWAPFREE_MB:-9999}

# 失效保護: 讀數異常(<=0 或空)時絕不釋放, 只記錄錯誤後退出
if ! [ "${AVAIL_MB:-0}" -gt 0 ] 2>/dev/null; then
  logline "ERROR,avail_mb=${AVAIL_MB:-NA},swapfree_mb=${SWAPFREE_MB:-NA},action=none_bad_reading"
  exit 0
fi

DANGER=0
[ "$AVAIL_MB" -lt "$AVAIL_MIN_MB" ] && DANGER=1
[ "$SWAPFREE_MB" -lt "$SWAPFREE_MIN_MB" ] && DANGER=1

if [ "$DANGER" -eq 0 ]; then
  logline "OK,avail_mb=$AVAIL_MB,swapfree_mb=$SWAPFREE_MB,action=none"
  tail -n 5000 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG" 2>/dev/null
  exit 0
fi

# --- 危險: cooldown 檢查 ---
NOW=$(date +%s); LAST=0; [ -f "$STATE" ] && LAST=$(cat "$STATE" 2>/dev/null || echo 0)
if [ $((NOW-LAST)) -lt "$COOLDOWN_SEC" ]; then
  logline "DANGER,avail_mb=$AVAIL_MB,swapfree_mb=$SWAPFREE_MB,action=cooldown_skip"
  exit 0
fi

# --- 釋放記憶體: 只動 Ollama / llama-server ---
FREED=""
if command -v ollama >/dev/null 2>&1; then
  ollama ps 2>/dev/null | awk 'NR>1 && NF{print $1}' | while read -r m; do ollama stop "$m" 2>/dev/null; done
  FREED="ollama_stop"
fi
if pgrep -f "llama-server" >/dev/null 2>&1; then
  pkill -f "llama-server" 2>/dev/null && FREED="${FREED};pkill_llama-server"
fi
# purge 選配: 需 sudo, 無免密碼就跳過並記錄 (不 hang, 無 TTY 會直接失敗)
if sudo -n true 2>/dev/null; then sudo -n purge 2>/dev/null && FREED="${FREED};purge"; else FREED="${FREED};purge_skipped_need_sudo"; fi

echo "$NOW" > "$STATE"
sleep 3
AVAIL2_MB=$(read_avail_mb)
logline "ACTION,avail_before_mb=$AVAIL_MB,swapfree_mb=$SWAPFREE_MB,freed=${FREED},avail_after_mb=$AVAIL2_MB"
tail -n 5000 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG" 2>/dev/null
exit 0
