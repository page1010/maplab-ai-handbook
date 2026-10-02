# A6 LINE OA Curriculum Validation Receipt

- Timestamp: 2026-10-02 22:13 CST
- Verdict: `SAFETY_PASS / IMPROVED_DEVELOPMENT_FIXTURES_ONLY / WEIGHT_LEARNING_NOT_PROVEN / PROMOTION_BLOCKED`
- Scope: local-only materialization and deterministic contract validation

## Source

- A6 snapshot id: `1`
- Saved replies: `28`
- Source payload SHA-256: `1fc1eeacdd4465e053356325839a8f9a001e9e3362cf235b35f9a8345fe8a871`
- Raw message copied into fixture: `false`

## Result

- Development fixtures: `28`
- `PROHIBITED_NEGATIVE`: `20`
- `HISTORICAL_REFERENCE`: `8`
- Approved-pattern violation count: `0`
- Source violation signals: availability commitment `1`; money or terms commitment `8`; more than one question `3`
- Fixture SHA-256: `83feab25499816587736c8eaa879ad1a4fb86b947db287975cc79f16acb71060`
- Lesson SHA-256: `c3e079899de7f13eef950b33967ce734c37ca1c4d1a92785120dbf473ae050bc`

## Execution Counters

- Provider attempts: `0`
- Optimizer steps: `0`
- Weight delta created: `false`
- Customer sends: `0`
- External egress: `0`

## Storage Controls

- Private root: `/Users/pagemacmini/.maplab/a6-hermes-training/line_oa_saved_replies/`
- Directory mode: `0700`
- `development_fixtures.jsonl`: `0600`
- `current_lessons.md`: `0600`
- `receipt.json`: `0600`

## Verification Commands

```text
python3 -m unittest tests.test_a6_line_saved_reply_curriculum
Ran 2 tests ... OK

python3 -m unittest tests.test_hermes_sheets_assistant tests.test_line_oa_settings_import tests.test_a6_line_saved_reply_curriculum
Ran 19 tests ... OK

python3 -m compileall -q scripts/a6_line_saved_reply_curriculum.py tests/test_a6_line_saved_reply_curriculum.py
exit 0
```

## Evidence Boundary

This receipt proves a private, reloadable curriculum and current-contract regression layer. It does not prove model-weight learning, live Telegram or LINE behavior, owner-approved human gold, or production promotion.
