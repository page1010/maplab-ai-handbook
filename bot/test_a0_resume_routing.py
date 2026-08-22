"""Tests for the A0/Fable5 relay routing added 2026-08-22.

Owner decisions being tested:
- 21:32: a heartbeat-triggered stateless one-shot has no prior context, so
  "A0 offline" must relay to A0/Fable5 instead of a bare one-shot, and every
  outbound reply must say plainly whether it is Fable5 (relayed) or a bot
  one-shot fallback.
- 21:37: no more "已收到" ack while A0 looks alive (洗板); the bot stays
  silent and waits up to A0_WAIT_TIMEOUT_S for a receipt in
  A0_REPLIES_FILE (written by scripts/a0_reply.sh) before deciding A0 missed
  the message and relaying itself. A leading "代答" always forces the
  relay/fallback path immediately.
- VERIFIED 22:32 + Owner 22:35: `claude -p --resume <session>` timed out at
  180s because that session's context sits at ~98% (huge to reload on every
  resume). Default routing (A0_RELAY_MODE=fresh, unset) is now a
  fresh-context one-shot relay primed with FABLE5_HANDOFF.md's RESUME
  PROMPT + standing memory + recent inbox/replies, instead of resuming the
  near-full session. `--resume` stays available opt-in via
  A0_RELAY_MODE=resume.

Codex review (FABLE5_CONTINUITY_COGOV_REVIEW_20260822.md route A) minimal
fixes, also 2026-08-22:
- a0_replies.jsonl receipts are now *paired* to a specific a0_inbox message
  via "reply_to_inbox_ts" (scripts/a0_reply.sh writes it; bot/bot.py's
  _a0_has_replied_for() matches on it exactly instead of a coarse ts>=
  comparison that could credit a receipt meant for a different message).
- Timed-out subprocesses (_a0_resume_ask, _a0_fresh_relay_ask) are always
  kill()ed *and* wait()ed so a late-finishing child can never be read again
  and its output can never be sent.
- The bot claims a single-reply marker (_a0_claim_single_reply) before ever
  sending an automatic answer for a given inbox message, so the immediate
  "代答" path and the wait-timer path can't both auto-answer the same
  message.
"""

import asyncio
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

FIXED_INBOX_TS = "2026-08-22T14:00:00"


