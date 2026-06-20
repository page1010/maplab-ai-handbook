# A6/A5 Quote Trainee Training Receipt

Timestamp: 2026-06-20 08:21-15:57 CST
Supervisor: Codex
Target: A5/A6 15 pax birthday quote, 10 menu rows, Sheet-first `createQuoteVariants` payload

## Verdict

Usable trainee path:

- Direct local Ollama `qwen2.5:14b` is usable only with a strict JSON contract, `temperature=0` for fixed customer copy, and supervisor validation.
- OpenClaw main is not certified for this quote trainee workflow.
- Hermes is not certified for this quote trainee workflow.

Completion still remains Sheet-first: model output is only a payload/customer-copy draft. A real A5/A6 quote is complete only after GAS creates the quote Sheet and the quote ranges are read back.

## Runtime Results

| Runtime | Round | Result | Evidence |
| --- | ---: | --- | --- |
| OpenClaw main | 1 | FAIL | Self-marked PASS but produced 6 generic/non-MAPLAB rows and wrong payload shape. |
| OpenClaw main | 2 | FAIL | Self-marked PASS but wrote items directly into `variants[]`, omitted required totals/action/base, and invented prices. |
| OpenClaw main | 3 | FAIL | Returned a fake tool-call style object instead of the required JSON quote payload. |
| Hermes qwen2.5:14b | smoke | BLOCKED | Hermes required >=64K model context; local qwen2.5:14b context was 32K. |
| Hermes gemma4 default | smoke | FAIL | Smoke output was corrupted (`HERIPlease`), not a reliable trainee response. |
| Ollama qwen2.5:14b | 3 | FAIL | Payload math was correct, but customer copy leaked internal wording `高毛利` and overpromised `桌椅`. |
| Ollama qwen2.5:14b | 4 | FAIL | Removed internal wording, but weakened urgent deposit from `50% 訂金` to `一定比例的訂金`. |
| Ollama qwen2.5:14b + temperature 0 | 5 | PASS | Exact payload, 10 menu rows, `foodCost=3140`, `totalRevenue=15700`, `overallMargin=0.8`, `depositAmount=7850`, and fixed customer-safe copy. |

## Round 5 Acceptance Checks

- `action=createQuoteVariants`
- `variants[0].menu` exists
- exactly 10 menu rows
- exact MAPLAB item names preserved
- total item cost = `3140`
- `foodCost=3140`
- `totalRevenue=15700`
- `overallMargin=0.8`
- `depositAmount=7850`
- customer copy says `預收 50% 訂金`
- customer copy says tabletop setup only
- customer copy does not mention `高毛利`, `成本`, `毛利`, `利潤`, `桌椅`, `背板`, or `氣球`

## Supervisor Rule Learned

Do not ask a trainee model to freely draft customer quote copy for urgent jobs. The trainee may assemble/check structured payloads, but the customer-facing commercial terms must come from a fixed approved template unless a supervisor explicitly edits them.

## Next Resume Prompt

我是 A5/A6 Quote Supervisor，環境是 `/Users/pagemacmini/maplab-ai-handbook`。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A6-001.md`、`skills/a5-quotation-engine-skills.md`，再接續 `workbook/reviews/A6-QUOTE-OPENCLAW-TRAINING-20260618/training_receipt_20260620.md`。目前結論：OpenClaw/Hermes 未通過；可用學徒路徑是直接 Ollama `qwen2.5:14b` + strict JSON + `temperature=0` + fixed customer template + supervisor grader。不要把模型輸出當正式報價；正式完成仍要 GAS 建 Sheet 並回讀 `報價單!D2:F31` / `報價單!I7:J31`。
