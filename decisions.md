# decisions.md — 歷史決策記錄

> **用途**：Agent 冷啟動時快速了解「為什麼不用 X」「試過什麼失敗了」。
> 不記錄：檔名變更、任務狀態、誰在幾月幾號改了什麼。
> 更新方式：checkpoint.sh commit 後提示「有值得記錄的決策嗎？」→ 追加到對應區塊。

最後更新：2026-04-15

---

## GAS / Apps Script

### clasp 部署
- **clasp push 前必須確認 .clasp.json scriptId** — 報價系統 = `1JIiPW_OUwNzB...`，LINE 對話 = `1Fkl34P7p395k...`。A0 曾連續 3 天推到錯的專案，所有工作白費。
- **clasp 對 Sheet-bound Script 不可靠** — clasp list 回傳的 ID 與 Sheet-bound Script ID 不同，會靜默推到錯的地方。推完必須到 Apps Script 編輯器確認。
- **GAS 多檔案不能有同名函數** — 重複函數名會讓整個專案壞掉，不只是衝突的那個檔案。
- **Monaco API setValue 無法真正寫入 Apps Script** — 看起來成功但不會持久化。唯一可靠方法：Owner 手動貼或 clasp push。

### QUOTE_DRAFT 保護
- **setValue 會摧毀公式** — I/J 欄有 VLOOKUP，D 欄有下拉驗證。寫入前必確認目標 Range 無公式。可寫入：D（品名純文字）、G（數量）、K（狀態）。禁止覆蓋：I（業務報價）、J（小計）。
- **QUOTE_DRAFT 模板不能直接測試** — 必須先 makeCopy。A0 曾直接 setValue 破壞模板，靠 Sheets 版本紀錄還原。
- **copyTo 單一工作表會斷 VLOOKUP** — 複製出的 Sheet 裡沒有 Items 頁，公式變 #REF。正確做法：只複製值，或複製整個檔案+隱藏不需要的頁。
- **E 欄全是標籤，不是值** — D/F 欄才是值。A0 曾誤讀截圖把 E2 當日期值，錯誤傳播到多個 .gs 檔。
- **E25 公式用 =SUM(H7:H19)** — 不能用 SUMPRODUCT 引用 I 欄（I 欄是業務手動報價，故意留空）。
- **H33 公式 = H32**（不是 H32+G32）— G32 是報價小計不是成本，加進去會讓毛利率從 80% 變成 50%。
- **E33（總報價金額）故意留空** — 業務自己決定最終報價，空格是設計不是 bug。
- **列印範圍 C1:F55** — 框內=客戶看的，框外=內部用。舊範圍 C1:F61 已全部修正。
- **MVP 流程 = 業務手動下拉選品項** — 不是自動篩選。A0 曾寫不需要的 selectItemsForBudget_() 函數。

### GAS API
- **slide.move(index)** — 不是 presentation.moveSlide()，後者不存在。
- **GAS 版本控制 ≠ Sheet 資料版本控制** — clasp 管程式碼，Sheet 資料靠 Google Sheets 內建版本紀錄。
- **GAS endpoint 狀態：未確認 = 失敗** — 不要推測部署是否成功，未明確驗證就當作失敗（GAS 鐵律）。
- **禁止留舊版 GAS 函數在 production** — v2/v3 舊版 generateProposal 會造成圖片拉伸、空白、頁序錯誤。

### Python 替代方案
- **可用 Python + Google API 取代 Apps Script** — 避開所有 Apps Script 編輯器問題。Token 在 `~/.claude/mcp-keys/google-token.json`，scope 只有 spreadsheets+drive（沒有 presentations）。

---

## Slide 簡報生成

