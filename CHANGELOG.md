# CHANGELOG.md — MAPLAB AI System 版本演進紀錄

本文件記錄 maplab-ai-handbook 的所有重大版本變更。
格式：版本號 | 日期 | 變更摘要 | 執行 Agent

---

## v2.2 — 2026-03-14（最新）

**進入執行階段：補齊同步機制 + 建立執行看板 + 啟動 A5 任務**

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
