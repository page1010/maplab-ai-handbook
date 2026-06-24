# Skill: session-lifecycle — Session 開始 + 結束規則

## 觸發條件

- 每個新 session 開始時（強制）
- 每次有意義的變更後（強制）
- Session 結束前（強制）

---

## 開始規則（Session Start）

**必做，不可省略：**

1. 讀 `CURRENT_STATUS.md` — 了解最新系統狀態
2. 執行目錄確認：
   ```bash
   ls scripts/     # 確認現有腳本，避免重複建立
   ls skills/      # 確認現有 skill
   ```
3. 讀 `handoff/session-notes/` 最新一份 — 了解上個 session 的斷點
4. 輸出 Session Start 摘要：
   - 當前最高優先任務
   - 上個 session 留下的 pending 事項
   - 本 session 預計完成項目

---

## 變更後規則（After Meaningful Change）

**每次完成有意義的變更，立即執行一個指令：**

```bash
bash scripts/checkpoint.sh "角色名" "做了什麼"
```

腳本自動處理：`git add -A` → `commit` → `cherry-pick 到 main` → `push` → 驗證

commit message 會自動格式化為：`checkpoint(角色名): 做了什麼`

1. **更新 `CURRENT_STATUS.md`** 後再跑 checkpoint（確保狀態也被 commit 進去）
2. 不需要手動 cherry-pick、不需要手動 push，腳本全包

**什麼叫「有意義的變更」：**
- 新增或修改任何 `.py` / `.gs` / `.js` 腳本
- 新增或修改 skill（`skills/` 目錄）
- 新增或修改 task card（`handoff/tasks/`）
- 修改 `AGENT_RECALL_PROMPTS.md` / `CURRENT_STATUS.md` / `AGENT_RULES.md`
- 任何應該被下一個 session 繼承的資訊

---

## 結束規則（Session End）

**Session 結束前，執行最後一次 checkpoint：**

```bash
bash scripts/checkpoint.sh "角色名" "Session 結束摘要"
```

若無新變更（`ℹ️ 沒有需要存檔的變更`），則額外確認：

```bash
bash scripts/verify-commit-on-main.sh  # 確認上次 commit 已在 main
```

接著：
1. 更新 `AGENT_RECALL_PROMPTS.md` 你的角色段落（## AX 下的 code block），寫入最新的斷點狀態。這樣 Extension 下次拉取時就是最新進度。
2. 建立 session note（如果本 session 有重要發現/決策）：
   - 路徑：`handoff/session-notes/YYYY-MM-DD-session-[n].md`
6. 輸出 SESSION END 摘要給 Owner：
   - 本 session 完成了什麼
   - 下個 session 應該接續的事項
   - 任何需要 Owner 決策的 blocker

---

## 禁止行為

- ❌ 不准把進度只留在對話裡（對話結束 = 進度消失）
- ❌ 不准等到 session 結束才一次大 commit
- ❌ 不准在沒有 `ls scripts/` 確認的情況下新建腳本
- ❌ 不准 commit 但不更新 CURRENT_STATUS.md

---

## § 資源衛生 — 任務結束即清理（2026-06-24 強制，所有角色）

> **背景**：Owner 觀察到 Claude app 吃 ~20 GB RAM、同名 session 重複開、Chrome tab 不關，是反覆出現的系統問題根源。

### 規則 R1：任務完成即關閉 session，不留 idle

- 任務完成、Handoff Checkpoint 寫完、checkpoint.sh 跑完後，**主動結束 session**，不要讓 Claude 視窗留在 idle 狀態。
- idle session = 佔 RAM 且製造假「進行中」訊號，下次 patrol 會誤判系統狀態。

### 規則 R2：不重複開同名 session

- 開新 session 前先確認**同名任務是否已有進行中 session**（Claude Desktop / Cowork Project 清單）。
- 如果舊 session 還在：**先關舊的，再開新的**，或直接在舊 session 繼續。
- 重複開同名 session = RAM double、context 分裂、兩個 AI 互相覆蓋狀態。

### 規則 R3：自己開的 Chrome 分頁/視窗，任務結束前關掉

- 任何 agent 為了執行任務開的 Chrome 分頁（OpenClaw / 巡查 / 截圖 / GA / GSC 等），**收工前自己關閉**。
- 不要把關分頁的工作丟給 Owner。
- 詳細規範見 `AGENT_RULES.md` §「資源衛生 — Chrome / 瀏覽器 session 用完即關」。
- ⚠️ 例外：Owner 自己開的分頁不碰，但可以提醒「這個分頁是否還需要？」

### 規則 R4：禁止 keep-awake hack

- 不在 Chrome 開影音/倒數頁面讓螢幕/機器保持喚醒。
- 這台 Mac mini 是專職 agent 機，休眠/鎖定已由系統設定控制，不需要 hack。
- 「保持喚醒」類分頁發現即關。

### 規則 R5：長跑 / 背景 session 必須有明確結束條件

- 背景 session（如：Hermes patrol、定時巡檢、Codex monitor）必須在 Task Card 或 CURRENT_STATUS.md 寫明：
  1. **結束條件**（任務 X 完成 / Owner 下指令 / 特定日期）
  2. **交班觸發**（context 滿了誰來接、接手 prompt 在哪）
- 沒有結束條件的背景 session = 幽靈任務，下次 A1 巡檢時列入清理清單。

### 快速 Checklist（任務結束前掃一遍）

```
[ ] checkpoint.sh 已跑（最後一次 commit 落地）
[ ] CURRENT_STATUS.md 已更新
[ ] Handoff Checkpoint 已輸出（或 task complete 已標記）
[ ] 我開的 Chrome 分頁已關
[ ] 沒有留著 idle 的同名 session
[ ] 背景 session 有寫結束條件（若有）
```

---

> 核心原則：下一個接手的 AI 從 GitHub + CURRENT_STATUS.md 就能完整還原系統狀態。
> 任何只存在於對話裡的資訊 = 遺失的資訊。
> 任何留著的 idle session = 消耗資源且污染系統狀態的噪音。
