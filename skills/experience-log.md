# Experience Log — 成功路徑 + 失敗教訓

> **用途**：記錄所有 Agent 的實戰經驗，包含成功和失敗。  
> 新 Agent 開工前翻一下，避免重複踩坑，也知道最快的做法。  
> **取代舊的 lessons-learned.md**（舊檔只記失敗，不記成功）。

版本：v1.0 | 建立：2026-03-23 | 維護者：A1 + 所有 Agent

---

## 寫入規則

1. 任務結束時，如果有新經驗，在這裡新增一筆
2. 每筆都用 EXP-xxx 編號（SUCCESS 或 FAILURE）
3. 必須包含「下次怎麼做最快」— 這是最重要的欄位
4. 舊的 lessons-learned.md INCIDENT-001~005 已搬遷至下方

---

## 成功經驗（SUCCESS）

### EXP-S001: Gemini REST API 比 Python Library 快 2 倍且更穩定

- **日期**: 2026-03-23
- **Agent**: A4 Pipeline Agent
- **類型**: SUCCESS — 工具選擇
- **場景**: 122,200 張照片需要 Gemini Vision AI 分類
- **試過什麼**:
  - Vertex AI SDK → 404（模型名稱格式不同）
  - google.generativeai library → 400 Bad Request + Colab proxy 斷線後無法恢復
- **最終選擇**: Gemini REST API（requests.post 直接呼叫）
- **為什麼好**: 310 張/小時 vs 160 張/小時，不依賴 proxy，Colab 斷線重連後直接繼續
- **下次怎麼做最快**: 直接用 REST API + gemini-2.5-flash，跳過 python library

### EXP-S002: Google Sheets 模擬 RDB 對小規模業務夠用

- **日期**: 2026-03-13
- **Agent**: A5 Master Data Agent
- **類型**: SUCCESS — 架構決策
- **場景**: MAPLAB Kitchen ERP 需要資料庫
- **決策**: 用 Google Sheets 模擬 RDB（6 張表 + item_id FK 關聯）
- **為什麼好**: 外燴業務 <10,000 筆，Sheets 進入成本極低，Gemini 輔助格式驗證
- **下次怎麼做最快**: Sheets + item_id 命名規則 {TYPE}-{SUBTYPE}-{SEQ3}，先清洗品項再建結構

### EXP-S003: CURRENT_STATUS 單一入口解決 Agent 迷路問題

- **日期**: 2026-03-18
- **Agent**: A1 Handbook Agent
- **類型**: SUCCESS — 治理設計
- **場景**: Agent 開工不知道先讀什麼檔案
- **決策**: 建 CURRENT_STATUS.md 作為唯一起點，所有其他文件衝突以它為準
- **為什麼好**: Agent 不再猜測，一個入口看到全局
- **下次怎麼做最快**: Day 1 就建 CURRENT_STATUS + TASK_QUEUE

### EXP-S004: GPS 座標比 AI Vision 更適合判斷照片地點

- **日期**: 2026-03-23
- **Agent**: A4 Pipeline Agent
- **類型**: SUCCESS — 技術選擇
- **場景**: 日常照片需要分 home/shop
- **試過什麼**: Gemini Vision（無法判斷拍攝地點，除非有店招）
- **最終選擇**: 從 Takeout JSON metadata 提取 GPS 座標 + 距離計算
- **為什麼好**: 零 API 成本、~5000 張/分鐘、準確度高於視覺判斷
- **下次怎麼做最快**: 直接用 GPS，不要嘗試 AI Vision 判斷地點

### EXP-S005: 先用現有貼文上線廣告，不等完美素材

- **日期**: 2026-03-23
- **Agent**: Owner
- **類型**: SUCCESS — 策略決策
- **場景**: Canva C款素材未完成，Meta 廣告「慶生周歲派對」無法上線
- **決策**: 用現有貼文先上線，測試受眾反應
- **為什麼好**: 不被素材製作阻塞，提早取得數據
- **下次怎麼做最快**: 先上現有素材測受眾，再用數據指導素材優化

