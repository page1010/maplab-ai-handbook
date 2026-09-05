from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_human_annotation_validator.py"
SPEC = importlib.util.spec_from_file_location("hermes_line_human_annotation_validator", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _case_hash(index: int) -> str:
    return hashlib.sha256(f"synthetic-case-{index}".encode()).hexdigest()


class HumanAnnotationValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.guide_path = self.root / "guide.json"
        self.preflight_path = self.root / "preflight.json"
        self.annotations_path = self.root / "annotations.json"

        self.guide = {
            "schema_version": MODULE.GUIDE_SCHEMA,
            "created_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat().replace("+00:00", "Z"),
            "criteria_order": list(MODULE.CRITERIA_ORDER),
            "current_commercial_authority_snapshot_sha256": "a" * 64,
            "data_boundary": {
                "guide_contains_private_line_content": False,
                "guide_contains_customer_identifiers": False,
                "private_preflight_must_remain_immutable": True,
                "annotations_must_be_written_to_separate_private_file": True,
                "model_or_third_party_annotation_allowed": False,
            },
            "human_annotation_contract": {
                "schema_version": MODULE.ANNOTATION_SCHEMA,
                "output_location": "separate owner-only 0600 file",
                "reviewer_is_human_required": True,
                "independent_review_attestation_required": True,
                "all_20_case_hashes_exactly_once": True,
                "overall_must_be_recomputed": True,
                "ai_or_synthetic_labels_count_as_human_gold": False,
                "required_parent_bindings": [
                    "private_preflight_sha256",
                    "annotation_guide_sha256",
                    "commercial_authority_snapshot_sha256",
                ],
                "reviewer_required_fields": [
                    "reviewer_id",
                    "reviewer_name",
                    "reviewer_role",
                    "is_human",
                    "reviewed_at_utc",
                    "independent_review_attestation",
                ],
                "case_required_fields": [
                    "case_hash",
                    "criteria",
                    "unsafe_claim",
                    "overall_pass",
                    "rationale",
                    "evidence_refs",
                ],
            },
            "execution_gate": {
                "annotation_may_start_after_this_guide": True,
                "scorer_calibration_may_start": False,
                "render_or_e1_may_start": False,
                "customer_send_allowed": False,
            },
        }
        self.preflight = {
            "schema_version": MODULE.PREFLIGHT_SCHEMA,
            "cases": [{"case_hash": _case_hash(index)} for index in range(20)],
        }
        self._write_json(self.guide_path, self.guide, private=False)
        self._write_json(self.preflight_path, self.preflight, private=True)
        self.guide_sha = MODULE.sha256_file(self.guide_path)
        self.preflight_sha = MODULE.sha256_file(self.preflight_path)

        self.annotations = {
            "schema_version": MODULE.ANNOTATION_SCHEMA,
            "parent_bindings": {
                "private_preflight_sha256": self.preflight_sha,
                "annotation_guide_sha256": self.guide_sha,
                "commercial_authority_snapshot_sha256": "a" * 64,
            },
            "reviewer": {
                "reviewer_id": "reviewer-01",
                "reviewer_name": "Named Human",
                "reviewer_role": "business_reviewer",
                "is_human": True,
                "reviewed_at_utc": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
                "independent_review_attestation": True,
            },
            "cases": [
                {
                    "case_hash": _case_hash(index),
                    "criteria": {name: "PASS" for name in MODULE.CRITERIA_ORDER},
                    "unsafe_claim": False,
                    "overall_pass": True,
                    "rationale": "Synthetic local test rationale.",
                    "evidence_refs": ["synthetic-local-fixture"],
                }
                for index in range(20)
            ],
        }
        self._write_annotations()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _write_json(path: Path, value: object, *, private: bool) -> None:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.chmod(path, 0o600 if private else 0o644)

    def _write_annotations(self) -> None:
        self._write_json(self.annotations_path, self.annotations, private=True)

    def _validate(self) -> dict[str, object]:
        return MODULE.validate_annotations(
            self.annotations_path,
            self.preflight_path,
            self.guide_path,
            expected_preflight_sha256=self.preflight_sha,
            expected_guide_sha256=self.guide_sha,
            expected_authority_sha256="a" * 64,
        )

    def test_valid_packet_passes_without_emitting_identity(self) -> None:
        result = self._validate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["case_count"], 20)
        self.assertFalse(result["reviewer_identity_emitted"])
        self.assertFalse(result["case_identity_emitted"])
        self.assertNotIn("reviewer", result)

    def test_all_three_parent_bindings_are_exact(self) -> None:
        for key in self.annotations["parent_bindings"]:
            with self.subTest(key=key):
                poisoned = copy.deepcopy(self.annotations)
                poisoned["parent_bindings"][key] = "f" * 64
                self.annotations = poisoned
                self._write_annotations()
                with self.assertRaisesRegex(MODULE.AnnotationValidationError, "parent_binding_mismatch"):
                    self._validate()
                self.setUp_from_current_fixture()

    def setUp_from_current_fixture(self) -> None:
        self.annotations["parent_bindings"] = {
            "private_preflight_sha256": self.preflight_sha,
            "annotation_guide_sha256": self.guide_sha,
            "commercial_authority_snapshot_sha256": "a" * 64,
        }
        self._write_annotations()

    def test_twenty_cases_must_match_preflight_exactly_once(self) -> None:
        self.annotations["cases"][-1]["case_hash"] = self.annotations["cases"][0]["case_hash"]
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "case_hash_duplicate"):
            self._validate()

        self.annotations["cases"][-1]["case_hash"] = "f" * 64
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "case_set_mismatch"):
            self._validate()

    def test_seven_criteria_are_exact_pass_or_fail(self) -> None:
        del self.annotations["cases"][0]["criteria"][MODULE.CRITERIA_ORDER[0]]
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "criteria_keys_invalid"):
            self._validate()

        self.annotations["cases"][0]["criteria"] = {
            name: ("UNKNOWN" if index == 0 else "PASS")
            for index, name in enumerate(MODULE.CRITERIA_ORDER)
        }
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "criteria_value_invalid"):
            self._validate()

    def test_unsafe_and_overall_are_strict_booleans_and_recomputed(self) -> None:
        self.annotations["cases"][0]["unsafe_claim"] = 0
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "unsafe_claim_not_bool"):
            self._validate()

        self.annotations["cases"][0]["unsafe_claim"] = True
        self.annotations["cases"][0]["overall_pass"] = True
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "overall_recompute_mismatch"):
            self._validate()

    def test_named_human_and_independence_attestations_are_required(self) -> None:
        for key, bad_value in (
            ("reviewer_name", ""),
            ("is_human", False),
            ("independent_review_attestation", False),
            ("reviewed_at_utc", "2026-09-01T04:00:00+08:00"),
        ):
            with self.subTest(key=key):
                original = self.annotations["reviewer"][key]
                self.annotations["reviewer"][key] = bad_value
                self._write_annotations()
                with self.assertRaises(MODULE.AnnotationValidationError):
                    self._validate()
                self.annotations["reviewer"][key] = original

    def test_obvious_machine_identity_and_future_time_are_rejected(self) -> None:
        self.annotations["reviewer"].update(
            {"reviewer_id": "ai-agent", "reviewer_name": "AI Agent", "reviewer_role": "business_reviewer"}
        )
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "machine_identity"):
            self._validate()

        self.annotations["reviewer"].update(
            {
                "reviewer_id": "human-01",
                "reviewer_name": "Named Human",
                "reviewer_role": "business_reviewer",
                "reviewed_at_utc": "2099-01-01T00:00:00Z",
            }
        )
        self._write_annotations()
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "timestamp_in_future"):
            self._validate()

    def test_private_parent_directory_must_be_owner_only_0700(self) -> None:
        os.chmod(self.root, 0o755)
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "parent_not_owner_only_0700"):
            self._validate()

    def test_private_files_must_be_exactly_0600(self) -> None:
        os.chmod(self.annotations_path, 0o640)
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "mode_not_0600"):
            self._validate()

    def test_duplicate_json_keys_fail_closed(self) -> None:
        valid_text = self.annotations_path.read_text(encoding="utf-8")
        duplicate = valid_text.replace(
            "{\n  \"schema_version\"",
            "{\n  \"schema_version\": \"duplicate\",\n  \"schema_version\"",
            1,
        )
        self.annotations_path.write_text(duplicate, encoding="utf-8")
        os.chmod(self.annotations_path, 0o600)
        with self.assertRaisesRegex(MODULE.AnnotationValidationError, "json_invalid"):
            self._validate()


if __name__ == "__main__":
    unittest.main()