def _fake_update(text: str, chat_id: int = 555, message_id: int = 4242):
    update = MagicMock()
    update.effective_user.id = maplab_bot.OWNER_CHAT_ID
    update.effective_chat.id = chat_id
    update.message.text = text
    update.message.message_id = message_id
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
            patch.object(maplab_bot, "_a0_inbox_append", return_value=FIXED_INBOX_TS),
            patch.object(maplab_bot, "_record_history"),
            patch.object(maplab_bot, "log_and_commit"),
            patch.object(maplab_bot, "git_pull_silent"),
            patch.object(maplab_bot, "read_file", return_value="STATUS"),
            # The single-reply claim guard touches real disk by default
            # (A0_HANDLED_DIR); tests here care about routing, not the
            # claim mechanics itself, so default to "always claims" and
            # exercise the real function separately below.
            patch.object(maplab_bot, "_a0_claim_single_reply", return_value=True),
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
        # reply_to_inbox_ts must be exactly the ts _a0_inbox_append handed
        # back — this is what pairs a later a0_reply.sh receipt to this
        # specific inbox message (Codex route-A minimal fix).
        self.assertEqual(args[3], FIXED_INBOX_TS)

    async def test_handle_message_passes_message_id_to_inbox_append(self):
        update = _fake_update("問一下 CURRENT_STATUS", message_id=9999)
        context = _fake_context()
        inbox_append_mock = MagicMock(return_value=FIXED_INBOX_TS)
        with (
            patch.object(maplab_bot, "_a0_inbox_append", inbox_append_mock),
            patch.object(maplab_bot, "_a0_alive", return_value=True),
            patch.object(maplab_bot, "_a0_wait_then_maybe_resume", AsyncMock()),
        ):
            await maplab_bot.handle_message(update, context)

        inbox_append_mock.assert_called_once_with(update.effective_chat.id, "問一下 CURRENT_STATUS", 9999)

    # ── handle_message: A0 offline → fresh-context relay (default) ─────────

    async def test_a0_offline_uses_fresh_relay_with_fable5_label_by_default(self):
        update = _fake_update("財務問題請直答")
        context = _fake_context()
        relay_result = maplab_bot.ModelResult(ok=True, answer="這是新 context 的回答")
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=False),
            patch.object(maplab_bot, "_local_runtime_question_answer", return_value=""),
            patch.object(maplab_bot, "A0_RELAY_MODE", "fresh"),
            patch.object(maplab_bot, "_a0_fresh_relay_ask", AsyncMock(return_value=relay_result)) as relay_mock,
        ):
            await maplab_bot.handle_message(update, context)

        relay_mock.assert_awaited_once()
        context.bot.send_message.assert_awaited_once()
        sent_text = context.bot.send_message.await_args.kwargs["text"]
        self.assertTrue(sent_text.startswith(maplab_bot.A0_FRESH_RELAY_LABEL))
        self.assertIn("這是新 context 的回答", sent_text)
        maplab_bot.log_and_commit.assert_called_once()
        log_args = maplab_bot.log_and_commit.call_args[0]
        self.assertEqual(log_args[2], "a0-fresh-relay")

    async def test_fresh_relay_system_prompt_includes_handoff_and_recent_inbox(self):
        """The fresh relay's system prompt must actually carry the RESUME
        PROMPT header text and recent inbox/reply context — otherwise the
        new-context session has nothing to ground its answer in."""
        update = _fake_update("財務問題請直答")
        context = _fake_context()
        relay_result = maplab_bot.ModelResult(ok=True, answer="ok")
        captured = {}

        async def fake_relay(user_message, timeout=None):
            captured["system_prompt"] = maplab_bot._a0_fresh_relay_system_prompt()
            return relay_result

        with TemporaryDirectory() as tmp:
            handoff = Path(tmp) / "FABLE5_HANDOFF.md"
            handoff.write_text(
                "\n".join([f"line{i}" for i in range(5)] + ["🔴 RESUME PROMPT marker line"]),
                encoding="utf-8",
            )
            inbox = Path(tmp) / "a0_inbox.jsonl"
            inbox.write_text(
                json.dumps({"ts": "x", "chat_id": 1, "text": "最近的 Owner 訊息 ABC"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            replies = Path(tmp) / "a0_replies.jsonl"
            replies.write_text(
                json.dumps({"ts": time.time(), "reply_to_inbox_ts": "x", "len": 3}) + "\n", encoding="utf-8"
            )
            with (
                patch.object(maplab_bot, "_a0_alive", return_value=False),
                patch.object(maplab_bot, "_local_runtime_question_answer", return_value=""),
                patch.object(maplab_bot, "A0_RELAY_MODE", "fresh"),
                patch.object(maplab_bot, "FABLE5_HANDOFF_FILE", handoff),
                patch.object(maplab_bot, "FABLE5_MEMORY_DIR", Path(tmp) / "nonexistent-memory"),
                patch.object(maplab_bot, "A0_INBOX_FILE", inbox),
                patch.object(maplab_bot, "A0_REPLIES_FILE", replies),
                patch.object(maplab_bot, "_a0_fresh_relay_ask", AsyncMock(side_effect=fake_relay)),
            ):
                await maplab_bot.handle_message(update, context)

        self.assertIn("RESUME PROMPT", captured["system_prompt"])
        self.assertIn("最近的 Owner 訊息 ABC", captured["system_prompt"])

    # ── handle_message: fresh relay fails → labelled bot fallback ──────────

    async def test_fresh_relay_failure_falls_back_with_bot_label(self):
        update = _fake_update("財務問題請直答")
        context = _fake_context()
        relay_result = maplab_bot.ModelResult(
            ok=False, answer="⚠️ fresh relay 錯誤: boom", failure_kind="fresh_relay_failed", stderr="boom"
        )
        fallback_mock = AsyncMock()
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=False),
            patch.object(maplab_bot, "_local_runtime_question_answer", return_value=""),
            patch.object(maplab_bot, "A0_RELAY_MODE", "fresh"),
            patch.object(maplab_bot, "_a0_fresh_relay_ask", AsyncMock(return_value=relay_result)),
            patch.object(maplab_bot, "_run_claude_background", fallback_mock),
        ):
            await maplab_bot.handle_message(update, context)

        # offline notice was sent directly (not via _run_claude_background)
        context.bot.send_message.assert_awaited_once()
        notice_text = context.bot.send_message.await_args.kwargs["text"]
        self.assertIn("fresh-context relay 失敗", notice_text)

        fallback_mock.assert_awaited_once()
        call_args, call_kwargs = fallback_mock.await_args
        self.assertEqual(call_args[0], context.bot)
        self.assertEqual(call_args[4], "bot-fallback")  # log_label
        self.assertEqual(call_kwargs["reply_prefix"], f"{maplab_bot.BOT_FALLBACK_LABEL}\n")

    # ── handle_message: A0_RELAY_MODE=resume still routes to --resume ──────

    async def test_resume_mode_still_uses_session_resume(self):
        update = _fake_update("財務問題請直答")
        context = _fake_context()
        resume_result = maplab_bot.ModelResult(ok=True, answer="這是續接 session 的回答")
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=False),
            patch.object(maplab_bot, "_local_runtime_question_answer", return_value=""),
            patch.object(maplab_bot, "A0_RELAY_MODE", "resume"),
            patch.object(maplab_bot, "_a0_resume_ask", AsyncMock(return_value=resume_result)) as resume_mock,
            patch.object(maplab_bot, "_a0_fresh_relay_ask", AsyncMock()) as fresh_mock,
        ):
            await maplab_bot.handle_message(update, context)

        resume_mock.assert_awaited_once()
        fresh_mock.assert_not_called()
        sent_text = context.bot.send_message.await_args.kwargs["text"]
        self.assertTrue(sent_text.startswith(maplab_bot.A0_RESUME_LABEL))
        self.assertIn("這是續接 session 的回答", sent_text)
        log_args = maplab_bot.log_and_commit.call_args[0]
        self.assertEqual(log_args[2], "a0-resume")

    # ── handle_message: "代答" forces relay path even if A0 looks alive ────

    async def test_answer_now_prefix_forces_immediate_fresh_relay(self):
        update = _fake_update("代答 幫我看一下報表")
        context = _fake_context()
        relay_result = maplab_bot.ModelResult(ok=True, answer="代答結果")
        wait_mock = AsyncMock()
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=True),
            patch.object(maplab_bot, "A0_RELAY_MODE", "fresh"),
            patch.object(maplab_bot, "_a0_wait_then_maybe_resume", wait_mock),
            patch.object(maplab_bot, "_a0_fresh_relay_ask", AsyncMock(return_value=relay_result)) as relay_mock,
        ):
            await maplab_bot.handle_message(update, context)

        wait_mock.assert_not_called()
        relay_mock.assert_awaited_once()
        sent_text = context.bot.send_message.await_args.kwargs["text"]
        self.assertTrue(sent_text.startswith(maplab_bot.A0_FRESH_RELAY_LABEL))
        self.assertIn("代答結果", sent_text)

    # ── handle_message: single-reply guard blocks a duplicate auto-answer ──

    async def test_duplicate_claim_blocks_second_automatic_answer(self):
        """If the single-reply marker is already claimed for this inbox
        message (e.g. the wait-timer path lost a race with an explicit
        "代答"), _a0_resume_or_fallback must not send anything a second
        time — no relay call, no fallback, no message."""
        update = _fake_update("財務問題請直答")
        context = _fake_context()
        relay_mock = AsyncMock()
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=False),
            patch.object(maplab_bot, "_local_runtime_question_answer", return_value=""),
            patch.object(maplab_bot, "_a0_claim_single_reply", return_value=False),
            patch.object(maplab_bot, "_a0_fresh_relay_ask", relay_mock),
        ):
            await maplab_bot.handle_message(update, context)

        relay_mock.assert_not_called()
        context.bot.send_message.assert_not_called()
        maplab_bot.log_and_commit.assert_not_called()

    # ── _a0_wait_then_maybe_resume: two timer cases ─────────────────────────

    async def test_wait_timer_skips_resume_when_receipt_found(self):
        resume_or_fallback = AsyncMock()
        with (
            patch.object(maplab_bot, "A0_WAIT_TIMEOUT_S", 0.2),
            patch.object(maplab_bot, "A0_WAIT_POLL_INTERVAL_S", 0.02),
            patch.object(maplab_bot, "_a0_has_replied_for", return_value=True),
            patch.object(maplab_bot, "_a0_resume_or_fallback", resume_or_fallback),
        ):
            await maplab_bot._a0_wait_then_maybe_resume(MagicMock(), 999, "hello", FIXED_INBOX_TS)

        resume_or_fallback.assert_not_called()

    async def test_wait_timer_triggers_resume_when_no_receipt(self):
        resume_or_fallback = AsyncMock()
        with (
            patch.object(maplab_bot, "A0_WAIT_TIMEOUT_S", 0.1),
            patch.object(maplab_bot, "A0_WAIT_POLL_INTERVAL_S", 0.02),
            patch.object(maplab_bot, "_a0_has_replied_for", return_value=False),
            patch.object(maplab_bot, "_a0_resume_or_fallback", resume_or_fallback),
        ):
            bot = MagicMock()
            await maplab_bot._a0_wait_then_maybe_resume(bot, 999, "hello", FIXED_INBOX_TS)

        resume_or_fallback.assert_awaited_once_with(bot, 999, "hello", FIXED_INBOX_TS)

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

    # ── _a0_has_replied_for: paired-receipt matching (Codex route-A) ───────

    def test_has_replied_for_matches_paired_receipt(self):
        with TemporaryDirectory() as tmp:
            replies_file = Path(tmp) / "a0_replies.jsonl"
            replies_file.write_text(
                json.dumps({"ts": time.time(), "reply_to_inbox_ts": "2026-08-22T10:00:00", "len": 5}) + "\n"
                + json.dumps({"ts": time.time(), "reply_to_inbox_ts": "2026-08-22T10:05:00", "len": 8}) + "\n",
                encoding="utf-8",
            )
            with patch.object(maplab_bot, "A0_REPLIES_FILE", replies_file):
                self.assertTrue(maplab_bot._a0_has_replied_for("2026-08-22T10:00:00"))
                self.assertTrue(maplab_bot._a0_has_replied_for("2026-08-22T10:05:00"))
                self.assertFalse(maplab_bot._a0_has_replied_for("2026-08-22T99:99:99"))

    def test_has_replied_for_ignores_receipt_for_different_message(self):
        """A receipt that answers a *later* inbox message must not be
        credited to an earlier one still waiting — this is exactly the bug
        the coarse ts>=since_ts check had."""
        with TemporaryDirectory() as tmp:
            replies_file = Path(tmp) / "a0_replies.jsonl"
            replies_file.write_text(
                json.dumps({"ts": time.time(), "reply_to_inbox_ts": "2026-08-22T10:05:00", "len": 8}) + "\n",
                encoding="utf-8",
            )
            with patch.object(maplab_bot, "A0_REPLIES_FILE", replies_file):
                self.assertFalse(maplab_bot._a0_has_replied_for("2026-08-22T10:00:00"))

    def test_has_replied_for_ignores_legacy_unpaired_receipt(self):
        with TemporaryDirectory() as tmp:
            replies_file = Path(tmp) / "a0_replies.jsonl"
            replies_file.write_text(json.dumps({"ts": time.time(), "len": 5}) + "\n", encoding="utf-8")
            with patch.object(maplab_bot, "A0_REPLIES_FILE", replies_file):
                self.assertFalse(maplab_bot._a0_has_replied_for("2026-08-22T10:00:00"))

    def test_has_replied_for_missing_file_is_false(self):
        with patch.object(maplab_bot, "A0_REPLIES_FILE", Path("/nonexistent/a0_replies.jsonl")):
            self.assertFalse(maplab_bot._a0_has_replied_for("2026-08-22T10:00:00"))

    def test_has_replied_for_empty_key_is_false(self):
        self.assertFalse(maplab_bot._a0_has_replied_for(""))


