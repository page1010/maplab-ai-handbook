# AGENT_STARTUP_PROTOCOL.md — 接手前必讀 SOP
**所有 Agent 開始任務前，必須依序完成以下步驟。**
這份文件的目的是解決「每個 Agent 一開始沒有大局觀」和「分頁斷線後記憶歸零」的問題。

> ⚠️ **核心原則：先讀外部記憶，再開始工作。不准依賴聊天上下文判斷專案狀態。**

---

## 啟動流程（7 步驟）

### Step 1. 讀 CURRENT_STATUS.md（最高優先）
這是唯一最新狀態入口。確認：系統版本、當前 Phase、進行中任務、Blockers、Source of Truth 文件清單。
> ⚠️ 若其他文件與 CURRENT_STATUS.md 衝突，以 CURRENT_STATUS.md 為準。

### Step 2. 讀 TASK_QUEUE.md
確認：有哪些待認領任務、你的角色可以做什麼、前置條件是否滿足。

### Step 3. 讀 AGENT_RULES.md
確認：自己的角色編號（A1-A7）、負責範圍、禁止事項。

### Step 4. 讀對應的 Task Card（handoff/tasks/T-xxx.md）
如果你要接手一個進行中任務，讀它的 Task Card 確認：上一個 Agent 做到哪、下一步是什麼、Blockers。

### Step 5. 讀 skills/superpowers-guide.md 路由表 + 必拿技能
查「任務類型 → 建議預讀技能書」，選擇最適合當前任務的技能書。

⚠️ **Superpowers 規則**：
- **必拿**：skills/task-progress-guide.md — 所有任務都必須讀，不可跳過
- Agent 產出的文字（commit message、Task Card、CHANGELOG）必須由 Agent 自己撰寫
- GitHub 操作使用網頁版介面（非 CLI），搭配 skills/github-api-workflow-guide.md
- 遇到不會的操作 → 先查 skills/troubleshooting-hub.md → 找不到才回報 A1
- 技能書是工具箱，不是指令集 — 按需取用，不必全讀（task-progress-guide 除外）

### Step 6. 輸出 Startup Check（強制）
完成以上步驟後，**必須**輸出以下格式，等 owner 確認後才能開始執行：

```
Startup Check
- Files read: [你讀了哪些檔案]
- Current version: [系統版本]
- Active task: [你要做的任務 ID + 名稱]
- Confirmed progress: [你理解的當前進度]
- Skills loaded: [從路由表選的技能書，至少 1 本 + task-progress-guide（必拿）]
- Questions for Owner: [至少 1 個問題，確認方向/範圍/優先順序]
- Risks / ambiguities: [你發現的衝突或不確定]
- Proposed scope: [你這輪只做什麼、不做什麼]
```

⚠️ **阻擋規則**：
- Skills loaded 為空 = 不算啟動完成
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

C) [做法名稱]
   ...

