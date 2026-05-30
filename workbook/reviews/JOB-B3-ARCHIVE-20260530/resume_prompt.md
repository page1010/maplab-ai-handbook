# Resume Prompt

我是接手這份 B3 archive 的 agent。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`tasks/INVESTOS_RESEARCH_METHOD_UPGRADE_20260529.md`，再讀 `workbook/reviews/JOB-B3-ARCHIVE-20260530/*` 與 `reviews/JOB-INVESTOS-AUDIT-20260529/*`。

上次做到：已把 round-1 overbuild audit 的 runtime 事實、provisional `continue / pause / refactor` 分類，以及 B3 / B4 的角色邊界，整理成 durable archive。

下一步：

1. 如果你是 B4，先核對 `CURRENT_STATE_AUDIT.md`、`OPENCLAW_ROLE_BOUNDARY.md`、`OPENCLAW_TASK_PROPOSAL.md`，確認這些建議哪些要升格成 final patrol verdict。
2. 如果你是 Codex，直接接 `tasks/INVESTOS_RESEARCH_METHOD_UPGRADE_20260529.md` 的 active `web_cdp` backend / smoke loop，不要重跑 audit。

Blocker：

- 不要把 `openclaw_tasks/cron.yml` 當作真 scheduler。
- 不要把 B3 archive 當成 B4 patrol 的 final decision。
- schema migration 已在 local task card 記錄為 approved + applied，後續只管 smoke-gated expansion，不要重新把它當成 pending。

踩過的坑：

- B3 的職責是 archive 和 handoff，不是替 B4 做最終巡查裁決。
- `continue / pause / refactor` 必須保留為 provisional，直到巡查角色確認。
