# Hermes training continuity and model-parity governance brief

- Date / window: 2026-08-27 21:45 +08:00; evidence checked through this audit
- Project: `/Users/pagemacmini/maplab-ai-handbook`
- Active Task Card: `handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`
- Audit role: A1 / Hermes training governance auditor
- Repository HEAD inspected: `175cf5518fe916d5a8a13620eda2fda36a9f50aa`
- Overall state: **RED** — the training loop is not rolling successfully, the current qualifying streak is `0/7`, and lower-model functional parity is not demonstrated.

## What

### Verified outcomes

- The de-named LINE corpus exists and its manifest agrees with the stored files: 20,256 pairs, with 15,993 train and 4,263 eval records.
- The new Hermes LINE loop has only two completed receipts, both from 2026-08-26:
  - `HERMES-LINE-20260826-231928`: 12 cases. Stored result `9/12 = 75%`, mean 79.6, with one unsupported `$18,000/$28,000` price insertion. Providers were Nemotron Ultra 550B for 8 cases and Super 120B for 4.
  - `HERMES-LINE-20260826-233219`: 2 repair cases, both `S2_DATA`. Stored result `2/2 = 100%`, mean 82.5, provider recorded only as `local-fallback`; the receipt does not preserve the actual local model ID.
- Re-evaluating both stored generations with the currently committed `score_reply()` gate changes the outcomes to `2/12 = 16.7%` and `1/2 = 50%`. Seven stored pass flags no longer satisfy the length gate, and one repair case no longer satisfies signal coverage. Because no receipt records a gate version, the stored scores are not comparable to the current gate. The trustworthy current qualifying streak is therefore `0/7`.
- The scheduled 2026-08-27 02:20 run failed before inference. Live `launchctl` reports `runs=1`, `last exit code=1`, `state=not running`; stderr records `PermissionError: Operation not permitted` while the LaunchAgent tried to read `train.jsonl` on MacExternal. There is no 2026-08-27 run receipt.
- The older A6 Gym is a separate system. It logged 47 rounds / 470 cases from 2026-07-01 through 2026-08-16, mean pass rate 17.66%, maximum 50%, and zero rounds at or above 85%. Its plist exists but is not loaded now. These rounds do not count toward the new LINE task's seven-run gate.
- Current Hermes gateway runtime is alive: `com.maplab.a6bot` is running with PID 6327, `runs=3`, `umask=77`. Its last recorded successful provider at 2026-08-27 10:23 was `nvidia/nemotron-3-ultra-550b-a55b:free` after earlier provider failures.
- Current focused tests passed: 14 Hermes capability/executor/gateway tests and 7 intake tests (`21/21`), plus the direct Telegram route script and prompt-guard script (`7/7` guard cases). They verify deterministic capability/status routing, fixed-argv safety, high-risk rejection, group addressing, private photo receipt handling, and deterministic intake parsing.

### Planned items that did not move

- No successful unattended daily run occurred on 2026-08-27.
- No weekly 30-case focused retraining job was found live.
- No full lower-model evaluation exists: the only `local-fallback` receipt has two cases, one stage, no actual model ID, no tool use, no multi-turn/restart test, and no live Telegram path.
- No seven-run streak counter, gate version, model ID, provider-specific score, or promotion decision is persisted in `loop_state.json`.
- The scorer does not implement all documented acceptance metrics. It currently approximates keyword coverage, question form, length, and unsupported money; it does not robustly score next-question correctness, known-field re-asking, maximum three questions, policy/availability hallucination, or semantic contradiction.
- `current_lessons.md` is overwritten each run rather than accumulated with regression provenance.
- Live Hermes v2 does not wire the old quote hot path into the current Telegram gateway. Quote intake currently has isolated synthetic tests, not live end-to-end proof.

### Decisions from this audit

- Do not treat either stored run as a qualifying current-gate pass and do not promote Hermes to customer automation.
- Do not count the legacy 47-round Gym toward the current LINE gate.
- Treat the Owner's stated minimum — lower-model conversation logic and system use must remain equivalent — as a required promotion gate. It is **not yet present** in the canonical Task Card and remains proposed until the task contract is updated.
- This audit was read-only apart from this report. No Telegram message, customer reply, schedule edit, model change, or external publish was performed.

## So What

- A configured schedule is not proof of continuous learning. The sole automatic attempt failed, so Hermes has not been rolling since the two manual runs.
- The displayed `loop_state.pass_rate = 1.0` is unsafe as a promotion signal because it is based on a two-case repair run and a superseded/unversioned gate. More runs under the same state contract would produce more misleading evidence.
- The model-independent shell is promising but limited: capability/status answers, recognized safe actions, authorization, group routing, and photo receipts are routed before the LLM, so those paths can remain stable across model changes. Ordinary conversation, multi-turn state use, business judgment, quote behavior, and response quality remain model-dependent and have not been proven equivalent.
- Offline and live provider policies differ. Training tries only the first two providers and then local fallback; live gateway tries the entire provider chain. Today's live success came from the third provider, which the training loop would not evaluate. Offline score therefore cannot currently represent the live provider path.
- The active work still supports the project direction — reducing Mina's repetitive drafting load — but it is not ready for shadow promotion or any claim that downgrade is lossless.

