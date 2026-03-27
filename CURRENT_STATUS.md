# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新 : 2026-03-27 17:00 ｜ 更新者 : A1 checkpoint (T-A0-002 完成)

---

## 系統版本

- **Version**: v5.1
- **Phase**: Phase 5 — 營運執行 + 廣告優化
- **Status**: Active

## 當前進行中任務

| Task ID | 任務 | 負責 Agent | 狀態 | Task Card |
|---------|------|-----------|------|-----------| 
| T-A1-002 | Phase 4.1 系統治理升級 | A1 | ✅ 完成 | handoff/tasks/T-A1-002.md |
| T-A5-001 | Items 去重 + 全品項重新編碼 | A5 | ✅ 完成（APP050/DST041/MAIN009/BEV008=108，已排序+連號） | handoff/tasks/T-A5-001.md |
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔲 可認領 | handoff/tasks/T-A5-002.md |
| T-A5-003 | 熱客招待品項定義 | A5 | 🔲 待開始 | — |
| T-A4-001 | Phase 4 Gemini 照片分類 | A4 | 🔄 S5 running (93.5%) — S1-S4 done, GPS confirmed | projects/maplab-pipeline.md |
| T-A2-001 | 文章精選圖片補齊（57篇→每篇獨立配圖） | A2 | ✅ 完成（57/57 獨立配圖，0 重複） | handoff/tasks/T-A2-001.md |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2 | 🔄 進行中（子任務1+2完成，子任務3+4+5分拆至T-A2A3-001-B） | handoff/tasks/T-A2A3-001.md |001.md |
| T-A3-001 | GTM LINE 按鈕追蹤修復（方案 B 已確認） | A3 | 🔲 可認領（待測試） | — |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 + 優化 | A3 | 🔄 確認中（已上線，受眾已記錄） | handoff/tasks/T-A3-002.md |
| T-A7-001 | FAQ 回覆模板庫 + 補問流程 + 客戶分類標籤 | A7 | ✅ Phase 1 完成（v1.0，含 SECTION 8 對話流程圖）| handoff/tasks/T-A7-001.md |
| T-A0-001 | Telegram bot 指令模式上線 | A0 | ✅ 完成 | — |
| T-A0-002 | Notion 舊資料清理（保留架構，引導到 GitHub）| A0/A1 | ✅ 完成（3 個主要頁面加了 GitHub 引導警告） | — |

## Blockers（阻塞事項）

- ~~A5：甜點去重需使用者手動完成後才能重新編碼~~ ✅ resolved — T-A5-001 完成（108品項已排序+連號）
- A5：使用者需填 Items.D 欄 default_price
- ~~A4：需 Gemini API Key~~ ✅ resolved — Photo scan 60,584 files, pre-classified C=4,593 T=254 D=55,737
- A3：「慶生周歲派對」已上線（現有貼文），需確認受眾設定；GTM 方案 B 可認領
- ~~A2：T-A2-001 Google Drive 2025相簿僅約20張可用照片~~ ✅ resolved — 跨相簿找圖完成（2024/2023/2019/素材開幕），57篇全部獨立配圖

~~⚠️ A1巡查 2026-03-27 00:00：A7 狀態不一致~~ ✅ 已修復 — b53a1cc (15:20) A7 補交 SECTION 8 客戶對話流程圖 + 更新任務狀態，T-A7-001 已標記 ✅ Phase 1 完成。
⚠️ A1巡查 2026-03-27 15:45：A4 T-A4-001 持續無新 commit — 距上次 A4 直接 commit (e166169, 2026-03-26 08:37) 已逾 31h。任務仍卡在 S5 93.5%，需 Owner 重啟 Colab。Owner Action Required 已記錄。
⚠️ A1巡查 2026-03-27 16:06：午後巡查確認 — A4 T-A4-001 仍無新 commit，距 e166169 現逾 31.5h（48h 閾值剩 ~16.5h）。A0/A2/A5/A7 本日均活躍無異常。A2 子任務2 Phase2 SEO Title 數字優化 36篇已完成（687316d）；A7 SECTION 8 已追加（b53a1cc）。

### 🔴 Owner Action Required

