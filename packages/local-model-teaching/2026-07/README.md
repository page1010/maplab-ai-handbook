# 地端模型教材包 — 2026-07（骨架版）

> 版本：MVP 骨架（B5 首次執行 2026-07-11，A1 代理）
> 目標模型：Ollama Qwen2.5:14b、gemma4
> 打包腳本：`scripts/b5-pack-teaching-package.sh`
> 評分基準：`reports/capability-inventory/inventory_2026-07.md`

---

## 教材包說明

這個教材包的目的：讓地端 Ollama 模型以最少資源繼承 MAPLAB 系統 2026 年上半年累積的工作智慧。

**不包含的內容**：
- MCP 工具呼叫流程（地端無法存取）
- GAS / Google Drive / Sheets API 細節（需即時存取）
- OAuth / credentials（安全原因）
- 超過 90 天的任務狀態（過時）

---

## 目錄結構

```
2026-07/
├── README.md                  ← 本文件（說明 + 適用模型）
├── recall_prompts/            ← 精煉版各角色召回 prompt（移除 MCP/API 依賴段落）
│   ├── README.md              ← 說明：地端版 vs 完整版的差異
│   └── [角色]_local.md       ← 待打包腳本自動填充
├── top_jobs/                  ← 評分 >= 4 的 JOB 輸出（高品質示範）
│   ├── README.md              ← 待打包
│   └── [job]-extract.md      ← 待打包腳本自動提取
├── eval_cases/                ← 從 weekly_eval_compounding 精選案例
│   ├── README.md              ← 待打包
│   └── [eval]-case.md        ← 待打包
└── pitfalls_digest.md         ← pitfalls.md 蒸餾版（去重 + 分類，待腳本生成）
```

---

## 本月評分 ≥ 4 的已識別項目

根據 `reports/capability-inventory/inventory_2026-07.md`：

**可直接打包（評分 5）：**
- docs/fable-mindset.md — 工作思維 10 條
- skills/task-progress-guide.md — 進度回報格式
- skills/brand-voice-guide.md — 品牌語氣
- skills/first-principles-check/SKILL.md — 決策框架
- skills/a6-safety-boundaries.md — 安全邊界
- skills/session-handoff.md — Session 交接格式
- pitfalls.md 中 6 條通用行為規則

**待下次打包完整版時執行：**
```bash
bash scripts/b5-pack-teaching-package.sh 2026-07
```

---

> 狀態：🔲 骨架已建立，等 Owner 確認評分後執行完整打包
