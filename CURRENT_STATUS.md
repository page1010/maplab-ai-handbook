# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新：2026-06-11 00:44（checkpoint.sh 自動同步）｜完整歷史存於 `archive/CURRENT_STATUS_2026-04-11_full.md`

---

## 系統版本

- **Version**: v6.0
- **Phase**: Phase 6 — 觀測性 + 業務閉環 + 策略循環
- **Status**: Active
- **v6.0 設計文件**: `projects/v6-architecture.md`
- **Sheets Dashboard**: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` → Task Board + Owner Actions 分頁

---

## 最新事實核對

- 2026-06-09：A2/A3/A4 approval-ready automation 規則落地（implementation commit `4988747`）。新增 `projects/a2a3a4-approval-ready-automation.md`，並更新 `AGENT_RULES.md`、`projects/a2-ads-seo-wordpress-patrol.md`、`handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`、`recalls/A2_recall.md`、`recalls/A3_recall.md`、`recalls/A4_recall.md`。Owner 校正：正式 WordPress / Google Ads / Meta Ads / Rank Math / GTM / Pixel / 預算 / 開關等第二層變更不是不能自動跑，而是要自動整理成 approval-ready plan，說清楚為什麼要改、改什麼、預期效果、影響範圍、風險、rollback、驗收方式與 Owner 可選項；Owner/A1 精確批准後才可進 execution mode。
- 2026-06-01：B1 Builder 依 MAPLAB B1 runtime handoff 修復 Investment OS Dashboard stale-data closed loop。Investment OS root cause：runtime dashboard copy 舊、launcher 只看 health OK 不替換舊 Streamlit、file watcher disabled、台股 LaunchAgent weekday 寫成 Tue-Sat、18502/8501 tmux-only 不耐久、Dashboard 優先讀舊 command_status。已修 `launch_dashboard.sh`、台股市場 LaunchAgents Mon-Fri、新增 launchd-backed `dashboard-mobile`/`dashboard-local`、更新 Dashboard command-board source priority、補跑 Investment OS runtime jobs 與 no-send browser-backed GPT refresh。驗證：Investment OS `18501/18502/8501` first screen 均顯示 `行情日 2026-06-01`、`AI研究日 2026-06-01`、`Agent板 06/01` 且 stale top-strip dates=0；pytest `23 passed`。MAPLAB B1 bundle：`workbook/reviews/JOB-B1-BUILDER-20260601/`。未讀 secrets、未碰 broker orders、未發 Telegram、未發布 WordPress/Ads/Rank Math。
- 2026-05-11：正式 repo = `/Users/pagemacmini/maplab-ai-handbook`；`/Users/pagemacmini/Downloads/maplab-ai-handbook-main` 為非 git 下載副本，只能作遷移/歷史參考，不得作為正式工作目錄。
- 2026-05-29：跨專案 Agent 召喚工作場景流程圖完成：MAPLAB 版 `docs/cross-project-agent-summon-workflow-map.md`，Investment OS 對應版 `/Users/pagemacmini/Documents/New project/docs/AGENT_SUMMON_WORKFLOW_MAP.md`。內容定義 Chrome Extension / Agent Office / Telegram / Codex 入口，GPT、Codex、Claude Code、Claude Chrome tab、Gemini、NotebookLM、Antigravity、Hermes、OpenClaw、local model、Windows agent 的使用場景與 why，並規劃 Windows 收盤後資訊商資料包送 Mac mini 地端模型/Hermes/B2/Codex 研究排程。未讀 secrets、未碰券商/下單/模擬單、未發布。
- 2026-05-29：Chrome Extension 升級為 v5.6.0 並已在 Chrome live profile 啟用：新增 `召喚任務` 欄位與 `自動選角`，Owner 可先輸入任務，再由 Extension 建議 A2 / B1 / B2 / B3 / B4；handoff prompt 會帶入 `本次召喚任務`。task module 讀取改為本機 extension packaged JSON 優先、GitHub raw fallback；role recall 也有 packaged fallback。已將 `/Users/pagemacmini/Desktop/chrome-extension` 改為指向 canonical repo `/Users/pagemacmini/maplab-ai-handbook/chrome-extension` 的 symlink，舊 Desktop v4.7.0 folder 備份為 `chrome-extension.stale-v4.7-20260529-212125`；Chrome Extensions 頁仍保留舊 v4.7.0 entry 但已關閉。live 驗證需以 Chrome Extensions 頁與 popup 實際畫面為準；舊 Secure Preferences path 或 repo commit 不可單獨當作已啟用證據。
- 2026-06-05：Chrome Extension 升級為 v5.6.1 並已在 Owner Chrome installed copy live readback：`交接目標` 從 4 個粗分類擴充為 Claude Code、Codex、GPT/ChatGPT、Claude Chrome tab、Antigravity、Gemini、OpenClaw、Hermes、Gemini Chrome tab。handoff prompt 新增 `runtime_target_label` 與各目標邊界說明，避免 repo runtime、browser chat、operator worker、cold-path worker 混用。驗證：`node --check chrome-extension/popup.js` pass；`python3 -m json.tool chrome-extension/manifest.json` pass；live DevTools target `chrome-extension://ifpmihhbfhpbcippnhdnjdecbgkmbgmf/popup.html` 回 `manifestVersion=5.6.1`、option count `9`、`IOS-KOL -> GPT / ChatGPT handoff` prompt 含 `runtime_target: gpt` 與 `runtime_target_label: GPT / ChatGPT`。證據：`workbook/reviews/JOB-A1-EXT-HANDOFF-TARGETS-20260605/validation_report.md`。
- 2026-05-29：Investment OS B-role family 建立中：原 B1 投資邏輯橋接拆為 B1 Builder（寫功能）、B2 Reviewer（資料流/錯誤/freshness review）、B3 Archivist（版本與交接紀錄）、B4 System Patrol（系統適配巡查）。原 B1 Investment OS Owner logic 轉為 B1-B4 共用底座；InnerFlowLab 內容發文仍暫停；B1-B4 不下單、不建模擬單、不給買賣建議。
- 2026-05-29：A2 新增 Ads/SEO/WordPress Patrol 召喚契約與每週定時巡查 automation：`a2-ads-seo-wordpress-patrol` ACTIVE，RRULE `FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0;BYSECOND=0`，cwd `/Users/pagemacmini/maplab-ai-handbook`。召喚後需先確認品牌價值、品牌語氣、品牌顏色/視覺來源、live web 狀態與 MAPLAB + Investment OS 共用文化（證據分層、風險邊界、交接紀律）。A2 可做 read-only 巡查與 safe repo/proposal 修改；WordPress 發布、Google/Meta Ads 設定、Rank Math 付費設定仍需 Owner/A1 批准。
- 2026-05-27：A2 已用 Owner Chrome 登入態把 Round 008 案例內容實際存入 WordPress 未發布草稿：Post ID `1696`，edit URL `https://www.maplabkitchen.com/wp-admin/post.php?post=1696&action=edit`，title `MAPLAB 企業外燴與活動茶點案例審核草稿 Round 008`，狀態 `草稿`。A2 已重載 edit URL 驗證內容持久化，包含 21 則案例段與圖片 slot/檔名/Alt/Caption；未發布、未改 Rank Math、未改 Google Ads / Meta Ads。Round 009 report：`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/wp_draft_round_009.md`。圖片實體尚未插入，因 Chrome extension file chooser 回 `Not allowed`；30 張 WebP 預期 uploads URL 仍為 404，下一步需 Owner 開啟 Codex Chrome extension 的 file URL access 後再補圖。
- 2026-05-26：A2 Round 008 已完成 Owner 審稿包：`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/wordpress_case_insert_draft_round_008.md`（21 則 existing live post 案例插入草稿）、`ads_landing_settings_round_008.md`（Google Ads P1 拆組與 Meta landing-page traffic proposal）、`asset_conversion_manifest_round_008.md` / `asset_conversion_status_round_008.csv` / `wordpress_assets_round_008/`（30/30 照片轉 WebP 本機審稿素材）。A2 acceptance review：`reports/a2_round_008_review.md`。未發布 WordPress、未改 Ads、未碰 Rank Math；下一步只等 Owner review 哪些案例段、外部名稱與圖片 slot 可用。
- 2026-05-11：Drive API 確認 `MAPLAB_ASSETS` active folder = `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy`，parent = `MAPLAB`；舊 ID `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` API 回 404。
- 2026-05-11：Sheets API 確認 `MAPLAB_ASSET_LOG` = `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`，tab `工作表1`，rowCount `36923`。
- 2026-05-26：A2 已用 CUA driver / Computer Use 只讀進 Meta detail pane 建 Round 006 visual bridge：`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_owner_chrome_detail_visual_bridge_round_006.md`，Antigravity-style review 已產 `reports/antigravity_detail_visual_bridge_round_006.md`，A2 acceptance review 已產 `reports/a2_round_006_review.md`。`互動廣告組合 A 企業窗口` 已確認為 Meta 互動/粉專按讚目標，不是 WordPress landing-page traffic；受眾為台南 +40km、30-60、所有性別，含半導體/工程/金融與商業決策者相關條件，預估 812,200-955,500。`互動廣告組合 B 公關公司窗口` 仍是 running B2B seed，但 detail pane 未成功打開，保持 `Needs UI Detail`。Round 007 已產 `meta_landing_page_proposal_round_007.md` 並由 A2 驗收 `reports/a2_round_007_review.md`：建議保留現役互動廣告不動，另提獨立 Meta→WordPress To B live URLs 的 landing-page traffic path。A2 未發布、未儲存、未改 toggle。
- 2026-05-26：A2 已用 Computer Use 只讀切到 Meta `廣告組合` / `廣告` 層並建立 Round 005 visual bridge：`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_owner_chrome_adsets_ads_visual_bridge_round_005.md`。目前可確認兩個現役 To B ad set seed：`互動廣告組合 B 公關公司窗口`、`互動廣告組合 A 企業窗口`；`中華賓士 ESG` 與 `新的開發潛在顧客` 為 closed B2B/lead-gen seed。尚未驗證詳細受眾、Advantage+、pixel/custom audience、destination URL；下一步交 `ANTIGRAVITY_ADSETS_ADS_VISUAL_BRIDGE_PROMPT.md` 檢查，再只讀開 detail pane。
- 2026-05-26：A2 已修正 Meta Ads 視窗來源：先前 `reports/meta_ads_chrome_round_002_account_recheck.md` 讀到 agent Facebook / Chrome 視窗，已標記 superseded。有效來源改為 Owner Chrome visual bridge：`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_owner_chrome_visual_bridge_round_004.md` + `visual_evidence_round_004/meta_ads_owner_chrome_campaigns_round_004_cropped.png`。正確 Meta account 為 `318634712 (318634712)`、business/global scope `215690449213844`，可見 13 個 campaign rows；Antigravity 下一輪改讀 `ANTIGRAVITY_VISUAL_BRIDGE_META_PROMPT.md`，不得再要求 API token/password，也不得發布、儲存、改設定、接受政策或切 toggle。
- 2026-05-26：A2 已把 B2B case + ads routing 轉成執行迴圈：`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/execution_loop.md`，每小時巡檢 automation `a2-b2b-case-ads-loop-check` 已啟用。Antigravity 已用 `Gemini 3.1 Pro (High)` 產 `reports/antigravity_round_001.md`，確認 7 個 public live URLs 皆 200，但因無登入 cookie 無法進 WP/Google/Meta 後台；A2 已用 Chrome 登入狀態補 `reports/google_ads_chrome_round_001.md`（13 筆 keyword 同在 `Campaign 4：高意圖搜尋_南台灣外燴 / 廣告群組 1`，keyword final URL 欄皆顯示 `—`）與 `reports/meta_ads_chrome_round_001.md`（Meta Ads Manager 導到 onboarding，A2 未點啟用）。A3/A4/A2 Round 001 回報與 `asset_conversion_manifest_round_001.csv` 已落檔；下一步只做 Google Ads proposal / WordPress update plan，不改設定。
- 2026-05-26：A2 Owner 批次照片已進 To B case + ads routing。產出 `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/review_request.md`：30 個照片檔已對應到 7 個 live To B landing pages、Google Ads keyword/final URL matrix、Meta 興趣分眾、WebP/裁切/alt/caption/slot 規格與 Antigravity 只讀 access-check prompt。同步產出 `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/access_check.md`：A2 已只讀確認 WordPress `post=586` 編輯頁可進入，Google Ads account `844-336-3178` 的 `搜尋關鍵字` 頁可進入。2026-05-26 前台再驗證 7 個 live URLs 皆為 200；5 個舊 planned slugs 皆為 404。Rank Math 既有設定繼續凍結。
- 2026-05-24：A2 live WordPress / To B 盤點完成 — public REST 仍為 6 pages / 57 posts；但 B2B 主要入口目前是 published posts，不是 pages。category `企業外燴案例` 有 15 篇；live To B URLs 以 `corporate-catering-tainan`、`corporate-tea-party-desserts`、`tainan-corporate-opening-tea-catering`、`brand-esg-catering-service`、`press-conference-catering`、`vip-expo-catering-business-meeting` 為準。planned slugs `catering-corporate-tainan`、`meeting-refreshment-catering-tainan`、`opening-event-catering-tainan`、`brand-event-catering`、`school-event-catering-tainan` 目前前台 404，不可當發文目標。Rank Math 已退訂，既有設定先保留，不再做 RM 設定工作；下一步是 Owner 提供照片與場次後，A2 依 live URL 補 To B 真案例。
- 2026-05-11：WordPress public REST 現況仍為 6 pages / 57 posts；A2/A3 local workbench planned slugs 不可直接視為 live URLs。
- 2026-05-19：A6 Case Store v0 接線 — LINE inbound 仍以 Sheet `CONVERSATION_LOG` 為原始證據；新增 `bot_a6/case_store.py` 只讀 Sheet、寫本機 SQLite 案件索引，A6 Telegram 新增 `/linecases`、`/case`、`/casequote`，路徑圖補回 `projects/line-quote-assistant.md`。
- 2026-05-19：A6 Telegram route guard 修正 — `/start` 預設為一般聊天，`/status` / `/model` 與「你現在是跑什麼模型」直接由 A6 回 runtime/model 狀態；只有明確「報價 ...」、`/localquote ...` 或可判定為外燴報價需求時才進 A5，避免普通對話被 A5 fallback 吞掉。
- 2026-05-19：A6 一般聊天/SEO 改為 Codex-first — Telegram 普通對話先用本機 `codex exec --ephemeral --sandbox read-only` 呼叫 Codex 雲端對話層；Codex CLI 不可用、額度/網路失敗或逾時時才透明切到本機 Ollama。A5 報價仍沿用明確報價路由，不動 Sheet/GAS/公式。
- 2026-05-20：A6 quote intent 擴充 — 會議/Workshop 茶點、coffee break、午餐、自助 bar、TTL/總額數字、日期時間組合會被判定為報價需求並進 A5；修正「5/21 成大 workshop，茶點+午餐 TTL 25000」這類無「報價」字樣但明確外燴需求被一般聊天接走的問題。
- 2026-05-19：B1 已由 InnerFlowLab 內容發文角色改為「暫停中的跨專案治理顧問」；Chrome Extension B1 module 將指向 `projects/b1-cross-project-governance-advisor.md`，review bundle 在 `workbook/reviews/JOB-B1-CROSS-PROJECT-20260519/`。原 Substack / innerflowlab.com / 多平台發文自動化暫停，不得未經 Owner/A1 恢復就執行。
- 2026-05-19：B1 補上 Investment OS 判斷邏輯橋接：`projects/b1-investment-logic-bridge.md` 與 `workbook/reviews/JOB-B1-CROSS-PROJECT-20260519/b1_investment_logic_summon.md`，讓 Owner 可召喚 B1 到其他 agent 時先帶入左側/右側/風控/籌碼/新聞語言；B1 仍不下單、不建模擬單、不給買賣建議。
- 2026-05-11：GitHub sync audit 啟動 — 以 `origin/main` 為備份基準，將 durable docs/scripts/task cards/review index 補齊入庫；`.env`、logs、runtime history、raw A6 review bundles 暫不盲目 commit，先建立 sanitized/index 流程。
- 2026-05-30：B4 Investment OS System Patrol 完成巡查，review bundle `workbook/reviews/JOB-B4-PATROL-20260530/` 已落檔。結論：核心 owner-facing surfaces（`CURRENT_STATUS.md` / task cards、Chrome Extension 召喚、Agent Office switchboard、Telegram + Mobile Dashboard、B1-B4 role split）繼續；OpenClaw / Hermes 只保留 bounded read-only 路徑；research_method_layer 與其他實驗性擴張維持 draft-only / pause；legacy broker-simulation / InnerFlowLab content path 保持 archive / paused；cloud mirrors / share page / export 必須從 GitHub HEAD 派生，不得當 truth source。
- 2026-06-03：WIN Windows Evidence Collector 角色建立（Investment OS Windows 採集端）：`recalls/WIN_recall.md` + `chrome-extension/popup.html` WIN option + `chrome-extension/task-modules/WIN.json`。WIN 運行於 Windows computer，負責採集 UI / 三竹 / 新聞 / 市場資訊，壓成 packet 放 My Drive\Investment OS\windows_agent_bridge\outbox，等 Mac 端（B2）交叉驗證。不做決策、不下單、不碰 broker order state。repo: page1010/investment-os branch investment-os-v0.1-integrated。

