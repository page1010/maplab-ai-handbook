# MAPLAB Playbook — 從 0 到上線完整路徑

> **用途**：記錄 MAPLAB Kitchen 第一個網站從無到有的完整路徑。  
> 第二個網站照這份走，不用重新摸索。  
> 每個階段記錄：做了什麼 → 用了什麼工具 → 最終選擇 → 踩過的坑。

版本：v1.0 | 建立：2026-03-23 | 維護者：A1 Handbook Agent  
資料來源：GitHub commit history（2026-03-12 ~ 2026-03-23）+ CHANGELOG v2.2~v3.9 + 7 個 projects/ 文件 + lessons-learned + 實戰紀錄

---

## 目錄

- SECTION 0 — 全局地圖：一條龍總覽
- SECTION 1 — 系統治理建立（A1）
- SECTION 2 — 資料層建立（A5）
- SECTION 3 — 照片 Pipeline（A4）
- SECTION 4 — 廣告系統（A3）
- SECTION 5 — SEO + 內容（A2/A3）
- SECTION 6 — GTM 追蹤（A3）
- SECTION 7 — 客戶回覆系統（A7）
- SECTION 8 — 失敗經驗總整理
- SECTION 9 — 第二個網站複製清單

---

## SECTION 0 — 全局地圖

### 一條龍流程

```
Day 1-3     治理架構（A1）→ 規則 + 協議 + 技能書
Day 2-5     資料層（A5）  → ERP schema + 品項清洗 + 報價 MVP
Day 3-7     照片 Pipeline（A4）→ Takeout 解壓 → AI 分類 → SEO 命名
Day 3-5     廣告帳號設定（A3）→ Meta + Google Ads + Pixel
Day 5-7     GTM 轉換追蹤（A3）→ LINE/表單/電話事件
Day 5-8     SEO 內容（A2/A3）→ 關鍵字頁面 + Landing Page
Day 7+      素材上線（A3）→ Meta 廣告素材 + 受眾設定
Day 10+     回覆系統（A7）→ LINE OA 自動回覆
```

### 依賴關係

```
A1 治理 ──→ 所有 Agent 都能開工
A5 資料 ──→ A4 照片（品項 ID 比對）、A3 廣告（報價單）、A7 回覆（價格查詢）
A4 照片 ──→ A2/A3 SEO+廣告（素材圖片）
A3 GTM  ──→ A3 廣告（轉換追蹤優化）
```

### 工具棧（最終選擇）

| 層面 | 工具 | 為什麼選它 |
|------|------|-----------|
| 治理 | GitHub（maplab-ai-handbook） | 唯一真相源，Agent 不用 Notion |
| 資料庫 | Google Sheets（模擬 RDB） | 外燴業務 <10,000 筆，Sheets 夠用 |
| 照片處理 | Google Colab + Gemini REST API | 雲端執行，不吃本機資源 |
| AI 模型 | gemini-2.5-flash（REST API） | 比 google.generativeai library 穩定、快 2x |
| 廣告 | Meta Ads + Google PMax | 品牌認知（Meta）+ 收割轉換（Google） |
| 追蹤 | GTM + Meta Pixel + GA4 | 統一管理所有追蹤碼 |
| SEO | WordPress（maplabkitchen.com） | 已有網站 |
| 版本管理 | GitHub commit（直接 main） | 小團隊不需要 PR review |
| 行事曆 | TimeTree（飛寶一家） | 客戶外燴日期的唯一來源 |

---

## SECTION 1 — 系統治理建立（A1 Handbook Agent）

### 時間線

