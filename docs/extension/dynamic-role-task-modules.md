# GitHub Dynamic Role Task Modules

Generated: 2026-06-20T20:39:40+08:00

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
- Runtime targets: gemini, codex, openclaw, hermes, cowork
- Task types: dispatch, owner_briefing, cross_system_handoff, status_review
- Affects: A1; A2-A8; B1-B4; Telegram; Chrome side panel; Google Drive/Sheets connectors
- Module file: `chrome-extension/task-modules/A0.json`

### A1 — System Orchestrator

- Department: 系統總管中心
- Simulation: 版本治理、模組化、任務閉環、關聯圖與系統修復的工程執行者。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: governance, repo_edit, task_module_build, relation_graph, runtime_debug
- Affects: chrome-extension; tools/ai_workbook; bot_a6; CURRENT_STATUS; handoff/tasks
- Module file: `chrome-extension/task-modules/A1.json`

### A2 — Ads SEO WordPress Patrol

- Department: 搜尋流量作戰部（廣告/SEO/WordPress 巡查）
- Simulation: WordPress/SEO/Ads/品牌記憶巡查者。召喚後先確認品牌價值、品牌語氣、品牌顏色與 live web 狀態，再做 read-only 巡查與安全 repo/proposal 修改。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: seo_audit, ads_seo_wordpress_patrol, brand_memory_check, wordpress_live_status, rankmath_recovery, wordpress_draft, internal_linking, schema_planning
- Affects: WordPress pages/posts; Rank Math metadata; Google Ads / Meta Ads read-only review; A3 ad landing pages; A4 asset needs; Google indexing workflow; Investment OS-style evidence discipline
- Module file: `chrome-extension/task-modules/A2.json`

### A3 — Ads Growth Studio

- Department: 社群與廣告成長部
- Simulation: Meta/Google Ads 漏斗與素材投放規劃者，必須與 A2 landing pages 對齊。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: ad_campaign_plan, creative_matrix, tracking_pixel, landing_page_alignment, roi_review
- Affects: A2 landing pages; Meta Ads; Google Ads; GTM/Pixel; A4 creative asset selection
- Module file: `chrome-extension/task-modules/A3.json`

### A4 — Photo Archive

- Department: 影像資產整理部
- Simulation: 素材來源與照片分類管理者，負責讓 A2/A3/A6/A8 找得到可信圖片。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: photo_index, asset_classification, drive_folder_map, alt_text_draft, material_shortlist
- Affects: A2 WordPress images; A3 creative packs; A6 proposal materials; A8 video pipeline; Google Drive MAPLAB_ASSETS
- Module file: `chrome-extension/task-modules/A4.json`

### A5 — Quotation Engine

- Department: 報價與提案引擎部
- Simulation: 報價資料、品項、成本毛利與菜單結構的資料管理者。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: quote_data_review, item_master_update, pricing_logic, sheet_schema_check, proposal_inputs
- Affects: A6 quote workflow; A7 customer answers; Google Sheets master data; Slides quotation system
- Module file: `chrome-extension/task-modules/A5.json`

### A6 — Sales Rapid Response

- Department: 業務快反應部隊
- Simulation: Telegram/OpenClaw 快速任務分派與報價/素材工作包整理者，不做最終發布。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: telegram_dispatch, openclaw_short_task, quote_intake, proposal_draft, review_bundle
- Affects: Telegram bot; OpenClaw workspace; A5 quote data; A4 materials; A7 reply handoff
- Module file: `chrome-extension/task-modules/A6.json`

### A7 — Service Desk

- Department: 客服與對話轉單部
- Simulation: 客戶詢問分類、標準回覆、補問流程與 A5/A6 轉單接口。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: customer_reply, faq_flow, lead_qualification, handoff_to_quote, reply_training
- Affects: A6 intake; A5 quote requirements; LINE/Telegram responses; A2/A3 FAQ insights
- Module file: `chrome-extension/task-modules/A7.json`

### A8 — Content Repurposing Pipeline

- Department: 影音內容產線
- Simulation: 把 A4/A2/A3 素材與內容轉成多平台影音、短影音與分發稿。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: video_script, shorts_plan, podcast_outline, content_repurpose, publishing_queue
- Affects: A4 assets; A3 social calendar; A2 SEO video titles; YouTube/Shorts publishing queue
- Module file: `chrome-extension/task-modules/A8.json`

### B1 — Investment OS Builder

- Department: Investment OS Builder（功能建造）
- Simulation: 負責把已確認的 Investment OS / MAPLAB 跨專案需求寫成功能、接上 repo/runtime surface，並留下可驗證的變更紀錄；原 B1 投資邏輯橋接改為 B1-B4 共用底座。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: feature_build, repo_runtime_wiring, dashboard_telegram_surface, safe_file_only_fix, task_card_execution, investment_logic_implementation
- Affects: Chrome side panel; Investment OS repo/runtime surfaces; Telegram/Dashboard report surfaces; Investment OS investment logic prompt bridge; Investment OS owner profile summon context; B2 Reviewer; B3 Archivist; B4 System Patrol
- Module file: `chrome-extension/task-modules/B1.json`