你的方向比較偏向哪一種？或者你有想到我沒列的做法？
```

⚠️ **禁止行為**：
- 不要預設 A 是最佳方案 — 排序不代表推薦
- 不要隱藏某個做法的缺點來引導 Owner 選特定選項
- 每個做法的盲點/風險必須誠實寫，不能只寫「可能比較慢」這種空話
- 如果只有一種做法，也要列出該做法的風險，並問 Owner 是否有其他想法

---

## 執行中規則（強制）

### 規則 1：每步紀錄（不可跳過）
每完成一個子步驟，立即用以下格式紀錄。不要等全部做完才寫。

```
Progress Log #[序號]
- Done: [剛完成什麼]
- Result: [結果是什麼，成功/失敗/部分完成]
- Next: [下一步要做什麼]
- Blocker: [卡住什麼，沒有就寫「無」]
```

### 規則 2：子任務切割
如果任務預估超過 5 個步驟，必須先拆成子任務清單，每個子任務有明確的完成條件。
拆完列給 Owner 看，確認順序後才開始執行。

### 規則 3：接續 Prompt 生成
每完成一個子任務（或 session 即將結束時），生成一段接續 prompt，格式：

```
Resume Prompt（貼入新 session 即可接續）
---
角色：[Agent 編號 + 名稱]
任務：[Task ID + 名稱]
已完成：[完成的子任務清單]
下一步：[接下來要做什麼]
必讀檔案：[新 session 需要先讀的檔案]
注意事項：[上個 session 發現的坑或決策]
---
```

### 規則 4：方向偏移檢查
執行中如果發現實際情況跟原本選的做法不同（例如：選了寫程式解決但程式跑不通），必須**立即停下來回報 Owner**，不要自己換方案繼續做。回報格式：

```
方向偏移通知
- 原本做法：[A/B/C + 簡述]
- 遇到的問題：[為什麼行不通]
- 可能的替代方案：[列出選項 + 盲點]
- 需要 Owner 決定：[具體問題]
```

---

## 臨時任務處理規則

Owner 可能交辦不在 TASK_QUEUE 裡的臨時任務。處理方式：

1. 仍然輸出 Startup Check（可以簡化，但 Questions for Owner 和 Skills loaded 不能省）
2. 不需要建立 Task Card，但完成後必須在 CURRENT_STATUS.md「最新決策」區塊登記
3. 如果臨時任務規模大（預估 >10 步驟），建議 Owner 補建 TASK_QUEUE 條目
4. 臨時任務的 commit message scope 用指派的 Agent 編號（例：`data(a1): ...`）

---

## 完成任務後的收尾 SOP

### Step A. 輸出 Handoff Checkpoint（強制）
```
Handoff Checkpoint
- Read: [本輪讀了哪些檔案]
- Changed: [改了哪些檔案 + 做了什麼]
- Confirmed: [確認了什麼事實或決策]
- Next: [下一個接手者該做什麼]
- Blockers: [未解決的阻塞]
- Files to review: [建議下次先看哪些檔案]
```

### Step B. 更新 Task Card
把 Checkpoint 內容寫進 handoff/tasks/T-xxx.md。

### Step C. 更新 TASK_QUEUE.md
把你的任務狀態改為 ✅ 完成（或更新進度）。

### Step D. 更新 CHANGELOG.md
新增一條版本記錄。

### Step E. 回報 owner
完成摘要 + 需要 owner 決策的事項。

> 沒有輸出 Handoff Checkpoint = 不算完成。分頁可以關，但記憶不能丟。

---

## 為什麼這樣設計

| 問題 | 舊做法 | 新做法 |
|------|--------|--------|
| Agent 不知道最新狀態 | 讀 README + BOARD + 很多文件 | 只讀 CURRENT_STATUS.md 一份 |
| 分頁當掉記憶歸零 | 進度只在聊天裡 | 進度在 Task Card + Checkpoint + Resume Prompt |
| 簽到簽退沒人做 | 靠自律 | 強制 Startup Check + Handoff 格式 |
| Agent 讀到舊規則做錯事 | 歷史和當前混在一起 | CURRENT_STATUS 明列已完成事項 |
| 任務無人認領或重複做 | 散落在各處 | TASK_QUEUE 統一管理 |
| Agent 不問問題直接衝 | Startup Check 無阻擋 | Questions for Owner 必填，0 個 = 不能開始 |
| Agent 不拿技能書 | 建議讀但無人驗證 | Skills loaded 必填 + task-progress-guide 必拿 |
| 做法選錯不回報 | 自己換方案繼續做 | 方向偏移必須停下回報 |
| 臨時任務無流程 | 做完不知登記哪裡 | CURRENT_STATUS 最新決策 + 簡化 Startup Check |

---

## 關鍵約束（每次接手前確認）
- .env 金鑰、token、密碼 **絕對不能** 上傳 GitHub
- Google Photos 原始照片 **只讀不刪**
- 不修改 main branch schema without changelog
- GitHub commit 是唯一狀態真相（非 Notion）
- 不假設任務範圍，有疑問先確認

---

*版本：v1.4 | 建立：2026-03-14 | 更新：2026-03-23 | 維護者：A1 Handbook Agent*
*v1.4 變更：Startup Check 新增 Skills loaded + Questions for Owner 強制欄位；Step 7 改為盲點分析格式（禁止預設最佳方案）；新增執行中規則（每步紀錄 + 子任務切割 + 接續 Prompt + 方向偏移檢查）；新增臨時任務處理規則*
*v1.3 變更：新增 Step 7 ABCDE 互動選項 + Superpowers 規則（Step 5）*
*v1.2 變更：Step 1 改為 CURRENT_STATUS.md、精簡為 6 步驟、新增強制 Startup Check + Handoff Checkpoint 格式*
