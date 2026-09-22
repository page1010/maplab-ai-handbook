import tempfile
import unittest
from pathlib import Path
from unittest import mock

from bot_a6 import hermes_task_executor as executor
from bot_a6 import quote_calc


class QuoteCalcTest(unittest.TestCase):
    def test_every_number_in_the_price_book_has_a_source(self):
        """紅線「絕不編價」的機械化檢查:沒有 source 的數字不准存在。"""

        book = quote_calc.load_price_book()
        for line in book["menu_lines"]:
            self.assertTrue(line["price_source"].strip(), line["key"])
            self.assertTrue(line["cost_source"].strip(), line["key"])
            self.assertGreater(line["price"], 0, line["key"])
            self.assertGreater(quote_calc._unit_cost(line), 0, line["key"])
        for service in book["service_lines"]:
            self.assertTrue(service["source"].strip(), service["key"])

    def test_sandwich_cost_is_half_the_takeout_price_and_cutting_small_doubles_pieces(self):
        """Owner msg 5800:三明治成本以外帶售價的 50% 計算,切小一點提高毛利。"""

        whole = quote_calc.lookup("蛋沙拉三明治")
        self.assertEqual(quote_calc._unit_cost(whole), whole["price"] * 0.5)
        self.assertEqual(whole["pieces_per_unit"], 12)

        cut = quote_calc.lookup("蛋沙拉三明治_切小")
        # 切小:單位成本不變、件數加倍 → 每件成本砍半
        self.assertEqual(quote_calc._unit_cost(cut), quote_calc._unit_cost(whole))
        self.assertEqual(cut["pieces_per_unit"], whole["pieces_per_unit"] * 2)
        self.assertAlmostEqual(
            quote_calc._cost_per_piece(cut), quote_calc._cost_per_piece(whole) / 2
        )

        # 切小本身不改毛利率(售價與成本同一組不動);它買的是件數
        same_units = [("蛋沙拉三明治", 3)], [("蛋沙拉三明治_切小", 3)]
        whole_plan = quote_calc.plan_by_items(same_units[0], package_price=30000, pax=100)
        cut_plan = quote_calc.plan_by_items(same_units[1], package_price=30000, pax=100)
        self.assertEqual(whole_plan["food_cost"], cut_plan["food_cost"])
        self.assertEqual(cut_plan["pieces"], whole_plan["pieces"] * 2)

    def test_flatbread_cost_unit_is_per_piece_not_per_whole_round(self):
        """薄餅的「份」是一片還是整張 8 吋,決定成本差 8 倍。已交叉驗證=一片。

        依據:items_master APP026 法式黑松露野菇烤薄餅 20/份,菜單同品 $320/8 片 → 40/片,
        20 正好是 40 的 50%,與 Owner msg 5800 的「成本=外帶售價 50%」吻合。
        若「份」指整張,成本會是 2.5/片(毛利 93.75%),與全表其他品項的食材成本佔比完全不合。
        這支測試把結論釘住,免得下輪又當成未解問題重新猜一次。
        """
        flatbread = quote_calc.lookup("打拋豬薄餅")
        self.assertEqual(flatbread["pieces_per_unit"], 8)
        per_piece = quote_calc._cost_per_piece(flatbread)
        # 落在「一片」的量級(20 出頭),不是「整張」的量級(個位數)
        self.assertGreater(per_piece, 15)
        self.assertLess(per_piece, 30)
        # 嚴格套 50% 規則的值與現行推估差距要很小,否則這條交叉驗證就不成立
        strict_half = flatbread["price"] * 0.5 / flatbread["pieces_per_unit"]
        self.assertLess(abs(per_piece - strict_half) / strict_half, 0.05)

        # 全表沒有任何品項的食材成本佔售價低於 10%——這是上面反證的基礎
        for row in quote_calc.margin_table():
            self.assertLess(row["margin_rate"], 0.9, row["key"])

    def test_retired_plan_is_neither_listed_nor_runnable(self):
        """Owner msg 5800「why 開了 60% 的」——作廢版不得再出現在選項裡。"""

        self.assertNotIn("A-60", [plan["name"] for plan in quote_calc.reference_plans()])
        with self.assertRaises(quote_calc.QuoteError) as ctx:
            quote_calc.run_reference_plan("A-60")
        self.assertIn("已作廢", str(ctx.exception))

    def test_owner_piece_count_plan_holds_the_80_percent_floor(self):
        """H3 是照 Owner msg 5800 四條配的,毛利率必須守住他定的下限。"""

        book = quote_calc.load_price_book()
        floor = book["rules"]["target_margin_floor"]
        result = quote_calc.run_reference_plan("H3-OWNER")
        self.assertGreaterEqual(result["margin_rate"], floor)
        # 便宜的多、貴的少:件數最多的那幾項必須是每件成本最低的那幾項
        by_pieces = sorted(result["lines"], key=lambda row: row["pieces"], reverse=True)
        self.assertIn(by_pieces[0]["key"], ("梅子醬蝦棗", "打拋豬薄餅"))
        pizza = [row for row in result["lines"] if "pizza" in row["key"] or "披薩" in row["key"]]
        self.assertTrue(pizza)
        for row in pizza:
            self.assertEqual(row["units"], 1)

    def test_unknown_item_is_never_priced_by_guessing(self):
        with self.assertRaises(quote_calc.QuoteError):
            quote_calc.lookup("神秘新菜")
        with self.assertRaises(quote_calc.QuoteError):
            quote_calc.plan_by_items([("神秘新菜", 1)])

    def test_menu_sum_ceiling_matches_highest_margin_item(self):
        """Owner msg 5771「毛利必須高於80%」的答案是數學事實,不是方案。"""

        ceiling = quote_calc.menu_sum_ceiling()
        rows = quote_calc.margin_table()
        self.assertAlmostEqual(ceiling["ceiling_rate"], rows[0]["margin_rate"])
        self.assertLess(ceiling["ceiling_rate"], 0.8)

    def test_cutting_piece_count_does_not_change_margin_rate(self):
        """砍件數不改毛利率(收入與成本等比降)——這條講錯過一次就會誤導 Owner。"""

        half = quote_calc.plan_by_items([("梅子醬蝦棗", 50), ("綠咖喱小鹹派", 20)])
        full = quote_calc.plan_by_items([("梅子醬蝦棗", 100), ("綠咖喱小鹹派", 40)])
        self.assertEqual(half["margin_rate"], full["margin_rate"])
        self.assertEqual(full["pieces"], half["pieces"] * 2)

    def test_h1_falls_under_the_80_floor_once_owners_sandwich_rule_applies(self):
        """H1 原呈 Owner 的是食材 5,920／80.3%,件數與倍率不變但成本基礎變了。

        Owner msg 5800 把三明治成本改成外帶售價的 50%(蛋沙拉 360→400、薯泥 300→410),
        H1 的食材成本升到 6,070 → 毛利率 79.8%,**跌破他自己定的 80% 下限**。
        這是他的新規則帶出來的後果,不是算錯,所以釘住新數字並要 Owner 知道 H1 已不合格。
        """
        result = quote_calc.run_reference_plan("H1-80")
        self.assertEqual(result["food_cost"], 6070)
        self.assertEqual(result["margin_rate"], 0.7977)
        self.assertLess(
            result["margin_rate"], quote_calc.load_price_book()["rules"]["target_margin_floor"]
        )
        # 件數與倍率沒被這條規則動到
        self.assertEqual(result["pieces"], 276)
        self.assertEqual(result["price_multiple_vs_menu"], 1.97)
        self.assertEqual(result["pieces_per_pax"], 2.76)
        joined = " ".join(result["warnings"])
        self.assertIn("不得列菜單單價", joined)
        self.assertIn("輕食小點", joined)

    def test_reference_plan_h2_still_clears_the_floor(self):
        """H2 原 85.3%,套上 5800 的三明治成本後 84.8%,仍在 80% 之上。"""

        result = quote_calc.run_reference_plan("H2-85")
        self.assertEqual(result["food_cost"], 4566)
        self.assertEqual(result["margin_rate"], 0.8478)
        self.assertEqual(result["pieces"], 212)
        self.assertGreaterEqual(result["margin_rate"], 0.8)

    def test_scale_keeps_menu_choice_with_the_human_and_refuses_impossible_margins(self):
        scaled = quote_calc.scale_mix_to_margin(
            [("梅子醬蝦棗", 10), ("綠咖喱小鹹派", 4)], 30000, 100, 0.8
        )
        self.assertGreaterEqual(scaled["margin_rate"], 0.8)
        self.assertLessEqual(scaled["food_cost"], scaled["cost_budget"])
        # 沙拉盆食材 600/盆,整案價 1,000 元要 80% 毛利=成本上限 200 元,一輪都配不下。
        with self.assertRaises(quote_calc.QuoteError) as ctx:
            quote_calc.scale_mix_to_margin([("水耕沙拉盆", 1)], 1000, 10, 0.8)
        self.assertIn("做不到", str(ctx.exception))

    def test_change_order_reports_margin_points_not_just_new_number(self):
        before = quote_calc.run_reference_plan("H1-80")
        after = quote_calc.plan_by_items(
            [(item["key"], item["units"]) for item in quote_calc.reference_plans()[0]["mix"]]
            + [("水耕沙拉盆", 1)],
            package_price=30000,
            pax=100,
        )
        delta = quote_calc.change_order(before, after)
        self.assertEqual(delta["food_cost_delta"], 600)
        self.assertLess(delta["margin_points_delta"], 0)
        self.assertAlmostEqual(delta["margin_points_delta"], -2.0, places=1)

    def test_external_item_price_follows_the_local_base_times_1_35_rule(self):
        """小肚肚案 Owner msg 5197:緞帶在地 1,000 → 對外 1,350。"""

        priced = quote_calc.external_item_price(1000)
        self.assertEqual(priced["external_price"], 1350)
        self.assertEqual(priced["markup"], 1.35)

    def test_parse_brief_lists_what_is_still_missing_instead_of_guessing(self):
        parsed = quote_calc.parse_brief("用預算反推 30000塊 人數100人 毛利要80% 10月上旬")
        self.assertEqual(parsed["facts"]["pax"], 100)
        self.assertEqual(parsed["facts"]["budget"], 30000)
        self.assertEqual(parsed["facts"]["target_margin"], 0.8)
        self.assertEqual(parsed["missing"], [])

        vague = quote_calc.parse_brief("幫我報個價")
        self.assertEqual(vague["facts"], {})
        self.assertEqual(len(vague["missing"]), 3)

        per_pax = quote_calc.parse_brief("40人 每人300元")
        self.assertEqual(per_pax["facts"]["budget"], 12000)
        self.assertTrue(per_pax["facts"]["budget_from_per_pax"])


