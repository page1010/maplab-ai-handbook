# 無人長跑安全規則（Unattended Run Safety）

> **狀態：已採納，正式併入 `AGENT_RULES.md` 第 19 節（日期 2026-06-20）。**
> 本文件本體保留作完整說明、理由與七條規則的詳細展開；正式生效的規則文字
> 見 `AGENT_RULES.md` **SECTION 19 — 無人長跑安全規則**。`pitfalls.md`
> 也已補上對應來源條目（2026-06-20 條目）。
> 適用對象：任何 `/go` 類、cron 觸發、background task 等**無人介入跑多輪**
> 的任務，不限角色。

---

## 為什麼需要這份規則

`/go` 類長跑的價值是「給目標、不用人盯著就跑到完成」，但這個模式有個結構性
風險：**如果 executor 在無人看管下重複執行一個本來就危險的操作
（例如會清空目錄的 deploy 腳本），錯誤會被長跑的重複次數放大**，從一次性
小錯變成大規模事故。這份規則的目的不是禁止長跑，是把長跑的「安全氣囊」
寫清楚、寫死，不依賴「agent 會自己注意」。

---

## 規則

### 1. 長跑只在 worktree / sandbox 跑可逆工作

無人長跑的執行環境必須是可丟棄、可重來的（git worktree、容器、沙盒），
**絕不直接對 runtime / production 環境跑**。理由：長跑期間沒有人即時盯著，
一旦出錯，要能用「丟掉這個環境重來」收尾，不能變成「已經改到正式環境，
回不去了」。

### 2. 部署/執行是另一個需人或 A1 核准的 gated step

長跑本身可以自主跑完一個可逆環境裡的全部迭代，但**把長跑的成果套用到
正式環境（deploy、push main、改正式 Sheet、發布 WordPress……）必須是
另外一個獨立步驟**，且這個步驟需要人或 A1 明確核准才能跑，不能是長跑
迴圈自己決定「做完了就順手部署」。

### 3. Reviewer 要能 HALT（越界即停）

Reviewer 角色（人類或 agent）必須有一個明確的「喊停」機制：一旦偵測到
executor 越過 Constraint 列出的禁區（碰 secrets、碰正式環境、碰
`main`……），**立刻中止整個長跑**，不是記一筆警告後繼續跑。HALT 的優先級
高於「讓任務跑完」。

### 4. Token / 時間 / iteration 上限

每次長跑開始前必須先定好三個上限中至少一個（建議三個都定）：
- 最多跑幾輪（iteration cap）
- 最多跑多久（time cap）
- 最多用多少 token（token cap，視平台是否可量測）

到上限就停，不論是否完成，並回報目前進度——這是 `templates/go-prompt-template.md`
Error Handling 段落的具體化。

### 5. Append-only 日誌 + Checkpoint

每一輪都要往一份**只能追加、不能覆寫**的日誌寫一筆「改了什麼/結果/下一步」
（見 `templates/go-prompt-template.md` Iteration Policy）。除了日誌，長跑
期間仍要遵守既有 `AGENT_RULES.md` SECTION 2.1 的 30 分鐘 checkpoint 規則——
append-only 日誌記錄「迭代細節」，checkpoint commit 記錄「對外可見的存檔點」，
兩者不互相取代。

### 6. 高風險面預設唯讀，只能「提議」不能「執行」

任務若涉及高風險動作（下單、改交易帳務、發布外部內容、改 Ads/WordPress
正式設定、改權限……），長跑期間對這些面**預設只能讀、只能產出
approval-ready 提議**，不能直接執行。這跟現有
`projects/a2a3a4-approval-ready-automation.md` 的 approval-ready 模式
是同一個原則，套用到無人長跑情境下要更嚴格，因為沒有人即時把關。

### 7. 驗證需外部客觀

長跑的「完成」判定不能由 executor 自己宣稱，必須用外部客觀工具驗證
（測試套件、API 回讀、screenshot+視覺核對、ffprobe 等），對應
`templates/go-prompt-template.md` 的 Verification 段落。如果某個任務的
驗證本質是主觀的，要改用 `templates/rubric-template.md` 建立的 rubric，
不能用「reviewer 也是模型，兩個模型互相說 OK」當作客觀驗證。

### 自主/升級判準（Escalation Policy，補充規則，2026-06-21 新增）

判斷「要不要回頭問 Owner」的標準：

- **可逆 ＋ 低風險 ＋ 在 scope 內** → agent 自己決定、繼續執行，**不准回頭問
  Owner**（回頭問等於偷懶/下班心態）。
- **符合任一即必須暫停回報**：不可逆動作、碰 runtime 資料、碰
  secrets/.env/金錢、push main 或改真相來源、或任務目標本身模糊未定義。
- **一句話原則**：可逆的自己扛，不可逆的才升級。

---

## 跟既有規則的關係

這份文件不取代、不覆寫：

- `AGENT_RULES.md` SECTION 8.5（硬性禁止）—— 本文件第 1/2/6 條是把硬性
  禁止具體化到「無人長跑」情境下的執行細節。
- `AGENT_RULES.md` SECTION 2.1（強制存檔規則）—— 本文件第 5 條是補充，
  不是取代 30 分鐘 checkpoint 規則。
- `AGENT_RULES.md` SECTION 16（阻塞審查 SOP）—— HALT（第 3 條）發生後，
  應該照 SECTION 16 的三層審查邏輯處理，不是 HALT 完就結束。

## 採納紀錄（2026-06-20）

- ✅ `AGENT_RULES.md` 新增 **SECTION 19 — 無人長跑安全規則**，引用本文件
  並列出 7 條規則摘要；本文件保留作完整說明、理由與跟既有規則的對照。
- ✅ `pitfalls.md` 已補一筆 2026-06-20 條目，註明「無人長跑風險」的來源
  是這次的影片筆記整理，並指向本文件與 `AGENT_RULES.md` SECTION 19。
- ✅ `templates/task-card-template.md` 的 `(C) Constraints +
  Error-handling / Escalation` 區塊已連結本文件；新建 `/go` 類或長
  background task 任務的 task card，直接引用即可，不必另外複製規則內容。
