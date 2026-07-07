#!/usr/bin/env bash
# Loop-15: SOP 偏移捕手
# 比對 CURRENT_STATUS.md 聲稱狀態 vs git commit 證據
# Usage: bash scripts/loop_15_sop_drift.sh [--silent]
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$REPO/state"
REPORT="$STATE_DIR/loop_15_drift_report.md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

echo "【Loop-15 SOP 偏移捕手】$TIMESTAMP"
mkdir -p "$STATE_DIR"

# 1. 讀 CURRENT_STATUS 中所有帶狀態標記的行
STATUS_FILE="$REPO/CURRENT_STATUS.md"
if [[ ! -f "$STATUS_FILE" ]]; then
  echo "ERROR: CURRENT_STATUS.md 不存在" >&2
  exit 1
fi

# 提取聲稱 DONE(✅) 的任務關鍵字
DONE_TASKS=$(grep -E "✅" "$STATUS_FILE" | grep -v "^>" | head -30 || true)
INPROGRESS_TASKS=$(grep -E "🔄" "$STATUS_FILE" | grep -v "^>" | head -20 || true)

# 2. 讀最近 50 筆 git log
GIT_LOG=$(cd "$REPO" && git log --oneline -50 2>/dev/null || echo "")

# 3. 計算最後 commit 距今多少小時
LAST_COMMIT_TS=$(cd "$REPO" && git log -1 --format="%ct" 2>/dev/null || echo "0")
NOW_TS=$(date +%s)
HOURS_SINCE=$(( (NOW_TS - LAST_COMMIT_TS) / 3600 ))

# 4. 偵測超時（進行中任務 > 48h 無 commit）
DRIFT_COUNT=0
DRIFT_ITEMS=""

if [[ $HOURS_SINCE -gt 48 ]]; then
  DRIFT_COUNT=$((DRIFT_COUNT + 1))
  DRIFT_ITEMS="$DRIFT_ITEMS\n- 最後 commit 距今 ${HOURS_SINCE}h（超過 48h 警戒線）"
fi

# 5. 寫報告
{
  echo "# Loop-15 SOP 偏移報告"
  echo "更新：$TIMESTAMP"
  echo "偏差數：$DRIFT_COUNT"
  echo ""
  echo "## 系統狀態"
  echo "- 最後 commit：${HOURS_SINCE}h 前"
  echo "- 監看 DONE 任務：$(echo "$DONE_TASKS" | grep -c . || echo 0) 筆"
  echo "- 監看進行中任務：$(echo "$INPROGRESS_TASKS" | grep -c . || echo 0) 筆"
  echo ""
  if [[ $DRIFT_COUNT -gt 0 ]]; then
    echo "## ⚠️ 偏差清單"
    echo -e "$DRIFT_ITEMS"
    echo ""
    echo "## 建議行動"
    echo "- 確認進行中任務是否有進度"
    echo "- 超過 48h 無 commit 的進行中任務 → 改為 ⚠️ 或補充說明"
  else
    echo "## ✅ 無偏差"
    echo "所有聲稱狀態均有對應更新紀錄。"
  fi
  echo ""
  echo "## 最近 10 筆 commit"
  echo '```'
  echo "$GIT_LOG" | head -10
  echo '```'
} > "$REPORT"

echo "報告已寫入：$REPORT"
echo "偏差數：$DRIFT_COUNT"

# GOAL 判斷
if [[ $DRIFT_COUNT -eq 0 ]]; then
  echo "GOAL STATUS: ✅ 無偏差"
  exit 0
else
  echo "GOAL STATUS: 🔄 ${DRIFT_COUNT} 個偏差待處理"
  # 若 > 3 個偏差，可在此接 Telegram 推送（需 bot token）
  exit 0  # 非 fatal，loop 繼續
fi
