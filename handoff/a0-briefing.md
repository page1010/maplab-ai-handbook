# A1 → A0 Briefing
> 最後更新：2026-04-17 by A0（代寫，等 A1 接手後由 A1 維護）

## Owner 最新校正（2026-04-17）
- 缺資訊不要卡報價：影響毛利率的必問，不影響的填「待確認」先出
- 測試必須標記 [QA-TEST]，操作必須即時記錄
- A6 claude -p 幻覺 GAS 掛了 → 教訓：不要推測系統狀態，只回報實際錯誤
- A0/A1 需要雙向 briefing + 抽考機制

## 系統狀態
- A6 bot 已重啟（PID 31445），觸發邏輯已改善
- Google OAuth token 有效（patrol.sh 已加自動偵測）
- GAS endpoint 活的（v4 部署正常）
- A6 P0 技能文件已修（safety-boundaries / telegram-window / rapid-quote-sop）
- worktree cleanup 自動化已上線（launchd 每 30 分鐘）

## 未完成
- QA 測試（QA-1~QA-7）還沒跑
- 新增品項功能還沒寫
- A0/A1 briefing 機制剛建立，還沒實際運行過

## 關鍵 Commits（2026-04-17）
- e0dc015: A0 強制記錄規則
- cc5b925: A6 recall 缺資訊處理原則
- 3746ec9: patrol.sh token 自動偵測
- 66cf0cf: 對話紀錄 + methodology 整合
- 71fa1a8: A0/A1 briefing protocol 設計文件
