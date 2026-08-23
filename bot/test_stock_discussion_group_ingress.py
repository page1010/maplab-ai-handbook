"""Tests for the Stock Discussion Group ingress added 2026-08-24.

Owner decision being tested (Owner 2026-08-24 01:11, plus the 能力測試 D
ruling this task must not regress): the bot is already a member of group
chat_id -5589898264 and receives Owner's own messages there (bots never see
other bots' messages). General group chit-chat must stay completely silent.
Only Owner's own messages starting with 研調:/研調：/辯論:/辯論：/討論:/討論：
(optionally after an @bot mention) trigger anything; everything else in the
group — including any message from a non-Owner sender — gets no reply at
all, not even the private-chat deny() "⛔ 未授權".

On trigger, the bot acks with a topic-id line, spawns
investment-os/scripts/run_stock_discussion.py in the background (never
blocking the polling loop), and always follows up with either a <=3-line
summary or a one-line failure — never silent after the ack. A second
trigger for a topic already running gets a "仍在進行" ack instead of a
duplicate run. Owner replying to the bot's ack/summary message in the group
is treated as a follow-up that re-runs the orchestrator with the parent
topic text plus an explicit "追問(承接 topic-id <id8>): ..." continuation.

These group-ingress messages must never be fed into the existing A0/Fable5
offline resume/relay path tested in test_a0_resume_routing.py — see the
chat_id<0 guards added to _a0_resume_or_fallback and
_a0_wait_then_maybe_resume, and handle_message's own group short-circuit.
"""

import asyncio
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

BOT_MODULE_PATH = Path(__file__).with_name("bot.py")
BOT_SPEC = importlib.util.spec_from_file_location("maplab_bot_group_ingress_under_test", BOT_MODULE_PATH)
maplab_bot = importlib.util.module_from_spec(BOT_SPEC)
sys.modules[BOT_SPEC.name] = maplab_bot
BOT_SPEC.loader.exec_module(maplab_bot)

GROUP_CHAT_ID = -5589898264


def _fake_group_update(text: str, *, sender_id: int, chat_id: int = GROUP_CHAT_ID, message_id: int = 100, reply_to_message_id=None):
    update = MagicMock()
    update.effective_user.id = sender_id
    update.effective_chat.id = chat_id
    update.effective_chat.type = "supergroup"
    update.message.text = text
    update.message.message_id = message_id
    update.message.reply_text = AsyncMock()
    if reply_to_message_id is not None:
        reply_to = MagicMock()
        reply_to.message_id = reply_to_message_id
        update.message.reply_to_message = reply_to
    else:
        update.message.reply_to_message = None
    return update


def _fake_context():
    context = MagicMock()
    context.bot.send_message = AsyncMock(return_value=MagicMock(message_id=999))
    return context


class GroupIngressTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        maplab_bot._GROUP_DISCUSSION_RUNNING.clear()
        maplab_bot._GROUP_TOPICS.clear()
        maplab_bot._GROUP_MSG_TO_TOPIC.clear()
        self._patches = [
            patch.object(maplab_bot, "_a0_inbox_append", return_value="2026-08-24T01:11:00"),
        ]
        for p in self._patches:
            p.start()
            self.addCleanup(p.stop)

    async def _drain(self):
        await asyncio.sleep(0)
        await asyncio.sleep(0)


