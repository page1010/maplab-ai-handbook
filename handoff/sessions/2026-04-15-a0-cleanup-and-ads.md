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

## 交接 — 下一個 A0 session 的接手指南

### 快速確認問句（用來測試新 session 有沒有進入狀況）

1. 「A6 是幹嘛的？它跑在哪個平台？」— 答案：報價加速器，跑在 Telegram bot（bot_a6.py），用 claude -p 生成報價 → 寫 Sheet → 觸發 GAS
2. 「bot/ 目錄是棄用的嗎？」— 答案：不是，DEPRECATED.md 過期了，bot/bot.py 是 A1 Telegram bot，PID 在跑
3. 「GTM 現在版本幾？追蹤了什麼？」— 答案：版本 21。v20 加了 Meta LINE 追蹤，v21 加了 Google Ads LINE 轉換追蹤。兩個共用 Trigger - LINE Button ID
4. 「AGENT_RECALL_PROMPTS.md 在哪？」— 答案：已移到 trash/，recalls/ 是唯一 recall 來源。CLAUDE.md 指向 recalls/A1_recall.md
5. 「CURRENT_STATUS.md 多大？」— 答案：114 行（從 453 行瘦身），完整版在 archive/

### 本輪做完但下一輪需要驗證的事

1. **QUOTE_DRAFT 品牌色** — Sheets API 格式化已套用到母版。下次 createQuote makeCopy 時確認新報價單是否帶品牌色
2. **Google Ads 轉換追蹤** — GTM v21 已發布。24-48hr 後檢查 Google Ads 轉換頁面是否開始收到「LINE 諮詢點擊」數據
3. **Facebook Ads 追蹤** — GTM v20 Meta tag 已發布。檢查 Facebook 事件管理員是否收到 Contact 事件

### 下一輪優先任務

1. **QA-1~QA-7 場景測試** — 場景定義在 skills/a6-qa-examples.md，7 組全未執行
2. **Facebook Ads 數據分析** — 廣告管理員已開（act=318634712），需要查看花費和成效
3. **A3 社群策略** — Owner 提出三個新方向：
   - Threads/Meta 海巡（主動到其他貼文留言互動）
   - A4 照片內容規劃（活動照片 → WordPress 案例文章 or 作品集）
   - Substack/內容變現（AI 協作過程的內容產品化）
4. **Worktree 清理** — 本 session 結束時有 40+ idle code tasks 的 worktree。需要在終端機跑：
   ```bash
   cd /Users/pagemacmini/maplab-ai-handbook
   rm -rf .claude/worktrees/*/
   git worktree prune --verbose
   ```

### 本輪教訓（已寫入 pitfalls + recall + auto-memory）

- P11: 文件標記 ≠ 實際狀態 — 必須 ps/launchctl 驗證
- P12: handoff log 必須完整讀完
- P13: 用 ls 檢查檔案存在
- A0 recall 11-14: 冷啟動必讀、快速會議先行、使用者場景優先、窮盡工具再問 Owner
- Worktree 不清 = 記憶體殺手
