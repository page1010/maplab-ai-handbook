# T-A2-003: 每週全站 WP 內容稽核排程

---

## 接續狀態

> **Agent 冷啟動時第一個看的區塊。每次 checkpoint 必須更新。**

- **狀態**: 🟪 SUPERSEDED
- **最後活動**: 2026-09-01
- **接續點**: 舊 `wp-audit.sh` / `wp-audit-cron.sh` 只保留為歷史內容合規工具；新的 canonical 入口是 `.agents/skills/maplab-seo-coach-patrol/` 與 `T-A2-HERMES-SEO-COACH-001`。
- **阻塞**: 無；不得再要求 Owner 建立已被取代的排程。

---

## 狀態（舊）
SUPERSEDED — 舊腳本宣稱與實作不一致，不能再當全站 SEO 健康真相。

## 背景
T-A2-002 完成後，建立了 `scripts/wp-audit.sh` 和 `scripts/wp-audit-cron.sh`。
為確保未來 agent 不再重複寫入 `<script>` / 禁用詞，需要排程每週自動稽核。

## 排程意圖
```
taskId: wp-content-audit-weekly
description: 每週全站 WP 內容稽核（禁用詞/schema/style）
cronExpression: 0 9 * * 1  # 每週一上午 9 點（台北時間）
prompt: 執行 bash scripts/wp-audit-cron.sh，如果有違規就回報 Owner 並建立 handoff/feedback/{date}-wp-audit-report.md。
```

## 執行方式

不要再由本 Task Card 建立排程。公開技術基線改由無模型 sensor/probe 先判斷；只有 material delta、未完成驗收、fresh performance evidence 或 Owner 明確要求才喚醒 SEO 教練/Hermes。

## 腳本位置
- `scripts/wp-audit.sh` — 單篇或全站稽核
- `scripts/wp-audit-cron.sh` — 含日誌輸出，適合排程呼叫

## 稽核結果存放
`data/wp-audit-log/{YYYY-MM-DD}.md`

## 關聯
- `AGENT_RULES.md` Section 14
- `skills/wp-content-audit/SKILL.md`
- `skills/seo-session-checklist.md`（禁用詞唯一來源）
- `handoff/feedback/2026-04-07-wp-foodsafety-update-log.md`
