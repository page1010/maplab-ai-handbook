---
name: maplab-seo-coach-patrol
description: Coach and run evidence-based MAPLAB public-site SEO patrols, decide whether a wakeup should no-op, produce a focused fix or a plan, and dispatch one bounded public-safe task to Hermes. Use for MAPLAB SEO status checks, WordPress patrols, meaningful wakeups, content-cannibalization review, or Hermes SEO assignments. Do not use to publish WordPress, change Ads or Rank Math, read secrets, or send customer messages without explicit authorization.
---

# MAPLAB SEO Coach Patrol

Turn a scheduled wakeup into a verified decision, not activity for its own sake.

## Cold start

1. Read `CURRENT_STATUS.md`, `pitfalls.md`, and the active Task Card before doing work.
2. Read the newest prior receipt under `workbook/reviews/JOB-A2-SEO-COACH-*` when one exists.
3. Read `references/source-contract.md` and `references/wake-dispatch-contract.md` in this skill.
4. Announce the role, environment, exact task, and safety boundary.
5. Keep private customer material, LINE conversations, browser login state, cookies, and secrets local. Do not pass them to public research providers or model gateways.

## Decide whether this wakeup is meaningful

Treat the wakeup as actionable when at least one condition is true:

- The Owner explicitly requested a check or a prior acceptance deadline is due.
- The newest complete public baseline is older than seven days; this wakes only the deterministic public sensor. A model/Hermes action still requires a material delta or an unfinished acceptance item.
- The sitemap URL set, sitemap `lastmod`, published-post count, or a monitored page fingerprint changed.
- A monitored URL now returns a redirect/error, becomes `noindex`, loses its self-canonical, title, description, single H1, schema, or image-alt coverage.
- A new verified case or approved public asset creates a specific content opportunity.
- Fresh GSC/analytics evidence is locally available and a comparison window is due.
- The prior task has a measurable failure or an unverified acceptance item.

If none is true, write a compact `NO_DELTA_NO_DISPATCH` receipt. A stale baseline with a fresh sensor result and no material delta takes the same no-dispatch route. Do not create a new draft, increment a round merely for freshness, dispatch Hermes, or notify the Owner.

## Establish the public baseline

Run the bundled probe with a fixed URL set. It performs public HTTP/WordPress reads only and writes JSON to stdout:

```bash
python3 .agents/skills/maplab-seo-coach-patrol/scripts/public_seo_probe.py \
  --site https://www.maplabkitchen.com/ \
  --url https://www.maplabkitchen.com/ \
  --url https://www.maplabkitchen.com/corporate-catering-tainan/ \
  --url https://www.maplabkitchen.com/tainan-catering-guide/ \
  --url https://www.maplabkitchen.com/icc-tainan-catering/ \
  --url https://www.maplabkitchen.com/corporate-tea-party-desserts/
```

Save the exact stdout as `public_seo_baseline.json` only inside the dated review bundle. Compare it with the newest prior baseline before proposing work.

When a conclusion depends on the whole post/page corpus (for example, "all 64 URLs are 200" or "this URL has zero sitemap-corpus inbound links"), run the bundled all-corpus sensor and save its exact stdout as `public_seo_corpus_audit.json`:

```bash
python3 .agents/skills/maplab-seo-coach-patrol/scripts/public_seo_corpus_audit.py
```

Do not promote a sampled-page observation into a whole-corpus claim. If a same-method comparison is used as a dispatch gate, also save a compact replayable `public_seo_no_delta_receipt.json` that binds the baseline path/hash, both method fingerprints, comparison decision, and external-effect counters.

Use these evidence labels in every report:

- `VERIFIED`: observed in this run from a live source or exact local readback.
- `INFERENCE`: a bounded interpretation of verified facts.
- `MISSING`: required evidence was unavailable; do not fill it from memory.
- `PROPOSED`: an external or creative change that has not been executed.

## Choose detail work or planning

Use the smallest branch that can change an acceptance metric:

1. **Technical breakage or indexability drift** — prepare one URL-specific repair proposal with before/after checks. A safe repo-only fix may be made when it does not change the live site.
2. **Cannibalization or intent overlap** — write a keyword/URL consolidation plan. Do not generate another generic article first.
3. **Fresh case evidence** — prepare one evidence-backed case brief or draft package. Keep prices, availability, customer names, and performance claims `MISSING` unless current authority exists.
4. **Ranking/CTR opportunity with fresh GSC data** — choose one query-page pair and one changed variable; define the fixed comparison window and stop-loss.
5. **No objective delta** — no-op. Do not use a new version number as proof of progress.

Never treat Rank Math score alone as ranking proof. Never reuse old GSC numbers as current state.

## Dispatch exactly one bounded task to Hermes

Hermes receives work only after a Task Card exists. The card must include:

- one objective and one `next_bounded_action`;
- fixed public-safe inputs and their hashes or URLs;
- the relevant prior baseline;
- one changed variable, fixed acceptance checks, expected delta, and stop-loss;
- explicit deny list: no WordPress publish/edit, no Ads/Meta/Rank Math changes, no credentials, no customer/LINE sends, no invented prices or claims;
- output paths and checker role.

Hermes may run the public probe, classify exact findings, draft a consolidation plan, or prepare a proposal. Hermes must not select a material business or creative direction on its own. The coach verifies the artifact before updating status.

Do not dispatch when the input fingerprint and acceptance state are unchanged. Two consecutive runs with no verified improvement trigger a plateau review; switch to failure bucketing, sample-level errors, an explicit method hypothesis, and a single-variable experiment. A third repetition requires the five first-principles questions before any new run.

## Receipt and state update

Write to `workbook/reviews/JOB-A2-SEO-COACH-YYYYMMDD/`:

- `public_seo_baseline.json`
- `public_seo_corpus_audit.json` when a whole-corpus claim is used
- `public_seo_no_delta_receipt.json` when a same-method comparison gates dispatch
- `seo_priority_matrix.md`
- `hermes_assignment.md` when dispatch occurs
- `validation_receipt.md`

Verify artifacts by reading them back. Then atomically update the Task Card, `CURRENT_STATUS.md` Active Task, Next Bounded Action, and Resume Prompt. Stage only task-related files.

## Approval boundary

Stop at `OWNER_REVIEW` for live WordPress writes or publishing, Ads/Meta budget/audience/switch changes, Rank Math settings, new third-party private-data egress, irreversible operations, new spend, or material creative/business choices. Public and repo-only reads, deterministic baselines, safe reports, and proposal drafting are pre-authorized by this workflow.
