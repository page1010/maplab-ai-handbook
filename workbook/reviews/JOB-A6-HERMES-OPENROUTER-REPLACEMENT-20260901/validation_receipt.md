# Hermes OpenRouter output replacement receipt

- Checked at: `2026-09-01T13:13:01+0800`
- Scope: verify that the existing Hermes conversational output path can use OpenRouter instead of the former local Ollama fallback.
- Outcome: `PASS / OPENROUTER_OUTPUT_AVAILABLE / OLLAMA_FALLBACK_DISABLED / KEY_ROTATION_REQUIRED`
- Explicit non-goals: no human annotation, no model training, no Telegram send, no LINE customer send, no Google Sheets write, no private LINE/customer data egress.

## Runtime readback

- Pre-reload `com.maplab.a6bot`: PID `795`, started before the current source edit, so it was not accepted as live parity proof.
- Bounded reload: `launchctl kickstart -k gui/501/com.maplab.a6bot`; no message was sent.
- Post-reload `com.maplab.a6bot`: loaded and running; PID `45115`; runs `2`; no last exit code.
- Source mtime `2026-09-01 13:11:39 +0800`; new gateway start log `2026-09-01 13:12:37 +0800`, proving the daemon started after the no-Ollama source was installed.
- Configured chain: six `:free` OpenRouter models.
- Last previously recorded successful provider: `nvidia/nemotron-3-super-120b-a12b:free` at `2026-08-31T12:25:16+0800`.
- Runtime contract reports `local_fallback_enabled=false`.
- The gateway `answer()` iterates the OpenRouter chain and, when exhausted, returns failure without calling Ollama.

## Live synthetic transport smoke

The smoke replaced the normal system prompt with a synthetic-only prompt and sent no history, repo content, LINE content, customer data, credential value, or browser state. It called the existing Hermes `answer()` route and forbade any Ollama call.

- Status: `PASS`
- Transport: `openrouter_chat_completions`
- Configured chain free-only: `true`
- Provider attempts: `2`
- Attempt 1: `google/gemma-4-31b-it:free` — no accepted reply
- Attempt 2: `nvidia/nemotron-3-super-120b-a12b:free` — reply received
- Required marker present: `true`
- Reply length: `20`
- Reply SHA-256: `42be469741658e696ddfd65c04f4a017cc9f5067ca32aeecae13f30e4f7d80a5`
- Elapsed: `1281 ms`
- Ollama calls: `0`
- Telegram sends: `0`
- History messages sent: `0`
- Private data sent: `false`

## Deterministic verification

Command:

```text
python3 -m unittest -v tests.test_hermes_telegram_gateway tests.test_hermes_capability_runtime
```

Result: `12/12 PASS`.

The suite includes current-text and history DLP cases that assert OpenRouter is not called when the input contains customer/LINE/private indicators, plus an exhaustion regression that asserts the module has no `local_ollama_chat` fallback.

## Source pins

- `bot_a6/hermes_telegram_gateway.py`: `183b60ec750436901be08621bf597db5192d036c8f5e654b1924ea3b01471e9b`
- `bot_a6/hermes_capability_runtime.py`: `04ef5e6cca758f5ae4542fad85990c76f3fd946dd11df3ec360b6f43aef570b4`
- `tests/test_hermes_telegram_gateway.py`: `cb0bbfe0d3f7347ac32ece28b9d11a7f181ce80285d95d21b2eeb68ecb199933`
- `tests/test_hermes_capability_runtime.py`: `f53716b86978eb707ce350751f6046fbdaef1becd0a5f51c2cc7fa309748b3ee`

## Decision and boundary

OpenRouter is sufficient to replace the former Ollama generator for Hermes Owner-command-window and synthetic/public reply generation. The duplicate human-annotation and local-Ollama generation work is not a next action.

This receipt does not authorize raw LINE/customer payloads to be sent to OpenRouter and does not prove model quality superiority. Private LINE/customer workflows remain local/deterministic and customer sending remains disabled.

## Credential incident

During a parallel read-only provider audit, an over-broad local content search included a protected provider env file and displayed the full credential assignment inside the internal tool/model transcript. The subtask made no file writes, provider calls, shell network calls, or new credential copies, and the value is not reproduced in this receipt. Because the exact value entered transcript retention, the credential must be revoked/rotated before this route is treated as production-safe. Rotation was not performed because it is a separate credential-management action requiring Owner authorization.

## Next bounded action

Provider replacement code is complete. The only provider follow-up is Owner-authorized credential rotation followed by one synthetic-only smoke using the replacement key. Keep the OpenRouter-first, no-Ollama-fallback route and the private-data DLP tests. Continue only the separately authorized LINE-to-Sheets local contract; any live customer sender or new private third-party egress requires its own explicit authorization and readback receipt.

## Resume Prompt

I am the next Hermes runtime integrator. Read `CURRENT_STATUS.md`, `pitfalls.md`, `handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`, and this receipt first. Do not restart human annotation, local Ollama generation, or MLX training as the next action. The OpenRouter synthetic transport smoke already passed with a free-only chain, two attempts, one successful reply, zero Ollama calls, zero Telegram sends, and zero private-data egress. The existing credential needs Owner-authorized rotation because it appeared in an internal audit transcript; after rotation, run only one synthetic smoke. Preserve the DLP boundary: raw LINE/customer content stays local and customer sending stays disabled.