| 日期 | 做了什麼 | 產出 |
|------|---------|------|
| 3/12 | 建立 repo + 初始框架 | maplab-ai-handbook 建立 |
| 3/13 | 定義 Agent 角色 + 規則 | AGENT_RULES v1.0 + 7 個 projects/ 文件 |
| 3/14 | CHANGELOG 建立 | CHANGELOG v2.2 |
| 3/15 | 合併 A3+A6、AI 特性技能書 | AGENT_RULES v1.6 + ai-model-guide v1.0 |
| 3/17 | 技能書 x8 + troubleshooting hub | 11→14 本技能書 |
| 3/17 | Notion vs GitHub 對齊 | PROJECT_CONTEXT 刪除，GitHub 唯一 |
| 3/18 | Phase 3：簽到/簽退 + 衝突檢查 | BOARD v2.0 + WORKFLOW v2.1 |
| 3/18 | Phase 4：治理重構（單一入口） | CURRENT_STATUS v1.0 + TASK_QUEUE v1.0 + Task Card |
| 3/19 | Phase 4.2：全系統文件對齊 | README v2.4 + SYSTEM_MAP v2.1 + 4 文件更新 |
| 3/19 | 系統巡查：關鍵 20% 修復 | AGENT_RULES v1.9 + REPO_SYNC v1.0 |
| 3/20 | T-A1-002 結案（7 子任務） | PROTOCOL v1.3 + AGENT_RULES v2.0 + web-opt v1.0 |
| 3/23 | 系統行為強化 | PROTOCOL v1.5 + AGENT_RULES v2.2 + task-progress-guide |
| 3/23 | 跨部門溝通 | TimeTree v2.0（746 events） + handoff-to-A5 |

### 最短路徑（給第二個網站）

1. 複製 maplab-ai-handbook repo 結構（AGENT_RULES / PROTOCOL / CURRENT_STATUS / TASK_QUEUE）
2. 改 AGENT_RULES 的角色定義和專案名稱
3. 建 skills/ 資料夾，至少放：task-progress-guide（必拿）+ superpowers-guide（路由表）
4. 建 CURRENT_STATUS + TASK_QUEUE 作為任務管理入口
5. 第一天就定：GitHub 唯一、不用 Notion、直接 commit main

### 關鍵決策

- **GitHub 唯一真相**：最初 Notion + GitHub 並存 → Agent 混亂 → 3/17 決定 GitHub only
- **直接 commit vs PR**：初期要求 PR + branch → 實際太慢 → 改為直接 commit main
- **CURRENT_STATUS 單一入口**：初期 Agent 不知道先讀什麼 → 3/18 建立 CURRENT_STATUS 作為唯一起點
- **必拿技能**：初期 Agent 不拿技能書 → 3/23 建立 task-progress-guide 作為必拿技能 + SECTION 0 阻擋規則

### 踩過的坑

- CHANGELOG 宣稱修了但實際沒改（v3.6 → v3.7 修正）
- Agent 不問問題就開始做 → 加 Startup Check 強制欄位
- Agent 每次都選方案 A → 改為盲點分析格式
- ⚠️ icon 用在「無問題」場景 → 矛盾，icon 必須語意一致

---

## SECTION 2 — 資料層建立（A5 Master Data Agent）

### 時間線

| 日期 | 做了什麼 | 產出 |
|------|---------|------|
| 3/13 | Schema v0.1 設計（Gemini 對話） | 6 張核心表定義 + item_id 命名規則 |
| 3/13 | 報價系統分析 | SECTION 8 完整缺口報告 |
| 3/13 | QUOTE_DRAFT v0.3 建立 | 雙模式報價（正向/逆向） |
| 3/14 | Dashboard 修復 + 品項分類中文化 | #REF! 修復 + QUOTE_DRAFT 優化 |
| 3/17 | TimeTree 密集日掃描 | 2025 全年外燴密集日清單 |
| 3/18 | Items 品項清洗 | 300 → 139 筆（BEV 容量分離 + 去重 + 後綴清除） |
| 3/18 | QUOTE_DRAFT MVP | 下拉選品項 → VLOOKUP 帶出成本 |
| 3/20 | Schema 文件化 | schema-v0.1.md + table-relationship-map.md + field-naming-rules.md |
| 3/23 | TimeTree 事件增強 | 746 筆外燴事件含客戶名（A1 提取，供 A5 比對） |

