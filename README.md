# MAPLAB AI Multi-Agent System

**每次接手前，請先讀這份文件。讀完你就知道系統在哪、你要做什麼。**

> 想快速看懂整個系統架構？直接看 **[SYSTEM_MAP.md](./SYSTEM_MAP.md)** — 5 張視覺化地圖，1分鐘掌握全局。

---

## 1. Mission

MAPLAB AI Multi-Agent System 是一套用於支援 MAPLAB Kitchen（台南高階外燴品牌）的多 Agent 協作系統。

系統目標：讓 AI 接手重複性高的知識整理、內容生成、資料整理、監控與回覆工作，讓人類保留決策、審核、商業判斷與最終定稿權，建立可版本化、可交接、可擴充的 AI 工作流。

---

## 2. Why This Exists

目前單一 AI 對話容易出現：不知道目前專案進度、不知道自己角色邊界、不知道哪些資料已存在、每次接手都從頭開始、不同模型各自做事彼此無法對齊等問題。

因此建立本系統，目的是：統一 Agent 角色與職責、統一專案文件與交接規則、統一版本上下文、降低重工與幻覺風險、讓任何新 Agent 在 30 分鐘內進入工作狀態。

---

## 3. Core Projects

| 專案 | 負責 Agent | 主要 Repo | 當前狀態 |
|------|-----------|----------|---------|
| MAPLAB Pipeline（相簿自動化） | A4 | maplab-pipeline | Phase 1 進行中 |
| SEO & Ads Agent | A2/A3 | maplab-Detasys | SEO Python v1.4，廣告修復中 |
| MAPLAB Master Data（廚房 ERP） | A5 | maplab-master-data | v0.7 架構設計中 |
| AI Reply System（自動回覆） | A7 | maplab-ai-handbook | 規則建立中 |
| Handbook & 系統治理 | A1 | maplab-ai-handbook（本 repo） | 持續維護 |

**Notion 控制台**（任務看板、最新交辦）：請向 owner 索取連結，或搜尋「AI 自動工作團隊控制台」

---

## 4. Success Definition

系統成功時：任何 Agent 能在不詢問 owner 的情況下獨立找到任務、理解脈絡、開始執行；Agent 不會互相覆蓋彼此的工作；每個修改都有版本紀錄；人類只需要做決策與最終審核；重複性工作由 AI 處理佔比 80% 以上。

---

## 5. Agent Roster（快速查詢）

| Agent | 名稱 | 主要職責 | 建議使用模型 |
|-------|------|---------|------------|
| A1 | Handbook Agent | 系統文件、規則治理、交接維護 | Claude |
| A2 | SEO Content Agent | SEO 文章生成與優化 | GPT |
| A3 | Ads Monitor Agent | 廣告監控、成效分析 | GPT / Claude |
| A4 | Pipeline Agent | 資料流程、相簿整理自動化 | Claude |
| A5 | Master Data Agent | 廚房 ERP、主資料結構 | Gemini / Claude |
| A6 | Ads Tech Agent | 廣告技術文件、腳本維護 | Claude |
| A7 | AI Reply System Agent | 對話紀錄整理、自動回覆模組 | GPT |

詳細角色規則請見 [AGENT_RULES.md](./AGENT_RULES.md)

---

## 6. Document Structure（本 Repo 結構）

```
maplab-ai-handbook/
├── README.md                    ← 你在這裡（系統大局觀）
├── SYSTEM_MAP.md                ← 視覺化系統全圖（推薦第一個看）
├── PROJECT_CONTEXT.md           ← 各專案詳細地圖
├── AI_WORKFLOW_MAP.md           ← Agent 協作流程圖
├── AGENT_RULES.md               ← 所有 Agent 共用行為準則 v1.5
├── AGENT_STARTUP_PROTOCOL.md   ← 接手前必讀 SOP
├── CHANGELOG.md                 ← 系統版本演進紀錄
├── projects/
│   ├── ai-reply-system.md       ← A7 專案文件
│   ├── maplab-ads-monitor.md    ← A6 技術文件
│   ├── maplab-master-data.md    ← A5 專案文件
│   ├── maplab-pipeline.md       ← A4 專案文件
│   └── seo-ads-agent.md         ← A2/A3 專案文件
├── skills/
│   └── superpowers-guide.md     ← 13 項核心技能導覽
└── handoff/
    └── HANDOFF_TEMPLATE.md      ← 標準交接格式
```

---

## 7. Quick Start（接手時讀這個）

接手前必讀順序（Step 1 → 8）：

**Step 1.** 閱讀 [SYSTEM_MAP.md](./SYSTEM_MAP.md)（視覺化全圖，1分鐘掌握全局）

**Step 2.** 閱讀本 README.md（系統使命與成功定義）

**Step 3.** 閱讀 [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md)（各專案現況）

**Step 4.** 閱讀 [AI_WORKFLOW_MAP.md](./AI_WORKFLOW_MAP.md)（協作流程）

**Step 5.** 閱讀 [AGENT_RULES.md](./AGENT_RULES.md)（角色與禁止事項）

**Step 6.** 閱讀 [AGENT_STARTUP_PROTOCOL.md](./AGENT_STARTUP_PROTOCOL.md)（接手 SOP）

**Step 7.** 閱讀對應 [projects/](./projects/) 專案文件

**Step 8.** 閱讀最新 handoff/ 或 [CHANGELOG.md](./CHANGELOG.md)

---

## 8. Repo Map → 詳見 SYSTEM_MAP.md

[點這裡看完整視覺化地圖 →](./SYSTEM_MAP.md)

| Repo | 性質 | 用途 |
|------|------|------|
| maplab-ai-handbook（本 repo） | 公開・治理層 | Agent 規則、文件、handoff 中樞 |
| maplab-pipeline | 私有・執行層 | 相簿自動化、Google Photos → WebP → Drive |
| maplab-Detasys | 私有・執行層 | SEO/廣告 Python 腳本 |
| maplab-master-data | 私有・資料層 | 廚房 ERP、主資料 Sheets（待建立） |

---

*系統版本：v2.1 | 最後更新：2026-03-14 | 維護者：A1 Handbook Agent*
