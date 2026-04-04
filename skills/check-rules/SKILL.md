# Skill: check-rules — 修改前檢查清單

版本：v1.1 | 建立：2026-03-29 | 更新：2026-04-04（新增 QUOTE_DRAFT 公式完整性檢查）

---

## Sheets 資料修改檢查（clasp push 前、任何 GAS 修改前）

| # | 檢查項 | 說明 |
|---|--------|------|
| 1 | 確認工作表名稱 | 用 API 列出所有 tab，確認操作的是正確的 |
| 2 | 先讀後改 | 修改前先 GET 讀取目標 range，確認現有值 |
| 3 | Owner 手動資料不覆蓋 | Items E 欄（成本）是 Owner 手動維護，禁止批次覆蓋 |
| 4 | backup 同步 | 如果改了 Items，確認 Items_backup 是否需要同步 |
| 5 | 公式不破壞 | 改 cell 前確認有沒有公式引用它 |
| 6 | 記錄改動 | commit message 寫明改了哪個 Sheets 的哪個 range |

---

## QUOTE_DRAFT 公式完整性檢查（任何 clasp push 前必做）

> 背景：2026-04-04 A0 多次修改 createQuote 導致 QUOTE_DRAFT I 欄 VLOOKUP 被 setValue 覆蓋、D 欄下拉被 clearDataValidations 清除，需用版本紀錄還原。

在任何 clasp push 之前，必須確認：

- [ ] Code.gs 裡沒有 setValue 寫到 I 欄或 J 欄
- [ ] Code.gs 裡沒有 clearDataValidations
- [ ] createQuote 只寫 B2-B9、A30-A31、H1-H2、M/N 欄
- [ ] 沒有對 D8:D19 使用 setValue（D 欄是下拉選單）
- [ ] 測試用副本，不在主系統 Sheet 上跑

### QUOTE_DRAFT 公式參考
```
I8: =IF(D8="","",IFERROR(VLOOKUP(D8,Items!C:E,3,0),"N/A"))
（I8:I16 全部同樣公式，對應不同的 D 欄品項）
```
