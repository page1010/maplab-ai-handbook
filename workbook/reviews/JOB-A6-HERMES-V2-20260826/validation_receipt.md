# JOB-A6-HERMES-V2-20260826 — Validation Receipt

- job_id: `JOB-A6-HERMES-V2-20260826`
- claimed_by: `Codex`
- actual_executor: `Codex local implementation + com.maplab.a6bot runtime`
- scope: `A6 Hermes capability truth, natural safe execution, group routing, photo receive, private persistence`
- final_state: `VERIFIED private Telegram execution / VERIFIED live photo roundtrip / VERIFIED group route unit / MISSING group live eye proof`
- completed_at: `2026-08-26T18:24:36+08:00`
- implementation_commit: `9639178` (`fix(A6): make Hermes execute and receive photos`)

## Owner need translated into acceptance gates

1. Owner can talk naturally in Telegram and Hermes executes a bounded task without asking Owner to run Terminal.
2. Hermes states its actual gateway/model/memory boundary from runtime, not an LLM guess.
3. Owner group messages can reach Hermes when the bot is mentioned or replied to.
4. Owner photos can be received, saved privately and tied to a receipt.
5. No arbitrary shell, secrets, publishing, schedule mutation or trading authority is added.

## Runtime evidence

- launchd label: `com.maplab.a6bot`
- program: `/Users/pagemacmini/maplab-ai-handbook/bot_a6/hermes_telegram_gateway.py`
- launchd readback after reload: `state=running`, `pid=3376`, `runs=1`, `umask=77`, `last exit=(never exited)`.
- bot identity readback: `@maplab_a6_bot`.
- provider chain written to `~/.local/share/maplab-a6-hermes/gateway_state.json`; last provider is null until the first v2 generative answer, so the deterministic capability answer correctly says no v2 success sample yet.
- legacy conversation quarantined at `~/.local/share/maplab-a6-hermes/quarantine/legacy-conversation-20260826-181225.json`.
- `conversation.json`, quarantine and gateway logs read back as mode `0600`.
- installed `~/.hermes/HERMES_TAKEOVER_RUNBOOK.md` mirrors the repo runbook byte-for-byte; `~/.hermes/SOUL.md` now names Hermes Agent v0.20.5, OpenRouter-first providers, local `gemma4:latest` fallback and the separate A6 governed surface.

## Telegram Web evidence

At 18:14, Owner UI sent:

`你的權限到哪裡？現在運行什麼模型、有沒有持久記憶、可以直接做哪些工作？`

Visible response began:

`【hermes】能力真相 v2（runtime readback）`

The visible response named the OpenRouter provider chain and local fallback, said the gateway is not zero-access, stated the fixed action list, described persisted 12-message history, and kept secrets out of model context.

At 18:14, Owner UI sent:

`現在動能名單狀態如何？請直接查，不要叫我跑終端機。`

Visible response returned:

- task: `A6H-20260826-181433-26d05c`
- status: `completed`
- action: `signal-status`
- launchd truth: `not running`, `runs=18`, `last_exit=1`
- latest report: `/Users/pagemacmini/investment-os/reports/limit_up_chip_story/limit_up_chip_story_2026-05-22.md`
- verdict: report is not a 2026-08-26 output and cannot be presented as today's list.

Matching file receipt:

`workbook/reviews/A6-HERMES-TASKS/A6H-20260826-181433-26d05c/receipt.json`

## Tests

- focused unittest: `14 tests`, PASS.
- `py_compile`: PASS.
- plist lint for both repo copies: PASS.
- `git diff --check`: rerun after receipt finalization.
- photo unit gate verifies largest Telegram photo selection, download, bytes/hash receipt and 0600 permissions.
- group routing unit gate verifies private acceptance and group mention/reply requirement.

## Photo and group proof boundary

- Photo code path: `VERIFIED` by unit test.
- Telegram Web live photo upload: `VERIFIED`. A browser-native non-sensitive 5,354-byte PNG sent at 18:24 produced visible bot reply and `tg-493-AQADrhBrG1TacVR-.receipt.json`.
- Local file evidence: image and receipt are both 0600; receipt bytes `5354`; SHA-256 `8f96cb8c1a6c6e856e5eed1543657010a9e11f0d0cd78ef350f30c8c7eb5e386`; `shasum` matches exactly.
- Group routing code path: `VERIFIED` by unit test.
- Existing Owner group live mention: `MISSING`; no group was mutated or bot-added merely for a synthetic check.

## Security result

- Telegram authorization now uses `message.from.id`, so Owner group chat IDs are no longer incorrectly rejected.
- Group messages require mention or reply to avoid bot spam.
- Telegram text never becomes shell text; executor stays fixed argv.
- gateway message logs store only character count and SHA-256 prefix, not Owner plaintext.
- photo/model boundary is explicit: v2 stores photos but does not claim pixel understanding.

## Next bounded action

Use an Owner-designated existing test group for one @mention roundtrip; do not create or alter a production group. Confirm `@maplab_a6_bot` is a member, send `@maplab_a6_bot 幫我查 Hermes runtime 狀態`, and match the group response task id to its local `A6H-*` receipt.

## Resume Prompt

我是 A6 Hermes v2 驗收者。先讀 CURRENT_STATUS.md、pitfalls.md、handoff/tasks/T-A6-003-hermes-governed-executor.md 與本 receipt。不要重做已通過的 capability、natural-action 或 photo roundtrip。只補一個 MISSING eye proof：在 Owner 指定的測試群由 Owner 帳號 @maplab_a6_bot 說「幫我查 Hermes runtime 狀態」，同群必須回 matching A6H receipt。不得另建群、傳客戶素材或測高風險操作。
