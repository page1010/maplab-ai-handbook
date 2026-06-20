# Investment OS B1-B4 Recursive Self-Improvement

建立：2026-06-18
維護：B1 / B2 / B3 / B4
狀態：v0 baseline

## Purpose

RSI in this document means Recursive Self-Improvement. It is the B1-B4
maintenance loop that uses each run's evidence as the input for the next run.

The score is only an instrument panel. The real RSI mechanism is the cycle:

`B4 detects -> B2 verifies -> B1 repairs -> B3 preserves -> next run improves`

This is not a market indicator and has no relation to trading RSI.

## Growth Direction

B1-B4 should grow in this order:

1. From role labels to receipts.
2. From receipts to classified issues.
3. From classified issues to routed fixes.
4. From fixes to retest evidence.
5. From retest evidence to durable memory and stricter next-run checks.

The standard is simple: a future run should have fewer unresolved red items,
clearer ownership, better owner-facing output, or a documented reason why the
scope was intentionally paused.

## Recursive Loop

Each run follows one recursive loop:

1. Detect: read runtime truth sources such as nightwatch, background job state,
   shadow review findings, Telegram/Dashboard receipts, task cards, and review
   bundles.
2. Classify: B2 separates verified fact, reasonable inference, missing data,
   failure condition, and next step.
3. Route: assign each weakness to B1, B2, B3, or B4.
4. Act: build, review, archive, or patrol according to the assigned role.
5. Preserve: B3 stores the score, evidence, decision, and resume prompt.
6. Re-enter: the next run reads the prior output and must improve the loop or
   explain why it should pause/refactor.

No role may claim improvement from chat-only reasoning. Improvement requires a
file receipt, runtime state change, owner-visible readback, or an explicit
pause/refactor decision.

## Role Responsibilities

| Role | Recursive self-improvement responsibility | Evidence |
|------|-------------------------------------------|----------|
| B1 | Reduce confirmed failed checks by building or wiring the scoped fix. | `changed_files.md`, tests, runtime smoke, owner-visible proof |
| B2 | Convert raw model/shadow findings into verified review states. | `dataflow_review.md`, `error_report.md`, freshness matrix |
| B3 | Preserve the loop so the next agent can continue without chat memory. | `version_note.md`, `resume_prompt.md`, `pitfalls.md` writeback |
| B4 | Decide whether a loop should continue, pause, refactor, or archive. | `system_patrol_report.md`, fit check, stop/continue/refactor list |

## Score Inputs

The v0 scorer reads only file-backed evidence:

- `reports/nightwatch/latest.md`
- `reviews/background_jobs_state.json`
- `reports/shadow/local_model_findings.jsonl`
- MAPLAB review bundles for B1/B2/B3/B4 recency

The scorer does not read secrets, does not call broker APIs, and does not make
investment decisions.

## Score Bands

| Score | Meaning | Required action |
|-------|---------|-----------------|
| 85-100 | Healthy recursion | Keep current rhythm; archive proof. |
| 70-84 | Working but leaking | B2/B4 review the weakest evidence path. |
| 50-69 | Degraded recursion | B1 fixes only after B2/B4 classify the highest-impact red item. |
| 0-49 | Broken recursion | B4 recommends pause/refactor before more automation is added. |

## Local Model Boundary

Local models and Hermes can scout, summarize, classify, and produce shadow
review. They cannot close B2 review by themselves.

A local-model concern becomes useful only after B2 assigns one of these states:

- `accepted_issue`
- `false_positive`
- `needs_more_evidence`
- `handed_to_b1`
- `archived_by_b3`
- `patrol_decision_by_b4`

## Minimum Run Artifact

Every RSI run must leave:

- `b_role_recursive_self_improvement.json`
- `b_role_recursive_self_improvement.md`
- `builder_handoff.md`
- `review_request.md`

The next run compares against the latest prior JSON. If no prior JSON exists,
the run is a baseline and cannot claim improvement yet.

## Next Maturity Levels

1. v0: file-backed baseline scorer and manual B1 interpretation.
2. v1: scheduled daily Recursive Self-Improvement report from existing runtime
   evidence.
3. v2: Telegram first-screen summary for red items only.
4. v3: automatic B1/B2/B3/B4 handoff packet creation.
5. v4: owner reaction and fix outcome feed back into the next recursion.

