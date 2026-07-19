# Quota source matrix and dry-run — 2026-07-19

## What

Quota Sentinel v0.1 ran in dry-run mode across eight provider/runtime entries.
It called zero usage APIs, read zero secret files, created zero teacher jobs,
and blocked the global teacher-job decision because every nonlocal remaining
quota value is unknown.

| Provider | Health evidence | Remaining quota | Reset evidence | Decision |
|---|---|---:|---|---|
| OpenAI API | Not probed; metered API blocked by repo policy | `unknown` | Provider/billing-specific | No API call; no teacher job. |
| Codex subscription | CLI login health `available` | `unknown` | CLI does not expose a reliable reset window | Login is not quota proof. |
| Anthropic API | Not probed; metered API blocked by repo policy | `unknown` | Usage report buckets are UTC report windows | No API call; no teacher job. |
| Claude subscription | CLI auth health `available` | `unknown` | CLI does not expose remaining subscription messages | Login is not quota proof. |
| Gemini API / Google Cloud | Not probed; metered API blocked by repo policy | `unknown` | RPD midnight Pacific, officially documented | No API call; no teacher job. |
| Antigravity subscription | CLI binary health `available` | `unknown` | Subscription reset not exposed | No teacher job. |
| Hermes local | Gateway health `available` | not applicable | local runtime | Local preparation only. |
| Ollama local | Runtime health `available` | not applicable | local runtime | Local fixed eval allowed. |

Official source adapters are specified but disabled:

- OpenAI Usage and Costs API: <https://platform.openai.com/docs/api-reference/usage/audio_transcriptions_object>
- Anthropic Messages Usage Report: <https://docs.anthropic.com/en/api/admin-api/usage-cost/get-messages-usage-report>
- Gemini API rate limits: <https://ai.google.dev/gemini-api/docs/rate-limits>

The API sources require organization/admin or project access and are distinct
from ChatGPT, Claude, or Gemini app subscription message limits.

## So What

There is no truthful basis for an “use remaining quota before reset” job today.
The 15% reserve cannot be calculated against `null`, so `unknown` must stop the
planner instead of being converted to an estimate.

## Now What

- Keep the dry-run status at `local_model_evolution/state/provider_status.json`.
- Accept only an official export, a bounded local request ledger, or a dated
  manual override before changing confidence to `estimated` or `verified`.
- Recalculate reset windows daily at 00:05 Asia/Taipei in design; do not install
  a scheduler until the Owner approves the care loop.

## Loop Back

When a trusted usage source appears, test only the quota adapter and teacher-job
proposal. Preserve 15%, require the reset to be 12–36 hours away, and keep job
execution behind a separate approval/right-to-use gate.
