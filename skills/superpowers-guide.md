h# Superpowers Skills 導覽手冊 — MAPLAB AI Agent 版
版本：v2.1 | 建立：2026-03-14 | 更新：2026-03-26

> 完整互動版：https://www.notion.so/Superpowers-Skills-320ab0806d5c807c95c7d8d633a7e5c5
> 原始 Repo：https://github.com/obra/superpowers

---

## 🗺️ 任務類型 → 建議預讀技能書（開工前路由表）

> **自動判斷規則**：看到觸發關鍵字 → 自動載入對應技能書，不用手動查表。

| 觸發關鍵字 | 自動載入技能書 | 說明 |
|-----------|-------------|------|
| （所有任務自動載入） | **task-progress-guide** | 每步紀錄 + 子任務切割 + 接續 Prompt |
| 寫文章、發貼文、回客戶、報價、提案 | **brand-voice-guide** | 品牌語氣統一：禁用語、平台微調、受眾語氣 |
| 結束、收工、交接、下線 | experience-log | 記錄成功路徑 + 失敗教訓 |
| GitHub、commit、branch、PR、API | github-api-workflow-guide | API 流程 |
| 長文件、大量修改、token 快滿 | context-compression-guide | 防 prompt 過長 |
| 廣告、Google Ads、Meta、投放 | ai-model-guide + a3-social-ads-skills | AI 分工 + 廣告操作 |
| Colab、Python、batch、長時間 | colab-resilience-guide | 防死機 + checkpoint |
| Sheets、試算表、品項、資料 | sheets-data-cleaning-guide + sheets-tracking-guide | 清洗 + 追蹤 |
| 卡住、錯誤、失敗、bug | troubleshooting-hub | 先查急救表再行動 |
| 斷線、接手、上次做到哪 | crash-recovery-guide | 進度驗證 + 補齊 |
| 第一次、新 agent、不知道從哪開始 | AGENT_STARTUP_PROTOCOL.md | 完整 9 步驟 |
| 照片、相簿、圖片分類、素材 | photo-pipeline-toolkit-guide + a4-photo-asset-skills | 全流程 + 品牌規範 |
| GPS、座標、home、shop | gps-daily-subdivision-guide | Haversine 分類 |
| SEO、排名、關鍵字、GSC、GA | seo-session-checklist + seo-ranking-evaluation-guide | 排名判讀 + 優化 |
| GTM、Pixel、轉換、追蹤碼 | seo-session-checklist Phase 2 + gtm-conversion-setup | 追蹤設定 |
| WordPress、上傳圖片、featured image | gdrive-to-wordpress-upload-guide | 雲端圖片上傳 SOP |
| 報價、菜單、人數、預算 | a5-quotation-engine-skills | 菜單搭配 + 報價生成 |
| 急件、提案、簡報、客戶背景 | a6-sales-rapid-response-skills | 一鍵提案 + 客戶速查 |
| IG、FB、Threads、社群、貼文 | a3-social-ads-skills + brand-voice-guide | 多平台貼文 + 語氣 |
| 菜單卡、品牌素材、圖片規範 | a4-photo-asset-skills | 風格統一 + 數位菜單 |
| 客服、LINE、回覆、詢問 | a7-customer-service-skills + brand-voice-guide | FAQ + 語氣 |
| 策略、規劃、方向、大局 | strategic-review-guide | 5 問框架 |
| 驗證、確認、完成檢查 | verification-checklist-guide | 5 步驗證 |
| 媒體限制、100張、圖太多 | media-limit-workaround | 繞過限制策略 |
| 遠端桌面、Windows、跨機器、Colab、DESKTOP-PAGEHOME、Agent 監控 | remote-desktop-agent-bridge | 適用 A0：Chrome Remote Desktop 連接 Windows，監控 A4/A5 等跨機器 Agent |
| A0 行為、被動、回報、提醒、Owner Action | a0-proactive-dispatch-guide | 適用 A0（每次 session 必拿）：禁止被動回報，行動優先，驗證 Owner Action 狀態 |
| Extension、召喚、summon、Agent Commander、Side Panel、Chrome 側邊欄 | extension-agent-summon-guide | 適用 A0（主要）、所有角色（參考）：透過 Chrome Extension 召喚 A0-A8，含平台差異 + 遠端召喚 SOP |
| 視覺、色彩、字體、品牌、設計、IG、社群、Landing Page、CSS | maplab-visual-spec | 適用 A2/A3/A6/A8：7色票+CSS變數、字體規範、影像處理、IG版面系統、設計元素、黃花規則、命名規則 |
| 斷點、接下來、下一步、預覽、session 結束 | next-three-report | 每次斷點必用：回報下三個任務的目標/方法/步驟 |
| 執行、開工、任務啟動、protocol、SOP | task-execution-protocol | 任務執行標準流程：啟動前確認 + 每步紀錄 + 完成驗證 |

---

## 快速大綱

### 原版 Superpowers（from obra/superpowers）

