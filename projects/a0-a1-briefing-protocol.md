# A0/A1 雙向 Briefing + 抽考機制設計文件

> 版本：v1.0 | 2026-04-17 | Owner 指示設計
> 目標：讓 A0 session 砍了，5 分鐘內下一個 A0 能接上，且 A1 能驗證理解程度

---

## 一、問題定義

### A0 每次失憶的具體代價

| 事件 | 代價 |
|------|------|
| 2026-04-10：A0 沒讀前人結論，開 8 個 worktree 重新分析 | Owner 糾正 3 輪，浪費整個 session |
| 2026-04-11：worktree commit 沒合回 main，說「已完成」 | bot 功能實際沒上，Owner 下次 session 才發現 |
| 2026-04-17：A0 測試 A6 沒標記 [QA-TEST] | 下一個 A0 以為是真實客戶報價，判斷錯誤 |
| 每次 session 重新解釋 Owner 的三個問句訓練方法論 | Owner 校正成本線性累積 |

**根本問題：A0 的 auto-memory 恢復的是靜態知識，不是最新的 Owner 校正。Owner 說的話只活在對話記憶裡，session 砍了就消失。**

### 現有 auto-memory 的不足

1. **寫入時機不可靠** — 依賴 A0 主動寫，忙的時候忘
2. **內容粗粒度** — 只寫原則，不寫具體的 Owner 原話、commit hash、觸發事件
3. **無法驗證** — A0 說「我已讀取記憶」但 A1 無法確認理解程度
4. **單向** — A0 讀記憶，但 A1 不知道 A0 讀了什麼、讀進去了什麼

---

## 二、雙向 Briefing 機制

### 2.1 A1 → A0：`handoff/a0-briefing.md` 格式規範

```markdown
# A0 冷啟動 Briefing
> 寫入時間：YYYY-MM-DD HH:MM | 寫入者：A1 | 對應 commit：{hash}

## 當前系統狀態（最高優先）
- 進行中任務：{T-ID} {名稱} — {一句話說明目前卡在哪}
- 上次 Owner 校正：{日期} — {原話摘要，保留關鍵詞}
- 最新 commit：{hash} — {做了什麼}

## 未完成清單（A0 接手後繼續的）
- [ ] {任務描述} — 接續點：{具體位置}
- [ ] {任務描述} — 接續點：{具體位置}

## 系統狀態變更（A0 必須知道的架構異動）
- {日期}：{什麼改了} — 影響：{誰受影響，怎麼受影響}

## Owner 校正歷史（最近 3 次）
1. {日期} — {校正內容} — 出處：{commit hash 或 session log}
2. {日期} — {校正內容}
3. {日期} — {校正內容}

## A1 給 A0 的操作提示
- 現在不要碰：{具體哪個 bot/script/GAS，原因}
- 優先處理：{待辦 + 原因}
```

### 2.2 A0 → A1：`handoff/a1-briefing.md` 格式規範

```markdown
# A1 接收 Briefing
> 寫入時間：YYYY-MM-DD HH:MM | 寫入者：A0 | session 時長：{小時}

## 本 session 完成了什麼
- {操作描述} — commit：{hash}
- {操作描述} — commit：{hash}

## 未完成清單
- [ ] {任務} — 卡在：{原因}
- [ ] {任務} — 下一步：{具體動作}

## Owner 本 session 說了什麼（原話記錄）
> "{Owner 原話 1}" — 日期 {時間}
> "{Owner 原話 2}" — 日期 {時間}

## 測試記錄
- {日期} [QA-TEST]：{測試了什麼} — {結果}
- {日期} [PROD]：{真實客戶操作} — {結果}

## 發現的問題（A1 需要處理的）
- {問題描述} — 嚴重程度：P0/P1/P2
```

### 2.3 觸發時機

| 角色 | 寫 briefing 的時機 | 讀 briefing 的時機 |
|------|-------------------|-------------------|
| A0 | session 結束前（必做） | 冷啟動時（第一步） |
| A1 | 完成重要系統操作後（每次 checkpoint 同步更新） | A0 請求抽考時 |

**讀的優先順序：**
- `handoff/a0-briefing.md` > `auto-memory/MEMORY.md` > `recalls/A0_recall.md`
- 三者衝突時：briefing 勝出（因為最新）

### 2.4 Briefing 必須包含的四個要素

每份 briefing 必須包含（缺一不可）：

