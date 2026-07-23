# Local Model Evolution — first-cycle run plan

Date: 2026-07-23 revalidation of the 2026-07-19 first cycle
Owner: MAPLAB Owner
Role: Local Model Evolution Orchestrator (A1 integration; B5/B2/B4 governance lenses)
Mode: reversible, file-only, no model-weight training, no production scheduler install

## What

Create the first trustworthy evolution loop for two narrow domains:

1. Investment report and current-state analysis.
2. SEO ranking, strategy, and keyword tracking.

The revalidated first cycle produces quota truth, 40 fixed de-identified eval cases, a real
`qwen2.5:14b` baseline, a smallest reversible candidate, regression evidence,
and a one-week MVP. It does not create or execute teacher jobs.

## So What

The local model cannot improve safely if account availability is confused with
remaining quota, historical data is confused with current truth, or a score is
allowed to move with the test set. A fixed eval and deterministic safety gate
make later prompt, skill, RAG, routing, or adapter decisions comparable.

## Now What

1. Run `python3 local_model_evolution/bin/quota_sentinel.py --dry-run` hourly in
   design only; do not install the schedule in this cycle.
2. Materialize 20 eval cases per curriculum.
3. Run baseline and candidate modes against the same Ollama model and cases.
4. Review the top three failure classes and regression delta.
5. Keep LoRA closed until baseline, rights, rollback, and fixed-eval gates pass.

## Loop Back

The next cycle should select only the highest-frequency verified failure,
change one capability layer, rerun the identical eval, and either promote to a
shadow run or roll back. New production outcomes must become new fixed cases.

## First-principles breaker

| Question | Answer |
|---|---|
| Desired owner-visible outcome | Reliable local current-state and SEO routines with no fabricated facts and fewer Owner corrections. |
| Current evidence | Local models and runtimes exist; fixed domain evals and trustworthy remaining-quota values did not. |
| Failed assumption | CLI login/availability does not expose or prove remaining subscription quota. |
| Smallest reversible fix | Fixed evals + metadata hard filter + strict JSON validator; no weight change. |
| Proof | Baseline/candidate reports on identical cases, zero safety regressions, and a validation receipt. |

## Self-prompting contract

- `intent`: produce evidence-grounded narrow-domain output without crossing action boundaries.
- `context_manifest`: case facts, entity id, `as_of`, source timestamp, source confidence, allowed action, rights label.
- `prompt_generation_rule`: build prompts only from fields that pass entity/date/sensitivity filters.
- `eval_gate`: fixed case id and rubric; safety-critical checks are mandatory, not averaged away.
- `repair_loop`: classify failure, change one layer, rerun all cases, compare delta, shadow or rollback.
- `tool_routing`: SQLite/read-only local truth for Investment OS; Drive/Sheets metadata and approved SEO sources for SEO; no live writes.
- `trace_log`: JSONL result per case with model, mode, parse state, checks, latency, and timestamps.
- `security_context`: no secrets, orders, publishing, Ads changes, customer replies, quotes, or unapproved training data.

## Automation stewardship contract

- `automation_steward`: A1 Local Model Evolution Orchestrator; B5 reviews dataset/eval quality.
- `user_visible_outcome`: fewer corrections in fixed reports and keyword tracking.
- `route_type`: deterministic scheduler design -> local eval -> human-reviewed promotion.
- `why_ai_or_why_not`: AI drafts narrow summaries; deterministic code enforces identity, freshness, schema, and action limits.
- `frame_invariants`: 15% reserve; unknown means no teacher jobs; same fixed eval for comparisons; no automatic promotion.
- `health_signal`: sentinel timestamp, parse rate, safety pass rate, curriculum score, regressions.
- `eval_gate`: all safety-critical cases pass and weighted score improves without hidden case changes.
- `care_loop`: hourly sentinel design, weekly dataset/eval regression review, monthly promote/rollback/retire review.
- `repair_entrypoint`: `local_model_evolution/bin/run_eval.py` and the relevant curriculum/rubric.
- `rollback_or_stop_condition`: safety regression, rights uncertainty, stale truth, unknown quota, or score decrease.
- `supervision_cost`: target <= 20 minutes/week after the one-week MVP.
- `human_touch_frequency`: weekly review; monthly promotion decision.
- `common_failure_mode`: fluent answers merge stale, wrong-entity, or unsupported data.
- `last_manual_repair`: 2026-07-23 removed gold-label leakage from candidate
  fact selection, status, missing-data, and action decisions.
- `time_to_detect`: one eval run or one hourly sentinel cycle.
- `time_to_recover`: one reversible prompt/filter rollback.
- `owner_burden_delta`: expected reduction after shadow proof; not yet claimed.

## Schedule design only

| Cadence | Action | Hard gate |
|---|---|---|
| Hourly at :17 | Quota Sentinel dry-run | Never call paid APIs without case-specific approval. |
| Daily 00:05 Asia/Taipei | Recalculate provider reset calendar | `unknown` remains unknown. |
| Reset in 12–36 hours | Create bounded teacher-job proposal | Verified/estimated remaining quota and >=15% reserve required. |
| Weekly Sunday 09:00 | Dataset QA + fixed eval + regression review | Rights and provenance required. |
| Monthly first Sunday | Promotion/rollback/retirement review | Owner or authorized reviewer decides promotion. |

## One-week MVP

- Day 1: freeze 40 cases, baseline `qwen2.5:14b`, classify failures.
- Day 2: apply metadata/schema candidate and rerun identical cases.
- Day 3: review false positives and add only approved hard negatives.
- Day 4: shadow-generate one de-identified investment and one SEO report.
- Day 5: B5 dataset/provenance QA; no training-set admission by default.
- Day 6: regression run and rollback drill.
- Day 7: Owner-facing promotion decision with no automatic runtime change.

## 2026-07-23 revalidation checkpoint

- The 2026-07-19 candidate consumed `expected` gold labels and its 320/320 score
  was withdrawn as invalid evidence.
- Eval schema 1.1 moves required metrics and action boundaries into the input
  policy contract; runtime candidate code does not read `expected`.
- A mutation regression test changes every gold field and proves candidate
  selection/output are unchanged.
- Revalidated baseline: 284/320; safety 206/240; top three failures are
  provenance 11, forbidden-fact exclusion 11, and missing-data honesty 8.
- Revalidated deterministic candidate: 320/320; 0 model inference calls.
- Promotion decision is unchanged: file-only wrapper shadow only; model no
  promotion; LoRA and teacher jobs closed.

## Approval gates

Owner approval is required before paid API access, teacher-job execution,
training-data admission with unclear rights, LoRA/adapter work, scheduler install,
production data writes, public publishing, customer replies, quotes, or model promotion.