- **標準模板 = 文學館版（ID: 1s4VJY...U5E）** — 舊模板 "MAPLAB Kitchen - Catering Proposal v2" 已棄用。
- **P8/P9 菜單展示 + P10 報價頁 = 程式建立** — 模板上沒有 placeholder，必須刪除重建。
- **刪除/插入頁面後必須重新查詢所有頁面引用** — 操作後 page ID 會失效。
- **paymentMode 用三值列舉**（not_yet / deposit_received / paid_in_full）— 不是 boolean hasDeposit。
- **合約條款放在列印範圍內 C32/C33** — 舊版放 A30/A31（範圍外），客戶看不到。依 (isCorporate, paymentMode) 動態生成。
- **WordPress .avif/.webp 圖片不能直接用** — Google Slides 不支援。必須下載→轉 jpg→上傳 Drive→更新 K 欄。
- **Items K 欄只放圖片 URL** — 曾被活動記錄（如 "2025/11/21 1200/10人"）污染，破壞 Slide 自動生成。
- **沒有圖片的品項不能出現在 Slide** — 空白圖片占位不專業。BEV 飲品類例外（不需要照片）。

---

## Chrome Extension

- **MV3 禁止遠端 JS 執行** — 只能用本地 bundled code。
- **Private repo 用 GitHub Contents API** — raw.githubusercontent.com 不支援 token 認證。
- **每次版本變更必寫 CHANGELOG** — 否則下一個 agent 不知道改了什麼。
- **Bot→Extension clipboard 用 HTTP server（127.0.0.1:9876）** — AppleScript 需要 macOS Accessibility 權限會失敗。
- **parseStatus() 格式 = API 契約** — 自動生成 CURRENT_STATUS 時必須遵守現有格式（`- **Version**:`、任務表格、blocker 區塊）。

---

## Telegram Bot / A6 架構

- **A6 面向業務員 Mina，不面向客戶** — 客戶直接對話是未來 phase。目前 A6 = 背景報價加速器。
- **A6 永遠不自己算報價** — 呼叫 A5（報價引擎）。A5 是定價/成本/毛利的唯一真相源。
- **A6 觸發 GAS 用 HTTP endpoint（ApiEndpoint.gs）** — 不是點 Sheet 按鈕。A6 在 Claude Code terminal 裡無法點 UI。
- **GAS 失敗必須回傳明確錯誤訊息** — 靜默失敗會讓 AI agent 幻覺填補空白。
- **用 Anthropic SDK + OAuth token（sk-ant-oat01-）** — CLI subprocess -p 沒有記憶。SDK + conversation_history deque 保持上下文，Max 訂閱零額外成本。
- **四種合約模板**：to_c（個人）、to_b_deposit（企業有訂金，預設）、to_b_full（企業無訂金）、to_b_marketing（行銷公司）。
- **createQuote 後自動觸發 Slide 生成** — 不需要手動步驟。
- **fromMaster 模式** — 從母版 QUOTE_DRAFT 讀資料，不從副本讀（副本可能有過時資料）。

---

## LINE 整合

- **LINE Webhook 只能捕捉客戶→OA 的訊息** — 無法捕捉業務回覆。CONVERSATION_LOG 只有單向對話。
- **訓練資料來源改用 LINE OA Manager CSV 匯出** — CSV 有完整雙向對話，webhook 只有單向。
- **不要嘗試「補充」webhook 來捕捉業務回覆** — LINE API 根本不支援。
- **CONVERSATION_LOG 不拆分** — 144 行對效能無影響，拆分只增加複雜度。
- **doPost 直接寫入 + message.id 去重** — 不用 trigger queue（會造成 race condition）。
- **Case Store 是索引層，不是新的對話真相源** — 原始訊息仍以 Sheet `CONVERSATION_LOG` 為證據；本機 `data/case-store/a6_case_store.sqlite3` 只保存 row/msg_id 指標、摘要、缺欄位與候選 case_id，可重建，不 commit。
- **Case Store v0 只讀 LINE inbound** — `/linecases`、`/case`、`/casequote` 先用現有 CONVERSATION_LOG 建候選案件；正式報價仍由 A5/GAS 決定，A6 不因為找到候選案件就自動寫正式 Sheet。

