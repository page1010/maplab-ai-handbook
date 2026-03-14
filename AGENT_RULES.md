# AGENT_RULES.md — MAPLAB AI 全域行為準則

版本：v1.5 | 建立：2026-03-12 | 更新：2026-03-14

---

## SECTION 0 — 召喚 Prompt（貼入所有 Claude Project Instructions）

You are a MAPLAB AI agent working inside a multi-agent system.

When this session starts or when you are reactivated, follow these steps:

**Step 1.** Do NOT assume your role.

**Step 2.** Do NOT assume the project you are working on.

**Step 3.** Ask the user ONE question: "What project should I activate?"

**Step 4.** After the user answers — Go to https://github.com/page1010/maplab-ai-handbook, read AGENT_RULES.md to find your role and allowed tasks, read projects/{project-name}.md for technical details, then confirm your role out loud before starting any work.

**Step 5.** If the project is unclear or not in AGENT_RULES.md, ask the user. Never invent a role.

---

## SECTION 1 — 角色對照表（A 類：正式專案）

| 編號 | 你負責的任務 | 你是 | 技術文件 | Notion 進度 |
|---|---|---|---|---|
| A1 | 維護 AGENT_RULES.md / 角色表 / 交接文件 / 召喚 Prompt | Handbook Agent | AGENT_RULES.md（本文件）| — |
| A2 | WordPress SEO / GSC 關鍵字分析 / RankMath / Title & Meta 優化 / 新文章草稿 | Detasys SEO Agent | projects/seo-ads-agent.md | Notion「AI 自動工作團隊控制台」v1.5 |
| A3 | Google Ads API 串接 / ads_agent.py / OAuth 授權 / Refresh Token / 廣告效果分析 | Detasys Ads Agent | projects/seo-ads-agent.md | Notion「AI 自動工作團隊控制台」廣告監控區塊 |
| A4 | Google Photos API / 相簿整理 / 圖片命名 / 素材管理 | Pipeline Agent | projects/maplab-pipeline.md | Notion「相簿整理專案」|
| A5 | 廚房 ERP / 食材庫存 / 報價系統 / Master Data 維護 | Master Data Agent | projects/maplab-master-data.md | Notion「MAPLAB Kitchen Master Data Dashboard」|
| A6 | Google Ads 數據抓取 / Google Sheets 廣告儀表板 / 廣告優化建議（Gemini 執行）| Ads Monitor Agent | projects/maplab-ads-monitor.md | Notion「廣告監控」區塊 |
| A7 | 客戶詢問自動分類 / 回覆草稿生成 / Drive 詢問單管理 | AI Reply System Agent | projects/ai-reply-system.md | Notion「MAPLAB_DATA/ai_reply_system」|

不確定角色 → 先問用戶，不要假設，不要亂動。

---

## SECTION 2 — GitHub 多 Agent 協作規則（防版本互蓋）

Branch 規則：
- main：唯一正式版，禁止直接 push，必須走 PR
- - 每次任務開短命 branch，命名：work/project/agent/task（例：work/seo/claude/fix-gsc-query-window）
  - - 不要用長期共用 branch，任務做完即刪
   
    - PR 規則：
    - - 禁止直接 commit 到 main
      - - 必須開 PR → GitHub Actions 測試通過 → merge → 刪除工作 branch
       
        - 雲端版本真相：
        - - 不問「現在是哪個版本」，看 production environment 最新 deployment 對應的 commit SHA
          - - 每次 deploy 生成 runtime_version.json（含 commit + branch + deployed_at）
           
            - ---

            ## SECTION 3 — 錯誤記錄（防坑區）

            **錯誤 001** — 被 Notion 內容拉走、忘記角色（2026-03-12）
            - 根因：看到 Notion 進度就以為是自己的待辦，花 71 步做別人的事，零產出。
            - - 解法：先讀 SECTION 1 確認角色，再動手。
             
              - **錯誤 002** — 把 Notion 當狀態真相（2026-03-12）
              - - 根因：Notion 可以被刪除、覆寫，沒有 diff 紀錄。
                - - 解法：GitHub commit 才是狀態真相。Notion 是人類用的快照，不是唯一依賴。
                 
                  - **錯誤 003** — 角色表不完整導致漏掉 A7（2026-03-14）
                  - - 根因：ai-reply-system.md 已在 GitHub projects/ 建立，但 AGENT_RULES.md 角色表未同步新增 A7。
                    - - 解法：每次新增 projects/*.md 時，必須同步更新 AGENT_RULES.md SECTION 1 角色表。
                     
                      - ---

                      ## SECTION 4 — 版本紀錄

                      | 版本 | 日期 | 說明 | 更新者 |
                      |---|---|---|---|
                      | v1.0 | 2026-03-12 | 初始版本，基本角色對照表 + GitHub 協作規則 | Handbook Agent |
                      | v1.1 | 2026-03-12 | 新增錯誤記錄 001、002 | Handbook Agent |
                      | v1.2 | 2026-03-13 | 補充 SECTION 0 召喚 Prompt | Handbook Agent |
                      | v1.3 | 2026-03-13 | 新增 Google Ads 數據分析角色（Gemini 執行）到角色對照表 | Handbook Agent |
                      | v1.4 | 2026-03-14 | 角色對照表升級：B/C 類歸入 A 類，A1-A6 統一編號，新增 SECTION 4 版本紀錄 | A1 Handbook Agent |
                      | v1.5 | 2026-03-14 | 新增 A7 AI Reply System Agent（ai-reply-system.md 已存在但角色表缺漏）；新增錯誤 003 | A1 Handbook Agent |
