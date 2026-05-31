# Review Request — JOB-B1-CROSS-PROJECT-20260531

**To:** A1（治理/落地）, Owner（範圍決策）
**From:** B1

## 請審
1. 三層路由 + 能力邊界表是否符合你對 Codex/Antigravity/地端的定位？
2. 是否同意「不另開 SYSTEM_STATE/TASK_QUEUE 等重複檔，沿用 CURRENT_STATUS」的防重複決定？
3. 是否授權 A1 把三角色寫進 AGENT_RULES、並落地 patrol --continuity + run-log？

## 需 Owner 決策
- 地端 Ollama MVP 接線範圍（建議先半自動：盤查 + 生成 resume prompt，不自動執行）。
- checkpoint.sh 收尾是否要強制 verify-commit-on-main（建議：是）。

## 驗收條件
- 未來任一 session 額度斷掉後，Codex 只讀 resume prompt 即可接續，不需重讀對話。
- 缺資料一律標「缺」，不杜撰；所有結論分 verified/inferred/missing。
