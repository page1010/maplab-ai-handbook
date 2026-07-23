# Builder Handoff

The private portal is live and the local source package is complete. The live
PHP currently runs through Code Snippets because the browser extension cannot
upload local files until Chrome file-URL access is enabled. The installable zip
is kept in `dist/`.

Next safe slice:

1. Resolve the MAPLAB `CURRENT_STATUS.md` merge conflict.
2. Rebuild dynamic role modules and verify the source-hash alert clears.
3. Run IOS-ALPHA against fresh sources, produce a new phone card and shadow
   artifact, then verify the portal card leaves warning.
4. Create a WordPress Application Password and a low-frequency exporter
   schedule without storing credentials in git.

Do not expose local port 18502, raw SQLite, holdings details, secrets, or any
command execution endpoint to WordPress.
