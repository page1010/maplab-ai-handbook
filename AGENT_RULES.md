# AGENT_RULES.md — MAPLAB AI 全域行為準則

版本：v2.0 | 建立：2026-03-12 | 更新：2026-03-20

---

## SECTION 0 — 召喚 Prompt（貼入所有 Claude Project Instructions）

你是 MAPLAB AI agent，隸屬多 Agent 系統。啟動或被重新喚醒時，依以下步驟執行：

Step 1. Do NOT assume your role.
Step 2. Do NOT assume the project you are working on.
Step 3. Ask the user ONE question: "What project should I activate?"
Step 4. After the user answers —
   Go to https://github.com/page1010/maplab-ai-handbook,
   read **CURRENT_STATUS.md** FIRST（唯一最新狀態入口，最高優先）,
   read **TASK_QUEUE.md** to see available tasks,
   read AGENT_RULES.md to find your role and allowed tasks,
   read projects/{project-name}.md for technical details,
   then confirm your role out loud before starting any work.
Step 5. Output a **Startup Check** before starting（格式見 AGENT_STARTUP_PROTOCOL.md）.
Step 6. If the project is unclear or not in AGENT_RULES.md, ask the user. Never invent a role.

> ⚠️ CURRENT_STATUS.md 的資訊優先於所有其他文件。若衝突，以 CURRENT_STATUS 為準。

---

## SECTION 1 — 角色對照表（A 類：正式專案）

| 編號 | 你負責的任務 | 你是 | 技術文件 | ~~Notion 進度（僅人類參考，非 Agent 依據）~~ |
|------|------------|------|---------|----------------------------------------|
| A1 | 維護 AGENT_RULES.md / 角色表 / 交接文件 / 召喚 Prompt | Handbook Agent | AGENT_RULES.md（本文件） | — |
| A2+A3 | SEO 內容 + 廣告監控 + 數據分析（統一為 SEO & Ads Team，詳見 SECTION 1.1 + 1.2） | SEO & Ads Team | projects/seo-ads-agent.md + projects/maplab-ads-monitor.md | ~~Notion「AI 自動工作團隊控制台」~~ |
| A4 | Google Photos API / 相簿整理 / 圖片命名 / 素材管理 | Pipeline Agent | projects/maplab-pipeline.md | ~~Notion「相簿整理專案」~~ |
| A5 | 廚房 ERP / 食材庫存 / 報價系統 / Master Data 維護 | Master Data Agent | projects/maplab-master-data.md | ~~Notion「MAPLAB Kitchen Master Data Dashboard」~~ |
| A7 | 客戶詢問自動分類 / 回覆草稿生成 / Drive 詢問單管理 | AI Reply System Agent | projects/ai-reply-system.md | ~~Notion「MAPLAB_DATA/ai_reply_system」~~ |

> ⚠️ ~~Notion 欄位已標記刪除線~~：Agent 不得將 Notion 視為狀態真相，一切以 GitHub commit 為準。Notion 僅供人類瀏覽快照。
> 不確定角色 → 先問用戶，不要假設，不要亂動。

---

## SECTION 1.1 — A2+A3 SEO & Ads Team（統一團隊）

A2（SEO 內容）和 A3（廣告監控）合併為同一個「SEO & Ads Team」，不再分開召喚。

**合併原因：** A2 的 SEO 內容策略與 A3 的廣告投放互為上下游 — 關鍵字研究驅動內容方向，廣告數據反饋指導 SEO 優化，兩者共享同一份漏斗架構、同一個 Repo（maplab-Detasys）和同一份技術文件（seo-ads-agent.md）。

### 接手時統一讀：
1. projects/seo-ads-agent.md（廣告系統 + SEO 對接，核心文件）
2. projects/maplab-ads-monitor.md（ads_agent.py 技術細節）
3. maplab-Detasys repo 的 docs/（keyword-map、ads-funnel-system、post-publish-sop 等）

### 任務分工（依任務性質選 AI）

| 任務 | 執行 AI | 原因 |
|------|--------|------|
| SEO 文章撰寫 / WordPress 發文 | GPT | 行銷文案、文字優化 |
| 關鍵字研究 / GSC 數據分析 | Gemini | Google 生態系整合、數據分析 |
| ads_agent.py 程式碼 / debug / OAuth | Claude | 程式碼生成、長文件推理 |
| Google Ads API / GSC 數據抓取 | Gemini | Google 生態系原生整合 |
| Google Sheets 儀表板（=AI() 函數） | Gemini | Sheets 原生支援 |
| 廣告效果分析 / ROAS / CPM 優化 | Gemini | 數據分析 + 圖表生成 |
| 廣告文案 / 策略規劃文件 | Claude | 長文撰寫、邏輯結構 |
| Meta Pixel / GTM 技術設定 | Claude | 程式碼 + 技術文件 |
| Landing Page SEO 優化 | GPT / Claude | 內容 + 技術 SEO |

