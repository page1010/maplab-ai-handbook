# Builder Handoff

The private portal is live and the local source package is complete. The live
PHP currently runs through Code Snippets because the browser extension cannot
upload local files until Chrome file-URL access is enabled. The installable zip
is kept in `dist/`.

Next safe slice:

1. Merge `codex/innerflowlab-secretary-v0` into the canonical repo.
2. Owner follows `docs/innerflowlab-personal-secretary-sync.md` to create one
   WordPress Application Password and store it directly in macOS Keychain.
3. Run the one-shot sync, then the fail-closed installer.
4. Verify launchctl, logged-in timestamp, anonymous 302, and REST 401.
5. Route the four remaining failed jobs to scoped B1/B2 repair tasks.

The role-module generator now rebuilds the Excel relationship workbook only
when `CODEX_NODE_MODULES` points to the workspace dependency bundle. Without
that dependency it reports XLSX as skipped instead of claiming a stale workbook
was generated.

Do not expose local port 18502, raw SQLite, holdings details, secrets, or any
command execution endpoint to WordPress.