---

## 失敗經驗（FAILURE）

> 以下從舊 lessons-learned.md 搬遷，補充「下次怎麼做最快」欄位。

### EXP-F001: Takeout ZIP 被刪導致 EXIF metadata 永久遺失

- **日期**: 2026-03-17
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 不可逆資料遺失
- **嚴重性**: HIGH
- **事件**: 解壓只提取圖片，沒提取 JSON metadata → 建議清垃圾桶 → ZIP 被刪 → 再也拿不到 JSON
- **根因**: 流程規劃不完整，建議清除前沒確認依賴
- **下次怎麼做最快**: 解壓時一次提取所有檔案（圖片 + JSON），確認全部提取完成後才清除 ZIP

### EXP-F002: Vertex AI 模型 404

- **日期**: 2026-03-18
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — API 選擇錯誤
- **嚴重性**: MEDIUM
- **事件**: V2/V5 兩個版本浪費在不存在的 Vertex AI 模型名稱上
- **根因**: Vertex AI SDK 模型名稱格式與 Generative AI API 不同
- **下次怎麼做最快**: 直接用 google.genai + API key（見 EXP-S001）

### EXP-F003: GitHub Raw Content 快取導致部署舊版

- **日期**: 2026-03-18
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 快取問題
- **嚴重性**: MEDIUM
- **下次怎麼做最快**: curl 下載加 `?t={timestamp}` 破壞快取

### EXP-F004: PHOTO_ROOT 路徑錯誤

- **日期**: 2026-03-18
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 路徑假設錯誤
- **嚴重性**: LOW
- **下次怎麼做最快**: 不假設資料夾結構，先用 os.listdir 逐層驗證

### EXP-F005: google.generativeai PIL Image 400 錯誤

- **日期**: 2026-03-19
- **Agent**: A4 Pipeline Agent
- **類型**: FAILURE — 棄用套件
- **嚴重性**: HIGH
- **下次怎麼做最快**: 注意 FutureWarning，直接用 REST API（見 EXP-S001）

### EXP-F006: Agent 不問問題就開始做

- **日期**: 2026-03-23
- **Agent**: 全體
- **類型**: FAILURE — 治理缺陷
- **嚴重性**: HIGH
- **事件**: Agent 拿到任務就衝，不釐清方向、不拿技能書
- **根因**: 系統沒有強制卡點
- **修復**: PROTOCOL v1.4 加 Startup Check 必填欄位 + SECTION 0 阻擋規則
- **下次怎麼做最快**: Day 1 就設 Startup Check 強制欄位，不靠 Agent 自律

### EXP-F007: CHANGELOG 宣稱修了但實際沒改

- **日期**: 2026-03-19
- **Agent**: A1 Handbook Agent
- **類型**: FAILURE — 驗證缺失
- **嚴重性**: MEDIUM
- **下次怎麼做最快**: 先確認實際文件內容，再寫 CHANGELOG

### EXP-F007 — bot.py 記憶斷裂（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0 Telegram Bot
- **類型**: FAILURE — 架構設計錯誤
- **問題**: bot.py 用 `claude -p` one-shot 呼叫 Claude Code CLI，每條 Telegram 訊息都是全新 session，沒有對話記憶
- **為什麼做這件事**: A0 想讓 Telegram bot 接上 Claude AI 回覆，但不想用付費 API
- **失敗原因**: `-p` flag 是 one-shot prompt，用完就關 session。之前的版本用 Anthropic SDK + conversation_history deque 有記憶，改成 CLI 呼叫後記憶機制斷了
- **更好的方向**: 用 Anthropic SDK + OAuth token（sk-ant-oat01-）直接呼叫，保留 conversation_history，走 Max 訂閱不花錢。OAuth token 可以當 api_key 用
- **修復**: bot.py 改回 Anthropic SDK + OAuth token + conversation_history，加 `--dangerously-skip-permissions` 給 CLI fallback
- **下次怎麼做最快**: 用 Anthropic SDK + OAuth token + deque conversation_history，不要用 `claude -p`

