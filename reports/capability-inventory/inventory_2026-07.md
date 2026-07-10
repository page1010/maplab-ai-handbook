# B5 能力盤點蒸餾評分 — 2026-07

> 執行者：B5（首次執行，由 A1 代理）
> 執行時間：2026-07-11
> 觸發源：Owner 核准 B5 角色後首次蒸餾
> 下次評分：2026-08-01（每月）

---

## 蒸餾評分標準

| 分數 | 說明 |
|------|------|
| 5 | 可直接打包進地端教材包（清晰、具體、有範例、無 MCP/API 依賴） |
| 4 | 小幅改寫後可給地端（去除 API 依賴，保留核心邏輯） |
| 3 | 需要較多改寫才能給地端理解 |
| 2 | 僅適合有工具存取的雲端模型，改寫成本高 |
| 1 | 僅適合雲端高智能模型（重度依賴即時 MCP / 外部 API） |

---

## pitfalls.md 蒸餾評分（52 條）

### Top 10 可直接打包（評分 ≥ 4）

| 編號 | 條目 | 評分 | 理由 |
|------|------|------|------|
| P-01 | 2026-06-20 — Unattended long-running tasks | 5 | 通用行為規則，無 API 依賴，有具體原則 + 解法 |
| P-02 | 2026-06-18 — Test receipt must be written before claiming completion | 5 | 通用驗收原則，有反例，易懂 |
| P-03 | 2026-06-17 — A5 quote answers must come from a quote Sheet, not chat math | 5 | 具體流程規則，有正確做法 vs 錯誤做法對照 |
| P-04 | 2026-06-17 — Telegram `召喚` must create a dispatch receipt | 5 | 具體 receipt 要求，可複製行為 |
| P-05 | 2026-06-18 — Quote trainee agents must not self-certify PASS | 4 | 有具體 gate 要求，稍依賴 MAPLAB 品項知識 |
| P-06 | 2026-06-20 — A5 quote trainees need fixed customer templates | 4 | 有具體模板要求，稍依賴 MAPLAB 報價知識 |
| P-07 | 2026-06-18 — A6 quote mode must be Sheet-first, and Apps Script Web Apps need redeploy | 4 | 有具體三段驗收要求，GAS 知識稍有依賴 |
| P-08 | 2026-05-30 — B3 archive is not the same thing as the B4 patrol verdict | 5 | 角色分工原則，通用，無工具依賴 |
| P-09 | 2026-05-29 — Repo extension update is not live Chrome proof | 5 | 驗收原則，通用，有具體區別 |
| P-10 | 2026-06-11 — Session 留下的每分鐘 babysitting cron 變成殭屍，癱瘓 Hermes 半天 | 4 | cron 清理原則，稍依賴 Hermes/launchd 知識 |

### 需改寫後可用（評分 3）

- 2026-06-20 — IOS-KOL changed RSS rows must be cross-checked（IS 特定）
- 2026-06-17 — IOS-KOL Telegram digest must carry transcript gate（IS 特定）
- 2026-06-17 — A8 local fallback JSON is not a video（A8 pipeline 特定）
- 2026-06-17 — Extension summon is a file-backed role handoff（Extension 特定）
- 2026-05-24 — Planned B2B slugs are not live WordPress URLs（WP 特定）

### 不建議打包（評分 1-2，重度 API/系統依賴）

- 2026-06-20 — IOS-KOL RSS cross-check scoped query（Shioaji/DB 特定）
- 早期 GAS/Sheets 相關踩坑（重度 GAS 環境依賴）

---

## skills/ 技能書蒸餾評分

### Top 10 可直接打包（評分 ≥ 4）

| 技能書 | 評分 | 理由 |
|--------|------|------|
| skills/task-progress-guide.md | 5 | 通用進度回報格式，無工具依賴 |
| skills/brand-voice-guide.md | 5 | MAPLAB 品牌語氣，有具體禁用語/允許語對照，無 API |
| skills/first-principles-check/SKILL.md | 5 | 通用決策框架，無工具依賴 |
| docs/fable-mindset.md | 5 | 通用工作思維，10 條有範例，無 API |
| skills/a6-rapid-quote-sop.md | 4 | 報價 SOP，稍依賴 GAS/Sheets 環境 |
| skills/a6-safety-boundaries.md | 5 | 安全邊界規則，通用，無 API 依賴 |
| skills/a6-qa-examples.md | 4 | QA 範例集，依賴 MAPLAB 品項知識 |
| skills/a7-customer-service-skills.md | 4 | 客服框架，稍依賴品牌知識 |
| skills/session-handoff.md | 5 | Session 交接通用格式，無工具依賴 |
| skills/colab-resilience-guide.md | 4 | Colab 恢復流程，稍依賴 Colab 環境 |

