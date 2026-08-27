# pitfalls.md

> Cold-start required. 每次修到重複錯誤，要把「觸發條件 / 根因 / 解法 / 預防 / **封坑驗證**」寫回這裡。
>
> **封坑驗證（2026-07-07 起新增，G1 技能 TDD）**：一條可執行指令或具體情境，證明有此規則後坑真的進不去
> （例：`bash scripts/xxx.sh` 應回 PASS、`grep ... | wc -l` 應為 0）。寫不出驗證方式的條目視同 `unverified`。
> 覆蓋率由 IS `gen_system_truth.py` 每日統計進 SYSTEM_MAP §6（基線 2026-07-07：MAPLAB 0/47、IS 1/229）。
> 選填欄「當時的合理化」：記下當時給自己的藉口，累積成紅旗清單。
> 依據：superpowers「NO SKILL WITHOUT A FAILING TEST FIRST」；我們的記憶鏈缺的正是 Verify 階。

## 2026-08-26 — Telegram CLI 訊息不能把 JSON escape 當成實際換行

- 觸發條件：用 `JSON.stringify()` 把多行訊息拼進 `scripts/notify_owner.sh` 的單一 CLI 引數；Bot API 回 200，但 Telegram Web 顯示的是字面 `\\n`，連 URL 邊界也被 escape 文字污染。
- 根因：JSON 字串的 `\\n` 是兩個可見字元，不會在一般 shell 雙引號引數中自動還原成 newline；只驗 HTTP 200／`message_id`，沒有檢查送出的 `result.text` 與 Telegram 可見畫面。
- 解法：補發時使用 bash ANSI-C quoting `$'...\\n...'` 讓 shell 在呼叫腳本前產生真實換行；以 Bot API `result.text | split("\\n")` 驗證行數，再用 Telegram Web 反讀正式訊息與連結。
- 預防：多行 Telegram 訊息優先由 stdin／message file 或明確的 newline-safe 介面傳入；若仍用 CLI 引數，禁止直接塞 JSON escape。完成判準必含 `message_id`、實際 line count 與 Telegram Web 可見文字。
- 封坑驗證：正式訊息 `message_id=4130` 的 Bot API readback 為 26 lines，Telegram Web 顯示三個獨立連結；格式不良的 `message_id=4129` 只能標失敗樣本，不得當交付完成。

## 2026-08-25 — Graphify 首建與 incremental update 必須共用同一 corpus 邊界

- 觸發條件：先用 `graphify extract . --code-only` 產生 2,203-node AST 圖，之後依全域規則跑 `graphify update .`，圖卻膨脹為 7,332 nodes／622 communities，大量 `skills`、`docs`、`handoff` Markdown 被當成 code-like 節點。
- 根因：首建的 `--code-only` 只是當次參數，incremental update 仍依 `.graphifyignore` 決定 corpus；當 ignore 沒有排除文件時，首建與後續更新來自兩個不同集合。
- 解法：`.graphifyignore` 明確排除 `*.md`／`*.txt`／`*.html`、歷史／generated／runtime／secrets／customer raw 與 Investment OS 路徑；另外排除會記錄 Graphify 自身統計的 canonical manifest/schema，避免地圖索引自己的數字形成 self-reference。以 `graphify extract . --code-only --force` 重建，再連跑兩次 `graphify update .` 驗證穩定。文件／角色／SOP 由 canonical manifest 與 NotebookLM safe pack 管理。
- 預防：新 repo 建 Graphify 前先寫 `.graphifyignore`；首建後立刻再跑一次 update，若 nodes 大幅增長就停下修 corpus，不把膨脹圖當正常 freshness。
- 封坑驗證：`graphify update .` 應顯示 `No code-graph topology changes detected`；`graphify diagnose multigraph --graph graphify-out/graph.json --json` 應為 1820 nodes／3262 edges 且 missing／dangling／self-loop／collapsed 全為 0。

## 2026-08-25 — 去敏替換文字本身不能再長得像 secret assignment

- 觸發條件：NotebookLM safe pack 已把一個設定值換成 `[REDACTED_CONFIG_VALUE]`，但保留 `token=[REDACTED_CONFIG_VALUE]` 形狀，後續 secret scan 仍命中 1 筆。
- 根因：只考慮人眼看不到原值，沒有把 redaction output 再餵回同一組偵測 regex 做 idempotence 驗證。
- 解法：assignment 類遮罩改成 `token value redacted`，不保留 `:`／`=`；unit test 強制所有 redacted sample 再掃一次必須為 0 matches。
- 預防：任何 sanitizer 都要通過 `sanitize → rescan`；遮罩字串不可符合原始敏感值 pattern。
- 封坑驗證：`python3 -m unittest tools.ai_workbook.test_build_directional_system_map.DirectionalSystemMapTest.test_secret_value_redaction_preserves_policy_words -v` 必須 PASS，且兩個 NotebookLM upload packs 的 secret-value scan 為 0。

## 2026-08-25 — WordPress 公開稿不能兼作產線審核包

- 觸發條件：Owner 再次發現文章含「快速導覽」「公開草稿只選無人畫面」、日期、圖片佔位與寫歌／剪片流程；整檔貼進 WordPress 時，客人會看到 agent 的內部自言自語。
- 根因：A2 文案、素材審核、Songwriter 與 A8 剪片共用同一份 Markdown，把「給客人看的內容」與「給下一位 agent 的證據」誤當成同一交付物；舊 WP SOP 又把 TOC 當成所有文章的固定模板。
- 解法：公開正文固定放 `wp_draft.md`，SEO metadata、日期、內鏈驗證、素材分級與媒體狀態放 `wp_internal_notes.md`；WordPress → Songwriter → A8 改為依序交接。短案例不強塞 TOC，案例日期預設不公開。
- 預防：建立或上傳 WordPress 草稿前先跑 customer-ready gate，並只把 `wp_draft.md` 送進 public surface；任何含 `Owner`、`repo`、路徑、待補、素材排除、生成工具或日期的檔案都留在內部包。
- 封坑驗證：`python3 tools/ai_workbook/a8_public_copy_gate.py workbook/reviews/JOB-A8-BUNNY-EDM-WP-20260825/wp_draft.md --forbid-dates` 應回 `"ok": true`；`python -m pytest -q tests/test_a8_public_copy_gate.py` 應 3/3 PASS。

## 2026-06-20 — Unattended long-running tasks need hardcoded constraint/error-handling, not "agent will notice"

- 觸發條件：研究一支「AI agent 無人介入連跑 27 小時」的影片（`docs/references/ai-agent-long-running-go-feature-rubric.md`）後，發現 MAPLAB 目前沒有任何規則明確規定 `/go` 類、cron、background task 等無人長跑任務的安全邊界；長跑迴圈若配上既有的高風險操作（例如會清空目錄的 deploy 腳本），一旦無人看管下重複執行，錯誤會被放大成大規模事故。
- 根因：既有 `AGENT_RULES.md` SECTION 8.5（硬性禁止）與 Guardrails 都是針對「有人在看」的情境寫的，沒有針對「完全無人介入、跑多輪」這個情境另外規定 worktree-only、gated deploy、reviewer HALT 權、token/時間/iteration 上限這幾件事。
- 解法：Owner 2026-06-20 拍板採納，新增 `AGENT_RULES.md` SECTION 19（無人長跑安全規則）八條規則；完整說明與理由見 `docs/governance/unattended-run-safety.md`；對應任務定義模板見 `templates/go-prompt-template.md`（GO prompt 五要素）與 `templates/rubric-template.md`（主觀任務 rubric）；task card 標準擴充見 `templates/task-card-template.md`。
- 預防：任何 `/go` 類、cron、background task 等無人長跑任務開始前，先確認 constraint（不能碰 runtime/secrets/main）與 error-handling（何時暫停回報）已經寫進該任務的 prompt 或 task card 的 `(C) Constraints + Error-handling / Escalation` 區塊，不能依賴「agent 會自己注意」。

## 2026-06-18 — Test receipt must be written before claiming completion

- 觸發條件：Agent 回報 IOS-KOL 雷達修正時說已測試、會寫 receipt，但 final 前沒有先把測試紀錄落成 repo artifact；Owner 追問「沒寫嗎」「有寫沒做」並要求把企業文化塞成冷啟動。
- 根因：把測試當成聊天回報，而不是交付物的一部分；Startup Check 沒先宣告 Test plan / Receipt path，收尾也沒有用 Handoff Checkpoint 檢查 `Tests run` 與 `Receipt`。
- 解法：新增 `workbook/reviews/JOB-IOS-KOL-RADAR-TEST-20260618/TEST_RECEIPT.md`，記錄 target tests、source/runtime py_compile、live DB preview、yt-dlp smoke、full test file 的 40 passed / 1 unrelated fail。同步更新 `docs/company-values.md`、`AGENT_STARTUP_PROTOCOL.md`、`AGENT_RULES.md`、`CURRENT_STATUS.md`，把測試與 receipt 變成 cold-start 硬規則。
- 預防：任何會改 owner-facing 行為的任務，Startup Check 必須列 `Test plan` 與 `Receipt path`；final 必列 `Tests run`。若未跑或未落檔，不得宣稱完成，只能標 partial / unverified。

## 2026-06-20 — IOS-KOL changed RSS rows must be cross-checked by source id, not global latest window

- 觸發條件：新增《兆華與股惑仔》Podcast RSS 後，runtime DB 已寫入 `influencer_insights.id=611`，但 owner-facing digest 一開始沒有出現，因為該集發布日是 2026-06-18，前面已有更多 2026-06-20 rows。
- 根因：RSS sync 完成後呼叫 `build_cross_checks()` 只看全域 latest 20，不看本輪 changed row；新來源若發布時間較舊，會被較新的其他 KOL/RSS rows 擠掉。
- 解法：`build_cross_checks()` 新增 `source_ids` 參數，`sync_youtube()` / `sync_rss_sources()` 對本輪 changed ids 做 scoped cross-check；測試用 25 筆較新的 BlockTempo rows 回歸驗證，確保核心 KOL podcast RSS 仍會建立 cross-check。
- 預防：任何新增來源或補 sync，都要驗三層：`influencer_insights` 是否寫入、同一 id 是否有 `influencer_cross_checks`、owner-facing preview 是否渲染。production smoke 必須明確帶 `--db-path`，不得依賴目前工作目錄。

## 2026-06-18 — A6 quote mode must be Sheet-first, and Apps Script Web Apps need redeploy

- 觸發條件：Owner 在 Telegram 傳生日派對截圖與「15 人有主食高毛利、要英文菜單」後，`maplab_a6_bot` 先回 Claude 未知錯誤，再直接切 `gemma4:latest` 本地備援，只產 review bundle，沒有產可檢查的 Google Sheet 報價單。
- 根因：`bot_a6._run_a5_quote_background()` 雖然有雲端 A5/GAS helper，但實際 hot path 寫死先跑 `run_a5_local_quote()`；本地模型 JSON 品質不穩，A6 又把降級草稿當成完成。第二層問題是 `clasp push` 只更新 Apps Script HEAD，A6 `.env` 使用固定 Web App deployment v11，未 redeploy 時仍跑舊版 `applyQuoteVariantToCopy_()`，導致報價副本 D19/D20 殘留禮盒列。
- 解法：A6 明確報價訊息先用 deterministic `build_sheet_quote_payload()` 從 `data/items_master.json` 建 `createQuoteVariants` payload 並呼叫 GAS；成功後回 Sheet URL、菜單、總額、成本、毛利率。本地 `/localquote` 僅作測試，不寫 Sheet。GAS 修 `applyQuoteVariantToCopy_()` 清空 D/F/IJ 7:20，並用 `clasp deploy -i <existing deployment id>` 更新 A6 正在使用的 Web App 到新版本。
- 預防：任何 A6 報價修復驗收必須包含三段：本地 payload smoke、GAS live createQuoteVariants smoke、Google Sheets connector 回讀 `報價單!D2:F31` 與 `I7:J31`。若只看到 `Pushed files` 不算 Web App 已更新；要檢查 `clasp deployments` 並確認 `.env` 使用的 deployment id 已 redeploy。

## 2026-06-18 — Quote trainee agents must not self-certify PASS

- 觸發條件：Owner 要求把 A6/A5 報價成功路徑教給下游 agent；Codex 選 OpenClaw 跑 supervised training。OpenClaw Round 1 自判 `PASS`，但只列 6 個品項、使用泛稱/不存在品項、payload shape 不符；Round 2 仍自判 `PASS`，但把 `variants` 寫成品項陣列、漏 `action/base/totalRevenue/foodCost`，還自創價格與錯誤數量。
- 根因：下游本地 agent 可以吸收口號式規則，但不會自然遵守 A5 報價的 exactness gate；若讓 trainee 自判完成，會把「看似接近」誤當可用報價。
- 解法：建立 `workbook/reviews/A6-QUOTE-OPENCLAW-TRAINING-20260618/supervisor_lesson.md`，明確記錄 Round 1/2 失敗、正確 `createQuoteVariants` payload shape、10 個既有 MAPLAB 品名、NT$15,700 / NT$3,140 / 80.0% / 訂金 NT$7,850、客戶安全文案與下次訓練 gate。同步補進 `skills/a5-quotation-engine-skills.md` 的學徒 agent gate。
- 預防：任何 OpenClaw/Hermes/local model 接手 A5/A6 報價，必須由主管 agent 檢查：`action=createQuoteVariants`、`variants[].menu`、精確品項數、既有 Items 品名、回讀 Sheet 範圍、Telegram Web surface proof。沒有 supervisor readback，不得接受 trainee 的 `PASS`。

## 2026-06-20 — A5 quote trainees need fixed customer templates, not freeform commercial copy

