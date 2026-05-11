# CHANGELOG.md — MAPLAB AI System 版本演進紀錄

本文件記錄 maplab-ai-handbook 的所有重大版本變更。
格式：版本號 | 日期 | 變更摘要 | 執行 Agent

## v6.5（A2 Google Discovery / Rank Math Indexing Evidence）— 2026-05-11

**A1/A2 live 提交證據：把 8 個修復 URL 送進可發現/可重爬流程**

執行 Agent：A1（Codex acting as A2）

1. 新增 `tools/google_reindex_submit.py`：檢查 sitemap membership、live URL indexability、Rank Math `submitUrls`、GSC token scope。
2. 新增 review bundle：`workbook/reviews/JOB-A2-GOOGLE-RECRAWL-20260511/`。
3. 8 個 Rank Math keyword recovery URL 全部確認在 sitemap 中。
4. 8 個 URL 全部 HTTP 200、非 noindex、有 meta description、前台有 Rank Math marker。
5. Rank Math Instant Indexing endpoint accepted：`Successfully submitted 8 URLs.`
6. GSC API / URL Inspection 目前 blocked：本機 token 只有 Drive/Sheets scopes，GSC MCP 需要 service account credentials。
7. 更新 `docs/a2a3/rankmath-keyword-recovery-2026-05-11.md` 與 `pitfalls.md`，記錄 Google discovery 邊界、GSC 憑證落差、Google ping deprecated。

## v6.4（A2 Rank Math Keyword Recovery）— 2026-05-11

**A1/A2 live 修復：用 Rank Math REST + WP REST 搶回下滑關鍵字權重路徑**

執行 Agent：A1（Codex acting as A2）

1. 新增 `tools/wp_rankmath_recovery.py`：以環境變數讀 WP 認證，執行 Rank Math meta、title、內連、支援段落修復。
2. 透過 Rank Math REST `/wp-json/rankmath/v1/updateMeta` 更新 8 個 live owner 的 focus keyword / SEO title / meta description。
3. 修正 live owner keyword ownership：
   - `/` → 台南外燴推薦 / 台南到府外燴 / 台南派對外燴
   - `/tainan-catering-guide/` → 台南到府外燴 / 台南派對外燴
   - `/corporate-catering-tainan/` → 台南企業外燴
   - `/tainan-corporate-opening-tea-catering/` → 台南開幕茶會 / 開幕茶會流程
   - `/corporate-tea-party-desserts/` → 台南會議茶點
   - `/brand-esg-catering-service/` → 台南品牌活動外燴
   - `/catering-one-year-old-party-tainan/` → 台南週歲派對外燴
   - `/gender-reveal-party-tips/` → 性別揭曉派對 / Gender Reveal Party
4. 修復多個 stale internal links，避免權重導向 draft / 404 slug。
5. 新增 review bundle：`workbook/reviews/JOB-A2-RANKMATH-LIVE3-20260511/`。
6. 新增 `docs/a2a3/rankmath-keyword-recovery-2026-05-11.md`，記錄 live targets、修復內容、驗證與 Elementor 限制。
7. `pitfalls.md` 新增 Elementor 頁面 raw content 不等於前台 rendering 的踩坑規則。

## v6.3（A2/A3 Live Fact Check Correction）— 2026-05-11

**A1 修正：WordPress / Rank Math 以 live interface 為準，不以 repo 紀錄代替現況**

執行 Agent：A1（Codex）

1. 新增 `docs/a2a3/live-wp-rankmath-fact-check-2026-05-11.md`，以 live WordPress REST、Rank Math route discovery、前台 HTML head 為事實來源。
2. 確認 live WordPress public REST 目前是 6 published pages / 57 published posts，homepage `page_on_front` 是 1250。
3. 確認 A2/A3 workbench planned slugs（如 `catering-corporate-tainan`、`opening-event-catering-tainan`、`meeting-refreshment-catering-tainan`、`brand-event-catering`、`school-event-catering-tainan`）不是 live WP objects，前台回 404。
4. 確認 Rank Math PRO 前台輸出存在；Rank Math analytics / score / link endpoints 在未登入狀態回 401。
5. 新增 `pitfalls.md` 條目：WordPress / SEO / Rank Math 任務必須先查 live interface，再讀 repo 紀錄；repo 紀錄只用來減少斷點。
6. Owner 判定今日生成圖片不可用後，已清除桌面 A2/A3 工作台 scoped folders 內的圖片衍生物。

## v6.2（AI Workbook Core + A4 Photo Restart）— 2026-05-05

**A1 治理落地：建立任務閉環核心（model-agnostic）+ 啟動相片分類重啟流程**

執行 Agent：A1（Codex）

### AI Workbook Core（MVP v0.1）
1. 新增 `tools/ai_workbook/` 核心模組：
   - `ingest.py`（讀取 GitHub 真相源索引）
   - `parse_task_cards.py`（任務卡欄位抽取）
   - `build_context_pack.py`（最小上下文包）
   - `create_microtask.py`（短任務閉環模板）
   - `relation_graph.py`（task 關聯圖輸出）
   - `infer_need.py`（真實需求推斷 + 第二意見接口）
   - `runtime_adapter.py`（runtime 路由規則）
   - `adapters/ollama_adapter.py`、`adapters/gemini_adapter.py`
   - `photo_pipeline.py`（相片分類計畫生成，僅提案不搬檔）
   - `cli.py`（`index/context/microtask/graph/infer/photo-plan`）
2. 新增 `tools/ai_workbook/README.md`（命令、邊界、路由規則）
3. 新增 `workbook/` 輸出目錄（只回寫 workbook，不自動改 CURRENT_STATUS）

