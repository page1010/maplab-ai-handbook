# MAPLAB AI Multi-Agent System

> **⚡ 開工第一步：先讀 [CURRENT_STATUS.md](./CURRENT_STATUS.md) — 唯一最新狀態入口，優先於本文件。**

**每次接手前，請先讀這份文件。讀完你就知道系統在哪、你要做什麼。**

> 想快速看懂整個系統架構？直接看 **[SYSTEM_MAP.md](./SYSTEM_MAP.md)** — 視覺化地圖，1分鐘掌握全局。

---

## 1. Mission

MAPLAB AI Multi-Agent System 是一套用於支援 MAPLAB Kitchen（台南高階外燴品牌）的多 Agent 協作系統。

系統目標：讓 AI 接手重複性高的知識整理、內容生成、資料整理、監控與回覆工作，讓人類保留決策、審核、商業判斷與最終定稿權，建立可版本化、可交接、可擴充的 AI 工作流。

---

## 2. Business Objective

MAPLAB AI 系統的商業主軸是：
**降低重工、提升內容生產效率、把知識沉澱成可複用資產，最終支援 MAPLAB Kitchen 的品牌成長、廣告優化、ERP 效率與自動回覆能力。**

具體來說：
- 相簿整理與命名自動化 → 減少活動後手動作業時間
- SEO 文章與廣告監控 → 降低行銷人力成本，提升投放精準度
- 廚房 ERP 主資料 → 讓訂單、品項、客戶資料可被追蹤與重用
- AI 自動回覆 → 把過去成功的對話轉化為可複用知識庫
- Handbook 治理 → 讓每個 AI Agent 接手時不從零開始，縮短啟動時間

---

## 3. Why This Exists

目前單一 AI 對話容易出現：不知道目前專案進度、不知道自己角色邊界、不知道哪些資料已存在、每次接手都從頭開始、不同模型各自做事彼此無法對齊等問題。

因此建立本系統，目的是：統一 Agent 角色與職責、統一專案文件與交接規則、統一版本上下文、降低重工與幻覺風險、讓任何新 Agent 在 30 分鐘內進入工作狀態。

---

## 4. Success Definition

系統成功時：任何 Agent 能在不詢問 owner 的情況下獨立找到任務、理解脈絡、開始執行；Agent 不會互相覆蓋彼此的工作；每個修改都有版本紀錄；人類只需要做決策與最終審核；重複性工作由 AI 處理佔比 80% 以上。

---

## 5. Core Projects

| 專案 | 負責 Agent | 主要 Repo | 當前狀態 |
|------|-----------|----------|---------|
| MAPLAB Pipeline（相簿自動化） | A4 | maplab-pipeline | Phase 2/3 完成，cloud-only，等待用戶確認相片來源 |
| SEO & Ads（SEO & Ads Team） | A2/A3 | maplab-Detasys | seo-ads-agent v2.1 + GTM v15 已發布 |
| MAPLAB Master Data（廚房 ERP） | A5 | maplab-master-data | Schema v0.1 + QUOTE_DRAFT 完成 |
| AI Reply System（自動回覆） | A7 | maplab-ai-handbook | v1.0 框架建立完成 |
| Handbook & 系統治理 | A1 | maplab-ai-handbook（本 repo） | v3.4 持續維護 |

### 5.1 各專案詳細脈絡

**Pipeline（相簿自動化）：** Google Photos（唯讀）→ WebP 轉檔 → Google Drive 歸檔。關鍵約束：絕對不得刪除原始照片。詳見 [projects/maplab-pipeline.md](./projects/maplab-pipeline.md)

**SEO & Ads（SEO & Ads Team）：** 廣告監控 + SEO 內容 + GTM 轉換事件。A2（SEO）+A3（Ads）合併為 SEO & Ads Team（v3.2 起），共享行銷漏斗。詳見 [projects/seo-ads-agent.md](./projects/seo-ads-agent.md)

**Master Data（廚房 ERP）：** 客戶、訂單、食材、報價單。Google Sheets 為主。詳見 [projects/maplab-master-data.md](./projects/maplab-master-data.md)

**AI Reply System：** 對話紀錄整理 + 回覆規則 + Line OA。詳見 [projects/ai-reply-system.md](./projects/ai-reply-system.md)

