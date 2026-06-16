# Hermes Patrol Reaction Loop

Use this skill when Owner asks whether the daily Telegram patrol is being acted
on, whether Hermes can inspect patrol results, or whether repeated patrol
messages should become role-owned next steps.

## Role

Hermes is the cold-path reaction layer. It does not replace the deterministic
patrol script and does not own hot-path Telegram decisions.

- `scripts/patrol.sh`: collect task-card status and OAuth signals.
- `scripts/patrol-scheduled.sh`: scheduled wrapper and Telegram delivery.
- `tools/hermes_patrol_bridge.py`: convert patrol text + task cards into a
  Hermes-readable packet, prompt, Telegram decision card, and status panel.
- `local-control-plane/hermes.html`: Owner-visible panel.
- `workbook/hermes/patrol/latest.json`: machine-readable packet.
- `workbook/hermes/patrol/hermes_prompt.md`: prompt for Hermes or another
  cold-path worker.

## First Check

Run:

```bash
python3 tools/hermes_patrol_bridge.py --repo /Users/pagemacmini/maplab-ai-handbook
```

Then inspect:

```bash
/Users/pagemacmini/maplab-ai-handbook/scripts/open_agent_runtime_panel.sh hermes
```

## Decision Rule

Telegram delivery success is not task resolution.

Every daily patrol should result in one of:

1. No critical reaction; archive packet only.
2. A role-owned direct action that can be done without Owner.
3. A Codex/OpenClaw/Hermes task packet for controlled work.
4. A true Owner 5-minute card after three-layer blocker review.
5. A memory write-back candidate when the same failure pattern repeats.

## Priority Order

Owner's actual use case is an outside command window.

1. P0: Telegram command window. Owner sends one message; the system chooses the
   role, attaches the cold-start prompt/context, dispatches Codex/Hermes/A1/B1,
   and reports progress.
2. P1: Patrol reaction cards. Daily patrol findings become role-owned next
   steps and Codex follow-up prompts.
3. P2: Chrome Extension / role module / dashboard metadata sync.
4. P3: Panel polish.

Do not spend the main work budget on P2/P3 before P0/P1 has a working path.

## Anti-Pattern: Artifact Substitution

Do not replace the command-window problem with a nearby artifact cleanup.

Bad substitutes include:

- panel polish,
- Chrome Extension metadata sync,
- generated role module cleanup,
- dashboard status cards,
- README or skill routing updates,
- Hermes status JSON without Telegram command intake.

These can be useful later, but they do not prove Owner can command the system
from outside.

Before changing any artifact, answer:

1. What command can Owner send from Telegram?
2. Which role will be selected?
3. Which cold-start prompt/context will be attached?
4. Which worker receives it?
5. What receipt will Owner see?

If those five answers are missing, stop artifact work and build the command
window path first.

## Role Next-Step Packet

Each reaction card should include:

- `owner_role`
- `target_task_card`
- `next_step`
- `next_step_patch_hint`
- `codex_followup_prompt`

This prevents the system from saying "problem found" and stopping there.

## Guardrails

- Do not print `.env`, token, refresh token, cookies, or full OAuth JSON.
- Do not let Hermes one-shot auto-modify external systems from a scheduled job.
- Do not keep relaying stale blockers without assigning a next owner.
- Do not ask Owner until false blockers are removed by the three-layer review:
  another agent can solve, current agent can solve, or true Owner action.

## Chrome Extension Connection

Chrome Extension is the role summon entrypoint. When `runtime_target: hermes` is
selected, the handoff should point the worker to:

1. role task module JSON,
2. `CURRENT_STATUS.md`,
3. `pitfalls.md`,
4. `workbook/hermes/patrol/latest.json`,
5. role-specific task cards.

If the popup selector has Hermes but the task module JSON does not list Hermes,
the next A1 task is to rebuild role modules after updating the generator.
