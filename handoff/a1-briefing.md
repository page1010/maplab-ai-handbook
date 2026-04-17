# A0 → A1 Briefing
> 最後更新：2026-04-17 by A0

## 本次 Session 做了什麼
- A6 故障診斷：OAuth 過期 → claude -p 幻覺 → Python 備援沒觸發
- 修復：bot_a6.py 觸發邏輯改善、recall 加不推測規則、P0 技能文件修正
- 系統改進：patrol.sh token 偵測、worktree cleanup 自動化、A0 強制記錄規則
- 設計：A0/A1 briefing + 抽考機制

## Owner 校正原話（2026-04-17）
> 「那是『你』A0 不紀錄。看要寫在什麼層級才會聽話。」
> 「故障2一樣不該發生，這表示他一樣沒有眼見為憑，而是根據code推測 所以亂猜猜錯還亂回報」
> 「token不要讓他會過期 你修復」
> 「a0 a1是不是互換比較好 或是要有個溝通管道」
> 「a1要起到校正功能...比如抽考系統全貌 系統架構 技能書 與使用者對話是如何用3個問句訓練a6」
> 「舉一反三 請根據pltr 在部署訊練營時...」

## 未完成（下一個 session 接手）
- QA-1~QA-7 場景測試
- 新增品項功能開發
- A0/A1 briefing 機制第一次實際運行驗證

## 建議起始點
- 讀 projects/a0-a1-briefing-protocol.md 理解抽考機制
- 跑 QA 測試（用 Telegram Web 測 A6，每則測試加 [QA-TEST] 前綴）
