# Hermes Telegram 交辦範圍治理簡報

- 日期：2026-08-26 22:19 Asia/Taipei
- 專案：MAPLAB A6 Hermes v2
- Active Task Card：`handoff/tasks/T-A6-003-hermes-governed-executor.md`（CURRENT_STATUS 未提供機器可解析 Active Task pointer）
- Overall：AMBER

## What

### VERIFIED

- `com.maplab.a6bot` live `running`，pid `6327`。
- Owner 私聊可交辦；群組程式要求 @bot 或 reply bot，但既有 Owner 群尚缺 live eye proof。
- 自然語句與 `/do` 只會映射五個固定動作：`runtime-status`、`signal-status`、`repo-status`、`recent-commits`、`a6-self-test`。
- accepted/rejected 任務都會建立 file-backed task/receipt。
- Hermes 保存最近 12 則生成式對話 context；task receipt 長期保存。
- 系統知識來自 deterministic runtime contract、最多 9,000 字接手手冊、最近 12 則對話，以及五個固定 readback；沒有全 repo 任意搜尋能力。

### MISSING / DRIFT

- CURRENT_STATUS 沒有 audit script 可解析的 Active Task、Next Bounded Action、Resume Prompt；routing audit 因而回 `routing_aligned=false`。
- A6 gateway 沒有 Google Sheets、Drive、GitHub API 直連，也沒有任意 shell／SSH。
- OpenRouter 模型可協助推理與文字整理，但不能自行擴張 gateway 權限。

## So What

- Owner 可以在 Telegram 叫 Hermes「查目前狀態並留下收據」，不必再把每個只讀檢查搬回 Codex。
- Hermes 還不是通用執行 agent。超出五個 action 的請求只會聊天、拒絕，或需要建立新的治理 action；不得把自然語言理解能力誤認成任意系統操作能力。
- 對系統的理解是「A6/MAPLAB 路由與手冊級摘要 + 指定 live readback」，不是完整 repo、Drive、Investment OS 全貌。

## Now What

| task | status | owner/evidence | acceptance proof |
|---|---|---|---|
| Telegram 私聊查 A6 runtime／動能訊號／repo／commits／self-test | assigned/live | A6 Hermes gateway | Telegram 回覆 task id 與本機 receipt 同 id |
| Owner 群組真實 @mention roundtrip | proposed | 尚未指定群組 | 群組訊息與 receipt 同 id |
| 擴充更多安全工作 action | proposed | A0/A6 | 固定 argv、focused tests、Telegram roundtrip、receipt |

最高價值優先：先把常用、只讀、可驗證的工作逐項升格成固定 action，不開通通用 shell。

## Alignment Audit

- CURRENT_STATUS Active Task：missing
- Active Task Card：存在，但未被 CURRENT_STATUS 指向
- Next Bounded Action：missing
- Resume Prompt：task card 有，CURRENT_STATUS missing
- Scheduler/runtime routing：gateway live，但 audit 無 task pointer可比對，標 drift
- Actual assignee：A6 Hermes gateway live

## Resume Prompt

我是 A0/A6 接手者。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A6-003-hermes-governed-executor.md` 與本簡報。任何新增 Telegram 執行能力都必須新增固定 argv action、alias、拒絕規則、focused test、file-backed receipt 與 Telegram Web roundtrip；不得加入任意 shell、交易、發布、排程 mutation 或 secret 讀取。
