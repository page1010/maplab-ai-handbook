import hashlib
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

    def test_routes_seo_patrol_to_public_local_worker(self):
        intent = router.classify_durable_intent("每週檢查網站 SEO，有 material delta 才派工")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.job_type, "seo-patrol")
        self.assertEqual(intent.data_class, "public")
        self.assertEqual(intent.adapter, "codex-heartbeat+maplab-seo-coach-patrol")
        self.assertIsNone(router.classify_durable_intent("SEO 是什麼？"))

    def test_normalizes_full_width_and_zero_width_text(self):
        intent = router.classify_durable_intent("Ａ８\u200b 生歌、做影片並上傳 ＹｏｕＴｕｂｅ 給我看")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.job_type, "a8-production")

    def test_durable_scope_rejects_trading_deletion_and_customer_send(self):
        intent = router.classify_durable_intent("持續跑完並刪除舊資料")
        self.assertIn("fail closed", router.validate_durable_request("持續跑完並刪除舊資料", intent))
        line_intent = router.classify_durable_intent("LINE 訓練持續多跑幾輪並自動發送客戶")
        self.assertIn("fail closed", router.validate_durable_request("LINE 訓練持續多跑幾輪並自動發送客戶", line_intent))

    def test_seo_patrol_rejects_external_mutation_but_allows_read_only_scope(self):
        safe = "持續巡查 WordPress SEO，有差異才產 proposal"
        safe_intent = router.classify_durable_intent(safe)
        self.assertEqual(safe_intent.job_type, "seo-patrol")
        self.assertIsNone(router.validate_durable_request(safe, safe_intent))
        unsafe = "持續檢查 WordPress SEO 並直接改 Rank Math"
        unsafe_intent = router.classify_durable_intent(unsafe)
        self.assertIn("外部寫入", router.validate_durable_request(unsafe, unsafe_intent))
        send = "持續巡查網站 SEO 並發送 LINE 通知客戶"
        send_intent = router.classify_durable_intent(send)
        self.assertIn("不得對客", router.validate_durable_request(send, send_intent))
        private = "持續巡查網站 SEO，讀取 LINE 對話分析後上傳"
        private_intent = router.classify_durable_intent(private)
        self.assertIn("只接受公開資料", router.validate_durable_request(private, private_intent))
        for unsafe_admin in (
            "每週檢查網站 SEO 並自動調整 Google Ads 出價",
            "每日 SEO 巡檢並立即啟用 Rank Math 設定",
            "持續 SEO 巡查並修改 WordPress",
            "持續 SEO 巡查並調整 Google Ads 出價",
            "持續 SEO 巡查並啟用 Rank Math 設定",
        ):
            with self.subTest(unsafe_admin=unsafe_admin):
                unsafe_admin_intent = router.classify_durable_intent(unsafe_admin)
                self.assertIn("外部寫入", router.validate_durable_request(unsafe_admin, unsafe_admin_intent))
        private_gateway = "持續 SEO 巡查並把客戶對話交給 OpenRouter 分析"
        private_gateway_intent = router.classify_durable_intent(private_gateway)
        self.assertIn("第三方模型", router.validate_durable_request(private_gateway, private_gateway_intent))
        short_send = "持續 SEO 巡查並發 LINE 給客戶"
        short_send_intent = router.classify_durable_intent(short_send)
        self.assertIn("不得對客", router.validate_durable_request(short_send, short_send_intent))
        for customer_upload in ("持續 SEO 巡查並上傳報告給客戶", "持續 SEO 巡查並上傳報告到客戶 LINE"):
            with self.subTest(customer_upload=customer_upload):
                customer_upload_intent = router.classify_durable_intent(customer_upload)
                self.assertIn("不得對客", router.validate_durable_request(customer_upload, customer_upload_intent))
        generic_send = "持續完成任務並發 LINE 給客戶"
        generic_send_intent = router.classify_durable_intent(generic_send)
        self.assertEqual(generic_send_intent.job_type, "general-agent")
        self.assertIn("不得對客", router.validate_durable_request(generic_send, generic_send_intent))
        generic_private = "持續完成盤點並把客戶對話交給 OpenRouter"
        generic_private_intent = router.classify_durable_intent(generic_private)
        self.assertEqual(generic_private_intent.job_type, "general-agent")
        self.assertIn("第三方模型", router.validate_durable_request(generic_private, generic_private_intent))
        plan = "幫我更新網站 SEO 計畫並持續優化"
        plan_intent = router.classify_durable_intent(plan)
        self.assertEqual(plan_intent.job_type, "seo-patrol")
        self.assertIsNone(router.validate_durable_request(plan, plan_intent))
        safe_upload = "持續完成公開 SEO 報告並上傳到 Drive 給 Owner"
        safe_upload_intent = router.classify_durable_intent(safe_upload)
        self.assertEqual(safe_upload_intent.job_type, "seo-patrol")
        self.assertIsNone(router.validate_durable_request(safe_upload, safe_upload_intent))

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

    def test_local_seo_job_has_zero_send_and_specific_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(router, "JOB_ROOT", Path(tmp)):
            request = "每週檢查網站 SEO，有 material delta 才派工"
            intent = router.classify_durable_intent(request)
            job = router.create_durable_job(request, intent, 123, chat_id=None, chat_type="local")
            saved = json.loads(Path(job["job_path"]).read_text(encoding="utf-8"))
            self.assertEqual(saved["requester"]["channel"], "local-heartbeat")
            self.assertEqual(saved["notification_policy"], "none")
            self.assertEqual(saved["job_type"], "seo-patrol")
            self.assertTrue(saved["authorization"]["public_site_read"])
            self.assertTrue(saved["authorization"]["repo_report_write"])
            self.assertFalse(saved["authorization"]["external_system_write"])
            self.assertFalse(saved["authorization"]["customer_send"])
            self.assertFalse(saved["authorization"]["private_third_party_egress"])
            self.assertFalse(saved["authorization"]["wordpress_write"])
            self.assertFalse(saved["authorization"]["ads_write"])
            self.assertFalse(saved["authorization"]["rank_math_write"])
            self.assertIn("material-delta", " ".join(saved["acceptance"]))
            self.assertEqual(saved["max_attempts"], 3)
            self.assertFalse(saved["attempt_consumed"])
            self.assertEqual(router.pending_durable_notifications(), [])

    def test_linked_public_worker_reconciles_to_terminal_notification(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            router, "JOB_ROOT", Path(tmp) / "jobs"
        ), mock.patch.object(router, "LINKED_RECEIPT_ROOT", Path(tmp) / "receipts"):
            intent = router.classify_durable_intent("深度研究 DeerFlow 官方 GitHub，完成後通知")
            job = router.create_durable_job("深度研究 DeerFlow 官方 GitHub，完成後通知", intent, 123, chat_id=456)
            task_dir = Path(tmp) / "receipts" / "DFR-test"
            task_dir.mkdir(parents=True)
            artifact = task_dir / "research.md"
            artifact.write_text("public result\n", encoding="utf-8")
            worker = task_dir / "receipt.json"
            worker.write_text(
                json.dumps(
                    {
                        "action": "deerflow-public-research",
                        "parent_job_id": job["job_id"],
                        "request_sha256": job["request_sha256"],
                        "status": "completed",
                        "artifact_path": str(artifact),
                        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
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

    def test_linked_public_worker_rejects_unbound_or_missing_artifact(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            router, "JOB_ROOT", Path(tmp) / "jobs"
        ), mock.patch.object(router, "LINKED_RECEIPT_ROOT", Path(tmp) / "receipts"):
            request = "深度研究 DeerFlow 官方 GitHub，完成後通知"
            intent = router.classify_durable_intent(request)
            job = router.create_durable_job(request, intent, 123, chat_id=456)
            task_dir = Path(tmp) / "receipts" / "DFR-poison"
            task_dir.mkdir(parents=True)
            worker = task_dir / "receipt.json"
            worker.write_text(
                json.dumps(
                    {
                        "action": "deerflow-public-research",
                        "parent_job_id": "MAPJOB-wrong",
                        "request_sha256": job["request_sha256"],
                        "status": "completed",
                        "artifact_path": str(task_dir / "missing.md"),
                        "artifact_sha256": "0" * 64,
                    }
                ),
                encoding="utf-8",
            )
            job["state"] = "WAITING_EXTERNAL"
            job["linked_receipt"] = str(worker)
            router.write_job(Path(job["job_path"]).parent, job)
            self.assertEqual(router.pending_durable_notifications(), [])
            saved = json.loads(Path(job["job_path"]).read_text(encoding="utf-8"))
            self.assertEqual(saved["state"], "WAITING_EXTERNAL")


if __name__ == "__main__":
    unittest.main()
