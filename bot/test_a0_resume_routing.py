"""Tests for the A0/Fable5 session-resume routing added 2026-08-22.

Owner decisions being tested:
- 21:32: a heartbeat-triggered stateless one-shot has no prior context, so
  "A0 offline" must resume A0's own Claude Code session
  (`claude -p --resume <session_id>`) instead, and every outbound reply must
  say plainly whether it is Fable5 (resumed) or a bot one-shot fallback.
- 21:37: no more "已收到" ack while A0 looks alive (洗板); the bot stays
  silent and waits up to A0_WAIT_TIMEOUT_S for a receipt in
  A0_REPLIES_FILE (written by scripts/a0_reply.sh) before deciding A0 missed
  the message and resuming its session itself. A leading "代答" always
  forces the resume/fallback path immediately.
"""

import importlib.util
import json
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, MagicMock, patch

BOT_MODULE_PATH = Path(__file__).with_name("bot.py")
BOT_SPEC = importlib.util.spec_from_file_location("maplab_bot_a0_resume_under_test", BOT_MODULE_PATH)
maplab_bot = importlib.util.module_from_spec(BOT_SPEC)
sys.modules[BOT_SPEC.name] = maplab_bot
BOT_SPEC.loader.exec_module(maplab_bot)


def _fake_update(text: str, chat_id: int = 555):
    update = MagicMock()
    update.effective_user.id = maplab_bot.OWNER_CHAT_ID
    update.effective_chat.id = chat_id
    update.message.text = text
    update.message.reply_text = AsyncMock()
    return update


def _fake_context():
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    return context


class A0ResumeRoutingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        maplab_bot._conv_history.clear()
        self._patches = [
            patch.object(maplab_bot, "_a0_inbox_append"),
            patch.object(maplab_bot, "_record_history"),
            patch.object(maplab_bot, "log_and_commit"),
            patch.object(maplab_bot, "git_pull_silent"),
            patch.object(maplab_bot, "read_file", return_value="STATUS"),
        ]
        for p in self._patches:
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        maplab_bot._conv_history.clear()

    # ── handle_message: A0 alive → silent, no ack ───────────────────────────

    async def test_a0_alive_sends_no_ack_and_schedules_wait(self):
        wait_mock = AsyncMock()
        update = _fake_update("問一下 CURRENT_STATUS")
        context = _fake_context()
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=True),
            patch.object(maplab_bot, "_a0_wait_then_maybe_resume", wait_mock),
        ):
            await maplab_bot.handle_message(update, context)
            await self._drain()

        update.message.reply_text.assert_not_called()
        context.bot.send_message.assert_not_called()
        wait_mock.assert_awaited_once()
        args, _ = wait_mock.await_args
        self.assertIs(args[0], context.bot)
        self.assertEqual(args[1], update.effective_chat.id)
        self.assertEqual(args[2], "問一下 CURRENT_STATUS")
        self.assertLessEqual(abs(args[3] - time.time()), 5)

    # ── handle_message: A0 offline → resume ─────────────────────────────────

    async def test_a0_offline_resumes_session_with_fable5_label(self):
        update = _fake_update("財務問題請直答")
        context = _fake_context()
        resume_result = maplab_bot.ModelResult(ok=True, answer="這是續接 session 的回答")
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=False),
            patch.object(maplab_bot, "_local_runtime_question_answer", return_value=""),
            patch.object(maplab_bot, "_a0_resume_ask", AsyncMock(return_value=resume_result)) as resume_mock,
        ):
            await maplab_bot.handle_message(update, context)

        resume_mock.assert_awaited_once()
        context.bot.send_message.assert_awaited_once()
        sent_text = context.bot.send_message.await_args.kwargs["text"]
        self.assertTrue(sent_text.startswith(maplab_bot.A0_RESUME_LABEL))
        self.assertIn("這是續接 session 的回答", sent_text)
        maplab_bot.log_and_commit.assert_called_once()
        log_args = maplab_bot.log_and_commit.call_args[0]
        self.assertEqual(log_args[2], "a0-resume")

    # ── handle_message: resume fails → labelled bot fallback ───────────────

    async def test_resume_failure_falls_back_with_bot_label(self):
        update = _fake_update("財務問題請直答")
        context = _fake_context()
        resume_result = maplab_bot.ModelResult(
            ok=False, answer="⚠️ resume 錯誤: boom", failure_kind="resume_failed", stderr="boom"
        )
        fallback_mock = AsyncMock()
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=False),
            patch.object(maplab_bot, "_local_runtime_question_answer", return_value=""),
            patch.object(maplab_bot, "_a0_resume_ask", AsyncMock(return_value=resume_result)),
            patch.object(maplab_bot, "_run_claude_background", fallback_mock),
        ):
            await maplab_bot.handle_message(update, context)

        # offline notice was sent directly (not via _run_claude_background)
        context.bot.send_message.assert_awaited_once()
        notice_text = context.bot.send_message.await_args.kwargs["text"]
        self.assertIn("resume 失敗", notice_text)

        fallback_mock.assert_awaited_once()
        call_args, call_kwargs = fallback_mock.await_args
        self.assertEqual(call_args[0], context.bot)
        self.assertEqual(call_args[4], "bot-fallback")  # log_label
        self.assertEqual(call_kwargs["reply_prefix"], f"{maplab_bot.BOT_FALLBACK_LABEL}\n")

    # ── handle_message: "代答" forces resume path even if A0 looks alive ──

    async def test_answer_now_prefix_forces_immediate_resume(self):
        update = _fake_update("代答 幫我看一下報表")
        context = _fake_context()
        resume_result = maplab_bot.ModelResult(ok=True, answer="代答結果")
        wait_mock = AsyncMock()
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=True),
            patch.object(maplab_bot, "_a0_wait_then_maybe_resume", wait_mock),
            patch.object(maplab_bot, "_a0_resume_ask", AsyncMock(return_value=resume_result)) as resume_mock,
        ):
            await maplab_bot.handle_message(update, context)

        wait_mock.assert_not_called()
        resume_mock.assert_awaited_once()
        sent_text = context.bot.send_message.await_args.kwargs["text"]
        self.assertTrue(sent_text.startswith(maplab_bot.A0_RESUME_LABEL))
        self.assertIn("代答結果", sent_text)

    # ── _a0_wait_then_maybe_resume: two timer cases ─────────────────────────

    async def test_wait_timer_skips_resume_when_receipt_found(self):
        resume_or_fallback = AsyncMock()
        with (
            patch.object(maplab_bot, "A0_WAIT_TIMEOUT_S", 0.2),
            patch.object(maplab_bot, "A0_WAIT_POLL_INTERVAL_S", 0.02),
            patch.object(maplab_bot, "_a0_has_replied_since", return_value=True),
            patch.object(maplab_bot, "_a0_resume_or_fallback", resume_or_fallback),
        ):
            await maplab_bot._a0_wait_then_maybe_resume(MagicMock(), 999, "hello", time.time())

        resume_or_fallback.assert_not_called()

    async def test_wait_timer_triggers_resume_when_no_receipt(self):
        resume_or_fallback = AsyncMock()
        with (
            patch.object(maplab_bot, "A0_WAIT_TIMEOUT_S", 0.1),
            patch.object(maplab_bot, "A0_WAIT_POLL_INTERVAL_S", 0.02),
            patch.object(maplab_bot, "_a0_has_replied_since", return_value=False),
            patch.object(maplab_bot, "_a0_resume_or_fallback", resume_or_fallback),
        ):
            bot = MagicMock()
            await maplab_bot._a0_wait_then_maybe_resume(bot, 999, "hello", time.time())

        resume_or_fallback.assert_awaited_once_with(bot, 999, "hello")

    # ── helpers ──────────────────────────────────────────────────────────

    async def _drain(self):
        for _ in range(5):
            await self._sleep0()

    @staticmethod
    async def _sleep0():
        import asyncio
        await asyncio.sleep(0)


