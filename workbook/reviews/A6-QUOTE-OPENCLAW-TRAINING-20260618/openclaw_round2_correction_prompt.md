Codex supervisor correction for your round 1 output:

Your self-verdict PASS was wrong. Round 1 is NEEDS_CORRECTION.

Failures:
1. You produced only 6 menu item rows, but the requirement is exactly 10.
2. You invented or generalized item names: 意大利面, 白饭, 肉丸, 薯條雞球, 蛋糕, 果汁.
3. You did not use the MAPLAB existing item names from validation_report.md.
4. Your JSON used `items`; the GAS adapter expects `variants[].menu`.
5. Your base object omitted required event/client fields.
6. Your customer-safe draft mixed Simplified Chinese and English and did not sound like MAPLAB.

Correct MAPLAB menu from validation_report.md:
1. 義式經典拿波里肉醬義大利麵 — 1鍋
2. 鍋炒台南七股虱目魚香腸炒飯 — 1份
3. 義大利嫩煎香料豚肉球 — 15個
4. 澳式雞球迷你鬆餅 — 15份
5. 手工焦糖烤布丁 — 15份
6. 卡士達香緹手工小泡芙 — 15個
7. 葡式酥皮蛋塔 — 15個
8. 布朗尼切小正方/25 — 15片
9. 冷泡冰釀烏龍茶_無糖 — 1桶
10. 阿薩姆紅茶 — 1桶

Correct internal numbers:
- totalRevenue: 15700
- totalCost / foodCost: 3140
- margin: 80.0%
- urgent deposit 50%: 7850

Your task:
Redo the output, now as a corrected trainee answer. Include:
1. `Round 1 verdict: NEEDS_CORRECTION`
2. `Corrected trainee verdict: PASS` only if the corrected output has exactly 10 existing MAPLAB items and the verification checklist is exact.
3. Correct workflow explanation:
   - HTML form is human UI, not enough for agent because it only posts basic formData and does not accept full menu/cost/margin payload.
   - Complete workbook copy is used because single sheet copy breaks Items/VLOOKUP and direct master writes have damaged formulas before.
   - createQuoteVariants first creates the safe copy, then writes only generated quote copy ranges.
4. Correct payload summary using `variants[].menu`, with the 10 items above.
5. Customer-safe reply in polished Traditional Chinese, not revealing cost/margin, saying urgent case requires 50% deposit, and tabletop/dining-area setup only.

Do not ask for GAS commands. This is still a supervised training output, not execution.
