# A0 Architecture Patrol — Ecosystem Learning Loop

Date: 2026-06-15
Agent: A0 Dispatch Secretary / Codex
Risk: medium
Scope: Read-only architecture patrol plus GitHub improvement proposal. No WordPress, Ads, GTM, Pixel, budget, secret, or production setting changes.

## Input

Owner provided a repost summarizing Satya Nadella's thesis: enterprise advantage in the AI era should not come from picking one frontier model, but from owning a learning loop that compounds human capital and company-owned AI capability. The post was treated as strategic input, not as MAPLAB state evidence.

Public cross-check: Business Insider reported the same core claim on 2026-06-15: Nadella warned against value concentrating in a few models and argued companies need control over their learning systems.

## Cold-Start Evidence Read

- `CURRENT_STATUS.md`
- `pitfalls.md`
- `chrome-extension/task-modules/A0.json`
- `recalls/A0_recall.md`
- `AGENT_STARTUP_PROTOCOL.md`
- `AGENT_RULES.md` Section 10 / 15 / 16
- `docs/agent-behavior-framework.md`
- `docs/a0-dispatch-operations-manual.md`
- `skills/task-progress-guide.md`
- `skills/a0-proactive-dispatch-guide.md`
- `skills/hermes-patrol-reaction-loop.md`
- `projects/v6-architecture.md`
- `docs/agent-hq-architecture.md`
- `handoff/tasks/T-HQ-001.md`
- `handoff/tasks/T-A1-V7.md`
- `workbook/hermes/patrol/latest.json`
- sampled task cards named by the Hermes reaction packet

`AGENT_CORE.md` is not present in repo root. I used the CURRENT_STATUS source-of-truth list and A0 module `read_first` list instead.

## Patrol Commands

```bash
rtk python3 tools/hermes_patrol_bridge.py --repo /Users/pagemacmini/maplab-ai-handbook
rtk gh issue list --repo page1010/maplab-ai-handbook --state open --search "learning loop OR token capital OR Hermes patrol OR stale-active-dispatch OR AGENT-HQ" --limit 20 --json number,title,url,labels,state
```

The first command succeeded and regenerated Hermes reaction outputs. The first GitHub CLI attempt failed under restricted network, then succeeded with approved GitHub network access and returned `[]`, so no matching open issue was found.

## Verified Facts

- v6 already names the correct strategic direction: observation, business closed loop, and strategy cycle. It explicitly says MAPLAB is a Shadow System where real operations stay intact and AI learns beside them.
- `pitfalls.md` already contains the key local rule: patrol delivery is not reaction. Collect / deliver / react / dispatch / memory are separate layers.
- Hermes reaction bridge exists and is deterministic: it does not call an LLM, read `.env`, or modify external systems.
- Latest generated Hermes packet:
  - total task cards: 37
  - blocked: 4
  - active: 11
  - stale_active: 11
  - unmarked: 5
  - owner_related: 16
  - Hermes CLI exists, model is `gemma4:latest`
  - Hermes gateway is stopped
  - Telegram is not configured for Hermes
  - Chrome Extension module gap is false; 29 modules include Hermes runtime target
- T-HQ-001 has P1-P4 done and P5/P6 pending:
  - P5: data-policy automation
  - P6: Hermes memory enablement and A7 LINE JSONL export
- T-A1-V7 already points at the same underlying architecture goal: single truth, auto-sync, slimming, auto skill generation, and compression.
- The current worktree is dirty with many existing modifications and untracked artifacts. This was not created by this patrol. It is relevant as a symptom: MAPLAB has many token outputs, but not enough artifact classification.

## First-Principles Check

1. What are we protecting?
   MAPLAB's company-specific learning: decisions, pitfalls, task outcomes, quote corrections, WordPress facts, photo labels, customer responses, and agent operating procedures.

2. What is the actual Owner utility?
   Owner should be able to send one outside command and get role selection, cold-start context, worker dispatch, progress receipt, and durable writeback.

3. What cannot be outsourced?
   Learning. A model can generate text or code, but MAPLAB must own the evaluation signals, replay tests, task outcomes, memory candidates, and decision history.

4. What compounds?
   Replayable evaluations plus structured memory. A patrol finding becomes valuable only when it becomes a role-owned next action, an eval fixture, or a pitfall/skill update.

5. What should be deferred?
   Panel polish, metadata reshuffling, and extension cosmetics. They matter only after reaction/dispatch/memory has a working path.

## Architecture Diagnosis

### What is already strong

- MAPLAB has rich human capital capture: task cards, pitfalls, owner requirements panel, review bundles, role recalls, and operating manuals.
- MAPLAB has many token-capital artifacts: A6 quote engine, A4 photo classification/alt pipelines, SEO factory, Chrome role modules, Hermes reaction packets, and local-control-plane panels.
- The architecture already supports model plurality: Codex, Claude, Hermes, OpenClaw, local Ollama, Antigravity, Gemini, and Chrome-side roles are named surfaces.
- The culture already rejects fake blockers: AGENT_RULES Section 16 requires three-layer blocker review.

### Gap 1 — Reaction loop is not enforced

Evidence: Hermes packet found 4 stale blockers, 11 stale active tasks, and 5 unmarked task cards. The bridge produces reaction cards, but there is not yet a persistent reaction ledger that forces each card into `direct-do`, `delegated`, `true Owner 5-minute action`, `memory candidate`, or `closed`.

Risk: daily patrol becomes repeated notification instead of organizational learning.

### Gap 2 — Token capital is not measured as an asset

Evidence: MAPLAB has many generated artifacts, but there is no registry saying which artifact is:

