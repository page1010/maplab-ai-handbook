# 邦尼兔多平台發布交接 — 2026-08-26

## 平台矩陣

| 平台 | 素材 | 目前狀態 | 下一個最短動作 |
|---|---|---|---|
| YouTube 長版 | `video/maplab-bunny-youtube-long-50s.mp4` | `NEEDS_OWNER_FILE_PICK` | 在已開啟的 MAPLAB Studio 上傳視窗手選此檔 |
| YouTube Shorts | `video/maplab-bunny-youtube-short-15s.mp4` | `NEEDS_OWNER_FILE_PICK` | 長版選檔後再手選此檔 |
| TikTok | `video/maplab-bunny-youtube-short-15s.mp4` | `NEEDS_OWNER_FILE_PICK` | 在已登入 TikTok Studio 手選此檔 |
| Instagram Reels | 同一 15 秒直式片 | `PLANNED_NOT_OPEN` | 待前兩平台接續 |
| Facebook Reels | 同一 15 秒直式片 | `PLANNED_NOT_OPEN` | 待前兩平台接續 |
| Pinterest Pin 1／2 | `pinterest/*.jpg` | `LOGGED_IN_READY` | 手選圖片後填既定 title／description／alt／link |

## 本輪瀏覽器證據

- YouTube Studio 已登入 `maplabkitchen`／channel `UC85n15rcFgHzZtb78vV6-sw`。
- TikTok Studio 已登入且顯示影片上傳區。
- Pinterest 已登入 `maplabkitchen` 商業帳號並可見「建立 Pin」。
- YouTube 與 TikTok 的受控 file chooser 對已驗證本機 MP4 均回 `Not allowed`；依 SOP 停止重複嘗試，保留頁面給 Owner 手選。

## 欄位與通知

- 公開欄位單一來源：`platform_metadata.md`，已補 TikTok／Instagram／Facebook 說明、hashtags 與 alt 限制。
- YouTube 無獨立影片／縮圖 alt 欄位；使用標題、描述與字幕承接可及性和搜尋語意。
- `BLOCKER_MESSAGE_STATUS=MESSAGE_READY_NOT_SENT`：應先通知 Owner 缺少哪些手勢；Telegram 實際送出前仍須當下確認。

## 歌詞歸屬

- Google Doc：https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0
- 2026-08-25 commit `c9f1ace` 曾由 A8 改寫 repo 基礎歌詞。
- 本輪 Google Drive revision metadata 顯示後續修訂者為 `page Wu`；本輪沒有再修改 Google Doc。
- 目前以 Google Doc 現文為準，包含 `lemon and cream`、`伴隨著祝賀　寫下美好畫面`、新 Bridge 與 `把親友約上桌`。

## Resume Prompt

Owner 已在 YouTube Studio 與 TikTok Studio 手選對應影片後，A8 讀 `final/platform_metadata.md` 填欄位；先存私人／草稿，不公開。接著完成 Pinterest 兩張 Pin、IG Reels、FB Reels 的草稿／發布前頁面，逐平台取得 action-time approval 才公開。每個公開動作後回讀 URL；有缺件先準備 Telegram blocker 訊息，全數完成後準備 completion 訊息，兩者送出前都要 Owner 當下確認。