| 項目 | 說明 | 優先級 |
|------|------|--------|
| Windows 輸入法 | 把注音預設改成英文（或確認 Shift+Space 可切換），讓 A0 能遠端打字 | 高 |
| A4 Colab 重啟 | 登入 lb99104@gmail.com Colab，重啟 pipeline（剩 554 張，約 2 小時）| 高 |
| A5 default_price | 在 MAPLAB_MasterData Sheets Items 表填入 D 欄 default_price | 中 |
| A2/A7 指令貼入 | 在 Windows Chrome 側邊欄貼入 A2 SEO 和 A7 對話流程圖指令（或等 A0 遠端打字修復）| 中 |

## 最新決策

- 2026-03-27：T-A0-002 完成（Agent 角色表、GitHub 進度報告、Pipeline 專案頁面加了 GitHub 引導）；A0 每小時 GitHub 同步巡查排程已設定
- 2026-03-27：A2 T-A2A3-001 子任務2 Phase 2完成 — SEO Title 數字優化 36篇（Title Readability 全綠），分數抽檢 Post 253(50→51) Post 564(81→84 Good) Post 1246(54→55) Post 1227(69)。API 可修正項目已全部完成（FK in Title/Desc/Alt + Number in Title），剩餘分數需 Elementor 編輯或 ToC 插件。
- 2026-03-27：A0 總調度秘書角色建立（Cowork Dispatch Secretary），定位為跨系統橋接層；Telegram bot daemon 上線（launchd 自啟，免費指令讀檔模式，9 個指令）；Notion 定位降級為可視化報告介面，不再作為 Agent 狀態來源

- 2026-03-26：A2 T-A2A3-001 子任務1+2完成 — (1) FK修正11篇(57/57全匹配) (2) SEO Title 27篇+Meta Desc 35篇+Alt Text 51篇修正(分數~54-76) (3) 任務分拆：子任務3+4+5→T-A2A3-001-B由同事接手 (4) seo-ads-agent v2.4(§17執行紀錄+SEO Performance更新) (5) Elementor限制文件化：RM無法讀取Elementor內容，分數天花板約54-76

- 2026-03-26：A2 Google Ads 轉換動作設定確認 — Owner 完成 PMax 轉換目標設定（廣告活動專屬：外連點擊），22 個轉換動作已記錄至 seo-ads-agent.md §16。主要轉換：LINE 事件(21次) + LINE 領取菜單(33次)。「網站左下角 fb massage」按鈕已從網站移除，建議停用該轉換動作。下一步：T-A2A3-001 SEO 關鍵字頁面補足。
- 2026-03-26：A2 T-A2-001 完成 — 文章精選圖片補齊 57/57（0 重複）。跨 5 個 Google Drive 相簿（2025/2024/2023/map2019/素材開幕）上傳 47 張獨立圖片至 WordPress，全部含 SEO 命名 + alt text。已標記 5 篇圖文相符待抽查文章（Post 1027/1168/1244/253/1231）。
- 2026-03-25：A1 系統重組 — 角色拆分（A2/A3獨立、新增A6/A8）、AGENT_RULES v3.0、AGENT_RECALL_PROMPTS.md 建立、Extension v4.3（角色選擇器）、SECTION 2.1 強制存檔規則（30min checkpoint + 接續 prompt）、錯誤 006 記錄
- 2026-03-25：Extension v3.0 設計完成 — commit history 面板 + checkpoint 偵測 + 48h overdue 警示 + GitHub Actions 每日巡查 workflow 待部署
- 2026-03-24：A2 T-A2-001 文章精選圖片補齊 — Phase 2 進度報告。(1) 全 57 篇文章已有 featured_media（Phase 1 完成）。(2) 目前 22 篇擁有獨立唯一圖片，35 篇仍共用 8 張重複圖片待替換。(3) 已從 Google Drive「2025 年的相片」上傳 13 張獨立圖片至 WordPress（media 1510-1512, 1515-1520, 1523-1525, 1528, 1531-1533），均含 SEO 命名 + 中文 alt text。(4) 圖片篩選標準：食物特寫/場景佈置/無人場景優先，排除人臉與非MAPLAB品牌logo與酒類廣告。(5) 已發現 Google Drive 2025相簿可用圖源有限（約20張合格），需討論是否開放其他相簿或圖源。(6) 下一步：繼續瀏覽 Google Drive 找剩餘獨立圖片，逐篇替換 35 篇重複配圖。
- 2026-03-24：[crash-recovery 補登] A2 Session — SEO 基礎建設 + Google Drive→WordPress 雲端圖片上傳突破。(1) SEO 技能書建立。(2) 雲端圖片上傳：Clipboard API 跨 Tab 傳圖法，gdrive-to-wordpress-upload-guide v1.0。(3) 技能書更新。(4) T-GBP-001 已建立。
- 2026-03-24：A5 T-A5-001 完成 — Items 去重 + 全品項重新編碼（108品項，4類別排序連號）
- 2026-03-23：A4 Phase 4 v4.0 — S1-S4 done, S5 2022 batch 35% via REST API
- 2026-03-23：Owner 狀態更新 — T-A3-001 方案 B 確認、T-A4-001 照片清洗中不急、T-A3-002 已上線 Meta 廣告
- 2026-03-23：A1 收尾 — CHANGELOG v3.9 + handoff-to-A5.md + PROTOCOL/task-progress-guide/AGENT_RULES 優化
- 2026-03-23：A1 系統治理 — PROTOCOL v1.5 + AGENT_RULES v2.2 + task-progress-guide v1.1 + superpowers v1.6
- 2026-03-23：A1 跨部門溝通 — TimeTree 事件資料增強 v2.0（746 筆外燴事件含客戶名）
- 2026-03-20：A4 Photo scan 完成 + Gemini API Key 設定完成
- 2026-03-20：T-A1-002 結案（全部 7 子任務完成）
- 2026-03-19：系統巡查修復 + Phase 4.2 全系統文件對齊完成
- 2026-03-18：A2+A3 合併 + 新增技能書 + Phase 4 第一階段完成