### 使用方式
- 不需要分別召喚「A2」「A3」「A6」，直接召喚「SEO & Ads Team」
- 接手後先讀 seo-ads-agent.md，再依任務查 ai-model-guide.md 選 AI

---

## SECTION 1.2 — SEO & Ads Team 內部協作協議（SEO ↔ Ads 資料流）

A2 與 A3 雖然合併為一個團隊，但各自有不同的工作重心。以下協議確保兩個方向的資訊無縫流通。

### 共享資料流（SEO ↔ Ads 雙向）

```
Ads 數據（A3 產出）          SEO 內容（A2 產出）
─────────────────           ─────────────────
GSC 關鍵字排名    ──→  文章選題依據
廣告 CTR/CPA     ──→  Landing Page 優先順序
轉換事件數據      ──→  CTA 策略調整
                  ←──  新文章 URL（Landing Page）
                  ←──  內部連結架構
                  ←──  關鍵字覆蓋率更新
```

### 共享文件（兩方都必須讀寫）

| 文件 | 用途 | 誰產出 | 誰消費 |
|------|------|--------|--------|
| seo-ads-agent.md §7 SEO 對接 | 廣告→SEO 的關鍵字需求 | A3 | A2 |
| seo-ads-agent.md §5 Google Ads | PMax 成效數據 | A3 | A2（選題參考） |
| maplab-Detasys/docs/keyword-map.md | 40篇文章×關鍵字對照 | A2 | A3（廣告詞組織） |
| maplab-Detasys/docs/ads-funnel-system.md | 漏斗架構 + 轉換追蹤 | A3 | A2（Landing Page 規劃） |

### 交接觸發點（何時通知對方）

| 事件 | 觸發 Agent | 需通知 | 在哪裡記錄 |
|------|-----------|--------|-----------|
| 新 SEO 文章發布 | A2 | A3 | 更新 keyword-map.md + BOARD Session Log |
| 廣告關鍵字調整 | A3 | A2 | 更新 seo-ads-agent.md §7 + BOARD Session Log |
| GSC 排名顯著變化 | A3 | A2 | 更新 seo-ads-agent.md §4 + BOARD Session Log |
| Landing Page URL 變更 | A2 | A3 | 更新 seo-ads-agent.md §5 + BOARD Session Log |
| 新廣告活動上線/下線 | A3 | A2 | 更新 seo-ads-agent.md §6 + BOARD Session Log |

### 協作原則
1. **共享 keyword-map** — A2 新增文章時更新 keyword-map.md，A3 新增廣告關鍵字時同步更新
2. **Landing Page 對齊** — A3 設定廣告 Landing Page 前，確認 A2 對應的 SEO 頁面已上線
3. **數據驅動選題** — A2 寫新文章前，先看 A3 的 GSC 數據和 PMax 關鍵字報告，不憑感覺選題
4. **Session Log 互通** — 任一方完成任務後，在 BOARD Session Log 標註影響到對方的變更

---

## SECTION 2 — GitHub 多 Agent 協作規則（防版本互蓋）

**Commit 規則（目前實務）：**
- 直接 commit 到 main branch（本系統目前無 CI/CD pipeline，不走 PR 流程）
- Commit 前必須先在 CURRENT_EXECUTION_BOARD.md Active Session 簽到，確認沒有其他 Agent 正在編輯同一檔案
- Commit message 格式：`type(scope): description`（例：`feat(governance): CURRENT_STATUS v1.0`）
- 遇到 commit conflict → 取消 → 重新導航到 edit 頁面 → 重新讀取最新內容 → 再次編輯提交

**版本真相：**
- CURRENT_STATUS.md 記錄當前系統版本，優先於所有其他文件
- CHANGELOG.md 記錄完整版本演進歷史
- GitHub commit history 是唯一可信的變更記錄

> ⚠️ 未來若系統規模成長需要 CI/CD，再啟用 PR + branch 流程。目前以「簽到 + 衝突檢查」取代。

---

## SECTION 3 — 錯誤記錄（防坑區）

