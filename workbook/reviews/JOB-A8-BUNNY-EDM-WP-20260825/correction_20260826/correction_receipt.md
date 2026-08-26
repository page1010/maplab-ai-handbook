# 邦尼兔影片裁切／清晰度修正收據

日期：2026-08-26  
Verdict：`OWNER_REVIEW_REQUIRED`

## 已驗證成品

| 成品 | 素材構成 | 規格 | SHA-256 |
|---|---|---|---|
| `render/maplab-bunny-short-15s-v2.mp4` | 2 支原始直式影片＋3 張原始高解析照片 | H.264/AAC、1080×1920、30 fps、15.000 秒、3.30 Mbps | `057e15128408c1be08960afa444074d550724975affcec9aba4511da6564fe39` |
| `render/maplab-bunny-long-50s-v2.mp4` | 3 支原始影片＋7 張原始高解析照片 | H.264/AAC、1920×1080、30 fps、50.800 秒、3.18 Mbps | `ccf9fbb6294d1affd1dbf3c15546a8858454286584f2a234ee49ecc636e0e7f3` |

## 視覺 QA

- 已用原始品質辨識 22 張照片、6 支影片 contact sheet，以及兩支成品完整時間軸。
- 15 秒版第一次重剪仍出現「橫片縮在中央、周圍模糊」；當輪不採用，改以第三張高解析直式照片重剪後才留下本收據。
- 50.8 秒版第一次執行被 renderer 預設 `limit=5` 截斷；當輪不採用，明確設 `--limit 10` 後重剪，manifest 已反讀 10 個素材。
- 最終時間軸：`qa/bunny-short-v2-timeline.jpg`、`qa/bunny-long-v2-timeline.jpg`。
- 原始素材判定與排除理由：`source_visual_audit.md`。

## 平台能力（只驗證入口，未發布）

- Pinterest：Owner Chrome 已登入 `maplabkitchen`，可見「建立 Pin 或圖版」。
- TikTok：Owner Chrome 的 TikTok Studio 已登入，可見「選取影片」上傳入口；頁面接受 MP4、9:16／16:9，並顯示單檔上限 30 GB、60 分鐘。
- 本輪沒有上傳、建立草稿或公開任何影片。Owner 核准明確檔案後，下一個 bounded action 才是先上 TikTok／Pinterest 草稿、填欄位並回讀，再取得發布確認。

## Next Bounded Action

Owner 先看兩支 v2；若回覆「影片通過」，A8 以這兩個 hash 鎖定檔案，進入 TikTok／Pinterest 上傳與欄位 readback，不再改片或偷換版本。