1. **Owner 校正原話** — 不能只寫「Owner 說要更好」，要寫「Owner 說：『先查 session log 再讀 code，你不記錄 = 系統錯誤』」
2. **commit hash** — 每個重要操作都要有 hash，讓下一個 agent 能 `git show {hash}` 確認
3. **未完成清單** — 具體到「哪個檔案第幾行還沒改」，不能只寫「A6 還有問題」
4. **系統狀態變更** — 例如「GAS endpoint 換了新 URL」、「A6 的 Python 備援邏輯已啟用」

---

## 三、A1 抽考 A0 機制

### 設計原則

1. **必須具體回答**：不接受「我理解了」，必須給出具體數字/名稱/流程步驟
2. **可從文件驗證**：A1 能查哪個文件第幾段來判斷對錯（A0 說什麼不算，A1 獨立核對）
3. **三個層次**：系統架構（邊界）/ 操作知識（技能書）/ Owner 校正歷史（記憶）
4. **隨機抽取**：每次從題庫隨機抽 3 題，不能讓 A0 背答案

---

### 抽考題庫（20 題）

---

#### 【層次一：系統架構】— 答錯 = 還沒理解系統邊界（6 題）

**Q01｜A6 報價流程的完整路徑**
> A6 的報價流程經過哪幾個系統？按順序畫出來（不能省略任何一層）。

**標準答案：**
```
Telegram（客戶輸入） 
→ bot_a6.py（Python 接收，觸發 claude -p） 
→ claude -p（純文字輸出報價 JSON） 
→ bot_a6.py（解析 JSON，POST 到 GAS） 
→ createQuote（GAS function，建立 Sheet copy） 
→ generateProposalV2（GAS，填資料到 Slide） 
→ Slide URL 回傳到 Telegram
```
驗證出處：`docs/a0-dispatch-operations-manual.md` 第一節架構圖

---

**Q02｜claude -p 的能力邊界**
> `claude -p` 能做什麼、不能做什麼？各列出至少 2 項。

**標準答案：**
- 能做：產文字/JSON、讀注入的 prompt 內容、判斷報價邏輯
- 不能做：用 MCP、操作 Google Sheets/Drive、直接呼叫 GAS、讀系統環境變數、做任何 tool call
- 特性：print mode，每次呼叫是獨立 subprocess，無持久狀態

驗證出處：`docs/a0-dispatch-operations-manual.md` 運行環境說明表

---

**Q03｜Owner 的三個操作入口**
> Owner 有哪三個入口操作 MAPLAB 系統？每個入口能召喚哪些角色？

**標準答案：**
- Chrome Extension → 召喚 A2-A8（注入 recall 到側邊欄，不能召喚 A0/A1）
- Telegram Bot → A1（系統總管，Claude Code terminal）、A6（報價助手，claude -p）
- Cowork Dispatch → A0（總調度，委派 Code Task 給 A1 執行層）

驗證出處：`docs/a0-dispatch-operations-manual.md` 入口×角色對照表

---

**Q04｜bot_a6.py 的 GAS 觸發條件與失敗處理**
> bot_a6.py 在什麼條件下觸發 GAS？如果觸發失敗，系統應該怎麼做？

**標準答案：**
- 觸發條件：claude -p 輸出包含有效 JSON，bot_a6.py 解析成功後 POST 到 GAS endpoint
- 失敗時必須做：回傳明確錯誤訊息（實際 HTTP status code + error body），不能靜默回傳 None
- 原因：靜默失敗 = AI 幻覺空間（2026-04-11 踩坑：Claude 自己猜測「GAS endpoint 需重新部署」）

驗證出處：`docs/a0-dispatch-operations-manual.md` 踩坑記錄 2026-04-11（晚）

---

**Q05｜launchd bot 讀哪個 branch**
> launchd 管理的 bot_a6.py，讀的是 repo 哪個 branch 的程式碼？

**標準答案：**
- launchd 讀的是 **main branch** 的檔案
- worktree 操作對 launchd 不可見
- 改 bot/scripts/recalls 後必須 cherry-pick 到 main + push origin main 才會生效
- Code task 結束後必須驗證：`git log main --oneline -3` 確認 commit 在 main

驗證出處：`docs/a0-dispatch-operations-manual.md` 踩坑記錄 2026-04-11

---

**Q06｜A0 和 A1 的核心差異（能力互補）**
> A0 有手但沒持久記憶，A1 有持久記憶但沒手。各自能做什麼、不能做什麼？

