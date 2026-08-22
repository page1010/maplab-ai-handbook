# A8 各平台影片格式表（2026-08 查證）

單一真相來源程式：`tools/ai_workbook/a8_platform_formats.py`（`PLATFORM_FORMATS` config）。
Owner 定案：我方垂直短片一律壓 **≤30s**（平台本身允許更長，我們刻意壓短拉完播率）。

| 平台 | 比例 | 解析度 | 我方片長 | 平台上限 | 縮圖/封面 | 字幕安全區 |
|---|---|---|---|---|---|---|
| YouTube 長版 | 16:9 | 1920×1080 | 全曲 | 無 | 1280×720 (16:9) | 邊緣 5–8% |
| YouTube Shorts | 9:16 | 1080×1920 | ≤30s | 3 分鐘 | 從影格(桌面可上傳) | 上10/下10/右10% |
| IG Reels | 9:16 | 1080×1920 | ≤30s | 3 分鐘(可到 20 分) | 9:16 封面 | 上10/下20/右10%；Feed 裁 4:5 |
| TikTok | 9:16 | 1080×1920 | ≤30s | 60 分鐘(上傳) | cover 從影格 | 上8/下15/右12% |
| FB Reels | 9:16 | 1080×1920 | ≤30s | 無(一律 Reels) | 9:16 ≥1080寬，另備 1:1 | 上10/下20/右10% |
| IG Feed(直式) | 4:5 | 1080×1350 | ≤30s | — | 4:5 | 邊緣 5–10% |

共通：H.264 MP4、AAC 音訊、30fps+、檔案 ≤4GB（YT 幾乎不限）。

## 出處
- YouTube Shorts：[vidiq](https://vidiq.com/blog/post/youtube-shorts-vertical-video/)、[postfast](https://postfa.st/sizes/youtube/shorts)（9:16 1080×1920、2024-10 起上限 3 分鐘，多數高表現片 15–45s）
- YouTube 縮圖：[postfast](https://postfa.st/sizes/youtube/thumbnail)、[pixelbatch](https://pixelbatch.io/blog/youtube-thumbnail-size-guide)（1280×720 16:9，JPG/PNG，上限 2025-10 放寬到 50MB）
- IG Reels：[buffer](https://buffer.com/resources/instagram-image-size/)、[growthscribe](https://growthscribe.com/instagram-reel-aspect-ratio/)（9:16 1080×1920；安全區上10/下20/右10%；Feed 裁 4:5）
- TikTok：[fliki](https://fliki.ai/blog/tiktok-video-size)、[postfast](https://postfa.st/sizes/tiktok/video)（9:16 1080×1920；上帳號/右動作鍵/下 caption 安全區）
- FB Reels：[postfast](https://postfa.st/sizes/facebook/reels)、[aiarty](https://www.aiarty.com/knowledge-base/facebook-reel-size.htm)（9:16 1080×1920；2025-06 起 FB 影片一律 Reels；封面 9:16 ≥1080 寬，另可備 1:1）