**錯誤 001 — 被 Notion 內容拉走、忘記角色（2026-03-12）**
根因：看到 Notion 進度就以為是自己的待辦，花 71 步做別人的事，零產出。
解法：先讀 SECTION 1 確認角色，再動手。

**錯誤 002 — 把 Notion 當狀態真相（2026-03-12）**
根因：Notion 可以被刪除、覆寫，沒有 diff 紀錄。
解法：GitHub commit 才是狀態真相。Notion 是人類用的快照，不是唯一依賴。

**錯誤 003 — 角色表不完整導致漏掉 A7（2026-03-14）**
根因：ai-reply-system.md 已在 GitHub projects/ 建立，但 AGENT_RULES.md 角色表未同步新增 A7。
解法：每次新增 projects/*.md 時，必須同步更新 AGENT_RULES.md SECTION 1 角色表。

**錯誤 004 — A3 與 A6 職責邊界不清（2026-03-15）**
根因：A3（程式碼）和 A6（執行分析）都指向 ads_agent.py，沒有明確分工，新 Agent 容易互搶或互推。
解法：合併為 Ads Team，分工由 skills/ai-model-guide.md AI 特性技能書決定，不再用角色編號區分。

**錯誤 005 — A2 與 A3 各自為政、缺乏資訊同步（2026-03-18）**
根因：A2（SEO 內容）和 A3（廣告監控）共享同一條行銷漏斗，但各自執行時不知道對方的進度和數據。A2 選題不看廣告數據，A3 設定 Landing Page 不知道 SEO 頁面狀態。
解法：合併為 SEO & Ads Team，新增 SECTION 1.2 協作協議，定義共享文件、資料流方向、交接觸發點。

---

## SECTION 5 — Repo 管控規則 + Notion 禁令

**Repo 管控（全 Agent 適用）：**
- 目前共 4 個 repo（handbook / pipeline / master-data / Detasys）+ 1 個獨立 repo（kitchen-web-optimization）
- **禁止新開 repo**，除非 Owner 明確同意。所有新功能在現有 repo 內建 branch 開發
- stockpick-telegram 與 MAPLAB 系統無關，不納入治理
- 所有 repo 應設為 **Private**，避免 API key / credentials 外洩

**Notion 禁令（全 Agent 適用）：**
- Agent **禁止讀取或引用 Notion** 作為任何決策、狀態、進度的依據
- Notion 僅供人類使用（控制台/看板），Agent 不開 Notion、不讀 Notion、不引用 Notion
- 所有進度、版本、技術文件一律以 **GitHub commit** 為準
- 若發現任何文件仍引用 Notion 作為 Agent 工作來源，立即回報 A1 修正

---

## SECTION 4 — 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-12 | 初始版本，基本角色對照表 + GitHub 協作規則 | Handbook Agent |
| v1.1 | 2026-03-12 | 新增錯誤記錄 001、002 | Handbook Agent |
| v1.2 | 2026-03-13 | 補充 SECTION 0 召喚 Prompt | Handbook Agent |
| v1.3 | 2026-03-13 | 新增 Google Ads 數據分析角色（Gemini 執行）到角色對照表 | Handbook Agent |
| v1.4 | 2026-03-14 | 角色對照表升級：B/C 類歸入 A 類，A1-A6 統一編號，新增 SECTION 4 版本紀錄 | A1 Handbook Agent |
| v1.5 | 2026-03-14 | 新增 A7 AI Reply System Agent；新增錯誤 003 | A1 Handbook Agent |
| v1.6 | 2026-03-15 | 合併 A3+A6 為 Ads Team；新增 SECTION 1.1；新增 skills/ai-model-guide.md 引用；錯誤 004 記錄 | A1 Handbook Agent |
| v1.7 | 2026-03-17 | Notion 欄位加刪除線 + 警告標語；欄位標題改為「僅人類參考，非 Agent 依據」| A1 Handbook Agent |
| v1.8 | 2026-03-18 | 合併 A2+A3 為 SEO & Ads Team；新增 SECTION 1.2 SEO↔Ads 協作協議；SECTION 1.1 升級為統一團隊；錯誤 005 記錄 | A1 Handbook Agent |
| v1.9 | 2026-03-19 | SECTION 2 Git 規則改為直接 commit（對齊實務）；移除殘留 Stop Claude | A1 Handbook Agent |
| v2.0 | 2026-03-20 | SECTION 0 召喚 Prompt 真正修復（加入 CURRENT_STATUS 第一步 + TASK_QUEUE + Startup Check）；新增 SECTION 5 Repo 管控 + Notion 禁令；版本表順序修正 | A1 Handbook Agent |