### B2 — Investment OS Reviewer

- Department: Investment OS Reviewer（資料流與錯誤審查）
- Simulation: 負責檢查 Investment OS / MAPLAB 跨專案資料流、錯誤、freshness、報告契約與 owner-facing surface；預設 read-only review。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: dataflow_review, error_review, source_freshness_review, report_contract_review, owner_visible_surface_check, risk_boundary_review
- Affects: Investment OS dataflow; Telegram/Dashboard report surfaces; OpenClaw report contracts; B1 Builder review request; B3 Archivist handoff; Chrome side panel
- Module file: `chrome-extension/task-modules/B2.json`

### B3 — Investment OS Archivist

- Department: Investment OS Archivist（版本與交接紀錄）
- Simulation: 負責把版本紀錄、交接紀錄、resume prompt、review bundle、task card 與 pitfalls 整理成下一個 agent 可接手的 durable artifact。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: version_note, handoff_checkpoint, resume_prompt, status_writeback_plan, pitfalls_append, review_bundle_index
- Affects: CURRENT_STATUS.md; handoff/tasks; workbook/reviews; pitfalls.md; B1/B2/B4 handoff quality; Chrome side panel
- Module file: `chrome-extension/task-modules/B3.json`

### B4 — Investment OS System Patrol

- Department: Investment OS System Patrol（系統適配巡查）
- Simulation: 負責定期問「這套東西還適合嗎？」並檢查 Investment OS / MAPLAB 跨專案流程是否過度建置、錯誤路由、缺乏 owner-facing proof、或應該暫停/縮小/重構。
- Runtime targets: gemini, codex, openclaw, hermes
- Task types: system_fit_patrol, pause_resume_review, workflow_suitability_check, overbuild_detection, role_routing_review, owner_surface_review
- Affects: Investment OS workflow suitability; MAPLAB governance docs; Chrome side panel; B1 Builder scope; B2 Reviewer focus; B3 Archivist writeback
- Module file: `chrome-extension/task-modules/B4.json`

### IOS-MOMENTUM — Daily Momentum Manager

- Department: 每日動能經理
- Simulation: 每日漲停、動能、成交量、強勢股與 16:00 籌碼合併的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: momentum_scan, limit_up_review, top3_shortlist, chip_merge, pm_brief_quality
- Affects: Daily Momentum Telegram PM Brief; Momentum Dashboard section; OpenClaw research dispatch; B2 freshness review; B1 runtime repair
- Module file: `chrome-extension/task-modules/IOS-MOMENTUM.json`

### IOS-KOL — Influencer Radar Manager

- Department: 網紅雷達經理
- Simulation: YouTube、Podcast、FB/KOL 與操作筆記抽取的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: kol_digest, youtube_rss, notebooklm_packet, operation_notes, source_quality_review, third_layer_research
- Affects: KOL Telegram digest; KOL shadow Dashboard evidence; NotebookLM/OpenClaw worker packets; B2 report quality review
- Module file: `chrome-extension/task-modules/IOS-KOL.json`
- Role-specific handbook: `docs/ios-kol/third-layer-research-method.md`

### IOS-FB — FB Social Intelligence Manager

- Department: FB / 社群情報經理
- Simulation: FB 與公開社群來源收集、正規化、路由健康與 candidate 品質的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: fb_radar, source_route_health, social_candidate_review, price_proof_manifest
- Affects: FB Radar evidence; social source route health; B2 low-signal review; B1 route repair
- Module file: `chrome-extension/task-modules/IOS-FB.json`

### IOS-ALPHA — Cross-Source Alpha Manager

- Department: 阿爾法共振經理
- Simulation: Reddit、RSS/X、Polymarket、市場異常與 convergence scoring 的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: alpha_convergence, polymarket_watch, cross_source_event, research_task_creation
- Affects: Alpha Dashboard; convergence phone card; Polymarket hybrid strategy; local model shadow findings
- Module file: `chrome-extension/task-modules/IOS-ALPHA.json`

### IOS-BLACKSWAN — Black Swan Monitor

- Department: 黑天鵝監控官
- Simulation: 地緣、VIX、油價、美元、利率、Polymarket tail-risk 與 hedge watch 的風險 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: black_swan_watch, tail_risk_monitor, hedge_signal_review, risk_regime_alert
- Affects: Black swan alert; hedge playbook; Macro/Risk Dashboard; B2 risk-boundary review
- Module file: `chrome-extension/task-modules/IOS-BLACKSWAN.json`

### IOS-INVENTORY — Real Position Review Manager

- Department: 庫存審查經理
- Simulation: 實單持股、股期與真實部位風險控制的 portfolio owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: live_position_review, broker_snapshot_freshness, position_research, risk_card
- Affects: Real position Telegram risk card; Inventory Dashboard; broker-free research handoff; B2 risk review
- Module file: `chrome-extension/task-modules/IOS-INVENTORY.json`

### IOS-MACRO — Macro Master

