import hashlib
import hmac
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot_a6"))

from hermes_sheets_assistant import (  # noqa: E402
    AWAITING_SUMMARY_CONFIRMATION,
    SheetsAssistantState,
    apply_sheets_customer_message,
    apply_survey_response,
    build_quote_shell_payload,
    build_revision_request_payload,
    build_signed_request_envelope,
    compose_intake_reply,
    confirm_intake_summary,
    customer_reply_violations,
    dispatch_flow_event,
    load_contract,
    prepare_summary_confirmation,
    render_sheet_handoff_acknowledgement,
    render_summary_confirmation,
    route_customer_quote_response,
    route_no_reply,
    validate_quote_shell_payload,
    validate_revision_request_payload,
)


COMPLETE_FIELDS = {
    "business_category": "外燴",
    "event_date": "2026-10-15",
    "event_time": "14:00-17:00",
    "venue": "虛構展演中心，台南市東區測試路 1 號",
    "indoor_outdoor": "室內",
    "headcount": 60,
    "service_format": "現場外燴",
    "dietary_notes": "4位素食，1位堅果過敏",
    "logistics": "3樓有貨梯，可臨停",
}
HASH_ONLY = "a" * 64


def complete_state() -> SheetsAssistantState:
    return SheetsAssistantState(fields=dict(COMPLETE_FIELDS))


def confirmed_state() -> SheetsAssistantState:
    awaiting, _ = prepare_summary_confirmation(complete_state())
    return confirm_intake_summary(
        awaiting,
        "資料正確",
        source_message_ref="synthetic-line-message-001",
        confirmed_at="2026-09-01T04:30:00Z",
    )


