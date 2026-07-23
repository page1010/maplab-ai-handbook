# Runtime capability report — 2026-07-23

Role: Local Model Evolution Orchestrator
Environment: Mac mini / local Draft PR #20 worktree
Decision mode: read-only inventory plus local eval; no training or production writes

## Live capability inventory

| Surface | Verified evidence | Cycle decision |
|---|---|---|
| Hardware | Mac mini `Mac16,10`; Apple M4; 10 cores; 24 GB unified memory; arm64 | Suitable for quantized inference. Adapter training feasibility is not established. |
| Python | `/opt/homebrew/bin/python3` | Use stdlib-only eval and quota tools. |
| Ollama | `/usr/local/bin/ollama`; version `0.30.7` | Use for the fixed local baseline. |
| Local models | `qwen2.5:14b` 9.0 GB; `qwen2.5-coder:7b` 4.7 GB; `gemma4:latest` 9.6 GB; `moondream:1.8b` 1.7 GB | `qwen2.5:14b` remains the text baseline; others are inventory only. |
| Codex | `/opt/homebrew/bin/codex`; `codex-cli 0.144.6` | CLI health is not remaining-quota evidence. |
| Claude | `/Users/pagemacmini/.local/bin/claude`; `2.1.128` | CLI health is not remaining-quota evidence. |
| Antigravity | `/opt/homebrew/bin/agy`; `1.1.5` | CLI health is not remaining-quota evidence. |
| Gemini CLI | Standalone `gemini` binary absent | Do not infer Google quota from Antigravity health. |
| Hermes | `/Users/pagemacmini/.local/bin/hermes`; `v0.15.1` | Local preparation only; no teacher job in this cycle. |
| SQLite | `/usr/bin/sqlite3`; `3.51.0` | Read-only evidence surface; canonical DB path must remain explicit. |
| launchd | `/bin/launchctl`; about 579 jobs visible | Inventory only; no scheduler install or modification. |
| Training frameworks | `torch`, `transformers`, `peft`, `datasets`, `trl`, `mlx`, `mlx_lm`, `unsloth` absent from the selected Python | LoRA/adapter gate stays closed. |

## Observed runtime behavior

- The full 40-case baseline completed.
- `SEO-019` hit the per-case 180-second timeout and was recorded as `0/8`.
- During the slow tail, `ollama ps` showed `qwen2.5:14b`, 9.5 GB, 100% GPU,
  `Stopping...`. No kill or restart was performed during the baseline.
- This is a runtime reliability finding, not permission to hide or rerun the
  failed case until it passes.

## Decision

The machine is ready for fixed local inference, deterministic gates, and
file-only shadow work. It is not yet justified for LoRA, model promotion, or an
installed autonomous teacher schedule.
