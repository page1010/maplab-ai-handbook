import hashlib
import importlib.util
import json
import plistlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_method_redesign_audit.py"
SPEC = importlib.util.spec_from_file_location("hermes_line_method_redesign_audit_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


STAGES = (
    "S2_DATA",
    "S2_DIETARY",
    "S3_QUOTE_INTRO",
    "S3_QUOTE_SEND",
    "S4_PAYMENT",
    "S_PENDING",
)


class MethodRedesignAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.root.chmod(0o700)
        self.data = self.root / "data"
        self.data.mkdir(mode=0o700)
        for name in ("runs", "lesson_deltas", "supervisor_jobs"):
            (self.data / name).mkdir(mode=0o700)

        self.private_markers = []
        self._write_dataset("train", 10, "train")
        self._write_dataset("eval", 8, "eval")
        self._write_private_text(self.data / "current_lessons.md", "private rolling lesson marker")
        self.training_loop = self.root / "hermes_line_training_loop.py"
        self.supervisor_script = self.root / "hermes_line_training_supervisor.py"
        self.training_loop.write_text(
            "def build_prompt(sample, examples, lessons):\n"
            "    return [{'role': 'system', 'content': lessons}]\n",
            encoding="utf-8",
        )
        self.supervisor_script.write_text("# supervisor\n", encoding="utf-8")
        self.model_manifest = self.root / "model-manifest"
        self.model_manifest.write_text("pinned model manifest\n", encoding="utf-8")
        self.job_path = self.data / "supervisor_jobs" / "canonical_job.json"
        self._write_private_json(
            self.job_path,
            {
                "job_id": MODULE.EXPECTED_JOB_ID,
                "state": "RUNNING",
                "attempt": 6,
            },
        )
        self.repo_plist = self.root / "repo.plist"
        self.installed_plist = self.root / "installed.plist"
        self._write_plist(self.repo_plist, self.training_loop)
        self._write_plist(self.installed_plist, self.training_loop)

        self.round_rows = []
        for index in range(3):
            run_id = f"SUP-{index}"
            lesson = self.data / "lesson_deltas" / f"{run_id}.md"
            self._write_private_text(lesson, f"private lesson {index}")
            run = self.data / "runs" / f"{run_id}.json"
            payload = self._run_payload(
                run_id,
                f"2026-01-01T00:0{index}:00+00:00",
                results=[self._result(f"supervised-{index}", "S2_DATA", passed=index == 1)],
                lesson_delta=lesson,
                seed=100 + index,
            )
            self._write_private_json(run, payload)
            self.round_rows.append(
                {
                    "receipt": str(run),
                    "receipt_sha256": MODULE.sha256_file(run),
                }
            )

        bypass_lesson = self.data / "lesson_deltas" / "BYPASS.md"
        self._write_private_text(bypass_lesson, "private bypass lesson")
        bypass = self.data / "runs" / "BYPASS.json"
        self._write_private_json(
            bypass,
            self._run_payload(
                "BYPASS",
                "2026-01-01T00:04:00+00:00",
                results=[self._result("bypass-private-id", "S_PENDING", passed=False, unsupported=True)],
                lesson_delta=bypass_lesson,
                seed=999,
            ),
        )

        self.supervisor = self.data / "supervisor_jobs" / "receipt.json"
        self._write_private_json(
            self.supervisor,
            {
                "schema_version": "maplab.hermes.line-supervisor.v1",
                "job_id": MODULE.EXPECTED_JOB_ID,
                "status": "bounded_pause",
                "updated_at": "2026-01-01T00:03:00+00:00",
                "method_review_required": True,
                "loopback_ollama_calls": 3,
                "rounds": self.round_rows,
                "qualification_contract": {
                    "model": "gemma4:latest",
                    "inference_parameters": {"temperature": 0},
                    "evaluator_version": "maplab.hermes.line-evaluator.v1",
                    "base_batch": 1,
                    "requested_stage": None,
                    "target_pass_rate": 0.85,
                    "target_streak": 7,
                },
            },
        )

    def tearDown(self):
        self.temp.cleanup()

    def _write_private_text(self, path, value):
        path.write_text(value, encoding="utf-8")
        path.chmod(0o600)

    def _write_private_json(self, path, payload):
        self._write_private_text(path, json.dumps(payload, ensure_ascii=False))

    def _write_dataset(self, stem, per_stage, prefix):
        rows = []
        for stage_index, stage in enumerate(STAGES):
            for index in range(per_stage):
                marker = f"private-{prefix}-{stage_index}-{index}"
                self.private_markers.append(marker)
                rows.append(
                    {
                        "id": f"{prefix}-id-{stage_index}-{index}",
                        "stage": stage,
                        "conversation_id": f"{prefix}-conversation-{stage_index}-{index}",
                        "customer": marker,
                        "target": f"{marker}-target",
                        "context": [],
                    }
                )
        self._write_private_text(
            self.data / f"{stem}.jsonl",
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        )

    def _write_plist(self, path, program):
        path.write_bytes(
            plistlib.dumps(
                {
                    "Label": "com.maplab.hermes-line-training",
                    "ProgramArguments": ["/usr/bin/python3", str(program), "--batch", "5"],
                    "StartCalendarInterval": {"Hour": 2, "Minute": 20},
                }
            )
        )

    def _result(self, identifier, stage, *, passed, unsupported=False):
        return {
            "id": identifier,
            "stage": stage,
            "customer": f"private-customer-{identifier}",
            "generated": f"private-generated-{identifier}",
            "target": f"private-target-{identifier}",
            "evaluation": {
                "score": 80,
                "pass": passed,
                "required_signals": ["日期"],
                "hit_signals": ["日期"],
                "missed_signals": [],
                "unsupported_money": ["1000"] if unsupported else [],
                "question_ok": True,
                "length_ratio": 1.0 if passed else 3.0,
            },
        }

    def _run_payload(self, run_id, created_at, *, results, lesson_delta, seed):
        passed = sum(item["evaluation"]["pass"] for item in results)
        unsupported = sum(bool(item["evaluation"]["unsupported_money"]) for item in results)
        return {
            "schema_version": "maplab.hermes.line-run.v2",
            "run_id": run_id,
            "created_at": created_at,
            "evaluator_version": "maplab.hermes.line-evaluator.v1",
            "model": "gemma4:latest",
            "seed": seed,
            "pass_rate": passed / len(results),
            "unsupported_price_rate": unsupported / len(results),
            "unsupported_price_count": unsupported,
            "lowest_stage": results[0]["stage"],
            "loopback_ollama_calls": len(results),
            "lesson_delta": str(lesson_delta),
            "results": results,
        }

    def _build(self):
        return MODULE.build_audit(
            data_root=self.data,
            supervisor_receipt=self.supervisor,
            repo_plist=self.repo_plist,
            installed_plist=self.installed_plist,
            training_loop=self.training_loop,
            supervisor_script=self.supervisor_script,
            model_manifest=self.model_manifest,
            job_path=self.job_path,
            enforce_canonical_sources=False,
        )

    def _source_context(self):
        return {
            "data_root": self.data,
            "supervisor_receipt": self.supervisor,
            "repo_plist": self.repo_plist,
            "installed_plist": self.installed_plist,
            "training_loop": self.training_loop,
            "supervisor_script": self.supervisor_script,
            "model_manifest": self.model_manifest,
            "job_path": self.job_path,
        }

    def _validate(self, payload):
        MODULE.validate_audit(
            payload,
            source_context=self._source_context(),
            enforce_canonical_sources=False,
        )

    def test_freezes_balanced_private_manifests_and_detects_bypass(self):
        payload = self._build()
        self._validate(payload)
        self.assertEqual(payload["fixed_holdout"]["case_count"], 20)
        self.assertEqual(payload["fixed_holdout"]["unique_conversation_count"], 20)
        self.assertEqual(payload["fixed_few_shot"]["mapping_count"], 20)
        self.assertEqual(payload["fixed_few_shot"]["case_count"], 40)
        self.assertEqual(payload["supervisor_analysis"]["post_pause_bypass"]["loopback_ollama_calls"], 1)
        self.assertEqual(payload["attempt_before"], 6)
        self.assertEqual(payload["attempt_after"], 6)
        self.assertFalse(payload["attempt_consumed"])
        self.assertEqual(payload["model_calls_this_action"], 0)
        self.assertEqual(
            payload["experiment_contract"]["changed_variable"],
            "prompt_builder_contract_sha256 only",
        )
        serialized = json.dumps(payload, ensure_ascii=False)
        for marker in self.private_markers:
            self.assertNotIn(marker, serialized)
        self.assertNotIn("private-customer", serialized)
        self.assertNotIn("private-generated", serialized)
        self.assertNotIn("private-target", serialized)

    def test_holdout_excludes_entire_prior_exposed_conversation(self):
        rows = MODULE.load_private_jsonl(self.data / "eval.jsonl", "eval")
        exposed_id = rows[0]["id"]
        exposed_conversation = rows[0]["conversation_id"]
        rows[1]["conversation_id"] = exposed_conversation
        _, selected_source_rows = MODULE.select_holdout_manifest(
            rows,
            excluded_record_ids={exposed_id},
            excluded_conversation_ids={exposed_conversation},
        )
        self.assertNotIn(exposed_id, {row["id"] for row in selected_source_rows})
        self.assertNotIn(
            exposed_conversation,
            {row["conversation_id"] for row in selected_source_rows},
        )

    def test_sanitized_receipt_binds_private_bytes_and_hides_case_hashes(self):
        payload = self._build()
        private = self.root / "private" / "audit.json"
        self.assertTrue(MODULE.write_private_json(private, payload))
        private_sha = MODULE.sha256_file(private)
        sanitized = MODULE.build_sanitized_receipt(
            private,
            private_sha,
            source_context=self._source_context(),
            enforce_canonical_sources=False,
        )
        self.assertEqual(sanitized["private_audit_sha256"], private_sha)
        self.assertNotIn("cases", sanitized["fixed_holdout"])
        self.assertNotIn("mappings", sanitized["fixed_few_shot"])
        self.assertEqual(
            sanitized["call_accounting"]["round_count"],
            payload["supervisor_analysis"]["round_count"],
        )
        self.assertEqual(
            sanitized["call_accounting"]["physical_explicit_call_count_lower_bound"],
            payload["supervisor_analysis"]["physical_explicit_call_count_lower_bound"],
        )
        self.assertEqual(
            sanitized["call_accounting"]["explicit_calls_outside_supervisor"],
            payload["supervisor_analysis"]["explicit_calls_outside_supervisor"],
        )
        self.assertRegex(sanitized["body_sha256"], r"^[0-9a-f]{64}$")
        MODULE.validate_sanitized_receipt(sanitized)
        poisoned_sanitized = json.loads(json.dumps(sanitized))
        poisoned_sanitized["payload"] = "synthetic-secret-marker"
        poisoned_body = dict(poisoned_sanitized)
        poisoned_body.pop("body_sha256")
        poisoned_sanitized["body_sha256"] = MODULE.sha256_text(
            MODULE.canonical_json(poisoned_body)
        )
        with self.assertRaisesRegex(MODULE.MethodAuditError, "sanitized_topology"):
            MODULE.validate_sanitized_receipt(poisoned_sanitized)
        with self.assertRaisesRegex(MODULE.MethodAuditError, "private_audit_sha256_mismatch"):
            MODULE.build_sanitized_receipt(
                private,
                "0" * 64,
                source_context=self._source_context(),
                enforce_canonical_sources=False,
            )

    def test_private_writer_is_idempotent_and_conflicts_fail_closed(self):
        payload = self._build()
        output = self.root / "private" / "audit.json"
        self.assertTrue(MODULE.write_private_json(output, payload))
        original_sha = MODULE.sha256_file(output)
        replay = self._build()
        self.assertNotEqual(replay["created_at"], payload["created_at"])
        self.assertFalse(MODULE.write_private_json(output, replay))
        self.assertEqual(MODULE.sha256_file(output), original_sha)
        conflict = json.loads(json.dumps(replay))
        conflict["attempt_after"] = 7
        with self.assertRaisesRegex(MODULE.MethodAuditError, "existing_private_output_identity_conflict"):
            MODULE.write_private_json(output, conflict)

    def test_validator_rejects_provenance_type_time_and_nested_payload_poison(self):
        base = self._build()

        forged_script = json.loads(json.dumps(base))
        forged_script["implementation_provenance"]["audit_script_sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.MethodAuditError, "implementation_provenance"):
            self._validate(forged_script)

        future = json.loads(json.dumps(base))
        future["created_at"] = "2999-01-01T00:00:00+00:00"
        with self.assertRaisesRegex(MODULE.MethodAuditError, "created_at_future"):
            self._validate(future)

        extra = json.loads(json.dumps(base))
        extra["payload"] = "synthetic-secret-marker"
        with self.assertRaisesRegex(MODULE.MethodAuditError, "topology"):
            self._validate(extra)

        boolean_attempt = json.loads(json.dumps(base))
        boolean_attempt["attempt_before"] = True
        boolean_attempt["attempt_after"] = True
        with self.assertRaisesRegex(MODULE.MethodAuditError, "attempt_accounting"):
            self._validate(boolean_attempt)

        short_model_digest = json.loads(json.dumps(base))
        method = short_model_digest["experiment_contract"]
        method["model_digest"] = "a" * 12
        method_without_fingerprint = dict(method)
        method_without_fingerprint.pop("method_fingerprint")
        method["method_fingerprint"] = MODULE.sha256_text(
            MODULE.canonical_json(method_without_fingerprint)
        )
        with self.assertRaisesRegex(MODULE.MethodAuditError, "method_hash"):
            self._validate(short_model_digest)

        nested_case = json.loads(json.dumps(base))
        nested_case["fixed_holdout"]["cases"][0]["notes"] = "synthetic-secret-marker"
        nested_case["fixed_holdout"]["case_manifest_sha256"] = MODULE.manifest_digest(
            nested_case["fixed_holdout"]["cases"]
        )
        with self.assertRaisesRegex(MODULE.MethodAuditError, "case_topology"):
            self._validate(nested_case)

        bypass_payload = json.loads(json.dumps(base))
        bypass_payload["supervisor_analysis"]["post_pause_bypass"]["runs"][0][
            "payload"
        ] = "synthetic-secret-marker"
        with self.assertRaisesRegex(MODULE.MethodAuditError, "bypass_run_topology"):
            self._validate(bypass_payload)

        forged_job_pair = json.loads(json.dumps(base))
        forged_job_pair["implementation_provenance"]["canonical_job_sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.MethodAuditError, "live_source_provenance"):
            self._validate(forged_job_pair)

        forged_model_pair = json.loads(json.dumps(base))
        forged_model_pair["experiment_contract"]["model_digest"] = "1" * 64
        forged_model_pair["implementation_provenance"]["model_manifest_sha256"] = "1" * 64
        forged_model_core = dict(forged_model_pair["experiment_contract"])
        forged_model_core.pop("method_fingerprint")
        forged_model_pair["experiment_contract"]["method_fingerprint"] = MODULE.sha256_text(
            MODULE.canonical_json(forged_model_core)
        )
        with self.assertRaisesRegex(MODULE.MethodAuditError, "live_source_provenance"):
            self._validate(forged_model_pair)

        forged_supervisor_pair = json.loads(json.dumps(base))
        forged_supervisor_pair["supervisor_analysis"]["supervisor_receipt_sha256"] = "2" * 64
        forged_supervisor_pair["implementation_provenance"]["supervisor_receipt_sha256"] = "2" * 64
        with self.assertRaisesRegex(MODULE.MethodAuditError, "supervisor_live_source"):
            self._validate(forged_supervisor_pair)

        forged_baseline = json.loads(json.dumps(base))
        forged_baseline["experiment_contract"]["baseline_prompt_builder_source_sha256"] = "3" * 64
        forged_baseline_core = dict(forged_baseline["experiment_contract"])
        forged_baseline_core.pop("method_fingerprint")
        forged_baseline["experiment_contract"]["method_fingerprint"] = MODULE.sha256_text(
            MODULE.canonical_json(forged_baseline_core)
        )
        with self.assertRaisesRegex(MODULE.MethodAuditError, "live_source_provenance"):
            self._validate(forged_baseline)

        forged_lesson_pair = json.loads(json.dumps(base))
        forged_lesson_pair["experiment_contract"]["lesson_sha256"] = "4" * 64
        forged_lesson_pair["supervisor_analysis"]["current_lessons_sha256"] = "4" * 64
        forged_lesson_core = dict(forged_lesson_pair["experiment_contract"])
        forged_lesson_core.pop("method_fingerprint")
        forged_lesson_pair["experiment_contract"]["method_fingerprint"] = MODULE.sha256_text(
            MODULE.canonical_json(forged_lesson_core)
        )
        with self.assertRaisesRegex(MODULE.MethodAuditError, "supervisor_live_source"):
            self._validate(forged_lesson_pair)

        nested_metrics = json.loads(json.dumps(base))
        nested_metrics["supervisor_analysis"]["post_pause_bypass"]["metrics"][
            "payload"
        ] = "synthetic-secret-marker"
        with self.assertRaisesRegex(MODULE.MethodAuditError, "bypass_metrics_topology"):
            self._validate(nested_metrics)

        forged_missing_fields = json.loads(json.dumps(base))
        forged_missing_fields["supervisor_analysis"]["last_three_method_review"][
            "missing_fields"
        ].append("synthetic-secret-marker")
        with self.assertRaisesRegex(MODULE.MethodAuditError, "method_review_contract"):
            self._validate(forged_missing_fields)

    def test_build_derives_attempt_and_model_digest_from_source_files(self):
        payload = self._build()
        self.assertEqual(
            payload["experiment_contract"]["model_digest"],
            MODULE.sha256_file(self.model_manifest),
        )
        self.assertEqual(
            payload["implementation_provenance"]["canonical_job_sha256"],
            MODULE.sha256_file(self.job_path),
        )

        poisoned_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        poisoned_job["attempt"] = True
        self._write_private_json(self.job_path, poisoned_job)
        with self.assertRaisesRegex(MODULE.MethodAuditError, "attempt_before_invalid"):
            self._build()

    def test_permissions_and_supervisor_routing_fail_closed(self):
        eval_path = self.data / "eval.jsonl"
        eval_path.chmod(0o644)
        with self.assertRaisesRegex(MODULE.MethodAuditError, "eval_permissions_not_private"):
            self._build()
        eval_path.chmod(0o600)

        self._write_plist(self.installed_plist, self.supervisor_script)
        with self.assertRaisesRegex(MODULE.MethodAuditError, "post_pause_schedule_bypass_not_proven"):
            self._build()


if __name__ == "__main__":
    unittest.main()
