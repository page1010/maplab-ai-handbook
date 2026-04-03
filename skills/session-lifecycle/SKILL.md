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

**每次完成有意義的變更，立即執行：**

1. **更新 `CURRENT_STATUS.md`**：
   - 修改對應任務的狀態
   - 更新「最後更新」時間戳記
2. **Commit + Cherry-pick 到 main + Push**：
   ```bash
   git add -p                    # 選擇要 commit 的變更
   git commit -m "..."           # commit message 包含狀態摘要
   # 如果在 worktree，必須立即 cherry-pick 到 main：
   HASH=$(git rev-parse HEAD)
   cd /Users/pagemacmini/maplab-ai-handbook
   git checkout main
   git cherry-pick $HASH
   git push origin main
   cd -                          # 回 worktree
   # 如果在 main branch，直接 push：
   git push origin main
   ```
3. Commit message 格式：`type(scope): [做了什麼] — [下一步]`
   - type: feat / fix / docs / audit / checkpoint
   - scope: A0-A8 或 system

**什麼叫「有意義的變更」：**
- 新增或修改任何 `.py` / `.gs` / `.js` 腳本
- 新增或修改 skill（`skills/` 目錄）
- 新增或修改 task card（`handoff/tasks/`）
- 修改 `AGENT_RECALL_PROMPTS.md` / `CURRENT_STATUS.md` / `AGENT_RULES.md`
- 任何應該被下一個 session 繼承的資訊

---

## 結束規則（Session End）

**Session 結束前，依序確認：**

1. ✅ 所有進行中的變更已 commit（no uncommitted changes）
2. ✅ `CURRENT_STATUS.md` 反映本 session 最終狀態
3. ✅ 所有 worktree commits 已 cherry-pick 到 main（執行 `bash scripts/verify-commit-on-main.sh` 確認）
4. ✅ `git push` 到 remote 已完成
5. ✅ `git log main --oneline -1` 確認最新 commit 已在 main
5. 建立 session note（如果本 session 有重要發現/決策）：
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