---

## SEO / 內容

- **SEO 分數天花板 54-76（Elementor 限制）** — Rank Math 無法讀 Elementor widget 內容。新 Landing Page 改用 Gutenberg 原生區塊。
- **Rank Math updateMeta API 對 pages 回 403** — 用 WP REST API PUT `meta: { rank_math_focus_keyword, ... }` 代替。
- **Rank Math 工具列 CJK 內容顯示 0/100 是已知 bug** — 文章列表分數才準確。
- **圖片選擇：食物特寫、場地布置、空景** — 禁止：人臉、外部 logo、酒精。
- **禁用詞：「無麩質/Gluten-free」** — 暗示醫療級廚房認證，有法律風險。
- **「ESG」降級為軟性替代用語** — 觸發正式合規稽核，小型餐飲公司通不過。
- **改標題時保留 URL slug** — 改 slug 會斷 SEO 反向連結。

---

## 照片分類（A4）

- **用 Gemini REST API（requests.post）** — 不用 Python SDK。Vertex AI SDK 給 404，google.generativeai 給 400 + Colab 斷線。REST 速度 2x（310 vs 160 張/h）。
- **跳過 GPS 分類（S5.5 = no_gps）** — Google Takeout JSON 不在 Drive 裡，GPS 資料無法取得。Owner 指示跳過。
- **DELAY_SEC = 0.5，每 50 張批次寫 Sheet，每 200 張 Drive checkpoint** — 平衡吞吐量（~360-515/h）與 API 限制。
- **Takeout ZIP 必須完整解壓（圖片+JSON 都要）** — A4 曾只解圖片、丟 JSON、刪 ZIP，EXIF metadata 永久遺失。
- **Drive API v3 via google.colab.auth** — drive.mount 在 Colab 失敗。

---

## 廣告（A3）

- **LINE 按鈕追蹤用 regex `(lihi2\.com|lin\.ee|line\.me)`**（方案 A）— 所有 LINE CTA 都用 `lin.ee/IP8nt4n`。GTM v19 已驗證。
- **補充方案 B：Click ID trigger `LDP轉line`** — 首頁 LINE 按鈕共用此 ID。GTM v20 已部署。
- **Google Ads 0 轉換時不加預算** — NT$11,400/30 天 0 轉換，PMax 沒有轉換資料無法優化。Google 建議加 20.4% 預算應忽略。
- **也不暫停廣告** — 曝光 115K/30 天是好的，問題在追蹤不在投放。先修追蹤。
- **Meta 受眾加嘉義** — 訂單資料 7.4% 來自嘉義。移除奢侈品/汽車興趣（與實際客戶無相關）。
- **Claude 做技術設定（Pixel/GTM），Gemini 做成效分析（ROAS）** — 各有強項。

---

## 客服（A7）

- **FAQ 聚焦 LINE bot 處理不了的 30%** — LINE OA 選單已涵蓋 70% 初步資料收集。
- **不報具體價格，只給門檻** — 外燴最低 20 人、外送最低 NT$3000、高雄最低 NT$25000、最低出車 NT$10000。
- **每輪最多追問 3 題** — 優先序：日期 > 人數 > 活動類型 > 場地 > 預算 > 聯絡方式。
- **預算談判用菜單重組，不直接降價** — 品牌定位要求價格完整性。
- **服務範圍**：台南（免運）、高雄（≥NT$25K）、嘉義/屏東（報運費）、彰化以北 = 婉拒。
- **LINE OA 關鍵字回覆限 200 字** — 一個關鍵字只能對應一組回覆。
- **Flex Message 需要 Messaging API** — OA Manager 手動設定不支援。
- **優先自動化 Mode A（45%）+ B（25%）+ G（15%）= 85% 工作量**。

---

## 系統架構 / 治理