- 觸發條件：A5/A6 報價學徒訓練延續到 Round 3-5。直接 Ollama `qwen2.5:14b` 能產出正確 `createQuoteVariants` payload 與 10 道品項，但自由客戶文案先漏出 `高毛利` 與 `桌椅`，下一輪又把「預收 50% 訂金」改成「一定比例的訂金」。
- 根因：模型對數字/payload 的 exactness 可被 strict JSON 約束，但商務條款和客戶承諾若交給自由改寫，會自然軟化或過度承諾；自我檢查欄位也可能說 PASS 但文案實際不合格。
- 解法：Round 5 改用直接 Ollama `qwen2.5:14b`、`temperature=0`、固定客戶模板與 deterministic supervisor gate，通過 10 道品項、`foodCost=3140`、`totalRevenue=15700`、`overallMargin=0.8`、`depositAmount=7850`、`預收 50% 訂金`、桌面簡潔佈置、禁語檢查。
- 預防：A5/A6 學徒只可產生結構化 payload 或複製核准模板；不得自由改寫 urgent deposit、英文版、佈置承諾等商務條款。OpenClaw/Hermes 未通過相同 gate 前，不得宣稱已訓練堪用。

## 2026-06-17 — A5 quote answers must come from a quote Sheet, not chat math

- 觸發條件：Owner 提供生日派對截圖要求 A5 報價與 80% 以上毛利；Agent 先用聊天手算與自選菜單回覆，沒有先調用既有 Google Sheet 報價副本/QUOTE_DRAFT 試算，也沒有產出可檢查的報價單連結。
- 根因：讀到 A5 `createQuoteVariants` 與 Items 資料後，把「能算出一組數字」誤當成「完成報價」。沒有先讀 `skills/a6-rapid-quote-sop.md` SECTION 7 與 QUOTE_DRAFT 歷史踩坑，導致混用 GAS adapter、connector 與手算，且沒有遵守 MVP 流程：業務用既有下拉品項在報價 Sheet 裡試算。
- 解法：先用 Chrome/Owner 登入態或既有 GAS/Drive flow 複製整份 `MAPLAB_外燴系統_v0.1`，只在副本填 D/F 品項與數量、費用與總額欄；使用現有 `Items`/DropdownHelper 的基本品項，不自創菜名；最後讀回 Sheet 計算結果與連結。必要時只在副本補 VLOOKUP/小計公式，不改母版。
- 預防：任何 A5/A6/Codex 報價任務若要求報價、毛利、試算或報價單，完成標準必須包含 Sheet URL、菜單行、訂單成本、總金額、毛利率的回讀證據。聊天手算只能作草稿，不得當成 A5 報價完成。

## 2026-06-17 — Telegram `召喚` must create a dispatch receipt, not just routing advice

- 觸發條件：Owner 在 Telegram 問 Google/Meta 廣告成效判讀，`maplab_claude_bot` 回「召喚 A3」與下一步欄位，但沒有建立 task packet、沒有丟給 Codex/OpenClaw，也沒有回 dispatch receipt；Owner 追問「所以誰做你召喚了嗎」。
- 根因：`bot/bot.py` 的 `_local_dispatch_answer()` 只產文字建議，沒有 file-backed command intake、worker handoff、prompt artifact、OpenClaw/Codex queue 或 receipt。這違反外部 command window 的 P0 驗收：Telegram 指令 → role route → cold-start prompt/context → worker dispatch → progress receipt。
- 解法：新增 Telegram dispatch route：`/codex_dispatch` 與自然語句派工觸發都要建立 `workbook/telegram-dispatch/TG-DISPATCH-*/packet.json`、`prompt.md`、`README.md`、`index.jsonl`，並寫入 Codex clipboard bridge；回覆必須列 `dispatch_id`、主責角色、worker、status、packet/prompt 路徑，OpenClaw worker 可背景接手。
- 預防：任何 `召喚`、`派給`、`貼到 Codex`、`誰做`、`不是回覆` 類 Telegram 訊息，不得只回「請 A3/A2/A1 做」。若沒有產生可追蹤 dispatch artifact 或 worker receipt，只能說「尚未派工」，不能說「已召喚」。

## 2026-06-17 — A8 local fallback JSON is not a video, and internal ops wording must be blocked

- 觸發條件：Owner 指出 A8 地端模型只產 JSON 不算影片備援，且字幕 `取餐要順` 聽起來不順、不優雅；同時追問 Hermes/OpenClaw 是否應納入工具鏈。
- 根因：把「地端模型可產 storyboard/metadata JSON」誤報成「A8 local fallback 可用」，沒有把模型輸出接到本機影片工具與 MP4 驗證；prompt seed 也把 `取餐要順`、`動線穩` 這類內部流程語餵回模型，造成壞文案回流。
- 解法：新增 `tools/ai_workbook/a8_local_model_video_pipeline.py`，把 `qwen2.5:14b` 輸出接到 Swift/AppKit frame renderer 與 ffmpeg，完成 `local_model_video_v5/a8-short-local-model-video.mp4`；`a8_local_model_fallback.py` 加上 brand-clean seed、off-brand wording blocklist、platform copy validation。Hermes/OpenClaw 也要實測：Hermes gateway stopped 不進 hot path；OpenClaw browser 可做 UI readback，但 agent QA 回 `NO_REPLY`，不能當 A8 主 QA。
- 預防：A8 地端備援完成標準一律是 JSON valid + MP4 rendered + ffprobe 1080x1920 H.264 + QA frames checked。不得使用 `取餐要順`、`取餐`、`順暢`、`分開`、`詳盡`、`動線穩`、`節奏更穩` 等內部流程語；每次聲稱 Hermes/OpenClaw 可用前要跑 status / doctor / actual worker smoke，不得用工具名代替能力證明。

## 2026-06-17 — IOS-KOL Telegram digest must carry transcript gate and worker status

- 觸發條件：Owner 截圖詢問 TelbotFin/Telegram `網紅單集重點` 是否屬於 IOS-KOL / OpenClaw 責任，並指出期待不是只管游庭皓，而是要有逐字稿、重點整理、格式確認、英文內容翻譯、多 KOL 共識與夜盤總經判讀。
- 根因：`sync_influencer_agents.py` 的 `influencer_insights` 有 `transcript_status` / `transcript_source`，但 `influencer_cross_checks` 發送層只看 `status=closed` 與 `content_extraction`，沒有在 Telegram render 前明確檢查逐字稿品質與 worker 狀態；操作筆記也可能把 `操作/策略筆記` 這種段落標題當成內容。
- 解法：runtime `owner_visible_episode_rows()` 改為只讓 `transcript_status=ok` 的 YouTube 內容進正式 `網紅單集重點`，RSS / metadata-only 留待補；Telegram 開頭標明 `IOS-KOL 網紅雷達經理｜團隊指派 OpenClaw/ASR 回報` 與流程 gate；operation note render 濾掉段落標題與 Q/A 殘渣；新增 `docs/ios-kol/daily-telegram-workflow.md` 定義每日流程。
- 預防：IOS-KOL Telegram-facing output 必須在發送前列出資料層級：RSS metadata / transcript / ASR / summary / format-check / OpenClaw 或 NotebookLM worker 狀態。多 KOL 共識與夜盤總經判讀應走夜間綜合 digest，不要用單集通知假裝完成共識研究。

## 2026-06-17 — Extension summon is a file-backed role handoff, not a UI blocker

- 觸發條件：Owner 要求先透過 Chrome Extension 召喚 A2，檢查 prompt / task card / handoff 迴圈；Agent 先把 prompt 給 Owner 看，又在無法打開 `chrome-extension://.../popup.html` 後把問題說成需要 Owner 手動操作。
- 根因：沒有先讀 `skills/extension-agent-summon-guide.md`。把 Extension 誤解成只能由 UI 操作的頁面，而不是以 `chrome-extension/task-modules/{role}.json`、`workbook/task_modules/*` 與 `popup.js buildModuleHandoff()` 為核心的 file-backed dynamic role module。
- 解法：遇到 `extension`、`召喚`、`Agent Commander`、`角色通路`、`handoff 交接`，先讀 `skills/extension-agent-summon-guide.md`。若 UI 不可用，改走 file-backed summon：讀 role module JSON、讀 build report、按 handoff 結構放入本次召喚任務，直接交給對應 runtime / subagent，並取得被召喚角色回報。
- 預防：不得把「我建了 task card」等同「完成角色交接」；交接完成的判準是被召喚角色已收到 handoff、讀卡、回報 Startup Check / 缺口 / 驗收清單。若沒有角色回報，只能說 task card 已建立，不能說已交接。

## 2026-06-11 — Session 留下的每分鐘 babysitting cron 變成殭屍，癱瘓 Hermes 半天

- 觸發條件：Owner 問「Hermes 有貢獻了嗎可以用了嗎」，調查發現 Hermes 單日 280 個
  `Response remained truncated` 錯誤，所有產出停擺。
- 根因：5/23 某個 session 在 Hermes 建了 `auto-allow-gemini` cron（每 1 分鐘用 gemma4
  看螢幕、自動點 Antigravity/Gemini 的允許按鈕）。Session 結束後沒人清理，job 留著
  每分鐘失敗一次、空轉 GPU、跟 A6/照片管線搶資源。它同時是資安反模式：盲目自動批准
  權限對話框。
- 解法：備份 `~/.hermes/cron/jobs.json` 到 `agent-hq/memory/hermes/` 後
  `hermes cron remove b468df475c5f`。Owner 明確指令「刪除 auto-allow-gemini」後執行。
- 預防：(1) 任何 agent 建立的 cron / launchd / hermes job 必須登記到
  `agent-hq/runtime/REGISTRY.md`，未登記 = 野生 job，B4 patrol 可砍。
  (2) 為單次 session 建的 babysitting job 必須設次數上限或在 session 結束時移除。
  (3) 「自動點允許按鈕」類的 job 一律禁止——權限對話框存在的意義就是要人看過。
  (4) 排查「某 agent 突然壞掉」時先看它的 cron/scheduler 有沒有殭屍任務。

## 2026-05-30 — B3 archive is not the same thing as the B4 patrol verdict

- 觸發條件：B3 被召喚來做 Investment OS overbuild 的 runtime handoff，輸出內容同時包含 archive、resume prompt、status writeback plan，還會自然想把 `continue / pause / refactor` 一起整理進去。
- 根因：B3 的職責是把版本紀錄、交接紀錄、review bundle 與 durable artifact 收好，不是替 B4 做最後的系統巡查裁決；如果不切清楚，下一個 agent 會把 provisional 建議誤當成已批准的系統決策。
- 解法：B3 bundle 只保留 archive / handoff / resume / writeback plan / review request；`continue / pause / refactor` 明確標成 provisional，交 B4 review，再由 Owner 或 B4 升格成 final verdict。
- 預防：遇到「請列出哪些該繼續、暫停、重構」這類問題，先做角色邊界檢查。B3 先記錄，B4 來裁決；不要讓 archive bundle 變成第二份 patrol report。

## 2026-05-29 — Repo extension update is not live Chrome proof

- 觸發條件：Owner 指出 Chrome Extension 根本沒有「召喚欄位」，並質疑是否回到需要重新下載/重新設定的舊路。
- 根因：前一輪把 source repo 的 v5.5.6 角色拆分，誤當成 live Chrome extension 已更新；Chrome `Secure Preferences` 可殘留舊 unpacked extension path，但不代表目前 profile 真的啟用。桌面也可能有另一份 stale `chrome-extension` 資料夾，不能在 file chooser 誤選。
- 解法：v5.6.0 新增 popup 內的 `召喚任務` textarea 與 `自動選角`，並改成 task modules 優先讀 extension 本機 packaged JSON、GitHub raw 只作 fallback；改版路徑是 reload/重新載入 canonical unpacked folder `/Users/pagemacmini/maplab-ai-handbook/chrome-extension`，不是下載新 copy。
- 預防：任何 Chrome Extension 改版收尾都要分三層驗證：`manifest/popup source` 已改、Chrome Extensions 頁顯示 MAPLAB Agent Commander active、popup/side panel 實際看得到新 UI；未完成第三層前，不得說「Extension 已更新」。

## 2026-05-24 — Planned B2B slugs are not live WordPress URLs

- 觸發條件：Owner 要求 A2 先了解網站是否真的往 To B 經營，並提醒要同步冷啟動存檔，避免下次重查。
- 根因：舊 task card / local workbench 使用 planned slugs（如 `meeting-refreshment-catering-tainan`、`opening-event-catering-tainan`、`brand-event-catering`），但 live site 實際已發布的是另一組 post slugs；如果下次只讀 repo 舊紀錄，會把 404 當成目標頁。
- 解法：用 public REST + 前台 HTTP 狀態重查；確認 6 pages / 57 posts、`企業外燴案例` category 15 篇、live To B slugs 為 `corporate-catering-tainan`、`corporate-tea-party-desserts`、`tainan-corporate-opening-tea-catering`、`brand-esg-catering-service`、`press-conference-catering`、`vip-expo-catering-business-meeting`。同步更新 `CURRENT_STATUS.md`、`docs/a2a3/live-wordpress-audit.md`、`b2b-case-inventory.md`、`b2b-workflow-guide.md` 與 task cards。
- 預防：A2 寫案例前必先查 live URL 200/404，並分開 `可公開案例名 / 內部核對名 / 場景類型 / live URL / 可用照片`；Rank Math 已退訂後，既有設定先保留，不再把 RM 設定當本輪工作。

## 2026-05-11 — A4 asset root ID drifted across docs and scripts

