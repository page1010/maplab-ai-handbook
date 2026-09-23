# Validation Receipt — A2 SEO Meaningful Wake + Hermes Dispatch

- Verified at: `2026-09-01 12:25 Asia/Taipei`
- Scope: public site reads, repo artifacts, local routing, reversible scheduler state
- Live external writes: `0`
- Customer sends: `0`
- Private third-party egress: `0`
- Spend: `0`

## VERIFIED — public sensor

- Probe: `.agents/skills/maplab-seo-coach-patrol/scripts/public_seo_probe.py`
- Model: `none`
- Method fingerprint: `cd028320bc30cba1c78da38ef1cb2be6a02a11c91b3873b47192463b047de5a0`
- Saved baseline SHA-256: `c20cb0cf201976f91bb7cc88eddb293e6ef0b0a0fade332a11d9964dde22353e`
- Public WordPress counts: `58 posts / 6 pages`
- Child sitemap counts: `58 post URLs / 6 page URLs`
- Replayable same-method comparison: `public_seo_no_delta_receipt.json`, generated `2026-09-01T04:25:10+00:00`, baseline SHA-256 `c20cb0cf201976f91bb7cc88eddb293e6ef0b0a0fade332a11d9964dde22353e`, both method fingerprints `cd028320bc30cba1c78da38ef1cb2be6a02a11c91b3873b47192463b047de5a0`, `verified_delta=false`, `decision=NO_DELTA_NO_DISPATCH`.
- `/press-conference-catering/`: HTTP 200, self-canonical, index/follow, and finding `invalid_json_ld` remains stable.
- Replayable full-corpus receipt: `public_seo_corpus_audit.json`, method fingerprint `bb802a57fcb5ebcfa9fed1a5cd99b6e5fe3992488c1cee6e52e0e90888aea083`; post/page sitemaps contain `58 + 6 = 64` URLs, `all_http_200=true`, and `/press-conference-catering/` has zero inbound sources. This is a structure opportunity, not proof of ranking loss.

## VERIFIED — Skill and routing gates

- Skill validator: `Skill is valid!`
- Skill inventory: `19 skills`, duplicate frontmatter names: `{}`
- Python compile: router, executor, gateway, public probe, and full-corpus audit passed.
- Task-scoped staged-index Hermes routing/gateway tests: `29/29 PASS`.
- Canonical live-worktree full Hermes suite: `134/134 PASS` (`python -m unittest discover -s tests -p 'test_hermes*.py' -q`).
- Red-team cases fail closed:
  - automatic Google Ads bid change;
  - immediate Rank Math activation;
  - customer conversation sent to OpenRouter;
  - sending LINE to a customer.
- Safe controls remain allowed:
  - public read-only SEO patrol;
  - updating an SEO plan in repo;
  - the word `上傳` does not by itself become a customer-send match.
- Gateway end-to-end routing is typed as `EXECUTE / REJECT / CHAT`; executor rejections cannot fall through to provider chat.
- Provider-egress DLP checks both current text and local history before any OpenRouter call; mock tests prove zero provider calls for customer data, LINE conversation text, and a direct phone number.
- Linked DeerFlow terminal receipts now require allowlisted topology, exact parent job/request/action binding, a real same-task artifact, and recomputed SHA-256 before they can project `COMPLETED` or notify the Owner.

### Source snapshots and replay boundary

The task-scoped staged index passed its exact 29 routing/executor/gateway tests plus compile. The canonical worktree passed all 134 Hermes tests. A full-discover replay from a clean index archive is not a valid substitute because four unrelated LINE tests intentionally depend on pre-existing ignored durable-job receipts; the clean archive therefore reported four missing-fixture errors rather than a code regression.

- router: `15ea98bd7e74e6a361f4bc0659f05b9ca0a04101872aeb1bdfafc3ee0777903f`
- executor: `71ffc266e2f72a4fe5ea56830dd6e8c016d35d501c653ed00da46b35e8270488`
- gateway, task-scoped staged checkpoint: `7a957bf814fc65657cec14f25b1fb6dd06650d41f61de2e6fa2f61a5135f353d`
- gateway, canonical worktree full-suite run: `211e7adf91a92da71811cfe98a141c30c8d1abca3a2aae3ef6de8f0e5e5a028b`
- router tests: `d2af86ca18f3d446f0e9ce879b424b33db8119820a81e1e03dc98d4dbf14a8dc`
- executor tests: `0aa9cf20fa6b20daf1c1eaedf581bc6fed5faa52bcbc507a1afa21933cebd168`
- gateway tests: `81a133cfd97d3c8ac2e60a9c95a6e5f39a6047351e5ee2ee7887032f8c371aae`
- public probe: `02dc1d043805d83625d333d4d9aaf0db769e09f58e2b164fbbf400bd1bb72718`
- corpus audit: `28f3695d39eead55bc156ae1997e708ebf953c3ae15b75d3f9c016482da408db`
- Skill validator: `Skill is valid!`; inventory: `19 skills`, duplicates `{}`.

## VERIFIED — Hermes receipt

- Task Card: `handoff/tasks/T-A2-HERMES-SEO-COACH-001.md`
- Job: `MAPJOB-20260901-120729-7b2afc`
- State: `RUNNING`
- Adapter: `codex-heartbeat+maplab-seo-coach-patrol`
- Request channel: `local-heartbeat`
- Notification policy: `none`
- Current phase: `post-879-jsonld-preview-proposal`
- Attempt: `0`; attempt consumed: `false`; Owner acceptance delta: `0`
- Authorization readback: `public_site_read=true`, `repo_report_write=true`; WordPress, Ads, Rank Math, external-system writes, customer sends, and private third-party egress are all `false`.
- Next action is one preview-only raw-newline normalization proposal for post 879. No worker subprocess, DeerFlow job, Telegram message, or LINE message was started.

## VERIFIED — old-loop containment

- `com.maplab.seo-loop` was loaded but not running, scheduled daily at 02:00, with no live run count in the current launchd generation.
- Historical state/logs showed repeated `all_gaps_drafted` no-op churn.
- Reversible action: `launchctl bootout gui/501/com.maplab.seo-loop`.
- Live readback after bootout: service not found in `gui/501`.
- Existing Codex automation `a2-ads-seo-wordpress-patrol` was updated in place, rewritten to use the meaningful-wake contract, changed from worktree to canonical local execution, and set to `PAUSED` while the deterministic sensor remains the gate.

## MISSING

- Fresh GSC query/page data, URL Inspection, CTR, rankings, and Core Web Vitals.
- Authenticated current Google Ads or Meta Ads evidence.
- Live WordPress preview/write receipt for the proposed post 879 fix.
- A newly installed recurring no-model sensor schedule. This turn bundled and verified the deterministic gate, paused the old model schedule, and dispatched the current job; it did not create a new unattended scheduler.

These remain `MISSING`; none was inferred from an old report.

## Governance audit limitation

- Required cold-start files are present; Next Bounded Action and Resume Prompt are present; the automation routing check is `dynamic` and `routing_aligned=true`.
- The current governance audit regex strips `handoff/` from `handoff/tasks/...` and therefore reports `active_task_exists=false` against a non-canonical `tasks/...` path. Direct readback confirms the canonical Task Card exists. No duplicate Task Card or compatibility copy was created to mask this tool false-negative.

## Next acceptance check

Hermes/A2 produces `press_conference_faq_jsonld_patch_proposal.md` with one changed variable and a local parser receipt proving candidate JSON-LD `2/3 -> 3/3`. Coach readback is required before `OWNER_REVIEW`; a live-site repair must not be claimed without a later authorized WordPress write and public readback.
