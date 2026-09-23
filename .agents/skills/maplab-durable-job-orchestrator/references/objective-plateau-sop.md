# Objective-level plateau circuit breaker

Use this SOP when a durable job keeps producing technically valid artifacts but
the Owner-facing acceptance, business KPI, or promised deliverable does not
move. It prevents version churn and infrastructure work from being counted as
goal progress.

## Separate three kinds of delta

Every bounded-action receipt distinguishes:

1. `method_delta`: adapter, model, prompt/lesson, sampling, evaluator, or code
   changed.
2. `supporting_delta`: a test, synthetic fixture, inventory, security gate, or
   internal component improved.
3. `objective_delta`: an Owner-facing acceptance item changed from unmet to
   met, the primary business metric improved, or the action unlocked the next
   real-world step with evidence.

A new fingerprint proves only method novelty. Tests passing prove only the
declared test scope. Neither implies `objective_delta > 0`.

## Trigger

Run the circuit breaker before another action when any condition holds:

- two consecutive receipts have zero `objective_delta`;
- three consecutive actions stay inside supporting infrastructure;
- the Owner asks why the method is being used or says the work is wasting
  quota;
- versions or rounds increase while the same acceptance items remain open;
- the proposed action cannot name the concrete Owner-facing step it unlocks.

## First-principles five questions

Write evidence-backed answers into the receipt:

1. What is the true Owner outcome?
2. What currently prevents that outcome?
3. Which assumptions about the proposed method remain unproved?
4. What is the smallest falsifiable experiment against the real constraint?
5. What exact result stops this branch?

## Routing decision

Use this order:

1. Re-route to the smallest real-objective experiment.
2. If supporting work is useful but not blocking, defer it or split it into a
   separate job with its own acceptance and priority.
3. Continue supporting work only when a current blocker chain is proven:
   `supporting action -> verified gate -> named immediately executable
   Owner-facing next action`, and evidence shows every other prerequisite is
   already satisfied.
4. For an urgent safety issue, preserve the evidence and notify the Owner, but
   do not silently replace the authorized business task with an open-ended
   security program.

The review/re-route itself does not consume a domain attempt or paid model call.
Record `attempt_consumed=false`; it still appends history and a verified
artifact. This exemption is single-use for that plateau. The next executed
domain experiment consumes one attempt; only a pure poll/readback of an
already-running external action is exempt. Repeating review/re-route without
new evidence is invalid.

If supporting work is split into a separate job, record its lower priority,
attempt/spend cap, parent objective, and non-displacement rule. It cannot jump
ahead of the main business job unless a verified urgent safety issue or an
explicit Owner priority change requires it.

## Required receipt fields

- `method_version`, `method_fingerprint`, and last three fingerprints
- `objective_metrics_before` and `objective_metrics_after`
- `owner_acceptance_delta`
- `supporting_delta`
- `business_artifact_created`
- `unlocked_next_action`
- `attempt_consumed`
- answers to the five questions
- `decision`: continue, re-route, defer/split, owner review, or stop
- a fixed next bounded action and stop condition

If `owner_acceptance_delta=0`, the receipt must not use words such as
"progress", "validated", or "complete" without naming the supporting-only
scope.