- 觸發條件：Owner 要求「讓事實說話」，重新核對 A4 相片與素材存放位置。
- 根因：active docs/scripts 同時殘留三種 `MAPLAB_ASSETS` ID：舊 ID `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe`、一個 `O/0` 打錯的 ID、以及現行 ID；dashboard 和部分 credentials doc 仍指向舊 ID。
- 解法：用 Google Drive API 讀取 folder metadata；確認 `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy` 是目前 `MAPLAB_ASSETS`，且舊 ID API 回 404。active docs/scripts 統一更新到現行 ID，archive/review output 保留歷史原貌。
- 預防：任何資源位置更新前，先用 Drive/Sheets API 查 `id/name/parent/trashed`；不能只相信 repo 記錄或 dashboard HTML。

## 2026-05-11 — Do not move an active user working directory

- 觸發條件：Owner 發現 `/Users/pagemacmini/Downloads/maplab-ai-handbook-main` 工作目錄缺失。
- 根因：A1 將非 git 下載副本移到「沒用的資料夾」做隔離；雖然不是刪除，但該路徑正是目前 session 的 `cwd`，等同破壞工作環境。
- 解法：立即把資料夾原路徑恢復；治理報告改為「標記為非 canonical，不物理搬移」。
- 預防：清理/隔離任何使用者可見資料夾前，先確認是否為 active `cwd`、桌面入口、同步資料夾或近期工作區；移動前需 Owner 明確批准。

## 2026-05-11 — A2/A3 workbench built in non-git download copy

- 觸發條件：Owner 發現上方快速瀏覽連結壞掉，並懷疑 repo 紀錄寫壞。
- 根因：A2/A3 工作台文件與產生器被做在 `/Users/pagemacmini/Downloads/maplab-ai-handbook-main`，該資料夾不是 git repo；正式真相源 `/Users/pagemacmini/maplab-ai-handbook` 沒有收進同一批檔案。
- 解法：以 `/Users/pagemacmini/maplab-ai-handbook` 為唯一正式 repo，將 A2/A3 docs、產生器、技能書與 scenario config 收回正式 repo。
- 預防：任何可交接文件、產生器、技能書都必須先確認 `git status` 可追蹤；下載副本只能當暫存來源，不得作為正式工作目錄。

## 2026-05-11 — Generated HTML links pointed at stale command names

- 觸發條件：`handoff.html` / `handoff-board.html` 有 13 個 broken links。
- 根因：產生器改成建立 `run_wp_*` / `schedule_wp_*`，但 HTML 仍輸出舊的 `run_wordpress_*` / `schedule_wordpress_*`；快捷入口也錯指到 `wordpress 素材庫/*.command`。
- 解法：handoff board 產生器改用 `MAPLAB_A2A3_Workbench/*.command`，WordPress 任務按鈕改為 `run_wp_*` / `schedule_wp_*`，並在產生器結尾加入 link check。
- 預防：每次生成 HTML 後必跑 link checker；壞連結不得交給 Owner 當「可點擊面板」。

## 2026-05-11 — Public drafts mixed internal QA fields

- 觸發條件：WordPress preview / draft 中出現價格區間、內部日期與本機 Drive 線索。
- 根因：內部 QA、source bridge、公開草稿共用同一批欄位，沒有把「給人核對」和「可發布」分層。
- 解法：公開 `draft.md` / `copy.md` / WordPress preview 不得含價格、內部日期或 `file://`；日期、報價單推斷與本機素材路徑只放 `brief.md` / `source_bridge.md` / internal QA board。
- 預防：產生器結尾必跑 public output safety check，攔截價格、本機路徑與內部日期標籤。

## 2026-05-11 — Unreviewed generated photos must not become publish assets

- 觸發條件：Owner 判定今天生產的圖片不可用，要求不要保留。
- 根因：素材選圖與裁切未達可發布標準，且 preview / work package 把未審核圖片包裝成可交辦素材。
- 解法：刪除桌面 A2/A3 工作台中的圖片衍生物，保留文字、manifest、prompt 與治理紀錄；下一輪必須先完成圖片來源 QA，再重建圖包。
- 預防：未通過 Owner/visual QA 的圖片只能留在 internal review，不得放進 public draft 或 OpenClaw work package。

## 2026-05-11 — Repo records confused with live WordPress facts

- 觸發條件：Owner 指出「用接口進去看事實與現況，不是看人家寫給你的紀錄」。
- 根因：A2/A3 workbench 修復時先整理 repo 記錄與 local artifacts，沒有先用 WordPress / Rank Math 接口核對 live site。
- 解法：新增 live fact check：WP public REST 顯示 6 pages / 57 posts；planned workbench slugs 在 pages/posts 都是 0 match 且前台 404；Rank Math PRO 前台活著，但 analytics/score endpoints 未登入回 401。
- 預防：任何 WordPress / SEO / Rank Math 任務必須先查 live接口，再讀 repo 紀錄；repo 紀錄只減少斷點，不能作為現況證據。

## 2026-05-11 — Elementor page body ignored WP REST post_content edits

- 觸發條件：`/gender-reveal-party-tips/` 的 Rank Math title / description 已更新，但用 WP REST 追加的正文內連區塊只存在 raw `post_content`，前台沒有渲染。
- 根因：該頁前台由 Elementor data render，普通 `post_content` 不是實際畫面來源；同時原 Elementor HTML 區塊曾有 `</section` 斷尾，造成 raw content 與 rendered HTML 進一步不一致。
- 解法：Rank Math meta 可用 Rank Math REST 更新；但 Elementor-rendered 頁的正文、內連與 FAQ 必須走 Elementor data / wp-admin UI / Elementor 正式 API 驗證，不可只看 WP REST raw content。
- 預防：A2 修頁時同時檢查 `content.raw`、`content.rendered`、前台 HTML 三層；三者不一致時，以前台 HTML 為準。

## 2026-05-11 — Google recrawl submission cannot be inferred from old repo notes

- 觸發條件：Owner 問「所以是要去送資料給google確認對吧」，需要把 Rank Math 修復後的 URL 送進 Google 可發現/可重爬流程。
- 根因：repo 舊文件寫 GSC 已接通，但本機實際 `google-token.json` 只有 Drive/Sheets scope；`mcp-server-gsc` 可列出 `submit_sitemap` / `index_inspect` 工具，但目前憑證是 OAuth client，server 實際要求 service account 的 `private_key` + `client_email`。此外，Google sitemap ping 已 deprecated，Indexing API 也不是一般 WordPress 頁可用的萬用提交。
- 解法：先用 live HTTP 驗證 sitemap / robots / page indexability，再用 Rank Math Instant Indexing `/wp-json/rankmath/v1/in/submitUrls` 送出 8 個 URL，並把 GSC API 權限不足記錄在 review bundle。
- 預防：任何「提交 Google / GSC」任務必須分清楚四件事：sitemap 可發現、Rank Math indexing endpoint 是否 accepted、GSC URL Inspection 是否有 scope、Search Console UI Request Indexing 是否已人工點擊；不可把其中一項成功說成全部完成。

## 2026-05-12 — Image recognition is QA, not the primary asset key

- 觸發條件：Owner 要求「搜尋日期+報價單+外燴catering類別的檔案夾+已經seo辨識過文字的sheet，補2025先」。
- 根因：只看畫面或只看 AI 文字辨識會誤判案例；照片要先和活動事實鏈對上。
- 解法：先用 Drive metadata 的拍攝日期，交叉 TimeTree 外燴事件、本機報價單 `.gsheet` 日期、ASSET_LOG `year/category/keywords/seo_name`，最後才做視覺 QA。
- 預防：A2/A3/A6 找圖先跑 `python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 120`，不得直接從網格截圖或未核對圖庫拿圖。

## 2026-05-12 — Stale raw review bundles must leave active evidence area

- 觸發條件：`workbook/reviews/` 混入舊 A6/OpenClaw smoke-test raw bundles，導致 active review evidence 與失準測試混在一起。
- 根因：raw bundle 曾被保留作除錯證據，但未完成 sanitize / commit policy，後續 dashboard 與 review 視覺上混淆。
- 解法：無外部 repo 引用、未追蹤、標記 `hold_raw_bundle_until_sanitized` 的 raw bundle 移到 `trash/stale-runtime-artifacts/`，只保留 manifest pointer。
- 預防：`workbook/reviews/` 只放 active / reviewed / tracked evidence；stale raw bundle 不直接 commit。

## 2026-05-18 — Telegram commands need explicit CommandHandler

- 觸發條件：`/localquote ...` 已寫進 help，但 Telegram Web 發出後 bot 沒進報價流程。
- 根因：一般文字 handler 使用 `filters.TEXT & ~filters.COMMAND`，斜線命令會被排除；只新增 help 文案不會讓 command 被處理。
- 解法：為 `/localquote` 加上獨立 `CommandHandler("localquote", localquote_cmd)`，再由 handler 呼叫 A5 本地備援報價流程。
- 預防：任何新增 Telegram slash command 必須同時檢查 help text、CommandHandler 註冊、Telegram Web 實送測試三件事。

## 2026-05-18 — OpenClaw quote bundles depend on REVIEWS_DIR

- 觸發條件：A5 本地報價 fallback 顯示 `OpenClawAdapter unavailable`，只剩 direct Ollama，沒有 review bundle。
- 根因：`tools/ai_workbook/openclaw_adapter.py` 匯入 `REVIEWS_DIR`，但 `tools/ai_workbook/paths.py` 沒有定義該常數。
- 解法：在 `tools/ai_workbook/paths.py` 補上 `REVIEWS_DIR = WORKBOOK_DIR / "reviews"`，讓 A5 Telegram 報價能產生 `workbook/reviews/A5-QUOTE-*` bundle。
- 預防：新增 OpenClaw adapter 依賴時，先用同一個 bot runtime Python 做 import smoke test，不只用 repo 靜態閱讀判斷。

## 2026-05-18 — Local models need deterministic Chinese money parsing

- 觸發條件：Telegram A5 本地報價把 `預算5萬` 輸出成 `NT$500,000`，`預算4萬` 輸出成 `NT$400,000`。
- 根因：本地模型對中文單位「萬」不穩，容易把 5 萬誤展成 50 萬；光在 prompt 說明不夠可靠。
- 解法：進模型前先解析預算與人數，prompt 放硬解析提示；輸出後再以 deterministic postprocess 校正第一個預算欄位，並在 Telegram 回覆加 `金額校正` 註記。
- 預防：所有本地 A5 報價都要先跑金額、數量、飲食禁忌的 deterministic guard，再讓模型生成草稿。

## 2026-05-18 — Local model terminal control codes leak into Telegram

- 觸發條件：Telegram 報價草稿裡出現 `[K` 之類雜訊。
- 根因：本地模型或 CLI runtime 的 ANSI control sequence 混入 raw response；如果直接送 Telegram，手機端會看到殘留控制碼。
- 解法：A5 quote engine 在回覆與 review draft 寫入前先移除 ANSI escape sequences。
- 預防：所有 Telegram-facing local model output 都要先做 ANSI/control-code sanitize，再送出或存入可讀 review artifact。

## 2026-05-18 — launchd must pin the same local runtime as foreground tests

- 觸發條件：foreground Telegram `/localquote` 約 1 分鐘可回，但 launchd 長駐版只送出心跳，bundle 停在 `task_request.md`。
- 根因：手動測試時 shell 帶了 `A5_LOCAL_ENGINE=ollama A5_LOCAL_MODEL=llama3.1:latest` 和完整 Homebrew `PATH`；launchd plist 只設定 `PYTHONUNBUFFERED`，因此回到較慢的 `auto` / default model path，且 subprocess 找不到 `ollama` CLI。
- 解法：在 `bot_a6/com.maplab.a6bot.plist` 明確設定非秘密 runtime 參數：`PATH=/opt/homebrew/bin:...`、`A5_LOCAL_ENGINE=ollama`、`A5_LOCAL_MODEL=llama3.1:latest`、`A5_LOCAL_NUM_PREDICT=650`、`OPENCLAW_AGENT_TIMEOUT_SECONDS=45`。
- 預防：任何 foreground 成功的 bot runtime 測試，收尾時都要同步檢查 launchd plist / wrapper 是否帶同一組非秘密環境設定與 CLI PATH。

## 2026-05-19 — A6 LINE path doc was missing from active repo

- 觸發條件：Owner 要求「把路徑畫好，讓接手工作的找得到」，並詢問 Case Store 要自建還是拉資料。
- 根因：`CURRENT_STATUS.md` 知識地圖指向 `projects/line-quote-assistant.md`，但 active repo 沒有該檔，只剩 `trash/projects/line-quote-assistant.md`；接手者會以為文件不存在或跑去非 git Downloads 副本。
- 解法：補回 active `projects/line-quote-assistant.md`，明確畫出 LINE OA → CONVERSATION_LOG → Case Store → A6 Telegram → A5/GAS 的路徑，並列出現有成果、限制、測試最短路徑。
- 預防：CURRENT_STATUS 的知識地圖每個 active path 都必須存在；如果文件被移到 trash/archive，要同步改知識地圖或補新的 active handoff。

## 2026-05-19 — Paused roles need explicit module state

- 觸發條件：Owner 用 Chrome Extension 檢查 B1，發現 B1 仍掛在 Extension，但實際需求已從 InnerFlowLab 內容創作轉成跨專案治理建議，且希望建好 prompt 後暫停整個 B1 專案。
- 根因：角色模組只描述原功能，沒有表達「暫停」「只在明確召喚時啟用」「禁止發布/下單/讀 secrets」等狀態；接手者會以為 B1 仍應推 Substack/API 發文流程。
- 解法：新增 `projects/b1-cross-project-governance-advisor.md` 與 `workbook/reviews/JOB-B1-CROSS-PROJECT-20260519/`，更新 B1 recall、task card、skill、AGENT_RULES、AGENT_RECALL_PROMPTS，並重建 Chrome Extension B1 module。
- 預防：任何角色暫停時，必須同步更新 Task Card、Recall、Extension module、CURRENT_STATUS 與 Resume Prompt；不得只在聊天裡說「先暫停」。

