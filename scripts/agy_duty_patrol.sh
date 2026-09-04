#!/usr/bin/env bash
# agy_duty_patrol.sh — Antigravity（agy）無額度值班巡邏：唯讀盤點 + 產出落 bus 提案
# 依據 skills/quota-duty-rotation.md v1.0（Owner msg 4738）。
# agy 沙盒唯讀保證未驗證（ExecutionLease 治理檔），故值班一律唯讀：
# 只讀狀態、只寫 bus outbox/antigravity/，不改生產檔、不發布、不碰 secrets。
set -euo pipefail
BUS="${BUS_ROOT:-$HOME/agent-bus}"
HB="/Users/pagemacmini/maplab-ai-handbook"
DATE="$(date +%Y%m%d-%H%M)"
OUT="$BUS/outbox/antigravity/duty-$DATE.md"

if ! command -v agy >/dev/null 2>&1; then
    echo "❌ agy CLI 不存在"; exit 1
fi
mkdir -p "$BUS/outbox/antigravity" "$BUS/inbox/antigravity"

PROMPT="你是 Antigravity，正在 MAPLAB 系統無額度時段值班（唯讀）。請只讀不寫地盤點：\
1) 讀 $HB/handoff/dispatch/window-bus-20260904.md 與 $HB/state/system_journal.md 最後 30 行，摘要目前進行中/卡住的工作；\
2) 讀 $BUS/heartbeat/win-01.json 與 $BUS/inbox/win-01/ 卡片清單，回報 win-01 待辦；\
3) 若 $BUS/inbox/antigravity/ 有派給你的卡，逐張讀並起草回應方案（只起草，不執行）；\
4) 用繁體中文輸出值班報告：現況摘要/風險/建議下一步。不得執行任何寫入、安裝、發布或網路操作。"

echo "== agy duty patrol $DATE ==" | tee "$OUT.tmp"
agy --print "$PROMPT" >> "$OUT.tmp" 2>&1 || { echo "❌ agy 執行失敗" >> "$OUT.tmp"; }
mv "$OUT.tmp" "$OUT"

git -C "$BUS" pull --rebase -q || true
git -C "$BUS" add "outbox/antigravity/duty-$DATE.md"
git -C "$BUS" commit -q -m "duty(agy): 值班巡邏報告 $DATE"
git -C "$BUS" push -q || echo "⚠️ push 失敗，報告已留本地"
echo "✅ 值班報告：$OUT"
