# JOB-A5-20260519 Quote Variants Runtime Validation

## Identity

- Role: A5 報價與提案引擎部
- Environment: `/Users/pagemacmini/maplab-ai-handbook`
- Task: 原本 Sheet/GAS 報價接口接上 A/B/C 三版報價副本產出，A6 Telegram 雙對話接口可收到連結

## Scope

- Changed code/interface layer only.
- Did not edit master `QUOTE_DRAFT` layout, formulas, Items, or live table schema.
- Generated quote files are independent spreadsheet copies under the existing `createQuote()` Drive flow.

## Code Changes

- `scripts/apps-script/ApiEndpoint.gs`
  - Added `action: "createQuoteVariants"`.
- `scripts/apps-script/Code.gs`
  - Added `createQuoteVariants_()`.
  - Reused existing `createQuote()` copy generator.
  - Filled A/B/C menu, extra services, total quote, total cost, and margin into generated copies only.
  - Added `spreadsheetId` to quote responses for downstream verification/routing.
- `bot_a6/bot_a6.py`
  - Added multi-variant GAS response formatter so A6 can show three quote links instead of assuming one `url`.
  - Kept the existing owner + `SALES_USER_ID` whitelist flow.

## Deployment

- `clasp push`: success
- Apps Script version 9: `feat(A5): createQuoteVariants adapter 2026-05-19`
- Apps Script version 10: `fix(A5): clear generated quote fee internals 2026-05-19`
- Web App deployment updated in place:
  - `AKfycbwUZ0JDyCYd8aucbOvwX0Oworjz11Iizy0QUx-1Go4pkxccb2Q6IYvTbaG34GVUNBdF @10`
  - A6 `GAS_QUOTE_URL` was unchanged.

## Runtime Output

Generated at: `2026-05-19 08:31:07 Asia/Taipei`

| Variant | Case ID | Total | Margin | Sheet |
|---|---|---:|---:|---|
| A 小點補給版 | `Q20260519083013` | NT$148,000 | 53.9% | https://docs.google.com/spreadsheets/d/15Qq7eE_iZc7Cn_IhhkVkhM39FIZrAOjCC5RmBvG4lDg/edit |
| B 精緻特色小點版 | `Q20260519083030` | NT$212,000 | 57.6% | https://docs.google.com/spreadsheets/d/1wlDTcYKiTjz7943CU_f-OZrT0-pUshoM74M8zEN3QIA/edit |
| C 正餐派對版 | `Q20260519083049` | NT$300,000 | 60.2% | https://docs.google.com/spreadsheets/d/1M1Fbj3jyWzvTsJ0jamWihU7xI3f3EqWVkqhQZXwkZM0/edit |

## Telegram Delivery

Sent through A6 bot token with the existing two-person interface.

| Recipient | Chat ID | Telegram API Result |
|---|---:|---|
| Owner | `1077768811` | `ok: true`, message_id `327` |
| Mina / SALES_USER_ID | `8560189814` | `ok: true`, message_id `328` |

## Verification

- `node --check --input-type=commonjs < scripts/apps-script/Code.gs`: passed
- `node --check --input-type=commonjs < scripts/apps-script/ApiEndpoint.gs`: passed
- `python3 -m py_compile bot_a6/bot_a6.py`: passed
- `_format_gas_quote_result()` sample test: passed
- GAS `createQuoteVariants` live POST to deployed `/exec`: success, returned 3 quote URLs
- A6 LaunchAgent restarted via `launchctl kickstart -k gui/501/com.maplab.a6bot`
- `launchctl list`: `com.maplab.a6bot` running after restart

## Notes

- The first v9 live run produced valid quote links, but readback showed generated-copy internal fee rows still had template G/H leftovers. v10 fixed that by clearing `C22:H28` before writing fee rows; the final Telegram links use v10 output.
- Google Sheets connector readback hit `RATE_LIMITED` after the v10 run. The v9 readback already verified the adapter wrote the expected fee/total/margin cells; v10 changed only the generated-copy clear range before writing the same values.

## Resume Prompt

我是 MAPLAB A5 報價與提案引擎部。請先讀 `CURRENT_STATUS.md`、`AGENT_RULES.md`、`pitfalls.md`、`workbook/reviews/JOB-A5-20260519-quote-variants-runtime/validation_report.md`。本輪已在 `scripts/apps-script/ApiEndpoint.gs` / `Code.gs` 新增 `createQuoteVariants`，並把原 A6 Web App deployment 更新到 Apps Script version 10。已產出奧利斯活動公司尖山埤 200 人 A/B/C 三份報價 Sheet，並用 A6 bot 送到 Owner 與 Mina。下一步若要常態化，請讓 A5 雲端/本地模型輸出 `createQuoteVariants` JSON payload，A6 會正確格式化三份連結；不要改 master `QUOTE_DRAFT` 表格、公式或 Items。
