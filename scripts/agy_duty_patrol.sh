#!/usr/bin/env bash
# agy_duty_patrol.sh — Antigravity（agy）無額度值班巡邏：盤點 + 具名產出落 bus
# 依據 skills/quota-duty-rotation.md v1.1（Owner msg 4738 建制、msg 4748 授予寫入權＋全員具名制）。
# 共同紅線：draft-first 不發布、不碰 secrets、不動生產設定。
set -euo pipefail
BUS="${BUS_ROOT:-$HOME/agent-bus}"
HB="/Users/pagemacmini/maplab-ai-handbook"
DATE="$(date +%Y%m%d-%H%M)"
OUT="$BUS/outbox/antigravity/duty-$DATE.md"

if ! command -v agy >/dev/null 2>&1; then
    echo "❌ agy CLI 不存在"; exit 1
fi
mkdir -p "$BUS/outbox/antigravity" "$BUS/inbox/antigravity"

PROMPT="你是 Antigravity，正在 MAPLAB 系統無額度時段值班。你有寫入權（Owner 授予），但一律具名：所有產出檔案開頭標 executed_by: antigravity。請：\
1) 讀 $HB/handoff/dispatch/window-bus-20260904.md 與 $HB/state/system_journal.md 最後 30 行，摘要目前進行中/卡住的工作；\
2) 讀 $BUS/heartbeat/win-01.json 與 $BUS/inbox/win-01/ 卡片清單，回報 win-01 待辦；\
3) 若 $BUS/inbox/antigravity/ 有派給你的卡，逐張接走執行，回執寫 $BUS/outbox/antigravity/ 並標 executed_by=antigravity；\
4) 用繁體中文輸出值班報告：現況摘要/做了什麼/風險/建議下一步。\
紅線：不發布任何對外內容（draft-first）、不讀不寫 secrets、不動生產設定、不安裝軟體。"

echo "== agy duty patrol $DATE ==" | tee "$OUT.tmp"
agy --print "$PROMPT" >> "$OUT.tmp" 2>&1 || { echo "❌ agy 執行失敗" >> "$OUT.tmp"; }
mv "$OUT.tmp" "$OUT"

git -C "$BUS" pull --rebase -q || true
git -C "$BUS" add -A "outbox/antigravity" "inbox/antigravity"
git -C "$BUS" -c user.name="antigravity" -c user.email="antigravity@maplab.local" commit -q -m "duty(agy): 值班巡邏報告 $DATE (executed_by=antigravity)"
git -C "$BUS" push -q || echo "⚠️ push 失敗，報告已留本地"
echo "✅ 值班報告：$OUT"
