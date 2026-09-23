import copy
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_rubric_annotation_packet.py"
SPEC = importlib.util.spec_from_file_location(
    "hermes_line_rubric_annotation_packet_tested", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class HermesLineRubricAnnotationPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_v7 = MODULE.load_json(
            MODULE.PRIVATE_V7_PATH, private=True, label="test_private_v7"
        )
        cls.eval_rows = MODULE.load_eval_rows(MODULE.EVAL_PATH)
        cls.source_hashes = {
            **MODULE.EXPECTED_HASHES,
            "job_preimage_sha256": MODULE.sha256_file(MODULE.JOB_PATH),
        }

    def build_packet(self):
        return MODULE.build_packet(
            private_v7=copy.deepcopy(self.private_v7),
            eval_rows=copy.deepcopy(self.eval_rows),
            created_at="2026-08-28T02:17:05Z",
            source_hashes=copy.deepcopy(self.source_hashes),
        )

    def test_current_sources_bind_to_exact_frozen_20_without_labels(self):
        self.assertEqual(
            MODULE.sha256_file(MODULE.EVAL_PATH),
            MODULE.EXPECTED_HASHES["eval_dataset_sha256"],
        )
        self.assertEqual(
            MODULE.sha256_file(MODULE.PRIVATE_V7_PATH),
            MODULE.EXPECTED_HASHES["private_v7_sha256"],
        )
        packet = self.build_packet()
        self.assertEqual(packet["status"], "NEEDS_ANNOTATION_GUIDE")
        self.assertFalse(packet["annotation_guide_requirements"]["guide_ready"])
        self.assertFalse(
            packet["annotation_guide_requirements"]["human_annotation_may_start"]
        )
        self.assertEqual(len(packet["cases"]), 20)
        self.assertEqual(len({item["case_hash"] for item in packet["cases"]}), 20)
        self.assertEqual(packet["source_structured_human_label_count"], 0)
        self.assertTrue(all(item["human_annotation"]["annotator_role"] is None for item in packet["cases"]))

    def test_plateau_fingerprint_and_rates_are_bound_to_v7_source(self):
        review = self.private_v7["supervisor_analysis"]["last_three_method_review"]
        self.assertEqual(
            review["shared_partial_method_fingerprint"],
            MODULE.EXPECTED_PARTIAL_METHOD_FINGERPRINT,
        )
        self.assertEqual(
            [item["pass_rate"] for item in review["receipts"]],
            [0.2, 0.4, 0.2],
        )

    def test_panel_has_historical_and_controlled_negative_specimens(self):
        packet = self.build_packet()
        self.assertEqual(
            packet["specimen_origin_counts"],
            {
                "historical_human_authored_reference_unlabeled": 10,
                "controlled_negative_synthetic_local_only": 10,
            },
        )
        for item in packet["cases"]:
            if item["specimen_origin"].startswith("historical_"):
                self.assertEqual(item["reply_specimen"], item["historical_reference_target"])
            else:
                self.assertNotEqual(item["reply_specimen"], item["historical_reference_target"])

    def test_missing_duplicate_or_changed_holdout_fails_closed(self):
        for mutation in ("missing", "duplicate", "changed"):
            private_v7 = copy.deepcopy(self.private_v7)
            cases = private_v7["fixed_holdout"]["cases"]
            if mutation == "missing":
                cases.pop()
            elif mutation == "duplicate":
                cases[-1] = copy.deepcopy(cases[0])
            else:
                cases[0]["selection_key"] = "0" * 64
                private_v7["fixed_holdout"]["case_manifest_sha256"] = MODULE.sha256_text(
                    MODULE.canonical_json(cases)
                )
            with self.subTest(mutation=mutation):
                with self.assertRaises(MODULE.AnnotationPacketError):
                    MODULE.build_packet(
                        private_v7=private_v7,
                        eval_rows=copy.deepcopy(self.eval_rows),
                        created_at="2026-08-28T02:17:05Z",
                        source_hashes=copy.deepcopy(self.source_hashes),
                    )

    def test_unexpected_source_label_field_is_rejected(self):
        rows = copy.deepcopy(self.eval_rows)
        frozen_hash = self.private_v7["fixed_holdout"]["cases"][0]["case_hash"]
        matching = next(row for row in rows if MODULE._case_hash(row) == frozen_hash)
        matching["rubric_v2_labels"] = {"answers_current_question": "PASS"}
        with self.assertRaisesRegex(
            MODULE.AnnotationPacketError, "unexpected_source_structured_labels_present"
        ):
            MODULE.build_packet(
                private_v7=copy.deepcopy(self.private_v7),
                eval_rows=rows,
                created_at="2026-08-28T02:17:05Z",
                source_hashes=copy.deepcopy(self.source_hashes),
            )

    def test_packet_source_provenance_cannot_be_rewritten(self):
        mutations = {
            "source_provenance": lambda packet: packet["source_provenance"].__setitem__(
                "eval_dataset_sha256", "0" * 64
            ),
            "guide_flag": lambda packet: packet["annotation_guide_requirements"].__setitem__(
                "human_annotation_may_start", True
            ),
            "calibration_threshold": lambda packet: packet["calibration_contract"].__setitem__(
                "minimum_exact_agreement", "1/20"
            ),
            "reply_binding": lambda packet: packet["cases"][0].__setitem__(
                "reply_specimen_sha256", "0" * 64
            ),
            "panel_origin": lambda packet: packet["cases"][0].__setitem__(
                "specimen_origin", "controlled_negative_synthetic_local_only"
            ),
        }
        for name, mutate in mutations.items():
            packet = self.build_packet()
            mutate(packet)
            with self.subTest(name=name):
                with self.assertRaises(MODULE.AnnotationPacketError):
                    MODULE.validate_packet(packet)

    def test_sanitized_receipt_contains_no_private_payload_or_paths(self):
        packet = self.build_packet()
        receipt = MODULE.build_sanitized_receipt(
            packet_sha256=MODULE.sha256_text(MODULE.canonical_json(packet)),
            created_at="2026-08-28T02:17:05Z",
            job_preimage_sha256=MODULE.sha256_file(MODULE.JOB_PATH),
            script_sha256=MODULE.sha256_file(MODULE_PATH),
            test_sha256="a" * 64,
        )
        serialized = json.dumps(receipt, ensure_ascii=False)
        for token in (
            "/Users/",
            "case_hash",
            "historical_reference_target",
            "reply_specimen",
            '"context"',
            '"customer"',
        ):
            self.assertNotIn(token, serialized)
        self.assertFalse(receipt["execution_eligible"])
        self.assertEqual(receipt["state_recommendation"], "RUNNING")
        self.assertFalse(receipt["owner_action_required"])
        self.assertEqual(
            receipt["method_fingerprint"], MODULE.action_method_fingerprint()
        )
        self.assertEqual(receipt["model_calls_this_action"], 0)
        self.assertEqual(receipt["attempt_before"], receipt["attempt_after"])

    def test_public_receipt_leak_is_rejected_even_with_recomputed_body_hash(self):
        mutations = {
            "private_leak": lambda receipt: receipt.__setitem__(
                "next_bounded_action", "/Users/example/private reply_specimen"
            ),
            "plateau_rate": lambda receipt: receipt["plateau_review"].__setitem__(
                "last_three_pass_rates", [1.0, 1.0, 1.0]
            ),
            "execution_blockers": lambda receipt: receipt.__setitem__(
                "execution_blockers", []
            ),
            "unsafe_next_action": lambda receipt: receipt.__setitem__(
                "next_bounded_action", "Run E1 now."
            ),
        }
        for name, mutate in mutations.items():
            receipt = MODULE.build_sanitized_receipt(
                packet_sha256="a" * 64,
                created_at="2026-08-28T02:17:05Z",
                job_preimage_sha256="b" * 64,
                script_sha256="c" * 64,
                test_sha256="d" * 64,
            )
            mutate(receipt)
            body = dict(receipt)
            body.pop("body_sha256")
            receipt["body_sha256"] = MODULE.sha256_text(MODULE.canonical_json(body))
            with self.subTest(name=name):
                with self.assertRaises(MODULE.AnnotationPacketError):
                    MODULE.validate_sanitized_receipt(receipt)

    def test_private_writer_is_0600_atomic_and_refuses_conflict(self):
        packet = self.build_packet()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "private"
            path = root / "packet.json"
            self.assertTrue(MODULE.write_private_json(path, packet))
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
            self.assertFalse(MODULE.write_private_json(path, packet))
            conflict = copy.deepcopy(packet)
            conflict["status"] = "CHANGED"
            with self.assertRaisesRegex(
                MODULE.AnnotationPacketError, "identity_conflict"
            ):
                MODULE.write_private_json(path, conflict)

    def test_private_writer_rejects_symlink(self):
        packet = self.build_packet()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            path = root / "packet.json"
            path.symlink_to(target)
            with self.assertRaisesRegex(MODULE.AnnotationPacketError, "symlink"):
                MODULE.write_private_json(path, packet)

    def test_no_domain_model_network_or_customer_surface_is_imported(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        for token in (
            "requests.",
            "urllib.request",
            "openrouter",
            "ollama",
            "send_message",
            "line-bot-sdk",
        ):
            self.assertNotIn(token, source.lower())

    def test_job_update_requires_exact_live_preimage(self):
        with self.assertRaisesRegex(MODULE.AnnotationPacketError, "job_preimage_changed"):
            MODULE.update_job_for_annotation_guide(
                packet_path=Path("/tmp/private.json"),
                packet_sha256="a" * 64,
                receipt_path=Path("/tmp/public.json"),
                receipt_sha256="b" * 64,
                job_preimage_sha256="0" * 64,
                created_at="2026-08-28T02:17:05Z",
            )

    def test_active_receipt_binding_refresh_is_idempotent(self):
        packet_sha = "a" * 64
        prior_receipt_sha = "b" * 64
        new_receipt_sha = "c" * 64
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            job_path = root / "job.json"
            packet_path = root / "packet.json"
            receipt_path = root / "receipt.json"
            packet_path.write_text("{}\n", encoding="utf-8")
            receipt_path.write_text("{}\n", encoding="utf-8")
            job = {
                "schema_version": "maplab.durable-job.v1",
                "job_id": MODULE.JOB_ID,
                "state": "RUNNING",
                "attempt": MODULE.EXPECTED_ATTEMPT,
                "current_phase": "method-redesign-rubric-annotation-guide",
                "updated_at": "2026-08-28T02:17:05Z",
                "last_result": {
                    "execution_eligible": False,
                    "private_annotation_preflight_sha256": packet_sha,
                    "sanitized_readiness_receipt_sha256": prior_receipt_sha,
                },
                "artifacts": [
                    {
                        "path": str(packet_path),
                        "kind": "line-rubric-v2-private-annotation-guide-preflight",
                        "sha256": packet_sha,
                    },
                    {
                        "path": str(receipt_path),
                        "kind": "line-rubric-v2-sanitized-readiness-receipt",
                        "sha256": prior_receipt_sha,
                    },
                ],
                "history": [],
            }
            MODULE.atomic_replace_json(job_path, job, mode=0o600)
            with mock.patch.object(MODULE, "JOB_PATH", job_path):
                self.assertTrue(
                    MODULE.refresh_active_job_binding(
                        packet_path=packet_path,
                        packet_sha256=packet_sha,
                        receipt_path=receipt_path,
                        prior_receipt_sha256=prior_receipt_sha,
                        receipt_sha256=new_receipt_sha,
                        refreshed_at="2026-08-28T02:30:00Z",
                    )
                )
                self.assertFalse(
                    MODULE.refresh_active_job_binding(
                        packet_path=packet_path,
                        packet_sha256=packet_sha,
                        receipt_path=receipt_path,
                        prior_receipt_sha256=prior_receipt_sha,
                        receipt_sha256=new_receipt_sha,
                        refreshed_at="2026-08-28T02:31:00Z",
                    )
                )
            updated = json.loads(job_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated["last_result"]["sanitized_readiness_receipt_sha256"],
                new_receipt_sha,
            )
            self.assertEqual(len(updated["history"]), 1)


if __name__ == "__main__":
    unittest.main()