class A0SingleReplyGuardTests(unittest.TestCase):
    """_a0_claim_single_reply: atomic marker so one inbox message never gets
    two automatic bot answers (Codex route-A minimal fix)."""

    def test_first_claim_succeeds_second_claim_for_same_message_fails(self):
        with TemporaryDirectory() as tmp:
            with patch.object(maplab_bot, "A0_HANDLED_DIR", Path(tmp) / "a0_handled"):
                first = maplab_bot._a0_claim_single_reply("2026-08-22T14:00:00", 555)
                second = maplab_bot._a0_claim_single_reply("2026-08-22T14:00:00", 555)
        self.assertTrue(first)
        self.assertFalse(second)

    def test_different_messages_each_get_their_own_claim(self):
        with TemporaryDirectory() as tmp:
            with patch.object(maplab_bot, "A0_HANDLED_DIR", Path(tmp) / "a0_handled"):
                a = maplab_bot._a0_claim_single_reply("2026-08-22T14:00:00", 555)
                b = maplab_bot._a0_claim_single_reply("2026-08-22T14:00:01", 555)
        self.assertTrue(a)
        self.assertTrue(b)

    def test_same_ts_different_chat_id_are_independent(self):
        with TemporaryDirectory() as tmp:
            with patch.object(maplab_bot, "A0_HANDLED_DIR", Path(tmp) / "a0_handled"):
                a = maplab_bot._a0_claim_single_reply("2026-08-22T14:00:00", 555)
                b = maplab_bot._a0_claim_single_reply("2026-08-22T14:00:00", 777)
        self.assertTrue(a)
        self.assertTrue(b)

    def test_claim_fails_open_when_handled_dir_unwritable(self):
        """A marker-directory outage must not silently swallow Owner's
        message — the guard fails open (returns True) on filesystem
        errors, e.g. when A0_HANDLED_DIR can't be created at all."""
        # Point at a path whose parent is a *file*, so mkdir(parents=True)
        # raises NotADirectoryError / FileExistsError rather than creating it.
        with TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "blocker"
            blocker.write_text("not a directory", encoding="utf-8")
            with patch.object(maplab_bot, "A0_HANDLED_DIR", blocker / "a0_handled"):
                claimed = maplab_bot._a0_claim_single_reply("2026-08-22T14:00:00", 555)
        self.assertTrue(claimed)