### EXP-F008 — A0 開 Code task 不帶 recall prompt（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0 Cowork
- **類型**: FAILURE — 治理缺陷
- **問題**: A0 開了 30+ 個 Code task，每個都沒有貼 A1 recall prompt，導致每個 session 都是失憶狀態
- **為什麼做這件事**: A0 要委派 A1 做各種任務（git commit、讀文件、改程式碼）
- **失敗原因**: Cowork 的 start_code_task 工具沒有強制檢查 prompt 裡是否包含 recall prompt。A0 的 user preferences 裡也沒有這條規則
- **更好的方向**: 1. auto-memory 裡存 A1 recall prompt（已做）2. user preferences 加強制規則（已做，等 Owner 貼入）3. CLAUDE.md 放在 repo 根目錄讓 Claude Code 自動讀取（已做）4. 理想方案：Cowork 的 start_code_task 工具內建 recall prompt 注入（需 Anthropic 改產品）
- **下次怎麼做最快**: 開 Code task 時，確認 prompt 含 CLAUDE.md 或 A1 recall prompt；CLAUDE.md 已在根目錄自動注入

### EXP-F009 — CLAUDE.md 跟 AGENT_RECALL_PROMPTS.md 內容不同步（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0/A1
- **類型**: FAILURE — 文件不一致
- **問題**: A0 建了 CLAUDE.md 但內容是自己寫的簡化版，跟 Extension 裡 A1 的 recall prompt 不一樣。tmux 裡的 Claude Code 讀 CLAUDE.md 後以為自己是 A0
- **為什麼做這件事**: 想讓 Claude Code 啟動時自動知道自己是 A1
- **失敗原因**: 兩套不同的身份描述 = 身份混亂
- **修復**: CLAUDE.md 改為 AGENT_RECALL_PROMPTS.md A1 code block 的完整拷貝，加同步提醒
- **下次怎麼做最快**: CLAUDE.md 頂部加「本文件內容與 RECALL_PROMPTS A1 區塊同步」提醒，每次改一個就改另一個

### EXP-S007 — CRD「傳送文字」+ JavaScript dispatchEvent 成功啟動 Windows Agent（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0 Cowork
- **類型**: SUCCESS — 跨機器操作
- **場景**: A0 需要遠端啟動 Windows 上的 A2 和 A7
- **成功方法**: 1. form_input 把指令寫入 CRD「傳送文字」textarea（aria-label="傳送文字"）2. JavaScript: `document.querySelector('[aria-label="傳送"]').dispatchEvent(new MouseEvent('click', {bubbles: true}))` 3. 不用 left_click 點按鈕（會觸發 Windows Task View）
- **結果**: A2 完成 SEO Title 優化 36 篇，A7 完成客戶對話流程圖
- **下次怎麼做最快**: CRD 遠端打字用 form_input + JavaScript dispatchEvent，不用 left_click（會誤觸 Windows）

### EXP-S008 — A0/A1 並列架構確立（2026-03-27）

- **日期**: 2026-03-27
- **Agent**: A0/A1
- **類型**: SUCCESS — 系統架構
- **場景**: 需要定義 A0（Cowork）在系統中的角色
- **成功設計**: A0 和 A1 是並列關係（各自直屬 Owner），不是上下級
- **結果**: A0 = 跨系統橋接（repo 外），A1 = 技術執行（repo 內）。溝通協議寫入 AGENT_RULES v3.2
- **下次怎麼做最快**: 明確定義每個 Agent 的「邊界」（repo 內/外），避免職責重疊或互相等待

### EXP-S009 — bot.py session resume 修復成功（2026-03-28）

