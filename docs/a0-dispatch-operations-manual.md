# A0 調度操作手冊 — 使用者視角 + 系統架構 + 踩坑記錄

> 版本：v1.0 | 2026-04-10 | 來源：Owner 2026-04-10 session 糾正 + A6 訓練三問題方法論推廣
> 目的：讓每個新 A0 session 從使用者視角出發，不再從 code 結構猜測系統行為

---

## 一、系統架構圖 — Owner 的視角

Owner 有三個操作入口，角色和入口之間是多對多關係：

```
                          ┌─────────────┐
                          │  Owner (Page)│
                          └──────┬──────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼────────┐ ┌──────▼──────┐ ┌─────────▼────────┐
     │  Chrome Browser  │ │ Telegram App│ │  Cowork Desktop  │
     │                  │ │  (手機/桌面) │ │  (Mac mini)      │
     └────────┬────────┘ └──────┬──────┘ └─────────┬────────┘
              │                  │                  │
    ┌─────────┴─────────┐       │                  │
    │                   │       │                  │
┌───▼────┐  ┌───────────▼─┐  ┌─▼──────────┐  ┌───▼───────────┐
│Extension│  │ claude.ai   │  │ TG Bot x2  │  │ A0 Dispatch   │
│(召喚器) │  │ 側邊欄      │  │            │  │ (Cowork VM)   │
└───┬────┘  └──────┬──────┘  │ A1: 系統開發│  └───┬───────────┘
    │              │         │ A6: 報價助手│      │
    ▼              ▼         └─────┬──────┘      ▼
 注入 recall    任何角色            │         Code Task
 到側邊欄      (A2-A8)             │         → A1 執行層
 → 召喚任何    via prompt          ▼
   角色                     claude -p terminal
   (除A0/A1)                (Mac mini 常駐)
```

### 入口 × 角色 對照表

| 入口 | 能召喚的角色 | 執行環境 | 特性 |
|------|------------|---------|------|
| Chrome Extension | A2-A8（任何角色） | claude.ai 側邊欄 | 注入 recall prompt；有瀏覽器視覺，能看 Sheet/Web |
| claude.ai 側邊欄 | 取決於 Extension 注入哪個 recall | Claude API | 有網路、有視覺、但不能直接改 repo |
| Telegram Bot (A1) | A1 系統總管 | Claude Code terminal | 能改 repo、跑 API、操作 Sheets；無瀏覽器視覺 |
| Telegram Bot (A6) | A6 報價助手 | Claude Code terminal (claude -p) | 純文字輸出；不能操作 GAS/Sheets/Drive |
| Cowork Dispatch | A0 總調度 | Cowork VM | 有 MCP（Gmail/Drive/Notion/Chrome）；委派 Code Task |
| Code Task (A0 委派) | A1 執行層 | Claude Code worktree | 完整 repo 存取；git 操作；API 呼叫 |

### 運行環境說明

| 項目 | 說明 |
|------|------|
| Claude 方案 | **Max plan**（訂閱制，非 API token 計費）。沒有 per-request token 費用，但有每日使用量上限。密集使用可能觸發暫時限速。 |
| claude -p 特性 | print mode，純文字輸出，無 MCP / tool call。每次呼叫是獨立 subprocess。 |
| 回應時間 | 簡單問候 ~10 秒，報價場景 ~3-6 分鐘（正常，不是當機）。Max plan 無 per-request timeout。 |
| bot_a6 timeout | 600 秒（10 分鐘）。超時自動 kill subprocess 並回報。 |
| 不會發生的事 | API 額度耗盡（Max plan 不按量計費）、per-request 被強制中斷（只有 bot 自己的 timeout 在管） |
| 可能發生的事 | 每日使用量觸發限速（降速但不中斷）、Mac mini 網路不穩（Wi-Fi 斷線 → httpx.ConnectError） |

### 進階場景：同角色多實例

Owner 會讓 A1 用 Chrome Extension 再開一個 A1 來核對自己的工作：