class SilenceTests(GroupIngressTestCase):
    """能力測試 D: general group chit-chat stays silent; non-owner senders
    get no reply at all, not even deny()."""

    async def test_non_owner_sender_is_fully_silent_no_deny_no_inbox_tap(self):
        update = _fake_group_update("研調: 2330 要不要加碼", sender_id=maplab_bot.OWNER_CHAT_ID + 1)
        context = _fake_context()
        with patch.object(maplab_bot, "_a0_inbox_append") as inbox_mock:
            await maplab_bot.handle_group_message(update, context)
        context.bot.send_message.assert_not_called()
        update.message.reply_text.assert_not_called()
        inbox_mock.assert_not_called()

    async def test_owner_general_chit_chat_without_trigger_is_silent(self):
        update = _fake_group_update("大家早安，今天台股怎麼看", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        await maplab_bot.handle_group_message(update, context)
        context.bot.send_message.assert_not_called()
        update.message.reply_text.assert_not_called()

    async def test_owner_message_is_still_tapped_to_inbox_even_without_trigger(self):
        update = _fake_group_update("大家早安", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        with patch.object(maplab_bot, "_a0_inbox_append", return_value="ts") as inbox_mock:
            await maplab_bot.handle_group_message(update, context)
        inbox_mock.assert_called_once_with(GROUP_CHAT_ID, "大家早安", 100, source="group")

    async def test_trigger_prefix_with_empty_statement_is_silent(self):
        update = _fake_group_update("研調:", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        with patch.object(maplab_bot, "_dispatch_group_discussion", AsyncMock()) as dispatch_mock:
            await maplab_bot.handle_group_message(update, context)
        dispatch_mock.assert_not_called()
        context.bot.send_message.assert_not_called()


class TriggerParsingTests(unittest.TestCase):
    """All prefix variants (full/half-width colon) + @mention form."""

    def test_research_half_width_colon(self):
        m = maplab_bot._group_trigger_match("研調: 2330 要不要加碼")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "研調")
        self.assertEqual(m.group(2), "2330 要不要加碼")

    def test_research_full_width_colon(self):
        m = maplab_bot._group_trigger_match("研調： 2330 要不要加碼")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "研調")

    def test_debate_half_width_colon(self):
        m = maplab_bot._group_trigger_match("辯論: 該不該減碼 3296")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "辯論")

    def test_debate_full_width_colon(self):
        m = maplab_bot._group_trigger_match("辯論：該不該減碼 3296")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "辯論")

    def test_discussion_half_and_full_width_colon(self):
        self.assertEqual(maplab_bot._group_trigger_match("討論: 這則新聞").group(1), "討論")
        self.assertEqual(maplab_bot._group_trigger_match("討論：這則新聞").group(1), "討論")

    def test_mention_then_trigger(self):
        m = maplab_bot._group_trigger_match("@maplab_claude_bot 研調: 2330 法說會")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "研調")
        self.assertEqual(m.group(2), "2330 法說會")

    def test_mention_then_debate_trigger_full_width_colon(self):
        m = maplab_bot._group_trigger_match("@maplab_claude_bot 辯論：3296 該減碼嗎")
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "辯論")

    def test_mention_without_trigger_keyword_does_not_match(self):
        self.assertIsNone(maplab_bot._group_trigger_match("@maplab_claude_bot 幫我看一下 2330"))

    def test_plain_text_without_trigger_does_not_match(self):
        self.assertIsNone(maplab_bot._group_trigger_match("2330 今天漲停"))

    def test_trigger_keyword_not_at_start_does_not_match(self):
        self.assertIsNone(maplab_bot._group_trigger_match("早安，研調: 2330"))

    def test_mode_mapping(self):
        self.assertEqual(maplab_bot._GROUP_TRIGGER_MODE["研調"], "research")
        self.assertEqual(maplab_bot._GROUP_TRIGGER_MODE["討論"], "research")
        self.assertEqual(maplab_bot._GROUP_TRIGGER_MODE["辯論"], "debate")


class TopicIdTests(unittest.TestCase):
    def test_topic_id_matches_sha256_text_plus_date_first_16_chars(self):
        text = "2330 法說會很強"
        date_str = "2026-08-24"
        expected = hashlib.sha256((text + date_str).encode("utf-8")).hexdigest()[:16]
        self.assertEqual(maplab_bot._stock_discussion_topic_id(text, date_str), expected)

    def test_topic_id_deterministic(self):
        a = maplab_bot._stock_discussion_topic_id("同一句話", "2026-08-24")
        b = maplab_bot._stock_discussion_topic_id("同一句話", "2026-08-24")
        self.assertEqual(a, b)

    def test_topic_id_differs_by_text(self):
        a = maplab_bot._stock_discussion_topic_id("句子A", "2026-08-24")
        b = maplab_bot._stock_discussion_topic_id("句子B", "2026-08-24")
        self.assertNotEqual(a, b)