## Now What

Highest-value priority: make one truthful, repeatable, provider-labelled evaluation loop work unattended before adding more training volume.

| task | status | owner / evidence | acceptance proof |
|---|---|---|---|
| Restore unattended dataset access for the 02:20 LaunchAgent without broadening unsafe permissions | proposed | Hermes/A1; current TCC failure receipt | next scheduled run exits 0 and creates a timestamped run JSON without manual invocation |
| Version and align the gate, persist model/provider ID and consecutive streak, and stop using unversioned historical pass flags | proposed | A1/B1 review; current scorer and two run receipts | re-score receipt records `gate_version`, every metric, model ID, provider route, and truthful `streak`; regression tests cover prior false passes |
| Canonicalize one round size and stage sampling | proposed | A0 teaching owner | Task Card, plan, script, and LaunchAgent agree; a full round uses 12 stage-balanced cases, while five-case runs are labelled diagnostic and cannot advance streak |
| Add a lower-model parity gate | proposed | A0 + Hermes | each candidate provider/fallback runs the same frozen suite; deterministic route/action/safety/receipt results are 100%, business-state retention is 100%, unauthorized claims are 0%, semantic dialogue score is at least 90% and no more than 5 percentage points below the reference model |
| Run private shadow validation only after offline parity | proposed | Mina/A0 | 50 consecutive real shadow cases, direct-use or minor-edit rate at least 80%, with no automatic customer sends |

Next bounded action for the next working session: reproduce the LaunchAgent failure in its own execution context, choose a narrow dataset-access repair, then run exactly one 12-case stage-balanced, gate-versioned diagnostic receipt. Do not begin the seven-run streak until that receipt passes schema and evaluator regression checks.

Owner decisions to discuss:

1. Confirm that a five-case repair batch is diagnostic only and that a qualifying round is 12 stage-balanced cases.
2. Confirm the downgrade parity thresholds above as a hard promotion gate for every provider and local fallback, not just the currently selected model.
3. Confirm whether the legacy A6 Gym should be formally archived after its useful regression cases are migrated, to prevent future round-count confusion.

## Alignment Audit

| source | state | finding |
|---|---|---|
| `CURRENT_STATUS.md` Active Task | drift | It records Hermes v2 runtime work but does not expose `T-A6-HERMES-LINE-GYM-001` as the active canonical task; the governance auditor also resolved no active task pointer. |
| Active Task Card | dynamic | It correctly says `IN_PROGRESS` and defines seven consecutive runs at at least 85% with zero unsupported price, but it does not include the Owner's cross-model parity requirement. |
| Next Bounded Action | drift | The card still asks for the first five-case repair; a two-case repair already exists, while the actual next blocker is failed scheduling plus unversioned scoring. |
| Resume Prompt | drift | It asks for another repair batch but omits the launchd/TCC failure, gate-version mismatch, provider-policy mismatch, and parity gate. |
| Scheduler / automation | drift | Daily 02:20 is installed but failed its first automatic run; weekly 30-case automation is missing. Plan says daily 12 in some sections while the plist uses 5. |
| Actual assignee/runtime | dynamic | Hermes is named executor and the A6 gateway is running, but the training LaunchAgent is stopped after failure. |
| Training vs live provider routing | drift | Training tests two remote providers then local; live gateway tests the full chain. Provider-specific equivalence cannot be inferred. |

## Evidence

- `handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`
- `docs/hermes-line-reply-training-plan.md`
- `scripts/hermes_line_training_loop.py`
- `workbook/reviews/HERMES-LINE-TRAINING-20260826/validation_receipt.md`
- `state/hermes_line_training_stderr.log`
- `/Volumes/MacExternal/maplab-data/a6-hermes-training/runs/HERMES-LINE-20260826-231928.json`
- `/Volumes/MacExternal/maplab-data/a6-hermes-training/runs/HERMES-LINE-20260826-233219.json`
- `/Volumes/MacExternal/maplab-data/a6-hermes-training/loop_state.json`
- `bot_a6/hermes_telegram_gateway.py`
- `bot_a6/hermes_capability_runtime.py`
- `bot_a6/hermes_task_executor.py`
- `tests/test_hermes_capability_runtime.py`
- `tests/test_hermes_task_executor.py`
- `tests/test_hermes_telegram_gateway.py`
- `tests/test_a6_intake_flow.py`