- company knowledge,
- replay/eval fixture,
- runtime output,
- disposable noise,
- customer-facing publish candidate.

Risk: the system produces more files without knowing which ones improve future work.

### Gap 3 — Internal evals are role-local, not system-wide

Evidence: A6 has QA/replay-style artifacts, but A0 blocker review, A2 WordPress safety, A4 photo pipeline, Hermes reaction quality, and A1 task-card normalization do not share a common eval interface.

Risk: swapping the underlying model may preserve prompts but lose the "company veteran" behavior.

### Gap 4 — Knowledge base is Markdown-first, not query-first

Evidence: CURRENT_STATUS is the single entrance, but T-A1-V7 still records the 226 markdown file problem and the need for single truth, auto-sync, slimming, auto skill generation, and compression.

Risk: cold-start is better than memory recall, but still expensive and brittle. Agents know which files to read only if routing is current.

### Gap 5 — Model replaceability is declared but not smoke-tested

Evidence: role modules list Hermes targets and runtime selectors, but Hermes gateway is stopped and Telegram not configured. There is no model-swap smoke that checks whether A0/A1/A6 can produce the same output contract across Codex/Hermes/local worker.

Risk: MAPLAB can choose models, but cannot yet prove company knowledge survives model replacement.

### Gap 6 — Stale blockers hide direct-do work

Evidence from sampled task cards:

- T-A7-002 still has direct-do Phase 3A work such as region rule and flowchart sync.
- T-A1-V6-P2 can be pushed by creating virtual test data and running A6, not only by waiting.
- T-A2-005 should be converted from "waiting for WP credential" into an approval-ready staging/prod gate.
- T-A2-002 may need a current public/front-end scan before keeping a 69-day Owner-only blocker.

Risk: Owner receives repeated stale actions instead of a short list of true decisions.

## Recommended GitHub Issue

Create one umbrella issue:

`Architecture: MAPLAB Learning Loop v0 — patrol reaction -> eval -> memory -> dispatch`

Created: https://github.com/page1010/maplab-ai-handbook/issues/14

Why one umbrella issue:

- This is a medium-risk architecture improvement across A0/A1/B1, not a single bug.
- It should not be mixed into the existing dirty worktree.
- It gives future agents a GitHub-tracked place to split implementation PRs.

## Proposed Implementation Phases

### Phase 1 — Reaction Ledger

Create a durable ledger for patrol reaction cards.

Suggested path:

- `workbook/learning_loop/reaction_ledger.jsonl`
- or `workbook/hermes/patrol/reaction_ledger.jsonl` if keeping it under Hermes.

Each row:

- `reaction_id`
- `generated_at`
- `owner_role`
- `target_task_card`
- `decision`: `direct_do` / `delegated` / `owner_5min` / `memory_candidate` / `closed`
- `next_action`
- `assigned_to`
- `due_at`
- `evidence_path`
- `status`

Acceptance:

- A patrol reaction card cannot disappear after generation.
- Stale reactions older than 7 days are escalated to A0/A1 review.

### Phase 2 — Token Capital Registry

Create a registry that classifies outputs.

Suggested path:

- `workbook/learning_loop/token_capital_registry.json`

Classes:

- `company_knowledge`
- `eval_fixture`
- `runtime_output`
- `publish_candidate`
- `disposable_artifact`
- `secret_sensitive_excluded`

Acceptance:

- New review bundles can register whether they contain reusable knowledge.
- Dirty worktree patrol can separate useful token capital from noise.

### Phase 3 — Internal Eval Harness

Start with 5 eval families:

- A0: stale blocker three-layer review quality
- A1: task-card status normalization
- A2: WordPress/SEO public-output safety and live URL sanity
- A4: photo pipeline progress and no-duplicate/no-destructive behavior
- A6/A7: quote/customer conversation replay from safe samples

Acceptance:

- `make` or script command runs evals without secrets.
- Each eval emits `pass/fail`, evidence path, and regression note.

### Phase 4 — Model-Swap Smoke

For each key role target, verify that changing worker/model keeps the output contract.

Initial targets:

- Codex
- Hermes local layer
- local Ollama where deterministic fallback exists

Acceptance:

- A0/A1/A6 minimal tasks produce required sections and do not ask Owner for false blockers.
- Failures become eval fixtures or pitfalls.

## Immediate Next Actions

1. Open the GitHub issue with the body in `github_issue_body.md`.
2. Have A1/B1 choose the first implementation slice:
   - recommended first slice: Phase 1 reaction ledger, because Hermes bridge already emits structured cards.
3. Keep CURRENT_STATUS unchanged unless implementation actually starts; this patrol is an architecture proposal and review bundle.

## Handoff Checkpoint

- Read: files listed above.
- Changed: this review bundle and regenerated Hermes reaction packet.
- Confirmed: no matching open GitHub issue found by `gh issue list`.
- Next: implementation owner should start with Phase 1 reaction ledger from issue #14.
- Blockers: none.
- Files to review next:
  - `workbook/reviews/JOB-A0-ECOSYSTEM-LEARNING-LOOP-20260615/github_issue_body.md`
  - `workbook/hermes/patrol/latest.json`
  - `skills/hermes-patrol-reaction-loop.md`
  - `handoff/tasks/T-HQ-001.md`
  - `handoff/tasks/T-A1-V7.md`
- Shortest Path:
  1. Run Hermes bridge.
  2. Read `latest.json` counts and reaction cards.
  3. Sample named task cards.
  4. Create one GitHub issue for the missing learning loop.
- Tool Choices:
  - Used local files for MAPLAB facts.
  - Used Business Insider only to cross-check the external Nadella summary.
  - Used `gh issue list` to avoid duplicate GitHub issues.
