# [已關閉/VOID] TG-DISPATCH-20260821-125241-quote-intake — 分類器誤判，未執行任何動作

> **這個資料夾是什麼**：Owner 在聊股票敘事時提到「機會成本」，被舊版分類器的裸字「成本」誤判成報價任務而自動建立此派工包。分類器 bug 已於 2026-08-21 修復（見 commit，拿掉裸字「成本」，改用完整詞組比對）。此包**未被任何 agent 實際處理**（本機 Ollama 只吐出一段格式錯誤的片段就中止），純屬稽核紀錄，不需要、也不會再有後續動作。

- status: **closed_void**（已關閉，僅留稽核紀錄，非待辦事項）
- void_reason: quote-intake classifier matched on 「機會成本」bare「成本」, now fixed; local Ollama qwen2.5-coder:7b produced only a malformed tool_call fragment, no real work done, not sent to @maplab_a6_bot
- primary_role: A6（誤判標籤，非實際指派）
- roles: A6, A5
- worker: Codex/A6 intake; A5 quote engine or GAS/Sheet when a sheet artifact is required
- runtime_target: codex/a6/a5
- prompt: `workbook/telegram-dispatch/VOID-TG-DISPATCH-20260821-125241-quote-intake/prompt.md`
- packet: `workbook/telegram-dispatch/VOID-TG-DISPATCH-20260821-125241-quote-intake/packet.json`

## Owner Request

```text
這個方向很棒，動手，但不是只查核資料要提出看法與以風暴比敘事押注給機會成本對比現有持股的見解與建議
```