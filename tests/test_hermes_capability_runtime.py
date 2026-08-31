import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_capability_runtime as runtime


class HermesCapabilityRuntimeTest(unittest.TestCase):
    def test_capability_answer_is_gateway_model_and_memory_truth(self):
        snapshot = {
            "launchd": {"loaded": True, "state": "running", "pid": "12", "last_exit_code": None},
            "providers": {
                "configured_chain": ["provider/a", "provider/b"],
                "local_fallback": "gemma4:latest",
                "local_fallback_enabled": False,
                "last_provider": "provider/b",
            },
            "local_access": {"actions": ["runtime-status", "signal-status"]},
            "memory": {"history_limit_messages": 12},
        }
        with mock.patch.object(runtime, "capability_snapshot", return_value=snapshot):
            text = runtime.format_capabilities()
        self.assertIn("不是零存取", text)
        self.assertIn("固定白名單", text)
        self.assertIn("provider/a → provider/b", text)
        self.assertIn("最近成功 provider：provider/b", text)
        self.assertIn("本機 fallback 已停用", text)
        self.assertNotIn("最後才用 gemma4:latest", text)
        self.assertIn("跨重啟保存最近 12 則", text)
        self.assertIn("照片會私密留檔", text)
        self.assertNotIn("具體模型名稱/版本未知", text)
        self.assertNotIn("等 Fable5", text)

    def test_signal_status_marks_historical_report_stale(self):
        snapshot = {
            "launchd": {"loaded": True, "state": "not running", "runs": "18", "last_exit_code": "1"},
            "latest_report": "/tmp/limit_up_chip_story_2026-05-22.md",
            "latest_report_date": "2026-05-22",
            "latest_report_mtime": "2026-06-16T10:00:00+08:00",
        }
        with mock.patch.object(runtime, "signal_status_snapshot", return_value=snapshot), mock.patch.object(
            runtime.time, "strftime", return_value="2026-08-26"
        ):
            text = runtime.format_signal_status()
        self.assertIn("last_exit=1", text)
        self.assertIn("不是今天 2026-08-26 的產出", text)
        self.assertIn("不採用手冊中的歷史快照", text)

    def test_private_json_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "private" / "state.json"
            runtime.write_private_json(path, {"ok": True})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)


if __name__ == "__main__":
    unittest.main()