### 角色分工
- **A0 = 橋接層（Cowork），A1 = 執行層（Claude Code）** — A0 不直接改 GitHub 檔案。A0/A1 平行（都向 Owner 報告），不是層級關係。
- **A0 開 Code task 必須貼完整 recall prompt** — 不貼 = session 完全失憶。
- **Telegram bot 屬於 A1** — 在 Mac mini 上跑，不在 Cowork。三個 LaunchAgent：com.maplab.telegrambot、com.maplab.a6bot、com.maplab.git-pull。
- **兩個獨立 Telegram bot**：A0 知識庫 + A6 業務報價。分開避免干擾。

### 開發規範
- **checkpoint.sh 預設直推 main，--branch 走分支模式** — 因為 Git 具有完整的歷史追蹤與回溯復原能力，無須以分支作為主要存檔方式，全部變更皆應記錄存檔到 main branch。
- **worktree commit 必須 cherry-pick 到 main** — launchd bot 讀 main，worktree 裡的改動系統看不到。
- **建腳本前先 `ls scripts/`** — 防止重複建立已存在的腳本。
- **CURRENT_STATUS.md = 所有 agent 的唯一入口** — 與其他文件衝突時以此為準。
- **強制 Startup Check** — 不能接到任務就直接寫 code，必須先讀文件確認需求。
- **CLAUDE.md 必須是 AGENT_RECALL_PROMPTS.md A1 段落的精確版本** — 簡化版曾造成身份混淆。
- **.env / logs / conv_history.json 禁止進 git** — 曾被意外 commit，GitGuardian 觸發告警。
- **GitHub raw URL 加 `?t={timestamp}` 破快取** — 否則部署後拿到舊版。

### API 存取
- **三層備援**：MCP → curl + OAuth token → 回報 Owner。
- **Google OAuth MCP 必須用「網頁應用程式」類型** — 桌面類型沒有 redirect URI。
- **API 失敗必須給明確訊息** — return None 不帶訊息 = AI 會幻覺解釋。
- **Claude Code 用 Max 訂閱** — 不是按次計費。3-6 分鐘回應時間是正常的。

### 委派規範
- **委派時帶上前次結論 + 具體接續點** — 不要抽象指令（「去分析 X 架構」浪費整個 session）。
- **7 題快速會議 protocol** — A0 派任務前必跑，避免方向錯誤。
- **讀 session log 再讀 code** — code 只回答 "how"，不回答 "what actually happened"。
- **畫系統邊界再修 bug** — 多系統場景先釐清「誰跟誰說話」。
- **Chrome 驗證（eyes on target）** — 改 GAS→Apps Script 編輯器確認。改 bot→Telegram Web 測試。改 Sheet→開 Sheet 看。

### 成本優化
- **Batch API（5 折）+ Prompt Caching（省 90%）可疊加** — 非即時任務（照片分類、SEO 文章）適用。

### CRD 跨機器操作
- **用 form_input + dispatchEvent** — 不用 left_click。CRD 上 left_click 會觸發 Windows Task View。

---

## V7 系統進化決策

- **「按需搜尋」不適合本系統** — 子系統高度連動，agent 不知道自己該搜什麼。保持預讀，但預讀內容必須 100% 正確。
- **單一真相源** — 每項資訊只存在一個地方，其他地方用連結。
- **自動生成取代手動維護** — checkpoint/patrol 自動更新狀態檔。
- **Phase 順序 1→2→3→4→5** — 不能在建好真相結構（1）和自動同步（2）前瘦身（3）。

## Codex 召喚通路

- **A1 offload 用直接 CLI（通路①），不繞 A6（通路②）** — 2026-07-10 實測發現兩條路底層是同一支本機 `codex exec --ephemeral -s read-only`，延遲相近（~14s），A6 沒有獨立額度或服務端點。通路②唯一優勢是內建 A6 對話歷史模板，A1 自己的一次性 offload 用不到，直接繞過 A6 模組反而更輕量。
