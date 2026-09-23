#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot_a6"))

from hermes_sheets_assistant import (
    SheetsAssistantState,
    apply_sheets_customer_message,
    build_quote_shell_payload,
    confirm_intake_summary,
    customer_reply_violations,
    prepare_summary_confirmation,
)


SYNTHETIC_DIALOGUE = [
    "公司活動，需要外燴",
    "2026年10月15日",
    "14:00-17:00",
    "場地：虛構展演中心，台南市東區測試路 1 號",
    "室內",
    "60人",
    "現場外燴",
    "飲食：4位素食，1位堅果過敏",
    "3樓有貨梯，可進卸貨區，現場有人協助搬運",
]


def main() -> int:
    state = SheetsAssistantState()
    turns = []
    for index, customer_message in enumerate(SYNTHETIC_DIALOGUE, start=1):
        before_fields = set(state.fields)
        hermes_question = state.next_question()
        state = apply_sheets_customer_message(state, customer_message)
        turns.append(
            {
                "turn": index,
                "hermes_question": hermes_question,
                "question_violations": customer_reply_violations(
                    hermes_question or "", require_question=bool(hermes_question)
                ),
                "synthetic_customer": customer_message,
                "captured": sorted(set(state.fields) - before_fields),
                "remaining": state.missing_fields,
            }
        )

    state, summary = prepare_summary_confirmation(state)
    state = confirm_intake_summary(
        state,
        "資料正確",
        source_message_ref="synthetic-line-message-001",
        confirmed_at="2026-09-01T04:30:00Z",
    )
    quote_payload = build_quote_shell_payload(
        state,
        case_id="HERMES-GYM-20260826-01",
        source="line",
        client_name="虛構客戶",
        contact_ref_hash=hashlib.sha256(b"synthetic-contact").hexdigest(),
    )
    result = {
        "mode": "local_synthetic_dry_run",
        "network_calls": 0,
        "external_writes": 0,
        "turns": turns,
        "intake": {
            "fields": state.fields,
            "missing_fields": state.missing_fields,
            "intake_complete": state.intake_complete,
            "summary_confirmed": state.summary_confirmed,
            "summary": summary,
        },
        "sheets_payload_summary": {
            "action": quote_payload.get("action"),
            "event_date": quote_payload.get("eventDate"),
            "headcount": quote_payload.get("headcount"),
            "availability_status": quote_payload.get("availabilityStatus"),
            "dietary_review_status": quote_payload.get("dietaryReviewStatus"),
            "commercial_review_status": quote_payload.get("commercialReviewStatus"),
            "has_price_or_menu": bool(
                set(quote_payload)
                & {"amount", "price", "depositAmount", "menu", "items", "variants"}
            ),
        },
        "gate": "PASS" if state.intake_complete and quote_payload else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