- **日期**: 2026-03-28
- **Agent**: A0 Telegram Bot
- **類型**: SUCCESS — 架構修復
- **問題**: bot.py 用 `claude -p` one-shot 呼叫 Claude Code CLI，每條 Telegram 訊息都是新 session，無記憶、無 MCP、無 bash
- **為什麼做這件事**: Owner 要 Telegram bot 有 AI 對話能力 + 記憶 + MCP 工具 + bash 指令，跟昨天一樣
- **嘗試過的錯誤方向**:
  1. 用 Anthropic SDK 替代 CLI → 有記憶但沒有 MCP 和 bash
  2. 用 ccbot tmux bridge → 過度複雜，需要話題群組
  3. 用 `--dangerously-skip-permissions` → 解決了授權問題但沒解決記憶問題
- **成功方法**: 加 `-c` flag（`claude -p -c --dangerously-skip-permissions`），讓每次呼叫 continue 最近的 session。同一個 session = 有記憶 + 有 MCP + 有 bash + Max 免費
- **根因分析**: Claude Code CLI 有完整的 session 管理（-c continue / -r resume / --session-id / --name），一開始沒查就亂改。正確做法是先查 `claude --help` 看有什麼 flag 可用
- **更好的方向**: 如果 `-c` 不夠穩定（resume 到錯誤的 session），可以用 `--session-id telegram-bot` 固定 session ID
- **下次怎麼做最快**: 加 `-c` flag 就好，先查 `claude --help` 再動手

### EXP-S010 — A6/A5 地端報價模型要用 deterministic fallback 保底（2026-06-14）

- **日期**: 2026-06-14
- **Agent**: A0 Dispatch + A5/A6 runtime
- **類型**: SUCCESS — 地端模型調教
- **場景**: Owner 要 A6 測競品菜單截圖是否能辨識品項、找 MAPLAB 雷同品項、成本總價 * 5，並產 Google Sheet 試算表連結。
- **試過什麼**:
  - 只靠 gemma4 prompt：會輸出 Thinking，800 token 內可能沒有合法 JSON。
  - prompt 加 Items 清單：可降低假菜名，但仍不能保證產 `createQuoteVariants`。
  - deterministic fallback：用 `data/items_master.json` 與固定 mapping 產合法 payload。
- **最終選擇**: prompt 收窄 + sanitize + JSON 檢查 + deterministic `createQuoteVariants` fallback。
- **為什麼好**: 地端模型可以負責語意/OCR 輔助，但 Sheet payload 由程式保底；這次同一張競品菜單可產 12 項 MAPLAB 雷同品項、成本 NT$5,520、報價 NT$27,600，甜甜圈/烤蔬菜盤列人工補成本。
- **下次怎麼做最快**: 先讀 `skills/a6-local-quote-model-tuning.md`，不要把 local model raw output 當報價成果；合法 JSON + Sheet URL 才算完成。

### EXP-S011 — Mac 原生工具擴充要先做路由層，不要先換模型（2026-06-15）

- **日期**: 2026-06-15
- **Agent**: A0 Dispatch
- **類型**: SUCCESS — 能力評估
- **場景**: Owner 貼「Mac-1 接 487 個 macOS 原生工具」截圖，詢問是否要擴充地端模型能力。
- **試過什麼**: 搜尋 Mac-1、487 macOS tools、6.6B、Calendar/Mail/Safari 等 primary source 線索；未找到可信官方 repo/model card。
- **最終選擇**: 新增並修正 `skills/mac-local-tool-routing/`，把需求拆成 connector、Chrome/OpenClaw、shell/osascript、Codex review bundle 的行動路由；Mac-1 先列 watchlist，但既有工具可做的 read-only/draft/test 工作要先做。
- **為什麼好**: 即使模型 claim 未驗證，MAPLAB 仍能吸收「Mac 本機工具鏈」的好想法；同時避免把 secrets、寄信、刪檔、發佈權限交給不可審查的模型，也避免 agent 用權限當停工理由。
- **下次怎麼做最快**: 看到 Mac-native AI 工具 claim 先拿 `mac-local-tool-routing`；找不到 primary source 就禁止 production integration，但要用現有工具推進 read-only smoke、draft payload、disposable test 或 approval-ready packet。