### Runtime 路由策略（先行版）
4. 預設 `ollama`
5. `confidence < 0.78` 或 `cross-file reasoning` 升級 `gemini-2.5-flash-lite`
6. 若雲端金鑰缺失或輸出不穩，保留 A1 人工審核節點

### A4 相片分類重啟（先提案）
7. 建立 `workbook/outputs/2026-05-05/T-A4-photo-classification-restart/classification_plan.json`
8. 掃描來源先鎖定 `data/telegram-photos/`，輸出分類建議（proposed_only）
9. 明確採用「先計畫、人工核准、再搬檔」防呆流程
10. 修正 A4 真實入口：`MAPLAB_ASSET_LOG` Sheet（ID: `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`，tab: `工作表1`）才是主產出，`telegram-photos` 僅為本機暫存照片。
11. 新增 `asset-snapshot` 與 `dashboard` CLI，產出 `workbook/dashboard.html` 作為可點擊工作台入口。
12. 修正 `scripts/organize_photos_by_category.py`：分頁名改為 `工作表1`、Drive 根目錄改用既有 `MAPLAB_ASSETS` folder ID、預設 `DRY_RUN=True`。

## v6.1（SEO Factory）— 2026-05-04

**A1 治理同步 + A2 地端 SEO 內容工廠（Pillar First）**

執行 Agent：A1（治理同步）+ A2（SEO 實作）

### 新增模組
1. `automation/seo_factory/` 地端內容工廠骨架（local-first）
2. 七階段流程實作：`Planner -> Writer -> Linker -> Schema Builder -> Verifier -> WP Draft Publisher -> Auditor`
3. 三大 Pillar 設定：企業 / 週歲 / 婚禮（config）
4. 介面 schema：`ContentBrief` / `DraftArtifact` / `PublishPayload`
5. 週批次入口：`run_weekly_batch.py`
6. 第二波候選報告：`cannibalization-candidates.json`（由 post signals 產生）

### 配置與驗證
7. Ollama 預設模型切換為 `llama3.1:latest`（對齊本機已安裝模型）
8. RUN_LOG 新增：`automation/seo_factory/RUN_LOG_2026-05-04.md`
9. dry-run 驗證：3 個 Pillar 全通過（score 100，draft payload 正常產生）

### A1 治理層同步
10. 新增 Task Card：`handoff/tasks/T-A2-005-local-seo-factory.md`
11. `CURRENT_STATUS.md` 新增 T-A2-005 任務與 blocker（待 WP 憑證）
12. `projects/maplab-kitchen-web-optimization.md` 補上 Local SEO Factory 區塊
13. `.gitignore` 新增 `automation/seo_factory/output/`（避免提交執行產物）
14. 新增 `test_ollama_execution.py`（Ollama 實跑 + 單一 Pillar 測試）
15. `seo_factory.py` 新增 `OLLAMA_TIMEOUT_SECONDS` 與 `--pillars` 參數，降低批次卡死風險
16. 實測通過：Ollama 本地生成 + WP draft live publish（post_id 1679）

### A6 本地模式路由（2026-05-04 追加）
17. `bot_a6.py` 新增模式切換：`/mode quote|chat|seo` + Telegram 鍵盤選單
18. 報價模式維持原本 `Claude + GAS + Sheets`；聊天/SEO 模式改走本地 `Ollama`
19. 雙人白名單機制保持不變（Owner + Sales user ID）
20. `bot_a6/.env.example` 新增 `OLLAMA_BASE_URL` / `OLLAMA_MODEL_CHAT` / `OLLAMA_TIMEOUT_SECONDS`


## v5.2（Extension）— 2026-04-03

**Extension v5.2：Bot → Extension 剪貼板橋接（方案 2，不需輔助使用權限）**

執行 Agent：A1 Claude Code

### Bot
1. `bot.py`：加入 `/clip [文字]` 指令 — 將文字寫入 `/tmp/maplab_clip.json`
2. `bot.py`：內建輕量 HTTP server（127.0.0.1:9876）跑在 daemon thread，提供 `GET /clip` 端點回傳 JSON + CORS header
3. `bot.py`：新增 `clip_cmd` handler，已掛載到 CommandHandler

### Chrome Extension
4. `manifest.json`：`host_permissions` 新增 `http://localhost/*` + `http://127.0.0.1/*`（Extension fetch localhost 必要）
5. `popup.js`：新增 `fetchFromBot()` 函式 — fetch 127.0.0.1:9876/clip → 寫入 promptText 輸入框
6. `popup.html`：新增「📋 從 Bot 抓取」按鈕（位於注入按鈕上方）
7. 版本升級至 v5.2

### 使用流程
1. Telegram 傳 `/clip 你要傳的文字`
2. 開 Extension popup → 點「📋 從 Bot 抓取」
3. promptText 自動填入 → 點「⚡ 注入到 Claude tab」

---

## v5.4 — 2026-03-28

**Chrome Extension v4.7：加入 A0/A1 角色選項 + MCP 修復**

執行 Agent：A1 Claude Code

### Chrome Extension
1. popup.html：下拉選單加入 `A0｜Telegram 對話機器人` 和 `A1｜系統總管中心`
2. 之前沒放是因為當初 AGENT_RECALL_PROMPTS.md 的 A0/A1 區塊 format 不確定是否符合 parseRecallPrompts regex — 現在加入

