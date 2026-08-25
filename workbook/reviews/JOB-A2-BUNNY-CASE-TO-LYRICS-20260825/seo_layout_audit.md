# 邦尼托嬰畢業典禮案例｜SEO 佈局審查

## Verdict

`CORRECT → READY_FOR_OWNER_ARTICLE_REVIEW`

本案是站上 57 篇公開文章尚未覆蓋的「托嬰畢業典禮」長尾案例，不是週歲內容的改寫。公開 REST 搜尋「畢業」為 0 篇，建議 slug `tainan-daycare-graduation-catering` 目前不存在。

## 全站位置

- 泛字入口：首頁／台南外燴指南。
- 家庭活動 pillar：`catering-one-year-old-party-tainan`（post 498）。
- 本案：獨立 case child，主意圖 `台南托嬰畢業典禮外燴`。
- 菜單支援：`tainan-custom-catering-menu`（post 698）。
- 詢問支援：`tainan-catering-line-inquiry-guide`（post 1246）。
- 分類建議：`案例分享／活動紀錄`，不歸入「週歲壽宴案例」。

## 關鍵字

- Focus：`台南托嬰畢業典禮外燴`
- 自然變體：`台南托嬰中心畢業典禮外燴`
- Secondary：`台南畢業典禮外燴`、`親子活動茶點`、`畢業典禮甜點桌`
- 搜尋意圖：正在規劃托嬰／幼兒畢業活動的主辦人，尋找餐點形式、甜點桌配置與詢問前準備項目。

## 修正完成

- 公開 H1 移除未核准的客戶具名。
- 補 post 498 情境式內鏈，並明寫托嬰畢業與週歲是不同活動。
- 補 3 題 FAQ 與同字 FAQ schema。
- 次關鍵字自然放入正文／FAQ，不堆字。
- 兩句不可驗證的感受／效果改成可觀察或較克制敘述。
- Meta 改成使用者語言並含官方 LINE 行動方向。

## 系統層發現

`automation/seo_factory/config/pillars.json` 仍把 3 個已知 404 規劃 slug 當 pillar。這是 factory 設定漂移；本案不使用該設定，另以 live REST 為準修正。

## MISSING／發布前仍需驗

- GSC query overlap 與 Rank Math score 需要 authenticated surface，不能由公開 REST 代替。
- WordPress 草稿尚未建立，因此 front render、GTM LINE click、實際 schema、media ID 尚未驗。
- 客戶具名公開授權尚未找到；文章先使用無具名版本。
