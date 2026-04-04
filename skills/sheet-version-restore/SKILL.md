# Skill: sheet-version-restore — Google Sheets 版本恢復 SOP

版本：v1.0 | 建立：2026-04-04 | 原因：A0 修改 createQuote 導致 QUOTE_DRAFT 公式損壞，需用版本紀錄還原

## MVP 母本
目前的 MVP 母本版本：2026-04-03 下午 5:00
如果不確定要還原到哪個版本，先還原到 MVP 母本。

## 觸發條件
Agent 或系統改壞了 Google Sheets 的公式/驗證/資料

## 恢復步驟
1. 打開受影響的 Google Sheet
2. 檔案 > 版本記錄 > 查看版本記錄
3. 在右側面板找到出問題前的版本（看時間戳）
4. 點擊該版本預覽，確認資料正確
5. 點「還原這個版本」> 確認

## 注意事項
- 還原會影響整個 Spreadsheet（所有分頁），不只是你改壞的那個
- 還原後 SALES_INTAKE 等分頁也會回到舊版，新增的資料會遺失
- 還原後立即確認關鍵公式（I 欄 VLOOKUP、J 欄小計、毛利率）
- 還原不影響 Apps Script 程式碼（GAS 有自己的版本控制）

## 預防措施
- 任何 GAS 程式碼修改前，先在「建立副本」上測試
- 不要在主系統 Sheet 上直接跑未驗證的 createQuote
- 不要用 setValue 寫入有公式的格子
- 不要用 clearDataValidations 清除模板的下拉驗證
