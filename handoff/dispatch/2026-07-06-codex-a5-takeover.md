# Dispatch Packet — Codex 接管 A5(2026-07-06)

> 用法:把下方 code block 整段貼給 Codex(CLI 或 IDE),cwd 設在 maplab-ai-handbook repo 根目錄。

```
你現在接管 MAPLAB A5(報價與提案引擎)的日常管理,Owner 已於 2026-07-06 核准。

開工順序:
1. 讀 CURRENT_STATUS.md(唯一真相源)
2. 讀 AGENT_RECALL_PROMPTS.md 的 ## A5 段落(角色規則與斷點)
3. 讀 handoff/tasks/T-A5-007-codex-takeover.md(移交卡,含成本結構診斷結論與驗收標準)
4. 讀 handoff/tasks/T-A5-002.md / T-A5-004.md / T-A5-005.md

第一批工作(依 T-A5-007 驗收標準):
1. 執行 scripts/apps-script/Code.gs 的 fixMasterTemplate()(clasp run 或 GAS 編輯器),
   驗收 QUOTE_DRAFT G 欄無 #N/A、無重複品項列,然後關 T-A5-002。
2. 修毛利防呆:calcMarginDecimal_(Code.gs:546)在 |preset−computed|>0.02 時捨棄 preset
   改用 computed 並在 L 欄註記;或把副本 J31 改成公式 =IF(E30>0,1-J30/E30,"")。
   驗收:重放 50,000/4,870 案例不再顯示 75.7% 的矛盾毛利。
3. 跑 bot_a6/test_a6_10_rounds.py 回歸(目前 9/10,Round 6 budget 缺漏要修)。

規則:
- 毛利底線 ≥70%(docs/business-requirements/quote-pricing-logic.md);不得對客戶揭露成本/毛利。
- master QUOTE_DRAFT 公式/結構變更前先問 Owner;副本(createQuoteVariants)可自由產出。
- 每個有意義變更立即 bash scripts/checkpoint.sh "A5(Codex)" "做了什麼" 存檔。
- 完成後更新 CURRENT_STATUS.md + AGENT_RECALL_PROMPTS.md A5 狀態行,輸出給 Owner 的 5 行回報。
```
