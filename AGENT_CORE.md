# MAPLAB Agent Core

This file is the cold-start control contract. Detailed policy remains in `AGENT_RULES.md`; current work truth remains in `CURRENT_STATUS.md` and the active Task Card.

1. Read `CURRENT_STATUS.md`, `pitfalls.md`, and the active Task Card before action. Never rely on chat memory as state truth.
2. State role, environment, and exact task before acting.
3. For development: clarify the requested outcome, state the bounded version change, and ask only when a material choice cannot be discovered safely.
4. Every session leaves file-backed evidence, one Next Bounded Action, and a Resume Prompt. Stage only task-related files.
5. A repeated mistake becomes a `pitfalls.md` entry with trigger, root cause, remedy, prevention, and verification.
6. A third repeat, version churn without objective improvement, or an Owner challenge triggers the first-principles five questions before more execution.
7. Before asking the Owner to unblock work, try two safe methods, inspect available tools/agents, and report attempts plus the smallest five-minute Owner action.

External publishing, customer messaging, secrets, trading, irreversible changes, new spend, and private-data egress follow their explicit approval gates. A process exit, API 200, queued worker, or chat response is not completion without the promised artifact/live readback.