**標準答案：**
- A0（Cowork）：有手 — Chrome MCP / 桌面控制 / Gmail / Drive / Notion；沒有：持久記憶（每次 session 歸零）
- A1（Claude Code terminal）：有腳 — git / API / MCP / 改 code；沒有：看 Chrome、點 UI、操作桌面 app
- 設計方向：不互換，而是 A1 作為 A0 的持久記憶層，A0 作為 A1 的手

驗證出處：`docs/system-evolution-stories/2026-04-17-a0-a1-role-design.md` A0/A1 核心矛盾表

---

#### 【層次二：操作知識】— 答錯 = 技能書沒讀懂（8 題）

**Q07｜缺資訊時的報價原則**
> 客戶只說「展覽館要五個鹹點」，沒給地址和時間，A6 應該怎麼做？

**標準答案：**
- 地址填「待確認」，車馬費填 $0，先出報價
- 不要卡住等地址，不要問完整才開始報
- 原則：先出報價，後補資訊（缺非關鍵欄位不阻擋報價）
- 「展覽館」是場地類型，不是觸發卡住的理由

驗證出處：`recalls/A6_recall.md` 缺資訊處理原則段落

---

**Q08｜A6 訓練三件套 + 三個問句對照**
> A6 training 的三件套是什麼？分別對應 Owner 的哪三個類比問句？

**標準答案：**
- 操作手冊 ← Q1 會計系統（科目表 + 操作 SOP = 操作路徑）
- 踩坑記錄 + 錯誤處理表 ← Q2 政府系統（繞路地圖 = 所有坑都記下來）
- safety boundaries / checklist ← Q3 機械手臂（hard limit + pre/post 驗證）

驗證出處：`docs/business-requirements/a6-training-methodology.md` 三個問題段落

---

**Q09｜車馬費計算公式**
> 車馬費的計算公式是什麼？有哪些例外情況？

**標準答案：**
- 公式：`max(公里數 × $6, 行車分鐘 × $50)`
- 例外：缺地址時填 $0（待確認後補）
- 不能自己猜距離或用預設值

驗證出處：`recalls/A6_recall.md` 或 `skills/a6-*.md`

---

**Q10｜createQuote 失敗時的回報格式**
> createQuote GAS 呼叫失敗時，A6 應該回報什麼？不應該回報什麼？

**標準答案：**
- 應該回報：實際 HTTP status code + error message body（原文）
- 不應該回報：推測其他系統的狀態（「GAS 可能掛了」「Sheets 權限可能有問題」）
- 原則：眼見為憑 — 只報你看到的，不推測你看不到的

驗證出處：`docs/a0-dispatch-operations-manual.md` 踩坑 2026-04-11（晚）

---

**Q11｜is_active = FALSE 的品項能不能報價**
> Items 表裡 `is_active = FALSE` 的品項，A6 報價時能不能用？

**標準答案：**
- 不能用。`is_active = FALSE` 代表已停售/停用
- A6 只能從 `is_active = TRUE` 的品項選取
- 如果客戶指定的品項 is_active = FALSE，應告知客戶該品項不可用，提供替代品

驗證出處：`recalls/A6_recall.md` 或 `handoff/maplab-master-data.md`

---

**Q12｜委派任何角色前的 7 問題**
> A0 委派 Code task 前必須回答哪 7 個問題？（按順序）

**標準答案：**
1. 我們是誰（哪個 Agent，跑在什麼介面，能力邊界）
2. 我們前面做了什麼（上一個 session 的結論）
3. 我們接下來要做什麼（具體任務，一句話）
4. 我們為什麼要做（使用者需求，不是技術原因）
5. 這在系統運行中代表什麼（從 Owner 操作視角看這個環節）
6. 回到第一性原理：有更快達成目的的辦法嗎？
7. 如果沒有，我們從哪裡繼續（具體接續點：檔案/函數/commit）

驗證出處：`docs/a0-dispatch-operations-manual.md` 第二節委派協議

---

**Q13｜Chrome 眼見為憑的具體操作**
> 改了 GAS 之後，A0 或 A1 必須用 Chrome 做什麼才算「眼見為憑」？

**標準答案：**
- 改 GAS → 開 GAS 編輯器確認程式碼確實在（不只看 terminal 說「clasp push 成功」）
- 改 bot → Telegram Web 發測試訊息確認實際行為
- 改 Sheet → 開 Sheet 確認資料/公式正確
- 原則：不能只看 terminal 輸出，必須看使用者會看到的東西