class HermesSheetsAssistantTest(unittest.TestCase):
    def test_contract_is_connected_and_deployment_stays_blocked(self):
        contract = load_contract()
        template_ids = {item["id"] for item in contract["templates"]}
        for route in contract["flow_routes"]:
            self.assertIn(route["template_id"], template_ids)
        self.assertEqual(contract["customer_reply_contract"]["max_questions_per_reply"], 1)
        self.assertTrue(contract["deployment_gate"].startswith("BLOCKED_"))
        self.assertEqual(
            contract["transport_contract"]["allowed_actions"],
            ["createQuoteShell", "appendQuoteRevisionRequest"],
        )

    def test_each_turn_asks_one_next_missing_field_without_inference(self):
        state, reply = compose_intake_reply(SheetsAssistantState(), "公司活動")
        self.assertEqual(state.missing_fields[0], "business_category")
        self.assertNotIn("business_category", state.fields)
        self.assertEqual(reply.count("？") + reply.count("?"), 1)

        state, reply = compose_intake_reply(state, "需要外燴")
        self.assertEqual(state.fields["business_category"], "外燴")
        self.assertIn("哪一天", reply)

    def test_bare_no_is_stage_bound_and_never_fills_dietary_early(self):
        state = apply_sheets_customer_message(SheetsAssistantState(), "外燴")
        state = apply_sheets_customer_message(state, "沒有")
        self.assertNotIn("dietary_notes", state.fields)
        self.assertEqual(state.missing_fields[0], "event_date")

        dietary_pending = SheetsAssistantState(
            fields={key: value for key, value in COMPLETE_FIELDS.items() if key != "dietary_notes"}
        )
        updated = apply_sheets_customer_message(dietary_pending, "沒有")
        self.assertEqual(updated.fields["dietary_notes"], "無")

    def test_survey_rejects_empty_invalid_date_and_bad_headcount(self):
        bad_values = (
            ("venue", "   "),
            ("event_date", "2026-02-31"),
            ("headcount", 1.5),
            ("headcount", 5001),
        )
        for key, value in bad_values:
            with self.subTest(key=key, value=value):
                with self.assertRaisesRegex(ValueError, f"invalid_survey_field:{key}"):
                    apply_survey_response(SheetsAssistantState(), {key: value})

    def test_budget_is_capture_only_and_never_required_or_forwarded(self):
        state = apply_sheets_customer_message(SheetsAssistantState(), "預算3萬")
        self.assertEqual(state.fields["customer_budget_verbatim"], "預算3萬")
        self.assertNotIn("budget", state.missing_fields)
        payload = build_quote_shell_payload(
            confirmed_state(),
            case_id="CASE-SYNTHETIC-001",
            source="line",
        )
        self.assertNotIn("customer_budget_verbatim", payload)

    def test_summary_confirmation_is_stage_and_digest_bound(self):
        state = complete_state()
        with self.assertRaisesRegex(ValueError, "summary_confirmation_wrong_stage"):
            confirm_intake_summary(state, "是的", source_message_ref="msg-1")

        awaiting, summary = prepare_summary_confirmation(state)
        self.assertIn("需求類別：外燴", summary)
        self.assertEqual(awaiting.stage, AWAITING_SUMMARY_CONFIRMATION)
        confirmed = confirm_intake_summary(
            awaiting,
            "資料正確",
            source_message_ref="msg-2",
            confirmed_at="2026-09-01T04:30:00Z",
        )
        self.assertTrue(confirmed.summary_confirmed)
        self.assertEqual(
            confirmed.confirmation_receipt.summary_digest,
            hashlib.sha256(summary.encode()).hexdigest(),
        )

        stale = SheetsAssistantState(
            fields={**awaiting.fields, "headcount": 61},
            stage=AWAITING_SUMMARY_CONFIRMATION,
            pending_summary_digest=awaiting.pending_summary_digest,
        )
        with self.assertRaisesRegex(ValueError, "summary_digest_stale"):
            confirm_intake_summary(stale, "資料正確", source_message_ref="msg-3")

    def test_owner_and_redteam_negative_copy_has_specific_violation(self):
        fixtures = {
            "沒問題，總價就是 99,999 元，我已替你保留檔期，不用再提供資料。": {
                "money_or_terms_commitment",
                "availability_commitment",
                "no_more_confirmation",
            },
            "所有人都可以吃，沒有任何飲食限制，不必再確認。": {
                "dietary_safety_claim",
                "no_more_confirmation",
            },
            "報價固定是 88,888 元，檔期一定有空，直接下訂就可以。": {
                "money_or_terms_commitment",
                "availability_commitment",
                "booking_commitment",
            },
            "總價就是三萬元。": {"money_or_terms_commitment"},
            "這次免費，不用訂金。": {"money_or_terms_commitment"},
            "我們可以接這場，已為您登記完成。": {
                "availability_commitment",
                "booking_commitment",
            },
            "這道不含堅果，可以放心食用。": {"dietary_safety_claim"},
            "訂單已成立。": {"booking_commitment"},
            "我已把那天留起來。": {"availability_commitment"},
            "日期哪一天、時間幾點？": {"multiple_requested_fields"},
        }
        for copy, expected_codes in fixtures.items():
            with self.subTest(copy=copy):
                self.assertTrue(expected_codes.issubset(set(customer_reply_violations(copy))))

    def test_quote_shell_payload_is_noncommercial_and_receipted(self):
        payload = build_quote_shell_payload(
            confirmed_state(),
            case_id="CASE-SYNTHETIC-002",
            source="line",
            client_name="測試客戶",
            contact_ref_hash=HASH_ONLY,
        )
        contract = load_contract()["sheets_handoff"]
        self.assertEqual(set(payload), set(contract["allowed_payload_keys"]))
        self.assertFalse(set(payload) & set(contract["forbidden_payload_keys"]))
        self.assertTrue(payload["summaryConfirmed"])
        self.assertEqual(
            hashlib.sha256(payload["summaryText"].encode()).hexdigest(),
            payload["summaryDigest"],
        )
        self.assertNotIn("price", json.dumps(payload, ensure_ascii=False).lower())
        self.assertNotIn("menu", json.dumps(payload, ensure_ascii=False).lower())

    def test_quote_shell_rejects_missing_receipt_invalid_source_and_formula_field_is_signed(self):
        with self.assertRaisesRegex(ValueError, "explicit_summary_confirmation_required"):
            build_quote_shell_payload(
                complete_state(), case_id="CASE-SYNTHETIC-003", source="line"
            )
        with self.assertRaisesRegex(ValueError, "source_must_be_line"):
            build_quote_shell_payload(
                confirmed_state(), case_id="CASE-SYNTHETIC-003", source="telegram"
            )
        payload = build_quote_shell_payload(
            confirmed_state(),
            case_id="CASE-SYNTHETIC-003",
            source="line",
        )
        payload["venue"] = "=IMPORTRANGE(\"x\",\"A1\")"
        # The transport signs the exact customer text; the server stores it as
        # a literal. It must never be executed as a formula.
        envelope = build_signed_request_envelope(
            payload,
            secret="s" * 32,
            issued_at=1788249600,
            nonce="nonce_1234567890abcd",
        )
        self.assertIn("IMPORTRANGE", envelope["signedPayload"])

    def test_revision_request_is_verbatim_and_server_owns_revision_number(self):
        payload = build_revision_request_payload(
            case_id="CASE-SYNTHETIC-004",
            quote_id="quoteSynthetic001",
            customer_change_verbatim="希望甜點少一點，鹹食多一點",
            contact_ref_hash=HASH_ONLY,
        )
        self.assertEqual(payload["changeStatus"], "PENDING_MINA")
        self.assertNotIn("revisionNo", payload)
        self.assertEqual(
            payload["changeDigest"],
            hashlib.sha256(payload["customerChangeVerbatim"].encode()).hexdigest(),
        )
        payload["newPrice"] = 123
        with self.assertRaisesRegex(ValueError, "unsafe_revision_payload"):
            validate_revision_request_payload(payload)

    def test_signed_envelope_matches_documented_hmac_message(self):
        payload = build_revision_request_payload(
            case_id="CASE-SYNTHETIC-005",
            quote_id="quoteSynthetic002",
            customer_change_verbatim="希望改成較簡潔的服務形式",
        )
        envelope = build_signed_request_envelope(
            payload,
            secret="secret-value-for-test-only-123456",
            issued_at=1788249600,
            nonce="nonce_abcdefghijklmnop",
        )
        message = "\n".join(
            [
                envelope["authVersion"],
                envelope["actor"],
                str(envelope["issuedAt"]),
                envelope["nonce"],
                envelope["action"],
                envelope["signedPayload"],
            ]
        )
        expected = hmac.new(
            b"secret-value-for-test-only-123456",
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        self.assertTrue(hmac.compare_digest(expected, envelope["signature"]))
        with self.assertRaisesRegex(ValueError, "action_not_allowed"):
            build_signed_request_envelope(
                {"action": "createQuote"},
                secret="s" * 32,
                issued_at=1788249600,
                nonce="nonce_abcdefghijklmnop",
            )

    def test_executable_flow_waits_for_customer_detail_and_human_decision(self):
        self.assertEqual(route_no_reply(reminder_already_sent=False), "FOLLOWUP_ONCE")
        self.assertEqual(route_no_reply(reminder_already_sent=True), "WAITING_PAUSED")
        expected = {
            "yes": "NEEDS_MINA_CONFIRMATION",
            "no": "WAITING_CLOSE_REASON",
            "adjustment": "WAITING_REVISION_DETAIL",
            "no_reply": "WAITING_QUOTE",
        }
        for response_type, next_state in expected.items():
            self.assertEqual(route_customer_quote_response(response_type), next_state)

        adjustment = dispatch_flow_event(complete_state(), "quote_adjustment")
        self.assertEqual(adjustment["next"], "WAITING_REVISION_DETAIL")
        no = dispatch_flow_event(complete_state(), "quote_no")
        self.assertEqual(no["next"], "WAITING_CLOSE_REASON")

    def test_all_template_copy_is_one_question_and_noncommercial(self):
        contract = load_contract()
        next_question = contract["field_questions"]["event_date"]
        for template in contract["templates"]:
            reply = template["customer_facing"].replace(
                "{next_missing_question}", next_question
            )
            with self.subTest(template=template["id"]):
                self.assertLessEqual(reply.count("？") + reply.count("?"), 1)
                self.assertEqual(customer_reply_violations(reply), [])

    def test_sheet_handoff_copy_is_quiet_and_mina_owned(self):
        reply = render_sheet_handoff_acknowledgement()
        self.assertIn("Mina", reply)
        self.assertIn("內部需求單", reply)
        self.assertNotIn("完成", reply)
        self.assertEqual(customer_reply_violations(reply), [])

    def test_isolated_gas_is_two_action_signed_and_sterile(self):
        gas_dir = ROOT / "scripts" / "apps-script-hermes-sheets"
        code = (gas_dir / "Code.gs").read_text(encoding="utf-8")
        manifest = json.loads((gas_dir / "appsscript.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["webapp"]["access"], "ANYONE_ANONYMOUS")
        for required in (
            "verifySignedEnvelope_",
            "TIMESTAMP_OUTSIDE_WINDOW",
            "NONCE_REPLAYED",
            "ACTION_BINDING_MISMATCH",
            "LockService.getScriptLock()",
            "SpreadsheetApp.create(",
            "safeCellLiteral_",
            "CASE_QUOTE_BINDING_NOT_FOUND",
            "setTrashed(true)",
            "CLEAN_SHEET_FORMULA_FOUND",
        ):
            self.assertIn(required, code)
        for forbidden in (
            ".makeCopy(",
            "createQuoteVariants",
            "addItemToDatabase",
            "default_price",
            "default_cost",
            "revisionNo: body.revisionNo",
        ):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()
