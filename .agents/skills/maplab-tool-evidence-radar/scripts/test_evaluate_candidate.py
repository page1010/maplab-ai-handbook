#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from evaluate_candidate import ContractError, evaluate


def base_candidate() -> dict:
    return {
        "candidate_id": "local-helper",
        "kind": "tool",
        "identity": {"status": "upstream_verified", "url": "https://github.com/example/local-helper"},
        "license": {"status": "verified_open", "id": "MIT"},
        "maintenance": "active",
        "fit": "high",
        "overlap": "none",
        "runtime": {"ready": True, "smoke": "passed"},
        "data": {"max_allowed": "public", "egress": "none"},
        "credentials": ["none"],
        "side_effects": ["local_files"],
        "evidence": {
            "social_url": "https://www.instagram.com/example/",
            "official_urls": ["https://github.com/example/local-helper"],
            "checked_at": "2026-08-27",
        },
        "note": "fixture",
    }


class EvaluateCandidateTest(unittest.TestCase):
    def test_adopt_requires_local_readiness_and_smoke(self) -> None:
        self.assertEqual(evaluate(base_candidate())["decision"], "ADOPT")

    def test_social_only_is_rejected(self) -> None:
        candidate = base_candidate()
        candidate["identity"] = {"status": "social_only", "url": "https://www.instagram.com/example/"}
        candidate["evidence"]["official_urls"] = []
        self.assertEqual(evaluate(candidate)["decision"], "REJECT")

    def test_external_oauth_tool_is_pilot(self) -> None:
        candidate = base_candidate()
        candidate["data"]["egress"] = "external_service"
        candidate["credentials"] = ["oauth"]
        candidate["runtime"] = {"ready": False, "smoke": "not_run"}
        self.assertEqual(evaluate(candidate)["decision"], "PILOT")

    def test_security_scan_is_hold(self) -> None:
        candidate = base_candidate()
        candidate["side_effects"] = ["security_scan", "network_read"]
        self.assertEqual(evaluate(candidate)["decision"], "HOLD")

    def test_duplicate_is_rejected_before_pilot(self) -> None:
        candidate = base_candidate()
        candidate["overlap"] = "duplicate"
        candidate["credentials"] = ["oauth"]
        candidate["data"]["egress"] = "external_service"
        self.assertEqual(evaluate(candidate)["decision"], "REJECT")

    def test_reference_is_not_a_tool(self) -> None:
        candidate = base_candidate()
        candidate["kind"] = "reference"
        self.assertEqual(evaluate(candidate)["decision"], "NOT_A_TOOL")

    def test_missing_license_is_hold(self) -> None:
        candidate = base_candidate()
        candidate["license"] = {"status": "missing", "id": None}
        self.assertEqual(evaluate(candidate)["decision"], "HOLD")

    def test_none_cannot_mix_with_real_credential(self) -> None:
        candidate = copy.deepcopy(base_candidate())
        candidate["credentials"] = ["none", "oauth"]
        with self.assertRaises(ContractError):
            evaluate(candidate)

    def test_checked_at_must_be_iso_date(self) -> None:
        candidate = base_candidate()
        candidate["evidence"]["checked_at"] = "27-08-2026"
        with self.assertRaises(ContractError):
            evaluate(candidate)

    def test_paid_external_generation_requires_data_and_cost_gates(self) -> None:
        candidate = base_candidate()
        candidate["kind"] = "service"
        candidate["runtime"] = {"ready": False, "smoke": "not_run"}
        candidate["data"] = {"max_allowed": "synthetic", "egress": "external_service"}
        candidate["credentials"] = ["oauth"]
        candidate["side_effects"] = ["external_write", "paid_generation"]
        result = evaluate(candidate)
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("synthetic_or_public_fixture", result["required_gates"])
        self.assertIn("explicit_cost_approval", result["required_gates"])

    def test_runtime_ready_rejects_truthy_string(self) -> None:
        candidate = base_candidate()
        candidate["runtime"]["ready"] = "false"
        with self.assertRaises(ContractError):
            evaluate(candidate)

    def test_public_only_egress_rejects_private_data_class(self) -> None:
        candidate = base_candidate()
        candidate["data"] = {"max_allowed": "private", "egress": "public_only"}
        with self.assertRaises(ContractError):
            evaluate(candidate)

    def test_external_service_rejects_private_data_class(self) -> None:
        candidate = base_candidate()
        candidate["data"] = {"max_allowed": "private", "egress": "external_service"}
        with self.assertRaises(ContractError):
            evaluate(candidate)

    def test_substantial_overlap_cannot_be_adopted_without_unique_value_proof(self) -> None:
        candidate = base_candidate()
        candidate["overlap"] = "substantial"
        result = evaluate(candidate)
        self.assertEqual(result["decision"], "PILOT")
        self.assertIn("document_unique_capability", result["required_gates"])


if __name__ == "__main__":
    unittest.main()
