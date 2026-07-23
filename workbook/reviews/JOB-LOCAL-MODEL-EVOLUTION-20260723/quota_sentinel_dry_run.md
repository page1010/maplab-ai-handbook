# Quota Sentinel dry-run — 2026-07-23

Generated state: `local_model_evolution/state/provider_status.json`
Generated at: `2026-07-23T14:30:49+08:00`

## Result

| Control | Observed |
|---|---|
| Providers/runtimes inventoried | 8 |
| Secrets read | false |
| Usage APIs called | false |
| Teacher jobs created | 0 |
| Teacher jobs executed | 0 |
| Safe reserve | 15% |
| Global teacher decision | blocked |
| Block reason | all nonlocal remaining-quota values are unknown |

## Provider truth

- OpenAI API, Anthropic API, and Gemini API were not probed; policy blocks
  metered use without case-specific Owner approval and budget.
- Codex, Claude, and Antigravity subscription CLI health is available, but
  usage, remaining quota, and reset windows remain `unknown`.
- Hermes and Ollama local runtime health is verified; provider quota is not
  applicable.
- No reset-triggered teacher proposal is allowed while remaining quota is
  unknown. Availability is not quota.