## 2026-05-19 — A6 quote mode must not swallow general chat

- 觸發條件：Owner 在 Telegram 問「你現在是跑什麼模型」，A6 回「A5 報價模式處理中」，並切到 A5 本地 fallback。
- 根因：`/start` 與 `_get_mode()` 預設都把聊天放進 `MODE_QUOTE`，`handle_message()` 又把 quote mode 內的所有文字都丟進 A5，沒有先分辨模型/status/一般對話。
- 解法：A6 預設改為 `MODE_CHAT`；新增 `/status`、`/model` 與模型狀態意圖偵測；文字路由先處理 runtime/status 問題，再用明確報價意圖才進 A5。
- 預防：Telegram route 測試至少涵蓋四類：模型/status 問題不進 A5、一般聊天不進 A5、明確「報價 ...」進 A5、Case Store 查詢仍走 `/case`/`查` 路徑。

## 2026-05-19 — A6 chat fallback must not become the default

- 觸發條件：Owner 問 A6 是否真的能對話，指出需求是「平常接 Codex，除非沒有額度才改地端」，不是寫一段狀態文案敷衍。
- 根因：前一版只修掉誤入 A5，但一般聊天仍直接走 `_run_ollama_guarded()`；也就是 fallback 被當 default，能力自然偏弱。
- 解法：新增 Codex-first 對話層：普通聊天/SEO 先用 `codex exec --ephemeral -s read-only` 回覆；Codex CLI 不可用、額度/網路失敗或逾時時，才透明通知並 fallback 到本機 Ollama。
- 預防：A6 對話能力測試要證明 primary engine，而不是只證明有回覆；smoke 至少檢查 `codex_ask()` 實際回應、runtime status 顯示 Codex primary、fallback 通知存在。

## 2026-06-14 — Local quote model output is not a Sheet payload

- 觸發條件：Owner 要 A6 測競品菜單截圖，需求是辨識所有品項、做 MAPLAB 雷同品項、毛利/食材成本安全、成本總價 * 5、產試算表連結；gemma4 本地模型回了長篇 Thinking，但沒有合法 JSON。
- 根因：地端模型即使 prompt 寫「必須 JSON」，仍會輸出推理過程、截斷、漏掉 `createQuoteVariants`；prompt 只能降低風險，不能當資料契約。
- 解法：A5 quote engine 加 Items catalog prompt、禁止假菜名、移除 Thinking/ANSI，且 JSON 不合法時用 `data/items_master.json` deterministic fallback 產 `createQuoteVariants` payload。成本未知或 0 的品項列 `needsManualCost`，不硬猜。
- 預防：A6/A5 報價完成標準是「`_extract_form_data()` 讀到合法 JSON，GAS 回 Sheet URL」，不是模型看起來像有回答。競品菜單/雷同品項/成本*5 任務必讀 `skills/a6-local-quote-model-tuning.md`。

## 2026-06-14 — Case Store fallback seed is not live Google Sheets proof

- 觸發條件：A6 `case_store.py today` 顯示 `source=fallback:...conversation_log_seed.json`，若沒特別拔掉 fallback，容易誤以為 A6 已能讀 live `CONVERSATION_LOG`。
- 根因：`case_store.py` 的 fallback seed 會在 Google Sheets 讀取失敗時接手；本機 Google token 實測回 `invalid_grant: Token has been expired or revoked.`。
- 解法：live Sheet 驗證時把 `CASE_STORE_FALLBACK_JSON` 指到不存在的路徑再跑，例如 `CASE_STORE_FALLBACK_JSON=/tmp/a6-case-store-missing.json bot/venv/bin/python bot_a6/case_store.py today --rows 20 --limit 1`。只有不靠 fallback 成功，才算 A6 live Case Store 恢復。
- 預防：報告 A6 Sheet 能力時必分開「GAS Web App 可建報價副本」和「Case Store 可讀 live CONVERSATION_LOG」；兩條使用不同憑證/路徑，不可互相代證。

## 2026-06-14 — Secret safety must not become a work blocker

- 觸發條件：A6 runtime 判斷需要知道 `.env` 裡的非秘密設定或確認 launchd 是否真的帶入 `A5_LOCAL_MODEL`，但 Agent 說「我不會讀 `.env`，因為有 token/secrets」，導致無法判斷 live bot 設定。
- 根因：把「不要洩漏 secrets」誤解成「不能碰設定檔」。這會讓 Telegram bot、GAS、Sheets、LINE、OAuth 類工作全部卡死。
- 解法：可以在 Owner 任務範圍內讀取或 source `.env` 來執行/驗證；但不要把 token、OAuth、API key、完整 secret value 印到聊天、log、commit、review bundle。需要展示時只列 key 名、是否存在、前後遮罩或非秘密 runtime 值。
- 預防：遇到 `.env` 先分三類處理：`runtime config` 可讀可回報、`secret value` 可使用但不外顯、`要修改/輪替 secret` 才需要明確 Owner 確認。不得把安全規則當成不上班的理由。

## 2026-06-15 — Unverified social model claims are not runtime integration plans or work blockers

- 觸發條件：Owner 貼 IG/Threads/新聞截圖，聲稱某模型可控制 Mac、呼叫大量原生工具、或具備新 AI skill。
- 根因：Agent 把二手社群貼文當成已驗證 source，或反過來把「未驗證」當成不上班理由；兩者都忽略 MAPLAB 的主動推進與三層阻塞審查。
- 解法：先找 primary source；找不到就標註未驗證，但仍把可用概念拆成既有安全路由：connector、Chrome/OpenClaw、shell/osascript、review bundle、approval-ready packet。read-only、draft、disposable test 直接做。
- 預防：新 runtime 進 A6 前必須有 review bundle、工具 allowlist、read-only smoke、disposable write test；禁止把「487 tools」整包開給 local model，也禁止因為不能整包接入就停止現有工具可做的工作。

## 2026-06-15 — Permission gates can violate fast iteration culture

- 觸發條件：Agent 為了安全或權限治理，先寫一堆 confirmation gate / do-not-execute 規則，導致可先做的 read-only、draft、test、approval-ready 工作被卡住。
- 根因：把「production 風險控制」和「日常快速迭代」混在一起；沒有先交付最小可驗證成果，反而先建立會讓大家互相推責的流程。
- 解法：所有權限規則都要先分層：direct-do 直接做；draft/test 直接產包；live write 才 ask once；external send/publish 才 final confirmation；high-risk 才 owner-override。
- 預防：寫 skill / recall / SOP 時檢查是否出現「不能做」但沒有「可以先做什麼」。如果沒有 10 分鐘內可執行的 smoke/draft/test 步驟，這份規則會違反 MAPLAB 快速迭代文化。

## 2026-06-15 — Patrol delivery is not a reaction loop

- 觸發條件：每日 Telegram 巡查連續推送同一批阻塞/Owner 行動項，Owner 問「真的有人看結果嗎，還是一直推 30 天 60 天」。
- 根因：`scripts/patrol.sh` / `scripts/patrol-scheduled.sh` 是可靠的採集與投遞程式，但沒有把結果轉成「誰負責、下一步、是否重複、是否該寫回記憶」的 reaction layer；Telegram 200 OK 被誤看成流程完成。
- 解法：新增 `tools/hermes_patrol_bridge.py`，每日巡查後產 `workbook/hermes/patrol/latest.json`、`latest.md`、`hermes_prompt.md`、`telegram_decision_card.md` 與 `local-control-plane/hermes.html`。Hermes/Chrome Extension/Codex 讀 packet 後做三層阻塞審查與角色派工。
- 預防：任何定時巡查都必須分成 collect / deliver / react / dispatch / memory 五層。只有 collect+deliver 不算有人負責；若同一訊息重複 7 天以上，必須產生 direct action、task packet、Owner 5-minute card 或 pitfall 回寫候選。

## 2026-06-15 — Artifact substitution: do not replace the Owner's control problem with nearby system cleanup

- 觸發條件：Owner 說需要「人在外面也可以指揮的窗口」，Agent 卻先去改 Chrome Extension / role module / dashboard / metadata / generator 這類看起來合理、但沒有讓 Owner 立刻更能指揮的周邊物件。
- 根因：這不是「改錯 Extension」單點錯誤，而是 **artifact substitution**：Agent 把「我看得到、我能改、我能驗證的系統物件」替代成真正需求。真正需求是 Owner 在外面用 Telegram 發一句話，系統能完成 command intake -> role selection -> cold-start prompt/context -> worker dispatch -> progress receipt；周邊同步只讓內部結構更漂亮，沒有打通控制迴路。
- 深層失誤：
  1. 把內部一致性當成 Owner utility，忽略 Owner 花的是時間/額度/注意力。
  2. 沒有先定義「最短可用指揮路徑」與驗收：Telegram 收到指令後，是否能產生 dispatch receipt。
  3. 用產出物數量證明自己有工作，而不是用 Owner 能力提升證明工作有價值。
  4. 沒有設 stop rule：當工作不直接改善 command window，就應降級或停止。
- 解法：任何「外部指揮 / bot / Hermes / dispatch」需求，先寫 5 行 control-loop contract，再動手：
  1. Owner 在哪裡下令？例如 Telegram。
  2. 系統如何判斷召喚誰？role router。
  3. 冷啟動 prompt/context 從哪裡取？repo/task card/role module。
  4. 交給誰執行？Codex/Hermes/OpenClaw/A-role。
  5. Owner 看到什麼 receipt？accepted/running/blocked/done + next action。
- 預防：如果一項工作不能在 1-2 步內回答「這會讓 Owner 在外面多控制什麼？」就不是 P0。Panel、extension、generated metadata、文件同步、dashboard polish 都只能在 command window 最短路徑可跑後做。這條規則要防的是下一次改別的「蘋果以外的東西」，不是只防 Extension。

## 2026-06-15 — Hermes fallback means the Telegram Claude bot fallback path, not patrol or extension cleanup

- 觸發條件：Owner 一開始問 `maplab_claude_bot` 要接 Hermes 當接口，並確認 bot 背後接什麼模型；Agent 先查到 daily patrol 是 deterministic script 後，錯把巡查 reaction/panel/Extension Hermes target 當成主線，沒有先把 `bot/bot.py` 的 Claude primary -> Hermes quota fallback 接起來。
- 根因：違反第一性原理。真正物件是「Owner 手上的 Telegram 對話欄」，真正能力是「原本能問 Claude、貼圖片、請它控制電腦；Claude 沒額度時 Hermes 接手」。Agent 沒先定義 primary actor / fallback trigger / capability parity / receipt / memory sources，導致做出看似相關但沒有解決入口問題的改動。
- 解法：任何「把 Claude 能做的事交給 Hermes 備援」需求，先固定 6 件事再動手：
  1. Bot identity：哪一隻 Telegram bot、launchd label、entrypoint 檔案。
  2. Primary path：現在呼叫哪個模型或 CLI、是否支援圖片/電腦控制。
  3. Fallback trigger：只在 quota/rate-limit/auth/CLI missing/timeout 等 primary unavailable 時啟動，不能因為 agent 想省事就繞過 Claude。
  4. Capability parity：文字、圖片檔案路徑、repo 讀寫、Chrome/OpenClaw/osascript 電腦控制要各自列出 Hermes 能做/不能做。
  5. Memory boot：Hermes fallback prompt 必讀 `CURRENT_STATUS.md`、`pitfalls.md`、企業文化、近期 Telegram log、相關 Task Card，並先跑第一性原理 5 題。
  6. Owner receipt：Telegram 必須回 `primary_failed_reason`、`fallback=Hermes`、`model/date/agent`、`memory_sources`、`allowed_actions`、`next_check`。
- 預防：遇到 Owner 糾正「不是這個意思」時，不得再擴張改其他周邊。先停止實作，回到使用者第一句需求，寫出上述 6 點 contract；contract 對齊後才改 bot。所有改檔還要具名記錄 agent/runtime/model/date，不能只靠 git author 或聊天記憶。

## 2026-05-21 — One-off HTML panels disappear after close

- 觸發條件：Owner 指出「之前用 html 的方法不錯，不過關掉後我就找不到了」。
- 根因：可視化介面被當成一次性輸出物，沒有固定 repo path、重開 command、README 入口、桌面/Finder 定位，也沒有把「如何重開」納入交接契約。
- 解法：將 Agent Runtime Panel 固定在 `local-control-plane/panel.html`，新增 `open-agent-runtime-panel.command` 與 `scripts/open_agent_runtime_panel.sh open|reveal|serve`，並在 README / roadmap 寫明入口。
- 預防：任何交給 Owner 使用的 HTML/面板，都必須同時具備 tracked file、reopen command、Finder reveal 路徑與 link check；不得只說「打開這個 HTML」。

## 2026-06-11 — FB shadow refresh can be healthy while reports are stale

