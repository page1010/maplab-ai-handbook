# seo-session-checklist.md — A2/A3 每次 Session 標準流程
> 版本：v1.0 | 建立：2026-03-24 | 維護者：A2/A3
> 何時用：每次 A2/A3 agent 開工時必須執行，不可跳過

---

## 目的

建立 SEO & Ads 部門的標準作業紀錄，確保每次 session 都有數據基準線、問題被追蹤、進度被歸檔。

---

## Phase 1：SEO 健康檢查（每次必做）

### 1.1 Google Search Console 成效檢查（30 天）

到 Google Search Console > 成效，記錄：

```
【GSC 成效快照 — YYYY-MM-DD】
總點擊次數 (Clicks):        ___（▲/▼ ___）
總曝光次數 (Impressions):   ___（▲/▼ ___）
平均點閱率 (CTR):           ___%（▲/▼ ___）
平均排名 (Average Position): ___（▲/▼ ___）
```

### 1.2 關鍵字排名分佈

到 Keywords tab，記錄：

```
【關鍵字排名分佈 — YYYY-MM-DD】
Top 3:     ___（▲/▼ ___）
4-10 名:   ___（▲/▼ ___）
10-50 名:  ___（▲/▼ ___）
51-100 名: ___（▲/▼ ___）
```

### 1.3 索引狀態

到 Index Status tab，記錄：

```
【索引狀態 — YYYY-MM-DD】
已索引:       ___ 頁（___%）
找到未索引:   ___ 頁（___%）
重新導向:     ___ 頁（___%）
無法辨識:     ___ 頁（___%）
Excluded:     ___
```

### 1.4 核對廣告與 SEO 矩陣

> ⚠️ 2026-07-07 修正：本節原本引用 `ads_seo_matrix_settings.md`，這個檔案從未被建立過，是懸空參照。實際的廣告×SEO矩陣資料在下面三份文件，直接查這些，不要再找不存在的檔案：

檢查以下三份文件是否對齊：
- `docs/ad-funnel-battle-plan.md`（廣告漏斗策略、8情境對照表、B3試跑計畫）
- `docs/ad-buildout-plan.md`（Meta 受眾/素材/佈局執行細節）
- `docs/seo-keyword-map.md`（SEO 關鍵字地圖，含各群組 Pillar/Child 對齊狀態）

```
【矩陣對齊狀態 — YYYY-MM-DD】
Live URL 是否皆能正確開啟: ✅/❌
Google Ads 關鍵字是否與文章相符: ✅/❌
Meta Ads 受眾設定是否與 TA 一致: ✅/❌
```

### 1.5 內容盤點

到 Posts / Pages 列表快速確認：

```
【內容盤點 — YYYY-MM-DD】
文章數: ___
頁面數: ___
分類數: ___
新增文章（本週）: ___
```

---

## Phase 2：廣告 & 追蹤檢查（每次必做）

### 2.1 GTM 狀態

到 GTM > 工作區，記錄：

```
【GTM 狀態 — YYYY-MM-DD】
容器 ID:     GTM-T2Z52GP
目前版本:    v___（發佈日期: ___）
工作區變更數: ___
Tags 總數:   ___（暫停: ___）
Triggers 總數: ___
```

### 2.2 轉換追蹤驗證

確認以下追蹤是否正常運作：

```
【轉換追蹤狀態 — YYYY-MM-DD】
Meta Pixel (228166994905799):
  - PageView:     ✅/❌
  - Contact (LINE): ✅/❌
  - Phone Click:   ✅/❌

Google Ads (AW-821843155):
  - LINE 轉換:     ✅/❌
  - 電話轉換:      ✅/❌

GA4 (G-GCK6LKMZ25):
  - article_read_90s: ✅/❌
  - cta_visibility:   ✅/❌
  - scroll_depth_50:  ✅/❌
```

### 2.3 Google 商家檔案

到 Google 商家管理 > MAPLAB Kitchen，記錄：

```
【Google 商家 — YYYY-MM-DD】
客戶互動:  ___ 次
評論數:    ___ 則（___ 星）
產品上架:  ___ 個
```