驗證出處：`docs/a0-dispatch-operations-manual.md` 三點五節標準動作

---

**Q14｜[QA-TEST] 標記的用途**
> A0 在 Telegram 測試 A6 時，為什麼必須標記 [QA-TEST]？後果是什麼？

**標準答案：**
- 原因：Telegram 對話不分真實客戶和測試，下一個 A0 session 看到同樣的對話會誤判
- 2026-04-17 教訓：A0 測試 A6 沒標記，下一個 A0 以為是真實客戶報價，做出錯誤判斷
- 規則：所有測試訊息在 session log 必須標 [QA-TEST]，在 Telegram 對話裡發 [QA-TEST] 前綴

驗證出處：`docs/a0-dispatch-operations-manual.md` 踩坑記錄 2026-04-17

---

#### 【層次三：Owner 校正歷史】— 答錯 = 記憶沒恢復（6 題）

**Q15｜2026-04-17 A6 故障根因**
> 2026-04-17 A6 故障的完整根因鏈是什麼？（不是只說「OAuth 過期」）

**標準答案：**
1. Google OAuth token 過期
2. claude -p 呼叫 GAS 失敗，但靜默回傳（沒給明確錯誤）
3. Claude 幻覺填補靜默失敗，誤判「GAS endpoint 需重新部署」
4. Python 備援觸發邏輯有 bug，備援沒有啟動
5. 整條鏈斷掉，但表面上看起來「好像有在跑」

驗證出處：`docs/system-evolution-stories/2026-04-17-a0-a1-role-design.md` A6 故障相關段落

---

**Q16｜「眼見為憑」的具體含義 + 違反例子**
> Owner 說「眼見為憑」的具體含義是什麼？給一個實際違反的例子。

**標準答案：**
- 含義：只報你直接觀察到的（status code、error message、截圖），不報你推測的（「可能是」「應該是」）
- 違反例子：A6 Claude 說「GAS endpoint 需重新部署」— 實際上只看到 bot 回傳 None，GAS 狀態完全不知道
- 另一個違反例子：Code task 說「已 commit + push」就假設功能生效 — 實際上 commit 在 worktree branch，main 還是舊的

驗證出處：`docs/a0-dispatch-operations-manual.md` 踩坑記錄 + 判斷框架原則 6

---

**Q17｜「不記錄 = 系統錯誤」的觸發事件**
> Owner 說「不記錄 = 系統錯誤」，這句話的觸發事件是什麼？

**標準答案：**
- 觸發事件：2026-04-17，A0 透過 Telegram Web 測試 A6 報價流程，但沒有記錄測試結果
- 後果：下一個 A0 session 看到 Telegram 對話，誤以為是真實客戶報價，做出錯誤判斷
- 設計結論：測試沒記錄 = 系統無法區分測試和真實，等於系統錯誤

驗證出處：`docs/a0-dispatch-operations-manual.md` 踩坑記錄 2026-04-17

---

**Q18｜Owner 定義的兩層改進框架**
> Owner 在 A6 訓練方法論裡定義的兩層改進框架是什麼？

**標準答案：**
- 第一層：A6 業務思維改進 — 讓 A6 真的懂怎麼報價（操作手冊 + QA 範例 + 安全框架）
- 第二層：系統可重複工具改進 — 讓整個報價流程能被任何 Agent 用，不依賴某一次設定

驗證出處：`docs/business-requirements/a6-training-methodology.md`

---

**Q19｜「先查 session log 再讀 code」的原因**
> Owner 說「先查 session log 再讀 code」。為什麼這個順序很重要？

**標準答案：**
- Code 只回答 how（程式怎麼寫），不回答 what actually happened（系統實際怎麼跑）
- 2026-04-10 的教訓：A0 讀 code 就斷定「A6 是文字生成器」，但 Owner 已確認 A6 報價品質 OK（毛利率 79.7%）
- 正確做法：先用 list_sessions + read_transcript 查最近 session 結論，從那裡接著驗證
- 時間權重：最近 session 結論 > 一週前的文件 > code 結構推測

驗證出處：`recalls/A0_recall.md` 判斷框架原則 1 + `docs/a0-dispatch-operations-manual.md` 踩坑記錄 2026-04-10

---

**Q20｜Palantir FDE 方法論在 MAPLAB 的對應**
> Palantir FDE 部署方法論和 MAPLAB 三件套訓練法，有哪三個共通原則？

