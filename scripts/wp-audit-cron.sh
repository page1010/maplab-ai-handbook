#!/bin/bash
# 每週執行的全站 WP 稽核，結果寫進 data/wp-audit-log/
# 建議排程：cron 0 9 * * 1（每週一上午 9 點）
DATE=$(date +%Y-%m-%d)
LOG_DIR="data/wp-audit-log"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$DATE.md"

echo "# WP 稽核報告 $DATE" > "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "執行時間：$(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "\`\`\`" >> "$LOG_FILE"

bash "$(dirname "$0")/wp-audit.sh" --all >> "$LOG_FILE" 2>&1

echo "\`\`\`" >> "$LOG_FILE"

# 如果有 FAIL，加提示
if grep -q "❌ FAIL" "$LOG_FILE"; then
  echo "" >> "$LOG_FILE"
  echo "⚠️ 發現違規文章，請建立 handoff/feedback/${DATE}-wp-audit-report.md 回報 Owner 決定批次修復。" >> "$LOG_FILE"
  echo "⚠️ 稽核發現違規，詳見 $LOG_FILE"
else
  echo "✅ 本次全站稽核通過，無違規文章。"
fi
