import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_telegram_gateway as gateway


class _Response:
    def __init__(self, payload: bytes):
        self.payload = io.BytesIO(payload)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, amount=-1):
        return self.payload.read(amount)


class HermesTelegramGatewayTest(unittest.TestCase):
    def test_capability_question_is_deterministic_route(self):
        self.assertTrue(gateway.is_capability_question("權限邊界與當前模型是什麼？"))
        self.assertTrue(gateway.is_capability_question("你有持久記憶嗎"))
        self.assertFalse(gateway.is_capability_question("幫我查動能名單"))

    def test_natural_safe_request_routes_without_do_prefix(self):
        self.assertEqual(gateway.extract_action_request("幫我查 Hermes runtime 狀態"), "幫我查 Hermes runtime 狀態")
        self.assertEqual(gateway.extract_action_request("現在動能名單狀態如何"), "現在動能名單狀態如何")
        self.assertEqual(gateway.extract_action_request("/do recent-commits"), "recent-commits")
        self.assertEqual(
            gateway.extract_action_request("讓 A8 生歌、做影片並上傳 YouTube 給我看"),
            "讓 A8 生歌、做影片並上傳 YouTube 給我看",
        )

    def test_gateway_preserves_executor_rejections_instead_of_chat_fallback(self):
        dangerous = (
            "每週檢查網站 SEO 並自動調整 Google Ads 出價",
            "每日 SEO 巡檢並立即啟用 Rank Math 設定",
            "持續 SEO 巡查並把客戶對話交給 OpenRouter 分析",
            "持續 SEO 巡查並發 LINE 給客戶",
        )
        for text in dangerous:
            with self.subTest(text=text):
                route = gateway.route_gateway_text(text, [])
                self.assertEqual(route.disposition, "REJECT")
                self.assertEqual(route.request, text)
                self.assertTrue(route.reason)
                self.assertIsNone(gateway.extract_action_request(text))

        safe = gateway.route_gateway_text("持續完成公開 SEO 報告並上傳到 Drive 給 Owner", [])
        self.assertEqual(safe.disposition, "EXECUTE")
        self.assertEqual(gateway.route_gateway_text("上傳公開報告給客戶", []).disposition, "REJECT")
        self.assertEqual(gateway.route_gateway_text("把報告上傳到客戶 LINE", []).disposition, "REJECT")

    def test_provider_dlp_blocks_private_current_text_and_history(self):
        with mock.patch.object(gateway, "openrouter_chat", return_value="should-not-run") as provider:
            self.assertEqual(
                gateway.answer("key", ["model"], [], "這是客戶資料與 LINE 對話"),
                (None, None),
            )
            provider.assert_not_called()

        private_history = [{"role": "user", "content": "王小明 0912345678"}]
        with mock.patch.object(gateway, "openrouter_chat", return_value="should-not-run") as provider:
            self.assertEqual(
                gateway.answer("key", ["model"], private_history, "繼續"),
                (None, None),
            )
            provider.assert_not_called()

    def test_owner_group_message_requires_mention_or_reply(self):
        base = {"chat": {"type": "supergroup"}, "text": "大家早"}
        self.assertFalse(gateway.is_group_addressed(base, "maplab_a6_bot", 99))
        mentioned = {**base, "text": "@maplab_a6_bot 幫我查狀態"}
        self.assertTrue(gateway.is_group_addressed(mentioned, "maplab_a6_bot", 99))
        replied = {**base, "reply_to_message": {"from": {"id": 99}}}
        self.assertTrue(gateway.is_group_addressed(replied, "maplab_a6_bot", 99))

    def test_group_command_normalization(self):
        text = gateway.strip_bot_mention("/status@maplab_a6_bot", "maplab_a6_bot")
        self.assertEqual(gateway.normalize_command(text, "maplab_a6_bot"), "/status")

    def test_photo_is_downloaded_with_private_receipt(self):
        message = {
            "message_id": 88,
            "chat": {"id": 123, "type": "private"},
            "from": {"id": 456},
            "caption": "測試照片",
            "photo": [
                {"file_id": "small", "file_unique_id": "same", "file_size": 10, "width": 10},
                {"file_id": "large", "file_unique_id": "unique-id", "file_size": 20, "width": 20},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            gateway, "INBOX_ROOT", Path(tmp)
        ), mock.patch.object(
            gateway,
            "tg_call",
            return_value={"ok": True, "result": {"file_path": "photos/file_1.jpg"}},
        ) as tg, mock.patch.object(
            gateway.urllib.request, "urlopen", return_value=_Response(b"image-bytes")
        ):
            receipt = gateway.receive_photo("secret-token", message)
            self.assertEqual(tg.call_args.args[2]["file_id"], "large")
            saved = Path(receipt["file_path"])
            receipt_path = Path(receipt["receipt_path"])
            self.assertTrue(saved.exists())
            self.assertTrue(receipt_path.exists())
            self.assertEqual(saved.stat().st_mode & 0o777, 0o600)
            self.assertEqual(receipt_path.stat().st_mode & 0o777, 0o600)
            self.assertIn(str(receipt_path), receipt_path.read_text(encoding="utf-8"))

    def test_background_notification_is_sent_once_then_marked(self):
        deerflow_item = {"receipt": {"task_id": "DFR-1", "status": "completed"}, "receipt_path": "/tmp/r.json", "chat_id": 7}
        durable_item = {"job": {"job_id": "MAPJOB-1", "state": "COMPLETED"}, "job_path": "/tmp/j.json", "chat_id": 8}
        with mock.patch.object(gateway, "completed_deerflow_notifications", return_value=[deerflow_item]), mock.patch.object(
            gateway, "pending_durable_notifications", return_value=[durable_item]
        ), mock.patch.object(gateway, "deerflow_completion_summary", return_value="dfr done"), mock.patch.object(
            gateway, "durable_completion_summary", return_value="job done"
        ), mock.patch.object(
            gateway, "tg_call", side_effect=[{"result": {"message_id": 11}}, {"result": {"message_id": 12}}]
        ) as tg, mock.patch.object(gateway, "mark_deerflow_notified") as mark_dfr, mock.patch.object(
            gateway, "mark_durable_notified"
        ) as mark_job:
            self.assertEqual(gateway.drain_background_notifications("token"), 2)
            self.assertEqual(tg.call_count, 2)
            mark_dfr.assert_called_once_with("/tmp/r.json", 11)
            mark_job.assert_called_once_with("/tmp/j.json", 12)


if __name__ == "__main__":
    unittest.main()
