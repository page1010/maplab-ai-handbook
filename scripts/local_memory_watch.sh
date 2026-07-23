#!/usr/bin/env bash
# local_memory_watch.sh — 本機記憶體健康巡檢（5 項檢查）
# 由 launchd 每 2 小時觸發；超標時推 Telegram，正常時靜默寫 log
# Log: state/memory_watch.log（保留 7 天）
#
# 五項檢查：
#   1. Ollama 去抖 free≥12%：Ollama 啟動中且 free≥12% → 靜默（正常）
#   2. 非 Ollama free<20%：Ollama 未啟動且 free<20% → 警告
#   3. swap free<5% 且 free<30% → 警告（雙重壓力）
#   4. Codex orphan：超過 2 個 codex 程序 → 警告
#   5. 綜合狀態：四項全 OK → log 一行 ✅ 靜默

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$REPO_ROOT/state/memory_watch.log"
NOTIFY="$REPO_ROOT/scripts/notify_owner.sh"
MAX_LOG_DAYS=7

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

warn() {
    local msg="$1"
    log "⚠️  WARN: $msg"
    bash "$NOTIFY" "🖥️ [memory-watch] ⚠️ $msg" 2>/dev/null \
        || log "NOTIFY_FAILED（Telegram 推播失敗）"
}

# ── 讀取記憶體統計（macOS vm_stat，page size 16 KB）──────
PAGE_SIZE=$(pagesize 2>/dev/null || echo 16384)
TOTAL_BYTES=$(sysctl -n hw.memsize)
TOTAL_MB=$(( TOTAL_BYTES / 1024 / 1024 ))

FREE_PAGES=$(vm_stat | awk '/Pages free:/{gsub(/\./,"",$NF); print $NF+0}')
SPEC_PAGES=$(vm_stat | awk '/Pages speculative:/{gsub(/\./,"",$NF); print $NF+0}')
FREE_MB=$(( (FREE_PAGES + SPEC_PAGES) * PAGE_SIZE / 1024 / 1024 ))
FREE_PCT=$(( FREE_MB * 100 / TOTAL_MB ))

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

log "check free=${FREE_MB}MB(${FREE_PCT}%) swap_free=${SWAP_FREE_MB}MB(${SWAP_FREE_PCT}%) ollama=${OLLAMA_RUNNING} total=${TOTAL_MB}MB"

WARN=false

# 檢查 1 & 2：Ollama 去抖 / 非 Ollama 門檻
if [[ "$OLLAMA_RUNNING" == "true" ]]; then
    if [[ $FREE_PCT -lt 12 ]]; then
        warn "RAM ${FREE_PCT}% free（Ollama 啟動中門檻 12%，${FREE_MB}MB/${TOTAL_MB}MB）"
        WARN=true
    fi
else
    if [[ $FREE_PCT -lt 20 ]]; then
        warn "RAM ${FREE_PCT}% free（無 Ollama 門檻 20%，${FREE_MB}MB/${TOTAL_MB}MB）"
        WARN=true
    fi
fi

# 檢查 3：Swap 壓力 + RAM 壓力
if [[ $SWAP_FREE_PCT -lt 5 && $FREE_PCT -lt 30 ]]; then
    warn "Swap 剩 ${SWAP_FREE_PCT}%（${SWAP_FREE_MB}MB/${SWAP_TOTAL_MB}MB）+ RAM free ${FREE_PCT}% — 雙重壓力"
    WARN=true
fi

# 檢查 4：Codex orphan
CODEX_COUNT=$(pgrep -c -i "codex" 2>/dev/null || echo 0)
if [[ $CODEX_COUNT -gt 2 ]]; then
    CODEX_PIDS=$(pgrep -i "codex" 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo '?')
    warn "Codex orphan：${CODEX_COUNT} 個程序（pids: ${CODEX_PIDS}）"
    WARN=true
fi

# 檢查 5：全 OK
if [[ "$WARN" == "false" ]]; then
    log "✅ OK"
fi

trim_log
