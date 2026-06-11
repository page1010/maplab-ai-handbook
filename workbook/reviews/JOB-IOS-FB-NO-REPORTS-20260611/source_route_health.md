# IOS-FB Source Route Health

Date: 2026-06-11 13:31 Asia/Taipei
Scope: FB / social-source report route

## Current Route State

```yaml
fb_shadow_refresh:
  launchd_loaded: true
  schedule: daily 03:00
  observed_recent_runs: 2026-06-03 through 2026-06-11
  route_type: historical_shadow_sample_refresh
  fresh_production_collection: false
  telegram_reviewed_digest: false

social_account_auth:
  current_session_read_secrets: false
  owner_chrome_logged_in_route: not_verified_this_session
  notion_credential_route: documented_but_not_read_this_session
  status_for_next_collection: auth_preflight_required

quality_gate:
  status: failed
  blocker: FAIL_LOCAL_MODEL_TRAINING_RESPONSE
  reviewed_telegram_digest_allowed: false
```

## auth_missing Contract For Next IOS-FB Run

If IOS-FB cannot verify Owner Chrome logged-in FB route or an Owner/A0-approved Notion credential handoff, the next run must write:

```yaml
auth_missing:
  service: FB / IG / social source route
  tried:
    - checked Owner Chrome / visual bridge route
    - checked task card or handoff for credential label
    - checked A0 / Notion credential route availability
  reason: no usable login session or approved credential handoff
  owner_action_5min: open Owner Chrome FB session or ask A0 to validate the Notion credential label
```

The run must stop at `source_route_health.md`; it must not generate a current-looking report from old 2026-03-25 to 2026-04-25 samples.

## Safe Credential Rule

Notion may be used only as a credential vault / index when Owner/A0/A1 approves it. It is not state truth. The agent should only record route status and account labels, never passwords, tokens, cookies, OTP, or backup codes.