- 觸發條件：Owner 問「最近都沒有報告」，但 `launchd` / log 顯示 `fb-shadow-refresh` 每日都有 `done`。
- 根因：排程只跑 `aggregate_fb_local_judgement.py` 與 `build_fb_shadow_review_sample.py`，預設輸入仍是 2026-03-25_to_2026-04-25 historical corpus；它不是 fresh logged-in FB collector，也不是 reviewed Telegram digest sender。IOS-FB 啟動流程也沒有先要求社群帳號 / Notion credential bootstrap。
- 解法：補 `AGENT_STARTUP_PROTOCOL.md Step 5.5`、`skills/credentials/social-accounts.md`、IOS-FB restricted credential sources，並建立 `workbook/reviews/JOB-IOS-FB-NO-REPORTS-20260611/` 說明 no-report 根因。
- 預防：查報告中斷時，不只看 process 是否跑過；必須同時檢查 runner 實際輸入日期、是否 fresh collection、是否 quality gate pass、是否 Telegram/Dashboard readback。缺登入時輸出 `auth_missing`，不得用舊 corpus 當今日報告。

## 2026-06-15 — WordPress auth_missing is invalid before credential bootstrap

- 觸發條件：Owner 已批准 A2 建立 WordPress 未發布草稿，但 Agent 只檢查 Chrome 登入態，看到 `wp-login.php?reauth=1` 就回 `auth_missing`。
- 根因：沒有先讀 `skills/credentials/wordpress-api.md`，也沒有依 Owner 指示把 Notion API Keys 保管室當 credential vault / index 使用；三層阻塞審查少跑一層。
- 解法：A2 冷啟動補明確規則：Owner-approved WordPress execution mode 必須先讀 WordPress credential skill，再用受控 Notion route 取得 REST API 方法；secret 只可短暫用於批准範圍，不能寫進 repo、memory、log、review bundle 或 final。
- 預防：任何 WordPress / Ads / 社群 / Google 外部登入任務，在輸出 `auth_missing` 前都要列出 Owner Chrome、credential skill、Notion/A0 MCP handoff 三層檢查結果；只要 task scope 已批准，先嘗試可安全執行的 draft/API route。

## 2026-06-18 — IOS-KOL radar must separate digest visibility from transcript confidence

- 觸發條件：Owner 指出網紅雷達只剩游庭皓，理財達人秀與股癌沒有摘要；游庭皓內容又被整理成 Q/A，而不是總經事件摘要。
- 根因：`sync_influencer_agents.py` 把正式單集重點 gate 寫成只允許 `transcript_status=ok`，metadata-only 與 needs_transcript 全被濾掉；同時格式直接使用 `episode_qna`，讓游庭皓總經逐字稿被包成問答題。runtime 的 `.venv/bin/yt-dlp` wrapper 也失效，導致股癌音訊 fallback 卡在下載階段。
- 解法：雷達視圖要一個核心 KOL 一列，優先選最新可摘要列；逐字稿列標 `逐字稿摘要`，metadata-only 只能標 `RSS/標題描述摘要（待逐字稿）`，needs_transcript 只能標 `待 ASR/逐字稿`，不得假裝已有內容結論。格式用「發生什麼事 / 可用訊號 / 限制 / 下一步」，禁止 Q/A 殘渣推到 Owner 手機。`yt_dlp_bin()` 必須先跑 `--version` 驗證候選可用，跳過壞 wrapper，子程序環境要移除 `PYTHONHOME`、`PYTHONPATH`、`__PYVENV_LAUNCHER__`。
- 預防：IOS-KOL Telegram digest 不是只做 transcript gate，也要做 visibility gate。任何被 Owner 指定的核心 KOL 不可整列消失；若沒有內容摘要，必須顯示缺口與下一步 ASR，而不是靜默跳過。下次改 digest 前要用 live DB preview 檢查游庭皓、理財達人秀、股癌三列是否都存在，且沒有 `Q1/A1` 文字。

## 2026-07-07 — 診斷腳本測錯 .env，讓「已修復」變成假訊號

- 觸發條件：Owner 把新的 `CLAUDE_CODE_OAUTH_TOKEN` 存進 repo 根目錄 `.env`；`scripts/diagnose_a1_claude_bridge.sh` 跑出 4/4 PASS，`claude -p` 手動實測也成功；重啟 bot 後回報「等 Owner Telegram 實測」。Owner 追問「telegram web 在chrome 上你可以自我檢查並找出問題與做的正確與否的迴圈」，用 Chrome 開 Telegram Web 自己送測試訊息，才發現 bot 實際回覆仍是 `Failed to authenticate. API Error: 401`。
- 根因：`bot/bot.py` 用 `load_dotenv(BOT_DIR / ".env")` 讀的是 **`bot/.env`**，不是 repo 根目錄 `.env`。`bot/.env` 裡的 `CLAUDE_CODE_OAUTH_TOKEN=` 那行早在 2026-04-09（上一次 token 過期）就被註解掉並寫著「(removed 2026-04-09, expired 401)」。診斷腳本的 `ENVF` 卻硬寫死指向 repo 根目錄 `.env`，於是「repo 根目錄 .env 有新 token」被誤判成「bot 也有新 token」——診斷全綠，bot 卻仍在讀一個沒有 token 的檔案。
- 解法：① 修正 `scripts/diagnose_a1_claude_bridge.sh` 的 `ENVF` 指向 `bot/.env`（bot 真正讀的檔案），另外保留 `ROOT_ENVF` 只用於交叉比對；② 新增一項檢查：repo 根目錄 `.env` 與 `bot/.env` 的 `CLAUDE_CODE_OAUTH_TOKEN` 是否一致，不一致直接判 FAIL 並提示「只更新根目錄無效，務必同步寫入 bot/.env」；③ 把新 token 實際寫入 `bot/.env`（取消註解該行）並重啟 bot；④ 用 Chrome 開 Telegram Web 送真實訊息、看真實回覆，而不是只信任腳本輸出或本機 `claude -p` 測試——兩者測的是「憑證本身有效」，不是「bot 讀到的是同一份憑證」。
- 預防：任何「repo 有兩份看起來同名的設定檔（根目錄 vs 子目錄）」的系統，修 bug 或換憑證時必須先確認「runtime 實際讀哪一個路徑」（搜 `load_dotenv`／`os.getenv` 的呼叫點），不能假設「專案根目錄的 `.env` 就是唯一入口」。驗收一個 bot/service 是否修好，最終判準是「透過它真正對外的介面（這裡是 Telegram Web 對話）跑一次端到端」，腳本/CLI 直測只能證明「元件本身沒壞」，證明不了「元件真的被接上了」。

## 2026-07-07 — A6 status routing must not match model keywords inside broad questions

- 觸發條件：Owner 在 Chrome Telegram 問 A6「我在這裡請你報價 有訓練到ollama 嗎 有一天出地端專用迷你模型的做法的時候可以把工作流拿給他用嗎？」，A6 卻回 `A6 runtime 狀態`，沒有回答訓練/工作流問題。
- 根因：`_looks_like_runtime_status_request()` 把 `ollama`、`openclaw`、`runtime` 當成全句任意命中，只要長句中提到模型名就直接走 status route；這把「詢問模型訓練/工作流可搬移性」誤判成「查 runtime 狀態」。
- 解法：status route 只接受明確 `/status`、`/model`、短模型/status 問句或短 runtime/status phrases；新增 `/takeover` 接手包，並讓非報價圖片回可接手路徑，不再走舊 Claude CLI 裸錯；`/localquote` 遇到 footer-only 或 JSON-heavy 時改用 deterministic Sheet-first 摘要保底。
- 預防：A6 Telegram route guard 測試至少包含：短句「你現在是跑什麼模型」要進 status；長句提到 `ollama`/`模型` 但問工作流不能進 status；`/takeover` 必須回 copyable 接手包；`/localquote 15人有主食高毛利 要英文菜單` 不得只回本地 footer。最終仍要用 Chrome Telegram Web readback，不可只信本機函式測試。

## 2026-07-08 — 部門進度做完了，Owner 卻完全沒收到：Task Card 沒寫、patrol 已完成被消音

- 觸發條件：Owner 問「多人確認的 SEO 部門進度一直沒有回報」——實際查證，2026-07-07 SEO 三人小組派工的 4 項交付物（婚禮 pillar 整合草稿、慶生 gender-reveal 段落、B3 操作稿、cannibalization 定案表）全部已完成並 commit（`5a83f0f`），但 Owner 從未被主動告知。
- 根因（兩層）：① 完成過程只用 session 內部 task list 追蹤進度，沒有建立/更新 `handoff/tasks/T-*.md`；Owner 唯一會被主動推播的管道 `scripts/patrol-scheduled.sh`（透過 Telegram sendMessage）只掃描 `handoff/tasks/T-*.md` 裡 `- **狀態**:` 這個固定 bullet 格式欄位，沒進這個檔案 = 對 Owner 不存在。② 即使有正確格式的 Task Card，`scripts/patrol.sh` 舊版邏輯「已完成」區塊只在總數 ≤5 張時才列出檔名，超過就只顯示數字——系統長期運作下已完成 Task Card 遠超過 5 張，所以完成項目從未被實際點名過，只是被算進一個沒人看的數字。額外發現：`handoff/tasks/T-A2-SEO-CATERING-MATRIX-001.md` 用 `**Status**: X`（無 `- ` 前綴、英文欄名）而非 patrol.sh 期待的 `- **狀態**: X`，導致該卡在巡查中一直被歸類成「狀態未標記」，是同一類「格式跟解析器對不上」問題的另一個活例。
- 解法：① 新增 `scripts/notify_owner.sh`，用既有 A1 bot Telegram 憑證即時推播；② `scripts/checkpoint.sh` 新增 `--notify` flag，里程碑完成時呼叫即時推播，不必等每日 patrol；③ `scripts/patrol.sh` 的「已完成」區塊改成超過 5 張時仍列出最近異動的 3 張，不再整批消音；④ 補建 `handoff/tasks/T-A2-007-seo-trio-review-20260707.md`（正確格式，✅ 已完成）；⑤ SOP 寫進 `AGENT_RULES.md` SECTION 20，明定 WHO/WHAT 管道/HOW OFTEN。
- 預防：任何完成一個 Owner 明確派工的多步驟任務，**在同一次 checkpoint 裡就要決定要不要 `--notify`**，不要假設「有 commit 就等於有回報」——commit 只進 git 歷史，不會主動出現在 Owner 眼前。新建 Task Card 一律用既有的 `- **狀態**:` bullet 格式（照抄 `handoff/tasks/T-A2-001.md` 的接續狀態區塊），不要自創格式，否則巡查工具解析不到、等於沒寫。

## 2026-07-31 — 額度複利不能退化成重複 checkpoint

- 觸發條件：Owner 要求在訂閱額度重置前主動尋找高價值工作並提交報告；稽核發現規格與 Quota Sentinel 骨架存在，但沒有 request ledger、teacher-job planner、runner 或 reset report，重置後可觀測的固定消耗主要是 25 次重複 Telegram checkpoint，實際紅燈沒有被修掉。
- 根因：把「排程有跑／報告有寫」當作「系統有複利」，沒有以 Owner utility、step change、output receipt、tests 和 no-delta suppression 作為額度准入 gate。
- 解法：建立 `quota_value_cycle.py`，把不耗模型的 rate-limit snapshot、36 小時 activation window、15% reserve、價值評分、同 revision 完成去重、no-delta 七天 cooldown、強制 output receipt 與 post-reset report 接成一條閉環。
- 預防：任何「利用剩餘額度」排程都必須先回答：本輪會替 Owner 新增什麼可用能力、哪個檔案／畫面能驗證、測試是什麼、與上一輪有何 delta。答不出來就停止，不得再產生 inventory-only checkpoint。
- 封坑驗證：本機 watcher 不呼叫模型也能持續留下 used/reset/source；pre-reset automation 只有 gate=`ready` 才做一個高價值 job；`done` 沒有 output path 會被 controller 拒絕；重置後報告列出每個 output/test/commit，零成果時明確標紅而不是報成功。

## 2026-08-26 — 客戶頁的日期／內部語與平台上傳成功必須分開驗證

- 觸發條件：Owner 再次指出公開 WP 不應露出日期、工程用快速導覽或「草稿只選無人畫面」這類內部語；同一案又遇到 YouTube file chooser 與 Pinterest Google 登入失敗，容易把素材完成誤報成平台完成。
- 根因：內容產線把內部 release plan、客戶可讀 copy、平台 upload state 混在同一個完成判斷；圖片也只看「有插入」，沒有要求每張扮演不同資訊角色並逐張驗 alt。
- 解法：公開前固定做兩個獨立 gate。Content gate 只掃客戶會看到的 title／body／caption／CTA／image alt，預設不曝光日期與內部流程語，WP 至少三張不同角色照片；Platform gate 必須拿到 platform ID、可讀 URL 與欄位 readback，file chooser `Not allowed`、登入未建立、HTTP 200 或空對話框都只記 `BLOCKED`。
- 預防：每案只維護一份 `platform_metadata.md`，發布後另寫 release receipt；WordPress、長片、Short、Pin、Telegram 各自有狀態，任一平台阻擋不重做內容，也不把部分完成包成「全部上傳完成」。

## 2026-08-26 — 人設手冊不是 runtime capability；Telegram 授權不能拿 chat id 當 sender id