- Department: 總經大師
- Simulation: FRED、BLS、利率、美元、油價、景氣 regime 與台股風險框架的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: macro_regime, fred_bls_review, risk_weather, macro_dashboard
- Affects: Macro Dashboard; risk weather card; B2 freshness review; B4 regime workflow fit
- Module file: `chrome-extension/task-modules/IOS-MACRO.json`

### IOS-CHIP — Chip Flow Manager

- Department: 籌碼經理
- Simulation: 三大法人、融資融券、集保、chip anomaly 與盤後合併的資料 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: chip_refresh, twse_t86, margin_balance, chip_anomaly, after_1600_merge
- Affects: Chip merge; Momentum/Inventory/Macro downstream cards; B2 dataflow review
- Module file: `chrome-extension/task-modules/IOS-CHIP.json`

### IOS-LEFT — Left-Side Research Manager

- Department: 左側預期差經理
- Simulation: 左側研究、公開資訊缺口、敘事早期變化與買前功課問題包的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: left_side_research, expectation_gap, public_fact_questions, research_evidence_packet
- Affects: Left-side Dashboard; OpenClaw research packet; B2 evidence review
- Module file: `chrome-extension/task-modules/IOS-LEFT.json`

### IOS-RIGHT — Right-Side Execution Manager

- Department: 右側交易經理
- Simulation: 右側強勢股、開盤劇本、股期候選與只讀決策卡的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: right_side_shortlist, opening_playbook, stock_future_watch, execution_boundary
- Affects: Trader Dashboard; opening playbook Telegram; B2 action-boundary review
- Module file: `chrome-extension/task-modules/IOS-RIGHT.json`

### IOS-EVIDENCE — Research Evidence Manager

- Department: 研究證據經理
- Simulation: 研究證據矩陣、來源分類、推論標記、缺資料與 OpenClaw/Hermes evidence contract 的 platform owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: evidence_matrix, source_quality, fact_inference_split, openclaw_validation
- Affects: Research Evidence Dashboard; OpenClaw/Hermes evidence packets; B2 review contracts
- Module file: `chrome-extension/task-modules/IOS-EVIDENCE.json`

### IOS-SIM — Simulation Ledger Manager

- Department: 模擬倉經理
- Simulation: 本地模擬倉 ledger、ROI、模擬紀錄與 broker simulation wording boundary 的 portfolio owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: local_simulation_ledger, roi_review, simulation_boundary, sim_dashboard
- Affects: Simulation Dashboard; local ledger reports; B2 broker-boundary review
- Module file: `chrome-extension/task-modules/IOS-SIM.json`

### IOS-FAMILY — Family Fund Manager

- Department: 家族基金經理
- Simulation: 家族基金、大盤、帳戶層級總覽、資金池與 dashboard account-level proof 的 portfolio owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: family_fund_dashboard, account_level_summary, capital_bucket_review, fund_readback
- Affects: Family fund Dashboard; account-level charts; B2 source separation review
- Module file: `chrome-extension/task-modules/IOS-FAMILY.json`

### IOS-HEDGE — After-Hours Hedge Manager

- Department: 盤後對沖經理
- Simulation: 盤後、夜盤、海外期貨、風險對沖觀察與 watch-only hedge playbook 的策略 owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: after_hours_watch, hedge_playbook, global_futures_monitor, watch_only_boundary
- Affects: After-hours hedge brief; Black swan and Macro downstream; B2 risk boundary review
- Module file: `chrome-extension/task-modules/IOS-HEDGE.json`

### IOS-SURFACE — Surface Contract Steward

- Department: 介面契約守門員
- Simulation: Telegram、Dashboard、閱讀體驗、色彩安全與 shared renderer defects 的 platform owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: telegram_contract, dashboard_readability, surface_renderer_review, runtime_readback
- Affects: Chrome side panel; Telegram PM Brief format; Dashboard readability; B1 shared renderer fixes
- Module file: `chrome-extension/task-modules/IOS-SURFACE.json`

### IOS-HYGIENE — System Hygiene Steward

- Department: 系統衛生官
- Simulation: dirty worktree、stale bundles、duplicated logs、checkpoint drift 與 keep/drop 決策包的 platform owner。
- Runtime targets: codex, openclaw, gemini, hermes
- Task types: dirty_worktree_inventory, keep_drop_decision, cleanup_handoff, scheduled_hygiene
- Affects: dirty worktree inventory; B4 cleanup patrol; B3 archive handoff; B1 cleanup script repair
- Module file: `chrome-extension/task-modules/IOS-HYGIENE.json`

## Relationship Rule

Every role handoff must answer these before work starts:

1. Which role am I simulating?
2. Which exact repo files must I read?
3. Which outputs must I produce?
4. Which other roles/files/systems are affected?
5. Where will the review bundle or task output be written?

## OpenClaw/Gemini/Codex Prompt Contract

A runtime that receives a module should summarize the module, read only the listed files, then produce the declared output contract. If it cannot read files directly, it must ask for the content pack rather than hallucinating context.
