# JOB-A6-HERMES-SHEETS-ASSISTANT-20260901 — Validation Report

Status: `REDTEAM_BLOCKED / CHECKPOINT_SAVED / LIVE_NOT_DEPLOYED`

> 2026-09-01 checkpoint: the earlier `LOCAL_CONTRACT_PASS` below is historical and is superseded by the red-team review. The isolated signed project now lives at `scripts/apps-script-hermes-sheets/`, but final schema/mock/readback verification remains assigned in `checkpoint_handoff.md`. Do not deploy from this report.

## Owner direction

- Hermes does not quote, calculate price, select menu items, promise availability, confirm booking, or decide dietary safety.
- Hermes uses quiet, restrained one-question replies to complete intake.
- After explicit customer confirmation, Hermes may create a neutral Google Sheets quote shell.
- Negotiation or menu-change requests are recorded verbatim against the same `case_id + quote_id`; Mina decides the revision and outcome.

## What / So What / Now What

- What: the prior review surfaced prohibited replies as if they were candidate copy, while the legacy backend could still create price-bearing quote variants.
- So What: supervision checked artifacts and field completion but did not first verify commercial authority, brand tone, and the full downstream route.
- Now What: template contract, runtime route, Sheets allowlist, regression fixtures, Task Card, pitfall, and Resume Prompt now carry the same boundary.

## Implemented

- Machine contract and connected Mina scenario routes: `config/hermes-line-sheets-assistant-v1.json`.
- One-question state, deterministic reply guard, explicit-summary-confirmation gate, neutral Sheet payload, and revision payload: `bot_a6/hermes_sheets_assistant.py`.
- Mermaid flow, Q&A list, Mina template `*` inventory, evidence layers, and deployment boundary: `docs/hermes-line-sheets-assistant-flow-v1.md`.
- GAS source actions: `createQuoteShell` and `appendQuoteRevisionRequest`.
- Legacy A7 template file marked as historical reference; unsafe templates are starred and routed to the new contract.
- Existing Hermes intake dry-run no longer imports or calls the A5 automatic pricing engine.

## Deterministic verification

Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_hermes_sheets_assistant \
  tests.test_a6_intake_flow
```

Result: `21/21 PASS` (`14` new boundary tests + `7` legacy intake regressions).

Additional checks:

- `node --check < scripts/apps-script/Code.gs` → PASS.
- `node --check < scripts/apps-script/ApiEndpoint.gs` → PASS.
- `python3 -m json.tool config/hermes-line-sheets-assistant-v1.json` → PASS.
- `python3 scripts/run_hermes_intake_gym.py` → `gate=PASS`.
- Skill Creator `quick_validate.py .agents/skills/sol56-hermes-training-retrospective` → `Skill is valid!`.
- Numbers document readback after closing the rejected workbook → `0` open documents.

Synthetic dry-run proof:

```text
turns=9
questions_per_turn=1
missing_fields=[]
summary_confirmed=true
action=createQuoteShell
availability_status=UNVERIFIED
dietary_review_status=PENDING_HUMAN
commercial_review_status=PENDING_MINA
has_price_or_menu=false
network_calls=0
external_writes=0
```

Owner negative fixtures that now hard-fail:

1. Fixed total + held availability + no more information required.
2. Universal dietary-safety claim + no more confirmation required.
3. Fixed quote + guaranteed availability + direct booking instruction.

## Primary source hashes

```text
eae9be11e4632601dfb8a1a1f8a733824698b27693d3d308de566f9e21b350e6  config/hermes-line-sheets-assistant-v1.json
02cb2f823429d9a6d6c50eecb6f0a64d0e35c16a9d26e58d3980e1d8eb59bfa6  bot_a6/hermes_sheets_assistant.py
6a4befba378d13996b0ce54d54060df048b4b3864070b1fc9b05c04cbb00ef22  docs/hermes-line-sheets-assistant-flow-v1.md
1c5c4b08833f4a1fae00baae6b4ef1e165edf6a47d15a5a754aedad5070b5323  tests/test_hermes_sheets_assistant.py
05d6245ec06de0a3299bbbd61602fa8f61de59fac74789bfab1c3df6691eb6d2  .agents/skills/sol56-hermes-training-retrospective/SKILL.md
217b02a4afda10746aff5a9a2d7ef5884633da1b6190e9382d04f020c3679bfc  .agents/skills/sol56-hermes-training-retrospective/references/hermes-case-study.md
```

## Evidence boundaries

- Deidentified aggregate audit: 20,256 customer→Mina pairs; median reply length 25 characters; 4,202 records belong to exact-reply clusters. This supports short/template-based interaction, not the truth of historical commercial claims.
- Historical A7 templates are not line-by-line Mina gold and do not provide current price, availability, policy, or dietary authority.
- Explicit Google Sheets mentions in the deidentified corpus were zero; Sheets integration is the Owner's new control-plane requirement, not a historical Mina phrase.

## External effects and remaining gate

- Model calls: `0`.
- Training / optimizer / Ollama calls: `0`.
- Network calls: `0`.
- Real customer Sheets created: `0`.
- LINE customer sends: `0`.
- `clasp push` or GAS deployment: `0`.

The source is ready for Owner review. Live proof requires separate authorization to deploy only the two neutral actions to an isolated test environment and create one synthetic Sheet, then read back that price, menu, deposit, fee, term, availability, and payment fields remain empty or pending-human.
