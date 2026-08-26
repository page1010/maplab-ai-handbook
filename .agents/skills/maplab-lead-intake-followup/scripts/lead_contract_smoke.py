#!/usr/bin/env python3
"""Offline synthetic smoke for the MAPLAB lead-intake Skill contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "bot_a6"))

from intake_flow import IntakeState, apply_customer_message, build_training_snapshot


def main() -> int:
    state = apply_customer_message(IntakeState(), "想問30人外燴多少錢")
    snapshot = build_training_snapshot(state)
    contract = {
        "case_id": None,
        "source": "dm",
        "source_thread_id": "synthetic-thread-001",
        "source_message_id": "synthetic-message-001",
        "dedupe_status": "unverified",
        "matched_case_id": None,
        "known_fields": snapshot["fields"],
        "missing_fields": snapshot["missing_fields"],
        "next_question": snapshot["next_question"],
        "quote_ready": snapshot["quote_ready"],
        "route": "A7_CLARIFY",
        "customer_reply_state": "draft_only",
        "human_gate": "required",
        "side_effects": [],
    }

    assert contract["known_fields"] == {"business_category": "外燴", "headcount": 30}
    assert len(contract["missing_fields"]) == 8
    assert contract["missing_fields"][0] == "event_date"
    assert contract["next_question"] == "活動預計是哪一天？請提供西元年月日。"
    assert contract["quote_ready"] is False
    assert contract["case_id"] is None
    assert contract["dedupe_status"] == "unverified"
    assert contract["customer_reply_state"] == "draft_only"
    assert contract["human_gate"] == "required"
    assert contract["side_effects"] == []

    print(json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

