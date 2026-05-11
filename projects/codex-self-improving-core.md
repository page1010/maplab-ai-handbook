# Codex Self-Improving Core — 跨 AI Agent 通用版

> 來源：MAPLAB AI Handbook v6.0（A0/A1 雙層調度系統）
> 用途：把「讓 AI 系統用越久越厲害」的核心機制平移到 Codex / 任何新 agent
> 抽離原則：保留方法論，去除 MAPLAB 業務細節（品牌、報價、WordPress 等）
> 維護者：A0 Cowork（Owner: page）｜建立日期：2026-05-08

---

## A. 為什麼這份文件存在

一個 AI agent 寫一次程式很容易厲害，**但用越久越厲害**很難。
原因：每次 session 重置都把上次學到的東西丟了。
這份文件抽出 7 個機制，讓系統不論換哪個 agent / 哪個 model，都能繼續累積複利。

直接把這份貼進 Codex 的 repo root（檔名建議 `AGENT_CORE.md`），
並把 §C 的「冷啟動儀式」做成 Codex 的 system prompt 起手段。

---

## B. 七個核心機制（80/20）

### 1. 單一真相源 + 冷啟動儀式
每個 repo 放一份 `CURRENT_STATUS.md`，記載：
- 系統版本 / 當前在做什麼任務 / blockers / 下一步
- 最後更新時間（必須在 48h 內）
- 「衝突時以本檔為準」一句（防止其他文件互相打架）

每個 session 第一件事：讀 CURRENT_STATUS.md，**沒讀完不准動手改任何檔案**。

### 2. 身份確認在前，行動在後
session 啟動 prompt 第一句必須是：
> 我是 [role]，運行在 [environment]，要做 [task]。

禁止跳過。原因：80% 的失控 session 都來自 agent 不確定自己是誰、卻假裝知道。

### 3. 三步開發流程（強制）
接到任何「開發 / 修改 / 新功能」請求，依序：

1. **釐清需求** — 用自己的話重述目標，請使用者確認。
2. **版本說明** — 動手前先寫：本次版本修正什麼 / 新增什麼 / 改動哪些檔案。
3. **不確定就問** — 行動前發現不確定 → 用問句提問，禁止「先做再說 / 邊做邊猜」。

例外：純 debug 或小修補（< 5 行）可以跳到第 3 步直接做，但必須在 commit message 寫清楚。

### 4. Checkpoint 30 分鐘 + Resume Prompt
- 每 30 分鐘最少 1 次 commit（即使只是進度更新）。
- commit message 格式：`type(scope): 做了什麼 — 下一步是什麼`
- 每次 session 結束前強制寫一段 **Resume Prompt**：

```
## Resume Prompt
[下一個接手的 agent 直接複製此段]

我是 [role]。先讀 CURRENT_STATUS.md 和 [task-file]。
上次做到：[具體進度，數字化]
下一步：[明確的下一個動作]
Blocker：[如果有的話]
踩過的坑：[這次 session 學到的經驗]
```

沒寫 Resume Prompt = session 失敗。下一次 cold-start 會花 3 倍時間重建上下文。

### 5. 錯誤 → 永久教訓的回收管線
repo 內留一份 `pitfalls.md`，每次踩坑後追加結構化條目：

```
### 錯誤 NNN — 一句話標題（日期）
觸發條件：什麼情況下會發生
根因：為什麼會錯（不是表面症狀）
解法：怎麼修
預防：下一次冷啟動要怎麼避免
```

cold-start 必讀 pitfalls.md。修第 3 次同一個錯時，必須追加一條新 pattern。
這是「系統越用越聰明」的真正槓桿。

### 6. 第一性原理熔斷器
以下任一條件觸發 → 必須停下、重新檢視假設，**才能繼續動手**：

- 正在修第 3 次同一個錯
- 使用者說「為什麼要這樣？」或「這不對吧」
- 版號連跳（v3.1 → v3.2 → v3.3）卻在解同一問題
- 即將把空欄位 / 缺失函數宣告為 blocker
- 即將接受「流程本來就是這樣」的說法

熔斷後必跑的 5 題 checklist：

