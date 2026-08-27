import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_durable_job_router as router


class HermesDurableJobRouterTest(unittest.TestCase):
    def test_routes_a8_line_and_public_research_without_slash_commands(self):
        self.assertEqual(router.classify_durable_intent("讓 A8 生歌、做影片並上傳 YouTube 給我看").job_type, "a8-production")
        self.assertEqual(router.classify_durable_intent("Hermes 用 LINE 對話持續多跑三輪訓練").job_type, "hermes-line-training")
        self.assertEqual(
            router.classify_durable_intent("深入研究 DeerFlow 官方 GitHub 與 releases，至少 8 個來源，完成後通知").job_type,
            "public-research",
        )
        self.assertIsNone(router.classify_durable_intent("你覺得 DeerFlow 好用嗎？"))

    def test_normalizes_full_width_and_zero_width_text(self):
        intent = router.classify_durable_intent("Ａ８\u200b 生歌、做影片並上傳 ＹｏｕＴｕｂｅ 給我看")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.job_type, "a8-production")

    def test_durable_scope_rejects_trading_deletion_and_customer_send(self):
        intent = router.classify_durable_intent("持續跑完並刪除舊資料")
        self.assertIn("fail closed", router.validate_durable_request("持續跑完並刪除舊資料", intent))
        line_intent = router.classify_durable_intent("LINE 訓練持續多跑幾輪並自動發送客戶")
        self.assertIn("fail closed", router.validate_durable_request("LINE 訓練持續多跑幾輪並自動發送客戶", line_intent))

    def test_job_is_private_atomic_and_keeps_authorization(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(router, "JOB_ROOT", Path(tmp)):
            request = "讓 A8 生歌、做影片並上傳 YouTube 給我看"
            intent = router.classify_durable_intent(request)
            job = router.create_durable_job(request, intent, 123, chat_id=456, chat_type="private")
            job_path = Path(job["job_path"])
            saved = json.loads(job_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["state"], "ACCEPTED")
            self.assertTrue(saved["authorization"]["draft_upload"])
            self.assertFalse(saved["authorization"]["publication"])
            self.assertEqual(job_path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(job_path.parent.stat().st_mode & 0o777, 0o700)

    def test_linked_public_worker_reconciles_to_terminal_notification(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(router, "JOB_ROOT", Path(tmp)):
            intent = router.classify_durable_intent("深度研究 DeerFlow 官方 GitHub，完成後通知")
            job = router.create_durable_job("深度研究 DeerFlow 官方 GitHub，完成後通知", intent, 123, chat_id=456)
            worker = Path(tmp) / "worker-receipt.json"
            worker.write_text(
                json.dumps(
                    {
                        "status": "completed",
                        "artifact_path": "/tmp/research.md",
                        "artifact_sha256": "abc",
                        "answer_preview": "public result",
                    }
                ),
                encoding="utf-8",
            )
            job["state"] = "WAITING_EXTERNAL"
            job["linked_receipt"] = str(worker)
            router.write_job(Path(job["job_path"]).parent, job)
            notifications = router.pending_durable_notifications()
            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0]["job"]["state"], "COMPLETED")
            self.assertEqual(notifications[0]["job"]["last_result"]["answer_preview"], "public result")
            router.mark_durable_notified(notifications[0]["job_path"], 99)
            self.assertEqual(router.pending_durable_notifications(), [])


if __name__ == "__main__":
    unittest.main()