### 最短路徑（給第二個網站）

1. 先用 Google Sheets 模擬 RDB（短期 1-3 年夠用，不需要 MySQL）
2. 定義 item_id 命名規則：`{TYPE}-{SUBTYPE}-{SEQ3}`（如 DES-MAC-001）
3. 建 ITEM_MASTER 為主表，所有其他表用 item_id FK 關聯
4. 先清洗品項（去重 + 標準化命名）再建報價單
5. QUOTE_DRAFT MVP：下拉選品項 → VLOOKUP → 總價，不需要一開始就做逆向報價

### 關鍵決策

- **Sheets vs MySQL**：外燴 <10,000 筆 → Sheets 夠用，Gemini 輔助格式驗證
- **item_id 命名**：不用名稱做 Key（AI 辨識錯誤率高），用 `{TYPE}-{SUBTYPE}-{SEQ3}`
- **清洗優先**：先把 300 筆砍到 139 筆（去重/合併），再建結構
- **品項 Header 鎖定**：第一行定了就不改位置，Python 腳本依賴欄位順序

### 踩過的坑

- Items 與 ITEM_MASTER 命名不一致（v0.2 用 DST001，MasterData 用 DES-MAC-001）
- Dashboard #REF! 錯誤（QUERY LIMIT 公式斷連）
- 甜點去重需人工（AI 無法判斷「玫瑰馬卡龍」和「覆盆子馬卡龍」是否同品項）

---

## SECTION 3 — 照片 Pipeline（A4 Pipeline Agent）

### 時間線

| 日期 | 做了什麼 | 產出 |
|------|---------|------|
| 3/12 | 環境設定（Phase 0）：GCP + OAuth | Colab 環境就緒 |
| 3/14 | collector_picker.py + collector_local.py | PR #3 #4（Phase 1） |
| 3/15 | 兩帳號 Takeout 確認在 Drive | Phase 1.5 完成 |
| 3/17 | mina Takeout 解壓 122,200 files | Phase 2（Colab 執行） |
| 3/17 | collector_drive.py | PR #5（Phase 3） |
| 3/19 | Drive API Overlap Check | OLD Google Photos 全空，Takeout 唯一 |
| 3/19 | Photo scan 完成 | 60,584 files（C=4,593 T=254 D=55,737） |
| 3/20 | Gemini API Key 驗證 | google.genai + gemini-2.5-flash OK |
| 3/20 | TimeTree lookup + enriched dates | 361 dates enriched（C=322 T=39） |
| 3/23 | Phase 4 v4.0：S1-S4 完成 | 資料夾結構建立 + 先鋒 10 張 + prompt 定版 |
| 3/23 | S5 進行中 | 2022 全年 batch ~310/h via REST API |

### 最短路徑（給第二個網站）

1. **Takeout 下載**：Google Photos → Takeout（全選）→ 存到 Drive
2. **Colab 解壓**：用 Drive API v3（不用 drive.mount，會失敗）
3. **Photo scan**：掃描所有檔案建立清單（年份/數量）
4. **TimeTree 交叉比對**：用行事曆事件標記外燴/旅遊日期
5. **Gemini REST API 分類**：用 `gemini-2.5-flash` REST API，不用 python library
6. **GPS 細分**：日常照用 GPS 座標分 home/shop（Gemini 看不出地點）
7. **SEO 命名**：`{category}-{description}-{detail}.webp`
8. **WebP 轉檔**：比 JPG 小 25-35%

### 關鍵工具選擇

