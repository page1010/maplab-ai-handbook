# InnerFlowLab Personal Secretary — Hourly Sync Setup

## Status

The exporter, Keychain-only wrapper, LaunchAgent, and installer are ready.
Activation intentionally stays fail-closed until the Owner creates one
WordPress Application Password and places it in macOS Keychain.

No password belongs in chat, git, `.env`, a plist, shell history, or a review
bundle.

## One-time Owner action

1. Open WordPress `Users -> Profile -> Application Passwords`.
2. Create one named `InnerFlowLab Mac Secretary Sync`.
3. Copy the generated password once.
4. In Terminal, run the command below. The final `-w` prompts for the password
   without placing it in the command itself:

```bash
security add-generic-password -U \
  -a "pagewu1010@gmail.com" \
  -s "com.maplab.innerflowlab-personal-secretary" \
  -T "/usr/bin/security" \
  -w
```

5. Paste the generated application password only into that Keychain prompt.

## Activate after branch merge

From the canonical checkout:

```bash
cd /Users/pagemacmini/maplab-ai-handbook
zsh tools/innerflowlab_personal_secretary_sync.sh
zsh tools/install_innerflowlab_personal_secretary_sync.sh
```

The first command performs one live push. The installer refuses to run outside
the canonical checkout or when the Keychain item is missing. After successful
installation, launchd pushes a sanitized snapshot once per hour.

## Verification

```bash
launchctl print gui/$(id -u)/com.maplab.innerflowlab-personal-secretary-sync
tail -40 /Users/pagemacmini/.local/share/investmentos-telegram-operator/logs/launchd/innerflowlab-secretary-sync.err.log
```

Then verify:

- logged-in `/personal-secretary/` shows a current timestamp;
- anonymous page access redirects to login;
- anonymous snapshot REST returns HTTP 401;
- WordPress contains no raw SQLite, holdings detail, credentials, or logs.

## Rollback

```bash
launchctl bootout gui/$(id -u)/com.maplab.innerflowlab-personal-secretary-sync
```

This stops synchronization without deleting the Keychain item or historical
sanitized receipt.

