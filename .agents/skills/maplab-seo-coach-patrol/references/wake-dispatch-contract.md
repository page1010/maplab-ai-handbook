# Meaningful wake and Hermes dispatch contract

## Wake decision

Record these fields before any work:

- `trigger`
- `newest_receipt_at`
- `evidence_age_days`
- `current_method_fingerprint`
- `previous_method_fingerprint`
- `verified_delta`
- `decision`: `NO_DELTA_NO_DISPATCH`, `DETAIL_ACTION`, `PLAN_ACTION`, or `OWNER_REVIEW`

A calendar event is only a chance to inspect; it is not itself a reason to manufacture work.

## Priority matrix

| Signal | Default route | Example acceptance |
|---|---|---|
| 4xx/5xx, noindex, broken canonical | detail action | exact URL returns 200/index/self-canonical after approved fix |
| new URL or metadata drift | detail review | before/after field diff and intent remains aligned |
| overlapping URLs/intent | plan action | one pillar/child map, no new slug, live/GSC gaps explicit |
| fresh query-page opportunity | single-variable experiment | fixed window and expected CTR/position delta |
| approved new case evidence | draft package | source manifest, no unsupported claims, visual QA pending |
| no verified delta | no-op | compact receipt, zero dispatch, zero new draft |

## Hermes packet

Required fields:

```yaml
task_id: T-A2-HERMES-SEO-COACH-001
executor: Hermes
checker: A0/A2 coach
objective: one sentence
next_bounded_action: one action
inputs: fixed public URLs or repo artifacts
hypothesis: falsifiable statement
changed_variable: exactly one
fixed_holdout: fixed URLs or query-page set
expected_delta: measurable expectation
stop_loss: when to stop
acceptance: exact checks
deny: external writes, secrets, customer sends, invented claims
outputs: exact paths
```

## Plateau rule

Compare the latest three receipts by adapter or worker, model, prompt or lesson version, sampling, evaluator, and acceptance contract. Two consecutive runs without verified improvement prohibit the same method. Third repetition requires answers to:

1. What is the real business objective?
2. What constraint currently prevents it?
3. Which assumptions remain unproven?
4. What is the smallest falsifiable experiment?
5. What exact condition stops the work?
