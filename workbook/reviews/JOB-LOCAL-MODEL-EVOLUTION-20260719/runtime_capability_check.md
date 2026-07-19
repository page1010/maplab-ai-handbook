# Runtime capability check — 2026-07-19

## What

The Mac mini can run narrow-domain local inference and deterministic evals now.
It is not prepared for a safe LoRA/adapter cycle, and this first cycle did not
install a training stack.

| Surface | Current evidence | First-cycle decision |
|---|---|---|
| Hardware | Apple M4, 24 GiB unified memory, 10 logical CPUs, macOS 26.2 | Suitable for quantized inference; training feasibility unproven. |
| Ollama | Installed; local runtime healthy | Use for fixed baseline only. |
| `qwen2.5:14b` | 14.8B, Q4_K_M, 32K context, Apache-2.0 | Primary text baseline. |
| `gemma4:latest` | 9.6 GB; Hermes currently routes to it | Inventory only in this eval. |
| `qwen2.5-coder:7b` | 4.7 GB | Code-specialist inventory; not a domain baseline. |
| `moondream:1.8b` | 1.7 GB | Vision specialist; out of scope. |
| Codex | CLI 0.144.6; subscription login health verified | Teacher role possible only after quota confidence gate. |
| Claude | Claude Code 2.1.128; subscription auth health verified | Teacher role possible only after quota confidence gate. |
| Antigravity | `agy` 1.1.4 available | Google ecosystem teacher role remains quota-unknown. |
| Gemini CLI | Standalone `gemini` binary missing | Use Antigravity/connected Google tools; do not infer quota. |
| Hermes | v0.15.1; launchd gateway running; local `gemma4` endpoint; zero scheduled jobs | Cold-path/local preparation only. |
| Google Drive/Sheets | Connector live reads succeeded on MAPLAB/Investment OS metadata and narrow headers | Read smallest range; never use customer/raw-message columns as training data. |
| SQLite | `investment_os.sqlite3`: 33.9 MB/60 tables; `demo_evolution.sqlite3`: 45 KB/4 tables; `investment_os.db`: empty/0 tables | Canonical file must be explicit; the empty `.db` is a wrong-path hazard. |
| launchd | Existing Ollama/Hermes/MAPLAB/Investment OS jobs present; weekly eval and SEO loop last exit 0 | Design schedule only; install nothing in cycle 1. |
| Training frameworks | `torch`, `transformers`, `peft`, `trl`, `datasets`, `mlx`, `mlx_lm`, `unsloth`, `llamafactory`, `axolotl` all absent | LoRA gate closed. |

## So What

The shortest useful path is not installing another framework. It is fixing the
truth boundary and measuring the existing local model. Runtime capability is
strong enough for G1 routines but does not prove G2 routing or G3 repair.

## Now What

Keep `qwen2.5:14b` as the frozen baseline, place a deterministic metadata/schema
wrapper in shadow, then reassess whether any residual semantic failure truly
requires prompt, skill, RAG, or adapter work.

## Loop Back

If a later fixed eval shows a repeatable semantic failure after the wrapper,
benchmark an approved prompt/skill/RAG candidate before proposing a training
framework or changing weights.
