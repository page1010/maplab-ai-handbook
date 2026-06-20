# Mac-1 / macOS Native Tools Watchlist

Last checked: 2026-06-15

## Current Finding

The Instagram screenshot claim says an open-source "Mac-1" model with 6.6B parameters can call 487 macOS native functions across Calendar, Mail, filesystem, and Safari.

Public exact-match searches for the core claim did not surface a trustworthy primary source:

- `"Mac-1" "487" "macOS"`
- `"Mac-1" "6.6B"`
- `"Mac-1" "native tools" "macOS"`
- `"Mac-1" "487 tools"`
- `"開源模型" "Mac-1" "macOS"`
- `"Mac-1" "Calendar" "Mail" "Safari"`
- `site:github.com "Mac-1" "487"`
- `site:huggingface.co "Mac-1" "6.6B"`

Until a primary source is found, do not add Mac-1 itself to the A6/OpenClaw production route. This is not a work stoppage: continue by using existing MAPLAB routes for read-only checks, draft payloads, disposable tests, and approval-ready packets.

## Evidence Required Before Adoption

- Official repository or package source.
- Model card with license, maintainer, release notes, and parameter count.
- Tool schema or function list proving the claimed macOS native functions.
- Install procedure that can run on the owner Mac without exposing secrets.
- Security model for permissions, logging, confirmation, and sandboxing.
- Reproducible smoke test for at least one read-only and one disposable write action.

## MAPLAB Position

The useful idea is not "give a model 487 tools." The useful idea is:

1. Let the model classify intent.
2. Let deterministic, allowlisted tools execute.
3. Execute safe read-only and draft work immediately.
4. Ask Owner only for final live writes, external sends, destructive changes, or owner-overrides.
5. Leave review bundles and receipts.
