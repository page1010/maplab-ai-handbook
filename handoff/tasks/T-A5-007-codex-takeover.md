# Task Card: T-A5-007 — A5 報價系統移交 Codex 管理

---

## 接續狀態

- **狀態**: 🔲 待 Codex 認領(Owner 2026-07-06 口頭指示:「把 A5 接給 Codex 管理」)
- **最後活動**: 2026-07-06(遠端 Claude — 成本結構診斷完成,建立本卡)
- **接續點**: Codex 讀本卡「診斷結論」→ 執行「交接後第一批工作」
- **阻塞**: 無(fixMasterTemplate 可由 Codex 以 clasp/GAS 編輯器執行,或 Owner 手動跑一次)

---

## Meta
- **Task ID**: T-A5-007
- **任務名稱**: A5 報價系統移交 Codex 管理
- **負責 Agent**: Codex(接管 A5 domain);前置診斷:遠端 Claude
- **建立日期**: 2026-07-06
- **Sheets ID**: 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
- **相關卡**: T-A5-002(fixMasterTemplate 待執行)、T-A5-004(createSlides CRITICAL)、T-A5-005(trigger 待設)、T-A5-006(OrderLines,前置 005)

## 背景:Owner 懷疑「成本結構被改爆」的診斷結論(2026-07-06)

1. **成本結構公式沒有被改爆。** master QUOTE_DRAFT 公式(G 欄 VLOOKUP 成本、H=G*F、E25=SUM(H7:H19)、H33=H32)自 2026-03-31 修正後 git 無任何後續變更。
2. **兩個已知「資料級」問題,修復函式已寫好但從未執行**:`fixMasterTemplate()`(`scripts/apps-script/Code.gs:807`,commit `3209fba` 2026-06-23 已 clasp push):①「日式章魚燒明太子可頌」→「明太子可頌」、「府城冰梅醬蝦棗」→「台南古早味蝦棗」改名讓 G 欄 VLOOKUP 找得到成本(消 #N/A);② 清 D7:D20 重複品項列。**T-A5-002 卡在「執行一次」已 ~2 週。**
3. **Owner 截圖的毛利不一致(總金額 50,000/訂單成本 4,870/毛利率 75.70%)不是公式壞掉**:`createQuoteVariants` 產出的副本,J30(訂單成本)/J31(毛利率)是 **payload 靜態值**,且 `calcMarginDecimal_`(`Code.gs:546`)有 preset 覆蓋 — 模型給的 75.7% 是餐點口徑(4,870/(1−0.757)≈20,041≈foodRevenue),不是整體口徑 (50,000−4,870)/50,000=90.3%。根因是**信任模型數字、缺一致性防呆**。

## 交接後第一批工作(驗收標準)

1. **跑 `fixMasterTemplate()`**(GAS 編輯器或 clasp run),驗收:QUOTE_DRAFT G 欄無 #N/A、無重複品項列。→ 同時關 T-A5-002。
2. **毛利防呆(擇一或並行)**:
   - a. `calcMarginDecimal_` 加守門:|preset − computed| > 0.02 時捨棄 preset、用 computed,並在副本 L 欄寫警示註記;
   - b. 副本 J31 改寫公式 `=IF(E30>0,1-J30/E30,"")`,讓表自己算。
   - 驗收:重放 Owner 截圖案例(50,000/4,870),J31 顯示 90.3% 或明確警示,不再出現矛盾數字。
3. **回歸測試**:`bot_a6/test_a6_10_rounds.py` 全綠(目前 9/10,Round 6 budget 缺漏)。
4. 檢視 T-A5-004(createSlides)與 T-A5-005(trigger),排接續計畫。

## 規則(不變)
- 不揭露成本/毛利給客戶;副本框線內是客人看的,框線外是內部。
- 毛利底線 ≥70%(`docs/business-requirements/quote-pricing-logic.md`)。
- master QUOTE_DRAFT 公式/結構改動需 Owner 確認;副本可自由產出。