### EXP-F010 — 權限框架寫成停工制度，違反快速迭代文化（2026-06-15）

- **日期**: 2026-06-15
- **Agent**: A0 Dispatch
- **類型**: FAILURE — 企業文化違反 / 快速迭代
- **場景**: Owner 要評估「Mac-1 接 487 個 macOS 原生工具」是否能變成 A6/地端模型能力。我先查不到 primary source，接著新增 `mac-local-tool-routing`，但第一版把重點放在 risk gates / confirmation gates，語氣會讓 agent 把可先做的工作交回 Owner。
- **違反了什麼文化**:
  - 違反「主動推進」：沒有先做 read-only smoke、draft payload、disposable test、approval-ready packet。
  - 違反「快速迭代」：沒有先交付最小可驗證版本，而是先設計一套會拖慢大家的權限制度。
  - 違反「不做白工」：如果其他 agent 照第一版技能走，會產生等待、轉交、請示，沒有形成可驗證產出。
- **根因**: 把「未驗證模型不得進 production」錯誤擴張成「Mac 本機工具能力先不要做」；把安全邊界寫成停工邊界，而不是行動分層。
- **修復**: 立即把 `mac-local-tool-routing` 改成 action-first：direct-do 直接做，draft/approval-ready 先產包，live/external/high-risk 才問最後確認；watchlist 也改成「未驗證不等於 work stoppage」。
- **下次怎麼做最快**: 遇到新 AI tool claim，先拆成「今天可直接做的 10 分鐘 smoke / draft / disposable test」，做完留 receipt；production integration 另開 review gate，不得讓 gate 擋住最小可行迭代。

### EXP-S012 — 每日巡查要接 reaction layer，不只是 Telegram delivery（2026-06-15）

- **日期**: 2026-06-15
- **Agent**: A0 Dispatch + A1/Hermes/Codex runtime
- **類型**: SUCCESS — 系統閉環
- **場景**: Owner 指出每日巡查可靠推送，但同一批阻塞/Owner 行動項推 30 天 60 天仍沒人處理；需求不是更會通知，而是有人看結果、判斷、提出下一步，並寫回相對角色。
- **試過什麼**:
  - 只解釋 Telegram sender 歸 A1 patrol：可回答來源，但沒有解決「誰反應」。
  - 直接把 Hermes 放進 hot path：會增加不穩定與自動修改風險。
  - deterministic bridge：用程式把巡查結果、Task Card、Hermes 狀態、Chrome Extension Hermes 路由落差整理成 reaction cards。
- **最終選擇**: 保持 `scripts/patrol.sh` deterministic；在 `scripts/patrol-scheduled.sh` 後接 `tools/hermes_patrol_bridge.py`，產 `workbook/hermes/patrol/latest.json`、`hermes_prompt.md`、`telegram_decision_card.md`、`local-control-plane/hermes.html`。每張 reaction card 都要有 `owner_role`、`target_task_card`、`next_step_patch_hint`、`codex_followup_prompt`。
- **為什麼好**: 地端/Hermes 可以定期接手巡查結果，Codex/A1/B1 可按 packet 週期性確認專案進度並往下推；Owner 不必每天看同一段阻塞原文。
- **下次怎麼做最快**: 先跑 `python3 tools/hermes_patrol_bridge.py --repo /Users/pagemacmini/maplab-ai-handbook`，再開 `local-control-plane/hermes.html`；若 reaction card 指向 task card，就讓 Codex/A1 直接改接續點或產 5-minute Owner card。

### EXP-F011 — Artifact substitution: 用周邊產物替代 Owner 外部指揮問題（2026-06-15）

