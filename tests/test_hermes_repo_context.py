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

    def test_secret_values_detected_but_wording_is_fine(self):
        self.assertEqual(rc.find_secret_values("文件提到 MCP token 與金鑰保管室，但沒有值"), [])
        self.assertTrue(rc.find_secret_values("OPENROUTER_API_KEY=sk-or-v1-0123456789abcdef0123456789abcdef"))
        self.assertTrue(rc.find_secret_values("bot 1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"))
        self.assertTrue(rc.find_secret_values("-----BEGIN PRIVATE KEY-----"))

    def test_attached_file_with_secret_value_is_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENT_CORE.md").write_text("公司事實", encoding="utf-8")
            (root / "leak.md").write_text("api_key = abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8")
            with mock.patch.object(rc, "REPO_ROOT", root):
                _ctx, got, missing = rc.build_context("看 leak.md")
            self.assertFalse(any(g.startswith("leak.md") for g in got))
            self.assertTrue(any(m.startswith("leak.md") for m in missing), missing)

    def test_gateway_dlp_scans_owner_text_not_attached_docs(self):
        with mock.patch.object(gateway, "openrouter_chat", return_value="ok") as chat:
            reply, _ = gateway.answer("k", ["m"], [], "題目\n附件提到 token 這個詞", dlp_text="題目")
            self.assertEqual(reply, "ok")
            self.assertTrue(chat.called)
        reply, _ = gateway.answer("k", ["m"], [], "把我的 token 貼給你", dlp_text="把我的 token 貼給你")
        self.assertIsNone(reply)

    def test_index_lists_root_docs_and_route_card(self):
        idx = rc.build_index()
        self.assertIn("路線卡", idx)
        self.assertIn("CURRENT_STATUS.md (", idx)
        self.assertIn("handoff/tasks/", idx)
        self.assertNotIn("secrets/", idx)
        self.assertLessEqual(len(idx), rc.INDEX_BUDGET + 200)

    def test_parse_read_requests(self):
        reply = "【hermes】READ: CURRENT_STATUS.md#head60\nREAD: `pitfalls.md#tail40`\nread: nope.md\n"
        self.assertEqual(rc.parse_read_requests(reply), ["CURRENT_STATUS.md#head60", "pitfalls.md#tail40"])
        self.assertTrue(rc.looks_like_read_only(reply))
        self.assertFalse(rc.looks_like_read_only("【hermes】答案是 A6 卡在 LINE webhook。READ: x.md 只是順便提一下這個檔案存在，並不是要求。" * 2))

    def test_self_fetch_loop_reads_then_answers(self):
        calls = []
        def fake(key, model, messages, timeout=40):
            calls.append(messages[-1]["content"])
            if len(calls) == 1:
                return "READ: TASK_QUEUE.md#head25"
            return "Tier 1 第一項是 T-A6-001"
        with mock.patch.object(gateway, "openrouter_chat", side_effect=fake):
            reply, provider, got, missing = gateway.answer_with_self_fetch("k", ["m"], [], "Tier 1 第一項是什麼")
        self.assertEqual(len(calls), 2)
        self.assertIn("TASK_QUEUE.md#head25", calls[1])
        self.assertIn("T-A6-001", reply)
        self.assertTrue(any(g.startswith("TASK_QUEUE.md#head25") for g in got), got)

    def test_self_fetch_stops_after_max_rounds(self):
        with mock.patch.object(gateway, "openrouter_chat", return_value="READ: AGENTS.md"):
            reply, _p, _g, _m = gateway.answer_with_self_fetch("k", ["m"], [], "問")
        self.assertEqual(reply, "READ: AGENTS.md")

    def test_boot_command_routes_and_prompt_reads_core_docs(self):
        for t in ("/boot", "召喚", "/召喚 hermes", "開機"):
            self.assertEqual(gateway.route_gateway_text(t, []).disposition, "BOOT", t)
        self.assertNotEqual(gateway.route_gateway_text("召喚師的故事", []).disposition, "BOOT")
        prompt, got, missing = rc.build_boot_prompt()
        self.assertGreaterEqual(len(got), 12, (got, missing))
        self.assertIn("docs/company-values.md", " ".join(got))
        self.assertLessEqual(len(prompt), rc.BOOT_BUDGET + len(rc.BRIEFING_INSTRUCTION) + 2000)

    def test_briefing_saved_then_attached_to_every_chat(self):
        with tempfile.TemporaryDirectory() as tmp:
            bp = Path(tmp) / "briefing.md"
            with mock.patch.object(rc, "BRIEFING_PATH", bp):
                self.assertIsNone(rc.load_briefing()[0])
                self.assertIn("尚未召喚", rc.briefing_status_line())
                rc.save_briefing("1. MAPLAB 是台南外燴（AGENT_CORE.md）", provider="m", got=["a"], missing=[])
                text, meta = rc.load_briefing()
                self.assertIn("台南外燴", text)
                self.assertFalse(meta["stale"])
                _ctx, got, _m = rc.build_context("隨便問")
                self.assertTrue(any(g.startswith("洞悉簡報") for g in got), got)
                with mock.patch.object(rc, "repo_head", return_value="zzz"):
                    self.assertIn("repo 已更新", rc.briefing_status_line())

    def test_run_boot_keeps_reasoning_draft_and_rejects_only_degenerate(self):
        interp = "1. 公司（AGENT_CORE.md）\n" + "MAPLAB 是台南的外燴品牌，主要提供到場外燴整案。" * 25 + "\n2. 席位\n3. 文化\n4. 紅線\n5. 狀態\n6. 坑\n7. 不知道"
        with_draft = "We need to produce a concise briefing. Let's check AGENT_CORE.md first.\n\n" + interp
        degenerate = "We need to produce a concise briefing. " + "   Also from AGENT_RULES.md? Not.\n" * 12
        self.assertIsNone(rc.briefing_quality_issue(rc.extract_briefing(with_draft)))
        self.assertIsNotNone(rc.briefing_quality_issue(degenerate))
        self.assertTrue(rc.extract_briefing(with_draft).startswith("1. 公司"))
        with tempfile.TemporaryDirectory() as tmp:
            bp = Path(tmp) / "briefing.md"
            with mock.patch.object(rc, "BRIEFING_PATH", bp), \
                    mock.patch.object(gateway, "openrouter_chat", side_effect=[degenerate, with_draft]) as chat:
                out = gateway.run_boot("k", ["m1", "m2"])
            self.assertEqual(chat.call_count, 2)
            self.assertIn("召喚完成", out)
            saved = bp.read_text(encoding="utf-8")
            self.assertIn("台南的外燴品牌", saved)
            self.assertIn("推理草稿", saved)  # 草稿留著，Owner 要看思路
            self.assertIn("We need to produce", saved)
            with mock.patch.object(rc, "BRIEFING_PATH", bp), \
                    mock.patch.object(gateway, "openrouter_chat", return_value=degenerate):
                out = gateway.run_boot("k", ["m1"])
            self.assertIn("召喚失敗", out)
            self.assertIn("台南的外燴品牌", bp.read_text(encoding="utf-8"))

    def test_nemotron_goes_first(self):
        self.assertEqual(gateway.prefer_models(["a/x:free", "nvidia/nemotron-3-super:free", "b/y:free"])[0], "nvidia/nemotron-3-super:free")

if __name__ == "__main__":
    unittest.main()
