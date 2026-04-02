# Slide 動態連結需求 — 2026-04-02

> 來源：Owner 提供文學館實際報價 Slide + 使用者需求
> 關聯：T-A5-004

---

## 真實案例：WenXueGuan_20260527_23000

- Slide ID: 16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo
- 23 張投影片
- 結構：封面(1) → 品牌介紹(2) → 服務類型(3) → 實績(4) → 優勢(5) → 信賴夥伴(6-7) → **Menu Showcase(8-N)** → 流程/CTA(尾頁)

### Menu Showcase 格式（每頁 6 品項，3x2 grid）

每個品項 slot：
- 照片（有的是真實照片覆蓋在[Photo]佔位上，有的還是[Photo]佔位）
- 中文品名
- 英文品名 + 數量 (qty)

### 確認的品項範例（slide 8-9）

| 中文 | 英文 | qty | 有照片 |
|------|------|-----|--------|
| 澳式塔塔海老炸銀排小漢堡 | Aussie Shrimp Burger | 20 | ✅ |
| 義式羅勒青醬雞肉三明治 | Basil Pesto Chicken Sandwich | 20 | ✅ |
| 義式帕瑪季節番茄手工普切塔 | Seasonal Tomato Bruschetta with Parmigiano | 20 | ❌ [Photo] |
| 泰式綠咖哩雞奶香手工小鹹派 | Thai Green Curry Chicken Pie | 15 | ✅ |
| 七股虱目魚香腸灸烤小串 | Milkfish Sausage Skewer | 25 | ✅ |
| 焦糖綜合堅果小塔 | Caramelized Mixed Nut Tart | 20 | ✅ |

---

## Items 表 K 欄現況

- K1 header = `image_url`
- 部分品項有 WordPress .avif URL（格式：`https://www.maplabkitchen.com/wp-content/uploads/2025/06/{name}.webp.avif`）
- 部分品項有 Google Photos URL（格式：`https://lh7-rt.googleusercontent.com/...`）
- 部分品項的 K 欄被混用為活動紀錄（如 `2025/11/21 1200/10人`）
- 需要清洗：把非 URL 的值搬到 J 欄 note，K 欄只放圖片 URL

---

## Owner 需求摘要

1. **QuoteForm 加勾選「是否產出 Slide 提案」**
2. **動態連結的是 Menu Showcase 頁** — 根據 QUOTE_DRAFT 上選的品項，自動生成 Menu Showcase 頁
3. **封面、品牌介紹、服務、優勢等頁不變** — 直接複製 Slide 模板的固定頁
4. **品項照片來源 = Items K 欄 image_url** — 有照片用照片，沒照片用 [Photo] 佔位
5. **覆蓋圖層問題** — 有些照片是 Owner 手動覆蓋在佔位形狀上的，不是透過 Alt Text 替換
6. **.avif/.webp 格式** — WordPress 的圖片是 .webp.avif，Google Slides insertImage 可能不支援，需要用 Google Drive 原圖或轉檔

---

## Slide 模板資訊

| 項目 | 值 |
|------|-----|
| 模板 Slide ID | 1rRxwPK9Nsgb7oqoRiUOCFqu3iGNuw_zRKW3zeHbdHBY |
| 真實案例 Slide ID | 16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo |
| Menu Showcase 佔位 | {{PHOTO}} + {{ITEM_NAME}} |
| 每頁品項數 | 6（3x2 grid） |

---

## 實作規劃

### Phase 1：Items K 欄清洗
- [ ] K 欄非 URL 的值搬到 J 欄 note
- [ ] K 欄統一只放圖片 URL
- [ ] 盤點：有 URL 的品項數 vs 無 URL 的品項數

### Phase 2：Google Drive 品項照片資料夾
- [ ] 在 MAPLAB_DATA/MAPLAB_ASSETS/ 下建「item_photos」子資料夾
- [ ] 從 WordPress .avif URL 或 Google Photos URL 取得原圖，存到 Drive
- [ ] K 欄更新為 Drive 圖片 URL（Slides insertImage 用 Drive URL 最穩定）

### Phase 3：createSlides.gs
- [ ] 複製 Slide 模板
- [ ] 讀 QUOTE_DRAFT 選定品項
- [ ] 從 Items K 欄取照片 URL
- [ ] 生成 Menu Showcase 頁（每 6 品項一頁）
- [ ] 替換 {{PHOTO}} 和 {{ITEM_NAME}}

### Phase 4：QuoteForm 整合
- [ ] QuoteForm 加 checkbox「產出 Slide 提案」
- [ ] createQuote() 有 Slide 選項時，同時呼叫 createSlides()
- [ ] 報價單 + Slide 提案存到同一個 Drive 資料夾

---

## Drive 資料夾整合規劃

```
MAPLAB_DATA/（19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt）
├── 📋 進行中_Active Orders/
│   └── 2026/
│       └── 20260527_文學館/ ← 報價單 + Slide 提案都在這
├── ✅ 已結案_Completed Orders/
├── ❌ 未成交_Lost Quotes/
├── MAPLAB_ASSETS/
│   └── item_photos/ ← 品項照片（新建）
└── ai_reply_system/
```

等 Code.gs v3.1 部署確認後，DRIVE_FOLDER_ID 改為 `📋 進行中_Active Orders` 的 ID。
