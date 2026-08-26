# Candidate contract

Use this contract when a social post, GitHub repository, plugin, MCP server, app, or skill may enter MAPLAB.

## Evidence levels

1. `SOCIAL_LEAD`: creator, post URL, visible claim, and date. Discovery only.
2. `PRIMARY_IDENTITY`: official product domain or upstream repository, source revision, license or service terms, and current maintenance evidence.
3. `LOCAL_OVERLAP`: existing skill, SOP, connector, browser route, or runtime that already covers the use case.
4. `ISOLATED_PROOF`: narrow smoke with synthetic/public input, observed filesystem/network effects, and rollback.
5. `OWNER_SURFACE`: only required when the promised value is visible in an authenticated app or delivered artifact. A unit test or API response cannot substitute for this layer.

Never skip directly from `SOCIAL_LEAD` to installed or connected.

## JSON shape

```json
{
  "candidate_id": "context7",
  "kind": "tool",
  "identity": {
    "status": "official_verified",
    "url": "https://github.com/upstash/context7"
  },
  "license": {
    "status": "verified_open",
    "id": "MIT"
  },
  "maintenance": "active",
  "fit": "high",
  "overlap": "partial",
  "runtime": {
    "ready": false,
    "smoke": "not_run"
  },
  "data": {
    "max_allowed": "public",
    "egress": "external_service"
  },
  "credentials": ["oauth"],
  "side_effects": ["network_read", "dependency_install"],
  "evidence": {
    "social_url": "https://www.instagram.com/...",
    "official_urls": ["https://github.com/upstash/context7"],
    "checked_at": "2026-08-27"
  },
  "note": "Public library documentation only."
}
```

Allowed values:

- `kind`: `tool`, `skill`, `service`, `reference`, `claim`
- `identity.status`: `official_verified`, `upstream_verified`, `ambiguous`, `social_only`
- `license.status`: `verified_open`, `verified_proprietary`, `missing`, `unclear`, `not_applicable`
- `maintenance`: `active`, `unclear`, `stale`, `archived`
- `fit`: `high`, `medium`, `low`, `none`
- `overlap`: `none`, `partial`, `substantial`, `duplicate`
- `runtime.smoke`: `passed`, `not_run`, `failed`, `not_applicable`
- `data.max_allowed`: `public`, `approved_brand`, `synthetic`, `private`
- `data.egress`: `none`, `public_only`, `external_service`, `unknown`
- `credentials`: `none`, `api_key`, `oauth`, `github_read_token`, `github_write_token`, `llm_key`
- `side_effects`: `none`, `local_files`, `dependency_install`, `network_read`, `external_write`, `security_scan`, `paid_generation`, `publish`

`runtime.ready` must be a JSON boolean, never a string such as `"false"`. `evidence.official_urls` must be non-empty for a verified identity. `checked_at` must be an ISO date.

`data.max_allowed` means the highest data class permitted to cross the recorded egress boundary. Therefore `egress=public_only` requires `max_allowed=public`, and `max_allowed=private` is valid only with `egress=none`. Treat a contradictory pair as an invalid contract, not as a judgment call. Do not include secret values, cookies, raw tokens, private file paths, or personal browsing history.

## Decision meaning

- `ADOPT` is a completed local decision, not a promise. It requires runtime readiness and smoke evidence.
- `PILOT` permits only the documented synthetic/public test. It does not authorize account creation, credentials, spend, uploads, external writes, or production use.
- `HOLD` identifies the exact missing gate. It is not a request to keep retrying unchanged infrastructure.
- `REJECT` means no new control plane. Useful ideas may still be translated into a narrow local rule if licensing and attribution permit.
- `NOT_A_TOOL` keeps references in a reading list or brief; it must not become a fake installation task.

`overlap=substantial` can never reach `ADOPT` from this evaluator alone. It needs a documented unique capability and an isolated side-by-side comparison; otherwise retain the existing route.

## Receipt fields

For every candidate record exact identity, source revision or check date, license/terms, maintenance signal, one use case, overlap, runtime requirements, data class, egress destination, credential types, side effects, cost model, evaluator output, smoke result, rollback, and decision owner.