| 需求 | Skill | 核心原則 |
|------|-------|---------|
| 需求模糊 | brainstorming | 一次一問，列 2-3 方案 |
| 要寫計畫 | writing-plans | 每步 2-5 分鐘，路徑/指令全寫死 |
| 要寫程式 | test-driven-development | 先寫失敗測試，紅→綠→重構 |
| 遇到 Bug | systematic-debugging | 四階段根因調查，3次修不好質疑架構 |
| 說完成前 | verification-before-completion | 有證據才能說完成 |
| Code Review | requesting/receiving-code-review | 審前清單、技術回應 |
| 多人分工 | subagent-driven-development | 雙階段審查 |
| 平行作業 | dispatching-parallel-agents | 並發 Subagent |
| 隔離環境 | using-git-worktrees | 新 branch + worktree |
| 任務收尾 | finishing-a-development-branch | 合併/PR/保留/丟棄 |
| 批次執行 | executing-plans | 分批，保留人工確認點 |
| 寫新 Skill | writing-skills | TDD 方式寫文件 |
| 第一次用 | using-superpowers | 入門 |

### MAPLAB 自建技能包

| 需求 | Skill | 核心原則 |
|------|-------|---------|
| **任務紀錄（必拿）** | **task-progress-guide** | **每步紀錄 + 接續 Prompt + 方向偏移** |
| Colab 防死機 | colab-resilience-guide | checkpoint + timeout + retry |
| Prompt 太長 | context-compression-guide | 三層防線：預防→監測→應急 |
| GitHub 雲端開發 | github-api-workflow-guide | 7步 API 工作流 + fetch 範本 |
| 完成驗證 | verification-checklist-guide | 5步驗證關卡 + MAPLAB 場景表 |
| 雲端除錯 | systematic-debugging-cloud-guide | 四階段 + Colab/API/Drive 場景 |
| 選 AI | ai-model-guide | Claude/Gemini/GPT 分工 |
| Sheets 清洗 | sheets-data-cleaning-guide | 公式+腳本+SOP 工具箱 |
| 相簿 Pipeline | photo-pipeline-toolkit-guide | Takeout→分類→去重→WebP |
| 卡住急救 | troubleshooting-hub | 症狀→解法→技能書路由表 |

---

## MAPLAB 自建 Skill 詳細

### task-progress-guide — 任務紀錄與接續（必拿）
- **何時用**：所有任務，不可跳過
- **核心**：Progress Log 每步紀錄 + 子任務切割 + Resume Prompt 接續 + 方向偏移回報
- **路徑**：skills/task-progress-guide.md

### colab-resilience-guide — Colab 防死機
- 何時用：Colab 長時間任務（>30 分鐘）
- 6 條規則：checkpoint | timeout | 進度輸出 | unzip -n | session SOP | 斷線 SOP
- 路徑：skills/colab-resilience-guide.md

### context-compression-guide — 防 Prompt Too Long
- 何時用：session 做了很多事、讀了很多文件
- 三層防線：預防（6規則）→ 監測（水位表）→ 應急（存檔SOP）
- 路徑：skills/context-compression-guide.md

### github-api-workflow-guide — GitHub API 開發流程
- 何時用：要在 GitHub 上建 branch / 寫程式 / PR / merge
- 7 步標準流程 + JS fetch 範本 + 踩坑紀錄
- 路徑：skills/github-api-workflow-guide.md

### verification-checklist-guide — 完成驗證
- 何時用：說「完成」「修好了」之前
- 5 步驗證關卡 + MAPLAB 8 大場景對照表
- 路徑：skills/verification-checklist-guide.md

### systematic-debugging-cloud-guide — 雲端除錯
- 何時用：遇到任何 bug，在亂猜之前
- 四階段 + Colab/GitHub API/Drive 15 個常見場景表
- 路徑：skills/systematic-debugging-cloud-guide.md

### ai-model-guide — AI 選用指南
- 何時用：不確定該用 Claude / Gemini / GPT
- 對照表 + 跨 AI 協作範例 + GPT 幻覺校正 SOP
- 路徑：skills/ai-model-guide.md

### sheets-data-cleaning-guide — Sheets 資料清洗工具箱
- 何時用：品項去重、品名清洗、欄位格式驗證、批次操作
- 公式工具箱（TRIM/REGEXREPLACE/COUNTIF）+ Apps Script 自動化 + 清洗 SOP
- MAPLAB 特定解法：OrderLines R6 重建、QUOTE_DRAFT 增強、DST 去重
- 路徑：skills/sheets-data-cleaning-guide.md

### photo-pipeline-toolkit-guide — 相簿整理全流程工具鏈
- 何時用：Google Photos Takeout 解壓→分類→去重→WebP→歸檔
- Takeout JSON metadata 合併、EXIF 讀寫、HEIC 支援
- 重複偵測（MD5 + perceptual hash）、Gemini Vision 分類、Colab checkpoint
- 路徑：skills/photo-pipeline-toolkit-guide.md

