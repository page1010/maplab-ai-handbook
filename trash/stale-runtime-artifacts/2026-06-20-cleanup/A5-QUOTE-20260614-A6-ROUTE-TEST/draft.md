## A5 報價草稿
地端模型未輸出可直接建 Sheet 的合法 JSON，已改用 MAPLAB 品項表與成本規則產出結構化試算。

### 建議雷同品項
- 義式BBQ燻煙手撕豬普切塔：20個，成本 NT$700
- 義式羅勒青醬雞肉乳酪三明治：20個，成本 NT$400
- 日式醬蛋沙拉小漢堡：20個，成本 NT$600
- 法式燻燻鵝胸葡萄小串：20個，成本 NT$800
- 招牌義式炸雞腿：1盤，成本 NT$800
- 義式蒜香白酒蛤蠣義大利麵：1盤，成本 NT$500
- 法式玫瑰覆盆子小塔：12個，成本 NT$420
- 馬卡龍派對3：12個，成本 NT$360
- 卡士達香緹手工小泡芙：12個，成本 NT$240
- 法式焦糖烤布丁：12個，成本 NT$540
- 檸檬紅茶：4公升，成本 NT$80
- 阿薩姆紅茶：4公升，成本 NT$80

### 金額判斷
- 食材/餐點成本小計：NT$5,520
- 成本乘以 5 報價：NT$27,600
- 對應食材成本佔比：約 20%；餐點毛利：約 80%。

### 待人工確認
- 甜甜圈蛋糕：items_master 內甜甜圈架成本為 0，不能自動報價。
- 烤蔬菜盤：目前以雞腿主盤估算，蔬菜盤成本需人工補價。

