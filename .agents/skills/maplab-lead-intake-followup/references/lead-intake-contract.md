# Lead intake output contract

Return a machine-readable object or the same fields in a compact review table. Values shown here are synthetic.

```json
{
  "case_id": null,
  "source": "dm",
  "source_thread_id": "synthetic-thread-001",
  "source_message_id": "synthetic-message-001",
  "received_at": "2026-08-27T09:00:00+08:00",
  "dedupe_status": "unverified",
  "matched_case_id": null,
  "known_fields": {
    "business_category": "外燴",
    "headcount": 30
  },
  "missing_fields": [
    "event_date",
    "event_time",
    "venue",
    "indoor_outdoor",
    "service_format",
    "budget",
    "dietary_notes",
    "logistics"
  ],
  "next_question": "活動預計是哪一天？請提供西元年月日。",
  "quote_ready": false,
  "route": "A7_CLARIFY",
  "followup_state": "not_due",
  "customer_reply_state": "draft_only",
  "human_gate": "required",
  "evidence": []
}
```

## Allowed dedupe results

- `matched`: an exact approved key maps to an existing case; reuse it.
- `new_verified`: the canonical store was checked and no match exists; a new case may be proposed or created within task authority.
- `unverified`: the canonical store was not readable or evidence was insufficient; do not create or claim a unique canonical case.
- `conflict`: multiple records or keys disagree; route for review and do not merge automatically.

## Route values

- `A7_CLARIFY`: one or more required intake facts are missing.
- `A6_URGENT_REVIEW`: urgency or exception evidence requires human triage.
- `A6_TO_A5_DRAFT`: all ten fields are explicit and the internal quote-draft handoff is allowed.
- `OWNER_REVIEW`: B2B, VIP, complaint, policy conflict, opt-out, or another exception.
- `CLOSED_NO_ACTION`: the case is closed, duplicate, opted out, or otherwise suppressed with evidence.

Do not treat route values as permission to send a message, change pricing, write a formal quote, or update a live system.
