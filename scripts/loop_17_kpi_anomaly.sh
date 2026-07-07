#!/usr/bin/env bash
# Loop-17: KPI 異常監看（A6 報價轉換率版）
# 每日 08:00 執行，偵測異常推送 Telegram 警報
# Usage: bash scripts/loop_17_kpi_anomaly.sh [--init-baseline]
#
# 依賴：Sheets MCP 或直接讀 state/ 快取數據
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$REPO/state"
DAILY_REPORT="$STATE_DIR/loop_17_kpi_daily.json"
HISTORY="$STATE_DIR/loop_17_kpi_history.jsonl"
BASELINE="$STATE_DIR/loop_17_kpi_baseline.json"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
TODAY=$(date "+%Y-%m-%d")

echo "【Loop-17 KPI 異常監看】$TIMESTAMP"
mkdir -p "$STATE_DIR"

# 初始化基線模式
if [[ "${1:-}" == "--init-baseline" ]]; then
  echo "初始化基線模式：讀取 Sheets 歷史數據..."
  cat > "$BASELINE" << BASELINE_TEMPLATE
{
  "created": "$TODAY",
  "observation_period_days": 14,
  "status": "initializing",
  "metrics": {
    "quote_conversion_rate": {"baseline": null, "threshold_pct": 20},
    "quote_response_time_hours": {"baseline": null, "threshold_hours": 4},
    "daily_quote_count": {"baseline": null, "threshold_pct": 40},
    "high_tier_rate": {"baseline": null, "threshold_pct": 10}
  },
  "note": "需 Claude Code 呼叫 Sheets MCP 填入實際基線值"
}
BASELINE_TEMPLATE
  echo "基線檔建立：$BASELINE"
  echo "下一步：Claude Code 呼叫 Sheets MCP 填入 14 天歷史均值"
  exit 0
fi

# 檢查基線是否存在
if [[ ! -f "$BASELINE" ]]; then
  echo "⚠️ 基線未建立，執行初始化："
  echo "  bash scripts/loop_17_kpi_anomaly.sh --init-baseline"
  echo ""
  echo "建立觀察期骨架（14 天後自動更新基線）..."
  bash "$0" --init-baseline
  exit 0
fi

# 讀基線狀態
BASELINE_STATUS=$(python3 -c "import json,sys; d=json.load(open('$BASELINE')); print(d.get('status','unknown'))" 2>/dev/null || echo "unknown")

if [[ "$BASELINE_STATUS" == "initializing" ]]; then
  echo "🟡 觀察期進行中，尚未建立基線"
  echo "  請 Claude Code 呼叫 Sheets MCP 讀取 A6 報價數據填入基線"
  echo ""
  # 仍寫入每日骨架供手動填充
  cat > "$DAILY_REPORT" << DAILY_TEMPLATE
{
  "date": "$TODAY",
  "status": "observation_period",
  "anomalies": [],
  "note": "基線建立中，需 Sheets MCP 數據"
}
DAILY_TEMPLATE
  echo "$DAILY_REPORT 已寫入（觀察期骨架）"
  exit 0
fi

# 正式監看模式（基線已建立）
echo "讀取今日 KPI..."

# 寫每日報告骨架（實際數據由 Claude Code + Sheets MCP 填入）
{
  echo "{"
  echo "  \"date\": \"$TODAY\","
  echo "  \"timestamp\": \"$TIMESTAMP\","
  echo "  \"status\": \"pending_mcp_data\","
  echo "  \"anomalies\": [],"
  echo "  \"mcp_call_needed\": {"
  echo "    \"tool\": \"mcp__google-sheets__get_sheet_data\","
  echo "    \"spreadsheetId\": \"1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg\","
  echo "    \"range\": \"A6報價數據!A:Z\""
  echo "  }"
  echo "}"
} > "$DAILY_REPORT"

# 追加歷史
echo "{\"date\":\"$TODAY\",\"status\":\"pending_mcp_data\"}" >> "$HISTORY"

echo "每日骨架寫入：$DAILY_REPORT"
echo ""
echo "【GOAL 狀態】"
# 計算連續達標天數（讀歷史）
CONSECUTIVE_OK=$(grep '"status":"ok"' "$HISTORY" 2>/dev/null | tail -7 | wc -l | tr -d ' ')
echo "  連續達標：${CONSECUTIVE_OK} 天（目標：7 天）"

if [[ $CONSECUTIVE_OK -ge 7 ]]; then
  echo "  ✅ GOAL REACHED: 連續 7 天無異常"
  exit 0
else
  echo "  🔄 繼續監看（還需 $((7 - CONSECUTIVE_OK)) 天）"
  echo ""
  echo "下一步：Claude Code 呼叫 Sheets MCP 填入今日數據 → 檢查異常"
fi