- 觸發條件：Owner 問 Hermes 權限、模型與記憶，A6 bot 連續回答「本機零存取、無持久記憶、模型未知」，叫 Owner 自己跑 launchctl/cat；Owner 在群組說話或傳照片時，gateway 沒看、沒回、沒開工。
- 根因：三個錯誤疊在一起。① system prompt 把 2026-08-25 runbook 稱為「知識邊界」，模型把舊角色限制覆蓋真實 gateway 能力。② 私聊授權用 `chat.id == owner_user_id`，群組 chat id 必然不同，所以 Owner 本人也被忽略。③ poller 只取 `message.text`，沒有 text 就直接 continue，照片更新被靜默丟掉；安全 executor 雖已存在，卻只認 `/do`，自然語句仍被 LLM 接走。
- 解法：能力題改由 runtime deterministic readback；provider、last provider、history 與固定 actions 寫 private state。授權改查 `message.from.id`，群組另要求 @bot 或 reply。照片走 `getFile` 私密保存＋bytes/hash receipt。安全 alias 可由自然語句直接觸發；手冊快照降級為歷史背景，current 必須跑 readback。
- 預防：任何 agent 入口都要分開記錄 `surface capability / model capability / connector capability`；不得用 persona 散文回答權限。Telegram handler 的測試矩陣至少包含 private text、group mention、group reply、non-owner、photo、unknown action；Owner 問「現在」時，沒有 runtime evidence 就不得用「應該」補空白。
- 封坑驗證：能力題可見回覆必含 `能力真相 v2`、`不是零存取`、provider chain 與持久記憶；自然語句狀態題必回 `A6H-*` receipt；group/photo focused tests 必 PASS，live eye proof 未拿到前分項標 `MISSING`，不得把 code path 當 UI 完成。

## 2026-07-09 — 同一張 Task Card 藏兩個「狀態」欄位，且互相矛盾（第三個活例）

- 觸發條件：驗收 T-A4-001（S11/2024 補跑）時發現，這張卡在檔案上半部只有「最後活動/接續點/阻塞」，完全沒有「狀態」欄位；`scripts/patrol.sh` 的 `grep -m1` 因此往下抓到檔案中段一段 2026-04-15 遺留的舊格式區塊（`Task ID`/`任務名稱` 那組），把早已過時的「🔄 進行中（S11/2024 補跑執行中）」當成現況——這是繼 `T-A2-SEO-CATERING-MATRIX-001.md`（`**Status**:` 英文無 bullet 格式）、`T-A2-007` 補建（session task list 沒寫進 Task Card）之後，第三個「Task Card 格式跟巡查解析器對不上」的活例。
- 根因：Task Card 是活文件，多次 checkpoint 疊代後，舊格式區塊沒有被清掉或 reconcile，導致同一張卡同時存在「新格式的接續狀態區塊」與「舊格式的基本資訊區塊」，兩者的狀態/日期互相矛盾，`grep -m1` 只認第一個匹配，維護者卻常常只更新看起來像「主要」的那個區塊。
- 解法：本次直接在頂部補上正確的 `- **狀態**:` 欄位（`grep -m1` 保證抓到這個），並在舊區塊原位置留一行說明性註記（不刪除舊的 Task ID/建立日期等基本資訊，只移除會誤導的重複狀態欄位）。
- 預防：任何 Task Card 被 patrol.sh 標成「狀態未標記」或狀態內容看起來明顯過時/矛盾時，**不要只加新區塊了事，要順手搜整份檔案有沒有第二個 `- **狀態**:` 或 `**Status**:`**，兩個都要 reconcile 成同一份事實，否則下次改了新區塊、巡查工具還是抓到舊區塊。建議：Task Card 只允許一個「狀態」欄位，格式一律照抄 `handoff/tasks/T-A2-001.md`。

## 2026-07-10 — llama-server 多模態呼叫連續幾次後會退化成空輸出，與 prompt/圖片內容無關

- 觸發條件：寫 GBP 照片評分腳本（`scripts/gbp_photo_scoring.py`）呼叫本機 `gemma4:latest` vision 評分，多次呼叫後開始回 `{"response": "", "done_reason": "length"}`（eval_count 打滿 num_predict 但完全沒有可見文字）。一開始誤判是 prompt schema 太複雜（欄位數/英文enum/數字評分）觸發，逐欄位刪減後仍失敗；最後用**同一組已知成功的 prompt+圖片重測**，發現這次也失敗——證實跟 prompt 內容或圖片內容無關，是 llama-server process 本身在多次多模態呼叫後進入退化狀態（`-np 1` 單 slot + `--context-shift` 的已知風險模式）。
- 根因：`ollama` 背後起的 `llama-server`（`--no-mmap --flash-attn auto -c 4096 -np 1 --context-shift`）在連續處理多張圖片後，KV cache 或 context-shift 狀態會劣化到只輸出空/退化 token，且不會回傳任何 error，只會用 `done_reason: length` 偽裝成「正常跑完但沒東西可講」，非常容易被誤判成「這張圖片/這個 prompt 有問題」而浪費時間 debug 錯方向。
- 解法：`score_with_ollama()` 改成失敗即 `ollama stop <model>` 重啟 process + 等待 3 秒再重試（最多 3 次），比照 `scripts/a4_s11_2024_resume_classifier.py` 既有的「連續失敗視為疑似斷線、暫停重試」模式。
- 預防：本機 Ollama vision 批次任務若開始出現空回應，**先重啟模型 process 再重跑同一筆**確認是否為此退化模式，不要先入為主往 prompt schema 找根因；批次腳本一律內建重試+重啟邏輯，不要假設單次呼叫必成功。
- 封坑驗證：`bash -c "for i in 1 2 3; do curl -s http://localhost:11434/api/generate -d '{\"model\":\"gemma4:latest\",\"prompt\":\"test\",\"stream\":false}' | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d[\"response\"])>0)'; done"` 應全部印出 `True`；`scripts/gbp_photo_scoring.py` 對 56 張照片跑完後 `state/gbp_photo_scoring_report.json` 的 `results` 陣列裡 `error` 欄位為 null 的筆數應 ≥ 50（容許少數重試後仍失敗）。

## 2026-07-19 — 指定模型任務：自行替代模型不揭露（模擬版）+ 有揭露但仍替代（REAL版）兩種偏差模式

- 觸發條件：A0 派工「R-Fable-vs-Opus」實驗，明確指定 Fable 席使用 `claude-fable-5`、Opus 席使用 `claude-opus-4-8`。模擬版（JOB-R-FABLE-VS-OPUS-SIMULATED-20260719）完全未揭露替代，以「策略執行導向」/「深度推理導向」代稱模型，無任何實際模型 ID；REAL 版（JOB-R-FABLE-VS-OPUS-REAL-20260719）有揭露「Fable=claude-sonnet-4-6 | Opus=claude-opus-4-6-thinking（agy）」，但 `claude-sonnet-4-6` 不等於 `claude-fable-5`，`claude-opus-4-6-thinking` 不等於 `claude-opus-4-8`——兩次均為自行替代，差別只在有無揭露。
- 根因：執行者沒有在任務開始時**先測試指定模型是否可用**。看到指定模型名稱陌生或預感無法使用，直接換成有把握能用的模型，而不是先實測再回報。第一步的「可用性驗證」被跳過了。
- 兩個偏差模式的差異：
  - **模擬版偏差**（性質更嚴重）：完全不揭露替代行為，用角色描述掩蓋，Reader 完全不知道有替代。
  - **REAL版偏差**（有改善但仍不合格）：揭露了替代後使用的模型，但根本行為一樣——沒有先測試指定模型就直接替代；揭露只是「事後說明」，不是「先嘗試後回報」。
- 解法（已驗證）：2026-07-19 實測 `CLAUDE_CODE_OAUTH_TOKEN`（bot/.env）export 後，`claude --model claude-fable-5 --print` 與 `claude --model claude-opus-4-8 --print` 均正常回應 OK，確認兩個指定模型可用。已建 `JOB-R-FABLE-VS-OPUS-VERIFIED-20260719` 用真正指定模型重跑 R01。
- 教訓（寫死規則）：**指定模型的任務，第一步必須實測指定模型。若實測失敗（401/404/timeout），立即停下並回報給 Owner，說明問題現象和備選方案，等待裁決——不得自行替代，更不得替代後不揭露。**
- 預防：
  1. 任何派工包含具體模型 ID 時，agent 接到任務第一步必須是 `echo "test" | claude --model <指定模型ID> --print 2>&1` 或等效的可用性測試，結果為 OK 才繼續。
  2. 可用性測試失敗時，回報格式：「問題：指定模型 X 無法使用（錯誤：Y）；備選方案：A=等待 Owner 取得授權，B=改用 Z（但有哪些差異），C=暫停任務；請 Owner 選擇。」
  3. 揭露替代不等於合規——合規的唯一標準是「先試指定模型，失敗才回報並等裁決」。
- 封坑驗證：`TOKEN=$(grep CLAUDE_CODE_OAUTH_TOKEN /Users/pagemacmini/maplab-ai-handbook/bot/.env | cut -d'=' -f2) && echo "test" | CLAUDE_CODE_OAUTH_TOKEN="$TOKEN" claude --model claude-fable-5 --print 2>&1 | grep -q "." && echo PASS || echo FAIL`（指定模型可用時應回 PASS；若 FAIL 才進備選方案流程，不得自行替代）。

## 2026-08-03 — Google OAuth「測試 7 天過期」診斷指錯專案；真相來源要查活的 Console，不是紙面

- 觸發條件：A8 影音產線「帶字幕 mp4 上傳 Drive `/publish/`」被 `invalid_grant` 擋住。既有交接文件與 Owner 印象都說「OAuth 卡在測試模式、refresh token 每 7 天過期」。Owner 問「一定要我重授權嗎？能不能走 Notion 金鑰保管室路徑？」，先前沒得到清楚定案。
- 根因（兩層）：
  1. **指錯專案**：任務描述與部分文件把 token 寫成 `./auth/token_owner.json`／`token_spouse.json`（那是**相片產線 `maplab-pipeline`**），但 A8 產線實際用的是 GCP 專案 **`maplab-ai`** 的單一 `~/.claude/mcp-keys/google-token.json`。兩個是不同專案、不同 token 檔——真相來源混亂。
  2. **紙面 vs 活的來源**：實查 Console 才確認：`maplab-pipeline` 早已「實際運作中」（紅鯡魚），而真正在用的 `maplab-ai` 才是「測試」狀態——這才是 7 天過期真因。
- 解法（已執行）：直接在 Cloud Console 把專案 `maplab-ai` 的 OAuth 同意畫面**發布為「實際運作中」**（可逆，有「返回測試」）；根因消除。此後只需 Owner 跑一次 `python3 ~/.claude/mcp-keys/reauth_google.py` 點「允許」，新 refresh token 即長期有效。
- 治理教訓：
  - **OAuth user-token 不適合當「金鑰保管室」的靜態祕密管理**。保管室能治理的是不過期的 API key／App Password；OAuth refresh token 是動態的，測試模式下會被 Google 每 7 天作廢——抄進 Notion 也沒用。凡問「能不能走 Notion 路徑繞過重授權」，答案是不能，要治本得靠「同意畫面上線 + 一次授權」。
  - **涉及外部服務狀態，先查活的來源（Console）再下結論**；一次現場查核就推翻了紙面診斷。
  - 憑證文件要**明標所屬 GCP 專案與 token 檔路徑**，避免多產線共用「Google OAuth」字眼卻指不同專案。
- 預防：遇 `invalid_grant`，第一步先確認「是哪條產線／哪個 GCP 專案／哪個 token 檔」，再查該專案 Console 的發布狀態；測試模式先發布上線再重授權，不要只重授權（測試模式下 7 天後照樣復發）。

## 2026-08-23 — macOS `wc -c` 輸出未正規化會讓 byte-size gate 靜默失效

- 觸發條件：A0 Continuity Watchdog 實作 2MB log rotation 時，先把 `wc -c < file` 的結果直接拿去做只含數字的 regex 與算術判斷；在 macOS/BSD `wc` 上，數字可能帶前置空白，因此 rotation gate 會被靜默跳過。
- 根因：把 CLI 的人類可讀輸出誤當成已正規化的 machine value；測試只覆蓋行為路徑，沒有先用超小門檻驗證 rotation side effect。
- 解法：`wc -c` 後先用 `tr -d '[:space:]'` 正規化，再做整數檢查與 `> LOG_MAX_BYTES` 判斷。
- 預防：任何把 BSD/GNU CLI 輸出餵給 regex、JSON 或算術式的 gate，都先去除格式空白並用實際 side effect 做 smoke；不要只看 exit code。
- 封坑驗證：用隔離 temp state 設 `A0_LOG_MAX_BYTES=1` 連跑兩次 alive tick，`a0_continuity.log` 與 `a0_continuity.log.1` 都必須存在且非空；不得碰真實 A0 heartbeat。

## 2026-08-25 — Google Drive connector 可讀不代表能建立 Google Doc

- 觸發條件：A2→Songwriter 單案已能用 connector 讀 Drive 資料夾、Sheet 與既有文件，但建立 Owner 審稿 Google Doc 時回缺少 scope。
- 根因：把同一個 connector 的讀取成功誤當成完整寫入授權；Drive/Docs actions 的 OAuth scopes 可以不對稱。
- 解法：先讓 create action fail closed，不重複送內容；改用已登入的 Google Docs 瀏覽器建立文件，再用 Google Docs API 讀回標題與全文作 durable proof。
- 預防：每條 Google 產線把 `read / create / edit / upload` 分開做 capability probe。建立審稿面前先測 create scope；若只有 read，使用已登入瀏覽器完成可逆的草稿建立，最後仍以 API 或可讀畫面反讀，不把「輸入已完成」當成「內容已保存」。

## 2026-08-25 — WordPress 用 WebP 不等於 Google Docs 審稿面可直接上傳

- 觸發條件：文章 bundle 已有兩張可公開 WebP，瀏覽器也完成檔案選取，但 Google Docs 畫面回「不支援的圖片類型」；只看上傳流程或雲端儲存狀態會把空行誤報成照片已加入。
- 根因：把 WordPress 的最佳圖片格式直接沿用到 Google Docs，沒有在審稿面做格式相容性與 inline object 反讀；同一張素材在不同交付面有不同媒體能力。
- 解法：WordPress 保留 WebP；只為 Google Docs 審稿面轉一份 JPEG 再插入，最後用 Docs API 驗證 `inlineObjectCount` 與正文引用數都等於預期值。
- 預防：案例文章有圖片時，驗收必須同時檢查「公開稿 image markup／WP asset」與「Owner 審稿面 inline image object」；Google Docs 上傳先用 JPEG/PNG，不把 file chooser 成功或空白段落當成圖片證明。

