# T-A4-003 — 照片 ALT/SEO 管線（地端 gemma4）+ Drive 改串流釋空間

## 接續狀態
- **狀態**: 🔄 進行中（管線已驗證可跑，背景批次處理中）
- **最後活動**: 2026-06-11
- **接續點**: 等 36,676 張處理完 → Owner 改 Drive 串流 → 釋出 ~433GB
- **阻塞**: launchd 排程需 Owner 跑一次 `launchctl load`（見下）
- **assigned_session**: 2026-06-11 / B1
- **last_committed_by**: B1（本 commit）

建立：2026-06-11
依據：Owner「雲端硬碟不要抓來地端了……我本來要讓地端模型寫 alt seo 作業做相簿整理的，可以先整理完同步再離線釋出空間嗎。讓這個功能為我們系統做出貢獻」

## 設計（先整理 → 同步上雲 → 再離線）

1. **整理**：`scripts/a4_photo_alt_pipeline.py` 用地端 gemma4（有 vision）掃
   `MAPLAB/MAPLAB_ASSETS`（36,676 張精選照），每張產出：繁中 ALT 文字（SEO）、
   場景分類、標籤、可上網判定 → 寫 SQLite `data/photo_alt_index.db`
2. **同步**：CSV 匯出到 `MAPLAB_ASSETS/_alt_index/photo_alt_index.csv`（在 Drive
   資料夾內 → 自動同步上雲，永久可查）
3. **離線**：全部處理完後，Owner 把兩個 Drive 帳號改「串流檔案」→ 釋出 ~531GB
   （lb99104 433GB + pagewu1010 98GB）。之後 agent 要照片走雲端 API/串流下載。

## 對系統的貢獻

- **A2 SEO**：WordPress 圖片 ALT 直接從 CSV 取，不再人工寫
- **A4 素材庫**：用標籤/場景搜尋 3.6 萬張照片，秒選圖
- **A6 提案**：場景關鍵字（企業活動/婚禮/茶點桌面）直接找提案素材

## 驗證紀錄（2026-06-11）

- gemma4:latest capabilities 含 vision ✅
- 實測 2 張：ALT 品質可直接用（「豐盛的慶生派對餐桌佈置…」+ 場景 + 標籤）✅
- 斷點續跑：以 (rel_path, size) 為 key，重跑不重複 ✅
- 注意：homebrew python3.14 pip 壞（libexpat），用 `/usr/bin/python3`（自帶 PIL）

## Owner 待辦（兩個一次性動作）

1. 啟用每小時排程：
   ```
   launchctl load ~/Library/LaunchAgents/com.maplab.a4-photo-alt.plist
   ```
2. 全部跑完後（用 `--status` 查進度），Google Drive 桌面設定改「串流檔案」

## 進度查詢

```
/usr/bin/python3 scripts/a4_photo_alt_pipeline.py --status
```

速度估算：每小時 60 張 → 全量約 25 天；若 Owner 想加速可改 plist `--limit` 或手動跑大批次。
