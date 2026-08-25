# 邦尼兔 WordPress 內部備註

本檔只供 A2／A8／Owner 審核，不能整檔貼入 WordPress。公開頁面只使用同目錄的 `wp_draft.md`。

## 交稿欄位

- 建議 slug：`tainan-daycare-graduation-catering`
- SEO title：`台南托嬰畢業典禮外燴｜一口點心與成長日甜點桌｜MAPLAB`
- Meta description：`台南托嬰畢業典禮外燴案例，整理一口點心、花藝與親子活動餐桌配置；查看準備重點，透過 MAPLAB 官方 LINE 詢問。`
- Focus keyword：`台南托嬰畢業典禮外燴`
- 目前待核稿字元數：`1962`
- 目前待核稿前 500 字 SHA-256：`385c7784d6b18a6e`
- 真實 LINE URL：`https://lin.ee/IP8nt4n`
- 精選圖：`wp_assets/maplab-daycare-graduation-catering-dessert-table.webp`
- WordPress draft：post `2018`，preview=`https://www.maplabkitchen.com/?p=2018&preview=true`，status=`draft`。
- 精選圖：已透過 WordPress UI 上傳並設定；public preview 可見，但本輪 owner-facing readback 未暴露 media ID，因此 ID 保留 `MISSING`，不可猜。
- Owner 審稿 Google Doc 已反讀確認：2 個 inline image objects；CTA 為獨立段落且連至真實 LINE URL。

## 素材邊界

- 公開候選只取 `c03` 的無人餐點桌景，已輸出兩張 900×1600 WebP。
- `c01` 畫面含活動日期，即使無人也不進這篇公開稿。
- 排除：`c02` 含幼兒人像海報；不輸出 public alt、不進公開影片或文章。
- 公開文案不描述素材篩選、隱私判定、檔案路徑、產線狀態或生成工具。

## SEO 佈局

- 主關鍵字：`台南托嬰畢業典禮外燴`。
- 次關鍵字：`台南畢業典禮外燴`、`親子活動茶點`、`畢業典禮甜點桌`。
- 內容策略：作案例長尾草稿，不搶既有週歲 pillar；以情境式內鏈支援 498，但明寫兩者是不同活動。
- 掛載：案例／派對家庭活動 cluster；「畢業典禮」在目前 keyword map 是未覆蓋的長尾意圖。
- 已驗證內鏈：
  - `tainan-custom-catering-menu` → `https://www.maplabkitchen.com/tainan-custom-catering-menu/`
  - `tainan-catering-line-inquiry-guide` → `https://www.maplabkitchen.com/tainan-catering-line-inquiry-guide/`
  - `catering-one-year-old-party-tainan` → `https://www.maplabkitchen.com/catering-one-year-old-party-tainan/`
- 禁連：`school-event-catering-tainan` 仍列在 404 slug 清單；不可因場景相近就使用。

## 建議圖片命名與 alt

- 首圖後：`maplab-daycare-graduation-catering-menu.webp` — `台南托嬰畢業典禮外燴的一口鹹食與甜點桌景`
- 「一張甜點桌」段後：`maplab-daycare-graduation-catering-desserts.webp` — `台南畢業典禮外燴的甜點層架與花藝陳列`

## 查證邊界

- 內部來源：Drive 活動資料夾與同日客戶報價表；本輪沒有以外部名冊推定公開名稱。
- 已確認：台南場景、活動類型、報價表與資料夾對應、畫面可見的餐點與佈置。
- 公開具名：報價表使用「邦尼托嬰中心」，Drive 工作資料夾使用「邦尼兔」；未找到客戶具名發布授權，因此公開文章先不使用中心名稱，「邦尼兔」只保留為內部 case label 與待 Owner 核准的歌詞選項。
- 尚未核准：WordPress 發布；任何社群上傳。草稿建立已由 Owner 本輪明確要求。

## FAQ schema（需與公開頁面文字一致）

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "托嬰畢業典禮適合準備哪些餐點？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "可以先依活動時段、停留時間與賓客年齡，安排容易拿取的一口鹹食、烘焙點心與甜點。若跨過正餐時間，再增加較有飽足感的品項。"
      }
    },
    {
      "@type": "Question",
      "name": "親子活動茶點桌怎麼安排取餐動線？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "餐點、餐具與飲品依取用順序配置，桌邊保留拍照與通行空間；主要流程結束後再引導取餐，也較容易維持桌面完整。"
      }
    },
    {
      "@type": "Question",
      "name": "詢問畢業典禮甜點桌前要準備哪些資訊？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "先提供活動地點、預計人數、成人與孩子比例、流程時間、餐點方向及場地設備，就能開始整理菜單與桌面配置。"
      }
    }
  ]
}
```
