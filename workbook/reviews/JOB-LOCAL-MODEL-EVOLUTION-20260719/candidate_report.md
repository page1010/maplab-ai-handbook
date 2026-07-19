# Candidate v0.1 report — metadata filter + deterministic renderer

## What

Candidate v0.1 ran the identical 40 frozen cases. It filtered wrong entity,
future/unknown dates, unapproved facts, and case-forbidden facts before rendering
the structured report contract.

| Metric | Result |
|---|---:|
| Total | 320 / 320 (`100%`) |
| Safety checks | 240 / 240 (`100%`) |
| Investment curriculum | 160 / 160 (`100%`) |
| SEO curriculum | 160 / 160 (`100%`) |
| Deterministic renderer cases | 40 |
| Model inference calls | 0 |
| Regressions versus baseline | 0 |

## So What

This proves the fixed report contract can be made safe and cheap without weight
training. It does **not** prove `qwen2.5:14b` became G2/G3, because candidate
control fields and factual summaries were rendered deterministically.

## Now What

- Promotion decision: allow a de-identified file-only shadow of the wrapper.
- Model promotion decision: reject; keep `qwen2.5:14b` at the current tier.
- LoRA decision: reject for this cycle.
- Next eval should add a separate semantic-quality rubric for wording and
  prioritization while keeping all current safety checks immutable.

## Loop Back

If shadow review finds useful semantic tasks that deterministic rendering cannot
handle, let the local model draft only that non-control field, validate it, and
rerun all safety and semantic cases. Roll back on any safety regression.
