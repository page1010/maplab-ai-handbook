# T-A2-003: 每週全站 WP 內容稽核排程

## 狀態
PENDING — 待 Owner 用 schedule skill 建立實際排程

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
Owner 在 Claude Code terminal 執行：
```
/schedule
```
按照上方 taskId / description / cronExpression / prompt 建立排程。

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