class A0InboxAppendTests(unittest.TestCase):
    def test_returns_written_ts_and_includes_message_id(self):
        with TemporaryDirectory() as tmp:
            inbox_file = Path(tmp) / "a0_inbox.jsonl"
            with patch.object(maplab_bot, "A0_INBOX_FILE", inbox_file):
                ts = maplab_bot._a0_inbox_append(555, "hello", 4242)
            lines = inbox_file.read_text(encoding="utf-8").splitlines()
            entry = json.loads(lines[-1])
        self.assertEqual(entry["ts"], ts)
        self.assertEqual(entry["chat_id"], 555)
        self.assertEqual(entry["text"], "hello")
        self.assertEqual(entry["message_id"], 4242)

    def test_message_id_omitted_when_not_given(self):
        with TemporaryDirectory() as tmp:
            inbox_file = Path(tmp) / "a0_inbox.jsonl"
            with patch.object(maplab_bot, "A0_INBOX_FILE", inbox_file):
                maplab_bot._a0_inbox_append(555, "hello")
            entry = json.loads(inbox_file.read_text(encoding="utf-8").splitlines()[-1])
        self.assertNotIn("message_id", entry)

    def test_returns_ts_even_when_write_fails(self):
        # A directory that can never be created as a parent (its own
        # "parent" is a file) — write must fail, but a ts string is still
        # returned so the caller has something to key on.
        with TemporaryDirectory() as tmp:
            blocker = Path(tmp) / "blocker"
            blocker.write_text("x", encoding="utf-8")
            with patch.object(maplab_bot, "A0_INBOX_FILE", blocker / "sub" / "a0_inbox.jsonl"):
                ts = maplab_bot._a0_inbox_append(555, "hello")
        self.assertTrue(ts)