**標準答案：**
1. 教操作路徑，不教理論（FDE 跟著操作者走流程 = 三問句引導操作手冊）
2. 所有失敗都是系統資產（記錄繞路和踩坑 = 踩坑記錄 + 錯誤處理表）
3. 設框架讓 AI 在框框裡操作（hard limit = safety boundaries）

驗證出處：`docs/business-requirements/a6-training-methodology.md` Palantir 延伸段落（v1.1）

---

### 抽考執行協議

```
A0 冷啟動
    ↓
讀 handoff/a0-briefing.md（A1 寫的）
    ↓
輸出 Startup Check（我是誰 / 接續點 / 第一件事）
    ↓
A1 從題庫隨機抽 3 題（跨三個層次各至少 1 題）
    ↓
A0 回答（必須包含具體數字/名稱/流程步驟）
    ↓
A1 用系統文件核對答案（獨立核對，不靠 A0 自己說對不對）
    ↓
3 題全對 → 通過，開始工作
有錯 → A1 指出錯在哪，給正確答案出處（哪個文件哪一段），要求重讀後再答
    ↓
不能跳過抽考直接開工
```

**A1 抽題規則：**
- 每次從 Q01-Q20 中隨機選 3 題
- 必須跨三個層次（層次一至少 1 題、層次二至少 1 題、層次三至少 1 題）
- 同一個 session 不重複出同一題
- A1 先確認自己手上有正確答案出處，才能判對錯

---

## 四、實作計畫

### Phase 1：建立 briefing 檔案格式 + 抽考題庫（本文件完成後）

- [ ] 建立 `handoff/a0-briefing.md` 初始版本（由 A1 填寫）
- [ ] 建立 `handoff/a1-briefing.md` 範本
- [ ] 本文件 `projects/a0-a1-briefing-protocol.md` — ✅ 本次完成

### Phase 2：修改 A0 recall 冷啟動流程

修改 `recalls/A0_recall.md` 的【啟動流程】段落，加入：

```
【啟動流程 — 必須依序執行】
0. 讀 handoff/a0-briefing.md — 恢復 A1 給的最新狀態
1. 讀 auto-memory/MEMORY.md — 補充靜態知識
2. 開 Code task → git pull → 讀 CURRENT_STATUS.md
3. 比對記憶 vs GitHub，有差異就更新
4. 輸出 Startup Check（我是誰 / 接續點 / 第一件事）
5. 通知 A1 準備抽考，等抽考通過才開工
```

### Phase 3：修改 A1 recall（加入 briefing + 抽考職責）

修改 `recalls/A1_recall.md`，加入：

```
【A0 協作職責 — 防失憶機制】
- 每次重要 commit 後更新 handoff/a0-briefing.md
- A0 冷啟動請求時：從 Q01-Q20 隨機抽 3 題（跨三層次）
- 用系統文件核對答案（不靠 A0 自說對不對）
- 有錯：指出錯誤 + 給出處，要求重讀後再答
- 如果 A0 試圖跳過抽考：回報 Owner
```

---

## 五、防繞過機制

| 繞過方式 | 防護設計 |
|---------|---------|
| A0 說「我已經理解了，可以開工嗎？」 | 不接受，必須回答具體問題 |
| A0 給模糊答案（「大概是 X 流程」） | 答案必須包含具體數字/名稱/步驟，A1 對照文件核對 |
| A0 每次猜到 A1 會問哪題 | 20 題隨機抽 3 題，A1 不預先告知 |
| A0 說「這題文件裡沒有明確答案」 | 每題都有標準答案出處，A1 能獨立核對 |
| A0 跳過抽考直接說「我知道了我去做了」 | A1 明確拒絕，記錄嘗試繞過，回報 Owner |
| briefing 過時沒更新 | A1 每次 checkpoint 後更新，briefing 有時間戳，A0 能判斷是否過時 |

**A1 的判斷標準（不靠 A0 自己說）：**
- A1 讀文件原文，對照 A0 的答案
- A1 不問「你是不是理解了？」，只問「這個具體情況應該怎麼做」
- 答案有差異 → 給出處讓 A0 重讀，不是口頭解釋

---

## 變更記錄

| 版本 | 日期 | 內容 |
|------|------|------|
| v1.0 | 2026-04-17 | Owner 指示設計，初版建立（20 題題庫 + 雙向 briefing 格式 + 防繞過機制） |
