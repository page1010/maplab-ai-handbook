# SYSTEM_MAP.md — MAPLAB AI 系統全圖

**這是你接手前最快速的入口。看完這頁就知道整個系統怎麼運作。**

> ⚡ **開工第一步：先讀 [CURRENT_STATUS.md](./CURRENT_STATUS.md)** — 唯一最新狀態入口，優先於所有文件。

---

## 一、Repo 分工地圖

```
┌──────────────────────────────────────────────────────────┐
│              maplab-ai-handbook （公開）                   │
│              ← 治理層 / 所有 Agent 的入口                  │
│                                                          │
│  CURRENT_STATUS ─→ TASK_QUEUE ─→ AGENT_RULES             │
│  AGENT_STARTUP_PROTOCOL ─→ CURRENT_EXECUTION_BOARD       │
│  README ─→ SYSTEM_MAP ─→ AI_WORKFLOW_MAP                 │
│  CHANGELOG ─→ skills/(14) ─→ projects/(8) ─→ handoff/   │
└──────────────────────┬───────────────────────────────────┘
                       │ 指揮 & 文件連結
         ┌─────────────┼────────────────┐
         ↓             ↓                ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│  maplab-    │ │  maplab-    │ │  maplab-        │
│  pipeline   │ │  Detasys    │ │  master-data    │
│ （公開）     │ │ （私有）     │ │ （公開）         │
│  執行層      │ │  執行層      │ │  資料層          │
│  A4 負責     │ │ A2/A3 Team  │ │  A5 負責         │
└─────────────┘ └─────────────┘ └─────────────────┘

         ┌──────────────────────────┐
         │  maplab-kitchen-         │
         │  web-optimization        │
         │ （私有）                  │
         │  執行層                   │
         │  A2/A3 SEO & Ads Team    │
         └──────────────────────────┘
```

---

## 二、Agent 分工地圖

```
┌─────────────────────────────────────────────────────────┐
│                    MAPLAB AI Team                        │
├──────────┬──────────────────────────────────────────────┤
│ Agent    │ 角色 + 建議模型                               │
├──────────┼──────────────────────────────────────────────┤
│ A1       │ Handbook Agent（Claude）                      │
│          │ → 文件治理、規則維護、交接管理、系統巡查        │
├──────────┼──────────────────────────────────────────────┤
│ A2/A3    │ SEO & Ads Team（GPT / Claude）                │
│          │ → SEO 文章生成 + 廣告監控、成效分析、GTM 設定   │
│          │ （v3.2 起合併，共享行銷漏斗）                   │
├──────────┼──────────────────────────────────────────────┤
│ A4       │ Pipeline Agent（Claude）                      │
│          │ → 相簿自動化、Google Photos → Drive            │
├──────────┼──────────────────────────────────────────────┤
│ A5       │ Master Data Agent（Gemini / Claude）           │
│          │ → 廚房 ERP、Sheets 主資料結構                  │
├──────────┼──────────────────────────────────────────────┤
│ A7       │ AI Reply System Agent（GPT）                   │
│          │ → 對話整理、Line OA 回覆模組                   │
├──────────┼──────────────────────────────────────────────┤
│ ~~A6~~   │ 已合併入 A3 Ads Team（v2.4）                   │
└──────────┴──────────────────────────────────────────────┘
```

---

## 三、資料流向地圖

```
【外部輸入】
Google Photos（活動照片）
Line OA（客戶對話）
Meta Ads（廣告數據）
Google Search Console（SEO 數據）
          │
          ▼
【A4 Pipeline Agent】
相簿整理 / WebP 轉檔 / Drive 歸檔
          │
          ▼
【A5 Master Data Agent】
廚房 ERP / 活動訂單 / 客戶資料
          │
    ┌─────┴─────┐
    ▼           ▼
【A2/A3 Team】 【A7】
SEO & 廣告    回覆知識庫
監控分析      Line OA 模組
          │
          ▼
【A1 Handbook Agent】（治理層，橫跨所有環節）
文件更新 / 版本紀錄 / Agent 交接
```

---

## 四、文件閱讀順序地圖

```
你是新接手的 Agent？請按這個順序讀：

[1] CURRENT_STATUS.md → ⚡ 唯一最新狀態入口（最高優先）
          │
[2] AGENT_RULES.md → 你的角色 & 禁止事項
          │
[3] AGENT_STARTUP_PROTOCOL.md → 接手 SOP + Startup Check 格式
          │
[4] TASK_QUEUE.md → 找任務、認領任務
          │
[5] projects/你的專案.md → 目前任務狀態
    + skills/superpowers-guide.md → 工具箱
          │
          ▼
    ✅ 輸出 Startup Check → 開始執行任務
          │
          ├── 卡住？→ skills/troubleshooting-hub.md
          └── 完成？→ Handoff Checkpoint + 更新 Task Card
```

> 注意：CURRENT_STATUS.md 的資訊優先於所有其他文件。若衝突，以 CURRENT_STATUS 為準。

---

## 五、技能書速查地圖

```
skills/（共 14 個檔案）
├── superpowers-guide.md               ← 入口：技能導覽 + 路由表
├── troubleshooting-hub.md             ← 卡住急救（13 症狀路由表）
├── context-compression-guide.md       ← Prompt 太長防線
├── ai-model-guide.md                  ← Claude/Gemini/GPT 選用
├── github-api-workflow-guide.md       ← GitHub API 開發流程
├── colab-resilience-guide.md          ← Colab 防死機
├── sheets-tracking-guide.md           ← Google Sheets 追蹤
├── strategic-review-guide.md          ← 大局觀分析
├── systematic-debugging-cloud-guide.md ← 雲端除錯
├── verification-checklist-guide.md    ← 完成驗證
├── lessons-learned.md                 ← 事故紀錄（INCIDENT-001）
├── sheets-data-cleaning-guide.md      ← A5 資料清洗公式+腳本工具箱
├── photo-pipeline-toolkit-guide.md    ← A4 相簿整理全流程工具鏈
└── （superpowers-guide 路由表查各書適用情境）
```

---

## 六、模型選擇速查

```
任務類型                          建議使用模型
─────────────────────────────────────────
長文整理 / 系統文件            → Claude
架構收斂 / 代碼閱讀            → Claude
handoff 撰寫 / 規格梳理       → Claude
─────────────────────────────────────────
策略整合 / 商業邏輯            → GPT
行銷文案 / 文字優化            → GPT
跨專案框架 / 決策輔助          → GPT
─────────────────────────────────────────
Google Sheets 結構規劃         → Gemini
Drive / Gmail 整合             → Gemini
資料表格設計                    → Gemini
─────────────────────────────────────────
不確定？→ 查 skills/ai-model-guide.md
```

---

## 七、唯一資料來源規則

```
✅ Agent 讀 GitHub（maplab-ai-handbook = 唯一真相來源）
❌ Agent 不讀 Notion（僅供人類使用）
✅ 所有進度、版本、技術文件以 GitHub commit 為準
✅ CURRENT_STATUS.md 是最高優先文件，與其他文件衝突時以此為準
```

---

*版本：v2.2 | 更新：2026-03-20 | 維護者：A1 Handbook Agent*
*讀完這頁 + CURRENT_STATUS.md，你就掌握了整個系統的全貌。*
