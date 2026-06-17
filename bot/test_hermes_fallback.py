import os
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

import bot as maplab_bot


class FakeHermesProc:
    def __init__(self, stdout: str, stderr: str = "", returncode: int = 0):
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode
        self.killed = False

    async def communicate(self):
        return self._stdout.encode(), self._stderr.encode()

    def kill(self):
        self.killed = True


class HermesFallbackTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        maplab_bot._conv_history.clear()

    def tearDown(self):
        maplab_bot._conv_history.clear()

    async def test_claude_success_does_not_call_hermes(self):
        with (
            patch.object(
                maplab_bot,
                "_claude_ask_raw",
                AsyncMock(return_value=maplab_bot.ModelResult(ok=True, answer="CLAUDE_OK")),
            ) as claude_raw,
            patch.object(maplab_bot, "hermes_ask", AsyncMock(return_value="HERMES_OK")) as hermes,
            patch.object(maplab_bot, "_save_conv_history"),
        ):
            answer = await maplab_bot.claude_ask_with_fallback(1001, "hello")

        self.assertEqual(answer, "CLAUDE_OK")
        claude_raw.assert_awaited_once()
        hermes.assert_not_called()
        self.assertEqual(len(maplab_bot._get_history(1001)), 2)

    async def test_quota_failure_calls_hermes_once_and_receipts(self):
        claude_result = maplab_bot.ModelResult(
            ok=False,
            answer="⚠️ Claude 錯誤: usage limit reached",
            failure_kind="quota",
            stderr="usage limit reached",
        )
        with (
            patch.object(maplab_bot, "_claude_ask_raw", AsyncMock(return_value=claude_result)),
            patch.object(maplab_bot, "hermes_ask", AsyncMock(return_value="HERMES_OK")) as hermes,
            patch.object(maplab_bot, "_save_conv_history"),
        ):
            answer = await maplab_bot.claude_ask_with_fallback(1002, "quota test")

        hermes.assert_awaited_once()
        self.assertIn("primary_failed_reason", answer)
        self.assertIn("fallback=Hermes", answer)
        self.assertIn("model:", answer)
        self.assertIn("agent:", answer)
        self.assertIn("date:", answer)
        self.assertIn("memory_sources:", answer)
        self.assertIn("allowed_actions:", answer)
        self.assertIn("next_check:", answer)
        self.assertIn("HERMES_OK", answer)
        self.assertEqual(len(maplab_bot._get_history(1002)), 2)

    async def test_force_fallback_skips_claude(self):
        with (
            patch.dict(os.environ, {"MAPLAB_FORCE_HERMES_FALLBACK": "1"}, clear=False),
            patch.object(maplab_bot, "_claude_ask_raw", AsyncMock()) as claude_raw,
            patch.object(maplab_bot, "hermes_ask", AsyncMock(return_value="FORCED_HERMES")) as hermes,
            patch.object(maplab_bot, "_save_conv_history"),
        ):
            answer = await maplab_bot.claude_ask_with_fallback(1003, "force fallback")

        claude_raw.assert_not_called()
        hermes.assert_awaited_once()
        self.assertIn("fallback=Hermes", answer)
        self.assertIn("FORCED_HERMES", answer)

    async def test_disabled_fallback_returns_claude_failure(self):
        claude_result = maplab_bot.ModelResult(
            ok=False,
            answer="⚠️ Claude 錯誤: usage limit reached",
            failure_kind="quota",
            stderr="usage limit reached",
        )
        with (
            patch.dict(os.environ, {"HERMES_FALLBACK_ENABLED": "0"}, clear=False),
            patch.object(maplab_bot, "_claude_ask_raw", AsyncMock(return_value=claude_result)),
            patch.object(maplab_bot, "hermes_ask", AsyncMock(return_value="HERMES_OK")) as hermes,
        ):
            answer = await maplab_bot.claude_ask_with_fallback(1004, "disabled fallback")

        hermes.assert_not_called()
        self.assertEqual(answer, "⚠️ Claude 錯誤: usage limit reached")

    async def test_photo_path_reaches_hermes(self):
        claude_result = maplab_bot.ModelResult(
            ok=False,
            answer="⚠️ Claude 錯誤: rate limit",
            failure_kind="rate_limit",
            stderr="rate limit",
        )
        image_path = "/Users/pagemacmini/maplab-ai-handbook/data/telegram-photos/sample.jpg"
        user_message = f"Owner 傳了一張圖片，已存在 {image_path}，請分析圖片。"
        with (
            patch.object(maplab_bot, "_claude_ask_raw", AsyncMock(return_value=claude_result)),
            patch.object(maplab_bot, "hermes_ask", AsyncMock(return_value="IMAGE_OK")) as hermes,
            patch.object(maplab_bot, "_save_conv_history"),
        ):
            await maplab_bot.claude_ask_with_fallback(1005, user_message)

        hermes.assert_awaited_once()
        args, kwargs = hermes.await_args
        self.assertIn(image_path, args[1])
        self.assertIn("rate limit", kwargs["fallback_reason"])

    def test_prompt_includes_memory_anchors_and_respects_budget(self):
        history = maplab_bot._get_history(1006)
        history.append({"role": "user", "content": "x" * 10000})
        history.append({"role": "assistant", "content": "y" * 10000})
        with patch.dict(os.environ, {"HERMES_PROMPT_MAX_CHARS": "9000"}, clear=False):
            prompt = maplab_bot.build_hermes_prompt(
                1006,
                "請先判斷我是不是又在改錯方向",
                fallback_reason="⚠️ Claude 錯誤: usage limit reached",
            )

        self.assertLessEqual(len(prompt), 9000)
        self.assertIn("CURRENT_STATUS.md", prompt)
        self.assertIn("pitfalls.md", prompt)
        self.assertIn("stage_4_owner_message", prompt)

    def test_failure_classifier(self):
        self.assertEqual(maplab_bot._classify_claude_failure("usage limit reached"), "quota")
        self.assertEqual(maplab_bot._classify_claude_failure("rate limit 429"), "rate_limit")
        self.assertEqual(maplab_bot._classify_claude_failure("OAuth token expired"), "auth")
        self.assertEqual(maplab_bot._classify_claude_failure("service unavailable"), "primary_unavailable")
        self.assertEqual(maplab_bot._classify_claude_failure("syntax error"), "unknown")

    def test_toolset_routing_uses_single_purpose_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(maplab_bot._hermes_toolsets_for_message("一般文字問題"), "none")
            self.assertEqual(
                maplab_bot._hermes_toolsets_for_message(
                    "Owner 傳了一張圖片，已存在 /tmp/data/telegram-photos/a.jpg"
                ),
                "vision",
            )
        with patch.dict(os.environ, {"HERMES_FALLBACK_TOOLSETS": "memory,vision"}, clear=False):
            self.assertEqual(
                maplab_bot._hermes_toolsets_for_message("/tmp/data/telegram-photos/a.jpg"),
                "memory,vision",
            )

    def test_degraded_hermes_output_detector(self):
        self.assertTrue(maplab_bot._looks_like_degraded_hermes_output("HERII"))
        self.assertTrue(maplab_bot._looks_like_degraded_hermes_output("HERIThe"))
        self.assertFalse(maplab_bot._looks_like_degraded_hermes_output("HERMES_GEMMA_SHORT_WRAPPER_OK"))

    def test_runtime_secret_redaction(self):
        text = "POST https://api.telegram.org/bot123456:ABC_def-ghi/getUpdates"
        redacted = maplab_bot._redact_runtime_secrets(text)
        self.assertNotIn("123456:ABC_def-ghi", redacted)
        self.assertIn("bot<TELEGRAM_BOT_TOKEN>", redacted)

    def test_exact_reply_contract_detector(self):
        message = "請只回覆 HERMES_GEMMA_STAGED_PROMPT_OK，不要解釋。"
        self.assertEqual(
            maplab_bot._extract_exact_reply_request(message),
            "HERMES_GEMMA_STAGED_PROMPT_OK",
        )
        self.assertEqual(
            maplab_bot._exact_reply_contract_violation(message, "P0: OK\nHERMES_GEMMA_STAGED_PROMPT_OK"),
            "HERMES_GEMMA_STAGED_PROMPT_OK",
        )
        self.assertEqual(
            maplab_bot._exact_reply_contract_violation(message, "HERMES_GEMMA_STAGED_PROMPT_OK"),
            "",
        )

    async def test_exact_reply_guard_repairs_then_returns_expected(self):
        message = "請只回覆 HERMES_GEMMA_STAGED_PROMPT_OK，不要解釋。"
        fake_create = AsyncMock(
            side_effect=[
                FakeHermesProc("P0: OK\nHERMES_GEMMA_STAGED_PROMPT_OK\nAnswer: extra"),
                FakeHermesProc("仍然多講一句 HERMES_GEMMA_STAGED_PROMPT_OK"),
            ]
        )
        with (
            patch("asyncio.create_subprocess_exec", fake_create),
            patch.object(maplab_bot, "_ensure_no_tools_hermes_home", return_value=Path("/tmp/hermes-test")),
            patch.dict(os.environ, {"HERMES_FALLBACK_TOOLSETS": "none"}, clear=False),
        ):
            answer = await maplab_bot.hermes_ask(1010, message, fallback_reason="forced")

        self.assertEqual(answer, "HERMES_GEMMA_STAGED_PROMPT_OK")
        self.assertEqual(fake_create.await_count, 2)


if __name__ == "__main__":
    unittest.main()
