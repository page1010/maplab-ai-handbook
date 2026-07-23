# Baseline and first-improvement report — 2026-07-23

Eval cycle: `2026-07-23-first-cycle-revalidated`
Model: `qwen2.5:14b`
Cases: 40 synthetic/de-identified cases, 20 per P0 curriculum

## Why the 2026-07-19 candidate was superseded

The prior candidate filter and renderer read `case["expected"]` to select
allowed facts, set status, decide whether missing data was required, and set the
action decision. That leaked gold labels into the system under test, so its
320/320 score was tautological and could not support promotion.

The fixed candidate now:

1. selects facts only from input metadata: entity, `as_of`, freshness, usage
   rights, sensitivity, fact kind, approval, and confidence;
2. derives readiness from input `required_metrics`;
3. derives the action boundary from the input policy contract; and
4. leaves `expected` labels exclusively to the scorer.

A regression test mutates every gold field and proves candidate selection and
rendered output remain identical.

## Revalidated results

| Run | Checks | Score | Safety | Inference engine |
|---|---:|---:|---:|---|
| Baseline | 284/320 | 88.75% | 206/240 (85.83%) | Ollama `qwen2.5:14b` |
| Candidate | 320/320 | 100% | 240/240 (100%) | metadata gate + deterministic renderer |
| Delta | +36 | +11.25 pp | +34 checks / +14.17 pp | no candidate model inference |

Curriculum baseline:

- Investment current state: 146/160 (91.25%).
- SEO ranking/keyword: 138/160 (86.25%).

## Top three baseline errors

1. `fact_provenance`: 11 failures.
2. `forbidden_fact_exclusion`: 11 failures.
3. `missing_data_honesty`: 8 failures.

Other recorded failures: subject identity 2, parse/schema/as-of/action boundary
1 each. `SEO-019` timed out and correctly remained a failed case.

## Promotion decision

- Deterministic wrapper: eligible only for de-identified, file-only shadow.
- Local model: no tier promotion.
- LoRA/adapter: blocked.
- Production scheduler, external writes, customer replies, quotes, and live
  orders: not enabled.
