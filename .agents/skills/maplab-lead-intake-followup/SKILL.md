---
name: maplab-lead-intake-followup
description: Normalize MAPLAB leads from forms, LINE, DMs, or price questions; deduplicate them against existing cases; extract explicit intake facts; determine quote readiness; route A7 to A6/A5/Owner; and prepare human-reviewed follow-up drafts and receipts. Use for lead intake, 漏單 checks, 詢價整理, quote-ready gating, or follow-up queues. Do not create a second CRM, calculate prices, modify quote truth, or send customer messages automatically.
---

# MAPLAB Lead Intake + Follow-up

Turn every inbound lead into one traceable case decision while preserving the existing MAPLAB single source of truth.

## Canonical sources

Read the current versions before acting:

1. `docs/a6-a7-customer-to-quote-gym-sop.md` — authoritative ten-field intake order and quote-ready gate.
2. `bot_a6/intake_flow.py` — authoritative deterministic explicit-fact extraction and next-question behavior.
3. `skills/a7-customer-service-skills.md` — intent, escalation, customer tone, and follow-up patterns only; its old five-field readiness rule is superseded.
4. `skills/a6-rapid-quote-sop.md` — A6/A5 role and approval boundary only; its old two-required-field readiness rule is superseded.
5. `docs/a6-reply-closed-loop-mvp-design.md` — PII, correction, and human-send controls.

Quote readiness always follows sources 1 and 2. For any other disagreement, do not silently choose: report the exact conflict and use the newest task-approved source for a proposal-only result.

## Workflow

### 1. Normalize the source

Accept form submissions, LINE messages, DMs, or direct price questions. Record the source, source thread ID, source message ID, received time, and a protected reference to the original message. Do not copy raw PII into a public artifact or model prompt.

### 2. Resolve duplicates before creating anything

Look for an exact source message ID, source thread ID, existing `case_id`, or another approved canonical key. Reuse the existing case when found. If the canonical store cannot be read, set `dedupe_status=unverified`; do not claim a new canonical case or write a duplicate row.

### 3. Extract explicit facts only

Use the canonical order:

1. `business_category`
2. `event_date`
3. `event_time`
4. `venue`
5. `indoor_outdoor`
6. `headcount`
7. `service_format`
8. `budget`
9. `dietary_notes`
10. `logistics`

Never replace a missing event date with today. Never treat a dietary, staff, or搬運人數 as total headcount. Never invent a venue, availability, menu, price, or service promise.

### 4. Apply the quote-ready gate

All ten categories must be explicit before `quote_ready=true`. When incomplete, return known fields, missing fields, and only the next missing question; on mobile, at most three tightly related questions may be combined. Do not call A5 yet.

When complete, A6 may produce a traceable request with a `case_id`; A5 may produce an internal draft only. A human must approve the official Sheet, amount, terms, availability, and customer send.

### 5. Route the case

- A7: intent, clarification, tone, and customer-safe draft.
- A6: structured case, urgency, `case_id`, and quote handoff.
- A5: quote truth and internal draft after the gate passes.
- Owner/Mina: B2B, VIP, complaint, exception, policy conflict, final approval, and external send.

Do not reopen or overwrite a closed case without explicit evidence and authorization.

### 6. Prepare follow-up, never auto-send

Read the current case status, last contact, prior quote state, and opt-out/closure evidence. Draft the next message using the current A7 template and brand tone. Mark it `DRAFT — HUMAN REVIEW REQUIRED`; do not schedule or send it. Suppress follow-up for opted-out, closed, duplicate, or unresolved-conflict cases.

### 7. Return the contract

Use [references/lead-intake-contract.md](references/lead-intake-contract.md). At minimum include `case_id`, source keys, `dedupe_status`, explicit known fields, missing fields, next question, `quote_ready`, route, follow-up state, human gate, and evidence paths.

## Privacy and model route

Customer messages, names, phones, addresses, quote details, and order context are private. Keep originals in approved local or authenticated stores. Do not send them to DeerFlow, OpenRouter free models, public web tools, or logs. If model help is needed, use an approved protected route or a synthetic/redacted case whose context cannot be reidentified.

## Verification

For changes to deterministic intake behavior, run from the repo root:

```bash
python3 -m unittest tests.test_a6_intake_flow
python3 .agents/skills/maplab-lead-intake-followup/scripts/lead_contract_smoke.py
```

Add a regression test for each fixed intake error. Verify that an incomplete case cannot reach A5, dietary counts do not overwrite headcount, duplicate resolution is explicit, no network call or customer send occurs, and output contains a durable receipt.

Chat output alone is not completion. Write a task-scoped receipt with the input class, source keys, dedupe result, case decision, missing-data gate, route, draft/send state, test result, and next bounded action.
