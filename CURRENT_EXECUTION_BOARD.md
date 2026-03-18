# CURRENT_EXECUTION_BOARD.md

**最後更新：2026-03-18 | A1 Handbook Agent（Claude Opus 4.6）**

---

## 系統整體狀態

當前階段：Phase 2 Notion vs GitHub 對齊清理已完成 → Phase 3 多 Agent 團隊協作強化（已規劃，待執行）
最新系統版本：v3.0（2026-03-17）
當前最高優先任務：執行 Phase 3 四項任務（見下方「下次接手待辦」）

---

## 廣告現況（2026-03-17）

正在跑的廣告（共 2 則 Meta + 1 則 Google）：

| 平台 | 廣告名稱 | 狀態 | 每日預算 |
|------|---------|------|---------|
| Google | PMax 最高成效 | 進行中 | NT$300 |
| Meta | B組 互動 公關公司窗口 | 進行中 | 廣告組合預算 |
| Meta | B組 互動 企業窗口 | 進行中 | 廣告組合預算 |

草稿中（待上線）：Meta 策略一 冷受眾 C款，素材製作中

---

## 各 Agent 即時狀態

### A1 — Handbook Agent
狀態：Phase 2 完成，Phase 3 已規劃待執行
本次完成（2026-03-17～03-18）：
- Session A（6 commits）：README v2.3 整合 PROJECT_CONTEXT、刪除 PROJECT_CONTEXT、BOARD v1.7、ads-monitor v1.1、HANDOFF_TEMPLATE v1.1、CHANGELOG v3.0
- Session B（4 commits）：SYSTEM_MAP v2.0、AI_WORKFLOW_MAP v2.0、AGENT_RULES v1.7 Notion 刪除線、CHANGELOG 更新
- 總計 12 commits，所有檔案 Notion vs GitHub 對齊完畢
下一步：執行 Phase 3 多 Agent 團隊協作強化（見下方）

### A2 — SEO Content Agent
狀態：待機中
阻塞點：需要補足廣告對應關鍵字頁（見 seo-ads-agent.md 第七節）
建議下一步：台南外燴總頁、週歲派對外燴頁、婚禮外燴頁、企業外燴頁、價格/FAQ 頁

### A3 — Ads Monitor Agent（Ads Team）
狀態：文件化 + GTM SOP 完成，等待使用者執行（Canva 素材 + GTM 轉換事件設定 + PMax 標題新增）
今日完成（2026-03-17）：
- seo-ads-agent.md v2.0 完整重寫 + v2.1 PMax 問句型標題
- gtm-conversion-setup.md v1.0 → v1.1（GTM v15 已發布）
- CHANGELOG v2.6 → v2.7 → v2.9 更新
等待使用者：
- Canva C款素材完成並上傳
- 暫停「開發潛在客戶2026」空殼活動
- 確認「品牌知名度 A組」未發佈編輯內容

- **GTM Contact Event Debug（A2 Session 2026-03-18）：**
- 已完成：
- - 根因診斷：首頁 LINE 按鈕用 lin.ee URL，但 GTM 觸發條件只比對 lihi2.com → Contact 事件不觸發
  - - GTM 觸發器「僅連結」已修改：Click URL 改為 regex `(lihi2\.com|lin\.ee|line\.me)`
    - - 觸發器已儲存（Workspace 16），但尚未發布
      - - gtm-conversion-setup.md 已更新至 v1.2（含診斷與修正計畫）
        - - skills/media-limit-workaround.md 已建立（Too much media 解決方案）
         
          - ⚠️ 發現次要問題：LINE 按鈕使用 target="_blank"，GTM「僅連結」觸發器可能無法捕捉點擊事件（Tag Assistant 測試時無 Link Click 事件）
         
          - 📋 **待辦清單（等 Owner 有空回來處理）：**
          - - [ ] 修復 target="_blank" 問題（二擇一）：
            - [ ]   - 方案 A：在「僅連結」觸發器啟用「等待代碼」(Wait for Tags) 選項
            - [ ]     - 方案 B：改用「所有元素」(All Elements) 觸發器 + Click URL regex 條件
            - [ ] - [ ] GTM Preview 重新測試 → 確認 Link Click / Click 事件出現
            - [ ] - [ ] 確認 Meta - LINE Click Event 代碼觸發（Contact 事件）
            - [ ] - [ ] GTM 發布新版本（提交）
            - [ ] - [ ] Meta Pixel Helper 驗證 Contact 事件
            - [ ] - [ ] 更新 gtm-conversion-setup.md 至 v1.3（最終修正狀態）
