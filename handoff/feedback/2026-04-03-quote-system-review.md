# 自我檢討：報價系統修復 — 2026-04-03

## 我犯了什麼錯

### 1. Cell References 完全錯誤
v3.1 Code.gs 的 cell references 與 Owner 在 2026-04-02 重構的 QUOTE_DRAFT 版面完全不符：

| 錯誤（v3.1） | 正確（v3.2） | 問題 |
|---|---|---|
| B2-B9（客戶資訊） | D2, E2, D3, F3, D4, F4, D5, F5 | B 欄是 label，不能覆蓋 |
| H1/H2（Case ID/時間） | K1/K2 | H 欄在列印範圍外（C1:F55 之後） |
| M/N 欄（系統狀態） | K3/K4/K5 | M/N 欄不存在系統資訊 |
| N5/N7（下拉驗證） | K3/K4 | 位置錯誤 |
| A30/A31（條款） | C39/C40 | A 欄不在列印範圍，且列數錯 |

**根因：** handoff/feedback/2026-04-02-quote-draft-v3-layout.md 已有完整版面對照表，但我在寫 v3.1 時沒有讀這份文件就直接跑測試，用了舊的 cell references。

### 2. 沒有品項篩選邏輯
Owner 需要系統根據預算/人數/品項數量/毛利率自動篩選品項，但 v3.1 完全沒有這個功能。報價單只是空殼複製，品項區是空的。

**根因：** 把「產出報價單」理解成「複製模板」，沒有深究報價流程的完整需求。Owner 的真實需求是：系統要能「參謀建議菜單」，而不只是「複製空表格」。

### 3. D 欄 Dropdown 殘留
D8:D22 是模板裡讓業務手動選品項的 dropdown。產出給客戶的報價單裡，這些 dropdown 應該清除（直接顯示文字），但 v3.1 完全沒有清除。

### 4. 條款不可見
條款寫到 A30:A31，但實際版面條款在 C39+，而且沒有設定 wrap text / 確保行不隱藏，所以條款在輸出報價單裡不可見。

### 5. syncQuoteStatus_ 狀態欄位錯
syncQuoteStatus_ 讀 N5/N7，但 v3.2 狀態改為 K3/K4，導致同步功能完全失效。

---

## 根因分析

**共同根因：讀了版面文件但沒有在改 code 前核對每個 cell reference。**

具體失誤鏈：
1. Owner 在 2026-04-02 重構了 QUOTE_DRAFT 並口述 cell mapping
2. A1 寫進 handoff/feedback/2026-04-02-quote-draft-v3-layout.md
3. v3.1 Code.gs 是在那之前（或沒對照那份文件）寫的
4. 沒有做 cell reference 對照就 push + 測試 → 測試結果必然錯誤

---

## 改善措施

### 未來 Code.gs 修改前的必做步驟
1. 讀 `handoff/feedback/` 最新的版面文件，確認所有 cell references
2. 在 code 頂部的 JSDoc 寫清楚每個欄位的位置（已在 v3.2 加入）
3. 修改任何 cell reference 前，先 grep 現有 code 確認是否需要一起改

### 未來 doPost 測試前的必做確認
1. 確認品項篩選邏輯存在且有回傳值
2. 確認條款寫入位置正確
3. 確認 D 欄 dropdown 被清除

### 版面文件是唯一真相來源
`handoff/feedback/2026-04-02-quote-draft-v3-layout.md` 說：
> 這份文件是 Code.gs 所有 cell references 的唯一真相來源。

下次改 code，先讀這份文件，再改 code。

---

## v3.2 修復清單

- [x] 修正所有 client info cell references（D2, E2, D3, F3, D4, F4, D5, F5）
- [x] 修正系統狀態欄位（K1-K5，不在列印範圍）
- [x] 修正條款位置（C39/C40，含 wrap text + showRows）
- [x] 新增 D8:D22 clearDataValidations（產出後清除 dropdown）
- [x] 新增 selectItemsForBudget_()（預算→品項篩選→毛利率驗證）
- [x] 新增 writeItemsToQuote_()（寫入菜單區 D8:D13, D15:D19）
- [x] 修正 handleQuoteRequest_ 新增 budget/itemCount/minMargin/style 參數
- [x] 修正 syncQuoteStatus_ 讀 K3/K4（而非 N5/N7）
- [x] 修正 getQuoteDraftValues() cell references
- [x] makeCopy 後刪除分頁改為先收集再批次刪除（避免迭代中修改）
