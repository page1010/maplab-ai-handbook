# InnerFlowLab Personal Secretary

Private WordPress owner surface for sanitized MAPLAB and Investment OS health
snapshots.

## Security contract

- The page requires a logged-in WordPress administrator.
- WordPress stores a sanitized summary only.
- No broker credentials, API keys, cookies, holdings, raw logs, shell commands,
  or execution controls are accepted.
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

