# Security Incident Report — 2026-05-05

## Summary
- Incident type: credential exposure and unauthorized bot profile changes.
- Affected systems: Telegram bots `@maplab_a6_bot`, `@maplab_claude_bot`.
- Detection date: 2026-05-05.

## Confirmed Findings
1. Repository `page1010/maplab-ai-handbook` is public.
2. Sensitive tokens were committed in tracked backup env files:
   - `bot/.env.bak`
   - `bot_a6/.env.bak`
3. Exposed secrets included Telegram bot tokens and additional API/OAuth tokens.
4. Bot display names were modified and later restored.

## Likely Root Cause
- Token leakage from version-controlled `.env.bak` files in a public repository.
- Any actor with token access could call Telegram Bot API and alter bot metadata.

## Immediate Containment Completed
1. Bot display names reset to match usernames.
2. `.gitignore` updated to block env backups, logs, and local runtime artifacts.
3. Sensitive tracked artifacts queued for untracking from Git index.

## Required Next Actions (Critical)
1. Rotate all exposed secrets immediately:
   - Telegram bot tokens (done once; rotate again if uncertain).
   - Claude OAuth token(s).
   - Cloudflare/API tokens and any token found in committed files.
2. Convert repo to private until cleanup is complete.
3. Purge secret history from git (`git filter-repo` or BFG) and force-push.
4. Reissue production `.env` from a secure source and restart daemons.
5. Enable secret scanning and push protection in GitHub settings.

## Prevention Controls
- Keep runtime secrets only in local `.env` (never in backup files under version control).
- Use `.env.example` placeholders only.
- Add pre-commit secret scanning (`gitleaks` or equivalent).
- Monthly credential rotation policy for high-risk tokens.
