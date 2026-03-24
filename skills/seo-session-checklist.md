# seo-session-checklist.md — A2/A3 每次 Session 標準流程
> 版本：v1.0 | 建立：2026-03-24 | 維護者：A2/A3
> 何時用：每次 A2/A3 agent 開工時必須執行，不可跳過

---

## 目的

建立 SEO & Ads 部門的標準作業紀錄，確保每次 session 都有數據基準線、問題被追蹤、進度被歸檔。

---

## Phase 1：SEO 健康檢查（每次必做）

### 1.1 Rank Math SEO Performance（30 天）

到 WordPress > Rank Math SEO > Analytics > SEO Performance，記錄：

```
【SEO Performance 快照 — YYYY-MM-DD】
Search Traffic:    ___（▲/▼ ___）
Total Impressions: ___（▲/▼ ___）
Total Keywords:    ___（▲/▼ ___）
Total Clicks:      ___（▲/▼ ___）
CTR:               ___%（▲/▼ ___）
Average Position:  ___（▲/▼ ___）
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

### 1.4 SEO 分數分佈

到 Site Analytics tab，記錄：

```
【SEO 分數分佈 — YYYY-MM-DD】
Good:    ___
Fair:    ___
Poor:    ___
No Data: ___
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

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-24 | 建立 A2/A3 每次 Session 標準檢查流程 + 首次基準線 | A2 |