### MCP 修復（根本問題解決）
3. 建立 `/maplab-ai-handbook/.mcp.json`（從 `~/.claude/.mcp.json` 複製）
4. 根目錄 `.gitignore` 新增，排除 `.mcp.json` 和 `cookies.txt`（含 API keys，絕不 commit）
5. 根因：MCP 需要專案目錄下有 `.mcp.json`，`~/.claude/.mcp.json` 全域設定不被專案 session 自動讀取

### 教訓
- 下次開 Claude Code session 要在 `maplab-ai-handbook/` 根目錄，才能載入 MCP 工具

---

## v5.2 — 2026-03-27（深夜更新）

**bot.py 記憶修復 + A0/A1 並列架構 + 經驗總結**

執行 Agent：A1 Claude Code（Mac mini 常駐）

### bot.py
1. `--dangerously-skip-permissions` 加入 claude CLI 呼叫
2. 根因確認：`claude -p` one-shot 無記憶，需回到 SDK + conversation_history
3. 對話 log 功能確認完整（log_conversation + git_commit_log_sync）

### 系統架構
4. AGENT_RULES v3.2：A0/A1 並列定位 + 溝通協議（A1 自主建立）
5. CLAUDE.md 同步 AGENT_RECALL_PROMPTS A1 code block
6. A0_USER_PREFERENCES.md 完整版（等 Owner 貼入）
7. start-a1.sh 升級（自動注入 recall prompt + /mcp refresh）

### 經驗紀錄
8. EXP-F007 bot.py 記憶斷裂 + EXP-F008 空白 Code task + EXP-F009 CLAUDE.md 不同步
9. EXP-S007 CRD 遠端打字成功 + EXP-S008 並列架構

---

## v5.1 — 2026-03-27

**A0 總調度秘書建立 + Telegram bot daemon 上線 + Notion 定位降級**

執行 Agent：A0 Cowork Dispatch Secretary

### 系統架構
1. **AGENT_RULES.md v3.0 → v3.1** — 新增 A0 角色（SECTION 1 角色表 + SECTION 1.3 定義）、更新 SECTION 1.2 跨部門協作圖、Notion 定位降級補充
2. **AGENT_RECALL_PROMPTS.md** — 新增 A0 recall prompt + 角色總覽加入 A0
3. **CURRENT_STATUS.md** — 升版至 v5.1、新增 A0 任務（T-A0-001 完成、T-A0-002 可認領）

### Telegram Bot
4. bot/ 目錄建立 — python-telegram-bot v21 daemon
5. launchd 自啟配置（com.maplab.telegrambot.plist）— 24/7 存活，crash 30s 自動重啟
6. 免費指令讀檔模式（9 指令：/status /task /patrol /queue /agent /commit /blocker /refresh /ping）
7. 舊 Claude Code MCP plugin tmux session 清除（解決 409 Conflict）

### Notion 定位
8. Notion 降級為「Owner 可視化報告介面」，不再作為 Agent 狀態來源
9. 新增清理任務 T-A0-002（保留架構，引導到 GitHub）
10. skills/remote-desktop-agent-bridge.md v1.0 — A0 跨機器 Agent 監控技能書（Chrome Remote Desktop 操作 SOP）

---

## v5.0 — 2026-03-26

**A1 系統總管建立 + 角色重組 + MCP 工具接通 + 技能書大更新**

執行 Agent：A1 Claude Code（Mac mini 常駐）

### 系統架構重組
1. **AGENT_RULES.md v2.2 → v3.0** — A2/A3 拆為獨立部門、A1=Claude Code、新增 A6 業務快反應 + A8 影音製作、跨部門協作關係圖、SECTION 2.1 強制存檔規則（30min checkpoint + 接續 Prompt）
2. **AGENT_RECALL_PROMPTS.md v1.0** — 8 角色完整召喚 prompt（身份+斷點+踩過的坑+可用工具+強制存檔規則）
3. **CURRENT_STATUS.md** — 新增知識地圖（14 資料來源路徑）+ MCP 工具表 + 完成項目補齊

### Chrome Extension v2.0 → v4.6
4. v3.0 commit history + checkpoint 偵測
5. v4.0 遠端 JS 載入（失敗，Chrome MV3 CSP 擋）→ v4.2 回歸本地
6. v4.3 角色選擇器（從 RECALL_PROMPTS 即時讀取）
7. v4.4 auto-save token
8. v4.5 移除 commit history 注入
9. v4.6 高對比 UI + 大字體 + 移除 commit 面板
10. **CHANGELOG 完整補齊** v2.0→v4.6（含失敗經驗紀錄）

### MCP 工具接通（6 個已啟用 + 4 個待啟用）
11. **Google Sheets MCP** — A5 報價系統直接讀寫
12. **Google Drive MCP** — A4 素材管理
13. **Google Analytics MCP** — A2/A3 流量分析
14. **Google Search Console MCP** — A2 SEO 排名
15. **Google Ads MCP** — A3 廣告數據（管理 864-994-4780 / 投放 844-336-3178）
16. **Meta Ads MCP** — A3 Facebook/IG 廣告
17. GCP 專案 MAPLAB-AI 建立 + 18 個 API 啟用 + OAuth credentials

### 技能書（21 → 27 本）
18. **skills/a3-social-ads-skills.md** — 多平台貼文 + 廣告成效追蹤
19. **skills/a4-photo-asset-skills.md** — 品牌素材規範 + 數位菜單卡
20. **skills/a5-quotation-engine-skills.md** — 菜單搭配 + 報價生成 + 週活動簡報
21. **skills/a6-sales-rapid-response-skills.md** — 一鍵提案 + 客戶速查 + 需求表單
22. **skills/a7-customer-service-skills.md** — FAQ Top 10 模板 + 品牌語氣
23. **skills/brand-voice-guide.md** — MAPLAB 品牌語氣統一文件（禁用語、平台微調、受眾語氣、談判句型、檢查表）
24. **skills/superpowers-guide.md** — 路由表改為關鍵字自動觸發（23 組觸發詞）