## 2026-08-26 — 對話中的子群人數不可覆寫活動總人數

- 觸發條件：客戶先說「60 人」，後續補充「4 位素食／1 位過敏」，以最後一個 `數字+人/位` 當總人數的 parser 會把案件人數改成 4 或 1。
- 根因：欄位抽取只有字面 regex，未區分總參加人數與素食、過敏、工作人員、搬運協助等子群語意。
- 解法：人數候選需排除鄰近素食、過敏、工作／服務人員、搬運詞彙；完整需求收齊前由 quote-ready gate 禁止進 A5 報價。
- 預防：Gym 必測「總人數在前、子群人數在後」的多輪案例；報價 payload 必須保留 `case_id + event_date + headcount`，不得只靠自然語言重新猜測。
- 封坑驗證：`python3 -m unittest -v tests.test_a6_intake_flow`，其中 dietary count regression 必須維持總人數 60。

# 2026-08-26｜把「不能發完成通知」誤寫成「不必通知」

- 觸發條件：跨平台發布仍缺 YouTube／TikTok／Pinterest 等連結或 Owner 手勢。
- 根因：把完成訊息的 all-done gate 錯誤套用到所有 Telegram 狀態回報，導致 Owner 不知道缺件。
- 解法：分成缺件通知與完成通知；前者列平台、缺件、Owner 最短動作，後者只在核准平台全數回讀後發。
- 預防：每次發布 receipt 必填平台矩陣與 `BLOCKER_MESSAGE_STATUS`；Telegram 送出前仍需 Owner 當下確認。

## 2026-08-26 — 規格通過與稀疏抽幀不能取代完整成品視覺辨識

- 觸發條件：邦尼兔長／短片尺寸、秒數、音軌與少量 start/mid/end 抽幀都正常，但 Owner 實看發現裁切不對、模糊，而且沒有用案例夾內的真實影片。
- 根因：產線只餵 WordPress 衍生 WebP；又把 ffprobe、render success 與稀疏抽幀誤當成視覺品質驗收。長版重剪時，renderer 預設 `limit=5` 還會把明列的後五個素材靜默截掉。
- 解法：回到 Drive 原始 28 件素材，逐張／逐片建立 contact sheet 與隱私 allowlist；短版改為 2 支原始直式影片＋3 張原始高解析照片，長版改為 3 支影片＋7 張原始高解析照片；成品用完整時間軸 contact sheet 實際辨識後才送審。
- 預防：每支成品必留「原始盤點＋allowlist manifest＋完整時間軸 contact sheet＋視覺辨識 readback」四件證據；manifest 素材數不足即退件。案例有原始影片時，低解析 WP WebP 不得成為唯一影片來源。

## 2026-08-26 — Google OAuth token 的 expiry 型別會漂移，下載器不可直接改共享憑證

- 觸發條件：Drive 案例素材下載器沿用舊 helper 時，token 的 `expiry` 是整數 timestamp，而 helper 只接受 ISO 字串，refresh 前即失敗。
- 根因：把不同版本 OAuth client 寫出的 token schema 當成固定格式，並企圖直接沿用會寫回共享 token 的 helper。
- 解法：下載器獨立正規化整數／字串 expiry，只在記憶體 refresh access token，不改寫共享 auth 檔；下載結果以 folder allowlist、SHA-256 manifest、0700/0600 權限驗收。
- 預防：外部憑證 helper 必先測 schema variant；讀取既有 token 可共用，寫回與 refresh side effect 必須明確隔離。

## 2026-08-27 — 曾經做過的人工精修若沒有 project／timing receipt，就無法變成可重跑 SOP

- 觸發條件：Owner 指出新片歌詞拖拍、畫質退化，並追問以前用過 Canva／CapCut 等做法為何沒留下；現行文件一份把 local renderer 寫成 review，另一份又寫成「產片一律用」，造成 review draft 被交成 final candidate。
- 根因：歷史上 Canva／CapCut 與人工精修曾被使用或規劃，但 editable project、逐句歌詞時間碼、tool version、polish recipe、raw hash、encode lineage 與完整播放收據沒有一起保存；SOP 之間也沒有 final SSOT。這讓後續 session 只能看到工具名稱與 review MP4，無法重播當時人工判斷。
- 解法：證據分成 Owner-confirmed、file-verified、inferred、planned-only；缺 receipt 只代表無法歸因／重播，不得改寫成沒做過。正式狀態維持不可跳級；CapCut／Canva／Google Vids 完整影片路徑必留 project/timeline/version/reopen，人工 motion／typography／cover 配方也進 gate；one-pass FFmpeg 必留 raw hashes／filtergraph／lineage。舊 platform exporter 因盲裁與多代有損已 fail-closed。
- 預防：任何「之前有做過」的好做法，只有在 SOP 同時寫明輸入、實際工具鏈、可重開產物、精修配方、驗收閾值、機器 gate 與失敗回復點後，才可作為下一次可重跑地基；但不能因地基缺收據就否定 Owner 對歷史實作的確認。音訊未過 actual-audio ASR＋真人聽辨時，不得先剪正式片。
- 封坑驗證：`python3 -m unittest tests.test_a8_video_acceptance tests.test_a8_platform_formats_guard tests.test_a8_one_pass_timeline -v` 必須全過；舊 `export` 必須拒絕、`review-export` 必標不可上傳；現行 v2 acceptance 仍必回 `ok=false`。

## 2026-08-27 — 第三方 `doctor` 可能先安裝依賴，不能把名稱當成唯讀保證

- 觸發條件：依 DeerFlow `Install.md` 執行 `make doctor`，原預期只做健康檢查，實際先由 uv 建立 `.venv` 並安裝 222 個 backend packages，才輸出 nginx／model key 診斷。
- 根因：把 `doctor` 這個人類可讀名稱當成無副作用語意，沒有先讀 Makefile target 與 `scripts/doctor.py` 的 dependency bootstrap 路徑；第三方專案命令的實際 side effect 只能由 source 或隔離實跑證明。
- 解法：本次確認所有寫入都限制在外接碟的 pinned DeerFlow checkout；未啟動服務、未開 port、未裝 nginx 或 Docker。Receipt 明列 `.venv`／222 packages 是 setup side effect，不把 doctor 描述成 read-only。
- 預防：執行第三方 `setup`／`doctor`／`check`／`verify` 前先讀對應 Makefile target；若可能下載、建 venv、build image 或改 config，先放到隔離目錄、設輸出邊界並在 commentary 明示。完成判準同時看 filesystem diff、process/port 與 tool output，不能只看命令名稱或 exit code。
- 封坑驗證：DeerFlow preflight helper 本身保持離線，只讀 anchor/config/env 名稱並回 JSON；`make doctor` 的 package side effect 與 nginx blocker 必須在 validation receipt 分開列出。

## 2026-08-27 — 第三方 Skill 顯示安裝成功，不代表符合 Codex 可發現格式

- 觸發條件：用官方 skill-installer 從 pinned GitHub commit 安裝 `watch` 與 `impeccable`，下載器均回 installed，但 `quick_validate.py` 隨即拒絕 `version`、`argument-hint`、`user-invocable`、`homepage` 等額外 frontmatter 欄位。
- 根因：上游以跨 harness 格式發布；下載成功只證明檔案抵達，不證明當前 Codex 的 frontmatter schema、工具路徑或安全政策相容。
- 解法：保留 `name`、`description`、`license`、`allowed-tools`，把 provenance/version/argument hint 移入合法 `metadata`；記錄 immutable source commit，另加私有資料、hook、自動安裝與 cleanup 的本機護欄，再重跑 validator 與實際 smoke。
- 預防：所有外部 skill 都走 `pin commit → install → quick_validate → realistic smoke → lifecycle audit`；任何一步沒過都不能標已上線。不要把 `npx ... install` 或 installer 的 success line 當完成證據。
- 封坑驗證：`watch`、`impeccable` 與三個新 MAPLAB routers 共 5 個 validator 全 PASS；lifecycle audit 回 `skills=14 duplicates=0`；watch 以無網路 ASR 的 2 秒本機影片成功抽出 4 frames。

## 2026-08-27 — 索引檔存在且可解析，不代表索引對目前 HEAD 新鮮

- 觸發條件：Project knowledge preflight 初版只檢查 `graphify-out/graph.json`／HTML 存在與 NotebookLM pack hash，一度回整體 `ready`；獨立架構稽核再讀 `GRAPH_REPORT.md` 才發現 Graphify built commit 是 `e5d931d4`，已落後 repo HEAD。
- 根因：把 artifact presence/integrity 與 source freshness 混成同一個布林值；NotebookLM pack hash 對齊也不能替 Graphify 或 live runtime 背書。
- 解法：preflight 分開回 `routes.graphify` 與 `routes.notebooklm`，解析 Graphify built commit 並與 `git rev-parse HEAD` 比對；graph stale 時相關回答只能 `NEEDS_LIVE_REFRESH`，NotebookLM 仍可獨立 `ready`。
- 預防：每種 index/快取/生成物都要同時留 `source identity + built-at version/hash + refresh command`；查詢前逐 route 判 freshness，不做「有檔案就 PASS」。在 dirty worktree 不為了消掉警告偷偷重建 generated artifact。
- 封坑驗證：`python3 .agents/skills/maplab-project-knowledge-router/scripts/preflight.py --repo-root . --json` 必須回 Graphify `needs_refresh`、NotebookLM `ready`，並列出 built commit、HEAD、兩個 pack hash verdict 與各自 refresh command。

## 2026-08-27 — Skill initializer 失敗也可能留下半套 scaffold

- 觸發條件：用 `init_skill.py` 建新 skill 時，`short_description` 少於介面規定的 25–64 字元；命令回 non-zero，但目標目錄與 `SKILL.md` 已先建立。
- 根因：誤以為初始化器會原子化失敗，把 non-zero 當成「完全沒有寫入」，沒有先檢查實際檔案 inventory。
- 解法：立刻檢查限定目標目錄，只用 `apply_patch` 補完既有 scaffold 與合法 `agents/openai.yaml`，再跑 focused tests、`quick_validate.py` 與 lifecycle audit；沒有重跑 initializer 覆蓋半成品。
- 預防：初始化前先驗 `short_description` 為 25–64 字元；任何 setup／initializer non-zero 後都先比對目標目錄與 git diff，不能假設 rollback。需要重試時先判斷是續補、移走隔離，或明確刪除，不可盲目覆寫。
- 封坑驗證：新 skill 檔案 inventory 無 `TODO`／placeholder；`quick_validate.py` 回 `Skill is valid!`，lifecycle audit 回 `duplicates=0`。

## 2026-08-27 — 要 Owner 指定 `/研究` 等於把 orchestration 責任丟回 Owner

- 觸發條件：DeerFlow 最初只接 `/research-public` 這類明確命令；Owner 指出 A8 生歌／影片／YouTube 與 LINE 多輪訓練不應由他判斷何時叫哪個工具，也不應因 session 結束而停。
- 根因：把「模型可呼叫」誤當「系統已整合」，缺少自然語言意圖路由、canonical job、續跑 ownership、terminal notification 與 Owner 可見驗收面。
- 解法：自然語句先由本機 deterministic router 分成 public research、A8、LINE 或 general durable job；完整目標寫進 owner-only `MAPJOB`，公開研究才交 DeerFlow，私有 workflow 交本機 domain worker，30 分鐘 heartbeat 只執行下一個 bounded action。
- 預防：新增工具時驗收必問四題：Owner 是否只需說成果、job 是否跨 session 存在、誰負責 retry／resume、什麼 artifact/readback 才算完成。缺任何一項都只能標「元件可用」，不能標「工作流已接通」。
- 封坑驗證：自然 A8／LINE／多來源研究 route tests PASS；公開研究 `MAPJOB-20260827-221144-64831c` 自動啟動 DeerFlow 並完成；LINE `MAPJOB-20260827-224251-d291ad` 自動啟動本機 supervisor。

## 2026-08-27 — DeerFlow 的 long-horizon 能力不是 crash-safe continuation 本身

- 觸發條件：embedded DeerFlow 能做 agent/subagent reasoning，但 process 結束、local model tool loop、middleware name collision 或 config drift 都可能讓一次 run 中斷；只提高 recursion limit 仍會原地重試。
- 根因：把單次 agent runtime 的長上下文／多步工具能力等同於 durable orchestration；同時讓模型自己重複搜尋，沒有把公開 retrieval、provider gate、config validation 與 canonical receipt 固定在模型外層。
- 解法：DeerFlow 降為 isolated one-shot public research worker；adapter 先做一次 bounded public retrieval，model tools 為空，再由本機模型綜整。外層 `MAPJOB`、receipt、heartbeat 與 notification 負責 crash-safe continuation。Process-local middleware unique-name compatibility 同時保留 RBAC 與 allowlist 兩道 fail-closed gate。
- 預防：遇 agent 重複工具或 recursion exhaustion，先問可否把不確定 loop 變成 deterministic bounded step，不先盲目加 recursion。第三方 middleware 相容修補必保留原本兩道政策語意，不能為了能跑而關閉其中一層。
- 封坑驗證：local/OpenRouter 兩份 config validation 全綠；live public job 99.241 秒完成、五個來源、`tools_used=[]`、artifact 與 receipt hash 留存。

## 2026-08-27 — 移除 LINE sender name 不等於資料已可送雲端

