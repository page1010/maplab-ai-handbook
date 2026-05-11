# A2/A3 WordPress Page Pack

這份文件把候選 Landing Page 收斂成一致格式。
注意：它不是叫你一次把 8 類都做成主頁。
目前第一批優先順序以 `docs/a2a3/b2b-case-inventory.md` 為準，先跑 B2B 四個叢集。

## 必備欄位

每個頁面都要有：

- H1
- 場景 / 活動類型
- 適合人數
- 預算區間
- 真實案例區
- FAQ
- LINE CTA
- 內部連結
- SEO title / description / slug

## 候選頁面（不等於全部都要獨立主頁）

| 頁面 | Slug | 對應真實場景 | 主目的 |
|------|------|--------------|--------|
| 台南開幕茶會外燴 | `/opening-event-catering-tainan/` | 診所開幕、品牌開幕、清清顏、公司開幕 | B2B 高價值詢問 |
| 台南會議茶點外燴 | `/meeting-refreshment-catering-tainan/` | 成大會議、科林研發、學校講座、企業會議 | 平日高密度成交 |
| 台南品牌活動外燴 | `/brand-event-catering/` | 賞車、建案發表、展覽開幕、VIP 接待 | 品牌型案件 |
| 台南企業外燴／公司茶會 | `/catering-corporate-tainan/` | 公司春酒、公司茶會、企業活動 | 主樞紐頁 |
| 台南學校活動外燴 | `/school-event-catering-tainan/` | 成大、南臺、長榮、崑山、畢典 | 校園 / 機構案 |
| 台南週歲生日外燴 | `/catering-birthday-party-tainan/` | 週歲、生日、抓周、家庭聚會 | 高轉換現金流 |
| 台南婚禮證婚外燴 | `/catering-wedding-tainan/` | 婚禮、證婚、迎賓茶點、Candy Bar | 婚禮長線資產 |
| 台南宗教儀式外燴 | `/religious-event-catering-tainan/` | 神明安座、感恩茶會、廟宇儀式 | 長尾測試頁 |

## 每頁結構建議

1. 開頭先講場景，不急著講價格
2. 中段放「這場活動通常在意什麼」
3. 再放餐點 / 動線 / 服務
4. 用真實案例收尾
5. FAQ 補搜尋意圖
6. CTA 指向 LINE 與聯絡方式

## 每個 WordPress 資料夾建議檔案

- `brief.md`
- `draft.md`
- `seo.md`
- `outline.md`
- `internal_links.md`
- `rankmath_payload.json`
- `source_bridge.md`
- `preview.html`
- `assets/`

## SEO 與內連規則

- 企業頁優先連企業 / 開幕 / 會議 / 品牌活動
- 家庭頁優先連週歲 / 生日時序 / 家庭聚會
- 婚禮頁優先連婚禮 / 戶外婚禮 / 迎賓茶點
- 不要全部導首頁
- Rank Math 的核心欄位要先寫好再交給 OpenClaw 或 WP REST API

## A2/A3 的寫法

- A2 先做頁面與 SEO 架構
- A3 再把素材與廣告語氣對齊
- 每頁都要回到案例和 CTA
