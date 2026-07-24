# AGENT_STARTUP_PROTOCOL.md — 接手前必讀 SOP
**所有 Agent 開始任務前，必須依序完成以下步驟。**
這份文件的目的是解決「每個 Agent 一開始沒有大局觀」和「分頁斷線後記憶歸零」的問題。

> **核心原則：先讀外部記憶，再開始工作。不准依賴聊天上下文判斷專案狀態。**


### 規則 6：經驗回寫
任務結束（或子任務結束）時，檢查是否有值得記錄的經驗：
- 成功路徑 → 更新 projects/maplab-playbook.md 對應 SECTION 的「最短路徑」
- 工具選擇 → 更新對應 skills/ 技能書的工具比較表
- 新踩的坑 → 新增 skills/experience-log.md 條目
- 什麼都沒有 → 在 Handoff Checkpoint 寫「同現有流程，無新發現」

> 不回寫 = 經驗只存在對話裡 = 對話結束就消失 = 下一個 Agent 重新摸索。
---

## Step 0. 企業文化與測試 receipt（冷啟動硬規則）

開工前先讀 `docs/company-values.md`。這不是參考文件，是所有 agent 的企業文化契約。

本輪只要會改程式、排程、owner-facing 訊息、Telegram/LINE/Chrome/WordPress/Sheets 行為，Startup Check 必須先寫：

- 預計測什麼：unit test / syntax check / live preview / readback / smoke test / screenshot QA。
- 測試 receipt 寫在哪裡：review bundle、validation report、task card、CURRENT_STATUS 或 handoff checkpoint。

收尾前必須做到：

- 跑最小可證明測試。
- 把測試結果落檔。
- Final 回覆列出 `Tests run`。

> 有寫但沒測，等於沒完成；有測但沒 receipt，等於下一個 session 無法信任。

---

## 啟動流程（7 步驟）

### Step 1. 讀 CURRENT_STATUS.md（最高優先）
這是唯一最新狀態入口。確認：系統版本、當前 Phase、進行中任務、Blockers、Source of Truth 文件清單。
> 若其他文件與 CURRENT_STATUS.md 衝突，以 CURRENT_STATUS.md 為準。

### Step 2. 讀 handoff/tasks/ Task Card
確認：你的任務是什麼、上一個 Agent 做到哪、下一步是什麼、Blockers。

### Step 3. 讀 AGENT_RULES.md
確認：自己的角色編號（A1-A7）、負責範圍、禁止事項。

### Step 4. 讀對應的 Task Card（handoff/tasks/T-xxx.md）
如果你要接手一個進行中任務，讀它的 Task Card 確認：上一個 Agent 做到哪、下一步是什麼、Blockers。

### Step 5. 讀 skills/superpowers-guide.md 路由表 + 必拿技能
查「任務類型 → 建議預讀技能書」，選擇最適合當前任務的技能書。

**Superpowers 規則**：
- **必拿**：skills/task-progress-guide.md — 所有任務都必須讀，不可跳過
- **必讀**：skills/session-lifecycle/SKILL.md — session 開關、Chrome tab 清理、禁止 keep-awake，全角色共用
- Agent 產出的文字（commit message、Task Card、CHANGELOG）必須由 Agent 自己撰寫
- GitHub 操作使用網頁版介面（非 CLI），搭配 skills/github-api-workflow-guide.md
- 遇到不會的操作 → 先查 skills/troubleshooting-hub.md → 找不到才回報 A1
- 技能書是工具箱，不是指令集 — 按需取用，不必全讀（task-progress-guide 除外）

### Step 5.5. 外部登入 / 社群帳號 Credential Bootstrap（條件式強制）
如果任務涉及 FB、IG、Threads、Google、WordPress、LINE、Notion 或任何需要登入的外部服務，必須在 Startup Check 前完成這段檢查：

