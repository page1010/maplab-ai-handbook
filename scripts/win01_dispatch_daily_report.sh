#!/usr/bin/env bash
# win01_dispatch_daily_report.sh — 派「今天回顧＋明天展望」日報卡給 win-01（agent-bus）
# Owner msg（2026-09-04）「一樣讓win-os 回報今天展望明天」授權。
# 只寫一張卡進 inbox/win-01/ 並 push；不動 win-01 其他狀態。
set -euo pipefail
BUS="${BUS_ROOT:-$HOME/agent-bus}"
DATE="$(date +%Y%m%d)"
TASK_ID="daily-report-today-tomorrow-$DATE"
CARD="$BUS/inbox/win-01/$TASK_ID.json"

if [[ ! -d "$BUS/inbox/win-01" ]]; then
    echo "❌ bus inbox 不存在：$BUS/inbox/win-01"; exit 1
fi
if [[ -f "$CARD" ]]; then
    echo "⚠️ 今天的日報卡已存在，不重複派：$CARD"; exit 0
fi

git -C "$BUS" pull --rebase -q || true

cat > "$CARD" <<EOF
{
 "task_id": "$TASK_ID",
 "machine_id": "win-01",
 "state": "assigned",
 "domain": "ops/reporting",
 "type": "status-report",
 "assigned_by": "mac-a0 (Fable5)",
 "created_at": "$(date '+%Y-%m-%dT%H:%M:%S%z')",
 "priority": "P1",
 "title": "日報：今天做了什麼＋明天展望（Owner 例行要求）",
 "instructions": [
  "1) 回報今天實際完成/推進的項目，以 outbox 與 archive 的實績為準，不要憑印象。",
  "2) 說明目前 pending_inbox 每張卡的狀態（進行中/卡住原因/預計何時動）。",
  "3) 明天展望：列出明天打算執行的卡與順序，一句話說明各自的產出物。",
  "4) 附上你這台的額度/資源使用概況（若有 API 額度計數就附，沒有就說沒有）。",
  "5) 心跳從今天約 11:00 之後停了（hb_age>400m）——回報卡住或重啟的原因。"
 ],
 "acceptance": "outbox/win-01/$TASK_ID.json state=done，內容涵蓋上述 5 點，實績有檔案路徑佐證。",
 "constraints": { "read_only_report": true, "no_publish": true },
 "return": "outbox/win-01/$TASK_ID.json"
}
EOF

git -C "$BUS" add "inbox/win-01/$TASK_ID.json"
git -C "$BUS" commit -q -m "dispatch(mac-a0): $TASK_ID 日報卡（Owner 例行今天/明天回報）"
git -C "$BUS" push -q
echo "✅ 日報卡已派：inbox/win-01/$TASK_ID.json（已 push）"
