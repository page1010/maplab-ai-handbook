# 存檔技能（save-checkpoint）

## 觸發條件
Owner 說「存檔」「存一下」「記下來」「先存」或 session 即將結束時。

## 流程（依序執行）

### Step 1：判斷存什麼
根據當下情境判斷類型：

| 情境 | 類型 | 存放位置 |
|------|------|----------|
| 討論完一個計畫/目標/方向 | 計畫存檔 | 更新或建立 Task Card（handoff/tasks/T-AX-*.md） |
| 做完一個程式碼/文件改動 | 改動存檔 | 直接走 checkpoint.sh |
| 確定了一個決策/偏好/為什麼不用 X | 決策存檔 | 追加 decisions.md + checkpoint.sh |
| session 要結束了 | 收尾存檔 | 更新 Task Card 接續點 → checkpoint.sh |
| Owner 要記住的個人偏好/工作習慣 | 記憶存檔 | 寫入 memory/ |

### Step 2：寫入正確位置

#### 計畫存檔
1. 確認 Task Card 是否存在 → 不存在則建立
2. 更新 Task Card 的：
   - **狀態**（🔲 待開始 / 🔄 進行中 / ✅ 完成）
   - **接續點**（做到哪、下一步是什麼）
   - **阻塞**（等誰、等什麼）
3. 如果涉及重大方向決策 → 同時追加 decisions.md

#### 改動存檔
1. 直接跑 checkpoint.sh

#### 決策存檔
1. 追加到 decisions.md，格式：
```
### [角色]-[主題]: [決策描述]
- **背景**: 什麼問題
- **試過**: 方案 A → 失敗原因
- **決定**: 方案 B → 為什麼
- **日期**: YYYY-MM-DD
```
2. 跑 checkpoint.sh

#### 收尾存檔
1. 更新 Task Card 接續點（寫清楚下一個 session 要從哪接）
2. 如果有未記錄的決策 → 追加 decisions.md
3. 跑 checkpoint.sh

#### 記憶存檔
1. 寫入 memory/ 對應的記憶檔
2. 更新 memory/MEMORY.md 索引
3. 跑 checkpoint.sh

### Step 3：執行 checkpoint.sh
```bash
# A1 系統操作 → --fast
bash scripts/checkpoint.sh "角色名" "做了什麼" --fast

# 其他角色業務改動 → 預設 branch 模式
bash scripts/checkpoint.sh "角色名" "做了什麼"
```

### Step 4：回報
告訴 Owner：
- 存了什麼（哪個檔案、什麼內容）
- commit hash
- 如果是 branch 模式 → 提醒 Owner 需要 approve

## 注意事項
- 存檔前先確認 Task Card 的接續點描述夠詳細（下一個 agent 能看懂）
- 不要存已經在程式碼裡可以看到的東西（如函式名、檔案路徑）
- decisions.md 只存「為什麼不用 X」這種不從程式碼看得出來的決策
- 記憶只存跨 session 有用的資訊，當前 session 的進度用 Task Card
