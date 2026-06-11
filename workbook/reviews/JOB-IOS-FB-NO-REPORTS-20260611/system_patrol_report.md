# IOS-FB No-Report Patrol

Date: 2026-06-11 13:31 Asia/Taipei
Role: IOS-FB FB Social Intelligence Manager / Codex runtime
Question: Owner asked whether agents know to use Notion for social-account credentials, and why recent FB/social reports have not arrived.

## Verdict

1. Startup flow did not previously encode the Notion credential route for social accounts. That was a governance gap.
2. The recent no-report symptom is not because `fb-shadow-refresh` never runs. It has run daily, but it only rebuilds the old historical shadow-review sample.
3. No current evidence shows a durable daily production FB logged-in collector or reviewed Telegram report sender running after the 2026-05-26 production checkpoints.
4. The current quality/training gate still blocks SQLite write, price proof, and reviewed Telegram digest.

## Background Task Evidence

Execution path inspected:

- LaunchAgent: `/Users/pagemacmini/Library/LaunchAgents/com.investmentos.fb-shadow-refresh.plist`
- Runtime working directory: `/Users/pagemacmini/.local/share/investmentos-telegram-operator`
- Runtime script: `/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/fb_shadow_refresh.sh`
- Log: `/Users/pagemacmini/.claude/logs/fb-shadow-refresh.log`

Current `launchctl print` shows the loaded job as not running, scheduled daily at 03:00, with arguments:

```text
/bin/bash
/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/fb_shadow_refresh.sh
```

Log proof: 2026-06-03 through 2026-06-11 each show `fb-shadow-refresh start` and `fb-shadow-refresh done` around 03:00. Every run reports the same historical outputs:

```text
draft_tasks: 354
row_judgements: 776
candidates: 354
output path: fb_kol_intel/historical_corpus/local_judgement/2026-03-25_to_2026-04-25/
shadow_sample_report: reviews/FB-RADAR-QUALITY-GATE-SHADOW-REVIEW-20260525/shadow_sample_report.md
row_sample_count: 60
task_sample_count: 30
```

There is one older 2026-06-02 `Operation not permitted` line for the repo script path, followed by successful runtime-copy runs. That is a launchd/runtime-copy hygiene note, not the primary no-report root cause.

## What The Scheduled Job Actually Does

`scripts/fb_shadow_refresh.sh` only calls:

1. `scripts/aggregate_fb_local_judgement.py`
2. `scripts/build_fb_shadow_review_sample.py`

It does not collect fresh FB posts, does not run logged-in social source routing, does not write reviewed Telegram output, and does not promote candidates.

`aggregate_fb_local_judgement.py` defaults to:

```text
fb_kol_intel/historical_corpus/local_judgement/2026-03-25_to_2026-04-25
```

Its default mode is file-only; `--write-db` is optional and is not used by the launchd job.

`build_fb_shadow_review_sample.py` also defaults to the 2026-03-25 to 2026-04-25 historical corpus and writes the same review directory:

```text
reviews/FB-RADAR-QUALITY-GATE-SHADOW-REVIEW-20260525
```

## Gate Evidence

`shadow_sample_report.md` says the sample is for blind quality review only and must not be written to SQLite or used for price proof until the quality gate explicitly passes.

`training_gate_report_20260607.md` says the current artifacts still fail promotion and remain blocked from SQLite, price proof, and reviewed Telegram digest.

Hard gaps from that gate:

- Codex/local disagreements: 32
- Local useful rows with empty `missing_data`: 45
- Useful rows without local ticker mapping: 42
- Single-source task candidates: 30

Local model gate:

- Model: `qwen2.5-coder:7b`
- OK: `false`
- Duration: 180.03 seconds
- Error: `timed out`
- Verdict: `FAIL_LOCAL_MODEL_TRAINING_RESPONSE`
- Covered scenarios: `0/20`

## Production Collector Evidence

The production logged-in collection task card defines the intended daily/near-24h route:

```text
OpenClaw/Chrome logged-in FB page collection
-> raw posts enter SQLite
-> same-date high-grade review
-> research task cards
-> evidence and manual review gates
```

The last visible production checkpoints in the task card are 2026-05-26:

- 17:18: 12 rows from 3 normalized seed sources; only 1 logged-in FB visible post and 11 public fallback rows.
- 17:43: high-grade row review passed for the 12-row file-only input.
- 18:10: evidence collection passed with manual-review gaps; no candidate promotable.
- 18:40: 3 manual-review records created; all block SQLite and price proof.
- 19:09 note: bottleneck is source quality / route balance, not an active runner failure.

The 2026-06-01 follow-up card added the daily 03:00 shadow refresh, but explicitly notes re-judgement still needs Codex/manual trigger. That job was not a production collector.

## Root Cause

Primary root cause:

- IOS-FB had no startup credential bootstrap for social accounts, so agents were not forced to check Owner Chrome / A0 / Notion credential routes before running FB/social work.

Operational root cause:

- The daily launchd job is a historical shadow-review refresher, not a fresh production report pipeline.

Quality gate root cause:

- The current training/promotion gate fails, so reviewed Telegram digest and DB/price-proof promotion remain blocked.

Visibility root cause:

- The system can log a healthy daily `done` while producing the same stale review sample. That looks alive at the process layer but is stale at the Owner report layer.

## Changes Made In MAPLAB Startup Flow

- Added `AGENT_STARTUP_PROTOCOL.md Step 5.5` for external-login and social-account credential bootstrap.
- Added `skills/credentials/social-accounts.md`.
- Updated `AGENT_RULES.md` to clarify the Notion credential exception: Notion is not state truth, but may be an Owner/A0/A1-approved credential vault / index.
- Updated `skills/credentials/notion-api.md` to forbid token/password paste into repo, prompts, logs, memory, or review bundles.
- Updated IOS-FB role module so it lists `social-accounts`, `notion-api`, and `meta-ads-api` as restricted A1-only credential references.

## Next Repair Path

1. Run IOS-FB production preflight: check Owner Chrome logged-in FB route or A0/Notion credential handoff without printing secrets.
2. If missing, write `source_route_health.md` with `auth_missing` and Owner 5-minute action; do not run old historical sample as today's report.
3. If available, run a bounded fresh collection for active sources, then high-grade review and manual-review gate.
4. Only send reviewed Telegram digest after the quality gate passes, or send a clearly labeled `auth_missing` / `gate_failed` status report instead.

## Warnings

- Do not read or print social-account passwords, tokens, cookies, OTP, or backup codes.
- Do not treat Notion as task state or progress truth.
- Do not promote historical shadow samples into current production reports.
- Do not silently downgrade from logged-in FB collection to old corpus output.
