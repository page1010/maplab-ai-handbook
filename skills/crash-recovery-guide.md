# crash-recovery-guide.md — 當機復原與進度驗證技能書

版本：v1.0 | 建立：2026-03-24 | 維護：A2

## 何時用

- Session 中斷後接手，不確定上一個 Agent 做到哪
- GitHub 記錄（CURRENT_STATUS / TASK_QUEUE）和實際狀態對不上
- Summary 壓縮後可能遺漏或失真
- 任何時候覺得「文件說的 ≠ 系統實際的」

## 核心問題

Agent 執行任務時，如果在「做完事」和「寫回 GitHub」之間當機，就會產生 **進度落差**：

```
實際狀態：WordPress 已上傳 3 張圖、文章已設好精選圖片
GitHub 記錄：CURRENT_STATUS 完全沒提到這些事
```

下一個接手 Agent 只看 GitHub，會以為「什麼都沒做」，可能重做或漏接。

## 第一步：進度驗證 Checklist（接手必做）

接手任務後，**不要直接相信 GitHub 文件**。先跑一遍驗證：

### 1. 比對 Git Commit History

```
查看最近的 commits（看時間戳和 commit message）
→ 能看出上一個 Agent 實際建立/修改了什麼檔案
→ 即使 CURRENT_STATUS 沒更新，commit 本身就是證據
```

怎麼做：到 repo 首頁看 commits，或特定資料夾的 commits

### 2. 比對外部系統實際狀態

每個系統都有自己的驗證方法：

| 系統 | 驗證指令 |
|------|---------|
| WordPress 媒體庫 | `fetch('/wp-json/wp/v2/media?per_page=5&orderby=date&order=desc')` 看最近上傳 |
| WordPress 文章精選圖片 | `fetch('/wp-json/wp/v2/posts?per_page=100&_fields=id,title,featured_media')` 看哪些有圖 |
| GTM | 登入看工作區變更數和最新版本號 |
| Rank Math SEO | 看 Analytics > SEO Performance 最近數據 |
| Google Drive | 直接瀏覽資料夾確認檔案狀態 |
| Google Business Profile | 搜尋商家名稱看產品/照片 |

### 3. 比對 CURRENT_STATUS.md

用步驟 1-2 的實際狀態，和 CURRENT_STATUS.md 的「最新決策」「當前進行中任務」對照：

- ✅ 文件有記錄 + 實際也有 → 正常
- ⚠️ 實際有做但文件沒記錄 → **當機落差，需要補寫**
- ❌ 文件說有但實際沒有 → **可能做到一半中斷，需要完成**

## 第二步：補齊落差

### 發現「做了但沒記錄」

1. 確認具體做了什麼（用 commit history + 外部系統驗證）
2. 補寫 CURRENT_STATUS.md 最新決策
3. 補寫 TASK_QUEUE.md 狀態更新（如有 Task Card 也更新）
4. 在最新決策加上 `[crash-recovery 補登]` 標記，區分正常紀錄

### 發現「記錄說做了但實際沒做」

1. 這代表上一個 Agent 在執行中途斷線
2. 從 commit history 找最後成功的步驟
3. 從那個點繼續執行
4. 在 CURRENT_STATUS.md 標記 `[crash-recovery 接續]`

## 第三步：寫 Checkpoint（防止下一次當機）

### 規則：每完成一個「外部系統操作」就 commit

```
外部系統操作 = 不在 GitHub 上的改變
```

例如：
- 上傳一張圖到 WordPress → 立即 commit 一筆記錄到 GitHub
- 修改 GTM 設定 → 立即 commit
- 更新 Google Business Profile → 立即 commit

### Checkpoint 格式

建議在 handoff/tasks/ 或 CURRENT_STATUS.md 登記：

```markdown
## Checkpoint [YYYY-MM-DD HH:MM] — [Agent ID]

### 已完成（有實際改變的）
- [x] 操作 1：[具體描述] → 證據：[media ID / commit hash / URL]
- [x] 操作 2：[具體描述] → 證據：[同上]

### 進行中（下一步）
- [ ] 操作 3：[具體描述]

### 未開始
- [ ] 操作 4：[具體描述]
```

### 頻率建議

| 情境 | Checkpoint 頻率 |
|------|----------------|
| 一般文件編輯 | 每 3-5 個步驟 |
| 外部系統操作（WordPress / GTM / 廣告） | **每次操作後立即** |
| 批次作業（如上傳 10 張圖） | 每 3-5 張一次 |
| 長時間任務（>30 分鐘） | 每 15 分鐘一次 |

## 第四步：Resume Prompt 加入驗證指令

在生成 Resume Prompt 時，加入驗證步驟讓接手者能快速確認：

```markdown
Resume Prompt（貼入新 session 即可接續）
---
接手驗證（先做這些確認實際狀態）：
1. WordPress: fetch('/wp-json/wp/v2/media?per_page=5&orderby=date&order=desc') 確認最近上傳
2. GitHub: 看 skills/ 資料夾最近 commits 確認技能書狀態
3. 如果和下面的「已完成」不符，參照 crash-recovery-guide.md 補齊
---
```

## 防當機最佳實踐（寫給所有 Agent）

### 原則：先記再做，不要先做再記

```
❌ 錯誤順序：做事 → 做事 → 做事 → 最後一次性記錄（當機 = 全丟）
✅ 正確順序：做事 → 記錄 → 做事 → 記錄 → 做事 → 記錄
```

### 具體做法

1. **開工第一件事**：在 CURRENT_STATUS.md 或 handoff 留下「我開始了」的標記
2. **每個外部操作完成後**：立即 commit 一筆 checkpoint
3. **每 15 分鐘**：評估是否該寫 Resume Prompt（即使還沒做完）
4. **收工最後一件事**：更新 CURRENT_STATUS.md + 寫 Resume Prompt

### Commit Message 格式

```
checkpoint(scope): 簡述已完成的事 + 下一步
```

例如：
- `checkpoint(a2): 已上傳 3 張圖至 WP (ID:1510-1512)，下一步繼續剩餘 44 篇`
- `checkpoint(a2): SEO checklist + ranking guide 建立完成，下一步更新 CURRENT_STATUS`

## MAPLAB 場景對照

| 場景 | 驗證方法 | Checkpoint 重點 |
|------|---------|----------------|
| 上傳圖片到 WordPress | REST API 查 media 最近上傳 | 記錄 media ID + 配對文章 ID |
| 設定文章精選圖片 | REST API 查 posts 的 featured_media | 記錄 post ID + media ID |
| 建立技能書 | GitHub commit history | 記錄 commit hash + 檔名 |
| GTM 標籤設定 | 登入 GTM 看版本號 | 記錄版本號 + 變更內容 |
| SEO 數據記錄 | Rank Math Analytics 截圖/數字 | 記錄基準線數據 |
| Google Business Profile 修改 | 搜尋商家名稱確認 | 記錄修改了什麼 |

## 版本紀錄

| 版本 | 日期 | 說明 | 建立者 |
|------|------|------|--------|
| v1.0 | 2026-03-24 | 初版：進度驗證 4 步驟 + checkpoint 機制 + 防當機最佳實踐 | A2 |
