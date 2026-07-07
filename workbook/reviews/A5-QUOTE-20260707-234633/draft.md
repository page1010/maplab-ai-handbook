## A5 報價草稿
地端模型未輸出可直接建 Sheet 的合法 JSON，已改用 MAPLAB 品項表與成本規則產出結構化試算。

### 建議雷同品項
- 義式經典拿波里肉醬義大利麵：1鍋，成本 NT$500
- 鍋炒台南七股虱目魚香腸炒飯：1份，成本 NT$800
- 義大利嫩煎香料豚肉球：15個，成本 NT$225
- 澳式雞球迷你鬆餅：15份，成本 NT$300
- 手工焦糖烤布丁：15份，成本 NT$345
- 卡士達香緹手工小泡芙：15個，成本 NT$300
- 葡式酥皮蛋塔：15個，成本 NT$270
- 布朗尼切小正方/25：15片，成本 NT$240
- 冷泡冰釀烏龍茶_無糖：1桶，成本 NT$80
- 阿薩姆紅茶：1桶，成本 NT$80

### 金額判斷
- 食材/餐點成本小計：NT$3,140
- 成本乘以 5 報價：NT$15,700
- 對應食材成本佔比：約 20%；餐點毛利：約 80%。

### 待人工確認
- 無

```json
{
  "action": "createQuoteVariants",
  "base": {
    "clientName": "Telegram報價試算",
    "customer": "Telegram報價試算",
    "eventDate": "2026-07-07",
    "date": "2026-07-07",
    "time": "",
    "eventType": "外燴正餐",
    "eventName": "15人外燴正餐高毛利正餐",
    "headcount": 15,
    "pax": 15,
    "totalItems": 10,
    "depositAmount": 7850,
    "dietaryNotes": "A6 deterministic Sheet-first payload；品項皆取自 Items standard_name。｜含甜點與飲品共 10 道。｜未提供活動日期，eventDate 暫填試算日而非正式活動日｜可能需英文版；急件確認後需 50% 訂金。"
  },
  "variants": [
    {
      "label": "A",
      "title": "基本版高毛利正餐 10 道",
      "totalItems": 10,
      "positioning": "15 人左右正餐桌面餐檯，高毛利基本版。",
      "menu": [
        {
          "sourceItem": "一麵",
          "itemId": "MAIN004",
          "name": "義式經典拿波里肉醬義大利麵",
          "qty": 1,
          "unit": "份",
          "qtyText": "1鍋",
          "unitCost": 500.0,
          "subtotal": 500.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "一飯",
          "itemId": "MAIN009",
          "name": "鍋炒台南七股虱目魚香腸炒飯",
          "qty": 1,
          "unit": "份",
          "qtyText": "1份",
          "unitCost": 800.0,
          "subtotal": 800.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "肉丸",
          "itemId": "APP007",
          "name": "義大利嫩煎香料豚肉球",
          "qty": 15,
          "unit": "個",
          "qtyText": "15個",
          "unitCost": 15.0,
          "subtotal": 225.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "鬆餅雞球",
          "itemId": "APP046",
          "name": "澳式雞球迷你鬆餅",
          "qty": 15,
          "unit": "份",
          "qtyText": "15份",
          "unitCost": 20.0,
          "subtotal": 300.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "甜點",
          "itemId": "DST012",
          "name": "手工焦糖烤布丁",
          "qty": 15,
          "unit": "份",
          "qtyText": "15份",
          "unitCost": 23.0,
          "subtotal": 345.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "甜點",
          "itemId": "DST017",
          "name": "卡士達香緹手工小泡芙",
          "qty": 15,
          "unit": "個",
          "qtyText": "15個",
          "unitCost": 20.0,
          "subtotal": 300.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "甜點",
          "itemId": "DST008",
          "name": "葡式酥皮蛋塔",
          "qty": 15,
          "unit": "個",
          "qtyText": "15個",
          "unitCost": 18.0,
          "subtotal": 270.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "甜點",
          "itemId": "DST013",
          "name": "布朗尼切小正方/25",
          "qty": 15,
          "unit": "片",
          "qtyText": "15片",
          "unitCost": 16.0,
          "subtotal": 240.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "飲品",
          "itemId": "BEV005",
          "name": "冷泡冰釀烏龍茶_無糖",
          "qty": 1,
          "unit": "桶",
          "qtyText": "1桶",
          "unitCost": 80.0,
          "subtotal": 80.0,
          "matchNote": "A6 deterministic basic set"
        },
        {
          "sourceItem": "飲品",
          "itemId": "BEV007",
          "name": "阿薩姆紅茶",
          "qty": 1,
          "unit": "桶",
          "qtyText": "1桶",
          "unitCost": 80.0,
          "subtotal": 80.0,
          "matchNote": "A6 deterministic basic set"
        }
      ],
      "foodCost": 3140.0,
      "foodRevenue": 15700,
      "totalCost": 3140.0,
      "totalRevenue": 15700,
      "foodNote": "totalRevenue 依 foodCost * 5 後百元進位；食材成本佔比約 20%。",
      "decorNote": "桌面餐檯佈置。",
      "internalNote": "A6 deterministic Sheet-first payload；品項皆取自 Items standard_name。；含甜點與飲品共 10 道。；未提供活動日期，eventDate 暫填試算日而非正式活動日；可能需英文版；急件確認後需 50% 訂金。"
    }
  ],
  "needsManualCost": []
}
```