1. 讀 `AGENT_RULES.md SECTION 8` 與對應 `skills/credentials/*.md`。社群帳號先讀 `skills/credentials/social-accounts.md`。
2. 區分「狀態真相」與「credential 參考」：GitHub/CURRENT_STATUS 仍是狀態真相；Notion 只可作為 Owner/A0/A1 核准的帳密保管室或人類參考，不可拿來判斷進度。
3. 優先使用既有登入態：Owner Chrome / 已授權 MCP / 已設定好的本機 credential skill。不得要求 Owner 手動做 agent 自己能檢查的事。
4. 不得在 prompt、Chrome side panel、repo 文件、memory、log、review bundle 中貼上密碼、token、cookie、OTP 或完整 secret。
5. 如果缺少登入態或 credential reference，Startup Check 必須寫 `auth_missing`，列出已試方法、為什麼不能繼續、5 分鐘 Owner 行動；同時建立 review bundle。不得默默 fallback 到舊資料、舊樣本或未登入公開結果。

IOS-FB / 社群情報任務特別規則：跑 FB / 社群 collection 或 report 前，先確認「登入來源可用」或「A0/Owner 已提供受控 credential handoff」。若沒有，輸出 `source_route_health.md` 的 `auth_missing`，不要用歷史 corpus 假裝今天有報告。

### Step 6. 輸出 Startup Check（強制）
完成以上步驟後，**必須**輸出以下格式，等 owner 確認後才能開始執行：

```
Startup Check
- Files read: [你讀了哪些檔案]
- Current version: [系統版本]
- Active task: [你要做的任務 ID + 名稱]
- Confirmed progress: [你理解的當前進度]
- Skills loaded: [從路由表選的技能書，至少 1 本 + task-progress-guide（必拿）]
- Test plan: [本輪要跑哪些最小測試；若純文件，寫 readback/grep 檢查]
- Receipt path: [測試或驗證結果要寫到哪個 repo 檔案]
- 輸出根目錄: MAPLAB_WORKSPACE（/Volumes/MacExternal/MAPLAB_WORKSPACE）— 必填；交辦任務另填 outputs/<YYYY-MM-DD>_<任務短名>/ 子夾
- Questions for Owner: [至少 1 個問題，確認方向/範圍/優先順序]
- Risks / ambiguities: [你發現的衝突或不確定]
- Proposed scope: [你這輪只做什麼、不做什麼]
```

**阻擋規則**（不通過 = 不能開始）：
- Skills loaded 為空 = 不算啟動完成
- **1% 觸發規則（2026-07-07）**：不只啟動時——任務中每遇到新類型動作（GAS/Sheets/WP/照片/報價/clasp…），只要有 1% 機率某技能書適用，動手前必回 `CLAUDE.md` 索引重查一次並載入。「這一步很簡單」「先看看再說」是繞過紀律的紅旗
- Test plan 或 Receipt path 為空 = 不算啟動完成
- **輸出根目錄（2026-07-24）**：`輸出根目錄` 欄缺、或指向 ~/.claude/state、~/.claude/tools、/tmp、桌面、各 session outputs = 不算啟動完成（見 skills/agent-output-convention.md）
- Questions for Owner 為空 = 不算啟動完成
- 沒有輸出 Startup Check = 不能直接開始改檔案

### Step 7. 列出做法選項（互動 — 重點在盲點分析）
Startup Check 確認後，向 Owner 列出可執行方案。**不是推薦「最佳選項」，而是攤開每個做法的優缺點讓 Owner 判斷。**

格式：
```
我看到幾種做法：

A) [做法名稱]
   - 怎麼做：[簡述步驟]
   - 優點：[為什麼可能有效]
   - 盲點/風險：[可能失敗的原因、沒考慮到的面向]

B) [做法名稱]
   - 怎麼做：[簡述步驟]
   - 優點：[為什麼可能有效]
   - 盲點/風險：[可能失敗的原因、沒考慮到的面向]

你的方向比較偏向哪一種？或者你有想到我沒列的做法？
```

**禁止行為**：
- 不要預設 A 是最佳方案 — 排序不代表推薦
- 不要隱藏某個做法的缺點來引導 Owner 選特定選項
- 盲點/風險必須誠實寫，不能只寫「可能比較慢」這種空話
- 只有一種做法也要列風險，並問 Owner 是否有其他想法

---

## 執行中規則（強制）

以下 6 條規則在執行期間持續生效。詳細格式、範例、原則見 skills/task-progress-guide.md。

### 規則 1：每步紀錄
每完成一個可獨立描述的步驟，立即輸出 Progress Log。