class A0SessionConfigTests(unittest.TestCase):
    def test_reads_session_id_and_model_from_file(self):
        with TemporaryDirectory() as tmp:
            session_file = Path(tmp) / "a0_session.json"
            session_file.write_text(
                json.dumps({"session_id": "abc-123", "model": "claude-fable-5"}),
                encoding="utf-8",
            )
            with patch.object(maplab_bot, "A0_SESSION_FILE", session_file):
                session_id, model = maplab_bot._a0_session_config()
        self.assertEqual(session_id, "abc-123")
        self.assertEqual(model, "claude-fable-5")

    def test_falls_back_to_defaults_when_file_missing(self):
        with patch.object(maplab_bot, "A0_SESSION_FILE", Path("/nonexistent/a0_session.json")):
            session_id, model = maplab_bot._a0_session_config()
        self.assertEqual(session_id, maplab_bot.A0_SESSION_ID_DEFAULT)
        self.assertEqual(model, maplab_bot.A0_RESUME_MODEL_DEFAULT)

    def test_answer_now_command_detection(self):
        self.assertTrue(maplab_bot._is_a0_answer_command("代答 幫我看看"))
        self.assertTrue(maplab_bot._is_a0_answer_command("  代答直接回"))
        self.assertFalse(maplab_bot._is_a0_answer_command("代表隊的問題"))
        self.assertFalse(maplab_bot._is_a0_answer_command("一般訊息"))

    def test_has_replied_since_reads_receipts(self):
        with TemporaryDirectory() as tmp:
            replies_file = Path(tmp) / "a0_replies.jsonl"
            now = time.time()
            replies_file.write_text(
                json.dumps({"ts": now - 10, "len": 5}) + "\n" + json.dumps({"ts": now + 5, "len": 8}) + "\n",
                encoding="utf-8",
            )
            with patch.object(maplab_bot, "A0_REPLIES_FILE", replies_file):
                self.assertTrue(maplab_bot._a0_has_replied_since(now))
                self.assertFalse(maplab_bot._a0_has_replied_since(now + 100))

    def test_has_replied_since_missing_file_is_false(self):
        with patch.object(maplab_bot, "A0_REPLIES_FILE", Path("/nonexistent/a0_replies.jsonl")):
            self.assertFalse(maplab_bot._a0_has_replied_since(time.time()))


if __name__ == "__main__":
    unittest.main()
