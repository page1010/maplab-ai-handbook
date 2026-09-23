# Hermes LINE Training Governance Brief

- Date: 2026-08-31 13:13 Asia/Taipei
- Window: 2026-08-26 to 2026-08-31
- Project: MAPLAB A6/A7 Hermes LINE reply training
- Task Card: `handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`
- Overall: AMBER — implementation and supervision improved; training promotion is intentionally paused for human calibration.

## What

- Verified takeover: commits `86c1cf1`, `f89117d`, `a856100`, `22edc4a`, `4a6afb0`, and `ac9885c` successively added plateau stop-loss, frozen holdout design, supervisor-only scheduling, label-readiness fail-closed routing, and the source-bound rubric-v2 annotation guide.
- Verified executed history: 12 supervised rounds, 60 local calls, 10/60 pass, best round 40%, success streak 0. The poor result triggered method redesign instead of blind reruns.
- Verified evaluator redesign: seven operational criteria are frozen — answers current question, necessary next question, no re-asking known facts, grounded facts, grounded commercial claims, at most three questions, and mobile readability. Fourteen positive/negative fixtures cover the seven criteria.
- Verified schedule routing: canonical and installed plist SHA are both `32803c23...`; live LaunchAgent calls `hermes_line_training_supervisor.py` with the canonical durable job and private data root. The 2026-08-31 02:20 run reached the supervisor and returned `owner_review / canonical_state_gate`, with zero model/network/customer-send calls.
- Verified private truth: local owner-only training root contains 17 physical run receipts, 15 generated lesson deltas plus one 2026-08-30 Owner-feedback delta, frozen train/eval files, and the 20-case private annotation material.
- Missing: structured named-human rubric-v2 labels remain 0/20; scorer, paired runner, rendered prompt manifest, and immutable lesson snapshot are not pinned. No E1 experiment may run yet.

## So What

- The system has been taken over and materially optimized; it no longer equates lexical similarity with business quality and no longer lets the scheduler bypass the plateau guard.
- The current pause protects Owner time: additional model rounds before human calibration would spend calls while repeating unsupported price, unnecessary questions, and ungrounded assumptions.
- The 2026-08-30 Owner feedback is captured as a pending regression lesson: do not invent experience, ask rather than assert unknown venue facts, collect opening-event alcohol/photo/style needs, and do not lead with price.

## Now What

Highest-value priority: complete one named-human annotation pass over the frozen 20 cases.

| Task | Status | Owner / evidence | Acceptance proof |
|---|---|---|---|
| Annotate 20 cases with seven PASS/FAIL labels | assigned, waiting human | Owner or Mina; private packet + guide | 20/20 labels, reviewer attestation, three parent SHA bindings |
| Calibrate identity-blind scorer | gated | Codex after human labels | exact agreement at least 18/20; zero safety-dimension mismatch |
| Run E1 prompt-only experiment | gated | Hermes supervisor | baseline/candidate share model, cases, two-shots, seed, rubric, lesson snapshot; only prompt contract differs |
| Resume scheduled improvement | gated | LaunchAgent supervisor | seven independent promotion runs >=85%, unsupported commercial claims=0 |

Next bounded action: a named human reviews the 20 private cases; do not edit the blank preflight in place. After labels exist, generate a separate bound annotation artifact and run scorer calibration before any new model calls.

## Alignment Audit

- `CURRENT_STATUS.md` LINE latest state: aligned (`OWNER_REVIEW`, 0/20 labels).
- Active LINE Task Card: aligned.
- Next Bounded Action: aligned across Task Card, durable job, training plan, and job summary.
- Resume Prompt: aligned.
- Scheduler: dynamically aligned to canonical durable job; supervisor-only, raw loop inaccessible.
- Live runtime: aligned fail-closed; 2026-08-31 schedule fired and made zero model calls.
- Global repo Active Task parser: drift/missing because `CURRENT_STATUS.md` has no machine-readable global `Active Task`; this does not break the LINE lane because its task/job pointers are explicit.
