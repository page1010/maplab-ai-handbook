# A6/A5 Quote Sheet-First Training — Supervisor Lesson

Date: 2026-06-18
Supervisor: Codex
Trainee runtime: OpenClaw `agent:main:a6-quote-openclaw-training-20260618`

## Verdict

OpenClaw is not certified to independently generate A5/A6 quote payloads yet.

Reason: it can repeat broad concepts after correction, but it still self-marks `PASS` while producing invalid payload shape, invented quantities/prices, mixed language, incomplete validation details, or fake tool-call style output.

## Why OpenClaw Was Chosen

- OpenClaw is better than Hermes for this task because the task is a supervised execution/training loop with a persistent agent session.
- Hermes is more suitable for memory/patrol/reaction-card style work in the current MAPLAB setup.
- OpenClaw status was healthy and gateway-backed, so it was the correct candidate to train first.

## Round Results

### Round 1

Trainee self-verdict: `PASS`

Supervisor verdict: `NEEDS_CORRECTION`

Failures:
- Only 6 menu rows, not 10.
- Invented/generic items: `意大利面`, `白饭`, `肉丸`, `薯條雞球`, `蛋糕`, `果汁`.
- Did not use MAPLAB existing item names from the validated Sheet.
- Used `items`, but GAS adapter expects `variants[].menu`.
- Base object omitted event/client fields.
- Customer-safe copy mixed Simplified Chinese and English.

### Round 2

Trainee self-verdict: `PASS`

Supervisor verdict: `NEEDS_CORRECTION`

Failures:
- `variants` was a list of item objects instead of a variant object containing `menu`.
- Missing `action`, `base`, `totalRevenue`, `foodCost`, `totalCost`, `overallMargin`, and `depositAmount`.
- Invented prices and changed quantities.
- Did not include the exact readback/checklist gate.
- Copy still mixed Simplified Chinese and Japanese glyphs (`団隊`).

### Round 3

Trainee runtime: OpenClaw main

Supervisor verdict: `FAIL`

Failure:
- Returned a fake tool-call style object (`id=createQuoteVariants`) instead of the required JSON payload.

### Hermes Smoke

Supervisor verdict: `FAIL`

Failures:
- `hermes -m qwen2.5:14b` was blocked by Hermes context requirements.
- Hermes default `gemma4:latest` smoke returned corrupted text, so it is not certified for quote trainee work.

### Local Ollama qwen2.5:14b

Round 3 supervisor verdict: `FAIL`
- Payload math was correct, but customer copy leaked internal wording (`高毛利`) and overpromised `桌椅`.

Round 4 supervisor verdict: `FAIL`
- Fixed internal wording but weakened `預收 50% 訂金` into `一定比例的訂金`.

Round 5 supervisor verdict: `PASS_WITH_GATE`
- Direct Ollama `qwen2.5:14b` passed with strict JSON, `temperature=0`, fixed customer template, and supervisor validation.
- This does not make model-only quote completion acceptable. Sheet creation and readback are still required for real A5/A6 completion.

## Correct Success Pattern

The subordinate must learn this exact pattern:

1. A5/A6 quote completion is Sheet-first. Chat math is never completion.
2. The old HTML form is human UI. It posts basic `formData` only and does not accept a full menu/cost/margin payload.
3. Complete workbook copy exists for safety: single-sheet copy breaks `Items` / `VLOOKUP`, and direct writes to master `QUOTE_DRAFT` previously damaged formulas.
4. `createQuoteVariants` first creates a safe copy, then writes only the generated quote copy.
5. The answer is not valid until the generated Google Sheet is read back from:
   - `報價單!D2:F31`
   - `報價單!I7:J31`
6. Bot-facing changes need Chrome Telegram Web proof.
7. Trainee must not self-mark `PASS` unless the payload shape, item count, exact item names, totals, and verification checklist all match.

## Correct Payload Shape

```json
{
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
}
```

## Customer-Safe Copy Pattern

```text
您好，這邊先依 6/20 生日派對、15 位、正餐 B 方向整理一版基本方案。

餐點會以一款麵食、一款飯食、肉丸、澳式雞球迷你鬆餅，再搭配甜點與飲品組合，合計 10 道，適合桌面餐檯分享。

因為這是急件，我們會先保留準備人力與食材檔期；確認後需先預收 50% 訂金。英文版菜單可以一併整理給您。

另外急件時程下，我們能提供餐檯桌面與用餐區的簡潔佈置，不含大型背板或氣球類裝置。
```

## Training Gate For Next OpenClaw Attempt

OpenClaw can be considered trained only after it produces all of these without supervisor correction:

- `action=createQuoteVariants`.
- Exactly one variant object with `menu` array.
- Exactly 10 `menu` rows.
- Exact validated MAPLAB item names.
- No invented prices; use the validated unit costs/subtotals or omit customer prices.
- `foodCost=3140`, `totalRevenue=15700`, `overallMargin=0.8`, `depositAmount=7850`.
- Verification checklist includes local payload smoke, GAS live URL, Google Sheets readback ranges, and Telegram Web proof for bot-facing changes.
- Customer copy is Traditional Chinese, does not reveal cost/margin, and says urgent jobs require 50% deposit plus tabletop/dining-area setup only.

## Certified Trainee Path As Of 2026-06-20

Use this path only as a supervised payload/copy generator:

1. Runtime: direct local Ollama `qwen2.5:14b`.
2. Options: `temperature=0` when customer copy is involved.
3. Prompt shape: strict JSON with exact expected menu rows and fixed customer-safe template.
4. Supervisor gate: deterministic validation against payload shape, item names, totals, forbidden customer words, and exact `預收 50% 訂金`.
5. Completion gate: GAS `createQuoteVariants` creates the Sheet copy, then supervisor reads back `報價單!D2:F31` and `報價單!I7:J31`.

Do not certify OpenClaw or Hermes for this path until they pass the same Round 5-style gate without correction.
