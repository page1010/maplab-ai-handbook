# Skill: system-audit — 系統巡檢 SOP

## 觸發條件

Owner 說以下任何一種：
- 「巡檢」「系統巡檢」「健檢」「系統健檢」
- 「檢查進度」「盤點一下」「掃一遍」
- 新 session 開始，想做 optional 預檢時

---

## SOP 步驟

### Step 1：Git + 目錄盤點

```bash
git log --oneline -20        # 看最近 20 次 commit
ls scripts/                  # 列出所有腳本
ls skills/                   # 列出所有 skill
ls handoff/tasks/            # 列出所有 task card
ls handoff/session-notes/    # 列出 session notes
```

### Step 2：比對 CURRENT_STATUS.md vs 實際 commit

1. 讀 `CURRENT_STATUS.md` 的「當前進行中任務」表格
2. 對每個「✅ 完成」的任務：
   - 確認對應 task card 存在於 `handoff/tasks/`
   - 確認有對應 commit（git log 或 task card 裡的 commit hash）
3. 對每個「🔄 進行中」的任務：
   - 確認距上次 commit 時間（A1 巡檢規則：超過 48h = WATCH，超過 72h = CRITICAL）

### Step 3：scripts/ 和 skills/ 掃描

- 有無重複功能的腳本？（例如兩個 update-dashboard 腳本）
- 有無 session 裡提到「要建立」但沒 commit 的腳本？
- skill 目錄裡有無只有空殼、沒有實際內容的？

### Step 4：handoff/tasks/ 完成狀態 vs 實際程式碼

- task card 說「✅ 完成」但 commit 裡找不到對應程式碼？ → ⚠️
- task card 說「🔄 進行中」但已有完整程式碼？ → 需更新狀態

### Step 5：輸出巡檢報告

格式：
```
## 巡檢報告 — [日期]

✅ 已正確 commit 的東西：
- [項目] — [commit hash]

⚠️ 應該在但找不到 / 狀態不一致：
- [項目] — [說明]

🗑️ 應該清理的東西：
- [項目] — [原因]
```

### Step 6：修正歸位 + commit

- 補建缺漏的 task card
- 移動舊/誤置的檔案到 `handoff/archive/`
- 更新 CURRENT_STATUS.md
- Commit: `audit(system): [本次巡檢摘要]`
- Push

---

## 注意事項

- 巡檢是唯讀優先：先盤點再動，不要邊盤點邊改
- 不確定要不要刪的檔案 → 先移到 `handoff/archive/`，不要直接刪
- 每個修正批次立即 commit，不要攢到最後
