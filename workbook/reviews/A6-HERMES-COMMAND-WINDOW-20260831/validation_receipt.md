# A6 Hermes command window validation receipt

- Date: `2026-08-31 Asia/Taipei`
- Result: `VERIFIED_WITH_BOUNDARIES`
- Owner surface: Telegram [`@maplab_a6_bot`](https://t.me/maplab_a6_bot)
- Task: `handoff/tasks/T-A6-HERMES-DEERFLOW-001.md`

## Verified

- `com.maplab.a6bot` is loaded and `running`; live PID readback existed in this run.
- Gateway state recorded a successful OpenRouter conversational provider at `2026-08-31T12:25:16+0800`.
- Gateway log contains real private-photo receipts on `2026-08-26` and `2026-08-29`.
- Group activation is intentionally addressed-only: Owner must mention the bot or reply to it; focused tests cover mention, reply, and command normalization.
- DeerFlow embedded checkout is pinned to `788a890bd022689ef293e6bbfa2c12988173db6c`; local provider/config/extension isolation checks are current and green.
- Existing live DeerFlow artifact remains `DFR-20260827-221144-b2879c/research.md`.
- Full Hermes-discovery suite: `111/111 PASS`.
- Focused capability/gateway/DeerFlow/executor suite after the truth fix: `22/22 PASS`.

## Boundaries

- OpenRouter conversational replies are live; OpenRouter-backed DeerFlow is a separate route and remains blocked until account-policy readback and Owner spend approval both exist.
- Photo receipt means private download/storage succeeded. No pixel-understanding claim is made.
- A6 has no arbitrary shell, SSH, broker/order authority, secret readout, WordPress publishing, or direct Google Drive/Sheets/GitHub API connector.
- Public research output is evidence for a Lead to integrate; it is not a final investment conclusion or trade instruction.

## Capability truth fix

`/capabilities` previously said the gateway would fall back to local `gemma4:latest`, while the gateway had already disabled that fallback on 2026-08-30. The runtime snapshot now exposes `local_fallback_enabled=false` and tells the Owner that total upstream failure is reported explicitly. Default capability output now also lists `deerflow-status` and `deerflow-public-research`.

## Next bounded action

Use the existing Telegram chat as the single command window. Send an outcome in natural language; for group use, mention `@maplab_a6_bot`. Keep the first A6 assignment to public research or read-only status so its artifact and receipt can be reviewed before adding any new write-capable adapter.

## Resume Prompt

我是接手 A6 Hermes command-window verification 的 A1/A6 integration engineer，環境是 `/Users/pagemacmini/maplab-ai-handbook`。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A6-HERMES-DEERFLOW-001.md` 與本 receipt。Telegram `@maplab_a6_bot` 是單一 Owner 指令窗；不要另建聊天 UI。OpenRouter conversational chain 已有 live success，DeerFlow local public research ready；OpenRouter-backed DeerFlow 仍維持 policy/spend fail-closed。照片只宣稱已接收留 receipt，不宣稱理解像素。下一步只從一筆公開研究自然語句做 artifact/receipt 驗收，不碰 private Investment OS、broker、secrets、customer send 或 publishing。
