# Review Request: IOS-FB No-Report + Credential Bootstrap

## Owner Request

Owner asked whether agents know to get social-account credentials from Notion, and why recent FB/social reports have not arrived.

## Files In This Bundle

- `system_patrol_report.md` — root-cause diagnosis with launchd/log/task-card evidence.
- `source_route_health.md` — credential/auth route status and next-run `auth_missing` contract.

## Decision Needed Later

Before the next fresh FB/social production report, choose one safe auth route:

1. Owner Chrome logged-in FB session / visual bridge.
2. A0 validates the Notion credential label and opens/maintains the login route.
3. Mark source route unavailable and send only an `auth_missing` status, not a stale historical report.

No passwords, tokens, cookies, OTP, or backup codes were read or written in this review bundle.