### troubleshooting-hub — 卡住急救手冊
- 何時用：執行中卡住，嘗試 1-2 次修不好
- 13 個常見症狀 → 解法 → 技能書路由表
- 找不到解法 → 回報格式 → A1 補充 → 全員受益
- 路徑：skills/troubleshooting-hub.md

- ### seo-session-checklist — A2/A3 每次 Session 標準檢查流程
- - 何時用：每次 A2/A3 agent 開工時必須執行
  - - Phase 1：SEO 健康檢查（Rank Math 六大指標 + 關鍵字排名 + 索引 + SEO 分數 + 內容盤點）
    - - Phase 2：廣告追蹤檢查（GTM + Meta Pixel + Google Ads + GA4 + 商家檔案）
      - - Phase 3：紀錄歸檔（更新 seo-ads-agent.md + 與上次對比 + Session Summary）
        - - 含 2026-03-24 基準線數據
          - - 路徑：skills/seo-session-checklist.md
           
            - ### seo-ranking-evaluation-guide — SEO 排名判讀與優化決策指南
            - - 何時用：評估 SEO 成效、決定優化方向、判斷排名好不好
              - - 排名區間定義（Top 3 / 4-10 / 11-20 / 21-50 / 51-100 / 100+）
                - - MAPLAB 目標參考值（短期 3 個月 / 中期 6 個月）
                  - - 指標判讀（Traffic / Impressions / CTR / Position）
                    - - SEO 分數解讀 + 索引健康度判讀
                      - - 優化優先順序決策框架（技術 > 快速見效 > 內容補強 > 長期經營）
                        - - MAPLAB 關鍵字策略地圖（核心 / 場景 / 長尾 / 防禦）
                          - - 路徑：skills/seo-ranking-evaluation-guide.md

---

gdrive-to-wordpress-upload-guide — Google Drive → WordPress 雲端圖片上傳

何時用：從 Google Drive 挑選照片上傳至 WordPress 媒體庫（不經手動下載/上傳）
核心：Drive viewer fetch → Canvas → Clipboard API → WordPress REST API upload
含 SEO 檔名/alt text 命名規範 + 圖片選擇規範 + 踩坑紀錄
路徑：skills/gdrive-to-wordpress-upload-guide.md

crash-recovery-guide — 當機復原與進度驗證

何時用：Session 中斷接手、GitHub 記錄與實際狀態不符、Summary 壓縮後可能遺漏
核心：進度驗證 4 步驟（Git commits → 外部系統驗證 → 比對 CURRENT_STATUS → 補齊落差）
checkpoint 機制：每完成外部系統操作立即 commit，防止進度丟失

### gps-daily-subdivision-guide — GPS 日常照片細分

- 何時用：日常照片需要細分 home/shop/other（S5.5/S6.5/S11.5-S13.5）
- - 核心：Takeout JSON geoData 提取 GPS → Haversine 距離計算 → 500m 閾值分類
  - - MAPLAB 座標：home（安中路）23.0475, 120.1841 / shop（和緯路）23.0125, 120.2025
    - - 含完整 Colab cell 程式碼 + 效能優化（batch list JSON）+ 踩坑紀錄
      - - 路徑：skills/gps-daily-subdivision-guide.md
路徑：skills/crash-recovery-guide.md

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-14 | 從 Notion 同步 | A1 |
| v1.1 | 2026-03-17 | 加入 colab-resilience-guide | A4 |
| v1.2 | 2026-03-17 | 加入 github-api-workflow / verification-checklist / systematic-debugging-cloud | A4 |
| v1.3 | 2026-03-17 | 加入 troubleshooting-hub | A1 |
| v1.4 | 2026-03-18 | 新增「任務類型 → 建議預讀技能書」路由表；修正 troubleshooting-hub 格式 | A1 |
| v2.4 | 2026-03-29 | 新增 next-three-report + task-execution-protocol 路由 | A1 |
| v2.3 | 2026-03-28 | 新增 extension-agent-summon-guide 路由 | A0 |
| v2.2 | 2026-03-27 | 新增 a0-proactive-dispatch-guide 路由 | A0 |
| v2.1 | 2026-03-26 | 新增 gps-daily-subdivision-guide 路由 + 技能描述 | A4 |
| v2.0 | 2026-03-24 | 新增 crash-recovery-guide 路由 + 技能描述 | A2 |
| v1.9 | 2026-03-24 | 新增 gdrive-to-wordpress-upload-guide 路由 + 技能描述 | A2 |
| v1.8 | 2026-03-24 | 新增 seo-session-checklist + seo-ranking-evaluation-guide 路由 + 技能描述 | A2 |
| v1.6 | 2026-03-23 | 新增 task-progress-guide（必拿）路由 + 路由表新增「所有任務」必拿列 | A1 |
| v1.5 | 2026-03-18 | 新增 sheets-data-cleaning-guide + photo-pipeline-toolkit-guide 兩本技能書路由 | A1 |
