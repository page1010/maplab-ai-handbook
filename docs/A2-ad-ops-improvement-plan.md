# A2 廣告能力進化計畫

版本：v0.1-draft | 建立：2026-07-03 | 狀態：**草案，待 Owner 審定**
維護：A2 + A0 調度

---

## 背景：對標目標工作流

我們對標的是一個 API 驅動的廣告自動化工作流：

```
安索夫矩陣 × MOT × 受眾溫度
        ↓
    受眾包規劃（Lookalike / 再行銷 / 興趣）
        ↓
Meta Marketing API 批量盤點 / 重組 / 寫入
        ↓
戰情中心：廣告成效 + 成交數據統一視圖
```

這個工作流的核心是「矩陣驅動策略 → API 批量執行」，速度快，但缺少合規閘門，屬於 fire-and-forget 模式。

---

## 我方現況盤點

### 已有（優勢層）

| 能力 | 說明 |
|---|---|
| A2 + 治理閉環 | 缺陷棘輪閘門、獨立驗證、maker/checker 架構 |
| Codex / agy | 本地模型輔助，省 token，不依賴雲端額度 |
| SEO factory | 內容生產 + 閘門（`seo_publish_gate.py`）已跑通 |
| 素材表 `asset_conversion_manifest` | 自帶 `ad_ok` / `needs_face_crop` / `landing_slug` / `cluster` 廣告合規欄位，閘門可直接讀 |
| 安全架構 | 憑證走 MCP/Notion vault，不手填；閘門強制擋批量寫入前的合規審查 |

### 缺少（差距層）

| 缺口 | 說明 |
|---|---|
| ① 廣告 API 未接 | Meta Marketing API / Google Ads API 尚未連通，目前只能手動操作廣告後台 |
| ② 無安索夫 × 溫度受眾矩陣 | 策略到素材到受眾的對應關係未系統化，見 `docs/ansoff-mot-audience-matrix.md`（Phase 0 產出） |
| ③ 戰情中心 B+C 行銷資料未統一 | 廣告成效（Meta/Google）、SEO 流量（GSC/GA）、成交（TimeTree）三源未整合 |

---

## 我方核心優勢（對比 fire-and-forget）

> **「又快又安全」勝過「只快不管」。**

1. **獨立驗證閘門**：批量廣告寫入前，強制過合規（`ad_ok` / `needs_face_crop`）、預算上限、受眾重疊、矩陣對齊四道閘。對方的 fire-and-forget 跑得快，但一旦出錯（上了不合規的圖、受眾重疊燒錢）要人工善後。

2. **素材表自帶廣告合規欄位**：`asset_conversion_manifest` 在素材生產階段就標好 `ad_ok` / `ad_restriction` / `needs_face_crop`，廣告閘門可直接機讀，不需重複人工審查。

3. **maker/checker + 本地模型**：A2 產受眾包草案（maker），閘門獨立跑合規（checker），本地模型省 token，整套不依賴 Claude API 額度。

---

## 分階段計畫

### Phase 0 — 建矩陣物件（可立即啟動，不需廣告帳號）

**目標**：把安索夫 × MOT × 受眾溫度 × 素材 cluster 對應關係寫成可機讀的文件/物件。

**產出**：
- `docs/ansoff-mot-audience-matrix.md`（本 Phase 草案，見同目錄）
- 未來可轉成 JSON/YAML，供 A2 廣告規劃腳本讀取

**負責**：A2 產草案 → Owner 審定 → A0 納入調度

**狀態**：草案已建立，待 Owner 審定。

---

### Phase 1 — 唯讀 Ads MCP 盤點（需廣告帳號）

**目標**：接通 Meta Marketing API（或 Google Ads API），唯讀掃描現有廣告受眾包、素材使用狀況、花費分布。

**前置條件（Owner 行動）**：
- 確認主要付費廣告平台（Meta? Google? 兩者皆用?）
- 提供廣告帳號 ID（不手填憑證，走 MCP/app 層 OAuth）

**產出**：
- 現有廣告受眾包清單
- 素材使用分布（哪些 cluster 的素材有跑廣告）
- 與矩陣對齊的缺口分析

**負責**：A2 + A0（API 接通後）

---

### Phase 2 — 廣告發布閘門（設計先於執行）

**目標**：在任何廣告批量寫入之前，建立類似 `seo_publish_gate.py` 的廣告版閘門 `ad_publish_gate.py`。

**閘門必查項目**：
1. 素材合規：`ad_ok = yes`、`needs_face_crop = no`、`needs_logo_crop = no`
2. 預算上限：單次批量寫入不超過 Owner 設定的日預算上限
3. 受眾重疊：新受眾包與既有包重疊率低於閾值（避免自我競標）
4. 矩陣對齊：素材 cluster 與安索夫格子/受眾溫度一致

**原則**：閘門由 checker 角色跑（非 maker A2 自跑），FAIL 即停，不靜默跳過。

---

### Phase 3 — 經閘門批量寫入

**目標**：Phase 2 閘門 PASS 後，A2 可經 Meta/Google API 批量建立/更新廣告受眾包與素材。

**前置條件**：Phase 1 + Phase 2 完成，Owner 核准執行範圍。

**安全邊界**：
- 不自動調整日預算
- 不自動暫停既有廣告
- 不刪除受眾包
- 每次批量操作後回報 diff（新增了什麼、改了什麼）

---

### Phase 4 — 戰情中心統一 B+C 資料

**目標**：把廣告成效（Meta/Google）、SEO 流量（GSC/GA）、成交資料（TimeTree 日曆）接進同一個儀表板，A0 可一眼看到全行銷漏斗。

**資料來源對照**：

| 資料類型 | 來源系統 | 接通方式 |
|---|---|---|
| 廣告成效（曝光/點擊/花費/轉換） | Meta Ads / Google Ads | Phase 1 API |
| SEO 流量（搜尋排名/點擊/頁面流量） | GSC + GA | 現有 A2 MCP |
| 成交 / 詢價紀錄 | TimeTree / 訂單系統 | 待確認接口 |

---

## 待 Owner 確認事項

| # | 待確認 | 影響哪個 Phase |
|---|---|---|
| 1 | **主要付費廣告平台**：Meta 優先？Google 也要？順序？ | Phase 1 |
| 2 | **廣告帳號 ID**（不手填，走 OAuth MCP） | Phase 1 |
| 3 | **日預算上限**（廣告閘門的預算護欄數字） | Phase 2 |
| 4 | **TimeTree 成交資料接口**（API 或手動匯出？） | Phase 4 |
| 5 | **`ansoff-mot-audience-matrix.md` 草案審定** | Phase 0 解鎖 Phase 1 |

---

## 變更紀錄

| 版本 | 日期 | 變更 | 來源 |
|---|---|---|---|
| v0.1-draft | 2026-07-03 | 初版草案 | Owner 親口指示骨架，A2 填入 |