**Handbook：** 本 repo，所有 Agent 知識基礎與治理中樞。

### 5.2 系統依賴關係

Handbook（治理層）連結所有專案。執行鏈：Master Data（資料底座）→ Pipeline（資料流動）→ SEO/Ads（分析監控）→ AI Reply（知識應用）。

---

## 6. Agent Roster（快速查詢）

| Agent | 名稱 | 主要職責 | 建議模型 |
|-------|------|---------|--------|
| A1 | Handbook Agent | 系統文件、規則治理、交接維護 | Claude |
| A2/A3 | SEO & Ads Team | SEO 文章生成 + 廣告監控、成效分析、GTM 設定 | GPT / Claude |
| A4 | Pipeline Agent | 資料流程、相簿整理自動化 | Claude |
| A5 | Master Data Agent | 廚房 ERP、主資料結構 | Gemini / Claude |
| A7 | AI Reply System Agent | 對話紀錄整理、自動回覆模組 | GPT |

> A2+A3 於 v3.2 合併為 SEO & Ads Team，共享行銷漏斗（關鍵字→內容→廣告→轉換）。
> A6 已於 v2.4 合併入 A3 Ads Team，不再單獨使用。

詳細角色規則請見 [AGENT_RULES.md](./AGENT_RULES.md)

---

## 7. Document Structure（本 Repo 結構）

```
maplab-ai-handbook/
├── CURRENT_STATUS.md        ← ⚡ 唯一最新狀態入口（開工第一讀）
├── TASK_QUEUE.md             ← 任務池（認領任務）
├── README.md                 ← 你在這裡
├── SYSTEM_MAP.md             ← 視覺化系統全圖
├── AI_WORKFLOW_MAP.md        ← Agent 協作流程圖
├── AGENT_RULES.md            ← Agent 行為準則 v1.8
├── AGENT_STARTUP_PROTOCOL.md ← 接手 SOP v1.2
├── REPO_SYNC_RULES.md        ← Repo 間同步規則
├── CURRENT_EXECUTION_BOARD.md ← 詳細看板（參考）
├── CHANGELOG.md              ← 版本紀錄
├── projects/（6 個專案文件）
├── skills/（14 個技能書）
└── handoff/（5 個交接文件 + tasks/ 任務卡）
```

---

## 8. Quick Start（接手時讀這個）

**Step 1.** [CURRENT_STATUS.md](./CURRENT_STATUS.md)（⚡ 唯一最新狀態入口，最高優先）
**Step 2.** [AGENT_RULES.md](./AGENT_RULES.md)（你的角色 & 禁止事項）
**Step 3.** [AGENT_STARTUP_PROTOCOL.md](./AGENT_STARTUP_PROTOCOL.md)（接手 SOP + Startup Check 格式）
**Step 4.** [TASK_QUEUE.md](./TASK_QUEUE.md)（找任務、認領任務）
**Step 5.** 對應 [projects/](./projects/) + [skills/superpowers-guide.md](./skills/superpowers-guide.md)
**Step 6.** 輸出 Startup Check → 開始執行

> 注意：CURRENT_STATUS.md 的資訊優先於所有其他文件。若衝突，以 CURRENT_STATUS 為準。

---

## 9. Repo Map

[完整視覺化地圖 →](./SYSTEM_MAP.md)

| Repo | 性質 | 用途 |
|------|------|------|
| maplab-ai-handbook（本 repo） | 公開・治理層 | Agent 規則、文件、handoff 中樞 |
| maplab-pipeline | 公開・執行層 | 相簿自動化 |
| maplab-Detasys | 私有・執行層 | SEO/廣告 Python 腳本 |
| maplab-master-data | 公開・資料層 | 廚房 ERP、主資料 Sheets |

同步規則詳見 [REPO_SYNC_RULES.md](./REPO_SYNC_RULES.md)

---

## 10. 唯一資料來源規則

**GitHub 是所有 Agent 的唯一資料來源。** Notion 僅供人類使用（控制台/看板），Agent 不讀 Notion。所有進度、版本、技術文件一律以 GitHub commit 為準。

---

*系統版本：v3.4 | 最後更新：2026-03-19 | 維護者：A1 Handbook Agent | README v2.4*