class A0FreshRelayAskTests(unittest.IsolatedAsyncioTestCase):
    """Direct coverage of _a0_fresh_relay_ask's subprocess handling — the
    fresh-context relay path that is now the default A0 routing. At least
    three cases per the relay2 handoff: a clean success, a timeout that
    must kill+wait the child (Codex route-A minimal fix), and the CLI
    being missing entirely. A fourth covers the --system-prompt
    unsupported→inline-prompt retry."""

    def _make_proc(self, returncode=0, stdout=b"ok answer", stderr=b""):
        proc = MagicMock()
        proc.communicate = AsyncMock(return_value=(stdout, stderr))
        proc.returncode = returncode
        proc.kill = MagicMock()
        proc.wait = AsyncMock()
        return proc

    async def test_success_returns_ok_result(self):
        proc = self._make_proc(returncode=0, stdout=b"fresh context answer", stderr=b"")
        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=proc)):
            result = await maplab_bot._a0_fresh_relay_ask("hi", timeout=5)
        self.assertTrue(result.ok)
        self.assertIn("fresh context answer", result.answer)
        proc.kill.assert_not_called()

    async def test_timeout_kills_and_waits_subprocess_and_never_sends_late_output(self):
        proc = MagicMock()
        proc.returncode = None
        proc.kill = MagicMock()
        proc.wait = AsyncMock()

        async def _hang_forever():
            await asyncio.sleep(10)
            return (b"late output that must never be used", b"")  # pragma: no cover

        proc.communicate = AsyncMock(side_effect=_hang_forever)

        with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=proc)):
            result = await maplab_bot._a0_fresh_relay_ask("hi", timeout=0.05)

        self.assertFalse(result.ok)
        self.assertEqual(result.failure_kind, "timeout")
        proc.kill.assert_called_once()
        proc.wait.assert_awaited_once()
        # No late output leaked into the (failed) result.
        self.assertNotIn("late output", result.answer)

    async def test_cli_missing_returns_cli_missing_failure(self):
        with patch("asyncio.create_subprocess_exec", AsyncMock(side_effect=FileNotFoundError())):
            result = await maplab_bot._a0_fresh_relay_ask("hi", timeout=5)
        self.assertFalse(result.ok)
        self.assertEqual(result.failure_kind, "cli_missing")

    async def test_unknown_system_prompt_flag_falls_back_to_inline_prompt(self):
        first_proc = self._make_proc(returncode=1, stdout=b"", stderr=b"error: unknown option '--system-prompt'")
        second_proc = self._make_proc(returncode=0, stdout=b"inline-mode answer", stderr=b"")
        create_mock = AsyncMock(side_effect=[first_proc, second_proc])
        with patch("asyncio.create_subprocess_exec", create_mock):
            result = await maplab_bot._a0_fresh_relay_ask("hi", timeout=5)
        self.assertTrue(result.ok)
        self.assertIn("inline-mode answer", result.answer)
        self.assertEqual(create_mock.await_count, 2)
        # second call folded the prompt into the positional message instead
        # of using --system-prompt
        second_cmd = create_mock.await_args_list[1].args
        self.assertNotIn("--system-prompt", second_cmd)


if __name__ == "__main__":
    unittest.main()
