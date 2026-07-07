# 廣告漏斗作戰計畫（MAPLAB 外燴）

版本：v0.1-draft | 建立：2026-07-03 | 狀態：**草案，待 A0/Owner 定案**
維護：A2 + A0

---

## 0. 真實現況（眼見為憑，來自 Owner 帳號截圖）

### Google Ads（帳號未命名）

**現跑搜尋活動：**

| Campaign | 廣告組 / 說明 |
|---|---|
| Campaign4 高意圖_南台灣外燴 | 台南外燴、入厝外燴開幕、周歲派對 #1、周歲派對 #2 |
| Campaign5 高意圖_大臺南會展中心 | 大臺南會展中心、ESG 相關字 |
| **PMax（最高成效）** | **⛔ 已停——實際轉單成效不佳** |

**真實搜尋詞（從後台搜尋字詞報告）：**
- `台南外燴`、`台南外燴推薦`、`台南外燴 ptt`、`台南外燴餐車`、`台南外燴公司`
- `台南點心外燴`
- `台南茶會點心推薦`
- `玖二品生活外燴廚房`（競品品牌詞，有人打我們字進來看到競品）

**轉換行為**：偏桌機（desktop），手機轉換率明顯偏低。

### Meta（廣告帳號 318634712）

**現跑活動：**

| 活動名稱 | 狀態 | 成效 |
|---|---|---|
| 頂層品牌認知 週歲/家庭 冷受眾 | ✅ 在跑 | 48,436 ThruPlay，NT$0.12/ThruPlay（CP 值佳，認知效率高） |
| 品牌知名度 A 組 高收入媽媽 | ✅ 在跑 | NT$0.39/ThruPlay（相對偏高） |
| B 組互動 CTA | ⛔ 已結束 | — |

**現況診斷：**
- 全是 **C 端冷層**，無 B 端任何廣告
- **溫層 retarget 完全空白**——最痛的缺口：花錢認知卻無人承接轉化
- 無收割層（熱層）：LINE 詢價前沒有再行銷把客人拉回來

---

## 1. 核心洞察

### PMax 為什麼轉單差

外燴是「高考慮 × LINE 詢價成交」產品：

```
搜尋 → 看頁面 → 看照片/案例 → 加 LINE 詢價 → 報價溝通（2–5 天）→ 成交
```

PMax 是黑箱：它自己決定出現在哪、給誰看、用哪個素材。這個模式對「點一下立刻買」的電商很好，但對「要先加 LINE 問」的高考慮服務，黑箱無法做到：
- **Message-match**：每個受眾看到的廣告 ≠ 他關心的場景（VIP 接待 vs 周歲 vs HR 茶會是完全不同語言）
- **轉換歸因**：LINE 詢價在廣告平台上是 off-platform 行為，PMax 抓不到，優化方向就跑歪

**修法**：回到「分受眾 × 分廣告 × 分 landing」，但補完整三溫暖漏斗，不是單層打法。

---

## 2. 漏斗架構（一受眾 = 一漏斗）

```
冷層（Meta 認知）
    ↓ 進站 / 影片看到 75%
溫層（Retarget ← 目前空 = 最痛缺口）
    ↓ 填表 / 點 LINE / 看費用頁
熱層（Google 搜尋 + landing）
    ↓
LINE 詢價 → 報價溝通 → 成交
    ↓
UTM 閉環：廣告 → landing → LINE → TimeTree 成交紀錄
```

**三溫暖邏輯：**
- 冷層做**認知 + 場景植入**，不要求立刻轉換，KPI = ThruPlay/CPM
- 溫層做**再行銷 + 拉回**，已經知道你，需要一個理由回來，KPI = 點擊率/加 LINE 數
- 熱層做**收割**，他已在搜尋，直接給最相關的 landing + 明確 CTA，KPI = 詢價轉換率

---

## 3. 六大做法

### ① 一頁一意圖：Message-match

每個受眾情境有對應的 landing page，廣告文案說的場景 = landing 說的場景。  
不用同一頁打所有人。已有的 landing 頁見第 4 節情境表。

