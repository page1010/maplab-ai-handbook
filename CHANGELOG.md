# CHANGELOG.md — MAPLAB AI System 版本演進紀錄

本文件記錄 maplab-ai-handbook 的所有重大版本變更。
格式：版本號 | 日期 | 變更摘要 | 執行 Agent

---

## v2.0 — 2026-03-14

**重大改版：建立 3 層文件結構**

執行 Agent：A1 Handbook Agent（Claude）

新增文件：
- README.md v2.0（重寫，新增 Mission / Why / Success Definition / Agent Roster / Quick Start / Repo Map）
- PROJECT_CONTEXT.md v1.0（新建，5個專案詳細地圖 + 依賴關係）
- AI_WORKFLOW_MAP.md v1.0（新建，模型分工 + Agent flow + Handoff Protocol）
- AGENT_STARTUP_PROTOCOL.md v1.0（新建，8步啟動 SOP + 收尾 SOP）
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

版本號 格式：v主版本.次版本（重大功能變更升主版本，小更新升次版本）

每條記錄包含：版本號、日期、執行 Agent、變更內容分類（新增/修改/刪除/修復）

---

*維護者：A1 Handbook Agent | 每次系統更新後必須更新本文件*
