from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_rubric_annotation_guide.py"
SPEC = importlib.util.spec_from_file_location("hermes_line_rubric_annotation_guide", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def source_bindings() -> dict[str, dict[str, str]]:
    bindings = copy.deepcopy(MODULE.EXPECTED_SOURCE_HASHES)
    bindings["private_blank_preflight"] = {
        "artifact_id": "rubric_v2_annotation_guide_preflight_v1",
        "sha256": MODULE.EXPECTED_PRIVATE_PREFLIGHT_SHA256,
        "authority": "IMMUTABLE_PRIVATE_PARENT_20_BLANK_SLOTS",
    }
    return bindings


def transitionable_job() -> dict[str, object]:
    job = json.loads(
        (
            ROOT
            / "workbook"
            / "reviews"
            / "MAPLAB-DURABLE-JOBS"
            / MODULE.JOB_ID
            / "job.json"
        ).read_text(encoding="utf-8")
    )
    if job["state"] == "OWNER_REVIEW":
        job["state"] = "RUNNING"
        job["deerflow_view"]["state"] = "RUNNING"
        job["current_phase"] = "method-redesign-rubric-annotation-guide"
        job["last_result"]["execution_eligible"] = False
        blockers = set(job["last_result"].get("execution_blockers", []))
        blockers.update(
            {
                "rubric_v2_structured_human_labels_missing",
                "rubric_v2_annotation_guide_not_frozen",
                "rubric_v2_criterion_coverage_not_proven",
            }
        )
        job["last_result"]["execution_blockers"] = sorted(blockers)
        job["artifacts"] = [
            item
            for item in job["artifacts"]
            if item.get("kind")
            not in {
                "line-rubric-v2-annotation-guide",
                "line-rubric-v2-annotation-guide-receipt",
            }
        ]
    return job


class AnnotationGuideTests(unittest.TestCase):
    def setUp(self) -> None:
        self.created_at = "2026-08-30T00:00:00Z"
        self.guide = MODULE.build_guide(self.created_at, source_bindings())

    def test_reference_guide_validates_and_has_exact_coverage(self) -> None:
        MODULE.validate_guide(self.guide)
        fixtures = self.guide["synthetic_public_fixtures"]
        self.assertEqual(len(fixtures), 14)
        for criterion in MODULE.CRITERIA:
            targeted = [
                item for item in fixtures if item["target_criterion"] == criterion
            ]
            self.assertEqual(
                {(item["target_polarity"], item["expected_labels"][criterion]) for item in targeted},
                {("POSITIVE", "PASS"), ("NEGATIVE", "FAIL")},
            )

    def test_missing_rule_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        poisoned["criteria"]["facts_are_grounded"]["fail_when"] = []
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "guide_rule_incomplete"):
            MODULE.validate_guide(poisoned)

    def test_missing_or_duplicate_coverage_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        poisoned["synthetic_public_fixtures"][-1] = copy.deepcopy(
            poisoned["synthetic_public_fixtures"][-2]
        )
        poisoned["synthetic_public_fixtures"][-1]["fixture_id"] = "duplicate-target"
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "guide_fixture_coverage_invalid"):
            MODULE.validate_guide(poisoned)

    def test_unknown_label_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        poisoned["synthetic_public_fixtures"][0]["expected_labels"][
            "mobile_readable"
        ] = "UNKNOWN"
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "fixture_label_value_invalid"):
            MODULE.validate_guide(poisoned)

    def test_overall_is_recomputed_not_trusted(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        poisoned["synthetic_public_fixtures"][1]["expected_overall_pass"] = True
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "guide_fixture_overall_invalid"):
            MODULE.validate_guide(poisoned)

    def test_unsupported_commercial_negative_must_be_unsafe(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        target = next(
            item
            for item in poisoned["synthetic_public_fixtures"]
            if item["target_criterion"]
            == "price_policy_availability_are_grounded"
            and item["target_polarity"] == "NEGATIVE"
        )
        target["unsafe_claim"] = False
        target["expected_overall_pass"] = False
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "commercial_negative_not_unsafe"):
            MODULE.validate_guide(poisoned)

    def test_authority_snapshot_cannot_claim_unverified_live_values(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        snapshot = poisoned["current_commercial_authority_snapshot"]
        snapshot["live_readback_performed"] = True
        body = dict(snapshot)
        body.pop("snapshot_body_sha256")
        snapshot["snapshot_body_sha256"] = MODULE.sha256_text(MODULE.canonical_json(body))
        poisoned["current_commercial_authority_snapshot_sha256"] = MODULE.sha256_text(
            MODULE.canonical_json(snapshot)
        )
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "snapshot_not_fail_closed"):
            MODULE.validate_guide(poisoned)

    def test_scorer_blinding_contract_is_exact(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        poisoned["identity_blind_scorer_contract"]["allowed_inputs"].append(
            "expected_labels"
        )
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "scorer_allowed_inputs_invalid"):
            MODULE.validate_guide(poisoned)

    def test_named_human_attestation_and_adjudication_are_required(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        poisoned["human_annotation_contract"]["reviewer_is_human_required"] = False
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "human_attestation_invalid"):
            MODULE.validate_guide(poisoned)
        poisoned = copy.deepcopy(self.guide)
        poisoned["human_annotation_contract"]["adjudication"][
            "adjudicator_must_be_named_human"
        ] = False
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "adjudication_invalid"):
            MODULE.validate_guide(poisoned)

    def test_public_private_path_marker_is_rejected(self) -> None:
        poisoned = copy.deepcopy(self.guide)
        poisoned["purpose"] = "/Users/private/customer.json"
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "private_marker_present"):
            MODULE.validate_guide(poisoned)

    def test_receipt_binds_guide_implementation_and_zero_egress(self) -> None:
        MODULE.validate_guide(self.guide)
        guide_sha = MODULE.json_file_sha256(self.guide)
        receipt = MODULE.build_receipt(
            created_at=self.created_at,
            guide=self.guide,
            guide_sha256=guide_sha,
            job_preimage_sha256="a" * 64,
            script_sha256="b" * 64,
            test_sha256="c" * 64,
        )
        MODULE.validate_receipt(
            receipt,
            guide=self.guide,
            guide_sha256=guide_sha,
            script_sha256="b" * 64,
            test_sha256="c" * 64,
        )
        poisoned = copy.deepcopy(receipt)
        poisoned["external_network_calls"] = 1
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "receipt_verification_invalid"):
            MODULE.validate_receipt(
                poisoned,
                guide=self.guide,
                guide_sha256=guide_sha,
                script_sha256="b" * 64,
                test_sha256="c" * 64,
            )

    def test_job_transition_preserves_attempt_and_closes_execution(self) -> None:
        job = transitionable_job()
        transitioned = MODULE.transition_job(
            job,
            transitioned_at=self.created_at,
            guide_path=MODULE.DEFAULT_GUIDE_PATH,
            guide_sha256="d" * 64,
            receipt_path=MODULE.DEFAULT_RECEIPT_PATH,
            receipt_sha256="e" * 64,
            authority_sha256="f" * 64,
        )
        self.assertEqual(transitioned["state"], "OWNER_REVIEW")
        self.assertEqual(transitioned["attempt"], MODULE.EXPECTED_ATTEMPT)
        self.assertFalse(transitioned["last_result"]["execution_eligible"])
        self.assertTrue(transitioned["last_result"]["owner_action_required"])
        self.assertNotIn(
            "rubric_v2_annotation_guide_not_frozen",
            transitioned["last_result"]["execution_blockers"],
        )

    def test_job_transition_rejects_wrong_identity_or_phase(self) -> None:
        job = transitionable_job()
        job["job_id"] = "wrong"
        with self.assertRaisesRegex(MODULE.AnnotationGuideError, "job_transition_precondition_invalid"):
            MODULE.transition_job(
                job,
                transitioned_at=self.created_at,
                guide_path=MODULE.DEFAULT_GUIDE_PATH,
                guide_sha256="d" * 64,
                receipt_path=MODULE.DEFAULT_RECEIPT_PATH,
                receipt_sha256="e" * 64,
                authority_sha256="f" * 64,
            )


if __name__ == "__main__":
    unittest.main()
