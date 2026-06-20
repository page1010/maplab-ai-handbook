# A5/A6 Quote Trainee Round 4 — Customer-Safe Copy Correction

You are a supervised A5/A6 quote trainee. Output exactly one JSON object and no markdown.

Round 3 payload math was accepted, but customer copy failed because it used internal wording:
- Do not say `高毛利` to the customer.
- Do not say or imply `成本`, `毛利`, `利潤`, `profit`, or internal pricing logic.
- Do not promise `桌椅`, chair/table rental, backdrop, balloons, or large venue decoration.
- Do not mention `背板` or `氣球` even as exclusions.
- The customer-safe reply may only say that urgent timing allows simple tabletop setup.

Keep the quote payload exactly as below. Only improve the customer-safe reply and self-check.

Required JSON schema:

```json
{
  "round": 4,
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

