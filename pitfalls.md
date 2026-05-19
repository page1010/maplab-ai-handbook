# pitfalls.md

> Cold-start required. 每次修到重複錯誤，要把「觸發條件 / 根因 / 解法 / 預防」寫回這裡。

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
