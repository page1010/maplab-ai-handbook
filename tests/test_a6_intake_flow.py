import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot_a6"))

from intake_flow import IntakeState, apply_customer_message, build_training_snapshot
from a5_quote_engine import build_sheet_quote_payload
from case_store import ConversationMessage, extract_case_facts


class IntakeFlowTest(unittest.TestCase):
    def test_opening_routes_to_business_category_first(self):
        state = apply_customer_message(IntakeState(), "想辦一場活動")
        snapshot = build_training_snapshot(state)
        self.assertFalse(snapshot["quote_ready"])
        self.assertEqual(snapshot["missing_fields"][0], "business_category")
        self.assertIn("哪一類服務", snapshot["next_question"])

    def test_incomplete_case_cannot_enter_quote(self):
        state = apply_customer_message(IntakeState(), "公司活動，30人")
        self.assertFalse(state.quote_ready)
        with self.assertRaisesRegex(ValueError, "quote_not_ready"):
            state.quote_request_text("GYM-001")

    def test_complete_synthetic_case_builds_traceable_quote_payload(self):
        state = IntakeState()
        messages = [
            "公司活動，需要外燴",
            "2026-09-18",
            "11:30-14:00",
            "場地：虛構會議中心，台南市東區測試路 1 號",
            "室內",
            "30人",
            "現場外燴",
            "預算3萬",
            "飲食：2位素食，無堅果過敏",
            "2樓有電梯，可臨停，現場有人協助搬運",
        ]
        for message in messages:
            state = apply_customer_message(state, message)

        self.assertTrue(state.quote_ready)
        request = state.quote_request_text("GYM-001")
        payload = build_sheet_quote_payload(request, user_name="Hermes Gym")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["base"]["eventDate"], "2026-09-18")
        self.assertEqual(payload["base"]["headcount"], 30)
        self.assertEqual(payload["base"]["caseId"], "GYM-001")
        self.assertEqual(payload["base"]["budget"], 30000)
        self.assertIn("台南市東區測試路", payload["base"]["venue"])
        self.assertIn("GYM-001", request)

    def test_no_missing_date_is_silently_replaced_with_today_at_gate(self):
        state = IntakeState(fields={key: "test" for key in (
            "business_category", "event_time", "venue", "indoor_outdoor",
            "service_format", "dietary_notes", "logistics",
        )})
        state.fields.update({"headcount": 30, "budget": 30000})
        self.assertIn("event_date", state.missing_fields)
        self.assertFalse(state.quote_ready)

    def test_dietary_count_does_not_override_headcount(self):
        state = apply_customer_message(IntakeState(), "活動共60人")
        state = apply_customer_message(state, "其中4位吃素，另有1位堅果過敏")
        self.assertEqual(state.fields["headcount"], 60)

    def test_chinese_date_is_normalized(self):
        state = apply_customer_message(IntakeState(), "活動是2026年10月15日")
        self.assertEqual(state.fields["event_date"], "2026-10-15")

    def test_case_store_keeps_total_pax_when_dietary_count_comes_later(self):
        messages = [
            ConversationMessage("m1", "", "", "", "customer", "活動共60人", "gym", "", "", 1),
            ConversationMessage("m2", "", "", "", "customer", "2026年10月15日，4位吃素", "gym", "", "", 2),
        ]
        facts = extract_case_facts(messages)
        self.assertEqual(facts["pax_hint"], 60)
        self.assertEqual(facts["event_date_hint"], "2026年10月15日")


if __name__ == "__main__":
    unittest.main()
