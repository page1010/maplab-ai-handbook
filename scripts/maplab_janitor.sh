#!/bin/bash
# maplab_janitor.sh — 定期清理: 回收 idle agent session + 關 agent 殘留分頁(best-effort)
# 與 mem_watchdog 共用鎖、fail-safe、可停用、log 每次動作。
# 守則: 不殺 Owner app(Claude 桌面/Chrome/其他)、不殺正在跑或近期 session、不關 Owner 分頁。
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# ---- 參數(可調) ----
SESSION_MIN_AGE_HRS=6     # 只回收「存在 > N 小時」的 idle agent session(保護今天新開的)
SESSION_MAX_CPU=3.0       # cpu 高於此=在跑, 不殺
TAB_CLEAN=1              # 1=嘗試關殘留分頁(需 Automation 權限, 失敗自動略過)

LOG=/Users/pagemacmini/maplab-ai-handbook/logs/janitor.log
mkdir -p "$(dirname "$LOG")" 2>/dev/null
ts(){ date "+%F %T"; }
logline(){ echo "$(ts),$*" >> "$LOG"; }

# ---- 共用鎖(與 watchdog 互斥, mkdir 原子鎖) ----
LOCKDIR=/tmp/maplab_mem.lock.d
if [ -d "$LOCKDIR" ]; then find "$LOCKDIR" -maxdepth 0 -mmin +5 -exec rmdir {} \; 2>/dev/null; fi
if ! mkdir "$LOCKDIR" 2>/dev/null; then logline "SKIP,reason=locked_by_watchdog"; exit 0; fi
trap 'rmdir "$LOCKDIR" 2>/dev/null' EXIT

# ---- A. 回收 idle agent session (claude/node) ----
# 保護自己的 claude 祖先, 不誤殺救援/當前 session
p=$$; PROTECT=""
for k in $(seq 1 12); do
  pp=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d " "); [ -z "$pp" ] && break
  uc=$(ps -o ucomm= -p "$pp" 2>/dev/null | tr -d " ")
  [ "$uc" = "claude" ] && { PROTECT="$pp"; break; }; p="$pp"
done

# 目標: ucomm=claude, 存在>=N小時, cpu<門檻, 排除 PROTECT
reclaim=$(ps -Ao pid,pcpu,etime,ucomm | awk -v pr="$PROTECT" -v mc="$SESSION_MAX_CPU" -v mh="$SESSION_MIN_AGE_HRS" '
  $4=="claude" && $1!=pr && ($2+0)<mc {
    et=$3; d=0; h=0;
    if (et ~ /-/){ split(et,a,"-"); d=a[1]; et=a[2] }
    n=split(et,b,":"); if(n==3) h=b[1];
    if (d*24+h >= mh) print $1
  }')
cnt=0
for pid in $reclaim; do kill -TERM "$pid" 2>/dev/null && cnt=$((cnt+1)); done
if [ "$cnt" -gt 0 ]; then
  sleep 4
  for pid in $reclaim; do kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" 2>/dev/null; done
  logline "RECLAIM_SESSIONS,count=$cnt,pids=$(echo $reclaim | tr ' ' '|')"
else
  logline "RECLAIM_SESSIONS,count=0"
fi

# ---- B. 關 agent 殘留分頁(best-effort; 只關明確殘留樣式, 白名單一律保留) ----
if [ "$TAB_CLEAN" = "1" ]; then
  APPLE=/Users/pagemacmini/maplab-ai-handbook/scripts/janitor_close_tabs.applescript
  if [ -f "$APPLE" ]; then
    out=$(osascript "$APPLE" 2>/dev/null); rc=$?
    if [ $rc -ne 0 ]; then logline "TAB_CLEAN,skipped=need_automation_permission_or_chrome_closed";
    else logline "TAB_CLEAN,closed=${out:-0}"; fi
  fi
fi
exit 0
