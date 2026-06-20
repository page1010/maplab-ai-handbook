# A5/A6 Quote Trainee Round 5 — Fixed Customer Template

Output exactly one JSON object and no markdown.

This is a copy-and-structure test. Do not rewrite the customer reply. Copy the `customer_safe_reply_zh_hant` value byte-for-byte from the required JSON below.

Hard fail conditions:
- If the reply changes `預收 50% 訂金` to any weaker wording, fail.
- If the reply contains `高毛利`, `成本`, `毛利`, `利潤`, `profit`, fail.
- If the reply contains `桌椅`, `椅`, `背板`, `氣球`, fail.
- If the payload shape is not `action=createQuoteVariants` with `variants[0].menu`, fail.
- If there are not exactly 10 menu rows, fail.

Required JSON:

```json
{
  "round": 5,
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
      "eventName": "基本版正餐 10 道",
      "depositAmount": 7850
    },
    "variants": [
      {
        "label": "A",
        "title": "基本版正餐 10 道",
        "totalItems": 10,
        "menu": [
          {"name": "義式經典拿波里肉醬義大利麵", "qty": 1, "unit": "鍋", "qtyText": "1鍋", "unitCost": 500, "subtotal": 500},
          {"name": "鍋炒台南七股虱目魚香腸炒飯", "qty": 1, "unit": "份", "qtyText": "1份", "unitCost": 800, "subtotal": 800},
          {"name": "義大利嫩煎香料豚肉球", "qty": 15, "unit": "個", "qtyText": "15個", "unitCost": 15, "subtotal": 225},
          {"name": "澳式雞球迷你鬆餅", "qty": 15, "unit": "份", "qtyText": "15份", "unitCost": 20, "subtotal": 300},
          {"name": "手工焦糖烤布丁", "qty": 15, "unit": "份", "qtyText": "15份", "unitCost": 23, "subtotal": 345},
          {"name": "卡士達香緹手工小泡芙", "qty": 15, "unit": "個", "qtyText": "15個", "unitCost": 20, "subtotal": 300},
          {"name": "葡式酥皮蛋塔", "qty": 15, "unit": "個", "qtyText": "15個", "unitCost": 18, "subtotal": 270},
          {"name": "布朗尼切小正方/25", "qty": 15, "unit": "片", "qtyText": "15片", "unitCost": 16, "subtotal": 240},
          {"name": "冷泡冰釀烏龍茶_無糖", "qty": 1, "unit": "桶", "qtyText": "1桶", "unitCost": 80, "subtotal": 80},
          {"name": "阿薩姆紅茶", "qty": 1, "unit": "桶", "qtyText": "1桶", "unitCost": 80, "subtotal": 80}
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
  "customer_safe_reply_zh_hant": "您好，這邊先依 6/20 生日派對、15 位、正餐 B 方向整理一版基本方案；餐點會以一款麵食、一款飯食、肉丸、澳式雞球迷你鬆餅，再搭配甜點與飲品，合計 10 道。因為這是急件，我們會先保留準備人力與食材檔期；確認後需先預收 50% 訂金。英文版菜單可以一併整理給您。急件時程下，現場佈置會以桌面上的簡潔擺設為主。",
  "self_check": {
    "menu_rows": 10,
    "payload_shape_is_createQuoteVariants": true,
    "uses_exact_existing_maplab_item_names": true,
    "foodCost": 3140,
    "totalRevenue": 15700,
    "overallMargin": 0.8,
    "depositAmount": 7850,
    "customer_reply_mentions_50_percent_deposit": true,
    "customer_reply_mentions_english_menu_available": true,
    "customer_reply_mentions_tabletop_setup_only": true,
    "customer_reply_mentions_internal_margin_or_cost": false,
    "customer_reply_mentions_backdrop_or_balloons": false,
    "customer_reply_mentions_chairs_or_large_decoration": false
  }
}
```