### 基礎設施
25. Mac mini Telegram bot 連線
26. 3 個遠端定時巡查（08:00/16:00/22:00 Taipei）
27. 每小時自動 git pull（LaunchAgent）
28. GitHub Actions system-patrol.yml
29. 自動允許權限設定（Telegram/Bash/Read/Edit/Write/Glob/Grep/WebSearch/Skill）
30. Anthropic Skills 市場加入

### 錯誤紀錄
31. **ERR-006** — A1 自己不守規則，Extension 改版未寫 CHANGELOG

設計原則：
- A1 也是 agent，也會斷線，必須寫完整紀錄
- 穩定優先於聰明（v4.0 遠端架構失敗 → v4.2 回歸本地）
- 所有規則 A1 先遵守，才有資格要求 A2-A8
- 工具接通後更新 RECALL_PROMPTS，確保 agent 知道可以用什麼
- 品牌語氣文件是對外文字的基礎建設，不是可選附件

---

## v4.0 — 2026-03-25

**A2 T-A2-001 完成 + A4 GPS 技能書 + A5 master-data 更新**

執行 Agent：A2 + A4 + A5

1. **A2 T-A2-001 完成** — 57/57 篇文章獨立配圖（0 重複），跨 5 個 Google Drive 相簿上傳 47 張圖片至 WordPress
2. **A4 gps-daily-subdivision-guide.md** — GPS 日常照片細分（Haversine + Takeout JSON）
3. **A4 superpowers-guide v2.1** — 新增 GPS 技能路由
4. **A5 maplab-master-data v1.7** — 格式優化 + TERMS_MASTER 使用條款資料庫化

---

## v3.9 — 2026-03-23

**A1 跨部門溝通 + 系統治理升級**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

跨部門溝通 — TimeTree 事件資料增強：
1. **data/timetree_events_2022_2026.json v2.0** — 從 TimeTree IndexedDB 提取 746 筆外燴事件（含客戶名，2022-2025，排除抓週），供 A5 比對 Google Drive 訂單
2. **CURRENT_STATUS.md v3.9 → v3.10** — 登記 TimeTree v2.0 + 治理升級

系統治理升級 — 解決 Agent 不問問題/不拿技能/做法選錯不回報：
3. **AGENT_STARTUP_PROTOCOL.md v1.3 → v1.5** — Startup Check 新增 Questions for Owner + Skills loaded 強制欄位；Step 7 改為盲點分析格式；新增執行中 5 條規則（每步紀錄、子任務切割、接續 Prompt、自動讀取下階段、方向偏移回報）；臨時任務規則；精簡去重
4. **AGENT_RULES.md v2.0 → v2.2** — SECTION 0 新增 2 條啟動阻擋規則
5. **skills/task-progress-guide.md v1.0 → v1.1** — 新建必拿技能書（Progress Log + 子任務切割 + 自動讀取下階段 + Resume Prompt + 方向偏移），每章補真實範例
6. **skills/superpowers-guide.md v1.5 → v1.6** — 路由表新增「所有任務（必拿）→ task-progress-guide」

設計原則：
- SECTION 0 只管啟動阻擋（2 條規則）
- PROTOCOL 管流程骨架（規則寫「做什麼」）
- task-progress-guide 管方法論（範例 + 原則寫「怎麼做好」）
- 即使 Agent 沒讀技能書，PROTOCOL 裡的精簡版規則已能擋住核心行為

## v3.8 — 2026-03-20

**T-A1-002 Phase 4.1 系統治理升級 — 全部完成**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

T-A1-002 全部 7 個子任務完成，Phase 4.1 結案。

更新（8 commits）：
1. **projects/maplab-kitchen-web-optimization.md v1.0** — 新增官網 SEO/RWD/PageSpeed 專案文件，從 web-optimization repo 彙整 23 項優化紀錄
2. **SYSTEM_MAP.md v2.1 → v2.2** — Repo 分工地圖新增 web-optimization（私有・執行層）、projects 6→8
3. **REPO_SYNC_RULES.md v1.0 → v1.1** — Repo Roles 新增 web-optimization、Owner 同步職責更新
4. **AGENT_STARTUP_PROTOCOL.md v1.2 → v1.3** — Step 5 新增 Superpowers 規則、新增 Step 7 ABCDE 互動選項
5. **handoff/archive/ 建立** — 歸檔區 README 索引（5 個舊 handoff 檔案待 Owner 手動移入）
6. **T-A1-002 Task Card 結案** — 全部子任務標記完成 + Checkpoint 3
7. **CURRENT_STATUS.md v3.7 → v3.8** — T-A1-002 結案 + Phase 4.1 完成
8. **TASK_QUEUE.md** — T-A1-002 標記完成

設計原則：
- web-optimization 收編進治理，所有 5 個 repo 都有對應的 projects/ 文件
- PROTOCOL 新增 Superpowers 規則確保 Agent 知道怎麼使用技能書
- ABCDE 互動選項讓 Agent 啟動後主動提供選擇，減少 Owner 決策負擔
- archive/ 建立歸檔機制，handoff/ 不再堆積過時文件

---

## v3.7 — 2026-03-20

**T-A1-002 子任務①⑥：AGENT_RULES v2.0 + CURRENT_STATUS/TASK_QUEUE 更新**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