### ② 補溫層 retarget（現在最緊急）

分 B 端 / C 端兩條線，條件不同：

| | B 端溫層 | C 端溫層 |
|---|---|---|
| 觸發條件 | 看過企業外燴/茶會/HR 頁 ≥ 30 秒，或 FB 粉專互動 | 看過周歲/入厝/壽宴頁 ≥ 30 秒，或 IG 互動 |
| 再行銷訊息 | 「上次看的會議茶點配置，這邊有費用估算可以參考」 | 「上次看的周歲外燴方案，已有幾個可用檔期」 |
| CTA | → 費用估算頁 / LINE 詢價 | → LINE 詢價 |
| 受眾有效期 | 30 天 | 14 天 |

### ③ 每層不同 KPI，不混投

| 層次 | KPI | 不用看的指標 |
|---|---|---|
| 冷層 | ThruPlay、CPM、觸及人數 | 轉換率（冷受眾本來就不轉） |
| 溫層 | CTR（點擊率）、加 LINE 數、費用頁訪問 | ThruPlay（溫受眾已知道你） |
| 熱層 | 詢價轉換率、Cost per Lead、桌機/手機分開看 | 品牌認知指標 |

### ④ Google 搜尋加碼 + 競品防守 + 桌機出價加碼

- **高意圖字加碼**：`台南外燴推薦`、`台南茶會點心`、`台南企業外燴` — 這些字有意圖，CPC 貴但 CPL 值得
- **競品防守**：`玖二品生活外燴廚房` 等競品品牌詞加防守廣告（文案不攻擊，說自己場景）
- **桌機出價調節器 +20–30%**：搜尋轉換已確認偏桌機，手機出價調低，不平均分配預算

### ⑤ UTM 閉環表

所有廣告連結強制帶 UTM，格式：

```
utm_source=meta|google
utm_medium=paid_social|paid_search
utm_campaign=[audience_type]-[scenario]
utm_content=[creative_id 或 ad_name]
utm_term=[keyword]（Google 搜尋專用）
```

追蹤閉環：廣告點擊 → landing 頁 GA 事件 → LINE 加好友（UTM 帶進 LINE Tag） → 詢價（TimeTree 備注 UTM 來源）→ 成交。  
閉環完成前，廣告優化沒有根據，不要亂動預算。

### ⑥ 廣告發布閘門（缺陷棘輪）

批量廣告寫入前，閘門強制查四項（詳見 `docs/A2-ad-ops-improvement-plan.md` Phase 2）：

| 閘門項目 | 說明 |
|---|---|
| Message-match | 廣告文案場景 = landing slug 對應場景，不跨情境混搭 |
| 預算上限 | 單次批量寫入總日預算不超過 Owner 設定上限 |
| 受眾重疊 | 新受眾包與既有包重疊率 < 閾值（避免自我競標） |
| 素材合規 | `ad_ok = yes`、`needs_face_crop = no`（來自 asset_conversion_manifest） |

---

## 4. 情境對照表（每情境一漏斗）

### B 端情境

