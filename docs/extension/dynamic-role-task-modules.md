# GitHub Dynamic Role Task Modules

Generated: 2026-05-21T18:57:57+08:00

## Purpose

This module set turns the Chrome side panel from a Claude-tab injector into a platform-neutral role handoff surface.
GitHub stores JSON/Markdown task data. Chrome/Gemini/Codex/OpenClaw consume the same module contracts.

## Non-negotiable design rule

- GitHub dynamic links load data/config only.
- Do not execute remote JavaScript in Chrome. Chrome MV3 CSP already broke that path in extension v4.0/v4.2.
- Claude tab injection remains optional legacy behavior, not the main runtime.

## Outputs

- `chrome-extension/task-modules/index.json` — public module index for the side panel.
- `chrome-extension/task-modules/{role}.json` — one portable role module per agent.
- `chrome-extension/config/task-modules.json` — extension config pointer.
- `workbook/task_modules/role_module_relation_graph.json` — directed impact graph.
- `workbook/task_modules/role_module_relationships.csv` and `.xlsx` — Excel-readable relationship table.

## Markdown Refresh Model

- Role JSON files are routing envelopes, not frozen copies of the source documents.
- The Chrome side panel hands Gemini/Codex/OpenClaw GitHub raw links so the runtime reads the latest Markdown/JSON content.
- Each source entry includes `source_sha256`; the side panel can compare it with current GitHub raw content and warn when a Markdown file changed after module generation.
- If hashes differ, run `python3 tools/ai_workbook/build_extension_task_modules.py`, commit, push, then reload the side panel.

## Role Modules

### A0 — Dispatch Secretary

- Department: 總調度秘書
- Simulation: 跨系統任務調度與 Owner 入口管理者，不直接取代各專業角色。
- Runtime targets: gemini, codex, openclaw, cowork
- Task types: dispatch, owner_briefing, cross_system_handoff, status_review
- Affects: A1; A2-A8; B1; Telegram; Chrome side panel; Google Drive/Sheets connectors
- Module file: `chrome-extension/task-modules/A0.json`

### A1 — System Orchestrator

- Department: 系統總管中心
- Simulation: 版本治理、模組化、任務閉環、關聯圖與系統修復的工程執行者。
- Runtime targets: codex, openclaw, gemini
- Task types: governance, repo_edit, task_module_build, relation_graph, runtime_debug
- Affects: chrome-extension; tools/ai_workbook; bot_a6; CURRENT_STATUS; handoff/tasks
- Module file: `chrome-extension/task-modules/A1.json`

### A2 — SEO Growth Unit

- Department: 搜尋流量作戰部
- Simulation: WordPress/Rank Math/GSC/內容架構 SEO 大師，先查 live facts 再做內容決策。
- Runtime targets: gemini, codex, openclaw
- Task types: seo_audit, rankmath_recovery, wordpress_draft, internal_linking, schema_planning
- Affects: WordPress pages/posts; Rank Math metadata; A3 ad landing pages; A4 asset needs; Google indexing workflow
- Module file: `chrome-extension/task-modules/A2.json`

### A3 — Ads Growth Studio

- Department: 社群與廣告成長部
- Simulation: Meta/Google Ads 漏斗與素材投放規劃者，必須與 A2 landing pages 對齊。
- Runtime targets: gemini, codex, openclaw
- Task types: ad_campaign_plan, creative_matrix, tracking_pixel, landing_page_alignment, roi_review
- Affects: A2 landing pages; Meta Ads; Google Ads; GTM/Pixel; A4 creative asset selection
- Module file: `chrome-extension/task-modules/A3.json`

### A4 — Photo Archive

- Department: 影像資產整理部
- Simulation: 素材來源與照片分類管理者，負責讓 A2/A3/A6/A8 找得到可信圖片。
- Runtime targets: gemini, codex, openclaw
- Task types: photo_index, asset_classification, drive_folder_map, alt_text_draft, material_shortlist
- Affects: A2 WordPress images; A3 creative packs; A6 proposal materials; A8 video pipeline; Google Drive MAPLAB_ASSETS
- Module file: `chrome-extension/task-modules/A4.json`

### A5 — Quotation Engine

- Department: 報價與提案引擎部
- Simulation: 報價資料、品項、成本毛利與菜單結構的資料管理者。
- Runtime targets: gemini, codex, openclaw
- Task types: quote_data_review, item_master_update, pricing_logic, sheet_schema_check, proposal_inputs
- Affects: A6 quote workflow; A7 customer answers; Google Sheets master data; Slides quotation system
- Module file: `chrome-extension/task-modules/A5.json`

### A6 — Sales Rapid Response

- Department: 業務快反應部隊
- Simulation: Telegram/OpenClaw 快速任務分派與報價/素材工作包整理者，不做最終發布。
- Runtime targets: gemini, codex, openclaw
- Task types: telegram_dispatch, openclaw_short_task, quote_intake, proposal_draft, review_bundle
- Affects: Telegram bot; OpenClaw workspace; A5 quote data; A4 materials; A7 reply handoff
- Module file: `chrome-extension/task-modules/A6.json`

### A7 — Service Desk

- Department: 客服與對話轉單部
- Simulation: 客戶詢問分類、標準回覆、補問流程與 A5/A6 轉單接口。
- Runtime targets: gemini, codex, openclaw
- Task types: customer_reply, faq_flow, lead_qualification, handoff_to_quote, reply_training
- Affects: A6 intake; A5 quote requirements; LINE/Telegram responses; A2/A3 FAQ insights
- Module file: `chrome-extension/task-modules/A7.json`

### A8 — Content Repurposing Pipeline

- Department: 影音內容產線
- Simulation: 把 A4/A2/A3 素材與內容轉成多平台影音、短影音與分發稿。
- Runtime targets: gemini, codex, openclaw
- Task types: video_script, shorts_plan, podcast_outline, content_repurpose, publishing_queue
- Affects: A4 assets; A3 social calendar; A2 SEO video titles; YouTube/Shorts publishing queue
- Module file: `chrome-extension/task-modules/A8.json`

### B1 — Investment OS Logic Bridge Advisor

- Department: 投資邏輯橋接顧問（InnerFlowLab 內容暫停）
- Simulation: 可被 Owner/A1 從 Chrome Extension 召喚，把 Investment OS 的 Owner 投資語言、左右側判斷、公司研究、加減碼、風控與盲點交給其他 agent；原 InnerFlowLab 內容專案暫停。
- Runtime targets: gemini, codex, openclaw
- Task types: owner_investment_profile, investment_logic_bridge, right_side_research_review, risk_prompt_coaching, agent_summon_bridge, cross_project_review, governance_gap_audit, prompt_design, report_contract_review, pause_resume_handoff
- Affects: Chrome side panel; MAPLAB governance docs; Investment OS governance recommendations; Investment OS investment logic prompt bridge; Investment OS owner profile summon context; OpenClaw/Telegram report surfaces; B1 content project paused
- Module file: `chrome-extension/task-modules/B1.json`

## Relationship Rule

Every role handoff must answer these before work starts:

1. Which role am I simulating?
2. Which exact repo files must I read?
3. Which outputs must I produce?
4. Which other roles/files/systems are affected?
5. Where will the review bundle or task output be written?

## OpenClaw/Gemini/Codex Prompt Contract

A runtime that receives a module should summarize the module, read only the listed files, then produce the declared output contract. If it cannot read files directly, it must ask for the content pack rather than hallucinating context.
