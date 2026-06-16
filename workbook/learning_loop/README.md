# MAPLAB Learning Loop Reaction Ledger

這個目錄是 MAPLAB learning loop v0 的第一個可執行層：把巡查結果從「通知」升級成「可追蹤反應」。

## 現有檔案

- `reaction_ledger.jsonl`: append-only reaction ledger。每一列是一個 patrol reaction，需要被分流、執行、關閉或回收成規則。
- `reaction_ledger_summary.md`: 給 A0/A1/Codex 快速讀的目前開放項、逾期項與決策統計。

同一個 `reaction_id + target_task_card` 在未關閉前不會重複開新 row；下一次 patrol 只會更新 summary。這讓 ledger 是「待處理控制面」，不是每日重複提醒清單。

## 產生方式

```bash
rtk python3 tools/hermes_patrol_bridge.py --repo /Users/pagemacmini/maplab-ai-handbook --raw-text-file logs/patrol-scheduled.log
```

這個 bridge 不讀 `.env`、不呼叫外部 API、不改外部系統。它只讀 repo 內 task cards / patrol text，然後輸出 reaction packet 與 ledger。不要把 generated `workbook/hermes/patrol/latest.md` 再餵回 bridge，避免 raw excerpt 出現巢狀 packet。

## 決策欄位

- `owner_5min`: 真正需要 Owner 的 5 分鐘動作，例如 OAuth reauth。不可用模糊「等 Owner」結案。
- `direct_do`: agent 可以直接處理，不應升級給 Owner。
- `delegated`: 交給指定角色或 task card 繼續拆解。
- `memory_candidate`: 重複踩坑或可泛化經驗，候選寫回 `pitfalls.md` / `skills/`。
- `closed`: 本輪無需處理，保留為巡查紀錄。

## 下一階段

1. Token capital registry: 把可複用的 prompt、評測、task packet、skill、pitfall 條目登記成公司自有 AI 能力資產。
2. Eval harness: 對 reaction ledger 定期檢查「有無逾期、是否被關閉、是否回寫到 task card / pitfalls / skills」。
3. Closure writer: 讓完成的 reaction 能用證據關閉，而不是只靠摘要顯示 open。

## Guardrails

- Ledger 是反應控制面，不是秘密庫。不得寫入 token、cookie、password、私密客戶資料。
- `owner_5min` 必須附上 Owner 在 5 分鐘內能完成的具體動作。
- 重複 7 天以上的 open reaction，要升級成 task card 修補或 `pitfalls.md` 教訓。
