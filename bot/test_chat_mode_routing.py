"""短問快答前綴的路由測試（Owner 2026-09-22 msg 5882）。

Owner 原話:「當我跟他溝通順便檢查他回覆我telegram 只看得到成果和單向對他說話,
沒有辦法溝通了」。

修法分兩層:
- 送信層:scripts/notify_owner.sh 改成會帶 reply_to_message_id,回覆掛在 Owner
  原訊息上(由 scripts/a0_reply_thread_check.sh 把關,不在本檔)。
- 路由層:bot.py 的 _parse_chat_mode —— Owner 句首打「聊」或「短」就走短問快答,
  不進 A0 的十五分鐘重批次。本檔測這一層。

這裡最要緊的不是「前綴有沒有被認出來」,而是「正常工作指令不可以被誤認成閒聊」。
「短期目標是什麼」「聊天記錄在哪」開頭都是前綴字,但它們是真的工作問題;如果只比對
開頭一個字,這些會被吃掉前綴、內容被改寫後丟去閒聊路徑,而且不落 a0_inbox ——
等於 Owner 的指令直接消失。所以分隔符那一條是硬性的。
"""

import importlib.util
import unittest
from pathlib import Path

BOT_PY = Path(__file__).resolve().parent / "bot.py"


def _load_parse_chat_mode():
    """只取 _parse_chat_mode 與 CHAT_MODE_LABEL,不 import 整個 bot 模組。

    bot.py 在 import 時會讀 .env、建 logger、碰 telegram 套件;測試不需要那些,
    而且在沒有憑證的環境會直接炸。這裡用 AST 挖出需要的片段來跑。
    """
    import ast

    source = BOT_PY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    wanted_funcs = {"_parse_chat_mode"}
    wanted_consts = {"CHAT_MODE_LABEL", "CHAT_MODE_TIMEOUT_S"}
    chunks = ["import os", "import re"]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in wanted_funcs:
            chunks.append(ast.get_source_segment(source, node))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in wanted_consts:
                    chunks.append(ast.get_source_segment(source, node))
    namespace: dict = {}
    exec("\n\n".join(chunks), namespace)
    return namespace


NS = _load_parse_chat_mode()
parse = NS["_parse_chat_mode"]


class TestChatModePrefixRecognised(unittest.TestCase):
    """Owner 主動打前綴時要認得出來,並且把前綴乾淨地剝掉。"""

    def test_space_separated(self):
        self.assertEqual(parse("聊 這個 logo 你覺得怎樣"), (True, "這個 logo 你覺得怎樣"))

    def test_full_width_colon(self):
        self.assertEqual(parse("聊：報價那個毛利率怎麼算的"), (True, "報價那個毛利率怎麼算的"))

    def test_half_width_colon(self):
        self.assertEqual(parse("短: 現在幾點"), (True, "現在幾點"))

    def test_comma_separators(self):
        self.assertEqual(parse("聊，隨便問一下"), (True, "隨便問一下"))
        self.assertEqual(parse("聊、隨便問一下"), (True, "隨便問一下"))

    def test_short_prefix_also_works(self):
        self.assertEqual(parse("短 你在做什麼"), (True, "你在做什麼"))

    def test_leading_whitespace_tolerated(self):
        self.assertEqual(parse("  聊 在嗎"), (True, "在嗎"))

    def test_bare_prefix_returns_empty_question(self):
        """只打前綴=仍然是短問模式,但沒有問題;呼叫端要回「你想問什麼」,
        不可以把裸前綴丟去問模型。"""
        self.assertEqual(parse("聊"), (True, ""))
        self.assertEqual(parse("短"), (True, ""))
        self.assertEqual(parse("聊 "), (True, ""))


class TestWorkInstructionsNeverMisrouted(unittest.TestCase):
    """本類是這個功能的安全網:工作指令被誤判成閒聊,等於 Owner 的指令消失
    (不落 a0_inbox、不寫收據、watchdog 也不會補跑)。一條都不准漏。"""

    def test_prefix_char_followed_by_more_chars_is_not_a_prefix(self):
        for text in (
            "短期目標是什麼",
            "聊天記錄在哪",
            "聊天室那個功能還要嗎",
            "短片素材放哪",
        ):
            with self.subTest(text=text):
                self.assertEqual(parse(text), (False, ""))

    def test_real_owner_instructions_this_week(self):
        for text in (
            "發給antigravity 留存 對標我們音樂頻道要有logo 叫台南chill out",
            "看照片整理內文做公司治理優化",
            "當我跟他溝通順便檢查他回覆我telegram 只看得到成果和單向對他說話，沒有辦法溝通了",
            "代答 這題你直接回",
            "why 開了 60% 的",
        ):
            with self.subTest(text=text):
                self.assertEqual(parse(text), (False, ""))

    def test_prefix_char_in_the_middle_is_not_a_prefix(self):
        self.assertEqual(parse("我想跟你聊 一下"), (False, ""))

    def test_empty_and_none_safe(self):
        self.assertEqual(parse(""), (False, ""))
        self.assertEqual(parse(None), (False, ""))


class TestChatModeGovernance(unittest.TestCase):
    def test_label_says_bot_not_fable5(self):
        """短問是 bot 答的,不是 Fable5 本人。標籤必須說清楚是誰在講話
        (owner-communication-standard),而且絕不能冒充 Fable5。"""
        label = NS["CHAT_MODE_LABEL"]
        self.assertIn("bot", label)
        self.assertNotIn("Fable5 本人", label)

    def test_timeout_is_short_enough_to_feel_like_a_conversation(self):
        """短問的意義就是不用等重批次。超時設定要明顯小於 A0 resume 的 900 秒,
        不然這條路等於沒開。"""
        self.assertLessEqual(NS["CHAT_MODE_TIMEOUT_S"], 300)


class TestRoutingWiredBeforeInboxAppend(unittest.TestCase):
    """短問必須在 _a0_inbox_append 之前就 return,否則閒聊會落進工作線,
    watchdog 會把它當成未回覆的 Owner 指令去逼 A0 補跑(就是今天踩過的坑)。"""

    def test_chat_mode_branch_precedes_inbox_append(self):
        source = BOT_PY.read_text(encoding="utf-8")
        handler_start = source.index("async def handle_message(")
        handler = source[handler_start:handler_start + 4000]
        chat_mode_at = handler.index("_parse_chat_mode(text)")
        inbox_at = handler.index("_a0_inbox_append(")
        self.assertLess(
            chat_mode_at,
            inbox_at,
            "短問分支必須排在 _a0_inbox_append 之前",
        )


if __name__ == "__main__":
    unittest.main()
