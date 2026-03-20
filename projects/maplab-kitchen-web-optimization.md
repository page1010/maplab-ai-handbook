# Kitchen Web Optimization — 角色定位與技術文件

版本：v1.0 | 建立：2026-03-20 | 更新：2026-03-20

## 你是誰（接手前先讀這段）

- **角色**：A2/A3 SEO & Ads Team
- **任務**：MAPLAB Kitchen 官網 SEO、手機 RWD 優化、Landing Page 改善、PageSpeed 提升
- **網站**：https://www.maplabkitchen.com/
- **GitHub**：https://github.com/page1010/maplab-kitchen-web-optimization（私有）
- **進度**：docs/optimization-log.md（web-optimization repo 內）
- **不在範圍**：ERP、相簿整理、AI 回覆 — 那是 A4/A5/A7 的事

## 技能清單（開工前翻一下）

完整技能庫：skills/superpowers-guide.md

| 情境 | 用哪個 Skill |
|------|-------------|
| SEO 策略分析 | strategic-review-guide |
| 廣告成效追蹤 | sheets-tracking-guide |
| 需求模糊 | brainstorming |
| 要寫計畫 | writing-plans |
| 遇到 Bug | systematic-debugging |
| 說完成前 | verification-before-completion |

## 專案概況

MAPLAB Kitchen 是台南外燴品牌的官方網站，基於 WordPress + Elementor 架構。本專案負責官網的 SEO 優化、手機 RWD 體驗改善、Landing Page 轉換率提升、以及 PageSpeed 效能優化。

## 技術架構

| 項目 | 說明 |
|------|------|
| CMS | WordPress + Elementor |
| 快取 | WP Rocket（JS defer/delay 已啟用）|
| 圖片格式 | AVIF（Imagick q50 壓縮）|
| 品牌色 | 棕金 #8B5E3C |
| 正式首頁 | page-id-1250（原草稿副本，已發布上線）|
| 備份草稿 | page-id-42（舊版備份，已轉為草稿）|

## Repo 結構

```
maplab-kitchen-web-optimization/
├── css/                  ← 全站 CSS 樣式（RWD、Sticky Nav、品牌色）
├── docs/
│   └── optimization-log.md  ← 優化紀錄（23 項已完成）
└── README.md
```

## 已完成優化項目（截至 2026-03-18）

共 23 項已完成，以下為關鍵里程碑：

| # | 項目 | 影響 |
|---|------|------|
| 1-10 | 草稿副本 + CSS Anchor + 快速導覽 + RWD + Landing Page 重排 | 基礎架構完成 |
| 11 | 首頁上線切換（page-1250 → 正式首頁）| 上線 |
| 12 | IG 客戶見證卡片化（8 張卡片 grid）| 信任感提升 |
| 13 | Hero 社會認同數據列（200+/50+/98%/10年）| 轉換率提升 |
| 14 | PageSpeed 優化（Mobile 25 → 70）| 效能大幅改善 |
| 15-16 | LINE CTA 整理（6→4 個）+ 按鈕色改品牌棕金 | UX 精簡 |
| 17-20 | Accessibility 修復（對比度、aria-label、H5→H3）| A11y 提升 |
| 21-23 | LCP preload + AVIF q50 壓縮 + CLS 修復 | 效能進一步優化 |

## 當前成效

| 指標 | Before | After |
|------|--------|-------|
| Mobile Performance | 25 | 70-75 |
| Best Practices | — | 100 |
| SEO Score | — | 100 |
| LCP | 7.9s | ~4.6s（lab）/ 1.5s（field）|

## Landing Page 重排邏輯

- **舊順序**：Hero → 服務卡 → 菜色 → 評價 → CTA → 快速導覽 → 流程 → FAQ
- **新順序**：Hero → 服務卡 → 菜色 → 快速導覽 → 流程 → 評價 → FAQ → CTA
- **邏輯**：AIDA（問題認同 → 方案說明 → 信任建立 → 消除疑慮 → 行動）

## CSS 關鍵規則

| 規則 | 值 |
|------|-----|
| 連結顏色 | #8B5E3C 棕金色 |
| CTA 按鈕 | #8B5E3C 品牌棕金（從 LINE 綠 #06C755 改）|
| 快速導覽 | Sticky + blur |
| 手機圖高 | max-height: 70vh |
| 桌機行寬 | max-width: 780px |

## 待辦（未來優化方向）

- LCP 進一步壓縮（Mobile Performance 75 → 85+）
- Accessibility 88 → 95+（對比度 + 連結名稱 + iframe 修正）
- JS defer + TTFB 優化

## 已知約束

- ⚠️ 所有 CSS/Elementor 修改須在草稿預覽確認後才上線
- ⚠️ 品牌色統一為 #8B5E3C，不可自行更換
- ⚠️ 正式首頁為 page-id-1250，不可隨意切換
- ⚠️ WP Rocket 快取需在修改後手動清除

## 與其他 Agent 的關係

| Agent | 協作點 |
|-------|--------|
| A4 Pipeline | 提供 WebP/AVIF 優化後的圖片素材 |
| A2/A3 SEO & Ads | 共用 SEO 關鍵字策略、廣告 Landing Page 需對齊 |
| A1 Handbook | 進度回寫 handbook（本檔案 + CURRENT_STATUS）|

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-20 | 初版建立 — 從 web-optimization repo 彙整 23 項優化紀錄 | A1 Handbook Agent |