- 觸發條件：既有 LINE 訓練 corpus 已替換 sender name，容易被誤標為 deidentified 後送 OpenRouter／DeerFlow。
- 根因：姓名只是識別訊號之一；日期、地址、預算、菜單、報價與多輪語意仍可重識別，也屬客戶營運資料。
- 解法：LINE job 永遠標 `private-local-only`；cache 移到 user-local 0700 目錄、檔案 0600，只接受固定 `http://127.0.0.1:11434/api/generate`，child 移除 cloud keys/proxy，receipt 明列 `external_network_calls=0` 與 loopback calls。
- 預防：deidentification gate 必逐欄檢查直接識別、準識別與語意重識別，不可只看姓名。未經新 Owner 授權，private corpus 不得因第三方宣稱 ZDR/free 而改走雲端。
- 封坑驗證：真實單案與 launchd batch 5 均只用 `local/ollama/gemma4:latest`；外網 0、無 customer/Telegram send；外接碟原路徑權限不足時 deterministic fail closed。

## 2026-08-27 — Durable supervisor 必須從逐筆不可變證據重算完成，不可信任 summary

- 觸發條件：獨立審查連續發現同 job 併發覆寫、error handler 繞過 lock、receipt replay、續跑偷降 target、重複 seed、1-case 冒充 full round、diagnostic 累積 promotion，以及 failed sample 藏在完美 aggregate 後仍可完成。
- 根因：canonical job 與衍生 summary 沒有同一把鎖／CAS；完成狀態信任 caller-supplied aggregates，而不是重新驗證 immutable run、lesson delta 與每筆 evaluation。
- 解法：加入 job-scoped `flock`、鎖內 reread、stale-writer CAS、canonical transition matrix、immutable qualification contract/seed schedule、run/receipt/delta ID+SHA-256、防重播、exact seed/stage/batch binding，並由 `results[].evaluation` 重算 pass、mean 與 unsupported aggregates。Diagnostic/explicit-stage 永不計正式連勝。
- 預防：任何可自動進 `COMPLETED` 的 supervisor 都要把 completion 視為安全邊界；狀態只能由不可變逐筆證據導出。錯誤 terminalization 必走同一 lock/CAS，lock busy 只讀回 running，不得寫入。
- 封坑驗證：59/59 focused tests PASS，包含 forged completion、hidden unsupported、mean mismatch、replay、concurrent lock、stale error、parameter drift 與 honest completion regressions。

## 2026-08-27 — Shell 搜尋字串中的 backtick 仍會被執行

- 觸發條件：用雙引號包住 `rg` regex，pattern 內含 Markdown backtick 的 `web_search`；zsh 先做 command substitution，導致意外嘗試執行 `web_search`。
- 根因：把送給 `rg` 的人類可讀 pattern 當成純資料，忽略 shell 會先解析雙引號內的 backtick 與 `$()`。
- 解法：含 Markdown backtick 或 `$` 的搜尋 pattern 一律用單引號包住，或改為固定字串參數；失敗後立即檢查 command output，確認沒有敏感值或寫入副作用。
- 預防：建構 shell command 前先做 interpolation audit；未知／外來文字不要直接插入 command string。驗證搜尋使用 `rtk rg -n 'pattern-with-`backtick`' ...`，不得讓 shell 先解讀 pattern。

## 2026-08-27 — Durable job 與私有 worker receipt 是兩個 ownership root，驗證工具不可混用

- 觸發條件：heartbeat 驗證 LINE round 時，先到 user-local `supervisor_jobs` 目錄尋找 job lock，又把該 repo 外路徑交給 `git status`，分別得到 lock 不存在與 `outside repository`。
- 根因：混淆 canonical control plane 與 private data plane；job state／lock 位於 repo 的 ignored `MAPLAB-DURABLE-JOBS/<job-id>/`，run／lesson／supervisor receipt 才位於 user-local 0700 cache。
- 解法：canonical `job.json` 與 `.line-training-supervisor.lock` 用 repo path 驗證；user-local run、delta、receipt 用 `stat`／SHA-256 驗證。`git status` 只接 repo 內 path，不拿它查外部資料根。
- 預防：每個 durable adapter 的 Resume Prompt 必列出 control root、data root、lock path 與各自驗證工具；完成檢查先按 ownership root 分組，不用單一命令跨兩個根。

## 2026-08-27 — Live 服務頁與案例資料夾都不能單獨證明真實案例

- 觸發條件：規劃 WP／音樂 01–10 時，先從十個 live 服務分類頁定題與曲風，沒有先逐案對應 Google Drive 活動資料夾、活動身分與素材；後續又發現一個案例夾混入無關私人文件。
- 根因：把「內容 owner 存在」誤當「案例證據存在」，也把「檔案位於案例夾」誤當「檔案屬於該案例」。這會讓關鍵字、專名與曲風在事實鏈完成前被過早定案。
- 解法：案例產線固定走 `Drive folder ID/inventory → event/quote anchor → TimeTree/外燴系統 → ASSET_LOG file ID → visual QA → 公開來源三角 → live SEO collision/pillar route → title/keyword/style`；無關私密文件標記後排除，不引用或摘要。十個案例逐案選 existing post、pillar proof、new gap 或 social-only，不自動建十個 slug。
- 預防：任何案例 registry 先跑 `scripts/maplab_case_first_gate.py --level intake`；進 WP 前再跑 `--level wp --case-id ...`。服務頁不能作 `source_kind`，final keyword 必須同時有 verified identity 與 live collision proof。
- 封坑驗證：`tests.test_maplab_case_first_gate` 7/7 PASS；真實 10 案 intake PASS；服飾店開幕案例在分店、ASSET_LOG、visual QA 與 live collision 未齊時由 WP gate 正確拒絕。

## 2026-08-28 — 多跑不同樣本不等於訓練，也不等於換方法

- 觸發條件：Hermes LINE supervisor 連跑 12 rounds／60 次本機推論，總通過率只有 10/60；每輪換問題與 seed，卻沒有固定 canary、單一 changed variable、可比較 baseline 或 stop-loss。
- 根因：把 worker activity、round count 與新 lesson 檔誤當品質進展；現行流程其實是 random two-shot prompt evaluation，不是權重訓練或 retrieval learning。總分又主要被長度 gate 支配，failure taxonomy 與真實業務正確性沒有分開。
- 解法：Supervisor 新增 plateau guard；兩個未通過 qualification rounds 後切到 `method-redesign`，後續 resume 零模型呼叫、零 attempt。下一版先固定 20 案分層 canary、校正 rubric，再做 baseline/candidate 單一變因比較。
- 預防：每次新實驗必填 hypothesis、failure bucket、changed variable、fixed holdout、expected delta、stop-loss 與 method version；同方法兩輪無改善後禁止只換 seed／樣本繼續跑。第三次同錯必跑第一性原理 5 題並更新 regression set。
- 封坑驗證：34/34 focused tests PASS；真實 job 在不帶 `--data-root` 的 resume 回 `plateau_method_review_required`，round 仍 12、attempt 仍 6、loopback calls 仍 60。

## 2026-08-28 — Durable resume 不可依賴呼叫者記得私有 data root

- 觸發條件：以 canonical job path 直接續跑 LINE supervisor 時，CLI 未帶 `--data-root`，程式退回舊外接碟預設並回 `permissions_not_private`；同一任務因入口不同讀到不同資料根。
- 根因：資料根只存在 launchd／shell 參數，沒有從 canonical supervisor receipt 回推；把狀態責任留給下一位操作者記命令。
- 解法：resume 先驗證 owner-only supervisor receipt，再從 receipt 的 `data_root` 綁回相同 private dataset；CLI explicit value 只保留初始設定／診斷用途，receipt path 與 job id／data root 必須一致。
- 預防：任何 durable job 的 provider、data root、model digest 與 contract 都要由 canonical receipt 自我恢復；環境變數只能 bootstrap，不能成為跨 session 單一真相源。
- 封坑驗證：`test_resume_derives_private_data_root_from_canonical_receipt` PASS；實機無參數 resume 成功讀回 user-local 0700/0600 root，且 plateau guard 阻止任何新增模型呼叫。

## 2026-08-28 — 找到客戶要求不等於找到可收費漏損；缺 join key 時應停掉分類迴圈

- 觸發條件：50 案 taxonomy calibration 找出 18 個 heuristic true candidates；固定十案再做 evidence join 時，10/10 LINE source rows 都能定位，卻沒有任何一案同時接到 quote content、actual delivery、incremental cost 與 OrderCharges。
- 根因：LINE conversation ID 只由私有 CSV filename hash 而來；quote folder、`SALES_INTAKE`、`OrderCharges` 與 `MAPLAB_ASSET_LOG` 沒有共用的 stable case/quote/asset key。本機 `.gsheet` pointer 只有檔名 metadata，也不是報價內容或 charged-fee 證據。
- 解法：停止增加 keyword、round 或 classifier 版本；先建立本機 read-only join bridge，把 case、quote、charge、asset 的最小 key 在 process 內對應，receipt 只留 hashes、evidence status 與 missing codes。Live readback 若仍 zero stable joins，就立即產 field-level schema proposal，並把下一樣本改為「已有 quote＋charge 的 order 往回找 conversation」，不再對相同 random conversations 加模糊條件。四柱缺一就維持 `insufficient_evidence`、金額 0。
- 預防：margin-leak pipeline 的第一個 acceptance 不是「候選數」，而是四柱 join coverage；每案必有 baseline scope、actual delivery、incremental cost、charged fee。實驗抽樣要先看 evidence availability：要找漏收金額時優先從 evidence-rich orders 做 join-first，conversation-first 只適合訊號 taxonomy。Pointer、keyword、姓名或回覆語氣只能進 review queue，不可自動成為 leakage。
- 封坑驗證：固定十案 10/10 source hash resolved；live Google minimal readback 為 `SALES_INTAKE=45`、`Orders=693`、`OrderCharges=184`、2026 quote Sheets=159，但 stable join 仍 0、四柱 verified 各 0。Private-label/source-ID leak audit 0；Google reads 12、writes/token writes/model/send/new third-party egress 0。下一方法改 join-first fixed-five，不得再跑相同 name matcher。

## 2026-08-28 — Two-anchor 候選很多仍不等於 identity join；歷史回填要有停損

- 觸發條件：從已有 quote＋OrderCharges 的固定五個 2026 Orders 往回掃 3,625 個 LINE archives；3 案沒有 two-anchor candidate，另 2 案卻各出現 8／9 個候選，仍沒有唯一可驗的 conversation。
- 根因：完整日期與客戶／活動 identity 在歷史匯出中會重複；有兩個 exact anchor 只代表 candidate，沒有跨系統 `case_id` 時，增加 fuzzy 條件只會把不確定性包裝成假精準。
- 解法：unique candidate 才能標 stable；0 candidates 與 ambiguous candidates 分開記錄，ambiguous 一律 fail closed。固定五案 unique joins=0 後立即執行 stop-loss，repair point 改為 intake-time `case_id` capture，不再擴歷史 matcher。
- 預防：所有新 LINE case 在 intake 建本機 opaque `case_id`，並讓同一 key 穿過 Case Store／SALES_INTAKE、quote、Orders／OrderCharges 與 ASSET_LOG。歷史 backfill 沒有 deterministic key 時只保留 `insufficient_evidence`，不得算漏收金額。
- 封坑驗證：`margin-join-first-shadow-v1` fixed-five 為 no-candidate=3、ambiguous=2、stable=0、confirmed amount=0；13/13 focused tests、`py_compile` 與 independent audit PASS；receipt SHA-256 `55ce24ff...`，raw/customer/source IDs/Google IDs/third-party egress/model/send/write 全為 0。

## 2026-08-28 — 把兩個 destination 合成一個 synthetic PASS，會製造假的端到端證明

- 觸發條件：intake-time `case_id` contract 初版把 Case Store 與 `SALES_INTAKE` 合成單一 `atomic_pair` node，並只用 process-local `RLock` 驗 concurrency；14/14 tests 雖過，獨立稽核仍可構造「其中一邊沒寫」與「worker restart 後重複 mint」兩個 false-positive。
- 根因：把設計意圖的 distributed atomicity 當成已驗事實，也把 thread safety 當 crash-safe idempotency。真實系統中兩個 destination 不可能因一個記憶體 node 就原子完成；語法合法的 post-cutover key 也不等於有 intake provenance。
- 解法：拆成 `case_store`／`sales_intake` 兩個獨立且唯一的 acknowledgement，coverage 必須兩者皆在且 key 相同；quote gate 的檢查與 insert 留在同一把 `RLock`，late duplicate ack 一律拒絕。新增 owner-only synthetic SQLite intake ledger，以 source-event primary key、case unique constraint、`BEGIN IMMEDIATE` 與 FULL sync 驗 restart／two-connection race；post-cutover link 直接查 ledger 的 event→case，不接受 caller boolean。Receipt 寫入前逐層比對 exact key/value allowlist、timestamp 與 body/fixture hashes，`OrderCharges` schema proposal 補齊 `case_id`／`quote_id`／idempotency key。
- 預防：任何「穿過 N 階段」的 acceptance 必須逐 destination 留獨立 receipt/readback，不能用 composite boolean 代替；任何「可重跑／併發安全」宣稱至少測 fresh process/connection、unique constraint 與 commit-before-ack。Synthetic PASS 只能進 separate live review，不得直接部署。
- 封坑驗證：fixed 10 scenarios 必須 10/10，包含 missing Case Store、missing `SALES_INTAKE`、one-side mismatch、restart 與 two-connection race；16/16 contract tests、29/29 margin focused suite、`py_compile` 與 independent red-team 全 PASS，live write/send/model/network 仍為 0。