---

## 當前進行中任務

| Task ID | 任務 | 負責 Agent | 狀態 | Task Card |
|---------|------|-----------|------|-----------|
| T-A1-EXT-001-dynamic-role-modules | T-A1-EXT-001 — GitHub Dynamic Role Task Modules | A1 |  | handoff/tasks/T-A1-EXT-001-dynamic-role-modules.md |
| T-A1-RTK-001 | RTK Token Proxy 掛載與選擇性上線 | A1 | 🟢 已上線（Codex hook 已掛、裝前/裝後 patrol diff 驗收通過、git 排除生效） | handoff/tasks/T-A1-RTK-001.md |
| T-A1-SYNC-GUARD-001 | 雲端同步破口修補 + patrol 紀錄瘦身 | A1 | 🔲 待開始（高槓桿、低成本，建議優先） | handoff/tasks/T-A1-SYNC-GUARD-001.md |
| T-A1-V6-P2 | T-A1-V6-P2 | A1 | 🔴 CRITICAL（~1271h無commit） | handoff/tasks/T-A1-V6-P2.md |
| T-A1-V6-P3 | T-A1-V6-P3 | A1 | 🔲 待開始（尚未開始。等 T-A1-V6-P2 完成後啟動。） | handoff/tasks/T-A1-V6-P3.md |
| T-A1-V7 | 系統進化 — 單一真相源 + 自動同步 + 瘦身 + 自動技能生成 + 自動壓縮 | A1 | 🔴 CRITICAL（~1271h無commit） | handoff/tasks/T-A1-V7.md |
| T-A2-002-foodsafety-seo-cleanup | T-A2-002 — 食安 + 法規 SEO 字眼清理 | A2 | ⏸️ 阻塞（Repo 端已清理完成；WordPress 端需 Owner 手動刪除/修改 5 篇文章的食安字眼） | handoff/tasks/T-A2-002-foodsafety-seo-cleanup.md |
| T-A2-003-weekly-wp-audit | T-A2-003: 每週全站 WP 內容稽核排程 | A2 | 🔲 待開始（腳本已建好（wp-audit.sh / wp-audit-cron.sh）。待 Owner 用 /schedule 建立） | handoff/tasks/T-A2-003-weekly-wp-audit.md |
| T-A2-004 | 首頁結構優化 — 配合品牌色票微調 + 轉換路徑整理 | A2 | 🔲 待開始（任務卡建立。A0 已完成對標分析和色票微調。） | handoff/tasks/T-A2-004.md |
| T-A2-005-local-seo-factory | T-A2-005：MAPLAB SEO Factory（地端閉環，Pillar First） | A2 | 🔴 CRITICAL（~911h無commit） | handoff/tasks/T-A2-005-local-seo-factory.md |
| T-A2-006-ads-seo-wordpress-patrol | T-A2-006 — Ads / SEO / WordPress Patrol | A2 |  | handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md |
| T-A2A3-001-B | SEO 場景頁面 + 內連結（從 T-A2A3-001 分拆） | A2/A3 | 🔴 CRITICAL（~359h無commit） | handoff/tasks/T-A2A3-001-B.md |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2/A3 | ⏸️ RM/GSC 部分暫停；案例寫作轉 T-A2A3-001-B（Rank Math 已退訂，已設定好的 SEO 欄位先不要再設定；下一步是依 live URL map 補 To B 真） | handoff/tasks/T-A2A3-001.md |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 + 優化 | A3 | ⏸️ 阻塞中（受眾輪廓分析完成（693筆 Orders）。待執行：嘉義加入廣告地區、興趣條件精簡、策略一冷受眾上線。） | handoff/tasks/T-A3-002.md |
| T-A4-001 | Phase 4 Gemini 照片分類（2022-2026） | A4 | 🔴 CRITICAL（~1295h無commit） | handoff/tasks/T-A4-001.md |
| T-A4-002 | pagewu1010 帳號 Takeout 解壓 + Gemini Flash 照片資產整合 | A4 |  | handoff/tasks/T-A4-002.md |
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔴 CRITICAL（~551h無commit） | handoff/tasks/T-A5-002.md |
| T-A5-004 | createSlides.gs — Slide 報價簡報自動生成 | A5 | 🔴 CRITICAL（~1511h無commit） | handoff/tasks/T-A5-004.md |
| T-A5-005 | 報價狀態追蹤同步 + Dashboard | A5 | 🔴 CRITICAL（~1535h無commit） | handoff/tasks/T-A5-005.md |
| T-A5-006 | T-A5-006 | A5 | 🔲 待開始（尚未開始。等 T-A5-005 完成後啟動。） | handoff/tasks/T-A5-006.md |
| T-A6-001 | A6 LINE 業務報價助手系統 | A6 | 🔴 CRITICAL（~551h無commit） | handoff/tasks/T-A6-001.md |
| T-A6-002 | LINE 對話訓練資料收集計畫 | A6 | 💤 暫停（原計畫拆 Sheet 做訓練資料，04-07 重新規劃方向。等 Owner 決定是否需要 LINE 訓練資料及取得方式。） | handoff/tasks/T-A6-002.md |
| T-A7-001 | FAQ 回覆模板庫 + 補問流程 + 客戶分類標籤 | A7 | 💤 暫停（Phase 2 v2.0 完成，等 Owner 確認政策 + A5 欄位補齊）（Q1-Q10 重構完成（真實 CSV 驅動），下一步是 Q7/Q10 政策確認 + Phase 3 上線測試） | handoff/tasks/T-A7-001.md |
| T-A7-002 | A7 部門 80/20 優先任務清單 | A7 | ⏸️ 阻塞中（任務 6（Q1-Q10 實裝）+ 任務 10（技能書 v2.0）已完成。Phase 3A 剩任務 4（地區判斷）、7（流） | handoff/tasks/T-A7-002.md |
| T-B1-001 | B1 Cross-Project Governance Advisor Prompt + Project Pause |  | 🟢 召喚型可用（Investment OS 投資邏輯橋接 ready；InnerFlowLab 內容發文專案暫停） | handoff/tasks/T-B1-001.md |
| T-B1-B4-investment-os-role-split | T-B1-B4-001 — Investment OS B1-B4 Role Split + Chrome Extension Summon |  | 🔄 進行中 | handoff/tasks/T-B1-B4-investment-os-role-split.md |
| T-B1-DASH-001 | Guild Ops Board 自動同步 + 即時狀態燈 |  | 🟢 READY（已派工，等執行 + 進度檢查） | handoff/tasks/T-B1-DASH-001.md |
| T-GBP-001 | T-GBP-001 | Owner | 🔲 待開始（尚未開始。等 Owner 準備新圖片。） | handoff/tasks/T-GBP-001.md |
---

