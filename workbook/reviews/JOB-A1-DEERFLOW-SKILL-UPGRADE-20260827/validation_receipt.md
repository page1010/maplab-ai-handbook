# Validation Receipt — DeerFlow/OpenRouter + Screenshot Tool Skill Upgrade

- Task: `T-A1-DEERFLOW-SKILLS-001`
- Date: 2026-08-27 Asia/Taipei
- Actor: Codex acting as A1 Skill/SOP Engineer
- Scope: reversible local/user/repo setup and documentation only
- Overall: `PASS_WITH_RUNTIME_GATE`

## Outcome

The system now has a discoverable DeerFlow/OpenRouter isolation skill, a MAPLAB lead-intake/follow-up repo skill, and the official Playwright agent CLI skill. DeerFlow source/config/backend diagnostics are prepared, but no service was launched because local nginx and Docker are absent.

## Installed or created

| Item | Location/version | Result |
|---|---|---|
| DeerFlow source | `/Volumes/MacExternal/MAPLAB_WORKSPACE/tools/deer-flow` at `788a890bd022689ef293e6bbfa2c12988173db6c` detached HEAD | PASS |
| DeerFlow config | ignored `config.yaml` v36; OpenRouter env placeholder; `google/gemma-4-31b-it:free` | PASS |
| DeerFlow diagnostic env | checkout-local `.venv`, 222 packages installed by `make doctor` | PASS, documented side effect |
| DeerFlow user Skill | `/Users/pagemacmini/.agents/skills/deerflow-openrouter-research` | PASS |
| MAPLAB lead repo Skill | `.agents/skills/maplab-lead-intake-followup` | PASS |
| Playwright CLI | `@playwright/cli` 0.1.18 | PASS |
| Playwright Agent Skill | `/Users/pagemacmini/.agents/skills/playwright-cli` | PASS |

No nginx, Docker, Anime.js, Cult UI, Supabase project/CLI, production service, public port, scheduler, Telegram route, or data migration was added.

## DeerFlow checks

- Official checkout anchors: `Makefile`, `backend/`, `frontend/`, `config.example.yaml` — PASS.
- Pin: exact reviewed commit, detached HEAD — PASS.
- Active model: `openrouter-gemma-4-31b-free` — PASS.
- Protected env check: `OPENROUTER_API_KEY` name present; value never printed — PASS.
- `make doctor` with protected env in process:
  - Python 3.12.13, Node 25.8.1, pnpm 11.19.0, uv 0.11.1 — PASS.
  - config loadable; one model configured; `langchain-openai` installed — PASS.
  - nginx — FAIL/MISSING.
  - Docker CLI — MISSING.
  - service launch and provider inference call — NOT RUN.
- Offline preflight result: only blocker `local_dependencies_missing=[nginx]`; warnings `docker_cli_not_installed` and no provider-call proof.

## Skill and flow checks

- `quick_validate.py` on `deerflow-openrouter-research` — PASS.
- `quick_validate.py` on `maplab-lead-intake-followup` — PASS.
- lifecycle audit from MAPLAB repo — both new skills and `playwright-cli` discovered; duplicates `{}` — PASS.
- `python3 -m unittest tests.test_a6_intake_flow` — 7 tests PASS.
- Independent forward test — PASS: public DeerFlow routing, PII rejection, exact nginx blocker, synthetic DM ten-field gate, `dedupe_status=unverified`, `draft_only`, and no-send behavior all matched the Skill contracts.
- Forward-test source conflict — FIXED: legacy A7 five-field and A6 two-field readiness rules are now explicitly superseded; current readiness is uniquely anchored to the 2026-08-26 ten-field SOP plus `intake_flow.py`.
- `python3 .agents/skills/maplab-lead-intake-followup/scripts/lead_contract_smoke.py` — PASS: synthetic input produced only `外燴 + 30`, eight missing fields, event-date next question, no case creation, no network/send side effect.

## Playwright smoke

- Version readback: `0.1.18` — PASS.
- Session: `maplab-skill-smoke`.
- Public target: `https://example.com`.
- Page title: `Example Domain`.
- Snapshot: `/Volumes/MacExternal/MAPLAB_WORKSPACE/outputs/2026-08-27_deerflow-openrouter-upgrade/playwright-smoke/example-domain.snapshot.yml`.
- Session close readback: `Browser 'maplab-skill-smoke' closed` — PASS.
- Final `playwright-cli list`: `(no browsers)` — PASS.
- Persistent profile/cookies: not used.

## Tool decision evidence

- Anime.js: defer to a real frontend project; install as project dependency and require reduced-motion/cleanup QA.
- Cult UI Hero Color Panels: defer to a React/TypeScript/Tailwind portal; import one reviewed source component, not a global package or WordPress shortcut.
- Lead follow-up: existing A7/A6/A5 workflow was wrapped as a repo-discoverable skill; no second CRM or new SaaS.
- Playwright CLI: installed for isolated, repeatable regression evidence; authenticated Owner state stays in existing Browser/Chrome route.
- Supabase: deferred until authenticated portal SSOT, PII, RLS, backup, migration, and rollback are approved.

## Safety readback

- Secret values printed or committed: zero.
- Customer/investment/private data sent externally: zero.
- External message, publish, ad, quote, order, or trading action: zero.
- Background service or listener left running: zero; final process/listener filters returned no DeerFlow or Playwright CLI process, and `playwright-cli list` returned `(no browsers)`.
- Existing dirty work staged or overwritten: zero; task-scoped paths only.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| DeerFlow Skill `SKILL.md` | `11e915069b82b7664bb772bfeb7a33a79d8ae3008298d7c6c81ec69da1bdb938` |
| DeerFlow preflight helper | `bddfb8127dd90449c6eb640b9f800933118c283ae018296aefb987646dc54920` |
| MAPLAB Lead Skill `SKILL.md` | `75c6b6a20ec0340fb084256ae7206eef9a18f6cee76f9f23437952c448b2d89a` |
| Lead contract smoke | `26bc016b4a8fdcc40ff5d736f8d4fcdd321faa5f3f463230ec58f356ed2057b5` |
| Playwright snapshot | `2f6f77bbc918236f7f9cd0db31a258c3744f5b6fa2dde2b1af346d04094a5692` |

## VERIFIED / DRIFT / NEXT

- `VERIFIED`: Skill discovery, validators, lead tests, Playwright smoke, DeerFlow pin/config/key-name loading, and exact local dependency gap.
- `DRIFT`: OpenRouter free-model availability and account Guardrail policy can change; verify live before every smoke. DeerFlow moving `main` is not trusted beyond the pinned commit.
- `NEXT`: only if Owner wants a live DeerFlow smoke, choose a reviewed Docker runtime or explicitly approve nginx installation, then run one loopback-only public/synthetic test with account-level provider-policy readback and a clean-shutdown receipt.
