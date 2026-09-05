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
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_mlx_training_preflight.py"
SPEC = importlib.util.spec_from_file_location("hermes_mlx_training_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class MlxTrainingPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.private_root = self.root / "private"
        self.private_root.mkdir(mode=0o700)
        self.model_root = self.root / "public-model"
        self.model_root.mkdir()
        self._write_bytes(self.model_root / "config.json", b"synthetic-config\n", private=False)
        self._write_bytes(self.model_root / "model.safetensors", b"synthetic-weights\n", private=False)
        self._write_bytes(self.model_root / "tokenizer.json", b"synthetic-tokenizer\n", private=False)
        self.model_hashes = {
            "model_config_sha256": MODULE.sha256_file(self.model_root / "config.json"),
            "model_weights_sha256": MODULE.sha256_file(
                self.model_root / "model.safetensors"
            ),
            "tokenizer_sha256": MODULE.sha256_file(self.model_root / "tokenizer.json"),
        }

        self.guide_path = self.root / "guide.json"
        self.annotation_preflight_path = self.private_root / "annotation-preflight.json"
        self.annotations_path = self.private_root / "annotations.json"
        self.gold_data_path = self.private_root / "gold.jsonl"
        self.holdout_data_path = self.private_root / "holdout.jsonl"
        self.dlp_manifest_path = self.private_root / "dlp-manifest.json"
        self.dlp_receipt_path = self.private_root / "dlp-receipt.json"
        self.gold_manifest_path = self.private_root / "gold-manifest.json"
        self.holdout_manifest_path = self.private_root / "holdout-manifest.json"
        self.training_config_path = self.private_root / "training-config.json"

        self.case_hashes = [_digest(f"annotation-case-{index}") for index in range(20)]
        self.guide = {
            "schema_version": "maplab.hermes.line-rubric-annotation-guide.v1",
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
                "schema_version": "maplab.hermes.line-rubric-human-annotations.v1",
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
        self.annotation_preflight = {
            "schema_version": "maplab.hermes.line-rubric-annotation-preflight.v1",
            "cases": [{"case_hash": value} for value in self.case_hashes],
        }
        self._write_json(self.guide_path, self.guide, private=False)
        self._write_json(self.annotation_preflight_path, self.annotation_preflight)
        self.guide_sha = MODULE.sha256_file(self.guide_path)
        self.annotation_preflight_sha = MODULE.sha256_file(self.annotation_preflight_path)

        self.annotations = {
            "schema_version": "maplab.hermes.line-rubric-human-annotations.v1",
            "parent_bindings": {
                "private_preflight_sha256": self.annotation_preflight_sha,
                "annotation_guide_sha256": self.guide_sha,
                "commercial_authority_snapshot_sha256": "a" * 64,
            },
            "reviewer": {
                "reviewer_id": "human-01",
                "reviewer_name": "Named Human",
                "reviewer_role": "business_reviewer",
                "is_human": True,
                "reviewed_at_utc": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
                "independent_review_attestation": True,
            },
            "cases": [
                {
                    "case_hash": value,
                    "criteria": {name: "PASS" for name in MODULE.CRITERIA_ORDER},
                    "unsafe_claim": False,
                    "overall_pass": True,
                    "rationale": "Synthetic local rationale.",
                    "evidence_refs": ["synthetic-local-fixture"],
                }
                for value in self.case_hashes
            ],
        }
        self._write_json(self.annotations_path, self.annotations)
        self.annotations_sha = MODULE.sha256_file(self.annotations_path)

        self._write_jsonl(self.gold_data_path, 30, "gold")
        self._write_jsonl(self.holdout_data_path, 20, "holdout")
        self.gold_conversations = [_digest(f"gold-conversation-{index}") for index in range(30)]
        self.holdout_conversations = [_digest(f"holdout-conversation-{index}") for index in range(20)]

        dlp_scan = MODULE.dlp_preflight.aggregate_scan(
            [
                MODULE.dlp_preflight.scan_jsonl(
                    self.gold_data_path, "gold", private=True
                ),
                MODULE.dlp_preflight.scan_jsonl(
                    self.holdout_data_path, "holdout", private=True
                ),
            ]
        )
        now = datetime.now(timezone.utc)
        attested_at = (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z")
        self.dlp_manifest = {
            "schema_version": MODULE.DLP_MANIFEST_SCHEMA,
            "manifest_id": "synthetic-hermes-rights-v1",
            "created_at": (now - timedelta(minutes=2)).isoformat().replace("+00:00", "Z"),
            "dataset": {
                "dataset_id": "synthetic-hermes-datasets",
                "data_class": "synthetic",
                "source_kind": "synthetic",
                "contains_raw_customer_text": False,
                "files": MODULE.dlp_preflight.manifest_file_projection(dlp_scan),
            },
            "authority": {
                "status": "APPROVED",
                "controller_id": "owner-controller",
                "attested_by": "Named Human",
                "attested_at": attested_at,
                "allowed_uses": ["offline_training", "offline_evaluation"],
                "prohibited_uses": sorted(MODULE.dlp_preflight.REQUIRED_PROHIBITED_USES),
            },
            "data_subject_rights": {
                "access_export": True,
                "correction": True,
                "deletion": True,
                "withdrawal_or_objection": True,
                "contact_route_id": "owner-local-process",
            },
            "retention": {
                "status": "ACTIVE",
                "policy_id": "owner-retention-policy",
                "expires_at": (now + timedelta(days=365)).isoformat().replace("+00:00", "Z"),
                "deletion_sla_days": 30,
            },
            "storage": {
                "owner_only": True,
                "allowed_root_fingerprint": MODULE.dlp_preflight.common_root_fingerprint(
                    [self.gold_data_path, self.holdout_data_path]
                ),
            },
            "egress": {
                "network_allowed": False,
                "third_party_allowed": False,
                "customer_send_allowed": False,
            },
            "review": {
                "free_text_review_status": "APPROVED",
                "reviewed_by": "Named Human",
                "reviewed_at": attested_at,
                "method": "synthetic_fixture",
                "known_identifier_dictionary_sha256": None,
            },
        }
        self._write_json(self.dlp_manifest_path, self.dlp_manifest)
        self.dlp_receipt = MODULE.dlp_preflight.build_receipt(
            manifest=self.dlp_manifest,
            manifest_sha256=MODULE.sha256_file(self.dlp_manifest_path),
            scan=dlp_scan,
            source_paths=[self.gold_data_path, self.holdout_data_path],
            created_at=now.isoformat().replace("+00:00", "Z"),
            scanner_sha256="b" * 64,
        )
        self._write_json(self.dlp_receipt_path, self.dlp_receipt)

        self.gold_manifest = {
            "schema_version": MODULE.GOLD_MANIFEST_SCHEMA,
            "status": "PASS",
            "data_class": "owner_corrected_gold",
            "dataset_path": str(self.gold_data_path),
            "dataset_sha256": MODULE.sha256_file(self.gold_data_path),
            "example_count": 30,
            "conversation_hashes": self.gold_conversations,
            "dlp_logical_name": "gold",
            "tokenizer_sha256": self.model_hashes["tokenizer_sha256"],
            "max_token_length": 256,
            "source_annotation_sha256": self.annotations_sha,
            "dlp_receipt_sha256": MODULE.sha256_file(self.dlp_receipt_path),
            "named_human_approval": True,
        }
        self.holdout_manifest = {
            "schema_version": MODULE.HOLDOUT_MANIFEST_SCHEMA,
            "status": "PASS",
            "data_class": "independent_holdout",
            "dataset_path": str(self.holdout_data_path),
            "dataset_sha256": MODULE.sha256_file(self.holdout_data_path),
            "case_count": 20,
            "conversation_hashes": self.holdout_conversations,
            "dlp_logical_name": "holdout",
            "tokenizer_sha256": self.model_hashes["tokenizer_sha256"],
            "max_token_length": 256,
            "frozen": True,
            "excluded_from_training": True,
            "prior_exposure_count": 0,
        }
        self._write_json(self.gold_manifest_path, self.gold_manifest)
        self._write_json(self.holdout_manifest_path, self.holdout_manifest)

        self.training_config = {
            "schema_version": MODULE.CONFIG_SCHEMA,
            "provider": "mlx_lm",
            "model_id": MODULE.EXPECTED_MODEL_ID,
            "model_revision": MODULE.EXPECTED_MODEL_REVISION,
            "model_path": str(self.model_root),
            "model_config_sha256": self.model_hashes["model_config_sha256"],
            "model_weights_sha256": self.model_hashes["model_weights_sha256"],
            "tokenizer_sha256": self.model_hashes["tokenizer_sha256"],
            "fine_tune_type": "lora_on_4bit_base",
            "private_root": str(self.private_root),
            "training_dataset_path": str(self.gold_data_path),
            "holdout_dataset_path": str(self.holdout_data_path),
            "adapter_output_path": str(self.private_root / "adapters" / "bounded-run-001"),
            "batch_size": 1,
            "grad_accumulation_steps": 1,
            "max_seq_length": 256,
            "num_layers": 2,
            "iterations": 20,
            "memory_limit_gb": 4.0,
            "terminate_on_memory_limit": True,
            "wall_time_limit_seconds": 1800,
            "mask_prompt": True,
            "network_allowed": False,
            "fallback_enabled": False,
            "fallback_provider": None,
            "process_fallback": None,
            "live_route_enabled": False,
        }
        self._write_json(self.training_config_path, self.training_config)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def _write_bytes(path: Path, value: bytes, *, private: bool) -> None:
        path.write_bytes(value)
        os.chmod(path, 0o600 if private else 0o644)

    def _write_json(self, path: Path, value: object, private: bool = True) -> None:
        self._write_bytes(
            path,
            (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode(),
            private=private,
        )

    def _write_jsonl(self, path: Path, count: int, prefix: str) -> None:
        text = "".join(
            json.dumps({"messages": [{"role": "user", "content": f"{prefix}-{index}"}]}) + "\n"
            for index in range(count)
        )
        self._write_bytes(path, text.encode(), private=True)

    def _evaluate(self, environment: dict[str, str] | None = None) -> dict[str, object]:
        return MODULE.evaluate_preflight(
            annotations_path=self.annotations_path,
            annotation_preflight_path=self.annotation_preflight_path,
            annotation_guide_path=self.guide_path,
            dlp_manifest_path=self.dlp_manifest_path,
            dlp_receipt_path=self.dlp_receipt_path,
            gold_manifest_path=self.gold_manifest_path,
            holdout_manifest_path=self.holdout_manifest_path,
            training_config_path=self.training_config_path,
            environment={} if environment is None else environment,
            expected_annotation_preflight_sha256=self.annotation_preflight_sha,
            expected_annotation_guide_sha256=self.guide_sha,
            expected_commercial_authority_sha256="a" * 64,
            expected_model_hashes=self.model_hashes,
        )

    def _validate_training_config(self) -> dict[str, object]:
        return MODULE.validate_training_config(
            self.training_config_path,
            {},
            expected_model_hashes=self.model_hashes,
        )

    def test_complete_offline_contract_returns_go_without_execution(self) -> None:
        result = self._evaluate()
        self.assertEqual(result["status"], "GO")
        self.assertTrue(result["eligible_for_bounded_mlx_training"])
        self.assertFalse(result["training_execution_performed"])
        self.assertFalse(result["ollama_used"])
        self.assertTrue(all(result["gates"].values()))

    def test_missing_labels_dlp_gold_and_holdout_are_no_go(self) -> None:
        self.annotations_path.unlink()
        self.dlp_receipt_path.unlink()
        self.gold_manifest_path.unlink()
        self.holdout_manifest_path.unlink()
        result = self._evaluate()
        self.assertEqual(result["status"], "NO_GO")
        for gate in ("labels", "dlp_rights", "gold", "holdout"):
            self.assertFalse(result["gates"][gate])

    def test_ollama_environment_url_and_process_fallback_are_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.TrainingPreflightError, "ollama_or_network_environment"):
            MODULE.validate_no_ollama_contract(self.training_config, {"OLLAMA_HOST": "127.0.0.1"})

        poisoned = copy.deepcopy(self.training_config)
        poisoned["model_path"] = {"nested": "http%253A%252F%252F127.0.0.1%253A11434/model"}
        with self.assertRaisesRegex(MODULE.TrainingPreflightError, "ollama_config_or_url"):
            MODULE.validate_no_ollama_contract(poisoned, {})

        poisoned = copy.deepcopy(self.training_config)
        poisoned["process_fallback"] = ["local-provider", "serve"]
        with self.assertRaisesRegex(MODULE.TrainingPreflightError, "process_fallback"):
            MODULE.validate_no_ollama_contract(poisoned, {})

    def test_forbidden_runtime_short_circuits_before_private_dataset_reads(self) -> None:
        with (
            mock.patch.object(
                MODULE, "validate_annotations", side_effect=AssertionError("labels read")
            ),
            mock.patch.object(
                MODULE, "validate_holdout_manifest", side_effect=AssertionError("holdout read")
            ),
            mock.patch.object(
                MODULE,
                "load_dataset_binding_from_manifest",
                side_effect=AssertionError("gold read"),
            ),
        ):
            result = self._evaluate({"OLLAMA_HOST": "127.0.0.1:11434"})
        self.assertEqual(result["status"], "NO_GO")
        self.assertFalse(any(result["gates"].values()))
        self.assertIn(
            "config:ollama_or_network_environment_rejected", result["errors"]
        )

    def test_batch_sequence_and_memory_limits_fail_closed(self) -> None:
        for key, value, error in (
            ("batch_size", 2, "batch_size"),
            ("batch_size", True, "batch_size"),
            ("max_seq_length", 257, "max_seq_length"),
            ("memory_limit_gb", 8.1, "memory_limit_gb"),
            ("terminate_on_memory_limit", False, "memory_limit_termination"),
        ):
            with self.subTest(key=key):
                poisoned = copy.deepcopy(self.training_config)
                poisoned[key] = value
                self._write_json(self.training_config_path, poisoned)
                with self.assertRaisesRegex(MODULE.TrainingPreflightError, error):
                    self._validate_training_config()
        self._write_json(self.training_config_path, self.training_config)

    def test_self_declared_replacement_model_hash_is_not_a_pin(self) -> None:
        self._write_bytes(
            self.model_root / "model.safetensors",
            b"synthetic-replacement-weights\n",
            private=False,
        )
        poisoned = copy.deepcopy(self.training_config)
        poisoned["model_weights_sha256"] = MODULE.sha256_file(
            self.model_root / "model.safetensors"
        )
        self._write_json(self.training_config_path, poisoned)
        with self.assertRaisesRegex(
            MODULE.TrainingPreflightError, "model_weights_sha256_not_pinned"
        ):
            self._validate_training_config()

    def test_dlp_receipt_must_be_pass_and_zero_findings(self) -> None:
        self.dlp_receipt["scan"]["review_required_findings"] = 1
        self.dlp_receipt["scan"]["findings_by_category"] = {"synthetic_review": 1}
        self.dlp_receipt["scan"]["files"][0]["review_required_findings"] = 1
        receipt_body = dict(self.dlp_receipt)
        receipt_body.pop("body_sha256")
        self.dlp_receipt["body_sha256"] = MODULE.dlp_preflight.sha256_text(
            MODULE.dlp_preflight.canonical_json(receipt_body)
        )
        self._write_json(self.dlp_receipt_path, self.dlp_receipt)
        result = self._evaluate()
        self.assertEqual(result["status"], "NO_GO")
        self.assertFalse(result["gates"]["dlp_rights"])
        self.assertFalse(result["gates"]["gold"])

    def test_gold_and_holdout_conversation_overlap_is_rejected(self) -> None:
        self.holdout_manifest["conversation_hashes"][0] = self.gold_conversations[0]
        self._write_json(self.holdout_manifest_path, self.holdout_manifest)
        result = self._evaluate()
        self.assertEqual(result["status"], "NO_GO")
        self.assertFalse(result["gates"]["contamination"])
        self.assertIn("contamination:conversation_overlap_nonzero", result["errors"])

    def test_config_must_bind_exact_gold_and_holdout_paths(self) -> None:
        self.training_config["training_dataset_path"] = str(self.holdout_data_path)
        self._write_json(self.training_config_path, self.training_config)
        result = self._evaluate()
        self.assertEqual(result["status"], "NO_GO")
        self.assertFalse(result["gates"]["config"])
        self.assertIn("config:training_dataset_binding_mismatch", result["errors"])


if __name__ == "__main__":
    unittest.main()