```json
{
  "action": "createQuoteVariants",
  "base": {
    "clientName": "競品菜單試算",
    "eventName": "MAPLAB 雷同品項成本乘以5試算",
    "dietaryNotes": "競品菜單 OCR 轉換；正式報價前需人工確認成本未知品項。"
  },
  "variants": [
    {
      "label": "A",
      "title": "MAPLAB 雷同品項成本乘以5試算",
      "positioning": "比照競品菜單，以 MAPLAB 近似品項估算。",
      "menu": [
        {
          "sourceItem": "BBQ手撕豬小漢堡",
          "itemId": "APP014",
          "name": "義式BBQ燻煙手撕豬普切塔",
          "qty": 20.0,
          "unit": "個",
          "qtyText": "20個",
          "unitCost": 35.0,
          "subtotal": 700.0,
          "matchNote": "以手撕豬普切塔替代迷你漢堡型態。"
        },
        {
          "sourceItem": "洋蔥燻雞三明治",
          "itemId": "APP011",
          "name": "義式羅勒青醬雞肉乳酪三明治",
          "qty": 20.0,
          "unit": "個",
          "qtyText": "20個",
          "unitCost": 20.0,
          "subtotal": 400.0,
          "matchNote": "以青醬雞肉乳酪三明治替代燻雞三明治。"
        },
        {
          "sourceItem": "蛋沙拉小可頌",
          "itemId": "APP030",
          "name": "日式醬蛋沙拉小漢堡",
          "qty": 20.0,
          "unit": "個",
          "qtyText": "20個",
          "unitCost": 30.0,
          "subtotal": 600.0,
          "matchNote": "以日式蛋沙拉小漢堡替代蛋沙拉可頌。"
        },
        {
          "sourceItem": "櫻桃鴨胸串",
          "itemId": "APP003",
          "name": "法式燻燻鵝胸葡萄小串",
          "qty": 20.0,
          "unit": "個",
          "qtyText": "20個",
          "unitCost": 40.0,
          "subtotal": 800.0,
          "matchNote": "以燻鵝胸葡萄小串替代鴨胸串。"
        },
        {
          "sourceItem": "烤雞腿排與烤蔬菜盤",
          "itemId": "MAIN007",
          "name": "招牌義式炸雞腿",
          "qty": 1.0,
          "unit": "盤",
          "qtyText": "1盤",
          "unitCost": 800.0,
          "subtotal": 800.0,
          "matchNote": "以招牌義式炸雞腿估算雞腿主盤成本，烤蔬菜需人工確認。"
        },
        {
          "sourceItem": "義大利麵",
          "itemId": "MAIN005",
          "name": "義式蒜香白酒蛤蠣義大利麵",
          "qty": 1.0,
          "unit": "盤",
          "qtyText": "1盤",
          "unitCost": 500.0,
          "subtotal": 500.0,
          "matchNote": "以蒜香白酒蛤蠣義大利麵作為義大利麵基準盤。"
        },
        {
          "sourceItem": "水果迷你小塔",
          "itemId": "DST021",
          "name": "法式玫瑰覆盆子小塔",
          "qty": 12.0,
          "unit": "個",
          "qtyText": "12個",
          "unitCost": 35.0,
          "subtotal": 420.0,
          "matchNote": "以覆盆子小塔估算水果迷你小塔。"
        },
        {
          "sourceItem": "季節水果馬卡龍",
          "itemId": "DST039",
          "name": "馬卡龍派對3",
          "qty": 12.0,
          "unit": "個",
          "qtyText": "12個",
          "unitCost": 30.0,
          "subtotal": 360.0,
          "matchNote": "以馬卡龍派對品項換算單顆成本。"
        },
        {
          "sourceItem": "卡士達迷你泡芙",
          "itemId": "DST017",
          "name": "卡士達香緹手工小泡芙",
          "qty": 12.0,
          "unit": "個",
          "qtyText": "12個",
          "unitCost": 20.0,
          "subtotal": 240.0,
          "matchNote": "以卡士達香緹手工小泡芙估算。"
        },
        {
          "sourceItem": "水果焦糖布丁",
          "itemId": "DST011",
          "name": "法式焦糖烤布丁",
          "qty": 12.0,
          "unit": "個",
          "qtyText": "12個",
          "unitCost": 45.0,
          "subtotal": 540.0,
          "matchNote": "以法式焦糖烤布丁估算，水果裝飾需確認。"
        },
        {
          "sourceItem": "蜂蜜檸檬飲",
          "itemId": "BEV006",
          "name": "檸檬紅茶",
          "qty": 1.0,
          "unit": "桶",
          "qtyText": "4公升",
          "unitCost": 80.0,
          "subtotal": 80.0,
          "matchNote": "以檸檬紅茶桶裝成本暫估蜂蜜檸檬飲。"
        },
        {
          "sourceItem": "英式伯爵茶",
          "itemId": "BEV007",
          "name": "阿薩姆紅茶",
          "qty": 1.0,
          "unit": "桶",
          "qtyText": "4公升",
          "unitCost": 80.0,
          "subtotal": 80.0,
          "matchNote": "以阿薩姆紅茶桶裝成本暫估伯爵茶。"
        }
      ],
      "foodCost": 5520.0,
      "foodRevenue": 27600.0,
      "totalCost": 5520.0,
      "totalRevenue": 27600.0,
      "foodNote": "foodRevenue = foodCost * 5；食材成本佔比約 20%。",
      "internalNote": "BBQ手撕豬小漢堡->義式BBQ燻煙手撕豬普切塔：以手撕豬普切塔替代迷你漢堡型態。；洋蔥燻雞三明治->義式羅勒青醬雞肉乳酪三明治：以青醬雞肉乳酪三明治替代燻雞三明治。；蛋沙拉小可頌->日式醬蛋沙拉小漢堡：以日式蛋沙拉小漢堡替代蛋沙拉可頌。；櫻桃鴨胸串->法式燻燻鵝胸葡萄小串：以燻鵝胸葡萄小串替代鴨胸串。；烤雞腿排與烤蔬菜盤->招牌義式炸雞腿：以招牌義式炸雞腿估算雞腿主盤成本，烤蔬菜需人工確認。；義大利麵->義式蒜香白酒蛤蠣義大利麵：以蒜香白酒蛤蠣義大利麵作為義大利麵基準盤。；水果迷你小塔->法式玫瑰覆盆子小塔：以覆盆子小塔估算水果迷你小塔。；季節水果馬卡龍->馬卡龍派對3：以馬卡龍派對品項換算單顆成本。；卡士達迷你泡芙->卡士達香緹手工小泡芙：以卡士達香緹手工小泡芙估算。；水果焦糖布丁->法式焦糖烤布丁：以法式焦糖烤布丁估算，水果裝飾需確認。；蜂蜜檸檬飲->檸檬紅茶：以檸檬紅茶桶裝成本暫估蜂蜜檸檬飲。；英式伯爵茶->阿薩姆紅茶：以阿薩姆紅茶桶裝成本暫估伯爵茶。；items_master 內甜甜圈架成本為 0，不能自動報價。；目前以雞腿主盤估算，蔬菜盤成本需人工補價。"
    }
  ],
  "needsManualCost": [
    {
      "sourceItem": "甜甜圈蛋糕",
      "reason": "items_master 內甜甜圈架成本為 0，不能自動報價。"
    },
    {
      "sourceItem": "烤蔬菜盤",
      "reason": "目前以雞腿主盤估算，蔬菜盤成本需人工補價。"
    }
  ]
}
```