下次接手時必看：seo-ads-agent.md 第十節「下次 Agent 接手必問清單」

### A4 — Pipeline Agent
狀態：等待用戶確認相片來源路線
詳見：projects/maplab-pipeline.md v1.3

### A5 — Data Schema Agent
狀態：Schema v0.1 完成（maplab-master-data.md v1.4）

### A7 — AI Reply System Agent
狀態：規則建立中，回覆模組草稿階段
詳見：projects/ai-reply-system.md v1.0

---

## 🔜 下次接手待辦 — Phase 3：多 Agent 團隊協作強化

**背景：** 6-10 個 Agent 並行運作，現有規則解決了「我是誰」和「我能碰什麼」，但缺少三層機制：簽到/簽退、檔案鎖定意識、技能書主動路由。以下四項任務已經 owner 確認規劃，待執行。

**接手前先讀：** skills/context-compression-guide.md（防 prompt 過長）、skills/github-api-workflow-guide.md（GitHub 編輯流程）

### 任務 1：CURRENT_EXECUTION_BOARD.md v2.0 — 簽到/簽退機制
- 新增「Active Session」區塊：Agent 編號 / 開始時間 / 正在改的檔案 / 預計完成項目
- 新增「Session Log」標準格式：每次 session 結束必須留一條記錄（誰 / 何時 / 做了什麼 / 改了哪些檔案 / 未完成什麼）
- Active Session 同時解決檔案鎖定 — 其他 Agent 開工前先看有沒有人佔住同個檔案
- 預估：1 commit

### 任務 2：AI_WORKFLOW_MAP.md v2.1 — 協作規則升級
- 現有 Rule 1-5 保留
- 新增 Rule 6：簽到/簽退 — 開工前在 BOARD 的 Active Session 登記，收工前清除並寫 Session Log
- 新增 Rule 7：檔案衝突檢查 — 開工前查 Active Session，若目標檔案已被佔用，等待或換任務
- Handoff Protocol 從 4 步變 5 步：Step 0 = 清除 Active Session 簽到
- 預估：1 commit

### 任務 3：AGENT_STARTUP_PROTOCOL.md v1.1 — 串接新機制
- Step 2 移除已刪除的 PROJECT_CONTEXT.md 引用（目前還在引用已刪除的檔案）
- 啟動前必讀清單加入：讀 BOARD 的 Active Session 確認沒有檔案衝突
- 完成任務收尾 SOP 加入：清除自己的 Active Session + 寫 Session Log
- 預估：1 commit

### 任務 4：superpowers-guide.md v1.4 — 技能書主動路由表
- 新增「任務類型 → 建議預讀技能書」對照表（不是卡住才查，是開工前就知道該讀什麼）
- 路由範例：碰 API → github-api-workflow-guide + systematic-debugging-cloud-guide
- 路由範例：寫長文件 → context-compression-guide + verification-checklist-guide
- 路由範例：廣告相關 → ai-model-guide（選 Claude 或 Gemini）
- 預估：1 commit

### 最後：CHANGELOG.md 統一更新
- 預估：1 commit
- 總計：5 commits

**執行順序：** 任務 1 → 2 → 3 → 4 → CHANGELOG（一次一個，每個任務先確認資源再動手）

**技術提醒：** GitHub CodeMirror 6 編輯器用 `document.querySelector('.cm-content').cmTile.view.dispatch()` 替換內容，不要用 clipboard paste（會 append 而非 replace）。

---

## 已知問題

| 問題 | 狀態 |
|------|------|
| 004 A3 vs A6 職責邊界模糊 | ✅ 已解決（v2.4 合併為 Ads Team） |
| 005 maplab-master-data.md header 版本矛盾 | ✅ 已修正（v1.4） |
| 006 CURRENT_EXECUTION_BOARD.md 重複區塊 | ✅ 已修正（v1.2） |
| 007 seo-ads-agent.md 舊版亂碼 | ✅ 已修正（v2.0） |
| 008 CURRENT_EXECUTION_BOARD 重複版本行 | ✅ 已修正（v1.7） |
| 009 AGENT_STARTUP_PROTOCOL Step 2 引用已刪除的 PROJECT_CONTEXT.md | ⏳ 待修（Phase 3 任務 3） |

---

## 重要連結

- 廣告技術文件：projects/seo-ads-agent.md
- GTM 設定 SOP：projects/gtm-conversion-setup.md
- Meta 廣告管理員：https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=318634712
- Google Ads：https://ads.google.com/aw/campaigns?ocid=252396667

---

*版本：v1.8 | 系統版本：v3.0 | 維護者：A1 Handbook Agent*