---

## Phase 3：紀錄歸檔（每次必做）

### 3.1 更新 seo-ads-agent.md

將 Phase 1 + Phase 2 的數據寫入 `projects/seo-ads-agent.md` 的對應章節。

### 3.2 與上次對比

與上次 session 記錄對比，標注：
- 📈 明顯進步的指標（為什麼？做了什麼？）
- 📉 退步的指標（原因？需要行動嗎？）
- ➡️ 持平的指標

### 3.3 產出本次 Session Summary

```
【A2/A3 Session Summary — YYYY-MM-DD】
檢查完成: Phase 1 ✅ / Phase 2 ✅
關鍵發現:
  1. ___
  2. ___
  3. ___
本次行動:
  1. ___
  2. ___
下次建議:
  1. ___
  2. ___
```

---

## 基準線（2026-03-24 首次建立）

```
【基準線 Baseline — 2026-03-24】

SEO Performance（30天）:
  Search Traffic:    333（▲+16）
  Total Impressions: 3.27K（▲+628）
  Total Keywords:    297（▲+103）
  Total Clicks:      76（▼-12）
  CTR:               2.32%（▼-1）
  Average Position:  11.87（▲+2.62）

關鍵字排名:
  Top 3:     21（▲+11）
  4-10 名:   16（▲+9）
  10-50 名:  9（0）
  51-100 名: 2（▼-3）

索引狀態:
  已索引: 32（70%）| 找到未索引: 6（13%）| 重導向: 5（11%）| 無法辨識: 2（4%）

SEO 分數: Good 2 / Fair 54 / Poor 6 / No Data 5

內容: 57 文章 / 8 頁面 / 9 分類

GTM: v19 | Tags 15（暫停 3）| Triggers 7
Meta Pixel: Contact Active ✅ | PageView Active ✅
Google 商家: 700 互動 / 433 評論 4.1★ / 4 產品
```

---

---

## SEO 文案禁用詞清單（食安 + 法規）

> 來源：2026-04-07 Owner 紅線指令（T-A2-002）
> A2/A3 generate 任何文案前必須比對本清單

### ⛔ 絕對禁用

| 禁用詞 | 禁用原因 |
|--------|---------|
| 無麩質 / Gluten-free / 無小麥 / 低敏 | 乳糜瀉醫療等級飲食需求，廚房環境無法保證無交叉污染 → 食安通報、業務過失訴訟風險 |
| ESG / ESG 認證 / ESG 標準 / ESG 框架 | 有法規強制力的專有名詞，企業採購部門會要求第三方認證，MAPLAB 目前無相關認證 |
| SDG / 永續發展目標 / 第三方永續認證 | 同上，有國際法規意涵 |
| 認證 / 標準 / 合規（單獨使用於環保脈絡時） | 含法律意涵，易引發採購部門硬性合規查核 |

### ✅ 可以用的替代詞

| 替代詞 | 適用情境 |
|--------|---------|
| 素食友善 / 健康飲食偏好 | 一般飲食描述（非醫療級） |
| 綠色行動 / 減碳理念 | 環保概念，無法規意涵 |
| 永續理念 / 環保餐點 | 輕量化環保表達 |
| 綠色廚房 / 綠色概念 | 品牌環保形象，軟性 |
| 環保外燴 / 低碳餐點 | 社群/廣告文案用 |

### 替換規則

- `無麩質 XXX` → 直接改為品項名稱（如「手工麵包」），不留任何飲食限制暗示
- `ESG 永續餐` → `綠色餐點` 或 `環保外燴`
- `ESG 認證 / ESG 標準` → 整段刪除（認證一詞不可換詞保留）

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-24 | 建立 A2/A3 每次 Session 標準檢查流程 + 首次基準線 | A2 |
| v1.1 | 2026-04-07 | 新增 SEO 文案禁用詞清單（食安 + 法規紅線，Owner 指令） | A2 |
| v1.2 | 2026-06-02 | 退訂 Rank Math，SOP 改依賴 GSC 與 Matrix Sheet，新增 Patch Notes 規範 | A2 |
