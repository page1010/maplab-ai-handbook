# MAPLAB 資料保留政策 (data-policy.md)

建立：2026-06-24（T-HQ-001 P5）  
維護：B1 Builder / A1 系統總管  
版本：v1.0

## 保留規則

| 類型 | 路徑 | 保留 | 壓縮 | 刪除 |
|------|------|------|------|------|
| 爬蟲 raw 檔 | data/raw/ | 30 天 | 30 天後 gzip | 90 天後刪除 |
| bot 對話 log | data/telegram-logs/ | 90 天 | >10MB rotate | 180 天後壓縮歸檔 |
| hermes log | ~/.hermes/logs/ | 14 天 | >10MB rotate | 30 天後刪除 |
| Hermes memories | ~/.hermes/memories/ | 永久 | 無 | 人工審核後刪 |
| archive/ | archive/ | 每季摘要 | B3 每季整理 | 保留摘要、刪 raw |
| bot/data/ | bot/data/ | 30 天 | >10MB rotate | 90 天後刪除 |
| IOS 爬蟲 raw | /Users/pagemacmini/Documents/New project/data/raw/ | 30 天 | 30 天後 gzip | 90 天後刪除 |

## Log Rotate 規則

- 觸發條件：檔案大小 > 10 MB
- 執行時間：每週一 03:00（launchd weekly job `com.maplab.log-rotate`）
- 操作：`mv log.md log.YYYYMMDD.md && gzip log.YYYYMMDD.md`
- 保留最新 10 個壓縮版本，超出的刪除

## Archive 壓縮規則

- 執行時間：每季（1/4/7/10 月 1 日 02:00）
- 對象：`archive/` 下超過 90 天的 raw 檔
- 操作：tar.gz + 刪除 raw，保留摘要 index

## Google Drive

- Owner 在 Drive 設定手動改「串流檔案（Stream Files）」可釋放 ~531 GB
- **Owner 人工一次性動作，不由腳本處理**
- 完成後通知 B3 更新 CURRENT_STATUS

## 注意事項

- secrets / .env / tokens 不得進入 archive
- git 中已有的 durable 摘要不刪除（只刪 raw）
- 此政策需 Owner 確認後方可執行刪除動作
