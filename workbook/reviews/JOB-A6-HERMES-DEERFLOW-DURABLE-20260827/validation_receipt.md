# A6 Hermes durable routing validation receipt

- Date: `2026-08-27 Asia/Taipei`
- Implementation: `2a5b361e3c09b170ef33b50ee78fd60ced6c3a9f`
- Task: `handoff/tasks/T-A6-HERMES-DEERFLOW-001.md`
- Result: `IMPLEMENTED`; LINE quality qualification remains a live durable job, not a claimed pass.

## Outcome contract

The Owner states the outcome in natural language. Hermes classifies locally and creates an owner-only `MAPJOB`; no `/research-*` command, provider name, or worker name is required. Public multi-source research may invoke hardened DeerFlow. A8 assets and LINE corpus remain with local domain workers. The 30-minute `MAPLAB durable job continuation` heartbeat resumes nonterminal jobs and performs one bounded action per wake.

## DeerFlow live evidence

- Official checkout: `/Volumes/MacExternal/MAPLAB_WORKSPACE/tools/deer-flow`
- Pinned commit: `788a890bd022689ef293e6bbfa2c12988173db6c`
- Runtime: embedded one-shot worker; no nginx, Docker, or public listener required.
- Local provider: `gemma4:latest` through Ollama.
- Natural-language parent job: `MAPJOB-20260827-221144-64831c` -> `COMPLETED`.
- Worker: `DFR-20260827-221144-b2879c` -> `completed` in `99.241s`.
- Artifact: `workbook/reviews/A6-HERMES-TASKS/DFR-20260827-221144-b2879c/research.md`
- Artifact SHA-256: `d643a8c0ba1473a1a1df9d771a21c53fda2b26485d0e1cd04a84e4e27b277888`
- Receipt SHA-256: `293354ad8049d84685027e89532c71a8a7b230616d33f3785ac554f20db7ae01`
- Usage: input `3553`, output `1687`, total `5240`; five public source URLs; model tools used `[]`.
- Both local and OpenRouter profile validation returned all checks true: memory and persistent DB off, model tools empty, host bash off, authorization and guardrails fail closed, scheduler and MCP tasks off, bounded subagents and token budget.
- OpenRouter execution remains disabled. The account-level privacy policy has not been authenticated in this runtime and no spend approval was inferred; the profile is configuration-only and requires both gates before a key is passed.

## LINE private-local-only evidence

- Protected cache: `/Users/pagemacmini/.maplab/a6-hermes-training` (`0700`); corpus files are `0600`.
- Train SHA-256: `1368a37084e5c4bb1539ec0ef8aa64827c3a17f56c84a9f8e2a7212f41f0e5db`
- Eval SHA-256: `24ef3187892c4fd65d6e96bb6dac9b43f54c6c4ce5629a33f3c183d3b5cafbe7`
- Manifest SHA-256: `a7841aac939f3b6b6d29ddf41bb14c84de4b81cc33668122ca10b5eb396843ea`
- Single-case smoke `HERMES-LINE-20260827-143532-155672`: local Ollama calls `1`, external network calls `0`, no customer or Telegram send.
- launchd batch `HERMES-LINE-20260827-143904-866309`: exit `0`, local Ollama calls `5`, external network calls `0`, pass `1/5`, unsupported price `1/5`, lowest stage `S2_DATA`.
- Batch receipt SHA-256: `2ceb87ada071bef67537274670c6766b8cf5fd99f324ff6927eb554e00c78b83`
- Lesson delta SHA-256: `cb1e9ab211b7ad186cd044ad53c68712d305687a31e510ceeacb1983c32a15d3`
- Natural-language durable job `MAPJOB-20260827-224251-d291ad` started automatically and completed its first two-round bounded supervisor chunk. The canonical state remains `RUNNING` with `bounded_pause/max_rounds_reached`, `round_count=2`, `success_streak=0`, last pass rate `0.0`, last unsupported-price rate `0.0`, local Ollama calls `10`, and external network calls `0`. The next heartbeat resumes the same receipt instead of starting over.
- The current quality result is deliberately not marked complete. Qualification requires seven consecutive full rounds with pass rate at least `0.85` and zero unsupported prices; diagnostic/stage-only rounds cannot count.

## Runtime and tests

- `com.maplab.a6bot`: reloaded and `running`; launchd readback contains `HERMES_LINE_PROVIDER=local-only` and the protected data root.
- `com.maplab.hermes-line-training`: reloaded; manual launchd kickstart finished with exit `0` using the protected cache.
- Focused unittest suite: `59/59 PASS`.
- Python compile: PASS.
- `git diff --check`: PASS.
- Skill validator: PASS.
- Skill lifecycle audit: new repo Skill discoverable; duplicates `{}`.
- Plist validation: repository and installed A6/LINE plists all PASS.

Supervisor regression coverage includes job-scoped flock, stale-writer CAS, immutable criteria and seed schedule, exact seed/stage/batch binding, receipt and lesson-delta SHA-256 replay protection, strict finite metric/provider checks, per-result aggregate recomputation, canonical state transitions, diagnostic exclusion from promotion, and sanitized failure terminalization.

## Owner surface boundary

No test message was sent to Telegram and no customer message was sent. Gateway code and focused notification tests prove terminal notification/dedup logic; live Owner-visible evidence in this run is the local receipt/artifact plus launchd readback. A real Telegram-created job will retain its chat destination and notify only on `OWNER_REVIEW`, `BLOCKED`, `FAILED`, or `COMPLETED`.
