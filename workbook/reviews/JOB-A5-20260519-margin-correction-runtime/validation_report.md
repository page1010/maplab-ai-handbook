# JOB-A5-20260519 Margin Correction Runtime

## Correction

Owner clarified that A5 should judge quote pricing by **餐點毛利 / 食材成本佔比** first, not only by whole-order margin.

Rule going forward:

- Food cost ratio = `foodCost / foodRevenue`
- Food margin = `(foodRevenue - foodCost) / foodRevenue`
- A5 target: food cost ratio should be <= 20%, food margin should be >= 80%
- Whole-order margin is still useful, but must be shown separately.

## Current Jianshanpi Quote Recheck

| Variant | Food Revenue | Food Cost | Food Cost Ratio | Food Margin | Whole-Order Margin | Result |
|---|---:|---:|---:|---:|---:|---|
| A 小點補給版 初版 | 60,000 | 14,300 | 23.8% | 76.2% | 53.9% | Below food-margin target |
| A 建議修正版 | 72,000 | 14,300 | 19.9% | 80.1% | 57.3% | Meets food-margin target |
| B 精緻特色小點版 | 100,000 | 28,500 | 28.5% | 71.5% | 57.6% | Requires menu/cost revision or food-price increase |
| C 正餐派對版 | 160,000 | 45,400 | 28.4% | 71.6% | 60.2% | Requires menu/cost revision or food-price increase |

Customer-facing recommendation:

- A should be discussed as `$360/person` food instead of `$300/person` if the current menu richness is kept.
- If customer insists on `$300/person`, A menu must be simplified.
- Do not mention margin/cost to customer.

## A6 / Local Interface Test

Observed from runtime bundle:

- `workbook/reviews/A5-QUOTE-20260519-122342/`
- Trigger phrase: `毛利都太低了 第一版報價稍微調整一下調高一點才有空間`
- Local route used `ollama llama3.1:latest`.
- The result reused stale test context (`6人 / 預算6000 / 台南`) and did not perform a meaningful quote adjustment.

Diagnosis:

- The local fallback route can generate text bundles, but it does not write Google Sheet outputs.
- Ambiguous follow-ups such as `第一版` are unsafe when the Telegram conversation history does not contain the current quote context.
- This matches Owner's observation that the local interface appeared to be connected but not operationally useful enough.

## Code Fix

- `scripts/apps-script/Code.gs`
  - `createQuoteVariants_()` now returns `foodRevenue`, `foodCost`, `foodCostRatio`, and `foodMargin` metadata for each quote.
- `bot_a6/bot_a6.py`
  - A6 multi-quote formatter now displays food margin, food cost ratio, and whole-order margin separately when metadata is available.
- `bot_a6/a5_quote_engine.py`
  - Local A5 prompt now explicitly says pricing must split food margin / food cost ratio from whole-order margin.
  - Local A5 prompt now warns not to reuse stale test cases for vague follow-ups such as `第一版` / `毛利太低`.

## Deployment / Runtime

- `node --check --input-type=commonjs < scripts/apps-script/Code.gs`: passed
- `python3 -m py_compile bot_a6/bot_a6.py bot_a6/a5_quote_engine.py`: passed
- A6 formatter sample test: passed
- A5 local prompt contract check: passed
- `clasp push`: success
- Apps Script version 11: `fix(A5): expose food margin separately 2026-05-19`
- Web App deployment updated in place:
  - `AKfycbwUZ0JDyCYd8aucbOvwX0Oworjz11Iizy0QUx-1Go4pkxccb2Q6IYvTbaG34GVUNBdF @11`
- A6 LaunchAgent restarted:
  - `launchctl kickstart -k gui/501/com.maplab.a6bot`
  - `launchctl list`: `com.maplab.a6bot` running

## Telegram Delivery

Sent two corrected messages to Owner and Mina:

1. Internal margin correction and menu explanation.
2. Customer-facing reply suggestion.

| Recipient | Chat ID | Message | Telegram API Result |
|---|---:|---|---|
| Owner | `1077768811` | internal correction | `ok: true`, message_id `333` |
| Owner | `1077768811` | customer reply draft | `ok: true`, message_id `334` |
| Mina / SALES_USER_ID | `8560189814` | internal correction | `ok: true`, message_id `335` |
| Mina / SALES_USER_ID | `8560189814` | customer reply draft | `ok: true`, message_id `336` |

## Resume Prompt

我是 MAPLAB A5 報價與提案引擎部。請先讀 `CURRENT_STATUS.md`、`AGENT_RULES.md`、`pitfalls.md`、`workbook/reviews/JOB-A5-20260519-margin-correction-runtime/validation_report.md`。Owner 已修正 A5 pricing 口徑：優先看餐點毛利與食材成本佔比，食材成本應 <= 餐點收入 20%；整體毛利要分開列。已修補 GAS `createQuoteVariants_()` 回傳 food margin metadata，A6 Telegram formatter 會分開顯示餐點毛利/食材占比/整體毛利；本地 A5 prompt 也已加入不要把 vague follow-up 接到舊測試案的規則。尖山埤案目前 A 初版不達標，建議 A 改報 160,000 起；B/C 要再精修菜單或調餐點報價。不要改 master Sheet 表格、公式或 Items。
