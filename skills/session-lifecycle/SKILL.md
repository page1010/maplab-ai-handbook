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
1. 建立 session note（如果本 session 有重要發現/決策）：
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

> 核心原則：下一個接手的 AI 從 GitHub + CURRENT_STATUS.md 就能完整還原系統狀態。
> 任何只存在於對話裡的資訊 = 遺失的資訊。
