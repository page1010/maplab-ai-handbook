---
name: mac-local-tool-routing
description: Action-first routing and evaluation workflow for Mac-native AI tool use. Use when a request mentions Mac-1, macOS native tools, Calendar/Mail/Safari/File/Finder automation, AppleScript/osascript, Shortcuts/App Intents, OpenClaw controlling the Mac, or expanding A6/local-model capabilities to operate local apps. The skill prevents permission ping-pong by routing safe work to existing connectors, Chrome/OpenClaw, shell/osascript, and approval-ready packets before adding any new local model/tool runtime.
---

# Mac Local Tool Routing

## Overview

Use this skill to turn "AI can control my Mac" requests into work that actually moves. A local model may parse intent and produce structured plans; existing deterministic tools should execute safe read-only and draft work immediately. Confirmation gates are for irreversible or external actions, not excuses to stop.

## Decision Ladder

1. Prefer purpose-built connectors for account-backed cloud actions: Google Calendar, Gmail, Google Drive, Sheets, Slides, GitHub.
2. Use Chrome or OpenClaw only when the task needs live browser state, logged-in UI, screenshots, or visible readback.
3. Use shell and `osascript`/AppleScript only for local Mac operations with clear app targets and bounded scope.
4. Use the local model only for parsing, classification, extraction, draft plans, and JSON payload generation.
5. If a new Mac-native model/runtime is unverified, keep it out of production but keep working through existing MAPLAB routes.

## Action Tiers

| Tier | Examples | Required handling |
| --- | --- | --- |
| Direct-do | list windows, read current Chrome URL, inspect files, summarize a screenshot, run read-only smoke tests, create local test artifacts | Do it, then write a short receipt. Do not ask Owner first. |
| Draft/approval-ready | draft email, prepare calendar event JSON, prepare Sheet update payload, create disposable test file or test-calendar event plan | Produce the draft/payload and review bundle. Ask only for the final live action if needed. |
| Live write with rollback | create/update a real calendar event, update a Sheet, upload a Drive file | Prepare exact target, diff/payload, rollback or correction path, then ask for one approval. |
| External send/publish | send email/message, publish WP/social, launch ads | Prepare approval-ready plan and final message/content. Execute only after explicit Owner confirmation. |
| High-risk/system | delete, overwrite, mass move, credentials, tokens, payment/broker/order | First find a safe read-only or draft route. If truly unavoidable, present risk, recovery plan, and owner-override request. |

## No Permission Ping-Pong

Before saying "I need Owner" or returning `auth_missing`, run the MAPLAB three-layer check:

1. Can A6/A1/Codex do the read-only or draft part now?
2. Is there an existing connector, credential skill, MCP/API route, Chrome logged-in state, OpenClaw route, shell command, or `osascript` readback?
3. Can the task be advanced to an approval-ready packet without the missing permission?

Only after all three fail, report:

- what was tried,
- why each route failed,
- the smallest 5-minute Owner action needed,
- what work remains ready to run after that action.

## A6 Integration Pattern

When Telegram A6 receives a Mac-native automation request, first produce an intent packet:

```json
{
  "intent": "mac_tool_task",
  "requested_app": "Calendar|Mail|Safari|Finder|Chrome|Sheets|Other",
  "requested_action": "read|draft|create|update|send|delete",
  "action_tier": "direct_do|draft_approval_ready|live_write_with_rollback|external_send|high_risk",
  "preferred_route": "connector|chrome|openclaw|osascript|codex_review",
  "missing_fields": [],
  "owner_confirmation_needed_for": "none|final_live_write|external_send|owner_override"
}
```

Execute automatically for `direct_do` and safe `draft_approval_ready` work when the target is unambiguous. For higher tiers, do all preparation first and ask for one concrete final approval instead of stopping early.

## Mac-1 / New Runtime Evaluation

Treat "Mac-1 can call 487 macOS tools" as unverified until proven by primary evidence. This blocks only production integration of that runtime; it does not block using existing MAPLAB tools to do read-only, draft, or approval-ready work. Read `references/mac-1-watchlist.md` when evaluating this claim or any similar local Mac model.

Minimum gate before production:

1. Verify primary source: official repo, model card, install docs, license, release date, and maintainer.
2. Capture a review bundle under `workbook/reviews/JOB-MAC-LOCAL-TOOLS-YYYYMMDD/`.
3. Enumerate all tools and tag each as read-only, draft, live write, external send, or high-risk.
4. Run read-only smoke tests first: app/version/status, no secret values, no external writes.
5. Run controlled write tests only on disposable files/test calendars/test sheets.
6. Add an allowlist and logging layer before Telegram/A6 can route to it.
7. Keep the local model as planner/parser unless the action executor is deterministic and auditable.

## Good Outputs

Return concise, evidence-split decisions:

- `Verified`: what was checked live or from primary sources.
- `Inference`: what seems likely but is not proven.
- `Route`: which existing MAPLAB tool should handle it now.
- `Expansion`: what must be built before A6 can use it safely.
- `Action taken`: what direct-do or draft work was completed.
- `Approval needed`: one exact final action, only when a live/external/high-risk action remains.
- `Blocker`: only after the no-permission-ping-pong check fails.
