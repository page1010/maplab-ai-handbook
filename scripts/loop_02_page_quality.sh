#!/usr/bin/env bash
# Loop-02: 程式化頁面品質關卡（A2 Search Console 接入版）
# 每週執行，抓低質頁產出 A2 優化待辦清單
# Usage: bash scripts/loop_02_page_quality.sh
#
# 依賴：Search Console MCP（maplab.com.tw 屬性需已授權）
# 若 MCP 不可用 → 輸出指引讓 A2 手動執行
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$REPO/state"
REPORT="$STATE_DIR/loop_02_page_quality_report.md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

echo "【Loop-02 頁面品質關卡】$TIMESTAMP"
mkdir -p "$STATE_DIR"

# GOAL 定義
GOAL_CTR_MIN=0.02        # 2%
GOAL_POSITION_MAX=20
IMPRESSION_MIN=100       # 樣本數門檻

# 寫報告骨架（MCP 呼叫由 Claude Code 補充）
{
  echo "# Loop-02 頁面品質報告"
  echo "更新：$TIMESTAMP"
  echo ""
  echo "## GOAL"
  echo "maplab.com.tw 所有文章 CTR ≥ ${GOAL_CTR_MIN} 且 Position ≤ ${GOAL_POSITION_MAX}"
  echo ""
  echo "## 執行步驟（Claude Code / MCP 呼叫）"
  echo ""
  echo "請用以下 MCP 呼叫抓數據："
  echo '```'
  echo "mcp__google-search-console__search_analytics"
  echo "  siteUrl: sc-domain:maplab.com.tw"
  echo "  dimensions: [page]"
  echo "  startDate: 28daysAgo"
  echo "  endDate: today"
  echo "  rowLimit: 100"
  echo '```'
  echo ""
  echo "## 低質頁篩選條件"
  echo "| 條件 | 閾值 | 優先級 |"
  echo "|------|------|-------|"
  echo "| Impression > ${IMPRESSION_MIN} AND CTR < 1% | 有曝光但沒人點 | 🔴 最優先 |"
  echo "| Impression > ${IMPRESSION_MIN} AND CTR 1-2% AND Position 10-20 | 改標題可進步 | 🟡 次優先 |"
  echo "| Position 21-30 | 接近首頁但未入 | 🟢 觀察 |"
  echo ""
  echo "## 待 MCP 執行後填入結果"
  echo "（此檔由 loop_02_page_quality.sh 建立骨架，Claude Code 填入實際數據）"
  echo ""
  echo "---"
  echo "下次執行：$(date -v+7d "+%Y-%m-%d") 09:00"
} > "$REPORT"

echo "報告骨架已寫入：$REPORT"
echo "下一步：Claude Code 呼叫 Search Console MCP 填入實際數據"
echo ""
echo "快速呼叫提示（貼到 Claude Code）："
echo "  用 Search Console MCP 執行 Loop-02，讀 maplab.com.tw 過去 28 天頁面數據，填入 $REPORT"
