#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot_a6"))

from a5_quote_engine import build_sheet_quote_payload
from intake_flow import IntakeState, apply_customer_message, build_training_snapshot


SYNTHETIC_DIALOGUE = [
    "公司活動，需要外燴",
    "2026年10月15日",
    "14:00-17:00",
    "場地：虛構展演中心，台南市東區測試路 1 號",
    "室內",
    "60人",
    "現場外燴",
    "預算5萬",
    "飲食：4位素食，1位堅果過敏",
    "3樓有貨梯，可進卸貨區，現場有人協助搬運",
]


def main() -> int:
    state = IntakeState()
    turns = []
    for index, customer_message in enumerate(SYNTHETIC_DIALOGUE, start=1):
        before = build_training_snapshot(state)
        state = apply_customer_message(state, customer_message)
        after = build_training_snapshot(state)
        turns.append(
            {
                "turn": index,
                "hermes_question": before["next_question"],
                "synthetic_customer": customer_message,
                "captured": sorted(set(after["fields"]) - set(before["fields"])),
                "remaining": after["missing_fields"],
            }
        )

    request = state.quote_request_text("HERMES-GYM-20260826-01")
    quote_payload = build_sheet_quote_payload(request, user_name="Hermes Gym")
    result = {
        "mode": "local_synthetic_dry_run",
        "network_calls": 0,
        "external_writes": 0,
        "turns": turns,
        "intake": build_training_snapshot(state),
        "quote_request": request,
        "quote_payload_summary": {
            "action": quote_payload.get("action") if quote_payload else None,
            "event_date": quote_payload.get("base", {}).get("eventDate") if quote_payload else None,
            "headcount": quote_payload.get("base", {}).get("headcount") if quote_payload else None,
            "variant_count": len(quote_payload.get("variants", [])) if quote_payload else 0,
        },
        "gate": "PASS" if state.quote_ready and quote_payload else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