| 需求 | 試過什麼 | 最終選擇 | 為什麼 |
|------|---------|---------|--------|
| Gemini API | Vertex AI SDK → 404 | google.genai + API key | Vertex AI 模型名稱格式不同 |
| Gemini 呼叫方式 | google.generativeai library → 400 + proxy 斷線 | REST API（requests.post） | 更快（310/h vs 160/h）、更穩、不依賴 proxy |
| Gemini Model | gemini-2.0-flash（retired）→ 1.5-flash（同 404） | gemini-2.5-flash | 2.0 已下架 |
| Drive 存取 | drive.mount → ValueError | google.colab.auth + Drive API v3 | mount 在 Colab 不穩定 |
| 日常照分類 | Gemini Vision（無法判斷地點） | GPS 座標距離計算 | 零 API 成本、更準確 |

### Colab 防斷線設定

- BATCH_SIZE = 50（每 50 張寫入 Sheet）
- CHECKPOINT_EVERY = 200（每 200 張存 Drive checkpoint）
- 重連 SOP：Auth cell → S5-RESUME cell（自動跳過已完成）
- REST API timeout = 120s + MAX_RETRIES = 3

### 踩過的坑

| INCIDENT | 問題 | 根因 | 教訓 |
|----------|------|------|------|
| 001 | Takeout ZIP 被刪，EXIF metadata 永久遺失 | 建議清垃圾桶前沒確認依賴 | 不可逆操作前列出所有未提取資料 |
| 002 | Vertex AI 404 | 模型名稱格式與 Generative AI API 不同 | 先用最簡單 API 驗證 |
| 003 | GitHub raw 快取導致下載舊版 | CDN 快取 | curl 加 ?t={timestamp} |
| 004 | PHOTO_ROOT 路徑錯 | 假設資料夾結構 | 先 os.listdir 逐層驗證 |
| 005 | google.generativeai PIL Image 400 | 套件已棄用 | 注意 FutureWarning |

### 資料規模參考

- mina 帳號：122,200 files → scan 後 60,584 有效
- 分類比例：外燴 C=4,593（8%）、旅遊 T=254（0.4%）、日常 D=55,737（92%）
- 2022 batch 8,559 張：REST API ~310/h ≈ 28 小時
- pagewu1010 帳號：~187 GB，待 mina 跑通後處理

---

## SECTION 4 — 廣告系統（A3 SEO & Ads Team）

### 時間線

| 日期 | 做了什麼 | 產出 |
|------|---------|------|
| 3/11 | 廣告系統初始文件（從 Notion 遷移） | seo-ads-agent.md v1.0 |
| 3/13 | 策略一廣告組合審查 + Pixel 確認 | v1.1 |
| 3/16 | 策略一受眾描述填寫 + Canva C款 WIP | v1.3~v1.5（受眾/TA/廣告布局快照） |
| 3/17 | 完整重寫：13 章節廣告技術文件 | seo-ads-agent.md v2.0 |
| 3/17 | PMax 問句型標題 + GTM SOP | v2.1 + gtm-conversion-setup.md v1.0 |
| 3/23 | 慶生周歲派對 Meta 廣告上線 | 使用現有貼文上線，受眾記錄完成 |

### 最短路徑（給第二個網站）

1. **帳號建立**：Meta 企業管理平台 + Google Ads + GTM 容器 + Meta Pixel
2. **漏斗設計**：Top（品牌認知/冷受眾）→ Mid（互動）→ Bottom（轉換/Google PMax）
3. **先跑 Google PMax**：設定預算 NT$300/天 + 最高成效廣告 + 至少 19 張圖 + 5 部影片
4. **再跑 Meta 互動**：B 組互動廣告（公關窗口 + 企業窗口）各一則
5. **最後上品牌認知**：冷受眾素材完成後才上線
6. **受眾設定**記錄在 Task Card（handoff/tasks/T-A3-002.md）

### 關鍵決策

- **Google 收割 + Meta 建品牌**：Google PMax 抓搜尋意圖（已想找外燴的人），Meta 做曝光（還不知道你的人）
- **不在 Meta 推銷/講價格**：冷受眾只講畫面感，不放方案/金額
- **PMax 單一活動先跑**：不急著拆 Campaign 1/2，先驗證轉換
- **素材用現有貼文先上**：不等 Canva C款完成，先用現有貼文測試受眾

