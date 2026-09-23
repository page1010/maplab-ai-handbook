"""工作單五欄模板與檢查器的測試。

AGENT_RULES.md SECTION 27 第四節:SOP 必配機械檢查,不准只留心得。
這支就是那個機械檢查的檢查——確保模板不會被悄悄拿掉欄位,
也確保檢查器真的會擋(擋不住的檢查器等於沒有)。
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "handoff" / "tasks" / "_WORK_ORDER_TEMPLATE.md"
CHECKER = REPO / "scripts" / "check_work_order.py"

_spec = importlib.util.spec_from_file_location("check_work_order", CHECKER)
check_work_order = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_work_order)


GOOD = """# Task Card: T-TEST-001 — 測試用工作單

- **結果**: 跑完後 state/foo.json 裡有 12 筆通過規則的紀錄,重跑得到同一批
- **指標**: python3 -m unittest tests.test_foo 全綠,且 12 筆各有來源欄
- **期限**: 2026-09-24 12:00 前
- **權限**: 只能動 bot_a6/ 與 tests/;可 commit 不可 push;不得碰金鑰與真倉
- **回報點**: 做完當輪回寫本卡。done = 指標那句被驗證且 log 落在 state/foo.log;blocked = 缺上游資料時寫卡點與已試過什麼
- **動作可逆性**: 可逆
"""


def write(text: str) -> Path:
    tmp = Path(tempfile.mkdtemp()) / "card.md"
    tmp.write_text(text, encoding="utf-8")
    return tmp


class WorkOrderTemplateTest(unittest.TestCase):
    def test_template_file_exists_and_carries_the_five_hard_columns(self):
        """SECTION 27 第三節說規則寫了,任務 #22 說模板要落成檔案——這裡驗它真的在。"""
        self.assertTrue(TEMPLATE.is_file(), "工作單模板檔不存在")
        text = TEMPLATE.read_text(encoding="utf-8")
        for name in check_work_order.REQUIRED:
            self.assertIn(f"**{name}**", text, f"模板缺第「{name}」欄")
        self.assertIn("**動作可逆性**", text)
        # 終態定義與 win-01 的真因要留在模板裡,否則下一個人只會看到欄位不知為何要填
        self.assertIn("done", text)
        self.assertIn("blocked", text)
        self.assertIn("picked-and-failed", text)
        self.assertIn("scripts/check_work_order.py", text)

    def test_template_itself_fails_the_check_because_it_is_all_placeholders(self):
        """模板是空殼,拿模板去派工必須被擋——擋不住表示佔位符判斷壞了。"""
        problems = check_work_order.check(TEMPLATE)
        self.assertTrue(problems, "模板全是佔位符卻通過檢查")
        self.assertTrue(any("未填" in p for p in problems), problems)

    def test_a_properly_filled_order_passes(self):
        self.assertEqual(check_work_order.check(write(GOOD)), [])

    def test_each_missing_column_is_caught_by_name(self):
        for name in check_work_order.REQUIRED:
            broken = "\n".join(
                line for line in GOOD.splitlines() if f"**{name}**" not in line
            )
            problems = check_work_order.check(write(broken))
            self.assertTrue(
                any(name in p for p in problems),
                f"拿掉「{name}」欄竟然沒被抓到:{problems}",
            )

    def test_report_column_without_terminal_states_is_rejected(self):
        """「做完跟我說」不算回報點:done 與 blocked 都要定義。"""
        vague = GOOD.replace(
            "做完當輪回寫本卡。done = 指標那句被驗證且 log 落在 state/foo.log;"
            "blocked = 缺上游資料時寫卡點與已試過什麼",
            "做完跟我說",
        )
        problems = check_work_order.check(write(vague))
        self.assertTrue(any("終態" in p for p in problems), problems)

        half = GOOD.replace("blocked = 缺上游資料時寫卡點與已試過什麼", "有問題再說")
        problems = check_work_order.check(write(half))
        self.assertTrue(any("blocked" in p for p in problems), problems)

    def test_cli_exit_codes_are_fail_closed(self):
        """exit 2 = 不准派工,與報價引擎「需人工」同一個 fail-closed 精神。"""
        ok = subprocess.run(
            [sys.executable, str(CHECKER), str(write(GOOD))],
            capture_output=True, text=True,
        )
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("可派工", ok.stdout)

        blocked = subprocess.run(
            [sys.executable, str(CHECKER), str(TEMPLATE)],
            capture_output=True, text=True,
        )
        self.assertEqual(blocked.returncode, 2, blocked.stdout + blocked.stderr)
        self.assertIn("不准派工", blocked.stdout)

        missing = subprocess.run(
            [sys.executable, str(CHECKER), str(REPO / "no-such-card.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(missing.returncode, 1)

    def test_section_27_points_at_the_template_so_the_rule_is_closed_loop(self):
        """規則與模板要互指,否則規則會再變成只寫不做(任務 #22 的成因)。"""
        rules = (REPO / "AGENT_RULES.md").read_text(encoding="utf-8")
        self.assertIn("_WORK_ORDER_TEMPLATE.md", rules)
        self.assertIn("check_work_order.py", rules)


if __name__ == "__main__":
    unittest.main()
