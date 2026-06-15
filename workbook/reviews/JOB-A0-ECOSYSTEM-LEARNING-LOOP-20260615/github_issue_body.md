## Context

Owner asked A0 to reflect on MAPLAB architecture after a post summarizing Satya Nadella's argument: durable AI advantage comes from an enterprise-owned learning loop, not from picking one frontier model.

Local patrol evidence shows MAPLAB already has many pieces of this:

- `CURRENT_STATUS.md` as single entrance
- task cards and pitfalls as human-capital memory
- A6 quote / A4 photo / A2 SEO / Hermes packets as token-capital artifacts
- multi-runtime role modules across Codex, Claude, Hermes, OpenClaw, local Ollama, Antigravity, Gemini

But the loop is not yet closed enough to compound.

Review bundle:

- `workbook/reviews/JOB-A0-ECOSYSTEM-LEARNING-LOOP-20260615/architecture_patrol_report.md`
- `workbook/hermes/patrol/latest.json`
- `workbook/hermes/patrol/latest.md`

## Verified Patrol Facts

Regenerated Hermes reaction packet on 2026-06-15:

- total task cards: 37
- blocked: 4
- active: 11
- stale_active: 11
- unmarked: 5
- owner_related: 16
- Hermes CLI exists and reports `gemma4:latest`
- Hermes gateway is stopped
- Hermes Telegram is not configured
- Chrome Extension module gap is false; 29 modules include Hermes target

`gh issue list` search found no matching open issue for `learning loop`, `token capital`, `Hermes patrol`, `stale-active-dispatch`, or `AGENT-HQ`.

## Problem

MAPLAB collects and delivers a lot of signals, but not every signal becomes one of:

- direct action
- delegated task
- true Owner 5-minute decision
- eval fixture
- memory/pitfall/skill update
- closed/no-action record

That means token output can grow without becoming company-owned learning.

## Proposed Scope: MAPLAB Learning Loop v0

### Phase 1 — Reaction Ledger

Create a durable ledger for Hermes/patrol reaction cards.

Candidate paths:

- `workbook/learning_loop/reaction_ledger.jsonl`
- or `workbook/hermes/patrol/reaction_ledger.jsonl`

Each row should include:

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
- Stale reactions older than 7 days are visible to A0/A1.
- Every Owner action is first filtered through three-layer blocker review.

### Phase 2 — Token Capital Registry

Create a registry that classifies generated artifacts:

- `company_knowledge`
- `eval_fixture`
- `runtime_output`
- `publish_candidate`
- `disposable_artifact`
- `secret_sensitive_excluded`

Candidate path:

- `workbook/learning_loop/token_capital_registry.json`

Acceptance:

- Review bundles can declare whether they contain reusable learning.
- Dirty worktree patrol can separate signal from noise.

### Phase 3 — Internal Eval Harness

Start with five eval families:

- A0: stale blocker three-layer review quality
- A1: task-card status normalization
- A2: WordPress/SEO public-output safety and live URL sanity
- A4: photo pipeline progress and no-duplicate/no-destructive behavior
- A6/A7: quote/customer conversation replay from safe samples

Acceptance:

- A no-secret command runs evals and emits pass/fail evidence.
- Failures become eval fixtures or pitfalls.

### Phase 4 — Model-Swap Smoke

Verify that replacing the worker/model keeps role output contracts intact.

Initial targets:

- Codex
- Hermes local layer
- local Ollama where deterministic fallback exists

Acceptance:

- A0/A1/A6 minimal tasks produce required sections.
- The worker does not create false Owner blockers.
- Any failure becomes an eval fixture or pitfall.

## Why This Matters

This is the MAPLAB version of "do not outsource learning":

- Human capital: Owner corrections, business judgement, task-card decisions, pitfalls.
- Token capital: code, prompts, artifacts, role modules, evals, local-model outputs.
- Durable advantage: the feedback loop that converts both into better future behavior.

## Out of Scope

- No WordPress publishing.
- No Ads/GTM/Pixel/budget changes.
- No secret reads.
- No cleanup of the existing dirty worktree.
- No panel polish until reaction/dispatch/memory has a working path.

## First Implementation Slice

Recommended first slice:

Implement Phase 1 reaction ledger using the existing deterministic output from `tools/hermes_patrol_bridge.py`.

Reason:

- The bridge already emits structured reaction cards.
- It is low-risk and no-secret.
- It directly reduces repeated stale patrol alerts.
