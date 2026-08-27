import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_task_executor as executor
from bot_a6 import hermes_durable_job_router as durable_router


class HermesTaskExecutorTest(unittest.TestCase):
    def test_classifies_safe_natural_language(self):
        self.assertEqual(executor.classify("請執行 A6 自我測試"), ("a6-self-test", None))

    def test_classifies_runtime_and_signal_readback(self):
        self.assertEqual(executor.classify("幫我查 Hermes runtime 狀態"), ("runtime-status", None))
        self.assertEqual(executor.classify("現在動能名單狀態如何"), ("signal-status", None))

    def test_rejects_high_risk_even_when_safe_alias_is_present(self):
        action, reason = executor.classify("看 repo 狀態後發布 WordPress")
        self.assertIsNone(action)
        self.assertIn("fail closed", reason)

    def test_natural_long_running_goals_route_without_manual_research_command(self):
        self.assertEqual(executor.classify("讓 A8 生歌、做影片並上傳 YouTube 給我看"), ("durable-job", None))
        self.assertEqual(executor.classify("Hermes 用 LINE 對話持續多跑三輪訓練"), ("durable-job", None))
        self.assertEqual(
            executor.classify("深入研究 DeerFlow 官方 GitHub 與 releases，至少 8 個來源，完成後通知"),
            ("durable-job", None),
        )

    def test_youtube_publication_can_be_explicit_but_wordpress_stays_denied(self):
        self.assertEqual(executor.classify("讓 A8 做影片並發布到 YouTube"), ("durable-job", None))
        action, reason = executor.classify("持續做影片並發布 WordPress")
        self.assertIsNone(action)
        self.assertTrue(reason)

    def test_rejects_schedule_mutation_but_allows_status_readback(self):
        action, reason = executor.classify("修改 launchd 後看 repo 狀態")
        self.assertIsNone(action)
        self.assertIn("fail closed", reason)
        self.assertIsNone(executor.classify("restart launchd and show repo status")[0])
        self.assertIsNone(executor.classify("重跑排程後查動能名單")[0])
        self.assertEqual(executor.classify("查 gateway 狀態"), ("runtime-status", None))

    def test_unknown_request_is_rejected_with_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(executor, "TASK_ROOT", Path(tmp)):
            receipt = executor.execute("幫我自由執行任意 shell", 123)
            self.assertEqual(receipt["status"], "rejected")
            saved = json.loads(Path(receipt["receipt_path"]).read_text(encoding="utf-8"))
            self.assertEqual(saved["policy"], "fixed-argv-allowlist-v2")
            self.assertEqual(Path(receipt["receipt_path"]).stat().st_mode & 0o777, 0o600)
            self.assertEqual(Path(receipt["receipt_path"]).parent.stat().st_mode & 0o777, 0o700)

    def test_safe_action_uses_fixed_argv_and_writes_receipt(self):
        completed = mock.Mock(returncode=0, stdout="ok\n", stderr="")
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(executor, "TASK_ROOT", Path(tmp)), mock.patch.object(executor.subprocess, "run", return_value=completed) as run:
            receipt = executor.execute("repo-status", 123)
            self.assertEqual(receipt["status"], "completed")
            self.assertEqual(run.call_args.args[0], ("git", "status", "--short"))
            self.assertNotIn("shell", run.call_args.kwargs)

    def test_a8_durable_job_is_created_without_starting_external_worker(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            durable_router, "JOB_ROOT", Path(tmp)
        ), mock.patch.object(executor.subprocess, "Popen") as popen:
            receipt = executor.execute("讓 A8 生歌、做影片並上傳 YouTube 給我看", 123, chat_id=456)
            self.assertEqual(receipt["action"], "durable-job")
            self.assertEqual(receipt["job_type"], "a8-production")
            self.assertEqual(receipt["job_state"], "RUNNING")
            self.assertTrue(Path(receipt["receipt_path"]).exists())
            popen.assert_not_called()

    def test_line_goal_starts_a_bounded_local_supervisor_chunk(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            durable_router, "JOB_ROOT", Path(tmp)
        ), mock.patch.object(executor, "LINE_TRAINING_SUPERVISOR", Path(__file__)), mock.patch.object(
            executor.subprocess, "Popen", return_value=mock.Mock(pid=4321)
        ) as popen, mock.patch.dict(
            executor.os.environ,
            {"HERMES_LINE_DATA_ROOT": "/Users/example/.maplab/a6-hermes-training"},
            clear=False,
        ):
            receipt = executor.execute("Hermes 用 LINE 對話持續多跑三輪訓練", 123, chat_id=456)

        self.assertEqual(receipt["action"], "durable-job")
        self.assertEqual(receipt["job_type"], "hermes-line-training")
        self.assertEqual(receipt["job_state"], "RUNNING")
        argv = popen.call_args.args[0]
        self.assertIn("--job-path", argv)
        self.assertEqual(argv[-6:], executor.LINE_SUPERVISOR_CHUNK)
        self.assertEqual(popen.call_args.kwargs["env"]["HERMES_LINE_PROVIDER"], "local-only")
        self.assertNotIn("OPENROUTER_API_KEY", popen.call_args.kwargs["env"])


if __name__ == "__main__":
    unittest.main()