問題：v3.6 巡查的 CHANGELOG 宣稱 SECTION 0 已修復，但實際內容未變更。缺乏 Repo 管控規則和 Notion 禁令。

修復（3 commits）：

T_RULES.md v1.9 → v2.0** — SECTION 0 真正修復（Step 4 加 CURRENT_STATUS FIRST + TASK_QUEUE；新增 Step 5 Startup Check）；新增 SECTION 5 Repo 管控 + Notion 禁令；版本表 v1.8/v1.9 順序修正
2. **CURRENT_STATUS.md v3.6 → v3.7** — 版本升至 v3.7；Phase 改為 4.1 進行中；T-A1-002 登錄；AGENT_RULES v2.0 決策紀錄
   3. **TASK_QUEUE.md** — T-A1-002 登錄高優先；日期更新

      4. 設計原則：
      5. - 召喚 Prompt 必須言行一致（CHANGELOG 說改了就真的要改）
         - - Repo 管控 + Notion 禁令寫入 AGENT_RULES 確保所有 Agent 開工就讀到
           - - 狀態文件即時反映進行中任務，避免其他 Agent 做衝突修改
## v3.6 — 2026-03-19

**系統巡查：關鍵 20% 問題修復 — 召喚 Prompt + Git 規則 + 過時文件**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

**巡查發現的 7 個問題（按衝擊排序）：**
1. 🔴 AGENT_RULES 召喚 Prompt 不導向 CURRENT_STATUS（每個 Agent 走錯起點）
2. 🔴 AGENT_RULES SECTION 2 Git 規則要求 PR+branch 但實際直接 commit（矛盾）
3. 🔴 REPO_SYNC_RULES 引用已刪除的 PROJECT_CONTEXT + 標示錯誤
4. 🔴 maplab-master-data.md 重複 SECTION 3 + 任務狀態停在 v1.4 + Notion 引用
5. 🟡 maplab-ads-monitor.md 未反映 A2+A3 合併
6. 🟡 三個檔案末尾殘留 Stop Claude（確認為讀取 artifact，非實際檔案內容）
7. 🟢 seo-ads-agent.md 十三節標題 typo

**修復（5 commits）：**
- AGENT_RULES.md v1.8 → v1.9 — SECTION 0 召喚 Prompt 加入 CURRENT_STATUS 第一步 + TASK_QUEUE + Startup Check；SECTION 2 Git 規則改為直接 commit 對齊實務
- REPO_SYNC_RULES.md v0.1 → v1.0 — 全面重寫：移除 PROJECT_CONTEXT 引用（3處）、修正 repo 公私標示、對齊 CURRENT_STATUS/TASK_QUEUE、A6→A2/A3 SEO & Ads Team
- projects/maplab-master-data.md v1.4 → v1.5 — 修正重複 SECTION 3（改為 SECTION 10）、更新任務狀態（Items 139筆/QUOTE_DRAFT MVP/TimeTree）、接手前必讀移除 Notion
- projects/maplab-ads-monitor.md v1.1 → v1.2 — 反映 A2+A3 合併、接手前必讀加 CURRENT_STATUS
- projects/seo-ads-agent.md — 修正十三節「相關連結h」typo

**設計原則：**
- 20/80 法則：修 4 個高衝擊問題就消除 80% 的 Agent 誤導風險
- 召喚 Prompt 是全系統入口，修一處影響所有 Agent
- Git 規則必須反映實際操作，否則新 Agent 會猶豫要不要開 PR

---

## v3.5 — 2026-03-19

**Phase 4.2：全系統文件對齊 — 治理重構後的文件同步更新**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

**問題：Phase 4 第一階段建立了新治理架構（CURRENT_STATUS / TASK_QUEUE / Task Card / PROTOCOL v1.2），但以下文件仍停留在舊版結構：**
- README：版本 v2.9、Quick Start 沒導向 CURRENT_STATUS、Agent Roster A2/A3 分開
- SYSTEM_MAP：skills 寫 11 個（實際 14）、閱讀順序沒提 CURRENT_STATUS、Repo 地圖缺新文件
- AI_WORKFLOW_MAP：A2/A3 分開列、Handoff Protocol 沒提 Task Card、Collaboration Rules 缺 CURRENT_STATUS 優先
- BOARD：系統版本寫 v3.1、Phase 寫 Phase 3、Session Log 缺 4 個 session 記錄

**更新：**
- README.md v2.3 → v2.4 — 頂部新增 CURRENT_STATUS 優先入口指引、Quick Start 第一步改為 CURRENT_STATUS、Agent Roster A2+A3 合併為 SEO & Ads Team、skills 11→14、Document Structure 新增 CURRENT_STATUS / TASK_QUEUE / handoff/tasks/、系統版本 v3.4
- SYSTEM_MAP.md v2.0 → v2.1 — Repo 地圖新增 CURRENT_STATUS + TASK_QUEUE、Agent 分工地圖 A2+A3 合併、skills 11→14（新增 3 本）、閱讀順序第一步改為 CURRENT_STATUS、七唯一資料來源新增 CURRENT_STATUS 優先規則
- AI_WORKFLOW_MAP.md v2.1 → v2.2 — A2+A3 合為 SEO & Ads Team、Handoff Protocol 新增 Task Card + Handoff Checkpoint 步驟、Collaboration Rules 新增 Rule 8 CURRENT_STATUS 優先 + Rule 9 Task Card 記憶
- CURRENT_EXECUTION_BOARD.md v2.1 → v2.2 — 頂部新增 CURRENT_STATUS 指引、系統版本 v3.1→v3.5、Phase 更新為 Phase 4、Session Log 補齊 S-D/E/F/G（4 個 session）、A2+A3 合併顯示、重要連結新增 CURRENT_STATUS + TASK_QUEUE

