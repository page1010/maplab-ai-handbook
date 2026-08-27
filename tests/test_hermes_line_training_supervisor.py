import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_training_supervisor.py"
SPEC = importlib.util.spec_from_file_location("hermes_line_training_supervisor_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def private_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.write_text(payload, encoding="utf-8")
    path.chmod(0o600)


def build_dataset(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    root.chmod(0o700)
    manifest = {
        "schema": "maplab.hermes.line_pairs.v1",
        "anonymization": "customer sender names removed/replaced; conversation IDs hashed",
        "split": "80/20 by conversation hash",
    }
    row = {
        "id": "sample",
        "stage": "S3",
        "conversation_id": "hashed-conversation",
        "customer": "private input",
        "target": "private target",
        "context": [],
    }
    private_write(root / "manifest.json", json.dumps(manifest))
    private_write(root / "train.jsonl", json.dumps(row) + "\n")
    private_write(root / "eval.jsonl", json.dumps(row | {"id": "eval"}) + "\n")


def build_job(root: Path, job_id: str = "MAPJOB-TEST-001") -> tuple[Path, dict]:
    job_path = root / job_id / "job.json"
    job = {
        "schema_version": "maplab.durable-job.v1",
        "job_id": job_id,
        "job_path": str(job_path),
        "request": "Hermes 用 LINE 對話持續多跑幾輪訓練",
        "job_type": "hermes-line-training",
        "adapter": "hermes-line-training-supervisor",
        "data_class": "private-local-only",
        "authorization": {"offline_training": True, "customer_send": False},
        "state": "ACCEPTED",
        "current_phase": "intake",
        "last_result": None,
        "next_bounded_action": "start",
        "attempt": 0,
        "artifacts": [],
        "history": [],
        "resume_prompt": "resume safely",
    }
    private_write(job_path, json.dumps(job, ensure_ascii=False))
    return job_path, job


class FakeRoundRunner:
    def __init__(self, data_root: Path, rates, *, providers=None, unsupported=None):
        self.data_root = data_root
        self.rates = list(rates)
        self.providers = providers or ["local/ollama/test-model"]
        self.unsupported = list(unsupported or [0.0] * len(self.rates))
        self.calls = []
        self.index = 0

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        pass_rate = self.rates[self.index]
        unsupported_rate = self.unsupported[self.index]
        self.index += 1
        run_id = f"FAKE-RUN-{self.index}"
        receipt_path = self.data_root / "runs" / f"{run_id}.json"
        lesson_path = self.data_root / "lesson_deltas" / f"{run_id}.md"
        MODULE.training_loop.write_private_text(lesson_path, f"# {run_id} lesson delta\n")
        result_provider = self.providers[0]
        passed_count = round(pass_rate * kwargs["batch"])
        unsupported_count = round(unsupported_rate * kwargs["batch"])
        full = {
            "schema_version": "maplab.hermes.line-run.v2",
            "evaluator_version": MODULE.training_loop.EVALUATOR_VERSION,
            "run_id": run_id,
            "local_only": True,
            "provider_policy": "loopback-ollama-only",
            "ollama_endpoint": MODULE.training_loop.DEFAULT_OLLAMA_URL,
            "model": "test-model",
            "inference_parameters": MODULE.training_loop.INFERENCE_PARAMETERS,
            "external_network_calls": 0,
            "loopback_ollama_calls": kwargs["batch"],
            "providers": self.providers,
            "pass_rate": pass_rate,
            "mean_score": pass_rate * 100,
            "unsupported_price_rate": unsupported_rate,
            "passed": passed_count,
            "unsupported_price_count": unsupported_count,
            "lowest_stage": "S3",
            "batch": kwargs["batch"],
            "seed": kwargs["seed"],
            "requested_stage": kwargs["stage"] or None,
            "lesson_delta": str(lesson_path),
            "results": [
                {
                    "provider": result_provider,
                    "inference_seed": kwargs["seed"] * 1000 + index,
                    "evaluation": {
                        "pass": index < passed_count,
                        "score": 100 if index < passed_count else 0,
                        "unsupported_money": ["999元"] if index < unsupported_count else [],
                    },
                }
                for index in range(kwargs["batch"])
            ],
        }
        MODULE.training_loop.write_private_json(receipt_path, full)
        return {key: value for key, value in full.items() if key != "results"} | {
            "receipt": str(receipt_path)
        }


class HermesLineTrainingSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data_root = self.root / "private-data"
        self.job_root = self.root / "durable-jobs"
        build_dataset(self.data_root)
        self.job_path, self.job = build_job(self.job_root)

    def tearDown(self):
        self.temp.cleanup()

    def call_supervise(self, runner, **overrides):
        kwargs = {
            "job_path": self.job_path,
            "job": self.job,
            "data_root": self.data_root,
            "max_rounds": 2,
            "max_seconds": 60,
            "batch": 10,
            "target_streak": 3,
            "target_pass_rate": 0.85,
            "regression_threshold": 2,
            "stage": "",
            "seed_base": 100,
            "round_runner": runner,
        }
        kwargs.update(overrides)
        with mock.patch.dict(os.environ, {"HERMES_LINE_LOCAL_MODEL": "test-model"}, clear=False):
            with mock.patch.object(MODULE, "DURABLE_JOB_ROOT", self.job_root):
                return MODULE.supervise(**kwargs)

    def test_same_job_receipt_resumes_until_target_streak(self):
        runner = FakeRoundRunner(self.data_root, [0.9, 0.9, 0.9])
        first, first_exit = self.call_supervise(runner)
        self.assertEqual(first_exit, 0)
        self.assertEqual(first["status"], "bounded_pause")
        self.assertEqual(first["success_streak"], 2)
        self.assertEqual(json.loads(self.job_path.read_text())["state"], "RUNNING")
        receipt_path = Path(first["supervisor_receipt"])

        self.job = json.loads(self.job_path.read_text(encoding="utf-8"))
        second, second_exit = self.call_supervise(runner, max_rounds=1)
        self.assertEqual(second_exit, 0)
        self.assertEqual(second["status"], "completed")
        self.assertEqual(second["success_streak"], 3)
        self.assertEqual(Path(second["supervisor_receipt"]), receipt_path)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(len(receipt["rounds"]), 3)
        self.assertTrue(all("lesson_delta" in item for item in receipt["rounds"]))
        self.assertNotIn("request", receipt)
        self.assertTrue(
            all(
                key not in round_result
                for round_result in receipt["rounds"]
                for key in ("customer", "target", "generated", "results")
            )
        )
        final_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        self.assertEqual(final_job["state"], "COMPLETED")
        self.assertEqual(final_job["request"], self.job["request"])
        self.assertFalse(final_job["last_result"]["customer_send"])
        self.assertEqual(receipt_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(receipt["external_network_calls"], 0)
        self.assertEqual(receipt["loopback_ollama_calls"], 30)

    def test_two_regressions_trigger_next_five_case_stage_diagnostic(self):
        runner = FakeRoundRunner(self.data_root, [1.0, 0.9, 0.8, 1.0])
        result, exit_code = self.call_supervise(
            runner,
            max_rounds=4,
            target_streak=7,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "bounded_pause")
        self.assertEqual(runner.calls[3]["stage"], "S3")
        self.assertEqual(runner.calls[3]["batch"], 5)

    def test_two_failed_qualification_rounds_require_method_review(self):
        runner = FakeRoundRunner(self.data_root, [0.4, 0.4, 0.9])
        result, exit_code = self.call_supervise(
            runner,
            max_rounds=3,
            target_streak=7,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["reason"], "plateau_method_review_required")
        self.assertTrue(result["method_review_required"])
        self.assertEqual(result["plateau_streak"], 2)
        self.assertEqual(len(runner.calls), 2)
        receipt = json.loads(Path(result["supervisor_receipt"]).read_text(encoding="utf-8"))
        self.assertTrue(receipt["method_review_required"])
        self.assertEqual(receipt["plateau_streak"], 2)
        final_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        self.assertEqual(final_job["state"], "RUNNING")
        self.assertEqual(final_job["current_phase"], "method-redesign")
        self.assertIn("zero model calls", final_job["next_bounded_action"])

    def test_method_review_resume_makes_zero_model_calls_or_attempts(self):
        runner = FakeRoundRunner(self.data_root, [0.4, 0.4, 0.9])
        first, _ = self.call_supervise(runner, max_rounds=3, target_streak=7)
        first_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        self.assertEqual(first_job["attempt"], 1)
        self.job = first_job

        second, second_exit = self.call_supervise(runner, max_rounds=1, target_streak=7)
        self.assertEqual(second_exit, 0)
        self.assertEqual(second["reason"], "plateau_method_review_required")
        self.assertEqual(len(runner.calls), 2)
        resumed_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        self.assertEqual(resumed_job["attempt"], 1)
        self.assertEqual(resumed_job["current_phase"], "method-redesign")

    def test_legacy_receipt_without_plateau_fields_migrates_without_new_round(self):
        runner = FakeRoundRunner(self.data_root, [0.4, 0.4, 0.9])
        first, _ = self.call_supervise(runner, max_rounds=3, target_streak=7)
        receipt_path = Path(first["supervisor_receipt"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt.pop("plateau_streak")
        receipt.pop("method_review_required")
        MODULE.training_loop.write_private_json(receipt_path, receipt)
        self.job = json.loads(self.job_path.read_text(encoding="utf-8"))

        second, second_exit = self.call_supervise(runner, max_rounds=1, target_streak=7)
        self.assertEqual(second_exit, 0)
        self.assertEqual(second["reason"], "plateau_method_review_required")
        self.assertEqual(len(runner.calls), 2)
        migrated = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(migrated["plateau_streak"], 2)
        self.assertTrue(migrated["method_review_required"])

    def test_wall_bound_pauses_without_starting_another_round(self):
        runner = FakeRoundRunner(self.data_root, [0.9])
        ticks = iter([0.0, 11.0])
        result, exit_code = self.call_supervise(
            runner,
            max_seconds=10,
            monotonic=lambda: next(ticks),
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["reason"], "max_seconds_reached")
        self.assertEqual(runner.calls, [])

    def test_nonlocal_round_receipt_blocks_the_job(self):
        runner = FakeRoundRunner(
            self.data_root,
            [0.9],
            providers=["external/provider"],
        )
        result, exit_code = self.call_supervise(runner, max_rounds=1)
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason"], "provider_policy_violation")
        final_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        self.assertEqual(final_job["state"], "BLOCKED")

    def test_canonical_job_path_contract_and_required_cli(self):
        with mock.patch.object(MODULE, "DURABLE_JOB_ROOT", self.job_root):
            path, job = MODULE.read_durable_job(self.job_path)
        self.assertEqual(path, self.job_path.resolve())
        self.assertEqual(job["job_type"], "hermes-line-training")
        parsed = MODULE.build_parser().parse_args(["--job-path", str(self.job_path)])
        self.assertEqual(parsed.job_path, str(self.job_path))

    def test_resume_derives_private_data_root_from_canonical_receipt(self):
        runner = FakeRoundRunner(self.data_root, [0.4, 0.4])
        first, _ = self.call_supervise(runner, max_rounds=2, target_streak=7)
        resumed_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        wrong_default = self.root / "wrong-default"

        with mock.patch.dict(
            os.environ,
            {"HERMES_LINE_DATA_ROOT": str(wrong_default)},
            clear=False,
        ):
            resolved = MODULE.resolve_supervisor_data_root(resumed_job)

        self.assertEqual(resolved, self.data_root)
        self.assertEqual(first["reason"], "plateau_method_review_required")

    def test_child_environment_drops_cloud_keys_and_proxies(self):
        with mock.patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "must-not-pass", "HTTPS_PROXY": "http://proxy.invalid"},
            clear=False,
        ):
            child = MODULE._sanitized_child_env(self.data_root)
        self.assertNotIn("OPENROUTER_API_KEY", child)
        self.assertNotIn("HTTPS_PROXY", child)
        self.assertEqual(child["HERMES_LINE_PROVIDER"], "local-only")
        self.assertEqual(child["NO_PROXY"], "127.0.0.1,localhost,::1")

    def test_main_marks_canonical_job_blocked_when_corpus_is_not_private(self):
        (self.data_root / "eval.jsonl").chmod(0o644)
        with mock.patch.object(MODULE, "DURABLE_JOB_ROOT", self.job_root):
            with redirect_stderr(io.StringIO()):
                exit_code = MODULE.main(
                    ["--job-path", str(self.job_path), "--data-root", str(self.data_root)]
                )
        self.assertEqual(exit_code, 3)
        final_job = json.loads(self.job_path.read_text(encoding="utf-8"))
        self.assertEqual(final_job["state"], "BLOCKED")
        self.assertEqual(final_job["last_result"]["status"], "blocked")
        self.assertFalse(final_job["last_result"]["customer_send"])

    def test_job_lock_busy_does_not_mutate_job_or_start_round(self):
        runner = FakeRoundRunner(self.data_root, [0.9])
        before = self.job_path.read_text(encoding="utf-8")
        with mock.patch.object(MODULE, "DURABLE_JOB_ROOT", self.job_root):
            descriptor = MODULE._acquire_job_lock(self.job_path)
            self.assertIsNotNone(descriptor)
            try:
                result, exit_code = MODULE.supervise(
                    job_path=self.job_path,
                    job=self.job,
                    data_root=self.data_root,
                    max_rounds=1,
                    max_seconds=60,
                    batch=10,
                    target_streak=7,
                    target_pass_rate=0.85,
                    regression_threshold=2,
                    stage="",
                    seed_base=100,
                    round_runner=runner,
                )
            finally:
                MODULE._release_job_lock(descriptor)
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "running")
        self.assertEqual(result["reason"], "already_running")
        self.assertEqual(runner.calls, [])
        self.assertEqual(self.job_path.read_text(encoding="utf-8"), before)

    def test_lock_held_config_error_does_not_mutate_canonical_job(self):
        before = self.job_path.read_bytes()
        with mock.patch.object(MODULE, "DURABLE_JOB_ROOT", self.job_root):
            descriptor = MODULE._acquire_job_lock(self.job_path)
            self.assertIsNotNone(descriptor)
            try:
                with mock.patch.dict(
                    os.environ,
                    {"HERMES_LINE_PROVIDER": "cloud"},
                    clear=False,
                ):
                    with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                        exit_code = MODULE.main(
                            ["--job-path", str(self.job_path), "--data-root", str(self.data_root)]
                        )
            finally:
                MODULE._release_job_lock(descriptor)
        self.assertEqual(exit_code, 0)
        self.assertEqual(self.job_path.read_bytes(), before)

    def test_lock_held_internal_error_does_not_mutate_canonical_job(self):
        before = self.job_path.read_bytes()
        with mock.patch.object(MODULE, "DURABLE_JOB_ROOT", self.job_root):
            descriptor = MODULE._acquire_job_lock(self.job_path)
            self.assertIsNotNone(descriptor)
            try:
                with mock.patch.object(
                    MODULE.training_loop,
                    "resolve_data_root",
                    side_effect=RuntimeError("synthetic internal failure"),
                ):
                    with redirect_stderr(io.StringIO()):
                        exit_code = MODULE.main(
                            ["--job-path", str(self.job_path), "--data-root", str(self.data_root)]
                        )
            finally:
                MODULE._release_job_lock(descriptor)
        self.assertEqual(exit_code, 5)
        self.assertEqual(self.job_path.read_bytes(), before)

    def test_stale_error_cannot_overwrite_newer_job_generation(self):
        expected = dict(self.job)
        advanced = dict(self.job)
        advanced["state"] = "RUNNING"
        advanced["attempt"] = 1
        advanced["last_result"] = {"status": "running", "reason": "newer checkpoint"}
        private_write(self.job_path, json.dumps(advanced, ensure_ascii=False))
        before = self.job_path.read_bytes()
        with mock.patch.object(MODULE, "DURABLE_JOB_ROOT", self.job_root):
            changed = MODULE._transition_after_error_if_idle(
                self.job_path,
                expected_job=expected,
                state="BLOCKED",
                reason="stale error",
                result={"status": "blocked"},
                next_action="do not overwrite",
            )
        self.assertFalse(changed)
        self.assertEqual(self.job_path.read_bytes(), before)

    def test_resume_cannot_lower_locked_qualification_target(self):
        runner = FakeRoundRunner(self.data_root, [0.9, 0.9])
        first, _ = self.call_supervise(runner, max_rounds=1, target_streak=7)
        self.assertEqual(first["success_streak"], 1)
        self.job = json.loads(self.job_path.read_text(encoding="utf-8"))
        second, _ = self.call_supervise(runner, max_rounds=1, target_streak=1)
        self.assertEqual(second["status"], "bounded_pause")
        self.assertEqual(second["success_streak"], 2)
        receipt = json.loads(Path(second["supervisor_receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["qualification_contract"]["target_streak"], 7)
        self.assertTrue(receipt["resume_overrides_ignored"])

    def test_resume_cannot_repeat_seed_by_changing_seed_base(self):
        runner = FakeRoundRunner(self.data_root, [0.9, 0.9])
        self.call_supervise(runner, max_rounds=1, target_streak=7, seed_base=100)
        self.job = json.loads(self.job_path.read_text(encoding="utf-8"))
        second, _ = self.call_supervise(
            runner,
            max_rounds=1,
            target_streak=7,
            seed_base=99,
        )
        self.assertEqual([call["seed"] for call in runner.calls], [100, 101])
        receipt = json.loads(Path(second["supervisor_receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(receipt["qualification_contract"]["seed_base"], 100)
        self.assertTrue(receipt["resume_overrides_ignored"])

    def test_replayed_round_receipt_is_blocked(self):
        base = FakeRoundRunner(self.data_root, [0.9])
        cached = None

        def replay_runner(**kwargs):
            nonlocal cached
            if cached is None:
                cached = base(**kwargs)
            return cached

        result, exit_code = self.call_supervise(
            replay_runner,
            max_rounds=2,
            target_streak=7,
        )
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_replay_detected")
        receipt = json.loads(Path(result["supervisor_receipt"]).read_text(encoding="utf-8"))
        self.assertEqual(len(receipt["rounds"]), 1)
        self.assertEqual(json.loads(self.job_path.read_text())["state"], "BLOCKED")

    def test_tampered_lesson_delta_blocks_resume_before_new_round(self):
        runner = FakeRoundRunner(self.data_root, [0.9, 0.9])
        first, _ = self.call_supervise(runner, max_rounds=1, target_streak=7)
        receipt = json.loads(Path(first["supervisor_receipt"]).read_text(encoding="utf-8"))
        MODULE.training_loop.write_private_text(
            Path(receipt["rounds"][0]["lesson_delta"]), "# tampered\n"
        )
        self.job = json.loads(self.job_path.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(MODULE.SupervisorError, "history_tampered"):
            self.call_supervise(runner, max_rounds=1, target_streak=7)
        self.assertEqual(len(runner.calls), 1)

    def test_forged_completed_streak_without_rounds_is_rejected(self):
        runner = FakeRoundRunner(self.data_root, [0.9])
        ticks = iter([0.0, 11.0])
        first, _ = self.call_supervise(
            runner,
            max_seconds=10,
            target_streak=7,
            monotonic=lambda: next(ticks),
        )
        receipt_path = Path(first["supervisor_receipt"])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["rounds"], [])
        receipt["status"] = "completed"
        receipt["success_streak"] = 7
        MODULE.training_loop.write_private_json(receipt_path, receipt)
        self.job = json.loads(self.job_path.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(MODULE.SupervisorError, "derived_state_tampered"):
            self.call_supervise(runner, max_rounds=1, target_streak=7)
        self.assertEqual(runner.calls, [])

    def test_nonfinite_or_incoherent_metrics_are_blocked(self):
        base = FakeRoundRunner(self.data_root, [0.9])

        def invalid_runner(**kwargs):
            payload = base(**kwargs)
            receipt_path = Path(payload["receipt"])
            full = json.loads(receipt_path.read_text(encoding="utf-8"))
            full["pass_rate"] = float("nan")
            MODULE.training_loop.write_private_json(receipt_path, full)
            return payload

        result, exit_code = self.call_supervise(invalid_runner, max_rounds=1)
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_metrics_invalid")

    def test_failed_sample_cannot_claim_perfect_aggregate(self):
        base = FakeRoundRunner(self.data_root, [1.0])

        def dishonest_runner(**kwargs):
            payload = base(**kwargs)
            receipt_path = Path(payload["receipt"])
            full = json.loads(receipt_path.read_text(encoding="utf-8"))
            full["results"][0]["evaluation"]["pass"] = False
            full["results"][0]["evaluation"]["score"] = 0
            MODULE.training_loop.write_private_json(receipt_path, full)
            return payload

        result, exit_code = self.call_supervise(
            dishonest_runner,
            max_rounds=1,
            target_streak=1,
        )
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_metrics_invalid")

    def test_unsupported_sample_cannot_claim_zero_unsupported_aggregate(self):
        base = FakeRoundRunner(self.data_root, [1.0])

        def dishonest_runner(**kwargs):
            payload = base(**kwargs)
            receipt_path = Path(payload["receipt"])
            full = json.loads(receipt_path.read_text(encoding="utf-8"))
            full["results"][0]["evaluation"]["unsupported_money"] = ["999元"]
            MODULE.training_loop.write_private_json(receipt_path, full)
            return payload

        result, exit_code = self.call_supervise(
            dishonest_runner,
            max_rounds=1,
            target_streak=1,
        )
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_metrics_invalid")

    def test_mean_score_must_match_per_sample_evaluations(self):
        base = FakeRoundRunner(self.data_root, [1.0])

        def dishonest_runner(**kwargs):
            payload = base(**kwargs)
            receipt_path = Path(payload["receipt"])
            full = json.loads(receipt_path.read_text(encoding="utf-8"))
            full["mean_score"] = 99.9
            MODULE.training_loop.write_private_json(receipt_path, full)
            return payload

        result, exit_code = self.call_supervise(
            dishonest_runner,
            max_rounds=1,
            target_streak=1,
        )
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_metrics_invalid")

    def test_honest_per_sample_aggregate_can_complete(self):
        runner = FakeRoundRunner(self.data_root, [1.0])
        result, exit_code = self.call_supervise(
            runner,
            max_rounds=1,
            target_streak=1,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "completed")

    def test_stage_only_rounds_never_count_toward_promotion(self):
        runner = FakeRoundRunner(self.data_root, [1.0, 1.0, 1.0])
        result, exit_code = self.call_supervise(
            runner,
            max_rounds=3,
            target_streak=3,
            stage="S3",
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "bounded_pause")
        self.assertEqual(result["success_streak"], 0)

    def test_owner_review_state_is_not_resumed_or_mutated(self):
        self.job["state"] = "OWNER_REVIEW"
        private_write(self.job_path, json.dumps(self.job, ensure_ascii=False))
        before = self.job_path.read_text(encoding="utf-8")
        runner = FakeRoundRunner(self.data_root, [0.9])
        result, exit_code = self.call_supervise(runner, max_rounds=1)
        self.assertEqual(exit_code, 4)
        self.assertEqual(result["status"], "owner_review")
        self.assertEqual(runner.calls, [])
        self.assertEqual(self.job_path.read_text(encoding="utf-8"), before)

    def test_malformed_round_payload_blocks_without_traceback(self):
        result, exit_code = self.call_supervise(lambda **kwargs: [], max_rounds=1)
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_output_invalid")
        self.assertEqual(json.loads(self.job_path.read_text())["state"], "BLOCKED")

    def test_round_batch_is_bound_to_supervisor_request(self):
        base = FakeRoundRunner(self.data_root, [1.0])

        def wrong_batch(**kwargs):
            return base(**(kwargs | {"batch": 1}))

        result, exit_code = self.call_supervise(wrong_batch, max_rounds=1)
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_invocation_mismatch")

    def test_round_seed_is_bound_to_supervisor_request(self):
        base = FakeRoundRunner(self.data_root, [1.0])

        def wrong_seed(**kwargs):
            return base(**(kwargs | {"seed": kwargs["seed"] + 1}))

        result, exit_code = self.call_supervise(wrong_seed, max_rounds=1)
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_invocation_mismatch")

    def test_round_stage_is_bound_to_supervisor_request(self):
        base = FakeRoundRunner(self.data_root, [1.0])

        def wrong_stage(**kwargs):
            return base(**(kwargs | {"stage": "S3"}))

        result, exit_code = self.call_supervise(wrong_stage, max_rounds=1)
        self.assertEqual(exit_code, 3)
        self.assertEqual(result["reason"], "round_invocation_mismatch")

    def test_regression_trigger_cannot_complete_before_diagnostic(self):
        runner = FakeRoundRunner(self.data_root, [1.0, 0.95, 0.9])
        result, exit_code = self.call_supervise(
            runner,
            max_rounds=3,
            batch=20,
            target_streak=3,
            regression_threshold=2,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "bounded_pause")
        self.assertEqual(result["success_streak"], 0)
        receipt = json.loads(Path(result["supervisor_receipt"]).read_text(encoding="utf-8"))
        self.assertTrue(receipt["diagnostic_mode"])
        self.assertEqual(json.loads(self.job_path.read_text())["state"], "RUNNING")


if __name__ == "__main__":
    unittest.main()
