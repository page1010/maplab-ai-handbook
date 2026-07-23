# InnerFlowLab Personal Secretary

Private WordPress owner surface for sanitized MAPLAB and Investment OS health
snapshots.

Version 0.2 adds a de-identified mirror of the local Investment OS dashboard
at `127.0.0.1:18501`: owner verdict, market date, production-job completion,
four core outcome lines, responsible roles, and freshness. It is a result
mirror, not a remote Streamlit proxy.

## Security contract

- The page requires a logged-in WordPress administrator.
- WordPress stores a sanitized summary only.
- No broker credentials, API keys, cookies, holdings, raw logs, shell commands,
  or execution controls are accepted.
- No account values, stock symbols, local filesystem paths, raw job messages,
  or localhost links are included in the 18501 mirror.
- The REST endpoint uses normal WordPress authentication and the
  `manage_options` capability.
- The page is marked `noindex`, `nofollow`, and `noarchive`.

## Install

1. Zip the `innerflowlab-personal-secretary` directory.
2. Upload it in WordPress Plugins, then activate it.
3. Activation creates `/personal-secretary/`.
4. Run the exporter in dry-run mode.
5. Provide WordPress credentials through environment variables and run with
   `--push`.

```bash
python3 tools/innerflowlab_personal_secretary_snapshot.py \
  --maplab-repo /Users/pagemacmini/maplab-ai-handbook \
  --ios-repo /Users/pagemacmini/investment-os
```

Push mode reads these environment variables without printing them:

- `IFL_WP_BASE_URL`
- `IFL_WP_USER`
- `IFL_WP_APP_PASSWORD`

```bash
python3 tools/innerflowlab_personal_secretary_snapshot.py \
  --maplab-repo /Users/pagemacmini/maplab-ai-handbook \
  --ios-repo /Users/pagemacmini/investment-os \
  --push
```

## Hourly sync

The production wrapper retrieves the WordPress Application Password from
macOS Keychain at runtime. No secret is stored in git, `.env`, or the launchd
plist. See `docs/innerflowlab-personal-secretary-sync.md`.

The installer remains fail-closed until the Owner has created the application
password and stored it in Keychain:

```bash
zsh tools/install_innerflowlab_personal_secretary_sync.sh
```