## Blockers（只列未解決的）

| 對象 | 問題 | 行動 |
|------|------|------|
| A1 | T-A1-V6-P2: 等 A6 實際報價測試 | 見 Task Card |
| A1 | T-A1-V6-P3: 前置 T-A1-V6-P2 需先完成 | 見 Task Card |
| A2 | T-A2-002-foodsafety-seo-cleanup: 等 Owner 操作 WordPress 後台 | 見 Task Card |
| A2 | T-A2-003-weekly-wp-audit: 等 Owner 建立排程 | 見 Task Card |
| A2 | T-A2-005-local-seo-factory: WordPress 寫入憑證與測試站檢核流程待 Owner 確認 | 見 Task Card |
| A2/A3 | T-A2A3-001-B: WordPress 圖片實體插入未完成，因 Chrome extension file chooser 回 `Not allowed`；需 Owner 開啟 Codex Chrome extension 的 file URL access 後再重試。WordPress 發布、Google Ads / Meta Ads 設定變更仍需 Owner approval。舊 planned slugs 不能當 live URL。 | 見 Task Card |
| A2/A3 | T-A2A3-001: RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL | 見 Task Card |
| A3 | T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） | 見 Task Card |
| A5 | T-A5-002: 等 Owner 確認（品項名稱改法、重複品項、I 欄用途） | 見 Task Card |
| A5 | T-A5-006: 前置 T-A5-005 需先完成 | 見 Task Card |
| A6 | T-A6-001: LINE webhook 已可看到 inbound 同步，但它只含客戶→OA 訊息；若要完整雙向訓練資料，需 LINE OA Manager CSV 匯出或其他正式來源。 | 見 Task Card |
| A6 | T-A6-002: 等 Owner 決定方向 | 見 Task Card |
| A7 | T-A7-001: Q7 試吃政策需 Owner 決定、Q10 取消/改期政策需 Owner 決定、A5 外送費級距未建立 | 見 Task Card |
| A7 | T-A7-002: 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限 | 見 Task Card |
| Owner | T-GBP-001: 等 Owner 準備新圖片 | 見 Task Card |
---

