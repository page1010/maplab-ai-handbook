# A6 Quote Sheet-First Repair Validation — 2026-06-18

## Scope

- Target: `maplab_a6_bot` quote path for Telegram A6/A5 requests.
- Problem: quote mode entered local `gemma4:latest` fallback and returned a review bundle instead of a usable Google Sheet quote.
- Fix: route concrete quote messages through deterministic `createQuoteVariants` payload + GAS first; use cloud/local model only as fallback.

## Code Changes

- `bot_a6/a5_quote_engine.py`
  - Added `build_sheet_quote_payload()`.
  - Added high-margin 10-item basic dinner payload from existing `data/items_master.json`.
  - Payload sets `variant.totalItems = 10`, `foodCost = 3140`, `totalRevenue = 15700`, `depositAmount = 7850`.
- `bot_a6/bot_a6.py`
  - Quote mode now tries Sheet-first GAS before cloud/local fallback.
  - `/localquote` stays local-only and does not write Google Sheet.
  - Captioned quote photos route into A5 quote mode instead of only Claude image analysis.
  - GAS failure message no longer claims the master Sheet was written.
- `scripts/apps-script/Code.gs`
  - `applyQuoteVariantToCopy_()` clears `D7:D20`, `F7:F20`, and `I7:J20` in the quote copy to prevent stale gift rows.

## Deployment

- `rtk clasp push -f`
  - Pushed 8 Apps Script files.
- `rtk clasp deploy -i AKfycbwUZ0JDyCYd8aucbOvwX0Oworjz11Iizy0QUx-1Go4pkxccb2Q6IYvTbaG34GVUNBdF -d "fix(A6): quote variants clear stale rows"`
  - Existing A6 `GAS_QUOTE_URL` deployment updated to `@12`.

## Verification

### Local

- `py_compile ok`
- `git diff --check` passed.
- Payload smoke:
  - `action`: `createQuoteVariants`
  - menu items: `10`
  - `variant.totalItems`: `10`
  - `foodCost`: `3140`
  - `totalRevenue`: `15700`
  - `depositAmount`: `7850`

### Live GAS v3

- Test quote URL: https://docs.google.com/spreadsheets/d/1dF0fy1ZB6NZTuSjj3FLF3IDoc87qnBKs4lqrJtjFrf4/edit
- File title: `20260620_A6接線測試_20260618_v3_A`
- Visible tabs:
  - `報價單`
  - hidden `Items`

Readback from `報價單!D2:F31`:

- Client: `A6接線測試_20260618_v3`
- Date: `2026/06/20`
- Headcount: `15`
- Event name: `基本版高毛利正餐 10 道`
- Total item count: `10`
- Total revenue: `$15,700`
- Rows D17:D20 are blank; stale gift rows removed.

Readback from `報價單!I7:J31`:

- Item costs:
  - `$500 / $500`
  - `$800 / $800`
  - `$15 / $225`
  - `$20 / $300`
  - `$23 / $345`
  - `$20 / $300`
  - `$18 / $270`
  - `$16 / $240`
  - `$80 / $80`
  - `$80 / $80`
- Order cost: `$3,140`
- Margin: `80.0%`

## Remaining Limit

- Pure photo OCR still depends on the Claude image path. A local Ollama vision smoke against the saved Telegram image returned no usable OCR text, so this repair only makes text/caption quote requests Sheet-first.
- A6 launchd was kickstarted after code changes; `bot_a6/launchd_stdout.log` shows `A6 Bot running` at `2026-06-18 11:18:56`.