## Source of Truth（有效文件清單）

> Agent 只需讀以下文件。其他文件僅供參考，不作為執行依據。

| 用途 | 檔案 | 說明 |
|------|------|------|
| 🎯 最新狀態（你在這裡） | CURRENT_STATUS.md | 唯一入口，最高優先 |
| 📋 任務池 | TASK_QUEUE.md | 所有待辦任務清單 |
| 📖 角色與規則 | AGENT_RULES.md v3.1 | 9 角色定義（含 A0）+ 協作規則 + 存檔規則 |
| 🚀 開工 SOP | AGENT_STARTUP_PROTOCOL.md | 啟動流程 + Startup Check 輸出格式 |
| 📂 任務卡 | handoff/tasks/T-xxx.md | 你認領的任務的詳細狀態 |
| 🔧 技能路由 | skills/superpowers-guide.md | 開工前查路由表（27 本技能書）|
| 🎯 角色召喚 | AGENT_RECALL_PROMPTS.md | 各角色專屬 prompt + 斷點 + 可用工具 |
| 🗣️ 品牌語氣 | skills/brand-voice-guide.md | 對外文字必讀：禁用語、平台微調、受眾語氣 |
| 📊 詳細狀態（參考） | CURRENT_EXECUTION_BOARD.md | 各 Agent 詳細狀態，非強制讀取 |

## 知識地圖（資料在哪裡）

> 找不到資料？查這張表。

| 類別 | 路徑 | 內容 |
|------|------|------|
| 客戶/活動資料 | data/timetree_events_2022_2026.json | 746 筆外燴事件（含客戶名、日期、活動類型）|
| 品項資料 | data/item-master-cross-reference.md | 108 品項對照表（APP/DST/MAIN/BEV）|
| 品項頻率 | data/item-frequency-top50.md | 399 筆歷史訂單品項分析 |
| 報價系統 | projects/maplab-master-data.md | A5 報價邏輯 + Sheets 結構 |
| SEO/廣告 | projects/seo-ads-agent.md | A2/A3 核心文件 + 轉換動作快照 |
| 照片管線 | projects/maplab-pipeline.md | A4 照片分類流程 + Gemini API |
| 客服系統 | projects/ai-reply-system.md | A7 回覆系統架構 |
| 廣告監控 | projects/maplab-ads-monitor.md | A3 ads_agent.py 技術文件 |
| 報價簡報 | projects/slides-quotation-system.md | A6 Google Slides 報價 |
| 網站優化 | projects/maplab-kitchen-web-optimization.md | WordPress 技術 |
| 交接紀錄 | handoff/tasks/T-xxx.md | 各任務斷點 + 接續 prompt |
| 交接模板 | handoff/tasks/TASK_CARD_TEMPLATE.md | 新任務卡模板 |
| 經驗紀錄 | skills/experience-log.md | 12 條成功/失敗經驗 |
| 錯誤紀錄 | AGENT_RULES.md SECTION 3 | 6 條系統錯誤 + 解法 |