```
場景：A1 自我核對

A1 (terminal) ─── 做完系統修改 ───→ commit
       │
       └── Owner 用 Extension 開新 A1 (Chrome 側邊欄)
                    │
                    └── 新 A1 看 Sheet / Web 核對結果
                              │
                              └── 回報：✅ 正確 / ❌ 發現問題
```

---

## 二、A0 委派前「快速開會」協議

> 來源：Owner 2026-04-10 指正 — A0 開了 8 個 worktree 做錯方向，因為沒有使用者視角

### 委派任何角色前，必須回答 7 個問題：

1. **我們是誰** — 哪個 Agent，跑在什麼介面上，能力邊界是什麼
2. **我們前面做了什麼** — 上一個 session 的結論（不是從零分析）
3. **我們接下來要做什麼** — 具體任務，用一句話說清楚
4. **我們為什麼要做** — 使用者需求是什麼（不是技術原因）
5. **這在系統運行中代表什麼** — 從 Owner 的操作視角看，這個任務在哪個環節
6. **回到第一性原理：有更快達成目的的辦法嗎？**
7. **如果沒有，我們從哪裡繼續？** — 具體的接續點（檔案、函數、commit）

### 範例：正確 vs 錯誤

❌ 錯誤的委派（2026-04-10 實際犯的錯）：
> 「請深度盤查 A6 的架構，讀所有相關檔案，輸出結構化報告」
> → 結果：sub-task 從零分析，斷定 A6 是「文字生成機器」，提議改 LineWebhook.gs

✅ 正確的委派（應該做的）：
> 「A6 是 Telegram 報價 bot，跑在 claude -p terminal。上一個 session Owner 確認回覆品質 OK（毛利率 79.7%），但 createQuote 自動化失敗。請從這個結論接著查：為什麼 A6 無法觸發 createQuote？不要重新分析 A6 是什麼。」

---

## 三、操作路徑表 — Owner 想做 X，怎麼做

| Owner 想做的事 | 用哪個入口 | 觸發哪個角色 | 角色實際能力 | 角色不能做的 |
|---|---|---|---|---|
| 報價：業務收到客戶需求 | Telegram → A6 | A6 報價助手 | 品項草稿、毛利率估算、禁忌識別 | 自動產 Sheet copy、觸發 GAS |
| 報價：產出正式報價單 | Sheet → 按鈕 | GAS (Code.gs) | makeCopy、填資料、回傳 URL | 被 terminal bot 觸發（目前斷裂） |
| 照片分類 | Chrome → Extension → A4 | A4 | 讀 Slides/Drive、分類照片 | — |
| 系統開發/升級 | Telegram → A1 | A1 系統總管 | git、API、MCP、改 code | 看 Sheet 畫面（需 Chrome A1 輔助） |
| 核對 A1 工作 | Chrome → Extension → A1 | A1 (Chrome instance) | 看 Sheet/Web、核對結果 | 改 repo（沒有 git） |
| 跨系統調度 | Cowork → A0 | A0 → Code Task | MCP、委派 A1、桌面控制 | 直接改 GitHub（要委派） |

---

## 三點五、修改程式碼的標準動作（所有 Code task 必讀）

每次修改 bot / GAS / scripts 時，必須遵守以下流程：

**1. 存檔點（改之前）**
- `git log main --oneline -3` 記下當前 commit hash
- 這是復原基準，寫進 session log

**2. 修改 + commit（在 main 上）**
- 確認 `git branch --show-current` = main
- 改完立即 commit + push origin main
- 如果是 worktree，必須 cherry-pick 到 main

**3. Chrome 眼見為憑（改之後）**
- GAS 修改 → 開 GAS 編輯器確認程式碼在
- bot 修改 → Telegram Web 發測試訊息確認行為
- Sheet 修改 → 開 Sheet 確認資料正確
- **不要只看 terminal 輸出，必須用 Chrome 看使用者會看到的東西**

**4. 存檔點（驗證後）**
- commit session log 記錄測試結果
- 標記「驗證通過」或「發現問題」

