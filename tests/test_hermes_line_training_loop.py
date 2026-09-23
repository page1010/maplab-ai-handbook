import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "hermes_line_training_loop.py"
SPEC = importlib.util.spec_from_file_location("hermes_line_training_loop_tested", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def private_write(path: Path, payload: str) -> None:
    path.write_text(payload, encoding="utf-8")
    path.chmod(0o600)


def build_dataset(root: Path) -> None:
    root.chmod(0o700)
    manifest = {
        "schema": "maplab.hermes.line_pairs.v1",
        "anonymization": "customer sender names removed/replaced; conversation IDs hashed",
        "split": "80/20 by conversation hash",
    }
    train = {
        "id": "train-1",
        "stage": "S2_DATA",
        "conversation_id": "train-conversation",
        "customer": "想詢問活動",
        "target": "請問日期、人數、地點？",
        "context": [],
    }
    evaluation = {
        "id": "eval-1",
        "stage": "S2_DATA",
        "conversation_id": "eval-conversation",
        "customer": "想詢問活動",
        "target": "請問日期、人數、地點？",
        "context": [],
    }
    private_write(root / "manifest.json", json.dumps(manifest, ensure_ascii=False))
    private_write(root / "train.jsonl", json.dumps(train, ensure_ascii=False) + "\n")
    private_write(root / "eval.jsonl", json.dumps(evaluation, ensure_ascii=False) + "\n")


class HermesLineTrainingLoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data_root = Path(self.temp.name)
        build_dataset(self.data_root)

    def tearDown(self):
        self.temp.cleanup()

    def test_data_root_comes_from_environment_and_must_be_absolute(self):
        with mock.patch.dict(os.environ, {"HERMES_LINE_DATA_ROOT": str(self.data_root)}):
            self.assertEqual(MODULE.resolve_data_root(), self.data_root)
        with self.assertRaisesRegex(MODULE.TrainingConfigError, "data_root_must_be_absolute"):
            MODULE.resolve_data_root("relative/private-data")

    def test_only_loopback_ollama_and_local_only_provider_are_accepted(self):
        with mock.patch.dict(os.environ, {"HERMES_LINE_PROVIDER": "local-only"}, clear=False):
            url, model = MODULE.resolve_local_provider()
        self.assertEqual(url, MODULE.DEFAULT_OLLAMA_URL)
        self.assertEqual(model, MODULE.DEFAULT_OLLAMA_MODEL)
        with self.assertRaisesRegex(MODULE.TrainingConfigError, "not_numeric_loopback"):
            MODULE.validate_loopback_url("http://api.example.com/v1/chat")
        for unsafe_url in (
            "http://localhost:11434/api/generate",
            "http://127.0.0.1:8080/api/generate",
            "http://127.0.0.1:11434/collect-private-line-corpus",
        ):
            with self.subTest(unsafe_url=unsafe_url):
                with self.assertRaises(MODULE.TrainingConfigError):
                    MODULE.validate_loopback_url(unsafe_url)
        with mock.patch.dict(os.environ, {"HERMES_LINE_PROVIDER": "cloud"}, clear=False):
            with self.assertRaisesRegex(MODULE.TrainingConfigError, "external_provider_forbidden"):
                MODULE.resolve_local_provider()

    def test_permissive_corpus_permissions_fail_closed(self):
        (self.data_root / "train.jsonl").chmod(0o644)
        with self.assertRaisesRegex(MODULE.DatasetError, "permissions_not_private:train.jsonl"):
            MODULE.validate_dataset_root(self.data_root)

    def test_round_writes_private_local_only_receipts_and_streak_state(self):
        def fake_generate(messages, **kwargs):
            self.assertEqual(kwargs["ollama_url"], MODULE.DEFAULT_OLLAMA_URL)
            self.assertEqual(kwargs["seed"], 7000)
            return "請問日期、人數、地點？", "local/ollama/test-model"

        summary = MODULE.run_training_round(
            data_root=self.data_root,
            batch=1,
            seed=7,
            stage="",
            ollama_url=MODULE.DEFAULT_OLLAMA_URL,
            model="test-model",
            timeout=5,
            generate_fn=fake_generate,
        )

        self.assertTrue(summary["local_only"])
        self.assertEqual(summary["providers"], ["local/ollama/test-model"])
        self.assertEqual(summary["pass_rate"], 1.0)
        self.assertEqual(summary["unsupported_price_rate"], 0.0)
        self.assertEqual(summary["external_network_calls"], 0)
        self.assertEqual(summary["loopback_ollama_calls"], 1)
        self.assertEqual(summary["inference_parameters"], MODULE.INFERENCE_PARAMETERS)
        self.assertEqual(summary["results"][0]["inference_seed"], 7000)
        lesson_delta = Path(summary["lesson_delta"])
        self.assertTrue(lesson_delta.is_file())
        self.assertEqual(lesson_delta.stat().st_mode & 0o777, 0o600)
        receipt = Path(summary["receipt"])
        self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
        self.assertEqual(receipt.parent.stat().st_mode & 0o777, 0o700)
        state_path = self.data_root / "loop_state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertTrue(state["local_only"])
        self.assertEqual(state["success_streak"], 1)
        self.assertEqual(state["regression_streak"], 0)
        self.assertEqual(state["external_network_calls"], 0)
        self.assertEqual(state["loopback_ollama_calls"], 1)
        self.assertEqual(state_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.data_root / "current_lessons.md").stat().st_mode & 0o777, 0o600)
        self.assertIn(str(lesson_delta), (self.data_root / "current_lessons.md").read_text())

    def test_nonlocal_generator_label_is_rejected_before_a_receipt_is_written(self):
        def fake_generate(messages, **kwargs):
            return "請問日期、人數、地點？", "external/provider"

        with self.assertRaisesRegex(MODULE.TrainingConfigError, "provider_policy_violation"):
            MODULE.run_training_round(
                data_root=self.data_root,
                batch=1,
                seed=7,
                stage="",
                ollama_url=MODULE.DEFAULT_OLLAMA_URL,
                model="test-model",
                timeout=5,
                generate_fn=fake_generate,
            )
        self.assertFalse((self.data_root / "runs").exists())

    def test_training_module_has_no_openrouter_call_path(self):
        source = MODULE_PATH.read_text(encoding="utf-8").lower()
        self.assertNotIn("openrouter", source)
        self.assertNotIn("load_free_env_key", source)

    def test_local_request_pins_temperature_and_seed(self):
        captured = {}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"response":"ok"}'

        class Opener:
            def open(self, request, timeout):
                captured["body"] = json.loads(request.data.decode("utf-8"))
                captured["timeout"] = timeout
                return Response()

        with mock.patch.object(MODULE.urllib.request, "build_opener", return_value=Opener()):
            reply, provider = MODULE.generate_local(
                [{"role": "user", "content": "private"}],
                ollama_url=MODULE.DEFAULT_OLLAMA_URL,
                model="test-model",
                timeout=5,
                seed=1234,
            )
        self.assertEqual(reply, "ok")
        self.assertEqual(provider, "local/ollama/test-model")
        self.assertEqual(captured["body"]["options"], {"temperature": 0, "seed": 1234})


if __name__ == "__main__":
    unittest.main()
