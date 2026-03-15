# CHANGELOG.md — MAPLAB AI System 版本演進紀錄

本文件記錄 maplab-ai-handbook 的所有重大版本變更。
格式：版本號 | 日期 | 變更摘要 | 執行 Agent

---
## v2.3 — 2026-03-15（最新）

**A1 系統巡查 + CURRENT_EXECUTION_BOARD 修正**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `CURRENT_EXECUTION_BOARD.md` v1.2 — 修正重複區塊（v1.0+v1.1 並存問題），新增「已知規則不明問題」SECTION，新增問題 004/005/006，同步 A4 路線等待狀態

- **發現問題（問題 004–006，詳見 CURRENT_EXECUTION_BOARD.md）：**
- - 問題 004：A3 與 A6 職責邊界不清（ads_agent.py 歸屬模糊）
  - - 問題 005：maplab-master-data.md header v1.3 與實際內容 v1.4 版本矛盾
    - - 問題 006：CURRENT_EXECUTION_BOARD.md 重複區塊（已本次修正）
     
      - **系統狀態：** A4 等待用戶確認相片入口路線（路線 A/B/C）
     
      - ---

      
## v2.2 — 2026-03-14

**進入執行階段：補齊同步機制 + 建立執行看板 + 啟動 A5 任務**

**代理：** A5 Master Data Agent  
**重點：** Schema v0.1 完成，第一條閉環開始運作

**新增：**
- `handoff/schema-v0.1.md` — 4 張核心表欄位規格（Orders / Customers / Events / Items）
- `handoff/table-relationship-map.md` — PK/FK 關係圖 + 資料流向 ASCII 圖
- `handoff/field-naming-rules.md` — ID格式 / 日期格式 / Enum允許値 / 禁止事項
- `handoff/handoff-to-A4.md` — A5 → A4 交接文件，含任務范圍 + 限制說明

**代理：** A5 Master Data Agent（診斷）/ A1 Handbook Agent（回寫）  
**重點：** A4 Pipeline 戰略重定向——繞開滹 Phase 1 卡點

**更新：**
- `projects/maplab-pipeline.md` v1.2 — 新增 SECTION 0 戰略警示（接手前必讀）
  - 根因診斷：Google Photos API 在 2025 年後持續限制，繼續卡在 OAuth token 問題沒有意義
  - 战場重定義：從「我要怎麼串接 Photos API」→「我要怎麼把相片弄到 Drive」
  - 路線 A：Google Takeout 直接送 Drive（不需任何 API，可拿到原始品質）
  - 路線 B：手動下載到本機，Python 直接讀本機路徑
  - 路線 C：先確認 Drive 是否已自動同步（用 Drive API 替代）

**下一步：** 用戶先確認路線 C → 若否則執行路線 A 或 B → 再通知 A4 接手

---



**更新：**
- `CURRENT_EXECUTION_BOARD.md` v1.1 — A5 狀態標記 ✅ 完成，A4 標記 ⭐ 等待中

**下一步：** A4 Pipeline Agent 接手，依據 schema 設計 pipeline mapping

---



執行 Agent：A1 Handbook Agent（Claude）

新增文件：
- README.md v2.2（新增 Business Objective 章節，說明商業主軸）
- REPO_SYNC_RULES.md v0.1（新建，定義 4 個 repo 的同步觸發規則、Owner 責任、不需回寫清單）
- CURRENT_EXECUTION_BOARD.md v1.0（新建，A1-A7 即時狀態 + 第一個閉環目標 A5→A4→A1）

更新文件：
- projects/maplab-master-data.md v1.4（新增 SECTION 3：A5 Schema v0.1 任務書，含 4 個必要輸出物與成功條件）

來源：GPT 建議（GitHub專案文件結構對話，下一步規劃 v1.1）

---

## v2.1 — 2026-03-14

**新增視覺化系統全圖**

執行 Agent：A1 Handbook Agent（Claude）

新增文件：
- SYSTEM_MAP.md v1.0（新建，5 張 ASCII 視覺化地圖：Repo分工/Agent分工/資料流向/文件閱讀順序/模型選擇速查）
- README.md v2.1（頂部加 SYSTEM_MAP callout + Quick Start Step 1 改為先讀 SYSTEM_MAP）

---

## v2.0 — 2026-03-14

**重大改版：建立完整 3 層文件結構**

執行 Agent：A1 Handbook Agent（Claude）

新增文件：
- README.md v2.0（重寫，新增 Mission / Why / Success Definition / Agent Roster / Quick Start / Repo Map）
- PROJECT_CONTEXT.md v1.0（新建，5個專案詳細地圖 + 依賴關係）
- AI_WORKFLOW_MAP.md v1.0（新建，模型分工 + Agent flow + Handoff Protocol + 4條協作規則）
- AGENT_STARTUP_PROTOCOL.md v1.0（新建，8步啟動SOP + 收尾SOP）
- CHANGELOG.md（本文件，新建）

來源：GPT 建議（GitHub專案文件結構對話，2026-03-14）

---

## v1.5 — 2026-03-14（同日早期）

**AGENT_RULES.md 更新 + 新增 4 個文件**

執行 Agent：A1 Handbook Agent（Claude）

變更：
- AGENT_RULES.md：v1.4 → v1.5（新增 A7 AI Reply System Agent + 錯誤 003）
- projects/maplab-ads-monitor.md：新建 v1.0（A6 技術文件）
- skills/superpowers-guide.md：新建 v1.0（13 項核心技能，來源 Notion）
- projects/maplab-pipeline.md：v1.0 → v1.1（更新至 Notion v2.2 進度）

---

## v1.4 — 2026-03-14（同日早期）

**B/C 類別 Agent 統一升格為 A 組**

執行 Agent：A1 Handbook Agent（Claude）

變更：
- AGENT_RULES.md：v1.3 → v1.4（A1-A6 統一表格，B/C 類別合併至 A 組）
- 來源：Notion MAPLAB Agent 角色分類表

---

## v1.3 — 建立初期

初始版本，包含：
- README.md（基礎版，只有快速連結）
- AGENT_RULES.md v1.3
- projects/ 目錄（4 個初始文件）
- handoff/HANDOFF_TEMPLATE.md

---

## 格式說明

新增版本記錄時請遵循以下格式：

版本號格式：v主版本.次版本（重大功能變更升主版本，小更新升次版本）

每條記錄包含：版本號、日期、執行 Agent、變更內容分類（新增/修改/刪除/修復）

同步觸發：每次更新 CHANGELOG 也必須更新 CURRENT_EXECUTION_BOARD.md 的系統整體狀態

---

*維護者：A1 Handbook Agent | 每次系統更新後必須更新本文件*