### 廣告成本參考（MAPLAB 第一個月）

| 平台 | 每日預算 | 30 天花費 | 轉換 | CPA |
|------|---------|----------|------|-----|
| Google PMax | NT$300 | NT$2,257（使用率 25%） | 7 次 | NT$322 |
| Meta B組 公關窗口 | — | — | — | NT$5/互動 |
| Meta B組 企業窗口 | — | — | — | NT$13/互動 |

### 踩過的坑

- Meta Pixel 重複觸發（GTM 有兩個 FB 標籤）→ 刪除重複 Pixel
- PMax 預算使用率僅 25%（受眾量或關鍵字覆蓋不足）
- 「開發潛在客戶2026」空殼行銷活動每天白燒 NT$100 → 需暫停
- 品牌知名度 A組 有「未發佈的編輯內容」→ 需確認發佈或還原
- seo-ads-agent.md v1.x 格式亂碼（> > - [ ] 格式）→ v2.0 完整重寫解決

### 受眾設定紀錄

地區：台南、高雄  
對象：25-45 歲媽媽（週歲/家庭冷受眾）  
興趣條件：奢侈品、國際旅行、日本料理、中式料理、新光三越台南西門店、甜點、巧克力、無印良品、肖像攝影、Photo shoot、Smart Parents 親子王、生日蛋糕、女性雜誌、攝影網站等  
完整清單見：handoff/tasks/T-A3-002.md

---

## SECTION 5 — SEO + 內容（A2/A3 SEO & Ads Team）

### 時間線

| 日期 | 做了什麼 | 產出 |
|------|---------|------|
| 3/12 | 官網 SEO 初始盤點 | web-optimization repo 建立 |
| 3/16 | PR #1：策略一廣告素材 + 受眾 | work/seo-ads/claude/strategy1-ad-creative |
| 3/16 | PR #2：TA 建議 + 困難回報 | work/seo-ads/claude/strategy1-ta-docs-v1.4 |
| 3/16 | PR #3：CHANGELOG v2.5 | work/seo-ads/claude/changelog-v2.5-board-v1.3 |
| 3/20 | 官網 SEO 優化紀錄彙整 | maplab-kitchen-web-optimization.md v1.0（23 項優化） |

### 最短路徑（給第二個網站）

1. **關鍵字策略**：先定 5 個核心頁面（總頁/週歲/婚禮/企業/價格FAQ）
2. **Landing Page 必備**：LINE 連結 + 詢問表單（GTM 才能追蹤轉換）
3. **內容方向**：對應 PMax 關鍵字群（台南外燴、週歲派對外燴、台南外燴推薦）
4. **SEO 與廣告聯動**：SEO 頁面 = Google PMax 的 Landing Page
5. **WordPress 基礎優化**：RWD + PageSpeed + meta 標題 + 結構化資料

### 關鍵決策

- **A2 + A3 合併**：SEO 和 Ads 共享行銷漏斗，分開執行會資訊斷層（v3.2 決定）
- **5 個交接觸發點**：SEO 和 Ads 任何變更都即時通知對方
- **PR 流程後來取消**：初期 A3 用 branch + PR，後來改為直接 commit（更快）

### 待建 SEO 頁面（優先順序）

1. 台南外燴總頁
2. 週歲/家庭派對頁
3. 婚禮外燴頁
4. 企業外燴頁
5. 價格/FAQ 頁

---

## SECTION 6 — GTM 追蹤（A3）

### 時間線

| 日期 | 做了什麼 | 產出 |
|------|---------|------|
| 3/17 | GTM 轉換事件 SOP 建立 | gtm-conversion-setup.md v1.0 |
| 3/17 | GTM v15 發布：LINE Click + Phone Click | Meta Pixel 事件上線 |
| 3/17 | LINE Click 未觸發 — 根因診斷 | v1.2 問題紀錄 |
| 3/23 | 方案 B 確認可執行 | 等待 A3 測試 |