| 情境 | 冷層（Meta 受眾） | 溫層（retarget 條件 + 目標 landing） | 熱層（Google 字詞） | Landing slug | 各層 KPI | UTM campaign |
|---|---|---|---|---|---|---|
| **B1 高管/總經理接待** | Lookalike 成交客 1% + 職業：高階主管/董事 | 看過 `/corporate-catering-tainan/` ≥ 30 秒 → 推費用頁 | `台南企業外燴`、`高端外燴推薦`、`台南商務宴客外燴` | `corporate-catering-tainan` | 冷:ThruPlay<NT$0.2 溫:CTR>2% 熱:詢價率>3% | `b1-vip-reception` |
| **B2 採購/供應商活動** | Lookalike + 職業：採購/供應鏈/業務主管 | 看過 `/corporate-catering-tainan/` 或 `/tainan-corporate-catering-cost/` | `台南外燴公司`、`台南外燴推薦`、`企業外燴報價` | `tainan-corporate-catering-cost` | 溫:費用頁點擊 熱:填表/加 LINE | `b2-procurement` |
| **B3 HR/行政茶會** | Lookalike + 職業：HR/人力資源/行政/秘書 | 看過 `/hr-admin-meeting-catering-guide-tainan/` 或 `/corporate-tea-party-desserts/` | `台南茶會點心推薦`、`台南會議茶點`、`台南點心外燴` | `hr-admin-meeting-catering-guide-tainan` / `corporate-tea-party-desserts` | 冷:ThruPlay<NT$0.25 溫:LINE加好友 熱:詢價轉換 | `b3-hr-tea` |
| **B4 公關/品牌活動** | Lookalike + 職業：公關/行銷/品牌主管 | 看過品牌活動相關頁 ≥ 30 秒 | `台南品牌活動外燴`、`台南開幕茶會外燴`、`ESG 活動外燴` | `corporate-catering-tainan`（主）/ opening_tea 頁（待上線） | 同 B1 | `b4-pr-brand` |
| **B5 大型論壇/會展** | Lookalike + 興趣：研討會/商務展覽 + 地區：大台南 | 看過 `/corporate-catering-tainan/` 或論壇案例頁 | `大臺南會展中心外燴`、`台南研討會茶點`、`台南論壇外燴` | `corporate-catering-tainan` | 熱層重押（會展有明確時間點，搜尋意圖強） | `b5-forum-expo` |

### C 端情境

| 情境 | 冷層（Meta 受眾） | 溫層（retarget 條件 + 目標 landing） | 熱層（Google 字詞） | Landing slug | 各層 KPI | UTM campaign |
|---|---|---|---|---|---|---|
| **C1 慶生派對** | 現跑「周歲/家庭冷受眾」繼續跑（48K ThruPlay NT$0.12 效率佳） | 看過慶生/周歲頁 ≥ 30 秒 → 推案例照片輪播 | `台南周歲外燴`、`台南慶生外燴推薦` | 周歲/慶生 landing（確認 slug） | 冷:ThruPlay<NT$0.15 溫:CTR>1.5% | `c1-birthday` |
| **C2 入厝宴客** | 新屋主興趣 + 生命里程碑事件 | 看過入厝/開幕相關頁 | `台南入厝外燴`、`台南喬遷宴外燴` | 入厝 landing（確認 slug） | 同 C1 | `c2-housewarming` |
| **C3 壽宴** | 50+ 年齡受眾 + 家庭關係者（子女輩） | 看過壽宴/長輩宴客頁 | `台南壽宴外燴`、`台南長輩宴客外燴` | 壽宴 landing（確認 slug） | 同 C1 | `c3-birthday-feast` |

> ⚠️ C 端 C2/C3 的 landing slug 需確認是否 live；若為 planned_404 則冷/溫層廣告 CTA 先導向 LINE 詢價，不導 404 頁。
>
> **2026-07-07 補充（婚禮/性別派對/遊艇 3 個 landing 缺口，已由 Owner 07-05 定案 + SEO 三人小組 07-07 覆核確認，見 §7）**：這 3 項不在本表原始 8 情境內，是 `docs/real-cases-to-seo-matrix.md` 後續案例分類時提出的缺口，決策記錄在 `docs/ad-buildout-plan.md` P2 段：**婚禮線開**（landing 其實早已存在，見 `docs/seo-keyword-map.md` 5 個 live 婚禮 slug，2026-07-07 A2 WP REST 全站掃描亦確認多篇 live；受眾包 `cold-c-wedding`，熱層字詞「台南戶外婚禮外燴」等，landing 建議整合到單一主頁 `tainan-outdoor-wedding-catering`（已修正原誤寫的 outdoor-wedding-catering-venue，該 slug 回404），不要再零散開新 slug）；**性別派對併入 `cold-c-birthday`（C1 慶生）**，不獨立受眾包但慶生 landing 內應有一個小節/案例圖承接 message-match；**遊艇外燴不建 landing、不投廣告**，案例照改作 B4 VIP/公關的廣告輪播素材使用。

---

## 5. FDE 第一片：「會議茶點 / HR 行政」線（B3）

