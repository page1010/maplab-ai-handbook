# Sheets 資料修改檢查規則

版本：v1.0 | 建立：2026-03-29

原因：2026-03-28 Items 被 backup 覆蓋弄丟 Owner 價格；QUOTE_DRAFT 改到錯誤的 QUOTE v2 工作表。

## 修改前必查

| # | 檢查項 | 說明 |
|---|--------|------|
| 1 | 確認工作表名稱 | 用 API 列出所有 tab，確認操作的是正確的 |
| 2 | 先讀後改 | 修改前先 GET 讀取目標 range，確認現有值 |
| 3 | Owner 手動資料不覆蓋 | Items E 欄（成本）是 Owner 手動維護，禁止批次覆蓋 |
| 4 | backup 同步 | 如果改了 Items，確認 Items_backup 是否需要同步 |
| 5 | 公式不破壞 | 改 cell 前確認有沒有公式引用它 |
| 6 | 記錄改動 | commit message 寫明改了哪個 Sheets 的哪個 range |