### 最短路徑（給第二個網站）

1. **GTM 容器建立** → 網站安裝 GTM 代碼
2. **Meta Pixel 標籤**（自訂 HTML）→ All Pages 觸發
3. **三個轉換事件**依序設定：
   - LINE 點擊：Click URL 匹配 `(lihi2\.com|lin\.ee|line\.me)`
   - 表單送出：Form Submit + 勾選「等待標籤」
   - 電話點擊：Click URL 包含 `tel:`
4. 每個事件設定 Meta Pixel 標籤（fbq track）+ Google Ads 轉換標籤
5. **驗證**：Meta Pixel Helper + GTM 預覽模式

### 關鍵教訓

- **LINE 按鈕 URL 不統一**：首頁用 lin.ee、SEO 文章用 lihi2.com → 觸發條件必須用正則 `(lihi2\.com|lin\.ee|line\.me)`
- **重複 Pixel 問題**：GTM 裡可能有多個 FB 標籤，只保留一個
- **先設轉換再優化廣告**：沒有正確的轉換事件 = PMax 對錯誤目標優化

---

## SECTION 7 — 客戶回覆系統（A7 AI Reply System Agent）

### 時間線

| 日期 | 做了什麼 | 產出 |
|------|---------|------|
| 3/13 | 系統框架建立（Gemini 對話） | ai-reply-system.md v1.0 |

### 最短路徑（給第二個網站）

1. 定義詢問分類規則（外燴詢問/報價請求/一般諮詢/未成交跟進）
2. 定義必填欄位（活動類型/日期/人數/場地/預算/聯絡方式）
3. 建立品牌語氣規範（專業溫暖、不空泛承諾、具體說明服務範圍）
4. Drive 資料夾工作流程：ai_reply_system → Active Orders → Lost Quotes → Completed
5. 串接 ITEM_MASTER（品項是否提供、價格區間、過敏原）
6. 中期目標：LINE Messaging API 自動回覆

### 核心設計原則

- **80/20 輸入過濾**：先抓 20% 關鍵變量（日期/人數/預算），不急著報價
- **框架提升**：先確認客戶真實需求（背後的「為什麼」），再給建議
- **情緒平衡**：不過度承諾，維持客戶在理性決策區

### 目前狀態

- 框架已建立，分類規則已定義
- 尚未串接 ITEM_MASTER（等品項填入完成）
- LINE 自動回覆尚未開始

---

## SECTION 8 — 失敗經驗總整理

### 致命級（資料遺失/不可逆）

| # | 事件 | 根因 | 防範 |
|---|------|------|------|
| 001 | Takeout ZIP 被刪，122K 張照片 EXIF metadata 永久遺失 | 建議清垃圾桶前沒確認依賴 | 不可逆操作前，列出所有未提取資料並確認 |

### 技術選擇錯誤（浪費時間）

| # | 事件 | 試了什麼 | 正確做法 |
|---|------|---------|---------|
| 002 | Vertex AI 404 | Vertex AI SDK + gemini-2.0-flash/1.5-flash | 用 google.genai + API key（模型名稱格式不同） |
| 005 | google.generativeai PIL 400 | google.generativeai + PIL Image | 用 REST API requests.post（library 已棄用） |
| — | drive.mount ValueError | drive.mount('/content/drive') | 用 google.colab.auth + Drive API v3 |
| — | Gemini 判斷日常照地點 | Gemini Vision（無法判斷） | GPS 座標距離計算（零成本、更準） |

### 流程/治理錯誤（影響所有 Agent）

