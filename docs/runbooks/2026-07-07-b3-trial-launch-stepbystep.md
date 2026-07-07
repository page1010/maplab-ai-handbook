# B3 HR/會議茶點線 — Week 1 試跑操作稿（Owner 可直接照貼）

版本：v1.0 | 建立：2026-07-07 | 依據：`docs/ad-funnel-battle-plan.md` §5（SEO 三人小組 07-07 覆核後修訂版）+ `docs/ad-buildout-plan.md` P1
維護：A2 | 狀態：**操作稿，Owner 依此在 Meta/Google 後台手動建立**（廣告帳號無 API/MCP 連接器，需人工操作）

---

## 為什麼是這個配置（一句話背景）

日預算 NT$100，Codex + Antigravity 唯讀評審一致認為均分兩個受眾包（corp+edu）太薄，訊號會被稀釋。已採納「Week 1 集中投放 corp 線」的較保守版本（Antigravity 意見），edu 線暫緩，等 corp 訊號夠乾淨再考慮加開。

---

## 1. Meta 廣告受眾包設定

**帳號**：318634712

**受眾包名稱**：`cold-b-meeting-corp`

| 設定項 | 值 |
|---|---|
| 受眾類型 | 職業興趣受眾（非 Lookalike，種子資料不足時用職業興趣） |
| 職業定向 | 人力資源、行政助理、秘書、辦公室主任 |
| 興趣定向 | 企業培訓、員工活動、企業內訓 |
| 年齡 | 25–55（涵蓋 HR/行政職涯常見年齡層） |
| 地區 | 大台南（含台南市全區，依實際服務範圍） |
| 語言 | 繁體中文 |
| **本輪不建立** | `cold-b-meeting-edu`（教育/研究單位）——暫緩，等 corp 線第 3-4 週評估後再決定是否加開 |

**日預算**：**NT$100/天**（Week 1-2 全數投入 corp 線，不分兩包）

**素材**：`maplab-corporate-forum-cathay-wealth-management-hero.webp`（已驗 `ad_ok=yes`）

**廣告文案**（品牌語氣，可直接照貼）：
```
主文案：200 人財富管理論壇的茶點，從詢價到進場只要 5 天。
說明：企業會議、教育訓練、員工活動的茶點配置，我們習慣先確認人數與時間，再談菜單方向。
CTA 按鈕：了解更多
```

**CTA 導向**：`https://www.maplabkitchen.com/hr-admin-meeting-catering-guide-tainan/`（見下方 UTM）

---

## 2. Meta 溫層受眾包（Day 1 就建，不要等 Week 2）

> 三人小組評審共識：Pixel 已確認安裝、ThruPlay 受眾現有資料可用，溫層受眾池要及早開始累積，等到原案的 Week 2 才建等於白白流失早期訪客。

| 受眾包名稱 | 建立條件 | 有效期 |
|---|---|---|
| `warm-website-visitors` | 網站訪客（任何頁面，Meta Pixel） | 30 天 |
| `warm-landing-visitors-hr` | 看過 `/hr-admin-meeting-catering-guide-tainan/` 或 `/corporate-tea-party-desserts/` ≥ 30 秒 | 14 天 |

本輪 Week 1-2 只建立受眾池，**不編列溫層廣告預算**（NT$100/天全部給冷層 corp），溫層廣告等冷層有初步訊號、且受眾池規模足夠（建議 ≥1,000 人）後再啟動，避免受眾規模過小導致投遞失敗。

---

## 3. Google Ads 關鍵字加碼清單

**Campaign**：Campaign4 高意圖_南台灣外燴（現有活動，加關鍵字，不新建 campaign）

**新增關鍵字**（比對詞，精準比對優先）：
```
"台南茶會點心推薦"
"台南會議茶點外燴"
"台南點心外燴"
```

**出價調整**：
- 桌機出價 **+25%**（實測轉換偏桌機）
- 手機出價 **-20%**

**Landing page**：`https://www.maplabkitchen.com/hr-admin-meeting-catering-guide-tainan/`（主）或 `https://www.maplabkitchen.com/corporate-tea-party-desserts/`（次）

---

## 4. UTM 命名（廣告連結務必帶上，否則無法追蹤閉環）

**Meta 廣告連結**：
```
https://www.maplabkitchen.com/hr-admin-meeting-catering-guide-tainan/?utm_source=meta&utm_medium=paid_social&utm_campaign=b3-hr-tea&utm_content=forum-hero-v1
```

**Google Ads 連結**（每個關鍵字對應 utm_term）：
```
https://www.maplabkitchen.com/hr-admin-meeting-catering-guide-tainan/?utm_source=google&utm_medium=paid_search&utm_campaign=b3-hr-tea&utm_term=台南茶會點心推薦
https://www.maplabkitchen.com/hr-admin-meeting-catering-guide-tainan/?utm_source=google&utm_medium=paid_search&utm_campaign=b3-hr-tea&utm_term=台南會議茶點外燴
https://www.maplabkitchen.com/corporate-tea-party-desserts/?utm_source=google&utm_medium=paid_search&utm_campaign=b3-hr-tea&utm_term=台南點心外燴
```

---

## 5. 評估時程與 KPI（3-4 週，非原案 2 週）

> 評審共識：NT$100/天量級下，2 週的詢價筆數基期太小，「詢價轉換率 > 3%」這種百分比容易被 1 筆詢價左右而失真。KPI 改分階段看，且延長評估期。

| 週次 | 這週看什麼 | 不用看什麼 |
|---|---|---|
| Week 1-2 | 冷層：link CTR、CPC、landing page view（不是 ThruPlay——本輪素材是靜態圖不是影片） | 轉換率（冷受眾本來就不轉） |
| Week 1-2 | 溫層受眾池是否累積到有意義規模（建議 ≥1,000） | 溫層廣告成效（本輪未編列溫層預算） |
| Week 3-4 | 熱層：qualified LINE 詢價「筆數」+ CPL（不是只看百分比） | — |
| Week 3-4 | 若溫層受眾池規模足夠 → 啟動小額溫層廣告測試 | — |

**複製結構到 B1/B2/B4/B5 的判斷時機**：Week 3-4 數據出來後，若冷層 CTR/CPC 合理、溫層池已建立、熱層有 qualified 詢價出現 → 才考慮複製；若訊號不清楚，先調整素材/文案，不要動受眾結構或貿然加開 edu 線。

---

## 6. 前置檢查清單（開始前逐項確認）

- [ ] Meta 帳號 318634712 有受眾包建立權限
- [ ] Google Ads Campaign4 有出價調整權限
- [ ] GA4 事件確認能收到 UTM 帶入的流量（先手動點一次帶 UTM 的連結，去 GA4 即時報告核對）
- [ ] WP 1992（行政外燴推薦 HR 活動餐點規劃）精選圖已補上——**明天照片評分後由 A0 補**，補上前廣告先導向 `corporate-tea-party-desserts`（已有完整內容）
- [ ] 素材 `maplab-corporate-forum-cathay-wealth-management-hero.webp` 已確認 `ad_ok=yes`

---

## 相關文件

- 策略依據：`docs/ad-funnel-battle-plan.md` §5（FDE B3 試跑計畫）、§7（SEO 三人小組評審制度）
- 受眾/素材完整規劃：`docs/ad-buildout-plan.md`
- 評審紀要：`workbook/reviews/JOB-A2-SEO-TRIO-REVIEW-20260707/decision_summary.md`
