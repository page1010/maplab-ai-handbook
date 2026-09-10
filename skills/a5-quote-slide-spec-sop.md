# 報價 Slide 規格與 SOP v1.0 — 2026-09-10

Owner 交辦「做出 slide 制定規格與 SOP」；加購項頁已由 Owner msg 5095 核定。
本規格為**所有 agent 製作對客報價簡報的唯一依據**，取代任何自行發想的版面。
數字與內容來源一律照 `skills/a5-quote-margin-path-sop.md`（報價毛利路徑 SOP）。

## 0. 為什麼是 Slide

文學館成交案（TWD 23,000）兩個報價版本都是 **Slide＋Sheet 雙格式**對外發送
（slides-quotation-system.md SECTION 12.2），Slide 是正式產出物，不是加分項。

## 1. 版面規格（7 頁，Owner 核定版）

| 頁 | 內容 | 必要元素 |
|---|---|---|
| 1 | 封面 | MAP LAB KITCHEN／旅圖 logo、案名、活動日期、`Quotation` |
| 2 | 客戶資訊 | Client／Date／Event／Guests／Contact／Address（12.4 六欄） |
| 3 | 菜單 SAVORY | 品項名＋數量＋品項照（A4 相片庫） |
| 4 | 菜單 DESSERT／BEVERAGES | 同上；飲品列桶裝款式 |
| 5 | 費用摘要 | Item／Amount (TWD)／Notes |
| 6 | **加購項（Owner 5095 核定）** | 攝影／花藝／喇叭／插旗／道具／剪綵**併入同一張報價**不另出版，**配一張示意圖**說明加購內容 |
| 7 | 服務範圍＋條款＋匯款 | ★七點、三級取消條款、中國信託／**圖蕾實業社**／222540645172 |

## 2. GAS 佔位符命名表（模板文字用 `{{}}`，圖片用 Alt Text）

| 佔位符 | 來源 |
|---|---|
| `{{CLIENT}}` `{{EVENT}}` `{{EVENT_DATE}}` `{{GUESTS}}` `{{CONTACT}}` `{{ADDRESS}}` | QUOTE_DRAFT 客戶區 |
| `{{SAVORY_ROWS}}` `{{DESSERT_ROWS}}` `{{BEVERAGE_ROWS}}` | QUOTE_DRAFT 品項區（品項名＋數量） |
| `{{TOTAL_PIECES}}` `{{PIECES_PER_GUEST}}` | 件數合計／人均件數 |
| `{{FEE_ROWS}}` `{{TOTAL_TWD}}` | 費用摘要（金額一律 TWD） |
| `{{ADDON_ROWS}}` | 加購項；未回報價的填「待廠商回覆」 |
| `{{DEPOSIT}}` | 訂金（預設 3,000，另有裁定時覆寫） |
| 圖片 Alt Text `item::<item_id>` | ASSET_MASTER → Drive file id |
| 圖片 Alt Text `addon::diagram` | 加購項示意圖（見 §3） |

## 3. 加購項示意圖規格（Owner 5095 指定）

- 版位：第 6 頁右半或下半，佔頁面約 40%。
- 內容：中央「活動當天」，環繞六個加購模組（攝影／花藝／音響／插旗／手拿道具／剪綵），
  各配一句話說明「客人得到什麼」，**不放價格**。
- 配色（`skills/maplab-visual-spec.md`）：底 `#FAF7F2` 奶油白、卡片 `#EDE5D8` 暖米、
  文字 `#3A3A2E` 深橄欖、強調 `#7A5C3E` 棕褐、圖示 `#8FA68E` 鼠尾草。
- 可重用檔：`assets/quote-slide/addon-diagram.svg`（本次產出，改文字即可複用）。

## 4. 製作流程

1. 依報價毛利路徑 SOP 產內部毛利表（成本查 A4 Sheet `Items` 分頁）。
2. QUOTE_DRAFT 填客戶區與品項區。
3. GAS T-SLIDE-004 替換佔位符（尚未實作前：人工複製文學館成交版 Slide 改內容）。
4. 匯出 PDF → **標「草稿，未對客戶發出」給 Owner/Mina 過目**。
5. Owner/Mina 核可後才對客發送。

## 5. 禁止事項（違反＝作廢重做）

- 成本、毛利率、item_id 等內部欄位出現在 Slide。
- 幣別寫 NTD（一律 TWD）。
- 未授權或非本案相片；查無相片留白，不借圖。
- 加購項另出一張報價單（Owner 已裁定：併入同一張）。
- agent 自行對客發送或承諾檔期。
