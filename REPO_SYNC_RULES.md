# REPO_SYNC_RULES.md — Repo 間同步規則

**版本：v0.1 | 建立：2026-03-14 | 維護者：A1 Handbook Agent**

本文件定義 `maplab-ai-handbook`（公開治理層）與各 private repo 之間的同步規則，避免規則、進度與實作三方脫節。

---

## Purpose（目的）

當多個 Agent 同時在不同 repo 工作時，最常出現的問題是：

- 私有 repo 有新進度，但 handbook 的 PROJECT_CONTEXT 沒更新
- Agent 角色增加或改變，但 AGENT_RULES 沒同步
- 命名規則、欄位標準在實作中悄悄改了，但文件還是舊的

RESULT：下一個 Agent 接手時讀到錯誤資訊，從頭重做。

本規則的目標：**讓 handbook 永遠是唯一可信的公開規則源。**

---

## Repo Roles（各 Repo 職責）

| Repo | 性質 | 職責 |
|------|------|------|
| maplab-ai-handbook | 公開・治理層 | 規則源 / 專案地圖 / Agent 協作框架 / 入口文件 |
| maplab-pipeline | 私有・執行層 | 相簿自動化實作、資料流程腳本 |
| maplab-Detasys | 私有・執行層 | SEO / Ads / Monitor 腳本與分析工具 |
| maplab-master-data | 私有・資料層 | ERP schema / Sheets 主資料設計 |

**原則：handbook 定義「是什麼、為什麼、怎麼協作」，private repo 定義「怎麼做到」。**

---

## Must Sync Back to Handbook（必須回寫的情況）

以下任何變更發生後，負責 Agent **必須在完成後 48 小時內**同步回 handbook：

**角色與架構類**
- 新增或修改 Agent 角色 → 更新 AGENT_RULES.md
- 新增 projects/*.md → 更新 AGENT_RULES.md SECTION 1 角色表
- 工作流或資料流改變 → 更新 AI_WORKFLOW_MAP.md

**專案進度類**
- 專案 phase 推進（如 Phase 1 → Phase 2）→ 更新 PROJECT_CONTEXT.md
- 里程碑完成 → 更新 projects/對應文件 + CHANGELOG.md
- 專案依賴項變更（如 schema 改了影響 pipeline）→ 更新 PROJECT_CONTEXT.md

**規則與標準類**
- 命名規則改變 → 更新對應 projects/ 文件
- handoff 格式改變 → 更新 handoff/HANDOFF_TEMPLATE.md
- 啟動 SOP 改變 → 更新 AGENT_STARTUP_PROTOCOL.md
- 可抽象為通用方法的執行經驗 → 更新 skills/superpowers-guide.md

**版本紀錄類**
- 任何上述變更 → 都必須在 CHANGELOG.md 新增一條記錄

---

## Keep Only in Private Repo（不必回寫的內容）

以下內容**留在 private repo 即可**，不需回寫 handbook：

- API keys / secrets / .env 設定（永遠不上 GitHub）
- 細部程式碼實作（腳本邏輯、函數細節）
- 暫時性 debug 紀錄
- 敏感客戶或營運資料
- 僅限單次執行的技術細節
- 實驗性分支或尚未穩定的功能

---

## Sync Trigger（觸發同步的時機點）

| 事件 | 必須更新的 handbook 文件 |
|------|------------------------|
| 新 Agent 角色啟用 | AGENT_RULES.md + CHANGELOG.md |
| 專案 phase 變更 | PROJECT_CONTEXT.md + projects/對應文件 + CHANGELOG.md |
| Schema / 欄位命名規則改變 | projects/對應文件 + CHANGELOG.md |
| 新 handoff 完成 | handoff/ + CHANGELOG.md |
| Workflow 重大調整 | AI_WORKFLOW_MAP.md + CHANGELOG.md |
| 系統地圖需要更新 | SYSTEM_MAP.md + CHANGELOG.md |

---

## Owner（誰負責執行同步）

- **規則層更新**（AGENT_RULES / STARTUP_PROTOCOL / REPO_SYNC_RULES）→ A1 Handbook Agent
- **執行層回報**（pipeline / Detasys 的 phase 進度）→ 對應 repo 的 Agent（A4 / A6）提交 handoff，A1 回寫
- **資料層回報**（master-data schema 變更）→ A5 提交 handoff，A1 回寫
- **最終合併**：由負責該 repo 的主 Agent 提交 handoff → A1 Handbook Agent 執行 handbook 更新

---

## Version Log（本文件版本）

- v0.1（2026-03-14）：初版建立，定義 4 個 repo 的同步規則基礎框架
- v0.2：待第一次實戰 handoff 後依實際情況修訂

---

*下次更新時機：A5 Master Data schema v0.1 完成並 handoff 給 A4 後*