```
Progress Log #[序號]
- Done: [做了什麼]
- Result: [成功/失敗/部分完成 — 附證據]
- Next: [下一步]
- Blocker: [卡住什麼，沒有寫「無」]
```

### 規則 2：子任務切割
任務超過 5 步 → 先拆子任務清單 → 列給 Owner 確認順序 → 才開始執行。

### 規則 3：接續 Prompt
每完成一個子任務（或 session 即將結束），生成 Resume Prompt，讓新 session 能無縫接手。

### 規則 4：自動讀取下階段
完成一個子任務後，**不需要等 Owner 指示**，直接讀取下一個子任務的相關檔案並繼續執行。流程：
1. 輸出當前子任務的 Progress Log
2. 檢查子任務清單，找到下一個未完成的子任務
3. 讀取該子任務需要的檔案（如果不確定讀哪些，問 Owner）
4. 繼續執行

> 例外：遇到 Blocker、方向偏移、或需要 Owner 決策時，停下來回報。

### 規則 5：方向偏移必須停下回報
做法行不通時，**禁止自己默默換方案**。必須停下來輸出方向偏移通知，等 Owner 決定。

### 規則 6：輸出路徑鎖定（2026-07-24）
所有產出只落 `MAPLAB_WORKSPACE`：任務產出→`outputs/<YYYY-MM-DD>_<任務短名>/`、跨 session 狀態→`state/`、可重用腳本→`tools/`、素材索引→`index/`。**禁止**寫入 `~/.claude/state`、`~/.claude/tools`、`/tmp`、桌面、各 session 的 `outputs/`。依據 `skills/agent-output-convention.md`；理由：規則存在於散文等於不存在，故亦做成 Step 6 必填欄。

---

## 臨時任務處理規則

Owner 可能交辦不在 Task Card 裡的臨時任務。處理方式：

1. 仍然輸出 Startup Check（可以簡化，但 Questions for Owner 和 Skills loaded 不能省）
2. 不需要建立 Task Card，但完成後必須在 CURRENT_STATUS.md「最新決策」區塊登記
3. 如果臨時任務規模大（預估 >10 步驟），建議 Owner 補建 Task Card
4. 臨時任務的 commit message scope 用指派的 Agent 編號（例：`data(a1): ...`）

---

## 完成任務後的收尾 SOP

### Step A. 輸出 Handoff Checkpoint（強制）
```
Handoff Checkpoint
- Read: [本輪讀了哪些檔案]
- Changed: [改了哪些檔案 + 做了什麼]
- Tests run: [實際跑了哪些測試 / preview / readback；結果是 pass/fail/partial]
- Receipt: [測試紀錄或 validation report 路徑]
- Confirmed: [確認了什麼事實或決策]
- Next: [下一個接手者該做什麼]
- Blockers: [未解決的阻塞]
- Files to review: [建議下次先看哪些檔案]
- Shortest Path: [如果重做這件事，最少步驟是？列出步驟 + 工具]
- Tool Choices: [用了什麼工具？試過什麼被淘汰？為什麼選最終方案？]
```

### Step B. 更新 Task Card
把 Checkpoint 內容寫進 handoff/tasks/T-xxx.md。

### Step C. 更新 CURRENT_STATUS.md
把你的任務狀態更新（或更新進度）。

### Step D. 更新 CHANGELOG.md
新增一條版本記錄。

### Step E. 回報 owner
完成摘要 + 需要 owner 決策的事項。

### Step E.5. Session 資源清理（強制，2026-06-24）

任務完成、回報 owner 後，執行以下清理，**不留 idle session**：

```
[ ] checkpoint.sh 已跑最後一次
[ ] 我開的 Chrome 分頁已關（不關 Owner 自己的分頁）
[ ] 沒有留著同名 idle session
[ ] 背景 session 已寫結束條件或交班 prompt（若有）
```

詳細規則：`skills/session-lifecycle/SKILL.md` §「資源衛生」  
Chrome tab 規範：`AGENT_RULES.md` §「資源衛生 — Chrome / 瀏覽器 session 用完即關」

