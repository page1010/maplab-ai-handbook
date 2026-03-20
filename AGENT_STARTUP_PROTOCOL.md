# AGENT_STARTUP_PROTOCOL.md — 接手前必讀 SOP
**所有 Agent 開始任務前，必須依序完成以下步驟。**
這份文件的目的是解決「每個 Agent 一開始沒有大局觀」和「分頁斷線後記憶歸零」的問題。

> ⚠️ **核心原則：先讀外部記憶，再開始工作。不准依賴聊天上下文判斷專案狀態。**

---

## 啟動流程（6 步驟）

### Step 1. 讀 CURRENT_STATUS.md（最高優先）
這是唯一最新狀態入口。確認：系統版本、當前 Phase、進行中任務、Blockers、Source of Truth 文件清單。
> ⚠️ 若其他文件與 CURRENT_STATUS.md 衝突，以 CURRENT_STATUS.md 為準。

### Step 2. 讀 TASK_QUEUE.md
確認：有哪些待認領任務、你的角色可以做什麼、前置條件是否滿足。

### Step 3. 讀 AGENT_RULES.md
確認：自己的角色編號（A1-A7）、負責範圍、禁止事項。

### Step 4. 讀對應的 Task Card（handoff/tasks/T-xxx.md）
如果你要接手一個進行中任務，讀它的 Task Card 確認：上一個 Agent 做到哪、下一步是什麼、Blockers。

### Step 5. 讀 skills/superpowers-guide.md 路由表
查「任務類型 → 建議預讀技能書」，選擇最適合當前任務的技能書。

⚠️ **Superpowers 規則**：
- Agent 產出的文字（commit message、Task Card、CHANGELOG）必須由 Agent 自己撰寫
- GitHub 操作使用網頁版介面（非 CLI），搭配 skills/github-api-workflow-guide.md
- 遇到不會的操作 → 先查 skills/troubleshooting-hub.md → 找不到才回報 A1
- 技能書是工具箱，不是指令集 — 按需取用，不必全讀

### Step 6. 輸出 Startup Check（強制）
完成以上步驟後，**必須**輸出以下格式，等 owner 確認後才能開始執行：

```
Startup Check
- Files read: [你讀了哪些檔案]
- Current version: [系統版本]
- Active task: [你要做的任務 ID + 名稱]
- Confirmed progress: [你理解的當前進度]
- Next suggested step: [你建議的下一步]
- Risks / ambiguities: [你發現的衝突或不確定]
- Proposed scope: [你這輪只做什麼、不做什麼]
```

> 沒有輸出 Startup Check = 不算啟動完成。不能直接開始改檔案。

### Step 7. 列出 ABCDE 選項（互動）

Startup Check 確認後，向 Owner 列出可執行選項，等待指示：

```
請選擇接下來要做什麼：

A) [第一優先任務] — 簡短說明
B) [第二優先任務] — 簡短說明
C) [第三優先任務] — 簡短說明
D) 系統巡查 — 檢查文件一致性、版本對齊
E) 自由指令 — 告訴我你要做什麼
```

⚠️ 具體選項由 Agent 根據 TASK_QUEUE + CURRENT_STATUS 動態生成，不是固定清單。

---

## 執行中規則

### 每完成一個階段，更新 Task Card
不要等「全部做完」才寫。每完成一個小段落就更新：
- Done（做了什麼）
- Next（下一步）
- Blocker（卡住什麼）

### 遇到 Bug → 查 troubleshooting-hub
1. 嘗試 1-2 次自行修復
2. 查 skills/troubleshooting-hub.md
3. 找不到 → 回報格式記錄 → 通知 A1 或 owner

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
|------|-------|-------|
| Agent 不知道最新狀態 | 讀 README + BOARD + 很多文件 | 只讀 CURRENT_STATUS.md 一份 |
| 分頁當掉記憶歸零 | 進度只在聊天裡 | 進度在 Task Card + Checkpoint |
| 簽到簽退沒人做 | 靠自律 | 強制 Startup Check + Handoff 格式 |
| Agent 讀到舊規則做錯事 | 歷史和當前混在一起 | CURRENT_STATUS 明列已完成事項 |
| 任務無人認領或重複做 | 散落在各處 | TASK_QUEUE 統一管理 |

---

## 關鍵約束（每次接手前確認）
- .env 金鑰、token、密碼 **絕對不能** 上傳 GitHub
- Google Photos 原始照片 **只讀不刪**
- 不修改 main branch schema without changelog
- GitHub commit 是唯一狀態真相（非 Notion）
- 不假設任務範圍，有疑問先確認

---

*版本：v1.3 | 建立：2026-03-14 | 更新：2026-03-20 | 維護者：A1 Handbook Agent*
*v1.3 變更：新增 Step 7 ABCDE 互動選項 + Superpowers 規則（Step 5）
v1.2 變更：Step 1 改為 CURRENT_STATUS.md、精簡為 6 步驟、新增強制 Startup Check + Handoff Checkpoint 格式*