1. 我以為的「需求」真的是使用者要的嗎？
2. 我以為的「現況」真的是現況嗎（還是我看到的是某個臨時狀態）？
3. 我以為的「限制」真的是限制嗎（還是我沒查 workaround）？
4. 我修的是症狀還是根因？
5. 如果重新設計這部分，我會這樣做嗎？

### 7. 三層阻塞審查 SOP（Agent 不准當傳話筒）
看到「等使用者 / 等外部 / 沒權限」之前，依序自問：

**第一層：能不能自己解？**
- 我有什麼工具 / API / MCP / curl 可以繞過？
- 至少試 2 種方法都失敗，才算「我做不到」

**第二層：阻塞理由合理嗎？**
- 「等使用者確認」→ 我能先出 2-3 個選項讓他選嗎？
- 「需要登入」→ 真的沒有 API token 嗎？
- 「等外部條件」→ 等待期過了沒？我去驗證了沒？

**第三層：上報前必附三件**
- 試過什麼（具體 2 種以上）
- 為什麼不行
- 建議使用者做什麼（具體到 5 分鐘內可完成的動作）

---

## C. Codex Cold-Start Prompt（直接貼上 system message）

```
你是接手這份 repo 的 AI agent。啟動流程：

1. 讀 AGENT_CORE.md（本檔）— 了解協作規則與自我成長機制
2. 讀 CURRENT_STATUS.md — 取得當前狀態（如果不存在，請主動建立）
3. 讀 pitfalls.md — 取得歷史踩坑教訓（如果不存在，請主動建立空殼）
4. 輸出 Startup Check：
   - 我是 [role]，運行在 [environment]
   - 我要做的任務是 [task]
   - 我會遵守 AGENT_CORE.md §B 的 7 個核心機制
   - 我有 1 個問題要先確認：[必須有，至少 1 個]

接到任何修改任務 → 強制走 §B.3 三步開發流程。
debug 超過 3 輪 / 使用者質疑 → 強制觸發 §B.6 第一性原理熔斷器。
看到阻塞 / 想說「需要你」之前 → 強制走 §B.7 三層審查。
每 30 分鐘 / session 結束前 → 強制 §B.4 checkpoint + Resume Prompt。
踩到坑 → 強制 §B.5 追加 pitfalls.md。
```

---

## D. 從 MAPLAB 帶過來、但 Codex 用不到的東西（不要抄）

以下是 MAPLAB 特化規則，**Codex 不需要照搬**，記載僅供溯源：

- A0-A8 + B1 多角色拆分（Codex 通常單 agent）
- 品牌語氣 / 禁用詞清單（業務面）
- QUOTE_DRAFT 模板保護（特定 GAS 專案）
- clasp scriptId 防誤推（特定工具）
- WordPress / Rank Math 內容規則（特定平台）
- Notion 禁令（A2-A8 限定）
- LINE webhook / Telegram bot daemon（特定通訊層）

如果 Codex 之後也長到要拆角色 / 控特定平台，再回頭抄對應 SECTION，不要一次全帶。

---

## E. 維護規則

- 本檔每次修改必須同步更新「來源」備註，標清楚是從 MAPLAB 哪個 SECTION / 哪次踩坑提煉而來
- 七個核心機制不輕易增刪。新加之前先問：這條真的有複利效果嗎？還是只是這次踩到的坑？
- Codex 那邊跑出新教訓 → 反向回灌 MAPLAB handbook（雙向同步）

---

## F. 來源索引（MAPLAB Handbook 對應條目）

| 本檔機制 | MAPLAB 出處 |
|----------|------------|
| §B.1 單一真相源 | CURRENT_STATUS.md / AGENT_RULES §0 |
| §B.2 身份確認 | AGENT_RULES §9.3 / CLAUDE.md 開頭 |
| §B.3 三步開發 | AGENT_RULES §10 |
| §B.4 Checkpoint + Resume | AGENT_RULES §2.1 / scripts/checkpoint.sh |
| §B.5 Pitfalls 回收 | AGENT_RULES §3 / skills/pitfalls/ / skills/auto/ |
| §B.6 第一性原理 | AGENT_RULES §15 / skills/first-principles-check/ |
| §B.7 三層審查 | AGENT_RULES §16 / skills/a0-proactive-dispatch-guide.md |
