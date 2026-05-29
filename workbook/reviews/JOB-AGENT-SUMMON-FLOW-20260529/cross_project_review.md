# Cross-Project Agent Summon Flow Review

Date: 2026-05-29
Role: B1 Investment OS Logic Bridge Advisor
Scope: MAPLAB + Investment OS agent summon workflow map

## What Changed

- Added MAPLAB-side workflow map: `docs/cross-project-agent-summon-workflow-map.md`.
- Linked the Investment OS twin document: `/Users/pagemacmini/Documents/New project/docs/AGENT_SUMMON_WORKFLOW_MAP.md`.
- Updated `CURRENT_STATUS.md` so cold-start readers can find the map.
- Covered summon entrances: Chrome Extension, Agent Office, Telegram, Codex session, Windows packet bridge.
- Covered worker roles: GPT/ChatGPT, Codex, Claude Code, Claude Chrome tab, Gemini, NotebookLM, Antigravity, Hermes, OpenClaw, local model, Windows agent.
- Covered MAPLAB A roles and Investment OS B1-B4 roles, including why each exists.

## Design Reason

The system needs a role map because "summon an agent" is currently too easy to confuse with "ask any model." The map separates:

- entrance: where Owner starts the request;
- router: which durable role owns the task;
- worker: which tool/model is suited to the action;
- evidence: where the result is written;
- reviewer: who checks the output before it becomes truth.

This keeps Chrome Extension summon simple while still allowing Codex, Claude, Gemini, Hermes, OpenClaw, and Windows agents to do different jobs without becoming competing truth sources.

## Windows To Mac Mini Plan

Windows is designed as a read-only vendor-data collector after close. It should create packet folders with manifest, payload, screenshots/exports, and normalized rows, then sync to Mac mini. Mac mini validates the packet before local model/Hermes/B2/Codex use it for research.

This prevents Windows from becoming a second Investment OS runtime, and prevents vendor UI text from being treated as verified fact before Mac-side validation.

## Boundaries

- No secrets, `.env`, cookies, or API keys read.
- No broker/order/simulation action.
- No Telegram send.
- No WordPress/social publishing.
- No external Chrome Extension runtime mutation in this pass.