- **日期**: 2026-06-15
- **Agent**: A0 Dispatch / Codex
- **類型**: FAILURE — 需求對齊 / 優先順序 / 錯誤模式
- **場景**: Owner 說需要一個人在外面也可以指揮的窗口；現有冷啟動 prompt 已可召喚角色，真正缺的是 Telegram 入口能把指令轉成「召喚誰、用哪份 prompt、交給哪個 worker、怎麼回報進度」。
- **表層錯誤**: 先把 Chrome Extension popup 與 generated role modules 的 Hermes target 對齊。這不是完全沒價值，但它是周邊一致性工作，不是 Owner 當下最需要的 P0。
- **真正錯誤模式**: artifact substitution。Agent 把「可見、可改、可驗證的內部產物」錯認成「使用者要解決的控制問題」。這次是 Extension；下次可能換成 panel、dashboard、skill、metadata、generator、README、status JSON。若只反省「不該改 Extension」，下次還會去改橘子、錢包或別的東西。
- **深層根因**:
  1. 沒有先寫使用者場景：人在外面，只能用 Telegram，下令後要看到 receipt。
  2. 沒有定義 P0 的驗收：Telegram command -> role route -> cold-start prompt/context -> worker dispatch -> progress receipt。
  3. 把「系統看起來更一致」誤判成「Owner 能力增加」。
  4. 忽略額度/注意力成本：Owner 花錢買的是決策與推進，不是 agent 自己覺得乾淨的結構。
  5. 沒有 stop rule：當工作離 command window 超過一層，就應停下改做 P0。
- **團隊指引**:
  - 任何 bot / Hermes / dispatch 需求，先產 control-loop contract，不先做周邊整理。
  - P0 必須是可操作入口，不是文件、面板或 metadata。
  - 每個輸出要回答「Owner 在外面現在能多做什麼？」答不出來就是 secondary。
  - 周邊整理可以做，但必須標為 P2/P3，不能佔用主線。
- **正確優先順序**:
  1. P0：Telegram command window，Owner 一句話進來後能選角色/套冷啟動 prompt/交給 Codex 或 Hermes worker/回報 receipt。
  2. P1：巡查結果轉 reaction cards，寫出 role next-step 與 Codex follow-up。
  3. P2：Chrome Extension / role module / dashboard metadata 對齊。
  4. P3：面板視覺與管理體驗。
- **下次怎麼做最快**: 先實作或設計 Telegram `/dispatch` / 自然語言 command route，最小驗收是 Telegram 回一張 dispatch receipt：`role`、`prompt_source`、`worker`、`status`、`next_check`。只有這條路可跑後，才做 Extension/module/panel 同步。

### EXP-F012 — Hermes fallback 不是泛化 Hermes 建設，而是 `maplab_claude_bot` 的備援路徑（2026-06-15）

- **日期**: 2026-06-15
- **Agent**: A0 Dispatch / Codex
- **類型**: FAILURE — 第一性原理 / bot 入口對齊 / 額度備援
- **Owner 原始需求**: `maplab_claude_bot` 要接給 Hermes 當接口；確認 bot 背後接什麼模型；保留原本和 Claude 對話、貼圖片、請它控制電腦的能力；Hermes 只在 Claude 沒額度或 primary unavailable 時接手，而且要善用長期記憶，能指出 agent 走歪路。
- **我查到的事實**:
  - `bot/bot.py` 是 A1 Telegram bot entrypoint。
  - 文字與貼圖都走 `claude -p --dangerously-skip-permissions`；貼圖會先存到 `data/telegram-photos/`，再把本機檔案路徑交給 Claude 讀。
  - 現況沒有 Hermes fallback wrapper，也沒有 Telegram 端的 `primary_failed_reason -> fallback=Hermes` receipt。
  - repo 有 checkpoint / 版本表 / 更新者習慣，但沒有看到全域正在執行的「每次改檔必記 agent/runtime/model/date」enforcement。
