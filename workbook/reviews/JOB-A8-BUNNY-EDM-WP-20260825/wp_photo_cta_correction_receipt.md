# 邦尼兔文章照片＋CTA 修正收據

日期：2026-08-25
角色：A2 WordPress／SEO 執行者
狀態：PASS，等待 Owner 核稿

## Owner 指出的缺口

1. WordPress 文章審稿面看不到照片。
2. CTA 不夠明確。
3. 同一案例需繼續跑，不另開第二案例。

## 本輪修正

- `wp_draft.md` 已加入 2 個正文圖片標記與公開安全 alt。
- 結尾改為活動資訊補問句，另立一段 `加入 MAPLAB 官方 LINE，開始討論活動`。
- CTA 指向既有真實 URL：`https://lin.ee/IP8nt4n`。
- Google Doc 已實際插入 2 張安全餐點照片。WordPress 素材保留 WebP；審稿面另用 JPEG 相容副本，不改原資產。

## 驗收證據

- Google Doc：<https://docs.google.com/document/d/18kApXho1icyj78XBVo2aEzFUfJI7sMKt4y9I0jq5Ky8/edit?tab=t.0>
- Docs API 反讀：`inlineObjectCount=2`、正文 inline references=`2`。
- CTA 反讀：獨立 paragraph；link URL=`https://lin.ee/IP8nt4n`。
- 公開文案 gate：`ok=true`。
- focused tests：`tests/test_a8_public_copy_gate.py` → `3 passed`。
- 本地公開稿：2 個 image markup、1 個 LINE CTA。
- 目前待核稿字元數：`1962`；前 500 字 SHA-256 前 16 碼：`385c7784d6b18a6e`。

## 邊界與下一步

- 尚未建立或發布 WordPress post；尚未生成新母帶；尚未啟動 A8 剪輯或社群發布。
- 唯一下一步：Owner 在同一份 Google Doc 核准文章，並選擇「歌詞安全版」或「具名邦尼兔版」。通過後才進 WordPress 草稿與新母帶。