**5. worktree 特別注意**
- Code task 預設在 worktree 操作
- launchd bot 讀的是 main branch 的檔案
- clasp push 從 worktree 推的程式碼和 main 可能不同
- **改 bot/GAS/scripts 的 task，prompt 裡必須寫「在 main branch 上操作」**

---

## 四、踩坑記錄 — 做錯了就記在這裡

### 2026-04-10：A0 從 code 推論系統行為（3 輪糾正）

| 錯誤 | 為什麼錯 | 正確做法 |
|------|---------|---------|
| 讀 code 就斷定「A6 是文字生成器」 | Owner 已確認回覆品質 OK | 先查 session log，再讀 code |
| 提議改 LineWebhook.gs 加報價路由 | LINE 和 Telegram 是完全獨立系統 | 先畫系統邊界圖 |
| 開 8 個 worktree 各自分析 | Owner 看不到，每個都從零開始 | 先讀前人結論，最多 2 個 task |
| 沒有使用者視角就派任務 | A0 在技術世界打轉 | 委派前跑 7 問題 pre-check |

### 2026-04-11：Worktree commit 沒合回 main（功能不存在）

| 錯誤 | 為什麼錯 | 正確做法 |
|------|---------|---------|
| build task 說「已 commit + push」就假設生效 | Code task 在 worktree branch commit，push 到 remote 的是 worktree branch，不是 main | 每個 task 結束後 A0 驗證：git log main --oneline -3 |
| bot_a6.py 改了但 bot 沒有新功能 | launchd 跑的 bot 讀 main branch 的檔案，worktree 修改對它不可見 | task prompt 必須明確要求「cherry-pick 到 main + push origin main」 |
| 重複發生（build + heartbeat + docs 三次） | A0 沒有 post-verify 流程 | 改 bot/scripts/recalls 的 task，結束後必須用 Chrome 或 Code task 做 post-verify |

**Worktree 使用規則（新增）：**
- Code task 會自動在 worktree 裡操作。如果改的是 main branch 上需要生效的檔案（bot_a6.py、recalls/、scripts/ 等），task prompt 裡必須包含：「確認在 main branch 上操作，或 cherry-pick 到 main」
- launchd 管理的 bot 只讀 main branch，worktree 修改對它不可見
- A0 不要假設「task 說成功了就是成功了」— 每次都要 post-verify
- 如果不確定 commit 在哪個 branch，跑 git branch --contains <hash> 確認

---

## 五、訓練方法論 — 從 A6 推廣到所有角色

> 來源：Owner 2026-04-09 a6-training-methodology.md

### 核心原則：教操作路徑，不教理論

| 場景 | 教什麼 | 不教什麼 |
|------|--------|---------|
| 會計系統 (Q1) | 科目表 + 分錄範例 + 操作 SOP | 會計原理 |
| 政府系統 (Q2) | 繞路地圖 + 錯誤處理表 + 踩坑記錄 | 系統設計邏輯 |
| 機械手臂 (Q3) | checklist + pre/post 驗證 + hard limit | 醫學知識 |
| **A0 調度 (推廣)** | **使用者場景表 + 委派協議 + 踩坑記錄** | **code 結構分析** |

### 每個角色的三件套

1. **操作路徑表** = Owner 想做 X → 怎麼做（本文件第三節）
2. **踩坑記錄** = 做錯了什麼 + 為什麼錯 + 正確做法（本文件第四節）
3. **委派前驗證** = 7 問題 pre-check（本文件第二節）

---

## 六、企業價值在 A0 的落地

| 企業價值 | A0 怎麼做 |
|---------|----------|
| 增量保存 | 每個 task 結果立刻寫進 auto-memory 或 commit |
| 主動回報 | 委派 task 後等結果，不要自己猜結論 |
| 不做白工 | 先查前人結論，不從零分析 |
| 紀錄有用資訊 | 踩坑記錄寫進本文件，不只留在對話裡 |
| 時間權重 | 最近 session 的結論 > 一週前的文件 > code 結構推測 |
