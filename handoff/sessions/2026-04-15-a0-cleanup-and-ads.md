# A0 Cowork Session — 2026-04-15
# 主題：Repo 大掃除 + 品牌色票 + 廣告轉換追蹤

## 成果清單

### Repo 大掃除（Phase 1-8）
- 12 個垃圾 → trash/
- 7 處死連結修復
- AGENT_RECALL_PROMPTS.md → trash/（recalls/ 統一為 sole source）
- session-notes/ 合併到 sessions/
- 15 張完成 task card → done/
- 4 組重複 skills → trash/
- 8 個 feedback 提煉成 P8-P13 進 pitfalls/SKILL.md
- STARTUP_PROTOCOL + REPO_SYNC_RULES → archive/
- CURRENT_STATUS.md 瘦身：453 → 114 行

### 系統診斷
- Extension 召喚 A0 vs A2 冷啟動實測：A0 失敗（private repo）、A2 成功
- 300+ 殭屍 worktree/branch 清理（記憶體過載根因）
- A1/A6 bot 狀態正常（PID 722/723）

### 品牌與設計
- 網站實際 CSS 色票抽取 + 三品牌對標（Ottolenghi/Peter Rowland/Essential）
- 品牌色票微調版落地：暖棕 #8B5E3C 為主色
- QUOTE_DRAFT 母版品牌色美化（13 個格式請求）
- visual-spec.md 追加微調版色票
- T-A2-004 首頁優化任務卡建立
- docs/user-scenarios.md 建立（系統全局地圖）

### 廣告轉換追蹤
- 發現 Google Ads PMax 花 NT$11,400 但 0 轉換
- 根因：GTM 有 Meta LINE 追蹤但未發布 + 無 Google Ads 轉換 tag
- GTM v20 發布：Meta LINE Button Click tracking
- Google Ads 建立「LINE 諮詢點擊」轉換動作（ID: 821843155）
- GTM v21 發布：Google Ads Conversion tracking
- Facebook + Google Ads 雙平台轉換追蹤上線

### 教訓寫入
- pitfalls P11-P13（文件標記≠實際、handoff完整讀、ls檢查存在）
- A0 recall 第 11-14 條（冷啟動必讀、快速會議先行、使用者場景、窮盡工具）
- auto-memory 3 條新增（exhaust_tools、user_scenario_first、worktree_cleanup）

## 未完成
- QA-1~QA-7 場景測試（已讀取場景定義，未執行）
- Facebook Ads 數據分析（tab 已開但未深入查看）
- 29 個 orphan skills 評估
