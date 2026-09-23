# Hermes LINE Training Loop — Validation Receipt

- source: MacExternal LINE OA export
- source files: 3,625
- source rows: 86,825
- paired customer→Mina examples: 20,256
- train/eval: 15,993 / 4,263, split by conversation hash
- customer sender names: removed and replaced
- external training payload: de-named dialogue only

## Baseline run

- run: `HERMES-LINE-20260826-231928`
- batch: 12 real customer questions
- providers: OpenRouter NVIDIA Nemotron 550B and 120B free routes
- initial pass: 9/12 under the first gate; mean score 79.6
- concrete failures: missed time question, missed menu action, and one unsupported `$18,000/$28,000` price insertion
- correction: missed signals and price prohibition were written into rolling lessons; excessive length was promoted to a hard fail.

## Runtime

- installed LaunchAgent: `com.maplab.hermes-line-training`
- schedule: daily 02:20
- bounded batch: 5
- provider attempts: first two OpenRouter models, 45-second bound each, then local fallback
- state and receipts remain on MacExternal so the loop survives Codex sessions.

## Next

Run the lowest-scoring stage repair batch, compare against the baseline, and keep iterating until seven consecutive runs reach 85% with zero unsupported commercial claims.
