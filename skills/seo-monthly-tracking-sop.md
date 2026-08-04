# skills/seo-monthly-tracking-sop.md — 月度 SEO 追蹤報表 SOP（Search Console → A2/A3 行動）

> 狀態：DRAFT（2026-08-02）。把每月 Search Console 內容成效變成固定追蹤表，讓數據驅動 A2(內容)/A3(投放)。
> 報表模板：`MAPLAB_SEO_monthly_tracker.xlsx`（本輪產出，可轉 Google Sheet）。站台：maplabkitchen.com。

## 1. 資料怎麼拉（先確認）

| 方案 | 內容 | 需要什麼 | 適用 |
|---|---|---|---|
| **A｜Search Console API（推薦）** | `searchAnalytics.query`：clicks / impressions / CTR / position，**by page & by query，可回溯約 16 個月** → 自動逐月填表 | Google 帳號**加 `webmasters.readonly` scope**（目前 token 僅 Drive+Sheets）；一支排程腳本每月拉 | 要「自動更新 + 過往熱圖」的正解 |
| **B｜解析月報 email（免加權限，先跑）** | 把每月 Search Console『內容成效』email 的成長/最佳頁數字貼進表 | 無（現況即可） | 立即先動、月數累積 |
| GA4（選配） | 工作階段/來源/轉換，補「進站後行為」 | 另加 `analytics.readonly` scope + GA4 property | 之後評估 |

**現況判斷**：目前**沒有 Search Console MCP**，Google token 只有 Drive+Sheets。→ **先用方案 B 起跑**（本表已 seed 當期數字），同時請 Owner 加一次 scope 解鎖方案 A 的自動化與回溯。

## 2. 報表結構（模板分頁）

1. **本期重點**：① 成長最多(MoM Δ) ② 成效最佳(clicks) ③ 新進流量 ④ 衰退警示。
2. **頁×月追蹤**：各頁每月 clicks，MoM Δ 公式，**色階＝點擊熱圖（過往點陣圖）**。
3. **Query×月熱圖**：主要關鍵字每月 clicks 色階。
4. **數據→行動**：每月由誰、看哪指標、觸發什麼行動。
> 米黃底＝每月輸入格；其餘公式/色階勿手改。新案例頁上線就在「頁×月」加一列。

## 3. 每月 數據→行動（A2/A3 追蹤機制，重點）

| 訊號 | 指標 | 負責 | 行動 |
|---|---|---|---|
| 某頁 clicks 領先（如 cost-guide 57） | 本期重點② | **A2** | 補該主題群內鏈、擴同主題子頁，把權重集中到贏家 |
| 某頁 MoM 大增（cost-guide **+20**） | 本期重點① | A2/A3 | A2 加碼同類內容；A3 對該關鍵字加投放測試 |
| 個案頁在漲（週歲 498 **+8**） | 頁×月追蹤 | **A2** | 多產同類個案（走 `case-study-production-sop`），內鏈回 pillar |
| 新進頁/字竄出 | 本期重點③ | A2/A3 | A2 補一篇承接內容；A3 開新受眾/素材測試 |
| 某頁 MoM 連兩月降 | 頁×月 MoMΔ | A2 | 改寫/合併/補內鏈；查互搶（seo-keyword-map §5） |
| 高曝光低點擊（CTR 低） | API CTR | A2 | 改標題/描述（RankMath）提點閱 |
| 高意圖字有量 | Query×月熱圖 | **A3** | 對該字加碼投放、對齊 landing |

**節奏**：每月 5 號前更新報表 → A2/A3 各挑 1–2 個訊號轉成當月行動 → 記進「數據→行動」新列（形成閉環，不只看報表）。
**本期即可動作（範例）**：cost-guide 在贏 → A2 建「外燴費用」主題群內鏈；週歲 498 在漲 → A2 排週歲個案；首頁穩 → 維持。

## 4. 落地 / 自動更新

- MVP：本 xlsx（可上傳成 Google Sheet 供 A2/A3 共編）。
- 自動化（方案 A 解鎖後）：一支 `gsc_monthly_pull.py`（`searchAnalytics.query` by page+query，寫入 Sheet/表），接 launchd/cron 每月 1 號跑；模板的輸入格改由程式回填。

## 5. 要 Owner 做的（若走方案 A）

**加一次授權**：Google 帳號重新授權，勾選 **Search Console 唯讀（`https://www.googleapis.com/auth/webmasters.readonly`）**（GA4 另加 `analytics.readonly`）。→ 之後全自動、可回溯 16 個月。不加也能用方案 B 手動起跑。