| # | 事件 | 根因 | 修正 |
|---|------|------|------|
| — | Agent 不問問題就開始做 | 沒有強制 Startup Check | PROTOCOL v1.4 加必填欄位 |
| — | Agent 不拿技能書 | 技能書是「可選」 | superpowers-guide 路由表 + task-progress-guide 必拿 |
| — | Agent 每次都選方案 A | 沒有盲點分析 | PROTOCOL Step 7 改為盲點分析格式 |
| — | CHANGELOG 說改了但沒改 | 沒有驗證 | 先確認實際文件再寫 CHANGELOG |
| — | Notion + GitHub 並存 | Agent 不知道讀哪個 | GitHub only（v3.0 決定） |
| — | 直接 commit vs PR 矛盾 | 規則寫要 PR 但實際不用 | AGENT_RULES 改為直接 commit（v3.6 修正） |
| — | ⚠️ icon 用在「無問題」場景 | 語意不一致 | icon 必須匹配實際狀態 |

### 環境/快取問題

| # | 事件 | 根因 | 修正 |
|---|------|------|------|
| 003 | GitHub raw 快取拿到舊版 | CDN 快取 | curl 加 ?t={timestamp} |
| 004 | PHOTO_ROOT 路徑錯 | 假設資料夾結構 | 先 os.listdir 逐層驗證 |

---

## SECTION 9 — 第二個網站複製清單

### Phase 1：治理（Day 1）

- [ ] Fork/複製 maplab-ai-handbook repo 結構
- [ ] 改 AGENT_RULES（角色/專案名稱）
- [ ] 改 CURRENT_STATUS + TASK_QUEUE（清空任務）
- [ ] 確認規則：GitHub 唯一、直接 commit main、不用 Notion

### Phase 2：資料（Day 1-3）

- [ ] 建 Google Sheets（ITEM_MASTER + PRICE_MASTER + ASSET_MASTER）
- [ ] 定義 item_id 命名規則
- [ ] 品項清洗（去重 + 標準化）
- [ ] QUOTE_DRAFT MVP（下拉選品項 → VLOOKUP）

### Phase 3：照片（Day 2-5）

- [ ] Google Photos Takeout → Drive
- [ ] Colab 解壓（Drive API v3，不用 drive.mount）
- [ ] Photo scan 建立清單
- [ ] Gemini REST API 分類（gemini-2.5-flash，不用 python library）
- [ ] GPS 細分（home/shop）
- [ ] SEO 命名 + WebP 轉檔

### Phase 4：廣告（Day 3-5）

- [ ] Meta 企業管理平台 + Pixel 設定
- [ ] Google Ads 帳號 + PMax 廣告
- [ ] GTM 容器 + 三個轉換事件（LINE/表單/電話）
- [ ] 受眾設定 + 記錄到 Task Card

### Phase 5：SEO（Day 5-8）

- [ ] 5 個核心 Landing Page
- [ ] 每頁必備：LINE 連結 + 詢問表單
- [ ] 對應 PMax 關鍵字群
- [ ] WordPress 基礎優化

### Phase 6：上線（Day 7+）

- [ ] Meta 廣告素材上線（可先用現有貼文）
- [ ] PMax 開始跑
- [ ] 驗證轉換事件觸發
- [ ] 監控 CPM / CTR / CPA

### Phase 7：回覆系統（Day 10+）

- [ ] 詢問分類規則
- [ ] 品牌語氣規範
- [ ] 串接品項資料
- [ ] LINE OA 自動回覆（中期）

### 預計時間

| 階段 | 天數 | 說明 |
|------|------|------|
| 治理 | 1 天 | 複製 + 改名 |
| 資料 | 2-3 天 | 品項少的話更快 |
| 照片 | 3-5 天 | 取決於照片量 |
| 廣告 | 2-3 天 | 帳號設定 + GTM |
| SEO | 3-5 天 | 5 頁內容 |
| 上線 | 1 天 | 素材 + 發布 |
| 回覆 | 持續 | 可後期再做 |
| **總計** | **~2 週** | 第一個網站花了 12 天（3/12~3/23），第二個應更快 |

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-23 | 完整 9 個 SECTION，從 GitHub 紀錄重建 | A1 Handbook Agent |

*(SECTION 7-9 下一批 commit)*
