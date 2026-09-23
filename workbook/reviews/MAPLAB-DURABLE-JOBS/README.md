# MAPLAB durable jobs

Hermes writes private runtime job packets below this directory.  Every job
directory and file is owner-only (`0700` / `0600`) and intentionally ignored by
Git because it may contain the Owner's exact request or private workflow state.

The tracked contract lives in
`.agents/skills/maplab-durable-job-orchestrator/references/job-contract.md`.
Terminal evidence may be promoted into a separate sanitized review receipt,
but raw job packets must never be staged.