class AckTests(GroupIngressTestCase):
    async def test_research_trigger_acks_with_topic_id_and_research_label(self):
        update = _fake_group_update("研調: 2330 要不要加碼", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", AsyncMock()):
            await maplab_bot.handle_group_message(update, context)
            await self._drain()

        context.bot.send_message.assert_awaited_once()
        kwargs = context.bot.send_message.await_args.kwargs
        self.assertEqual(kwargs["chat_id"], GROUP_CHAT_ID)
        text = kwargs["text"]
        self.assertTrue(text.startswith("收到 topic-id "))
        self.assertIn("開工(研調)", text)
        expected_id8 = maplab_bot._stock_discussion_topic_id("2330 要不要加碼", maplab_bot._stock_discussion_today())[:8]
        self.assertIn(expected_id8, text)

    async def test_debate_trigger_acks_with_debate_label(self):
        update = _fake_group_update("辯論: 3296 該不該減碼", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", AsyncMock()):
            await maplab_bot.handle_group_message(update, context)
            await self._drain()
        text = context.bot.send_message.await_args.kwargs["text"]
        self.assertIn("開工(辯論)", text)

    async def test_discussion_trigger_acks_with_research_label(self):
        update = _fake_group_update("討論: 這則新聞怎麼看", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", AsyncMock()):
            await maplab_bot.handle_group_message(update, context)
            await self._drain()
        text = context.bot.send_message.await_args.kwargs["text"]
        self.assertIn("開工(研調)", text)

    async def test_mention_form_also_dispatches(self):
        update = _fake_group_update("@maplab_claude_bot 研調: 2330 法說會超預期", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", AsyncMock()) as orch_mock:
            await maplab_bot.handle_group_message(update, context)
            await self._drain()
        orch_mock.assert_awaited_once()
        args = orch_mock.await_args.args
        # statement_text is the mention+prefix-stripped text
        self.assertEqual(args[4], "2330 法說會超預期")


class ConcurrencyGuardTests(GroupIngressTestCase):
    async def test_second_trigger_for_running_topic_gets_still_in_progress_ack(self):
        update = _fake_group_update("研調: 2330 要不要加碼", sender_id=maplab_bot.OWNER_CHAT_ID)
        context = _fake_context()
        # Orchestrator never completes within this test -- simulate "still running".
        never_done = asyncio.get_event_loop().create_future()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", return_value=never_done):
            await maplab_bot.handle_group_message(update, context)
            await self._drain()
            context.bot.send_message.reset_mock()
            await maplab_bot.handle_group_message(update, context)
            await self._drain()

        context.bot.send_message.assert_awaited_once()
        text = context.bot.send_message.await_args.kwargs["text"]
        self.assertIn("仍在進行", text)
        never_done.cancel()

    async def test_different_topics_do_not_block_each_other(self):
        context = _fake_context()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", AsyncMock()):
            update1 = _fake_group_update("研調: 2330", sender_id=maplab_bot.OWNER_CHAT_ID, message_id=101)
            update2 = _fake_group_update("研調: 3296", sender_id=maplab_bot.OWNER_CHAT_ID, message_id=102)
            await maplab_bot.handle_group_message(update1, context)
            await maplab_bot.handle_group_message(update2, context)
            await self._drain()
        self.assertEqual(context.bot.send_message.await_count, 2)
        for call in context.bot.send_message.await_args_list:
            self.assertNotIn("仍在進行", call.kwargs["text"])


class OrchestratorRunTests(GroupIngressTestCase):
    def _mock_proc(self, *, returncode=0, stdout=b"", stderr=b"", raise_timeout=False):
        proc = MagicMock()
        proc.returncode = returncode
        if raise_timeout:
            proc.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
        else:
            proc.communicate = AsyncMock(return_value=(stdout, stderr))
        proc.kill = MagicMock()
        proc.wait = AsyncMock()
        return proc

    async def test_success_posts_summary_with_fable5_integration_label(self):
        context = _fake_context()
        proc = self._mock_proc(returncode=0)
        with (
            patch.object(maplab_bot.asyncio, "create_subprocess_exec", AsyncMock(return_value=proc)),
            patch.object(maplab_bot, "_read_group_discussion_summary", return_value="第一行\n第二行\n第三行"),
        ):
            await maplab_bot._run_group_discussion_orchestrator(
                context.bot, GROUP_CHAT_ID, "abcd1234", "abcd1234efgh5678", "2330 要不要加碼", "research", "2026-08-24"
            )
        context.bot.send_message.assert_awaited_once()
        kwargs = context.bot.send_message.await_args.kwargs
        self.assertTrue(kwargs["text"].startswith("【Fable5 整合】topic-id abcd1234"))
        self.assertIn("第一行", kwargs["text"])
        self.assertNotIn("abcd1234efgh5678", maplab_bot._GROUP_DISCUSSION_RUNNING)

    async def test_nonzero_exit_posts_one_line_failure(self):
        context = _fake_context()
        proc = self._mock_proc(returncode=1, stderr=b"boom, everything is on fire and nothing works at all today unfortunately")
        with patch.object(maplab_bot.asyncio, "create_subprocess_exec", AsyncMock(return_value=proc)):
            await maplab_bot._run_group_discussion_orchestrator(
                context.bot, GROUP_CHAT_ID, "abcd1234", "abcd1234efgh5678", "2330", "research", "2026-08-24"
            )
        context.bot.send_message.assert_awaited_once()
        text = context.bot.send_message.await_args.kwargs["text"]
        self.assertTrue(text.startswith("topic-id abcd1234 失敗:"))
        self.assertIn("稍後重試", text)
        self.assertLessEqual(len(text), 200)

    async def test_timeout_kills_process_and_posts_failure(self):
        context = _fake_context()
        proc = self._mock_proc(raise_timeout=True)
        with patch.object(maplab_bot.asyncio, "create_subprocess_exec", AsyncMock(return_value=proc)):
            await maplab_bot._run_group_discussion_orchestrator(
                context.bot, GROUP_CHAT_ID, "abcd1234", "abcd1234efgh5678", "2330", "research", "2026-08-24"
            )
        proc.kill.assert_called_once()
        proc.wait.assert_awaited_once()
        text = context.bot.send_message.await_args.kwargs["text"]
        self.assertIn("逾時", text)
        self.assertIn("稍後重試", text)

    async def test_missing_summary_posts_failure_not_silent(self):
        context = _fake_context()
        proc = self._mock_proc(returncode=0)
        with (
            patch.object(maplab_bot.asyncio, "create_subprocess_exec", AsyncMock(return_value=proc)),
            patch.object(maplab_bot, "_read_group_discussion_summary", return_value=""),
        ):
            await maplab_bot._run_group_discussion_orchestrator(
                context.bot, GROUP_CHAT_ID, "abcd1234", "abcd1234efgh5678", "2330", "research", "2026-08-24"
            )
        text = context.bot.send_message.await_args.kwargs["text"]
        self.assertIn("失敗", text)
        self.assertIn("稍後重試", text)

    async def test_never_silent_running_set_cleared_even_on_exception(self):
        context = _fake_context()
        with patch.object(maplab_bot.asyncio, "create_subprocess_exec", AsyncMock(side_effect=RuntimeError("spawn failed"))):
            maplab_bot._GROUP_DISCUSSION_RUNNING.add("abcd1234efgh5678")
            await maplab_bot._run_group_discussion_orchestrator(
                context.bot, GROUP_CHAT_ID, "abcd1234", "abcd1234efgh5678", "2330", "research", "2026-08-24"
            )
        self.assertNotIn("abcd1234efgh5678", maplab_bot._GROUP_DISCUSSION_RUNNING)
        context.bot.send_message.assert_awaited_once()
        self.assertIn("失敗", context.bot.send_message.await_args.kwargs["text"])

    async def test_debate_mode_passes_mode_flag_to_subprocess(self):
        context = _fake_context()
        proc = self._mock_proc(returncode=0)
        captured_cmd = {}

        async def _fake_exec(*args, **kwargs):
            captured_cmd["args"] = args
            return proc

        with (
            patch.object(maplab_bot.asyncio, "create_subprocess_exec", _fake_exec),
            patch.object(maplab_bot, "_read_group_discussion_summary", return_value="裁決:正方較強"),
        ):
            await maplab_bot._run_group_discussion_orchestrator(
                context.bot, GROUP_CHAT_ID, "abcd1234", "abcd1234efgh5678", "3296 該不該減碼", "debate", "2026-08-24"
            )
        self.assertIn("--mode", captured_cmd["args"])
        self.assertIn("debate", captured_cmd["args"])
        self.assertIn("--send-telegram", captured_cmd["args"])


class FollowUpTests(GroupIngressTestCase):
    async def test_reply_to_summary_message_reruns_with_referenced_parent_id8(self):
        maplab_bot._GROUP_TOPICS["parenttopic123456"] = {
            "text": "2330 法說會很強要不要加碼",
            "mode": "research",
            "date": "2026-08-24",
            "id8": "parentto",
        }
        maplab_bot._GROUP_MSG_TO_TOPIC[555] = "parenttopic123456"

        update = _fake_group_update("那外資有回補嗎", sender_id=maplab_bot.OWNER_CHAT_ID, reply_to_message_id=555)
        context = _fake_context()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", AsyncMock()) as orch_mock:
            await maplab_bot.handle_group_message(update, context)
            await self._drain()

        orch_mock.assert_awaited_once()
        followup_statement = orch_mock.await_args.args[4]
        self.assertIn("2330 法說會很強要不要加碼", followup_statement)
        self.assertIn("追問(承接 topic-id parentto)", followup_statement)
        self.assertIn("那外資有回補嗎", followup_statement)
        # Reused the parent's mode.
        self.assertEqual(orch_mock.await_args.args[5], "research")

    async def test_reply_to_unrelated_message_is_treated_as_normal_trigger_check(self):
        update = _fake_group_update("研調: 2330", sender_id=maplab_bot.OWNER_CHAT_ID, reply_to_message_id=999999)
        context = _fake_context()
        with patch.object(maplab_bot, "_run_group_discussion_orchestrator", AsyncMock()) as orch_mock:
            await maplab_bot.handle_group_message(update, context)
            await self._drain()
        orch_mock.assert_awaited_once()

    async def test_reply_to_non_topic_message_without_trigger_is_silent(self):
        update = _fake_group_update("嗯嗯好", sender_id=maplab_bot.OWNER_CHAT_ID, reply_to_message_id=999999)
        context = _fake_context()
        await maplab_bot.handle_group_message(update, context)
        context.bot.send_message.assert_not_called()


class SummaryReaderTests(unittest.TestCase):
    def test_research_mode_out_dir_has_no_suffix(self):
        out_dir = maplab_bot._group_discussion_out_dir("2026-08-24", "abcd1234efgh5678", "research")
        self.assertTrue(str(out_dir).endswith("abcd1234efgh5678"))

    def test_debate_mode_out_dir_has_debate_suffix(self):
        out_dir = maplab_bot._group_discussion_out_dir("2026-08-24", "abcd1234efgh5678", "debate")
        self.assertTrue(str(out_dir).endswith("abcd1234efgh5678__debate"))

    def test_reads_summary_file_when_present(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(maplab_bot, "INVESTMENT_OS_DIR", Path(tmp)):
                out_dir = maplab_bot._group_discussion_out_dir("2026-08-24", "topicid12345678", "research")
                out_dir.mkdir(parents=True)
                (out_dir / "summary.txt").write_text("摘要第一行\n摘要第二行\n", encoding="utf-8")
                result = maplab_bot._read_group_discussion_summary("2026-08-24", "topicid12345678", "research")
        self.assertEqual(result, "摘要第一行\n摘要第二行")

    def test_falls_back_to_integrated_md_first_three_lines_when_summary_missing(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(maplab_bot, "INVESTMENT_OS_DIR", Path(tmp)):
                out_dir = maplab_bot._group_discussion_out_dir("2026-08-24", "topicid12345678", "research")
                out_dir.mkdir(parents=True)
                (out_dir / "integrated.md").write_text("【Claude 整合】\n\n第一行內容\n第二行內容\n第三行內容\n第四行內容\n", encoding="utf-8")
                result = maplab_bot._read_group_discussion_summary("2026-08-24", "topicid12345678", "research")
        self.assertIn("第一行內容", result)
        self.assertNotIn("第四行內容", result)

    def test_returns_empty_string_when_nothing_exists(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(maplab_bot, "INVESTMENT_OS_DIR", Path(tmp)):
                result = maplab_bot._read_group_discussion_summary("2026-08-24", "nosuchtopic00000", "research")
        self.assertEqual(result, "")


class RelayGuardTests(unittest.IsolatedAsyncioTestCase):
    """Group ingress (negative chat_id) must never reach the A0 offline
    resume/relay path — defense-in-depth guards added 2026-08-24."""

    async def test_resume_or_fallback_skips_negative_chat_id(self):
        with (
            patch.object(maplab_bot, "_a0_alive", return_value=False),
            patch.object(maplab_bot, "_a0_claim_single_reply") as claim_mock,
            patch.object(maplab_bot, "_a0_resume_ask", AsyncMock()) as resume_mock,
        ):
            await maplab_bot._a0_resume_or_fallback(MagicMock(), GROUP_CHAT_ID, "text")
        claim_mock.assert_not_called()
        resume_mock.assert_not_called()

    async def test_wait_then_maybe_resume_skips_negative_chat_id(self):
        with patch.object(maplab_bot, "_a0_has_replied_for") as replied_mock:
            await maplab_bot._a0_wait_then_maybe_resume(MagicMock(), GROUP_CHAT_ID, "text", "ts")
        replied_mock.assert_not_called()

    async def test_handle_message_itself_ignores_group_chat_type(self):
        update = MagicMock()
        update.effective_chat.id = GROUP_CHAT_ID
        update.effective_chat.type = "supergroup"
        update.effective_user.id = maplab_bot.OWNER_CHAT_ID
        update.message.text = "研調: 2330"
        update.message.message_id = 1
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.bot.send_message = AsyncMock()
        with patch.object(maplab_bot, "_a0_inbox_append") as inbox_mock:
            await maplab_bot.handle_message(update, context)
        inbox_mock.assert_not_called()
        context.bot.send_message.assert_not_called()
        update.message.reply_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
