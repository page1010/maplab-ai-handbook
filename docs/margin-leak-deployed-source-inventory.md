# MAPLAB deployed-source and header inventory

Status: `READ_ONLY_INVENTORY_COMPLETE / LIVE_ADOPTION_HOLD`  
Method: `margin-deployed-source-inventory-v1`  
Method fingerprint: `d282b0fee8655a3cbc075bc332c0eb9ab2e5f18bac05abefdb7d63f97c5f53c0`

This packet answers a deliberately narrow question: which integration facts are
independently verified today, and which ones are still only local or historical
evidence? It does not deploy, pull Apps Script source, read customer rows, mutate
Sheets, or authorize a live `case_id` rollout.

## Decision

- The four live full-header hashes still match the pinned static plan.
- The canonical quote GAS checkout and binding are present, and its selected
  eight-file local source bundle matches the pinned digest.
- The current deployed quote revision is **unresolved**. Historical deployment
  receipts do not prove that the later local source changes are deployed.
- A separate LINE GAS was historically configured and observed, but its current
  checkout, manifest, deployed revision, and source digest are **unresolved**.
- `Orders` / `OrderCharges` writer authority is **unresolved**. The quote GAS is
  not that writer; no qualifying current-source or Git-history selector match was
  found.
- Case Store and OpenClaw private artifacts are currently repo-contained with
  `0755/0644` exposure, so they fail the owner-only gate despite the launcher and
  wrapper declaring an owner-only umask. The Case Store `REPO_PATH` override is
  present and currently resolves to the canonical repo; it is hash-pinned rather
  than omitted from the root calculation.
- Direct GAS Web App ingress still cannot be LINE authority because it cannot
  verify the `x-line-signature` header against the untouched body.

Therefore the inventory is complete, but `eligible_for_live_change=false` and
confirmed leakage remains `0`.

## Truth matrix

| Surface | Verified now | Not proved / fail-closed result |
|---|---|---|
| Quote GAS local binding | Canonical `.clasp.json` digest `54d250fd991c659f11b301ae04f73f8e3f0eae2be2d6931392e2f9e99a104bb5`; binding fingerprint is stored only in the private receipt | A local binding is not deployed-source proof |
| Quote GAS local bundle | 8 selected files; tree digest `4d3014633bf0bc76e716e9570f34c396b0f3f69ad50e49528da8bc4d5cfa4a46`; `LineWebhook.gs` excluded | Current deployed revision/source digest `UNRESOLVED` |
| Quote GAS historical deployment | Script-ID fingerprint `9a1e92b9334587ca63b7b241c0c5c672e089e3326a618740a2bc1cad94b2d675`; deployment-ID fingerprint `f40bc41a8337e9072f44a4a930ee4f60b8f1e2193c177fd71029924f0ce65d07`; latest versioned receipt digest `b13fa3ab3f92eeea938ab1a4400cbd00454b3fb729cc2a6f5117674b9551e100` | Source changed after the latest qualifying receipt; history cannot be promoted to current runtime truth |
| Separate LINE GAS | Historical script-ID fingerprint `574c565ce94de0465e54695a7dad5d940760b5e7effb9d327ff02765c06e2f0b`; historical deployment-ID fingerprint `75a2b1726bfb7e5d27f92d3556d584476e1fe9eadf788b2dd77083c94e8baadd`; inbound was observed on 2026-05-19 | `scripts/apps-script-line/` absent; no current binding, manifest, version receipt, or deployed-source digest; `UNRESOLVED` |
| `Orders` / `OrderCharges` | 67 bounded current source files inspected; current writer matches `0`; Git-history sheet-selector matches `0`; quote GAS only writes `SALES_INTAKE` | Manual entry, an untracked bound script, or an external automation remain hypotheses, not authority |
| Case Store | `REPO_PATH` override present, fingerprint `d1420068bbedfdc3b8fb120401a9dca286849e45a5af61f88bc785e25e0d838a`, resolves to canonical repo; no direct DB/fallback override; directory `0755`, database `0644`, fallback seed present at `0644` | `REPO_LOCAL_UNSAFE`; database and fallback files are not repaired by a later process umask |
| OpenClaw review bundles | Default repo-contained `workbook/reviews`; root `0755`; no configured artifact-root override; fixed bundle-name scan found `405/405` regular artifacts at `0644`, `0` owner-only and `0` symlinks | `REPO_LOCAL_UNSAFE`; raw private prompt/output bundles cannot be considered owner-only |
| Google read credential | Token metadata present; mode `0644`; Apps Script project-read scope absent | `UNSAFE_MODE_AND_APPS_SCRIPT_SCOPE_MISSING`; it was not used for Apps Script network access |

All identifier fingerprints above are one-way SHA-256 values. Raw script IDs,
deployment IDs, URLs, tokens, customer identifiers, and customer rows are absent
from this document and the private receipt.

## Fresh full-header readback

| Table | Fields | SHA-256 | Result |
|---|---:|---|---|
| `SALES_INTAKE` | 15 | `b1ac8e43777ffe23e17dc4e0303b07b9d0cc1cbe7de46de03786865c7b3245fd` | matches pin |
| `Orders` | 29 | `672d0fa668a436d57a5f8593339839e22c347aabfa2600d00ac59e0bfa2b363e` | matches pin |
| `OrderCharges` | 4 | `2b34bd9c0b10b6ff00111ac9724d2e72b2567366491b487bf58dc53114fae949` | matches pin |
| `MAPLAB_ASSET_LOG` | 14 | `8ce84e88737b3d906ea1b789a2964a05d499cd3909d46b0906ecc3f7705ff9c9` | matches pin |

The connector performed 2 metadata reads and 7 bounded header reads. The higher
header count records two failed local hashing attempts plus the corrected
`MAPLAB_ASSET_LOG` normalization; it is not silently rewritten as four reads.
Null cell placeholders are excluded, while the literal string `"null"` remains
a real header value and would change the digest.

## Safety and proof boundary

- Google read operations: `9`; Google writes: `0`.
- Apps Script API calls: `0`; deploy/pull/push/write operations: `0`.
- Customer row reads, customer sends, price writes, and historical mutations: `0`.
- Credential network use and credential writes: `0`.
- Model calls for private data and new private third-party egress: `0`.
- Private receipt parent/file modes: `0700/0600`.

Receipt:
`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-deployed-source-inventory-v1.json`

- Receipt SHA-256: `2110647635fe3223e92bcf5ed421472774b68e339e59c60883f2d683af0dfd21`
- Deterministic body SHA-256: `c23563deae61f54aee6fa3e9e3b8d0e04b26e473556e2487f1e4dbd13c144fbc`

## Next repair point

Build a no-write hardening and migration plan before any live adoption:

1. map every consumer of the Case Store, OpenClaw review root, Google token, and
   deployed GAS bindings;
2. design owner-only external roots and atomic migration/readback/rollback gates;
3. design a dedicated hash-only deployed-source/header readback path without
   using the current `0644` credential or broadening private-data egress;
4. keep the LINE header-capable ingress and signature/replay envelope as Phase 0;
5. do not implement, deploy, chmod, migrate, or write live systems in that plan.

Only after those boundaries have independent readback can a separately approved
implementation task propose live changes.
