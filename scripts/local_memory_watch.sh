#!/usr/bin/env bash
# local_memory_watch.sh — 本機記憶體健康巡檢（狀態機版）
# 由 launchd 每 2 小時觸發；狀態轉換時推 Telegram，其餘靜默寫 log
# Log: state/memory_watch.log（保留 7 天）
# State: state/.memory_watch_state（記錄目前壓力狀態與最近推播時間）
#
# 2026-08-27 通知治理改版：
#   - 舊版每輪超標就推播（raw free 常年 0% → 每 2 小時洗版一次，且字面嚇人）。
#   - 改為狀態機：進入壓力狀態發一則、離開發一則；持續壓力中最多每 2 小時一則
#     並標註「已持續 N 小時」。
#   - 門檻判定改用「可用記憶體 avail = free+inactive+speculative+purgeable」，
#     與 mem_watchdog.sh 同口徑；raw free 只作參考附註（macOS 把閒置 RAM 當
#     快取，raw free 趨近 0 屬正常，不再拿它當警報主詞嚇人）。
#   - 同一輪多項異常合併成一則訊息，不再分開連發。
#
# 檢查項：
#   1. Ollama 啟動中：avail<12% → 壓力
#   2. 無 Ollama：avail<20% → 壓力
#   3. swap free<5% 且 avail<30% → 壓力（雙重壓力）
#   4. Codex orphan：超過 2 個 codex 程序 → 壓力
#   5. 全 OK → log 一行 ✅ 靜默

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$REPO_ROOT/state/memory_watch.log"
STATE_FILE="$REPO_ROOT/state/.memory_watch_state"
NOTIFY="$REPO_ROOT/scripts/notify_owner.sh"
MAX_LOG_DAYS=7
REALERT_SEC=7200   # 持續壓力中，兩次推播至少間隔 2 小時

