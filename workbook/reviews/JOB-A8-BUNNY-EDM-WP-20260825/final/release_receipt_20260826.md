# 邦尼兔跨平台發布收據 — 2026-08-26

## VERIFIED

- WordPress 正式頁已上線：https://www.maplabkitchen.com/tainan-daycare-graduation-catering/
- 公開頁 readback：H1、LINE CTA、三張正文圖與三組 alt 全部存在；`快速導覽／草稿／A2／A8／生成` 沒有出現在公開頁。
- 正式影片已完成：16:9 長版 50.840 秒；9:16 Short 15.000 秒。
- Pinterest 兩張 2:3 圖卡、標題、說明、alt 與目的連結已完成。
- 平台欄位單一來源：`platform_metadata.md`。

## PLATFORM STATE

| 平台 | 狀態 | 證據／原因 |
|---|---|---|
| WordPress | `PUBLISHED` | 正式 URL 可讀，三張圖片 alt 與 CTA readback PASS |
| YouTube 長版 | `UPLOAD_BLOCKED` | Studio 已登入；清除無關的 Suno 儲存視窗後，程式化 file chooser 對四種可控路徑仍回 `Not allowed`，視覺點擊也無法把受控分頁交給 macOS 選檔器 |
| YouTube Short | `UPLOAD_BLOCKED` | 同上；沒有建立影片 ID，不冒充草稿或成功 |
| Pinterest Pin 1／2 | `LOGIN_BLOCKED` | Google iframe button 與備用 button 都未建立登入分頁，帳號仍未登入 |
| Telegram | `WAITING_FOR_PLATFORM_LINKS` | 只有 WP link，不提前發「全部上傳完成」通知 |

## ARTIFACT HASHES

- Long MP4：`1231fbe9410915b017150627a48cadf079d9eada32e1bc4533238a5e6a2c0226`
- Short MP4：`61097eb8adb3c5538f32c24259cde2aec224d300943d538ee6607258d0ddd082`
- Pin 1：`d4fd1b9525fdf1c3ea01d480fdff3a02d2ab3012f1eccec3a06290aba1ec0ae2`
- Pin 2：`a2c3d30d4c08fa6f43304d8450fe8962739212e64d59be8c3d3f644ce8a0f042`
- Master WAV：`032d93033905def246cfca885d194bee726fe7a32ba5047c95b9442e01edf813`

## REFERENCE IMPLEMENTATIONS

- YouTube 官方 sample repo `youtube/api-samples` 已 archived；只用來核對 OAuth／upload flow，不直接移植舊碼。正式 API 方案應依目前官方 Data API upload guide 重建最小 adapter。
- Pinterest 官方 `pinterest/api-quickstart` 仍維護（Python、Apache-2.0）；未來若瀏覽器登入／上傳持續不穩，才建立 OAuth＋Create Pin adapter。
- 本次沒有因自動化失敗而建立第三套 queue 或假 sender。

## NEXT BOUNDED ACTION

Owner 只需做兩個瀏覽器手勢：在已開啟的 YouTube Studio 選檔器手選長／短 MP4；在 Pinterest 完成 Google 登入。下一輪直接消耗現成 artifact、填入既定欄位、發布與反讀所有公開連結，再發一則 Telegram 完成通知；不重做內容。