class QuoteEstimateRoutingTest(unittest.TestCase):
    def test_full_brief_routes_to_estimate_and_vague_one_stays_intake(self):
        """Owner msg 5774:人數+預算齊了就要幫他算,不要只回一句已受理。"""

        self.assertEqual(
            executor.classify("用預算反推 菜色以雷同的品項抓預算 抓完毛利 30000塊 人數100人")[0],
            "quote-estimate",
        )
        self.assertEqual(executor.classify("幫我報個價")[0], "quote-intake")
        self.assertEqual(executor.classify("幫我報10人周歲派對，預算20000")[0], "quote-estimate")

    def test_estimate_receipt_carries_real_numbers_and_the_no_send_marker(self):
        request = "用預算反推 抓完毛利 毛利要80% 30000塊 人數100人"
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            executor, "QUOTE_INTAKE_ROOT", Path(tmp) / "intake"
        ), mock.patch.object(executor, "TASK_ROOT", Path(tmp) / "tasks"):
            receipt = executor.execute(request, 123, chat_id=456)
            intake = list((Path(tmp) / "intake").glob("*.md"))
            self.assertEqual(len(intake), 1)
            case_body = intake[0].read_text(encoding="utf-8")

        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["action"], "quote-estimate")
        output = receipt["output"]
        self.assertIn("不得直接發給客人", output)
        self.assertIn("80.3%", output)
        self.assertIn("276 件", output)
        self.assertIn("天花板", output)
        self.assertIn("對外定價決定", output)
        self.assertIn(request, case_body)

    def test_catering_plan_must_name_its_takeout_derived_costs(self):
        """Owner msg 5824:「這是外燴的單,如果要拿外帶售價參考值取 50%,本來就不是外帶,你沒問我覺得我會被打」。

        本檔 rules.never 早就寫著「外燴整案價與外帶單品價不混用」,我卻讓三明治成本從外帶售價推導
        進來、還標成實數。這支測試把 Owner 的糾正交給程式擋:整案價(外燴)模式下,凡成本基礎是
        外帶推導的品項都要被點名並報出佔食材成本比重,且不得再標成實數。
        """
        h4 = quote_calc.run_reference_plan("H4-OWNER")
        self.assertEqual(h4["takeout_basis_items"], ["薯泥蛋沙拉三明治_切小", "蛋沙拉三明治_切小"])
        self.assertGreater(h4["takeout_basis_cost_share"], 0.4)
        self.assertTrue(any("Owner msg 5824" in w for w in h4["warnings"]))
        for line in quote_calc.load_price_book()["menu_lines"]:
            if line.get("cost_basis") == "外帶售價推導":
                self.assertTrue(line["cost_estimated"], line["key"])
        # 菜單價加總模式不是外燴整案價,不掛這條警語(免得每張外帶單都跳無關的警告)。
        takeout_only = quote_calc.plan_by_items([("蛋沙拉三明治", 1)])
        self.assertFalse(any("Owner msg 5824" in w for w in takeout_only["warnings"]))

    def test_owner_5824_cut_shrimp_add_starch_holds_the_floor_but_barely_moves_it(self):
        """砍蝦棗、多澱粉類照做了,但要誠實報出「幾乎沒動到毛利」這件事。

        蝦棗一件 17,切小三明治一件 16.67,兩者差 2%,所以一件換一件幾乎等值:
        H3 5,922/80.3%/312 件 → H4 5,872/80.4%/310 件。真正的收穫是甲殼類件數砍半與澱粉佔比拉高,
        不是毛利。同時代價要寫死:H4 把更多件數壓在外帶推導成本上(27% → 41%)。
        """
        h3 = quote_calc.run_reference_plan("H3-OWNER")
        h4 = quote_calc.run_reference_plan("H4-OWNER")
        floor = quote_calc.load_price_book()["rules"]["target_margin_floor"]
        self.assertGreaterEqual(h4["margin_rate"], floor)
        self.assertLess(h4["margin_rate"] - h3["margin_rate"], 0.005)
        shrimp = {line["key"]: line for line in h4["lines"]}["梅子醬蝦棗"]
        self.assertEqual(shrimp["units"], 50)
        self.assertGreater(h4["takeout_basis_cost_share"], h3["takeout_basis_cost_share"])

    def test_estimate_for_an_unseen_size_asks_for_the_menu_instead_of_inventing_one(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            executor, "QUOTE_INTAKE_ROOT", Path(tmp) / "intake"
        ), mock.patch.object(executor, "TASK_ROOT", Path(tmp) / "tasks"):
            receipt = executor.execute("人數 37人 預算 18000", 123, chat_id=456)
        output = receipt["output"]
        self.assertIn("選菜不是我的權責", output)
        self.assertNotIn("H1-80", output)


if __name__ == "__main__":
    unittest.main()