**為什麼從 B3 開始：**
- 現成文章上線：《行政外燴推薦 HR 活動餐點規劃》(WP 1992) — 精選圖待補，其餘閘門 9/9 PASS
- Landing 現有且 live：`corporate-tea-party-desserts`（企業茶會點心頁）
- Google 已在收割：`台南茶會點心推薦`、`台南點心外燴` 已在搜尋字詞報告中出現
- B 端詢價金額 > C 端，CPL 值更高

**試跑計畫（2026-07-07 SEO 三人小組覆核後修訂，日預算 Owner 定案 NT$100/天，非草案的 150）：**

> Codex + Antigravity 唯讀評審一致認為：NT$100/天若均分給 `cold-b-meeting-corp` + `cold-b-meeting-edu` 兩包（各 NT$50/天）太薄，訊號會被稀釋；且原案「2 週看熱層詢價率 > 3% 決定要不要複製結構」在這個預算量級下，詢價筆數基期太小、百分比容易失真。已按評審意見修訂如下（見 §7 評審紀要）。

```
Week 1-2（延長為 3-4 週試跑，非原案 2 週）：
  ├── 冷層（Meta）：NT$100/天**集中投放 `cold-b-meeting-corp`**（企業HR/行政），
  │       `cold-b-meeting-edu`（教育/研究單位）暫緩，待 corp 線先跑出訊號再考慮加開
  │       （原因：corp 轉換意圖與預算充足度都明顯高於 edu，且 edu 與 B5 會展/政府會議線受眾重疊，
  │       一開始就分兩包會讓兩邊訊號都不夠判讀）
  │       素材：maplab-corporate-forum-cathay-wealth-management-hero.webp
  │       文案：「200 人財富管理論壇的茶點，從詢價到進場 5 天」
  │       CTA：→ hr-admin-meeting-catering-guide-tainan（帶 UTM）
  │
  ├── 溫層（Meta）：**Day 1 就開始建**，不要等到原案的 Week 2 —— Pixel 已確認安裝、
  │       ThruPlay 受眾現有資料可用，溫層受眾池要及早開始累積，晚建等於白白流失早期訪客
  │
  └── 熱層（Google）：Campaign4 加關鍵字「台南茶會點心推薦」「台南會議茶點外燴」
          桌機出價 +25%，手機出價 -20%

第 3-4 週：數據評估（分階段 KPI，不再只看單一「詢價率 > 3%」門檻）
  ├── 冷層看：link CTR / CPC / landing page view（不是 ThruPlay —— ThruPlay 適合影片素材，
  │       B3 這波若以靜態圖/輪播為主，ThruPlay 不是合適的冷層 KPI）
  ├── 溫層看：link CTR > 2%、加 LINE 好友數、廣告頻率是否過高（避免騷擾）
  └── 熱層看：qualified LINE 詢價「筆數」+ CPL（不是只看百分比 —— 這個預算量級下，
        1 筆詢價就可能讓百分比失真，筆數 + CPL 一起看才有意義）
        ↓ 訊號夠清楚 → 複製結構到 B1/B2/B4/B5（含 corp/edu 拆分策略一併檢討）
        ↓ 未達標 → 調整素材或文案，不要動受眾結構
```

**UTM 示例：**
```
https://www.maplabkitchen.com/hr-admin-meeting-catering-guide-tainan/
?utm_source=meta&utm_medium=paid_social&utm_campaign=b3-hr-tea&utm_content=forum-hero-v1
```

**Landing page 規格（2026-07-07 Owner 指示）**：不限定用 Elementor 製作，只要符合 `skills/brand-voice-guide.md`（語氣）+ `skills/maplab-visual-spec.md`（7 色票，婚禮/週歲場景用裸粉`#D9C4B8`+暖米`#EDE5D8`）即可，工具不設限。

**FDE 啟動前置條件（待 A0/Owner 定案）：**
- [ ] Meta 帳號 318634712 受眾包建立權限確認
- [ ] Google Ads Campaign4 出價調整授權
- [ ] UTM 追蹤 Google Analytics 事件確認有收到（GA4 實時報告核對）
- [x] B3 冷層日預算上限 **已定案 NT$100/天**（2026-07-07 Owner；集中投放 corp 線，見上方修訂試跑計畫）
- [ ] WP 1992 精選圖補上（C-1 缺陷，Owner 瀏覽器 session 處理）

