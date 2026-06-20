You are continuing supervised A5/A6 quote training.

Important:
- Your previous rounds failed even though you wrote PASS.
- This round is only PASS if the JSON exactly satisfies the required schema and values.
- Do not write Markdown.
- Do not explain.
- Output exactly one JSON object and nothing else.

Scenario:
- 15-person birthday party
- Event date: 2026-06-20
- Time: 13:00
- Location: 台南市永康區東橋七路392號10樓之一
- Basic version, meal form B / full meal direction
- High margin target 80%+
- Needs English menu later
- Menu shape: one pasta/noodle, one rice, one meatball item, one waffle chicken ball item, remaining desserts and drinks
- Total menu rows: exactly 10
- Urgent case: customer-facing copy must say 50% deposit is required
- Urgent timeline: customer-facing copy must say MAPLAB can provide tabletop/dining-area setup only
- Do not mention backdrop boards or balloons in customer-facing copy.

Required exact menu rows and numbers:
1. 義式經典拿波里肉醬義大利麵 | qty=1 | unit=鍋 | qtyText=1鍋 | unitCost=500 | subtotal=500
2. 鍋炒台南七股虱目魚香腸炒飯 | qty=1 | unit=份 | qtyText=1份 | unitCost=800 | subtotal=800
3. 義大利嫩煎香料豚肉球 | qty=15 | unit=個 | qtyText=15個 | unitCost=15 | subtotal=225
4. 澳式雞球迷你鬆餅 | qty=15 | unit=份 | qtyText=15份 | unitCost=20 | subtotal=300
5. 手工焦糖烤布丁 | qty=15 | unit=份 | qtyText=15份 | unitCost=23 | subtotal=345
6. 卡士達香緹手工小泡芙 | qty=15 | unit=個 | qtyText=15個 | unitCost=20 | subtotal=300
7. 葡式酥皮蛋塔 | qty=15 | unit=個 | qtyText=15個 | unitCost=18 | subtotal=270
8. 布朗尼切小正方/25 | qty=15 | unit=片 | qtyText=15片 | unitCost=16 | subtotal=240
9. 冷泡冰釀烏龍茶_無糖 | qty=1 | unit=桶 | qtyText=1桶 | unitCost=80 | subtotal=80
10. 阿薩姆紅茶 | qty=1 | unit=桶 | qtyText=1桶 | unitCost=80 | subtotal=80

Required exact totals:
- foodCost: 3140
- totalCost: 3140
- foodRevenue: 15700
- totalRevenue: 15700
- foodMargin: 0.8
- overallMargin: 0.8
- depositAmount: 7850

Required JSON schema:
{
  "round": 3,
  "trainee_verdict": "PASS",
  "payload": {
    "action": "createQuoteVariants",
    "base": {
      "clientName": "Page_Telegram報價",
      "eventDate": "2026-06-20",
      "time": "13:00",
      "eventType": "生日派對",
      "location": "台南市永康區東橋七路392號10樓之一",
      "pax": 15,
      "eventName": "基本版高毛利正餐 10 道",
      "depositAmount": 7850
    },
    "variants": [
      {
        "label": "A",
        "title": "基本版高毛利正餐 10 道",
        "totalItems": 10,
        "menu": [
          {"name": "...", "qty": 1, "unit": "...", "qtyText": "...", "unitCost": 0, "subtotal": 0}
        ],
        "foodCost": 3140,
        "totalCost": 3140,
        "foodRevenue": 15700,
        "totalRevenue": 15700,
        "foodMargin": 0.8,
        "overallMargin": 0.8
      }
    ]
  },
  "verification_checklist": [
    "local payload smoke",
    "GAS live createQuoteVariants quote URL",
    "Google Sheets readback 報價單!D2:F31",
    "Google Sheets readback 報價單!I7:J31",
    "Chrome Telegram Web surface proof for bot-facing changes"
  ],
  "customer_safe_reply_zh_hant": "...",
  "self_check": {
    "menu_rows": 10,
    "uses_existing_maplab_item_names": true,
    "payload_shape_is_createQuoteVariants": true,
    "does_not_reveal_cost_or_margin_to_customer": true,
    "customer_reply_mentions_50_percent_deposit": true,
    "customer_reply_mentions_tabletop_or_dining_area_setup_only": true,
    "customer_reply_mentions_backdrop_or_balloons": false
  }
}

Customer-safe reply rules:
- Traditional Chinese only.
- Do not reveal internal cost or margin.
- Say urgent orders require 50% deposit.
- Say under urgent timeline MAPLAB can provide tabletop/dining-area setup only.
- Do not mention backdrop boards or balloons.
