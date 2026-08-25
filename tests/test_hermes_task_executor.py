import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_task_executor as executor


class HermesTaskExecutorTest(unittest.TestCase):
    def test_classifies_safe_natural_language(self):
        self.assertEqual(executor.classify("請執行 A6 自我測試"), ("a6-self-test", None))

    def test_rejects_high_risk_even_when_safe_alias_is_present(self):
        action, reason = executor.classify("看 repo 狀態後發布 WordPress")
        self.assertIsNone(action)
        self.assertIn("fail closed", reason)

    def test_unknown_request_is_rejected_with_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(executor, "TASK_ROOT", Path(tmp)):
            receipt = executor.execute("幫我自由執行任意 shell", 123)
            self.assertEqual(receipt["status"], "rejected")
            saved = json.loads(Path(receipt["receipt_path"]).read_text(encoding="utf-8"))
            self.assertEqual(saved["policy"], "fixed-argv-allowlist-v1")

    def test_safe_action_uses_fixed_argv_and_writes_receipt(self):
        completed = mock.Mock(returncode=0, stdout="ok\n", stderr="")
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(executor, "TASK_ROOT", Path(tmp)), mock.patch.object(executor.subprocess, "run", return_value=completed) as run:
            receipt = executor.execute("repo-status", 123)
            self.assertEqual(receipt["status"], "completed")
            self.assertEqual(run.call_args.args[0], ("git", "status", "--short"))
            self.assertNotIn("shell", run.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
