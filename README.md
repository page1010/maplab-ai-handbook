# 🤖 AI Agent Handbook — MAPLAB

> **每次接手前，請先讀這份文件。讀完你就知道現在系統在哪、你要做什麼。**
>
> ---
>
> ## ⚡ 30 秒懂整個系統
>
> MAPLAB 是一個由 AI agents 協作維護的廚房品牌自動化系統，包含三個子專案：
>
> | 專案 | 職責 | 狀態 |
> |------|------|------|
> | [maplab-pipeline](https://github.com/page1010/maplab-pipeline) | Google Photos → WebP → Drive → Notion 自動化 | Phase 1 進行中 |
> | [maplab-master-data](https://github.com/page1010/maplab-master-data) | ERP 主數據、食材庫存、訂單管理 | v0.7 穩定 |
> | SEO & Ads Agent | WordPress SEO + Meta 廣告自動化 | OAuth 修復中 |
>
> **Notion 控制台**（任務看板、最新交辦）：請向 owner 索取連結，或搜尋「AI 自動工作團隊控制台」
>
> ---
>
> ## 🗂️ 本 Repo 結構
>
> ```
> maplab-ai-handbook/
> ├── README.md              ← 你現在在這裡（30 秒懂系統）
> ├── AGENT_RULES.md         ← 所有 agent 共用行為準則
> ├── SYSTEM_MAP.md          ← 三專案關係圖 + 資料流
> ├── .env.example           ← 全專案環境變數清單（只有 key 名，無值）
> ├── CONTRIBUTING.md        ← 文件撰寫規則
> ├── projects/
> │   ├── maplab-pipeline.md       ← Pipeline 專案技術文件
> │   ├── maplab-master-data.md    ← Master Data 專案技術文件
> │   ├── seo-ads-agent.md         ← SEO & Ads agent 技術文件
> │   └── integration.md           ← 三專案整合與資料流說明
> ├── handoff/
> │   └── HANDOFF_TEMPLATE.md      ← 交接模板（每次工作結束必填）
> └── skills/
>     └── superpowers-guide.md     ← Superpowers AI Skills 導覽
> ```
>
> ---
>
> ## 🚀 Agent 接手 SOP
>
> 每次 AI agent 接手時，按以下順序操作：
>
> 1. **讀 README.md**（本文件）— 了解系統全貌
> 2. 2. **讀 `AGENT_RULES.md`** — 確認行為準則與禁止事項
>    3. 3. **讀 `projects/[你負責的專案].md`** — 了解專案現況
>       4. 4. **讀 Notion 控制台的「下一棒任務」** — 確認當前交辦事項
>          5. 5. **開始工作**，完成後更新 Notion checkpoint
>             6. 6. **填寫 `handoff/HANDOFF_TEMPLATE.md`**，寫下下一棒任務
>               
>                7. > 💡 之後只需對 AI 說：「請先閱讀 github.com/page1010/maplab-ai-handbook 的 README，以及 Notion AI Agent Handbook，然後接手 [任務]。」
>                   >
>                   > ---
>                   >
>                   > ## 📌 三專案快速連結
>                   >
>                   > ### maplab-pipeline
>                   > - GitHub: https://github.com/page1010/maplab-pipeline
>                   > - - 職責：相簿自動化（Google Photos → WebP 壓縮 → Drive 備份 → Notion 記錄）
>                   >   - - 目前卡點：Phase 1 等待 OAuth Desktop App credentials
>                   >     - - 詳細文件：[projects/maplab-pipeline.md](projects/maplab-pipeline.md)
>                   >      
>                   >       - ### maplab-master-data
>                   >       - - GitHub: https://github.com/page1010/maplab-master-data
>                   >         - - 職責：廚房 ERP 主數據（食材 174 項、訂單管理、供應商）
>                   >           - - 目前卡點：2025 訂單 import 格式問題
>                   >             - - 詳細文件：[projects/maplab-master-data.md](projects/maplab-master-data.md)
>                   >              
>                   >               - ### SEO & Ads Agent
>                   >               - - 無獨立 GitHub repo（腳本在本機）
>                   >                 - - 職責：WordPress SEO 優化 + Meta 廣告 ROAS 自動化
>                   >                   - - 目前卡點：OAuth token 過期（Web App → Desktop App 切換）
>                   >                     - - 詳細文件：[projects/seo-ads-agent.md](projects/seo-ads-agent.md)
>                   >                      
>                   >                       - ---
>                   >                       
## ⚠️ 絕對禁止事項

- `.env` 金鑰、token、密碼**絕對不能**進 GitHub
- - Pipeline 禁止刪除 Google Photos 原始相片（只讀取）
  - - 不得修改 `main` 分支上已穩定的 schema 而不記錄 changelog
    - - 不得在未更新 Notion 狀態的情況下結束工作

    ---

    ## 🔗 相關資源

    - [Superpowers AI Skills 導覽](skills/superpowers-guide.md)
    - - [Agent 行為準則](AGENT_RULES.md)
      - - [系統地圖](SYSTEM_MAP.md)
        - - [環境變數範例](.env.example)
          - - [交接模板](handoff/HANDOFF_TEMPLATE.md)