## Source of Truth（有效文件清單）

> Agent 只需讀以下文件。其他文件僅供參考，不作為執行依據。

| 用途 | 檔案 | 說明 |
|------|------|------|
| 🎯 最新狀態（你在這裡） | CURRENT_STATUS.md | 唯一入口，最高優先 |
| 📋 任務池 | TASK_QUEUE.md | 所有待辦任務清單 |
| 📖 角色與規則 | AGENT_RULES.md v4.0 | 13 角色定義（A0-A8 + B1-B4）+ 協作規則 + 存檔規則 |
| 🚀 開工 SOP | AGENT_STARTUP_PROTOCOL.md | 啟動流程 + Startup Check 輸出格式 |
| 📂 任務卡 | handoff/tasks/T-xxx.md | 你認領的任務的詳細狀態 |
| 🔧 技能路由 | skills/superpowers-guide.md | 開工前查路由表（27 本技能書）|
| 🎯 角色召喚 | AGENT_RECALL_PROMPTS.md | 各角色專屬 prompt + 斷點 + 可用工具 |
| 🗣️ 品牌語氣 | skills/brand-voice-guide.md | 對外文字必讀：禁用語、平台微調、受眾語氣 |

---

## 可用 MCP 工具（2026-03-26 接通）

> Agent 可直接使用以下工具讀寫外部服務，不需要開網頁手動操作。