**設計原則：**
- Phase 4 第一階段建了新架構，第二階段確保所有舊文件指向新架構
- 所有入口文件頂部都有 CURRENT_STATUS 指引，避免 Agent 走錯路
- Session Log 補齊確保歷史可追溯

---

## v3.4 — 2026-03-18

**Phase 4：系統治理重構 — 單一入口 + 任務池 + 強制 Startup/Handoff**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）
觸發來源：ChatGPT 對話「Agent協作與版本管理」v0.1–v0.3 問題診斷

**診斷的問題：**
- Agent 被 GitHub 歷史紀錄混淆，分不清已完成和進行中
- 簽到簽退機制無人遵守（沒有強制卡點）
- 分頁當掉 = 記憶歸零（進度只存在聊天上下文）
- 沒有唯一真相入口，Agent 自己猜要讀哪個檔案

**新增：**
- CURRENT_STATUS.md v1.0 — 唯一最新狀態入口（極簡控制塔），所有 Agent 開工前第一讀，優先於所有其他文件
- TASK_QUEUE.md v1.0 — 任務池，統一管理全部待辦，含認領規則和 Task Claim 格式
- handoff/tasks/TASK_CARD_TEMPLATE.md v1.0 — 標準化任務卡模板（Goal/Confirmed/Done/Next/Blocker/Checkpoint）

**更新：**
- AGENT_STARTUP_PROTOCOL.md v1.1 → v1.2 — Step 1 改為 CURRENT_STATUS.md、9 步精簡為 6 步、新增強制 Startup Check 輸出格式、新增強制 Handoff Checkpoint 格式

**設計原則（來自 ChatGPT 診斷）：**
- 不靠 Agent 自律，靠系統強制（沒輸出 Startup Check = 不算啟動）
- 記憶外部化（Task Card + Checkpoint），分頁可死但任務不失憶
- 治理層（A1/Owner）維護全局 + 執行層（其他 Agent）只讀任務卡
- 大局觀分層：人人看得到全局入口，但不需人人完整載入全局

---

## v3.3 — 2026-03-18

**新增 A4/A5 專用技能書：資料清洗工具箱 + 相簿整理 Pipeline 工具鏈**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

**新增：**
- skills/sheets-data-cleaning-guide.md v1.0 — A5 資料清洗公式工具箱（TRIM/REGEXREPLACE/COUNTIF）、Apps Script 自動化（批次清洗/重複偵測/防重複匯入/超時保護）、資料清洗 SOP、MAPLAB 特定情境解法（OrderLines R6/QUOTE_DRAFT/DST去重）
- skills/photo-pipeline-toolkit-guide.md v1.0 — A4 相簿整理全流程工具鏈：Takeout JSON metadata 合併、EXIF 讀寫（Pillow/piexif/HEIC）、重複偵測（MD5+perceptual hash）、Gemini Vision AI 分類、WebP 轉換+SEO 重命名、Colab checkpoint 機制、ASSET_LOG Sheets 追蹤整合

**更新：**
- skills/superpowers-guide.md v1.5 — 路由表新增 sheets-data-cleaning-guide + photo-pipeline-toolkit-guide，快速大綱新增兩本技能書

**設計原則：**
- 從 A4/A5 實戰痛點出發（品名後綴不統一、Apps Script 重複匯入、Takeout metadata 遺失、122K files 規模處理）
- 提供可直接複製使用的公式和 Python 程式碼片段
- 兼顧安全機制（預覽模式、備份、超時保護、checkpoint）

---

## v3.2 — 2026-03-18

**合併 A2+A3 為 SEO & Ads Team + 全 Agent 狀態巡查**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

**更新：**
- AGENT_RULES.md v1.8 — A2（SEO）+ A3（Ads）合併為 SEO & Ads Team，新增 SECTION 1.2 SEO↔Ads 協作協議（雙向資料流 + 共享文件 + 交接觸發點 + 協作原則），錯誤 005 記錄
- CURRENT_EXECUTION_BOARD.md v2.1 — A1 簽退 + Session Log S-C + 全 Agent 狀態巡查更新（A2 Detasys 動態、A5 Items 清洗進度、Issue #009 修復確認）

**設計原則：**
- A2 和 A3 共享同一條行銷漏斗（關鍵字→內容→廣告→轉換），分開執行會導致資訊斷層
- 新增 5 個交接觸發點，確保 SEO 和 Ads 任何變更都能即時通知對方
- 不是取消角色差異，而是讓資訊流動更平滑

---

## v3.1 — 2026-03-18

**Phase 3：多 Agent 團隊協作強化 — 簽到/簽退 + 檔案衝突檢查 + 技能書路由**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

**更新：**
- CURRENT_EXECUTION_BOARD.md v2.0 — 新增 Active Session 即時簽到區（Agent/時間/檔案/預計完成）、新增 Session Log 歷史紀錄表、簽到規則說明、系統狀態更新為 Phase 3
- AI_WORKFLOW_MAP.md v2.1 — 新增 Rule 6 簽到/簽退、新增 Rule 7 檔案衝突檢查、Handoff Protocol 升級為 5 步（新增 Step 0 清除 Active Session）
- AGENT_STARTUP_PROTOCOL.md v1.1 — Step 2 移除已刪除的 PROJECT_CONTEXT.md 改為讀 BOARD Active Session、新增 Step 9 簽到、啟動步驟 8→9 步、收尾 SOP 新增清除簽到 + 寫 Session Log（修復 Issue #009）
- skills/superpowers-guide.md v1.4 — 新增「任務類型 → 建議預讀技能書」路由表（10 種任務對照）、修正 troubleshooting-hub 格式