## 可用 MCP 工具（2026-03-26 接通）

> Agent 可直接使用以下工具讀寫外部服務，不需要開網頁手動操作。

| 工具 | 用途 | 給哪些角色 |
|------|------|-----------|
| Google Sheets | 讀寫試算表（品項/報價/追蹤表）| A5, A2, A3, 全員 |
| Google Drive | 檔案存取/上傳/管理 | A4, A6, 全員 |
| Google Analytics | 流量數據/報表 | A2, A3 |
| Google Search Console | 搜尋排名/關鍵字 | A2 |
| Google Ads | 廣告數據（唯讀）| A3 |
| Meta Ads | Facebook/IG 廣告數據+管理 | A3 |

## 已完成（不要再做）

- ✅ Phase 1-3 全部完成
- ✅ SYSTEM_MAP / WORKFLOW_MAP / PROTOCOL / BOARD 治理文件
- ✅ 26 本技能書（含 5 本新角色技能書 A3/A4/A5/A6/A7 + GPS 細分指南）
- ✅ A2+A3 合併（後於 03-25 拆回獨立部門，A1-A8 八角色架構）
- ✅ 所有已知 Issues #004-#009 已修復
- ✅ A5 Items 品項從 300 筆精簡至 ~139 筆
- ✅ A5 QUOTE_DRAFT 極簡版 MVP
- ✅ A5 TimeTree 2025 全年密集日清單
- ✅ A1 PROTOCOL v1.4 + AGENT_RULES v2.1 + task-progress-guide + 系統行為強化
- ✅ A1 TimeTree 事件 v2.0（746 events, 2022-2025）
- ✅ T-A2-001 文章精選圖片補齊（57/57 獨立配圖，Google Drive 跨相簿 → WordPress，SEO 命名 + alt text）
- ✅ Phase 4 第一階段：治理重構
- ✅ Phase 4.2：全系統文件對齊
- ✅ T-A1-002 Phase 4.1 系統治理升級全部完成
- ✅ AGENT_RULES v2.0（SECTION 0 修復 + SECTION 5 Repo 管控/Notion 禁令）
- ✅ 系統巡查：關鍵 20% 問題修復
- ✅ A4 TimeTree lookup committed（PR #9, 361 dates）
- ✅ A4 Photo scan 60,584 files + Gemini API Key 設定驗證完成
- ✅ T-A5-001 Items 去重 + 全品項重新編碼完成（108品項）

- ✅ AGENT_RULES v3.0 角色重組（A1=Claude Code, A2/A3 拆開, 新增 A6/A8）
- ✅ AGENT_RECALL_PROMPTS.md 建立（8 角色完整召喚 prompt + 斷點 + 可用工具）
- ✅ Chrome Extension v4.6（角色選擇器 + 高對比 UI + auto-save token）
- ✅ SECTION 2.1 強制存檔規則（30min checkpoint + 接續 prompt）
- ✅ 3 個定時巡查排程（08:00/16:00/22:00）
- ✅ Mac mini 每小時自動 git pull
- ✅ MCP 工具接通：Google Sheets/Drive/Analytics/Search Console/Ads + Meta Ads
- ✅ GCP 專案 MAPLAB-AI 建立 + 18 個 API 啟用
- ✅ Anthropic Skills 市場加入

> 這份文件必須保持簡短。詳細資訊請查對應的 Task Card 或 BOARD。