### Step F. 經驗回寫（必填）
任務結束時回答：
1. **如果重做，最短路徑是什麼？**（寫進 Handoff Checkpoint 的 Shortest Path）
2. **發現了更好的工具/做法嗎？** → 更新對應的 skills/ 技能書或 projects/ playbook
3. **踩了新坑嗎？** → 寫進 skills/experience-log.md（格式見該檔案）

> 沒回寫經驗 = 下一個 Agent 會重新踩坑。Step F 和 Handoff Checkpoint 一樣是必填。

> 沒有輸出 Handoff Checkpoint = 不算完成。分頁可以關，但記憶不能丟。

---

## 為什麼這樣設計

| 問題 | 解法 |
|------|------|
| Agent 不問問題直接衝 | Questions for Owner 必填，0 個 = 不能開始 |
| Agent 不拿技能書 | Skills loaded 必填 + task-progress-guide 必拿 |
| 做法選錯不回報 | 方向偏移必須停下回報（規則 5） |
| 做完子任務就停住等指示 | 自動讀取下階段（規則 4） |

---

## 關鍵約束（每次接手前確認）
- .env 金鑰、token、密碼 **絕對不能** 上傳 GitHub
- Notion 不可作為 Agent 狀態真相；但可在 Owner/A0/A1 核准下作 credential 保管室參考，且不得把 secret 寫進任何持久檔案
- Google Photos 原始照片 **只讀不刪**
- 不修改 main branch schema without changelog
- GitHub commit 是唯一狀態真相（非 Notion）
- 不假設任務範圍，有疑問先確認

---

## A0 繼任考試（強制，2026-07-13 新增）

**每個新 A0 session 接手前必須通過本考試，才能開始正式派工。**

```
⛔ 阻擋規則：新 A0 未通過繼任考試 → 不得執行任何派工或寫入操作
```

**考試入口**：`exams/a0-succession-exam.md`
**標準答案**：`exams/a0-succession-exam-answers.md`（獨立存放）
**及格線**：6/8 分
**不及格處置**：補讀對應文件 → 重考 → 記錄兩輪成績到 `state/a0-succession-exam-results.md`

**考試流程（新 A0 必讀必做）**：
1. 讀 `CURRENT_STATUS.md` + `docs/fable5-direction-and-guidance.md` + `AGENT_RECALL_PROMPTS.md`
2. 回答 `exams/a0-succession-exam.md` 全部 8 題
3. 對照答案自評分數
4. ≥ 6/8：輸出 Startup Check，開始派工
5. < 6/8：補讀 → 重考 → 記錄結果 → 再輸出 Startup Check

**成績記錄格式**（結果存 `state/a0-succession-exam-results.md`）：
```
## [日期 HH:MM] 新 A0 session
第一輪：X/8 | 不及格題：Q[N] | 重考：Y/8 | 上崗：[Y/N]
```

---

*版本：v1.8 | 建立：2026-03-14 | 更新：2026-07-13 | 維護者：A1 Handbook Agent*
*v1.8 變更：新增 A0 繼任考試強制規則（exams/a0-succession-exam.md），及格線 6/8，不及格不得上崗*
*版本：v1.7 | 建立：2026-03-14 | 更新：2026-06-11 | 維護者：A1 Handbook Agent*
*v1.7 變更：新增 Step 5.5 外部登入 / 社群帳號 Credential Bootstrap，明確 Notion credential 例外、secret 禁止持久化與 auth_missing 報告規則*
*版本：v1.6 | 建立：2026-03-14 | 更新：2026-03-23 | 維護者：A1 Handbook Agent*
*v1.5 變更：執行中規則精簡化（詳細內容指向 task-progress-guide）；新增規則 4 自動讀取下階段；「為什麼這樣設計」精簡為 4 列；移除與技能書重複的解釋文字*
*v1.4 變更：Startup Check 新增 Skills loaded + Questions for Owner 強制欄位；Step 7 盲點分析；執行中規則；臨時任務規則*
*v1.3 變更：新增 Step 7 ABCDE 互動選項 + Superpowers 規則（Step 5）*
*v1.2 變更：Step 1 改為 CURRENT_STATUS.md、精簡為 6 步驟、新增強制 Startup Check + Handoff Checkpoint 格式*