**設計原則：**
- 簽到/簽退解決多 Agent 並行時的檔案衝突問題
- Session Log 讓每次 session 的工作有跡可查
- 技能書路由表讓 Agent 開工前就知道該讀什麼，而非卡住才查

---

## v3.0 — 2026-03-17

**Notion vs GitHub 對齊清理 Session A — README 整合 + 過時文件修正**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

**更新：**
- README.md v2.3 — 整合 PROJECT_CONTEXT.md 內容（Section 5.1/5.2），更新 Core Projects 狀態表，新增 Section 10 唯一資料來源規則，移除 A6，Quick Start 從 8 步簡化為 7 步
- PROJECT_CONTEXT.md — 已刪除（內容整合入 README Section 5）
- CURRENT_EXECUTION_BOARD.md v1.7 — 刪除重複版本行（v2.9/v2.6 並存→僅 v2.9），整理 A3 區塊，已知問題全部標記 ✅ 已解決
- projects/maplab-ads-monitor.md v1.1 — A6→A3 Ads Team 對齊，移除 Notion 引用，更新協作邊界表
- handoff/HANDOFF_TEMPLATE.md v1.1 — 移除 Notion 引用，任務來源改為 GitHub，更新歷史交接表
- SYSTEM_MAP.md v2.0 — 7 張地圖全面重寫：Repo 分工（A6→Ads Team）、Agent 分工、資料流、閱讀順序（移除 PROJECT_CONTEXT）、新增技能書速查地圖、新增唯一資料來源規則
- AI_WORKFLOW_MAP.md v2.0 — A6 合併入 A3 Ads Team、移除 PROJECT_CONTEXT 引用、新增 Stuck Protocol 區段（troubleshooting-hub 路由）、Handoff 增加 CURRENT_EXECUTION_BOARD 步驟、新增協作規則 5（用技能書）
- AGENT_RULES.md v1.7 — Notion 欄位加刪除線（5 個 Agent 的 Notion 進度欄），欄位標題改為「僅人類參考，非 Agent 依據」，新增 ⚠️ 警告標語
- CURRENT_EXECUTION_BOARD.md v1.8 — Phase 3 多 Agent 團隊協作強化規劃寫入：4 項待辦任務（簽到/簽退機制、協作規則升級、STARTUP_PROTOCOL 串接、技能書主動路由）、新增已知問題 009、A1 狀態更新為 Phase 3 已規劃待執行

**設計原則：**
- GitHub 是所有 Agent 的唯一資料來源，Notion 僅供人類使用
- 刪除功能重複的文件（PROJECT_CONTEXT），降低誤讀風險
- 所有過時的 A6 引用統一改為 A3 Ads Team

---

## v2.9 — 2026-03-17

**gtm-conversion-setup.md v1.1 — GTM v15 發布 + 執行狀態更新**

執行 Agent：A3 Ads Monitor Agent（Claude Opus 4.6）

**更新：**
- GTM 版本 15 已發布至 Live 環境：Meta Pixel Contact 事件（LINE Click + Phone Click）
- - `projects/gtm-conversion-setup.md` v1.1 — 執行狀態表格更新，重複 Pixel 已確認
  - - 容器品質警告確認為誤判（該頁面實際已安裝 GTM 代碼）

---

## v2.8 — 2026-03-17

**troubleshooting-hub v1.0 + AGENT_STARTUP_PROTOCOL v1.1 + superpowers-guide v1.3**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

更新：
- skills/troubleshooting-hub.md v1.0 — 新建：Agent 卡住急救手冊，13 個常見症狀診斷表 + 回報流程 + 使用規則
- - AGENT_STARTUP_PROTOCOL.md v1.1 — 新增「執行中卡住怎麼辦」區段，引導 Agent 查 troubleshooting-hub
  - - skills/superpowers-guide.md v1.3 — MAPLAB ## v2.9 — 2026-03-17g-hub 行 + 詳細區段

    - 設計原則：
    - - troubleshooting-hub 只做路由（症狀 → 技能書），不重複寫解法
      - - 找不到解法 → 回報 A1 → A1 補充到 hub → 全員受益
        - - 解決核心問題：Agent 卡住時浪費 context 亂試，改為查表找解法

          - ---
## v2.7 — 2026-03-17

**seo-ads-agent.md v2.1 + gtm-conversion-setup.md v1.0**

執行 Agent：A3 Ads Monitor Agent（Claude Sonnet 4.6）

**更新：**
- `projects/seo-ads-agent.md` v2.1 — 素材要求區段新增 PMax 問句型標題建議（2 個，小幅測試用，追蹤 CTR 變化）
- - `projects/gtm-conversion-setup.md` v1.0 — 新建 GTM 轉換事件設定 SOP（LINE 點擊 / 表單送出 / 電話點擊）
  - - 版本紀錄表格修正（v1.1/v1.2 遺失修復 + v2.1 新增）
    - - 相關連結新增 GTM SOP 路徑

      - **調整 1 — PMax 問句型標題（小幅測試）：**
      - - 新增標題 1：辦週歲派對，餐點怎麼準備才不手忙腳亂？
        - - 新增標題 2：台南外燴推薦｜質感派對餐桌，不用自己張羅
          - - 追蹤方式：14 天後比較問句型 vs 原有標題 CTR 差異
            - - 目標：CTR 從 0.63% 提升至 1.0–1.5%

              - **調整 3 — GTM 轉換事件 SOP：**
              - - 三個事件完整設定步驟：GTM 觸發條件 + Meta Pixel 標籤 + Google Ads 轉換標籤
                - - 包含驗證方法（Meta Pixel Helper + Google Ads 轉換報表）
                  - - 包含重複 Pixel 處理步驟
                    - - 包含給 A2 SEO Agent / A4 Pipeline Agent / A5 Data Agent 的備註
                      - - 目標：PMax CPA 從 NT$322 降至 NT$200 以下

                        - ---



