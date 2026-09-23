# Durable job contract

Use this contract for `workbook/reviews/MAPLAB-DURABLE-JOBS/<job-id>/job.json` and `job.md`.

## Required fields

- `schema_version`: `maplab.durable-job.v1`
- `job_id`: server-generated `MAPJOB-YYYYMMDD-HHMMSS-xxxxxx`
- `created_at`, `updated_at`
- `requester`: channel, Owner identity, and reply destination; private receipt only
- `request`: exact Owner goal stored locally with mode `0600`
- `job_type`: `a8-production`, `hermes-line-training`, `public-research`, or a named domain adapter
- `state`: one of the states below
- `acceptance`: observable artifact, link, live readback, and receipt requirements
- `authorization`: actions already explicit in the Owner goal; do not ask twice
- `data_class`: `public`, `synthetic`, `deidentified-private`, or `private-local-only`
- `deerflow_view`: sanitized metadata only; never copy the raw request when data is not public
- `attempt`, `max_attempts`, `wall_deadline`, and any spend cap
- `current_phase`, `last_result`, `next_bounded_action`
- `objective_metrics_before`, `objective_metrics_after`,
  `owner_acceptance_delta`, `unlocked_next_action`, and `attempt_consumed` in
  each bounded-action result; method/test deltas do not substitute for these
- `artifacts`: absolute paths/URLs plus hashes or readback status
- `history`: append-only state transition summaries
- `resume_prompt`: enough for a fresh session to continue without chat memory

All directories are `0700`; files are `0600`. Write atomically. Do not put secrets in a job packet.

`attempt_consumed=false` is allowed once for an objective-plateau review/re-route
and for pure polling/readback of an already-running external action. The next
executed domain experiment consumes one attempt. Repeated replanning without
new evidence cannot avoid the counter. A supporting job split from the main
objective records a lower priority, attempt/spend cap, parent job, and a rule
that it cannot displace the main job absent a verified urgent safety issue or
Owner priority change.

## State machine

```text
ACCEPTED -> RUNNING -> WAITING_EXTERNAL -> RUNNING
                    -> OWNER_REVIEW -> RUNNING
                    -> BLOCKED
                    -> FAILED
                    -> COMPLETED
```

Only a verified artifact or live readback can enter `OWNER_REVIEW` or `COMPLETED`. A timeout should preserve a Resume Prompt and retry count, not erase the job.

## Auto-route rules

- Explicit long-run language (`持續`, `多輪`, `直到`, `跑完`, `全流程`, `交付成果`, `不要停`) is sufficient.
- A8 generation plus video/upload is durable even without those words because it spans providers, media QA, and platform state.
- LINE training/evaluation is durable when more than one round or a quality threshold is requested.
- Public research becomes DeerFlow work when it is multi-source, comparative, or part of a longer workflow.
- Never auto-route a greeting, small lookup, simple status question, or a single local edit.

## Authorization examples

| Owner wording | Record as authorized | Still gated |
|---|---|---|
| 生歌＋做影片給我看 | generation, local render, QA package | external upload, public publish |
| 上傳 YouTube 給我看 | private/unlisted upload and readback | public visibility |
| 發布到 YouTube | upload, public publish, public readback | new spend or unrelated platforms |
| LINE 多跑幾輪訓練 | offline rounds and lesson updates | any customer send |

If a supplied asset is private and the requested tool would send it to a new third party, record `OWNER_REVIEW` for that specific egress unless the Owner already named that provider/action in the same goal.

## Heartbeat behavior

At each wake:

1. Select the oldest/highest-priority nonterminal job whose retry time has arrived.
2. Read its Task Card, Resume Prompt, domain SOP, and latest receipt.
3. Compare the last three receipts against Owner-facing acceptance. If two
   consecutive actions have zero objective delta, run the objective-level
   circuit breaker and re-route before executing more supporting work. The
   re-route itself records `attempt_consumed=false` and does not increment the
   domain attempt.
4. Run exactly one bounded action or poll an external provider.
5. Verify and atomically update the job.
6. Continue on later wakes while state is `RUNNING` or `WAITING_EXTERNAL`.
7. Notify the Owner only for `OWNER_REVIEW`, `BLOCKED`, `FAILED`, or `COMPLETED`, and deduplicate notifications, except for a newly verified urgent safety issue.
