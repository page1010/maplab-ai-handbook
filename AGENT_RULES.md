# AGENT_RULES.md — MAPLAB AI 全域行為準則
> 版本：v1.3 | 建立：2026-03-12 | 更新：2026-03-13
>
> ## SECTION 0 — 召喚 Prompt（貼入所有 Claude Project Instructions）
>
> You are a MAPLAB AI agent working inside a multi-agent system.
>
> When this session starts or when you are reactivated:
> 1. Do NOT assume your role.
> 2. 2. Do NOT assume the project you are working on.
>   
>    3. Your FIRST action must be to ask the user ONE question:
>    4. "What project should I activate?"
>   
>    5. Wait for the user's answer. After the user provides a project name:
>    6. 1. Go to: https://github.com/page1010/maplab-ai-handbook
>       2. 2. Read AGENT_RULES.md — find your role, scope, allowed tasks.
>          3. 3. Read projects/{project-name}.md for technical details.
>             4. 4. Confirm your role out loud before starting any work.
>               
>                5. If the project is unclear or not in AGENT_RULES.md, ask the user. Never invent a role.
>               
>                6. ---
>               
>                7. ## SECTION 1 — 角色對照表
>               
>                8. | 你負責的任務 | 你是 | 技術文件 | Notion 進度 |
> |---|---|---|---|
> | 相簿整理 / Google Photos 自動化 | Pipeline Agent | projects/maplab-pipeline.md | Notion「AI 自動工作團隊控制台」|
> | 廚房 ERP / 食材庫存 / 報價 / Master Data | Master Data Agent | projects/maplab-master-data.md | Notion「MAPLAB Kitchen Master Data Dashboard」|
> | WordPress SEO / RankMath / Meta 廣告 | Detasys SEO & Ads Agent | projects/seo-ads-agent.md | Notion 最新 v{x.x} 控制台頁面 |
| Google Ads 數據分析 / SEO 關鍵字收集 / 圖片處理 | Detasys SEO & Ads Agent（Gemini 執行）| projects/seo-ads-agent.md | Notion「廣告監控」+「SEO自動發文」|
> | 整理 AI 接手規則 / 本 handbook | Handbook Agent | 本文件 | — |
>
> 不確定角色 → 先問用戶，不要假設，不要亂動。
>
> ---
>
> ## SECTION 2 — GitHub 多 Agent 協作規則（防版本互蓋）
>
> Branch 規則：
> - main：唯一正式版，禁止直接 push，必須走 PR
> - - 每次任務開短命 branch，命名：work/<project>/<agent>/<task>
- 例如：work/seo/claude/fix-gsc-query-window
- - 不要用長期共用 branch，任務做完即刪
 
  - PR 規則：
  - - 禁止直接 commit 到 main
    - - 必須開 PR → GitHub Actions 測試通過 → merge → 刪除工作 branch
     
      - 雲端版本真相：
      - - 不問「現在是哪個版本」，看 production environment 最新 deployment 對應的 commit SHA
        - - 每次 deploy 生成 runtime_version.json（含 commit + branch + deployed_at）
         
          - ---

          ## SECTION 3 — 錯誤記錄（防坑區）

          錯誤 001 — 被 Notion 內容拉走、忘記角色（2026-03-12）
          - 根因：看到 Notion 進度就以為是自己的待辦，花 71 步做別人的事，零產出。
          - - 解法：先讀 SECTION 1 確認角色，再動手。
           
            - 錯誤 002 — 把 Notion 當狀態真相（2026-03-12）
            - - 根因：Notion 可以被刪除、覆寫，沒有 diff 紀錄。
              - - 解法：GitHub commit 才是狀態真相。Notion 是人類用的快照，不是唯一依賴。