- **我做錯什麼**:
  1. 把 `scripts/patrol.sh` 的每日巡查問題和 `maplab_claude_bot` 的互動入口問題混在一起。
  2. 把 Hermes reaction panel、Extension runtime target、metadata sync 當成主線；它們可以有價值，但不能替代 Telegram fallback。
  3. 沒先回答最小驗收：「Claude 沒額度時，Owner 在 Telegram 貼一張圖，Hermes 是否會接手並回 receipt？」
  4. 沒在改檔前先做具名打卡，違反 Owner 對 agent/model/date 可追溯的要求。
- **第一性原理修正**:
  - 需求的本體是外部 command window，不是 dashboard。
  - primary 是 Claude CLI；fallback 是 Hermes；trigger 必須是 quota/rate-limit/auth/CLI missing/timeout 這種 primary unavailable，不是任意改路由。
  - Hermes 的價值不是「另一個聊天模型」，而是 cold-start memory worker：先讀 `CURRENT_STATUS.md`、`pitfalls.md`、企業文化、近期 Telegram log、相關 Task Card，再跑第一性原理檢查，必要時指出使用者或 agent 走錯主線。
  - 任何電腦控制能力都要保持和 Claude Code 相同的 receipt 與邊界：能讀/能草稿/能操作/需確認分開列，不把 secrets 或 live destructive action 交給不明狀態。
- **正確實作順序**:
  1. 在 `bot/bot.py` 加 `claude_ask_with_fallback()`，保留 Claude primary。
  2. 分類 Claude failure；只有 quota/rate-limit/auth/CLI missing/timeout 啟動 `hermes_ask()`。
  3. `handle_photo()` 產生同一份圖片路徑 prompt，fallback 時照樣交給 Hermes。
  4. Hermes prompt 注入 cold-start memory sources 與「先判斷我是不是走歪路」檢查。
  5. Telegram 回覆 receipt：`primary_failed_reason`、`fallback_engine`、`model`、`date`、`agent`、`memory_sources`、`allowed_actions`。
  6. 新增 `/model` 或 `/runtime` 讓 Owner 隨時看到 primary/fallback/model/date。
- **下次怎麼做最快**: 先寫 10 行 control contract 並貼給 Owner確認；確認後只改 `bot/bot.py` 與最小測試，不再先碰 patrol、Extension、panel。改檔前先留下具名打卡：Agent、runtime、model/date、任務、預計改哪些檔。

### EXP-FEEDBACK-001 — Cowork Dispatch 產品限制（2026-03-28）

- **日期**: 2026-03-28
- **Agent**: A0 Cowork Dispatch Secretary
- **類型**: FEEDBACK — 產品限制回報
- **問題 1**: Cowork 沒有像 Telegram 那樣的「指定回話」功能——每次新 session 都從零開始，A0 只有 auto-memory 跨 session，不是完整對話上下文
- **問題 2**: Cowork 沒有複製貼上功能——無法方便地複製長文字（如 recall prompt）貼到 Code task
- **影響**: A0 每次 session 開始要花大量 token 重建上下文；開 Code task 帶 recall prompt 很不方便
- **建議**: 回報給 Anthropic，建議 Cowork 加入 session resume 和 clipboard 功能
- **下次怎麼做最快**: A0 開 Code task 時，透過 Extension 複製 recall prompt，再貼到 Code task（比在 Cowork 打字快）

---

## 格式模板（新增時複製）

```
### EXP-Sxxx / EXP-Fxxx: [一句話標題]

- **日期**: YYYY-MM-DD
- **Agent**: [誰]
- **類型**: SUCCESS / FAILURE — [分類]
- **場景**: [遇到什麼問題/需求]
- **試過什麼**: [如適用]
- **最終選擇/根因**: [結果]
- **下次怎麼做最快**: [最重要的一行 — 給下一個 Agent 的最短路徑]
```
