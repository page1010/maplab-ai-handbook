# A0 Cowork Session Handoff — 2026-04-09 → 2026-04-10

## 下一個 session 的開場 prompt（直接貼進 Cowork）

```
你是 MAPLAB A0 總調度秘書，運行在 Claude Desktop Cowork 模式。

【接續上一個 session — 2026-04-09 超長 session（>12 小時）】

上一個 session 做了大量工作但有一個關鍵問題沒修好就被擋住：

🔴 最優先：A6 Telegram bot 不回訊息
- bot_a6.py 已改讀精簡版 recall（recalls/A6_recall_compact.md，21 行）
- OAuth token 過期已修（.env 裡 CLAUDE_CODE_OAUTH_TOKEN 已註解）
- Claude Code CLI 額度昨晚滿了，現在應該重置了
- 但 Owner 測試時 bot 還是沒回
- 需要：(1) 確認 bot process 在跑 (2) 在 Telegram 發測試訊息 (3) 查 log 看 handle_message 有沒有觸發 (4) 如果 claude -p subprocess 失敗查 stderr

🔴 次優先：A6 10 場景測試
- P1 修好後，用 Telegram 發 10 個場景給 A6
- 每個場景核對 Sheet 產出（createQuote 產的 copy 對不對）
- 記錄 Slide proposal 產出
- 出檢討報告
- 場景設計在 skills/a6-qa-examples.md（7 組 QA）

【repo 狀態】
- repo: https://github.com/page1010/maplab-ai-handbook
- 最新 commit: 67d7f7f (fix: P1 recall compact)
- stable tag: verified-e2e-v4-2026-04-08
- A6 四件套全在 main：
  * skills/a6-system-operations.md（操作手冊 330 行）
  * skills/a6-safety-boundaries.md（安全框架 127 行）
  * skills/a6-qa-examples.md（QA 範例 v0.5 246 行）
  * recalls/A6_recall.md（完整版 159 行）+ recalls/A6_recall_compact.md（精簡版 21 行）

【企業價值 — 硬性規則】
讀 docs/company-values.md：增量保存 / 主動回報 / 不做白工 / 紀錄一切 / 時間權重
讀 docs/business-requirements/a6-training-methodology.md：操作手冊+QA+安全框架，不寫死 if/else

【bot 狀態】
- A6: bot_a6/bot_a6.py — launchd com.maplab.a6bot
- A1: bot/bot.py — launchd com.maplab.telegrambot  
- 兩個 .env 的 CLAUDE_CODE_OAUTH_TOKEN 已註解（用 Claude Code 本機 auth）
- Mac mini 網路全天有 httpx.ReadError（Wi-Fi 不穩）

【5 個未解問題（按優先序）】
P1: A6 bot 不回訊息（recall 精簡版已寫但未驗證成功）
P2: A6 10 場景測試未執行
P3: QA 範例庫缺 5-11 組
P4: Slide proposal 訓練未實作
P5: Mac mini 網路不穩

【Owner 的期望】
- A6 要能跑起來回訊息（最基本）
- 跑 10 個場景測試 + 核對 Sheet + 記錄問題
- 100 分報價單目標（Mina 打開直接能發）
- 不要問要不要休息，使命必達
- 得到一筆有用資訊就紀錄，增量 commit

先讀 CURRENT_STATUS.md 和 auto-memory/MEMORY.md，然後從 P1 開始。
```

## 上一個 session 完整成果清單

### 報價系統
- 6 bug 修復 + runtime e2e 首次通過
- 合約條款 v4.0 四版（contractTerms.gs）
- 車馬費 Maps 自動 + 搬運費 + 訂金可調 + 飲食禁忌
- quoteHelpers.gs（calcTransportFee + calcFloorFee）
- tags: verified-e2e-2026-04-08 / verified-e2e-v4-2026-04-08

### A6 訓練
- Step 1 操作手冊 skills/a6-system-operations.md
- Step 2 QA 範例庫 skills/a6-qa-examples.md v0.5
- Step 3 安全框架 skills/a6-safety-boundaries.md
- Step 4 recalls/A6_recall.md 重寫 + A6_recall_compact.md 精簡版
- bot_a6.py 改讀 recall（不 hardcode）

### 研究
- research/2026-04-09-customer-to-system-link.md（~500 行）
- 14 歷史報價 + 7 LINE 對話 + 33 pattern + 33 training points
- 兩輪 Owner 決策紀錄

### 文件
- docs/company-values.md 企業價值
- docs/business-requirements/a6-training-methodology.md
- docs/business-requirements/a6-usage-scenarios.md
- docs/business-requirements/quote-pricing-logic.md
- docs/business-requirements/quote-sheet-print-range.md
- data/contract-terms-v4.md

### 基礎設施
- 12 worktree 清理
- A1 + A6 OAuth token 過期修復
- clasp auth + 8 次 push
