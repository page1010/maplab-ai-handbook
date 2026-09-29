import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_repo_context as rc
from bot_a6 import hermes_telegram_gateway as gateway


class HermesRepoContextTest(unittest.TestCase):
    def test_boot_pack_always_attached(self):
        ctx, got, missing = rc.build_context("隨便聊聊")
        self.assertTrue(any(g.startswith("AGENT_CORE.md") for g in got), got)
        self.assertIn("----- 檔案:AGENT_CORE.md -----", ctx)

    def test_mentioned_repo_path_with_slice_is_attached(self):
        ctx, got, missing = rc.build_context("看 CURRENT_STATUS.md#tail20 的 A6 狀態")
        self.assertTrue(any(g.startswith("CURRENT_STATUS.md#tail20") for g in got), got)
        self.assertEqual(missing, [])
        self.assertLessEqual(ctx.count("\n"), 20 + 40)  # boot pack + 20 tail lines

    def test_secrets_and_env_are_never_readable(self):
        for spec in ("secrets/anything.md", ".env", "bot_a6/.env", "../../etc/passwd.txt", ".git/config"):
            text, _label, err = rc.read_slice(spec)
            self.assertIsNone(text, spec)
            self.assertIsNotNone(err, spec)

    def test_missing_file_is_reported_not_faked(self):
        _ctx, got, missing = rc.build_context("讀 docs/does-not-exist.md")
        self.assertTrue(any(m.startswith("docs/does-not-exist.md") for m in missing), missing)
        self.assertFalse(any(g.startswith("docs/does-not-exist") for g in got))

    def test_budget_truncates_and_marks(self):
        _ctx, got, _missing = rc.build_context("看 CURRENT_STATUS.md", budget=5000)
        self.assertTrue(all("[" in g for g in got))
        self.assertIn("被 context 預算截斷", _ctx)

    def test_task_prefixes_route_to_task_card(self):
        for text in ("/task 幫我把 LINE webhook 上線", "交辦：整理 A6 狀態", "任務: 查 pitfalls"):
            route = gateway.route_gateway_text(text, [])
            self.assertEqual(route.disposition, "TASK", text)
            self.assertTrue(route.request)
        self.assertNotEqual(gateway.route_gateway_text("/task", []).disposition, "TASK")

    def test_task_card_written_and_queued(self):
        with tempfile.TemporaryDirectory() as tmp:
            inbox = Path(tmp) / "inbox"
            with mock.patch.object(rc, "INBOX_DIR", inbox), mock.patch.object(rc, "QUEUE_FILE", inbox / "QUEUE.md"), \
                    mock.patch.object(rc, "REPO_ROOT", Path(tmp)):
                card = rc.write_task_card("把 LINE webhook 上線\n第二行細節", chat_type="private", sender_id=1)
                self.assertTrue(card.exists())
                body = card.read_text(encoding="utf-8")
                self.assertIn("status: OPEN", body)
                self.assertIn("把 LINE webhook 上線", body)
                queue = (inbox / "QUEUE.md").read_text(encoding="utf-8")
                self.assertIn(card.stem, queue)
                self.assertIn("handoff/inbox/QUEUE.md", rc.task_card_reply(card))


if __name__ == "__main__":
    unittest.main()