---

## 6. 整體推進順序

```
Phase 0 ✅  安索夫矩陣 + 情境對照表建立（本文件）
Phase 1     唯讀盤點 Google/Meta 帳號現況（需 API 接通）
Phase 2     FDE B3 試跑兩週（人工操作，不需 API）
Phase 3     FDE 數據回來 → 複製到其他情境 → 廣告發布閘門自動化
Phase 4     UTM 閉環 → TimeTree 成交數據接入 → 戰情中心統一視圖
```

---

## 7. SEO 三人小組評審制度（2026-07-07 建立）

Owner 指示：SEO/廣告矩陣類決策，設成三人小組審查，透過 Chrome extension prompt 召喚子 session：

| 席位 | 角色 | 權限 | 召喚方式 |
|---|---|---|---|
| **Claude（A2）** | 決策 / 整合 / 執行改動 | 讀寫（唯一能改檔案的席位） | 本體 |
| **Codex** | 唯讀評審 | 唯讀（`codex exec --ephemeral -s read-only`） | `AGENT_RECALL_PROMPTS.md` §Codex 召回 prompt 前綴 |
| **Antigravity (agy)** | 唯讀評審 | 唯讀（`agy --print`，**不給 `--add-dir`/repo 存取**，從 repo 外的中立目錄呼叫，因 agy 尚無確認過的強制唯讀 sandbox，見 `AGENT_RECALL_PROMPTS.md` §Antigravity 風險註記） | `AGENT_RECALL_PROMPTS.md` §Antigravity 召回 prompt 前綴 |

**運作方式**：
1. Claude 準備評審包（背景摘要 + 具體問題），存到 `workbook/reviews/JOB-A2-SEO-*-REVIEW-*/review_packet.md`。
2. 分別呼叫 Codex（`-s read-only`，可給 repo 唯讀存取）與 Antigravity（**不給 repo 存取**，評審包內容直接貼進 prompt，自帶所有需要的背景，不需要它探索檔案系統）。
3. Claude 彙整兩位唯讀評審的意見，結合自己的判斷做出最終決策，寫回矩陣文件。**任何檔案改動只能由 Claude 執行**，Codex/Antigravity 的輸出只是文字意見，不會也不應該自己動手改。
4. 評審紀要（兩位的原話摘要 + 分歧點 + Claude 的整合決策與理由）留存在同一個 `workbook/reviews/` 資料夾，並在對應矩陣文件的變更紀錄註明本輪評審。

**首次實跑（2026-07-07）**：`workbook/reviews/JOB-A2-SEO-TRIO-REVIEW-20260707/`，評審對象是本文件 + `docs/ansoff-mot-audience-matrix.md` + `docs/A2-ad-ops-improvement-plan.md` + `docs/real-cases-to-seo-matrix.md`；三個問題：矩陣盲點/風險、B3 試跑方案（NT$100/天）合理性、3 個 landing 缺口的專業意見。結論已整合進本文件 §5、§4 註記。

---

## 變更紀錄

| 版本 | 日期 | 變更 | 來源 |
|---|---|---|---|
| v0.1-draft | 2026-07-03 | 初版草案：現況 + 核心洞察 + 六大做法 + 8 情境表 + FDE B3 | Owner 截圖 + 對話指示，A2 整理 |
| v0.2 | 2026-07-07 | 建立 SEO 三人小組評審制度（§7）；B3 日預算定案 NT$100/天（原案150）並依評審意見修訂試跑配置（集中投corp線、溫層Day1建立、KPI分階段、試跑期延長為3-4週）；landing不限Elementor + 品牌語氣色票規格；婚禮/性別派對/遊艇 3 個 landing 缺口決策補充註記（§4） | Owner 指示三人小組 + Codex/Antigravity 唯讀評審 + Claude 整合決策 |