## v2.6 — 2026-03-17

**seo-ads-agent.md v2.0 完整重寫 — 修正亂碼 + 廣告系統框架建立**

執行 Agent：A3 Ads Monitor Agent（Claude Sonnet 4.6）

**更新：**
- `projects/seo-ads-agent.md` v2.0 — 直接 commit 到 main，修正舊版 `> > - [ ]` 亂碼格式，完整重寫為 13 個章節的廣告系統技術文件
  - 一、核心目標（短期現金流 + 中長期品牌/SEO）
  - 二、整體漏斗設計（Top/Mid/Bottom Funnel）
  - 三、帳號資訊
  - 四、總預算配置（Google NT$300/天 + Meta NT$300/天 = NT$600/天）
  - 五、Google Ads 廣告系統（PMax 詳細設定 + 近期成效）
  - 六、Meta 廣告系統（目前 2 則進行中 + 1 則草稿）
  - 七、SEO 對接（給 SEO Agent 的關鍵字清單）
  - 八、素材對接（給素材 Agent 的規格 + 現況）
  - 九、待辦事項
  - 十、下次 Agent 接手必問清單
  - 十一、Pixel 串接確認
  - 十二、版本紀錄
  - 十三、相關連結

**廣告現況紀錄（截至 2026-03-17）：**
- Google PMax：NT$300/天，進行中，30天花費 NT$2,257，轉換 7 次，CPA NT$322
- Meta B組公關窗口：進行中，CPA NT$5/互動
- Meta B組企業窗口：進行中，CPA NT$13/互動
- Meta 策略一冷受眾：草稿，素材製作中，待上線

---


## v2.5 — 2026-03-16（最新）

**A3 廣告策略一執行 + 困難回報 + TA 建議文件化**

執行 Agent：A3 Ads Monitor Agent（Claude Sonnet 4.6）

**更新：**
- `projects/seo-ads-agent.md` v1.4 — 補充現有策略觀察、策略一冷受眾 TA 設定建議（完整描述文字）、素材計畫（C-1/C-2/C-3）、目前困難與暫時解決方案
- `CURRENT_EXECUTION_BOARD.md` v1.3 — A3 狀態更新為進行中，Canva C款素材 WIP 狀態記錄

**執行進度：**
- ✅ Notion 策略文件閱讀完成
- ✅ Meta 廣告組合受眾描述欄位填寫（策略一冷受眾 52608263444730）
- ✅ @maplabkitchen IG 圖片研究，選定婚禮風桌景照片
- ✅ Canva 1080x1080 C款背景圖建置完成
- 🔄 Canva 文字層（C-1/C-2/C-3）尚未完成
- ⏳ PR #1 + PR #2 awaiting user merge

**已知限制：**
- Meta 廣告操作需使用者明確確認，Claude 不自行 acting
- Canva 素材需繼續完成文字層

---

## v2.5 — 2026-03-15（最新）

**ai-model-guide v1.1 — GPT特殊地位補充 + 防prompt過長技能**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `skills/ai-model-guide.md` v1.1 — 補充 GPT 特殊地位：最早付費訂閱、長期記憶庫、幻覺校正 SOP、Step 0 背景確認協作流程
- `skills/context-compression-guide.md` v1.0 — 新建：防 prompt too long 技能書，包含 session 規劃、階段存檔、摘要格式、token 壓縮 SOP

**設計原則：** GPT 記憶需經使用者確認才可信；每個 session 應在 context 50% 時主動進行階段存檔

---

## v2.4 — 2026-03-15

**合併 A3+A6 為 Ads Team + 新增 AI 特性技能書**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `AGENT_RULES.md` v1.6 — 合併 A3+A6 為 Ads Team，新增 SECTION 1.1 任務分工表，新增 skills/ai-model-guide.md 引用，錯誤 004 記錄
- `skills/ai-model-guide.md` v1.0 — 新建：Claude / Gemini / GPT 特性說明 + 選 AI 速查表 + Ads Team 跨 AI 協作流程範例

**設計原則：** 以技能書取代固定角色召喚，任何 AI 接手時依任務性質查 ai-model-guide.md 選用最合適工具，不需重複說明背景

---

## v2.3 — 2026-03-15

**A1 系統巡查 + CURRENT_EXECUTION_BOARD 修正**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `CURRENT_EXECUTION_BOARD.md` v1.2 — 修正重複區塊（v1.0+v1.1 並存問題），新增「已知規則不明問題」SECTION，新增問題 004/005/006，同步 A4 路線等待狀態
- **發現問題（問題 004–006，詳見 CURRENT_EXECUTION_BOARD.md）：**
  - 問題 004：A3 與 A6 職責邊界不清（ads_agent.py 歸屬模糊）
  - 問題 005：maplab-master-data.md header v1.3 與實際內容 v1.4 版本矛盾
  - 問題 006：CURRENT_EXECUTION_BOARD.md 重複區塊（已本次修正）

---

## v2.2 — 2026-03-14

**初始版本歷史建立**

執行 Agent：A1 Handbook Agent

**更新：**
- 初始 CHANGELOG.md 建立
- 記錄 maplab-ai-handbook 早期版本歷史