---

## workbook/reviews/ JOB 輸出蒸餾評分

### 2026-07-10 JOB 輸出（A0 委派四件）

| JOB | 說明 | 評分 | 蒸餾建議 |
|-----|------|------|---------|
| JOB-CODEX-WEDDING-PILLAR-20260710 | 婚禮 Pillar 文章草稿 | 3 | SEO 框架可提取，品項細節去除後通用 |
| JOB-CODEX-B3-ADCOPY-20260710 | 廣告文案 | 4 | 品牌語氣示範，去除品項名後可打包 |
| JOB-CODEX-CONTENT-AUDIT-20260710 | 內容稽核 | 4 | 內容稽核框架通用，可進教材 |
| JOB-AGY-SECOND-READ-20260710 | Antigravity 第二輪閱讀 | 3 | 多模型共識框架有價值，但格式稍複雜 |

### 歷史 JOB 高分項

| JOB | 評分 | 理由 |
|-----|------|------|
| JOB-A1-ALT-TEXT-STANDARD-20260630 | 5 | 圖片 alt text 標準，通用無 API |
| JOB-A2-SEO-TRIO-REVIEW-20260707 | 4 | SEO 三人組框架，稍依賴 GSC |
| JOB-A0-ECOSYSTEM-LEARNING-LOOP-20260615 | 4 | Learning loop 架構，可適配到其他系統 |

---

## skills/auto/ 評分（A5-QUOTE 系列）

`skills/auto/A5-QUOTE-*`（29 個）：均為 A5 報價系統 QA 自動輸出。
- 評分：3（具體但高度依賴 MAPLAB 報價系統）
- 蒸餾建議：提取「報價 gate 邏輯」部分（payload shape + exactness 驗證）→ 評分升至 4
- 建議打包：只取 `A5-QUOTE-20260609-*` 系列最新版，舊版（20260518）已被覆蓋

---

## 教材包候選清單（評分 ≥ 4，建議優先打包）

### 立即可打包（評分 5，無需改寫）

1. `pitfalls.md` P-01/02/03/04/08/09 條（6 條，通用行為規則）
2. `skills/task-progress-guide.md`（進度回報格式）
3. `skills/brand-voice-guide.md`（品牌語氣）
4. `skills/first-principles-check/SKILL.md`（決策框架）
5. `docs/fable-mindset.md`（工作思維 10 條）
6. `skills/a6-safety-boundaries.md`（安全邊界）
7. `skills/session-handoff.md`（Session 交接格式）
8. `workbook/reviews/JOB-A1-ALT-TEXT-STANDARD-20260630`（圖片標準）

### 小幅改寫後可打包（評分 4）

9. `skills/a6-rapid-quote-sop.md`（報價 SOP → 去 GAS 細節）
10. `skills/a6-qa-examples.md`（QA 範例 → 去 MAPLAB 特定品項）
11. `skills/colab-resilience-guide.md`（Colab 恢復）
12. `pitfalls.md` P-05/06/07/10（4 條 → 去 MAPLAB 特定部分）
13. `workbook/reviews/JOB-CODEX-B3-ADCOPY-20260710`（廣告文案示範）
14. `workbook/reviews/JOB-CODEX-CONTENT-AUDIT-20260710`（稽核框架）

---

## 地端模型適配說明

目前地端模型（Ollama Qwen2.5:14b、gemma4）：
- **可直接繼承**：行為規則類（pitfalls P-01~04, 08~09）、格式規範類（task-progress, session-handoff, brand-voice）、思維框架類（fable-mindset, first-principles）
- **需微調繼承**：報價 SOP 類（去除 GAS/Sheets API 呼叫細節，保留流程邏輯）
- **雲端保留**：MCP 工具呼叫、GAS clasp push/deploy、OAuth 流程（需即時 API 存取）

---

> 下次執行：2026-08-01，掃描 7 月新增 pitfalls + skills/auto + JOB 輸出
