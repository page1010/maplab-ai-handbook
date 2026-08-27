import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_deerflow_bridge as bridge


class _Completed:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class _Worker:
    pid = 99999
    returncode = 0

    def communicate(self, input=None, timeout=None):
        return (
            json.dumps({"answer": "研究結果", "model": bridge.LOCAL_MODEL, "tools_used": [], "usage": {}}),
            "",
        )

    def poll(self):
        return 0


class HermesDeerFlowBridgeTest(unittest.TestCase):
    def test_public_classifier_rejects_private_context_paths_and_attachments(self):
        for request in (
            "/research-public 研究剛才那位客戶的報價",
            "/research-public 研究附件裡的內容",
            "/research-public 比較 /Users/me/private.txt",
            "/research-public 查 http://127.0.0.1:8000",
        ):
            query, rejection = bridge.parse_public_query(request)
            self.assertIsNone(query, request)
            self.assertIn("fail closed", rejection, request)

    def _task(self, root: Path) -> Path:
        task_dir = root / "DFR-20260827-120000-abcdef"
        task_dir.mkdir(mode=0o700)
        (task_dir / "question.txt").write_text("研究 DeerFlow 官方文件", encoding="utf-8")
        (task_dir / "receipt.json").write_text(
            json.dumps({"task_id": task_dir.name, "status": "accepted", "action": "deerflow-public-research"}),
            encoding="utf-8",
        )
        return task_dir

    def test_config_drift_stops_before_worker_start(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(bridge, "TASK_ROOT", Path(tmp)):
            task_dir = self._task(Path(tmp))
            with mock.patch.object(bridge, "_git_commit", return_value=bridge.EXPECTED_COMMIT), mock.patch.object(
                bridge, "provider_gate", return_value=(True, "ok")
            ), mock.patch.object(bridge.subprocess, "run", return_value=_Completed(returncode=1)), mock.patch.object(
                bridge.subprocess, "Popen"
            ) as popen:
                self.assertEqual(bridge.supervise(str(task_dir), "local"), 1)
                popen.assert_not_called()
            receipt = json.loads((task_dir / "receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["network_calls"], 0)
            self.assertIn("config validation", receipt["reason"])

    def test_child_disables_dotenv_and_uses_unique_job_thread(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(bridge, "TASK_ROOT", Path(tmp)):
            task_dir = self._task(Path(tmp))
            with mock.patch.object(bridge, "_git_commit", return_value=bridge.EXPECTED_COMMIT), mock.patch.object(
                bridge, "provider_gate", return_value=(True, "ok")
            ), mock.patch.object(bridge.subprocess, "run", return_value=_Completed(returncode=0)), mock.patch.object(
                bridge.subprocess, "Popen", return_value=_Worker()
            ) as popen:
                self.assertEqual(bridge.supervise(str(task_dir), "local"), 0)
                args, kwargs = popen.call_args
                self.assertEqual(kwargs["env"]["PYTHON_DOTENV_DISABLED"], "1")
                self.assertNotIn("A6_BOT_TOKEN", kwargs["env"])
                self.assertIn(f"dfr-{task_dir.name}", args[0])

if __name__ == "__main__":
    unittest.main()
