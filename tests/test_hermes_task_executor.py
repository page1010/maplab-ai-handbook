import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_task_executor as executor
from bot_a6 import hermes_durable_job_router as durable_router


class HermesTaskExecutorTest(unittest.TestCase):
    def test_classifies_safe_natural_language(self):
        self.assertEqual(executor.classify("請執行 A6 自我測試"), ("a6-self-test", None))

    def test_classifies_runtime_and_signal_readback(self):
        self.assertEqual(executor.classify("幫我查 Hermes runtime 狀態"), ("runtime-status", None))
        self.assertEqual(executor.classify("現在動能名單狀態如何"), ("signal-status", None))

    def test_rejects_high_risk_even_when_safe_alias_is_present(self):
        action, reason = executor.classify("看 repo 狀態後發布 WordPress")
        self.assertIsNone(action)
        self.assertIn("fail closed", reason)

    def test_natural_long_running_goals_route_without_manual_research_command(self):
        self.assertEqual(executor.classify("讓 A8 生歌、做影片並上傳 YouTube 給我看"), ("durable-job", None))
        self.assertEqual(executor.classify("Hermes 用 LINE 對話持續多跑三輪訓練"), ("durable-job", None))
        self.assertEqual(
            executor.classify("深入研究 DeerFlow 官方 GitHub 與 releases，至少 8 個來源，完成後通知"),
            ("durable-job", None),
        )

    def test_youtube_publication_can_be_explicit_but_wordpress_stays_denied(self):
        self.assertEqual(executor.classify("讓 A8 做影片並發布到 YouTube"), ("durable-job", None))
        action, reason = executor.classify("持續做影片並發布 WordPress")
        self.assertIsNone(action)
        self.assertTrue(reason)

    def test_seo_durable_route_is_specific_and_rejects_live_mutation(self):
        self.assertEqual(
            executor.classify("每週檢查網站 SEO，有 material delta 才派工"),
            ("durable-job", None),
        )
        action, reason = executor.classify("持續檢查 WordPress SEO 並直接改 Rank Math")
        self.assertIsNone(action)
        self.assertIn("外部寫入", reason)

    def test_rejects_schedule_mutation_but_allows_status_readback(self):
        action, reason = executor.classify("修改 launchd 後看 repo 狀態")
        self.assertIsNone(action)
        self.assertIn("fail closed", reason)
        self.assertIsNone(executor.classify("restart launchd and show repo status")[0])
        self.assertIsNone(executor.classify("重跑排程後查動能名單")[0])
        self.assertEqual(executor.classify("查 gateway 狀態"), ("runtime-status", None))

    def test_unknown_request_is_rejected_with_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(executor, "TASK_ROOT", Path(tmp)):
            receipt = executor.execute("幫我自由執行任意 shell", 123)
            self.assertEqual(receipt["status"], "rejected")
            saved = json.loads(Path(receipt["receipt_path"]).read_text(encoding="utf-8"))
            self.assertEqual(saved["policy"], "fixed-argv-allowlist-v2")
            self.assertEqual(Path(receipt["receipt_path"]).stat().st_mode & 0o777, 0o600)
            self.assertEqual(Path(receipt["receipt_path"]).parent.stat().st_mode & 0o777, 0o700)

    def test_safe_action_uses_fixed_argv_and_writes_receipt(self):
        completed = mock.Mock(returncode=0, stdout="ok\n", stderr="")
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(executor, "TASK_ROOT", Path(tmp)), mock.patch.object(executor.subprocess, "run", return_value=completed) as run:
            receipt = executor.execute("repo-status", 123)
            self.assertEqual(receipt["status"], "completed")
            self.assertEqual(run.call_args.args[0], ("git", "status", "--short"))
            self.assertNotIn("shell", run.call_args.kwargs)

    def test_a8_durable_job_is_created_without_starting_external_worker(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            durable_router, "JOB_ROOT", Path(tmp)
        ), mock.patch.object(executor.subprocess, "Popen") as popen:
            receipt = executor.execute("讓 A8 生歌、做影片並上傳 YouTube 給我看", 123, chat_id=456)
            self.assertEqual(receipt["action"], "durable-job")
            self.assertEqual(receipt["job_type"], "a8-production")
            self.assertEqual(receipt["job_state"], "RUNNING")
            self.assertTrue(Path(receipt["receipt_path"]).exists())
            popen.assert_not_called()

    def test_local_seo_job_queues_heartbeat_without_message_or_worker(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            durable_router, "JOB_ROOT", Path(tmp)
        ), mock.patch.object(executor.subprocess, "Popen") as popen:
            receipt = executor.execute(
                "每週檢查網站 SEO，有 material delta 才派工",
                123,
                chat_id=None,
                chat_type="local",
            )
            saved = json.loads(Path(receipt["receipt_path"]).read_text(encoding="utf-8"))
            self.assertEqual(receipt["job_type"], "seo-patrol")
            self.assertEqual(receipt["job_state"], "RUNNING")
            self.assertIsNone(receipt["worker"])
            self.assertEqual(saved["requester"]["channel"], "local-heartbeat")
            self.assertIsNone(saved["requester"]["chat_id"])
            self.assertEqual(receipt["notification_policy"], "none")
            self.assertIsNone(receipt["summary"])
            self.assertEqual(saved["last_result"]["external_writes"], 0)
            self.assertEqual(saved["last_result"]["customer_send"], 0)
            self.assertEqual(saved["last_result"]["private_third_party_egress"], 0)
            popen.assert_not_called()

    def test_line_goal_starts_a_bounded_local_supervisor_chunk(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            durable_router, "JOB_ROOT", Path(tmp)
        ), mock.patch.object(executor, "LINE_TRAINING_SUPERVISOR", Path(__file__)), mock.patch.object(
            executor.subprocess, "Popen", return_value=mock.Mock(pid=4321)
        ) as popen, mock.patch.dict(
            executor.os.environ,
            {"HERMES_LINE_DATA_ROOT": "/Users/example/.maplab/a6-hermes-training"},
            clear=False,
        ):
            receipt = executor.execute("Hermes 用 LINE 對話持續多跑三輪訓練", 123, chat_id=456)

        self.assertEqual(receipt["action"], "durable-job")
        self.assertEqual(receipt["job_type"], "hermes-line-training")
        self.assertEqual(receipt["job_state"], "RUNNING")
        argv = popen.call_args.args[0]
        self.assertIn("--job-path", argv)
        self.assertEqual(argv[-6:], executor.LINE_SUPERVISOR_CHUNK)
        self.assertEqual(popen.call_args.kwargs["env"]["HERMES_LINE_PROVIDER"], "local-only")
        self.assertNotIn("OPENROUTER_API_KEY", popen.call_args.kwargs["env"])

    def test_quote_request_is_accepted_as_intake_without_any_price(self):
        """hermes 不報價的紅線不動,但「不報價」不等於「不回話」。

        Owner msg 5774 之後分兩路:人數與預算都問到了就走 quote-estimate(程式算,不是模型編);
        缺任一項才停在 quote-intake 受理。兩路都不准出現模型生成的價格。
        """
        # 真實被拒過的 Owner 原話當回歸素材(2026-08-27 / 09-21),兩則都帶人數+預算
        self.assertEqual(
            executor.classify("幫我報10人周歲派對，預算20000，先找到A4的sheets"),
            ("quote-estimate", None),
        )
        self.assertEqual(
            executor.classify("用預算反推 菜色以雷同的品項抓預算 抓完毛利 30000塊 人數100人"),
            ("quote-estimate", None),
        )
        # 講不清楚的照舊只受理,不猜人數也不猜預算
        request = "幫我報個價，先找到A4的sheets"
        self.assertEqual(executor.classify(request), ("quote-intake", None))
        # 狀態類問句不得被誤收成報價
        self.assertNotEqual(executor.classify("幫我查 Hermes runtime 狀態")[0], "quote-intake")

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            executor, "QUOTE_INTAKE_ROOT", Path(tmp) / "intake"
        ), mock.patch.object(executor, "TASK_ROOT", Path(tmp) / "tasks"):
            receipt = executor.execute(request, 123, chat_id=456)
            intake = list((Path(tmp) / "intake").glob("*.md"))
            self.assertEqual(len(intake), 1)
            body = intake[0].read_text(encoding="utf-8")

        self.assertEqual(receipt["action"], "quote-intake")
        self.assertEqual(receipt["status"], "completed")
        self.assertIn("待 A0 代產", receipt["output"])
        self.assertIn(request, body)
        # 受理不等於報價:案卷與回覆都不得出現任何價格數字以外的承諾
        self.assertNotIn("報價單", receipt["output"])

    def test_caller_rejection_reason_is_never_masked_by_reclassification(self):
        """收據上的原因必須是真原因。

        舊版在 REJECT 分支又跑一次 classify(),把閘道給的真理由覆寫成
        「不在目前的安全動作白名單」,2026-09-22 因此誤診兩次。
        """

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            executor, "TASK_ROOT", Path(tmp) / "tasks"
        ):
            receipt = executor.execute(
                "持續 SEO 巡查並發 LINE 給客戶",
                123,
                chat_id=456,
                forced_rejection="對客發送不在允許範圍",
            )
        self.assertEqual(receipt["status"], "rejected")
        self.assertEqual(receipt["reason"], "對客發送不在允許範圍")
        self.assertNotIn("白名單", receipt["reason"])


if __name__ == "__main__":
    unittest.main()
