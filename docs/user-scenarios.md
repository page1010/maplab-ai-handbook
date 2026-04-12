# MAPLAB 使用者場景地圖

> 最後更新：2026-04-12 | 維護者：A0
> 這份文件是系統的全局地圖。任何 Agent 冷啟動時如果不確定自己在哪、該做什麼，先讀這裡。

---

## 系統核心：兩個主控台

A0 和 A1 是系統的大腦。所有決策、開發、對齊、釐清任務都在這裡發生。

### A0 — 總調度秘書（Cowork Desktop）

- **平台：** Mac mini Cowork app
- **職責：** 系統建置、架構設計、跨部門協調、問題診斷、任務對齊、大掃除、所有需要全局視角的工作
- **能力：** Chrome MCP、Gmail MCP、Drive MCP、Notion MCP、computer-use 桌面控制、開 Code task 委派 A1 執行
- **跟 Owner 的關係：** Owner 的系統級對話夥伴。溝通需求、釐清方向、確認優先級都在這裡
- **冷啟動讀：** auto-memory/MEMORY.md → CURRENT_STATUS.md → 最新 handoff session log

### A1 — 系統總管（Claude Code Terminal + Telegram Bot）

- **平台：** Mac mini 終端機（Claude Code）+ Telegram bot（bot/bot.py）
- **職責：** 系統開發與維護的執行層。A0 想到的事，A1 動手做——git 操作、API 呼叫、腳本開發、GAS 部署、bot 維護
- **能力：** 完整 CLI 環境、git、clasp、Python、curl、直接讀寫所有 repo 文件
- **Telegram bot 功能：** Owner 手機上快速查 repo 文件、看系統狀態（無 Claude API，純文件讀取）
- **冷啟動讀：** CLAUDE.md → recalls/A1_recall.md → CURRENT_STATUS.md

### A0 ↔ A1 的關係

A0 是橋接層（思考、對齊、調度），A1 是執行層（動手改 code、push commit）。A0 不直接改 GitHub 文件，透過開 Code task 委派 A1。Owner 是唯一決策者。

---

## 部門層：A2 — A8

每個角色是一個**部門**，有自己的專長領域但會隨業務需求延伸成長。Owner 坐在電腦前，透過 Chrome Extension 側邊欄召喚它們來交辦特定任務或確認進度。

### 召喚方式

1. 點 Chrome Extension（MAPLAB Agent Commander）
2. 下拉選角色 → Extension 從 `recalls/` 載入該角色的 recall prompt
3. 複製 → 貼到 Claude 側邊欄或新 tab
4. Agent 透過 GitHub tab 讀取 CURRENT_STATUS.md 和 Task Card 完成冷啟動

### 各部門

| 部門 | 專長領域 | 典型任務 | 延伸方向 |
|------|---------|---------|---------|
| **A2** 搜尋流量作戰部 | SEO、關鍵字、GA/GSC 分析 | 文章優化、Landing Page、排名追蹤 | 內容策略、搜尋廣告 |
| **A3** 社群與廣告成長部 | Facebook/IG 廣告、社群內容 | 廣告投放、GTM 追蹤、受眾分析 | 品牌行銷、社群經營 |
| **A4** 影像資產整理部 | 照片分類、品項圖片管理 | Gemini 批次分類、圖片 pipeline | 視覺素材庫、品牌形象 |
| **A5** 報價與提案引擎部 | 菜單品項、成本毛利、報價公式 | QUOTE_DRAFT 格式、Items 管理 | 報價自動化、提案模板 |
| **A6** 報價加速器 | 即時報價生成 | 一句話產報價單 + Slide 提案 | 客戶互動、報價追蹤 |
| **A7** 客服與對話轉單部 | FAQ、客戶回覆、對話模板 | 回覆模板庫、補問流程 | 客服自動化、轉單流程 |
| **A8** 多媒體影音製作部 | 影片、動態內容 | （尚未啟動） | 短影片、活動紀錄 |

### 部門的能力邊界

在 Chrome 側邊欄 / Claude tab 上，部門 Agent 可以：
- 透過 GitHub tab 瀏覽讀取 repo 所有文件
- 使用 web_fetch 讀取公開網頁
- 截圖分析任何開著的 Chrome tab（Google Sheets、WP 後台等）
- 產出分析、建議、草稿、程式碼片段

不能直接做（需要回報給 A0/A1 執行）：
- git push / commit
- 直接操作 Google Sheets API / GAS 部署
- 修改 bot 程式碼

---

## 行動入口：Telegram

Owner 不在電腦前時，透過手機 Telegram 操作。

| Bot | 用途 | 背後是誰 |
|-----|------|---------|
| maplab claude bot | 查 repo 文件、看系統狀態 | A1（bot/bot.py，無 Claude API） |
| MAPLAB A6 報價助理 | 一句話產報價單 + Slide | A6（bot_a6/bot_a6.py，用 Claude -p） |

---

## 什麼情況叫什麼

| 我想要... | 去哪裡 | 找誰 |
|----------|--------|------|
| 討論系統方向、對齊優先級 | Cowork | A0 |
| 修 code、push、部署 | 終端機 | A1 |
| 大掃除、盤查、跨部門協調 | Cowork | A0 |
| 手機查狀態 | Telegram | A1 bot |
| 手機報價 | Telegram | A6 bot |
| SEO 優化某個頁面 | Extension 側邊欄 | A2 |
| 設定廣告投放 | Extension 側邊欄 | A3 |
| 整理照片素材 | Extension 側邊欄 | A4 |
| 改報價單格式 | Extension 側邊欄 | A5 |
| 寫客服回覆 | Extension 側邊欄 | A7 |

---

## 系統基礎設施

| 元件 | 位置 | 用途 |
|------|------|------|
| GitHub repo | page1010/maplab-ai-handbook（private） | 所有文件的 source of truth |
| Google Sheets | MAPLAB_外燴系統_v0.1 | Items、QUOTE_DRAFT、SALES_INTAKE、DASHBOARD |
| Google Drive | MAPLAB_報價單/ | 客戶報價單存放 |
| Google Apps Script | 報價系統 GAS（Script ID: 1JIiPW...） | createQuote、createSlide、ApiEndpoint |
| Chrome Extension | MAPLAB Agent Commander v5.3 | 角色召喚、recall 載入 |
| launchd | com.maplab.telegrambot + com.maplab.a6bot | Mac mini 上 24/7 跑兩個 Telegram bot |