| 工具 | 用途 | 給哪些角色 |
|------|------|----------|
| NotebookLM | 文章→podcast 音檔（Audio Overview）| A8 |
| Gemini Flash | 照片分類/alt text/Shorts 腳本 | A4, A8 |
| Google Vids | 腳本+圖片→影片組裝 | A8 |
| YouTube Studio | 影片上傳/排程/SEO | A8 |
| Google Sheets | 讀寫試算表（品項/報價/追蹤表）| A5, A2, A3, 全員 |
| Google Drive | 檔案存取/上傳/管理 | A4, A6, 全員 |
| Google Analytics | 流量數據/報表 | A2, A3 |
| Google Search Console | 搜尋排名/關鍵字 | A2 |
| Google Ads | 廣告數據（唯讀）| A3 |
| Meta Ads | Facebook/IG 廣告數據+管理 | A3 |

OAuth token：`~/.claude/mcp-keys/google-token.json`（drive + spreadsheets scope）

---

## 知識地圖（資料在哪裡）

> 找不到資料？查這張表。

| 類別 | 路徑 | 內容 |
|------|------|------|
| 客戶/活動資料 | data/timetree_events_2022_2026.json | 746 筆外燴事件（含客戶名、日期、活動類型）|
| 品項資料 | data/item-master-cross-reference.md | 108 品項對照表（APP/DST/MAIN/BEV）|
| 品項頻率 | data/item-frequency-top50.md | 399 筆歷史訂單品項分析 |
| 品項去重 v2 | data/quote_items_deduped.json | 3,794 唯一品項 |
| 報價系統 | projects/maplab-master-data.md | A5 報價邏輯 + Sheets 結構 |
| SEO/廣告 | projects/seo-ads-agent.md | A2/A3 核心文件 + 轉換動作快照 |
| A2 Ads/SEO/WP Patrol | projects/a2-ads-seo-wordpress-patrol.md | A2 召喚後品牌記憶確認、廣告/SEO/WordPress 巡查契約、高風險邊界 |
| 照片管線 | projects/maplab-pipeline.md | A4 照片分類流程 + Gemini API |
| 客服系統 | projects/ai-reply-system.md | A7 回覆系統架構 |
| 廣告監控 | projects/maplab-ads-monitor.md | A3 ads_agent.py 技術文件 |
| 報價簡報 | projects/slides-quotation-system.md | A6 Google Slides 報價 |
| 網站優化 | projects/maplab-kitchen-web-optimization.md | WordPress 技術 |
| LINE 報價助手 | projects/line-quote-assistant.md | A6/A7 系統架構、三層資料模型 |
| B1 跨專案治理顧問 | projects/b1-cross-project-governance-advisor.md | B1 暫停狀態、跨專案治理 prompt、Investment OS 對照建議 |
| B1 投資邏輯橋接 | projects/b1-investment-logic-bridge.md | Owner 的 Investment OS 左側/右側/風控/籌碼/新聞判斷語言，供其他 agent 召喚 |
| Investment OS B role family | projects/invest-os-b-role-system.md | B1-B4 共用角色拆分、Owner logic、startup check、輸出契約 |
| Cross-project agent summon map | docs/cross-project-agent-summon-workflow-map.md | GPT/Codex/Claude/Gemini/NotebookLM/Antigravity/Hermes/OpenClaw/Windows agent 召喚場景、角色 why、Windows→Mac 收盤資料流 |
| A0 操作手冊 | docs/a0-dispatch-operations-manual.md | A0 調度操作手冊 |
| Drive 根目錄 | MAPLAB_DATA `19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt` | 品項圖片: MAPLAB_Items_Photos `1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT`；主試算表: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` |
| 交接紀錄 | handoff/tasks/T-xxx.md | 各任務斷點 + 接續 prompt |
| 歷史狀態 | archive/CURRENT_STATUS_2026-04-11_full.md | 2026-04-11 前完整巡查記錄 |
