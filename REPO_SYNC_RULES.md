# REPO_SYNC_RULES.md — Repo 間同步規則

**版本：v1.1 | 建立：2026-03-14 | 更新：2026-03-20 | 維護者：A1 Handbook Agent**

本文件定義 maplab-ai-handbook（公開治理層）與各執行層 repo 之間的同步規則，避免規則、進度與實作三方脫節。

---

## Purpose（目的）

當多個 Agent 同時在不同 repo 工作時，最常出現的問題是：
- 執行層 repo 有新進度，但 handbook 的 CURRENT_STATUS / TASK_QUEUE 沒更新
- Agent 角色增加或改變，但 AGENT_RULES 沒同步
- 命名規則、欄位標準在實作中悄悄改了，但文件還是舊的

RESULT：下一個 Agent 接手時讀到錯誤資訊，從頭重做。

本規則的目標：**讓 handbook 永遠是唯一可信的公開規則源。**

---

## Repo Roles（各 Repo 職責）

| Repo | 性質 | 職責 | 負責 Agent |
|------|------|------|-----------|
| maplab-ai-handbook | 公開・治理層 | 規則源 / CURRENT_STATUS / TASK_QUEUE / Agent 協作框架 | A1 |
| maplab-pipeline | 公開・執行層 | 相簿自動化實作、資料流程腳本 | A4 |
| maplab-Detasys | 私有・執行層 | SEO / Ads / Monitor 腳本與分析工具 | A2/A3 SEO & Ads Team |
| maplab-master-data | 公開・資料層 | ERP schema / Sheets 主資料設計 | A5 |
| maplab-kitchen-web-optimization | 私有・執行層 | 官網 SEO / RWD / Landing Page / PageSpeed 優化 | A2/A3 SEO & Ads Team |

**原則：handbook 定義「是什麼、為什麼、怎麼協作」，執行層 repo 定義「怎麼做到」。**

---

## Must Sync Back to Handbook（必須回寫的情況）

以下任何變更發生後，負責 Agent **必須在完成後 48 小時內**同步回 handbook：

**狀態類（最高優先）**
- 任務狀態改變 → 更新 CURRENT_STATUS.md + TASK_QUEUE.md
- Blocker 出現或解除 → 更新 CURRENT_STATUS.md Blockers 區段
- 決策確認 → 更新 CURRENT_STATUS.md 最新決策

**角色與架構類**
- 新增或修改 Agent 角色 → 更新 AGENT_RULES.md
- 新增 projects/*.md → 更新 AGENT_RULES.md SECTION 1 角色表
- 工作流或資料流改變 → 更新 AI_WORKFLOW_MAP.md

**專案進度類**
- 專案 phase 推進（如 Phase 3 → Phase 4）→ 更新 projects/對應文件 + CURRENT_STATUS.md
- 里程碑完成 → 更新 projects/對應文件 + CHANGELOG.md
- 專案依賴項變更（如 schema 改了影響 pipeline）→ 更新 projects/對應文件

**規則與標準類**
- 命名規則改變 → 更新對應 projects/ 文件
- handoff 格式改變 → 更新 handoff/HANDOFF_TEMPLATE.md
- 啟動 SOP 改變 → 更新 AGENT_STARTUP_PROTOCOL.md
- 可抽象為通用方法的執行經驗 → 更新 skills/superpowers-guide.md

**版本紀錄類**
- 任何上述變更 → 都必須在 CHANGELOG.md 新增一條記錄

---

## Keep Only in Private Repo（不必回寫的內容）

以下內容**留在執行層 repo 即可**，不需回寫 handbook：
- API keys / secrets / .env 設定（永遠不上 GitHub 公開 repo）
- 細部程式碼實作（腳本邏輯、函數細節）
- 暫時性 debug 紀錄
- 敏感客戶或營運資料
- 僅限單次執行的技術細節
- 實驗性分支或尚未穩定的功能

---

## Sync Trigger（觸發同步的時機點）

| 事件 | 必須更新的 handbook 文件 |
|------|------------------------|
| 任務完成或狀態改變 | CURRENT_STATUS.md + TASK_QUEUE.md + CHANGELOG.md |
| 新 Agent 角色啟用 | AGENT_RULES.md + CHANGELOG.md |
| 專案 phase 變更 | projects/對應文件 + CURRENT_STATUS.md + CHANGELOG.md |
| Schema / 欄位命名規則改變 | projects/對應文件 + CHANGELOG.md |
| 新 handoff 完成 | handoff/tasks/T-xxx.md（Task Card）+ TASK_QUEUE.md |
| Workflow 重大調整 | AI_WORKFLOW_MAP.md + CHANGELOG.md |
| 系統地圖需要更新 | SYSTEM_MAP.md + CHANGELOG.md |
| 新技能或工具發現 | skills/ 對應檔案 + superpowers-guide.md 路由表 |

---

## Owner（誰負責執行同步）

- **治理層更新**（CURRENT_STATUS / TASK_QUEUE / AGENT_RULES / PROTOCOL / REPO_SYNC_RULES）→ A1 Handbook Agent
- **執行層回報**（pipeline 的 phase 進度）→ A4 提交 Handoff Checkpoint，A1 回寫
- **SEO & Ads 回報**（Detasys 的廣告/SEO 進度）→ A2/A3 提交 Handoff Checkpoint，A1 回寫
- **資料層回報**（master-data schema 變更）→ A5 提交 Handoff Checkpoint，A1 回寫
- **最終合併**：由負責該 repo 的主 Agent 提交 Handoff Checkpoint → A1 Handbook Agent 執行 handbook 更新

---

## Version Log（本文件版本）

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.1 | 2026-03-20 | 新增 maplab-kitchen-web-optimization repo（私有・執行層）+ Owner 同步職責 | A1 Handbook Agent |
| v1.0 | 2026-03-19 | 全面重寫：移除 PROJECT_CONTEXT 引用、對齊 CURRENT_STATUS/TASK_QUEUE、修正 repo 公私標示、A6→A2/A3 SEO & Ads Team | A1 Handbook Agent |
| v0.1 | 2026-03-14 | 初版建立，定義 4 個 repo 的同步規則基礎框架 | A1 Handbook Agent |