ts()  { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" >> "$LOG_FILE"; }

# 保留 MAX_LOG_DAYS 天 log
trim_log() {
    [[ -f "$LOG_FILE" ]] || return
    local cutoff
    cutoff=$(python3 -c "import datetime; print((datetime.date.today() - datetime.timedelta(days=$MAX_LOG_DAYS)).strftime('%Y-%m-%d'))")
    python3 -c "
cutoff = '$cutoff'
lines = open('$LOG_FILE').readlines()
kept  = [l for l in lines if (len(l) > 10 and l[1:11] >= cutoff) or not l.startswith('[')]
open('$LOG_FILE', 'w').writelines(kept)
" 2>/dev/null || true
}

# 2026-09-04 Owner 裁決（msg 4642）：記憶體診斷屬系統自言自語，不進 Owner 線。
# 原 notify() 改寫 system_journal.md；朔源翻記事本，狀態機邏輯照舊。
JOURNAL="$REPO_ROOT/state/system_journal.md"
notify() {
    printf '[%s] [memory-watch] %s\n' "$(ts)" "$1" >> "$JOURNAL"
}

# ── 讀取記憶體統計（macOS vm_stat）─────────────────────────
PAGE_SIZE=$(pagesize 2>/dev/null || echo 16384)
TOTAL_BYTES=$(sysctl -n hw.memsize)
TOTAL_MB=$(( TOTAL_BYTES / 1024 / 1024 ))

FREE_PAGES=$(vm_stat | awk '/Pages free:/{gsub(/\./,"",$NF); print $NF+0}')
SPEC_PAGES=$(vm_stat | awk '/Pages speculative:/{gsub(/\./,"",$NF); print $NF+0}')
INACT_PAGES=$(vm_stat | awk '/Pages inactive:/{gsub(/\./,"",$NF); print $NF+0}')
PURGE_PAGES=$(vm_stat | awk '/Pages purgeable:/{gsub(/\./,"",$NF); print $NF+0}')

RAWFREE_MB=$(( (FREE_PAGES + SPEC_PAGES) * PAGE_SIZE / 1024 / 1024 ))
RAWFREE_PCT=$(( RAWFREE_MB * 100 / TOTAL_MB ))
AVAIL_MB=$(( (FREE_PAGES + SPEC_PAGES + INACT_PAGES + PURGE_PAGES) * PAGE_SIZE / 1024 / 1024 ))
AVAIL_PCT=$(( AVAIL_MB * 100 / TOTAL_MB ))

# Swap（sysctl vm.swapusage: total = 11264.00M  used = ...  free = 1479.44M）
SWAP_FREE_MB=$(sysctl vm.swapusage | sed 's/.*free = //' | awk -F'M' '{printf "%d", $1}')
SWAP_TOTAL_MB=$(sysctl vm.swapusage | sed 's/.*total = //' | awk -F'M' '{printf "%d", $1}')
SWAP_FREE_PCT=0
if [[ $SWAP_TOTAL_MB -gt 0 ]]; then
    SWAP_FREE_PCT=$(( SWAP_FREE_MB * 100 / SWAP_TOTAL_MB ))
fi

# ── Ollama 是否啟動 ──────────────────────────────────────
OLLAMA_RUNNING=false
pgrep -x ollama &>/dev/null && OLLAMA_RUNNING=true

log "check avail=${AVAIL_MB}MB(${AVAIL_PCT}%) raw_free=${RAWFREE_MB}MB(${RAWFREE_PCT}%) swap_free=${SWAP_FREE_MB}MB(${SWAP_FREE_PCT}%) ollama=${OLLAMA_RUNNING} total=${TOTAL_MB}MB"

# ── 判定本輪壓力原因（合併為一則）────────────────────────
REASONS=()

if [[ "$OLLAMA_RUNNING" == "true" ]]; then
    if [[ $AVAIL_PCT -lt 12 ]]; then
        REASONS+=("可用記憶體 ${AVAIL_PCT}%（Ollama 啟動中門檻 12%，${AVAIL_MB}MB/${TOTAL_MB}MB）")
    fi
else
    if [[ $AVAIL_PCT -lt 20 ]]; then
        REASONS+=("可用記憶體 ${AVAIL_PCT}%（無 Ollama 門檻 20%，${AVAIL_MB}MB/${TOTAL_MB}MB）")
    fi
fi

if [[ $SWAP_FREE_PCT -lt 5 && $AVAIL_PCT -lt 30 ]]; then
    REASONS+=("Swap 剩 ${SWAP_FREE_PCT}%（${SWAP_FREE_MB}MB/${SWAP_TOTAL_MB}MB）+ 可用記憶體 ${AVAIL_PCT}% — 雙重壓力")
fi

CODEX_COUNT=$(pgrep -c -i "codex" 2>/dev/null || echo 0)
if [[ $CODEX_COUNT -gt 2 ]]; then
    CODEX_PIDS=$(pgrep -i "codex" 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo '?')
    REASONS+=("Codex orphan：${CODEX_COUNT} 個程序（pids: ${CODEX_PIDS}）")
fi

NEW_STATE="OK"
[[ ${#REASONS[@]} -gt 0 ]] && NEW_STATE="PRESSURE"

# ── 讀上次狀態 ──────────────────────────────────────────
# STATE_FILE 格式：STATE|entered_epoch|last_notify_epoch
PREV_STATE="OK"; ENTERED_EPOCH=0; LAST_NOTIFY_EPOCH=0
if [[ -f "$STATE_FILE" ]]; then
    IFS='|' read -r PREV_STATE ENTERED_EPOCH LAST_NOTIFY_EPOCH < "$STATE_FILE" || true
    PREV_STATE="${PREV_STATE:-OK}"
    ENTERED_EPOCH="${ENTERED_EPOCH:-0}"
    LAST_NOTIFY_EPOCH="${LAST_NOTIFY_EPOCH:-0}"
fi
NOW_EPOCH=$(date +%s)

REASON_TEXT=""
if [[ ${#REASONS[@]} -gt 0 ]]; then
    REASON_TEXT=$(printf '• %s\n' "${REASONS[@]}")
fi
FOOTNOTE="（raw free ${RAWFREE_PCT}% 僅供參考：macOS 把閒置 RAM 當快取，raw free 低屬正常）"

# ── 狀態機：只在轉換或持續超過 REALERT_SEC 才推播 ─────────
if [[ "$NEW_STATE" == "PRESSURE" && "$PREV_STATE" != "PRESSURE" ]]; then
    # 進入壓力狀態 → 發一則
    notify "🖥️ [memory-watch] ⚠️ 進入記憶體壓力狀態：
${REASON_TEXT}
${FOOTNOTE}"
    log "⚠️  ENTER PRESSURE: ${REASONS[*]}"
    echo "PRESSURE|${NOW_EPOCH}|${NOW_EPOCH}" > "$STATE_FILE"
elif [[ "$NEW_STATE" == "PRESSURE" && "$PREV_STATE" == "PRESSURE" ]]; then
    # 持續壓力 → 最多每 REALERT_SEC 一則
    log "⚠️  STILL PRESSURE: ${REASONS[*]}"
    if [[ $(( NOW_EPOCH - LAST_NOTIFY_EPOCH )) -ge $REALERT_SEC ]]; then
        DUR_H=$(( (NOW_EPOCH - ENTERED_EPOCH) / 3600 ))
        notify "🖥️ [memory-watch] ⚠️ 記憶體壓力持續中（已持續約 ${DUR_H} 小時）：
${REASON_TEXT}
${FOOTNOTE}"
        echo "PRESSURE|${ENTERED_EPOCH}|${NOW_EPOCH}" > "$STATE_FILE"
    else
        echo "PRESSURE|${ENTERED_EPOCH}|${LAST_NOTIFY_EPOCH}" > "$STATE_FILE"
    fi
elif [[ "$NEW_STATE" == "OK" && "$PREV_STATE" == "PRESSURE" ]]; then
    # 離開壓力狀態 → 發一則
    DUR_H=$(( (NOW_EPOCH - ENTERED_EPOCH) / 3600 ))
    notify "🖥️ [memory-watch] ✅ 記憶體壓力解除（歷時約 ${DUR_H} 小時）：可用記憶體 ${AVAIL_MB}MB（${AVAIL_PCT}%），swap 剩 ${SWAP_FREE_PCT}%。"
    log "✅ EXIT PRESSURE (dur=${DUR_H}h)"
    echo "OK|0|${NOW_EPOCH}" > "$STATE_FILE"
else
    log "✅ OK"
    echo "OK|0|${LAST_NOTIFY_EPOCH}" > "$STATE_FILE"
fi

trim_log
