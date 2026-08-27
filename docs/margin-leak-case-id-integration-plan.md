# MAPLAB Case-ID No-Write Integration Plan

Status: `PROPOSAL_ONLY / STATIC_GATE_FIXTURES_VALIDATED / NO_LIVE_WRITE`

Method: `margin-case-id-integration-plan-v1`

Purpose: map the already validated intake-time `case_id` contract onto the
current MAPLAB code surfaces without changing live GAS, Sheets, messages,
prices, or historical rows. This plan is a patch map and migration contract,
not a deployment authorization. It does not prove leakage and keeps
`confirmed_leakage_amount=0`.

## Plateau decision

The recent methods were evidence join (`9a739a73...`), live Google bridge
(`8c96645...`), join-first shadow (`cfe227ba...`), and the synthetic intake
contract (`a1573a74...`). The last historical-join rounds produced no unique
identity link, so the declared stop-loss remains in force: do not add another
name/date/fuzzy backfill round. This method changes the repair point to exact
source-to-adapter mapping and synthetic compatibility gates; it makes no model
or network call.

## Exact current-source map

| Surface | Current anchor | Verified behavior | Required patch boundary |
|---|---|---|---|
| LINE ingress | `scripts/apps-script/LineWebhook.gs::doPost`, `handleLineWebhook_` | This is a direct Apps Script Web App handler. It locks, de-duplicates LINE message IDs, writes a new message UUID, and appends an empty `case_id`; its bounded Script Properties cache is not a durable case ledger. Google documents the Apps Script Web App event object with query/path/content-length/post-data fields but no request-header field, while LINE requires `x-line-signature` from the request header plus the untouched raw body. The current GAS handler therefore cannot implement LINE signature verification as written | Put a header-capable ingress in front of GAS/local intake. It must verify LINE's signature against the untouched raw bytes before JSON parsing, dedupe, acknowledgement, or outbox insertion, then forward only an authenticated, nonce-bound, replay-bounded internal envelope. GAS must reject direct/unsigned calls. If no such ingress is selected and verified, fail closed and do not enable LINE ingestion. A LINE message remains `PENDING_UNASSIGNED`; only an explicit case-open authority may mint/link a case. One LINE user may have concurrent cases. Never derive the key from customer data, elapsed time, or row number. |
| LINE deployment source | `scripts/apps-script/.claspignore`; `scripts/apps-script/README.md` | `LineWebhook.gs` is excluded from this clasp project; README points to a separate `scripts/apps-script-line/` path that is absent from this checkout | Treat the repo copy as evidence, not confirmed deployed truth. Obtain a read-only deployed-source digest in the separately approved live-review task before choosing a patch target. |
| Case Store fetch | `bot_a6/case_store.py::fetch_conversation_log_rows` | Reads only the most recent 600 rows by default | Replace window-derived identity with an exact intake-ledger lookup. The window may remain a display/cache bound but may not define identity. |
| Case Store build | `bot_a6/case_store.py::_case_from_cluster` | Falls back to `LINE-{date}-{user hash}-{first row}` | Post-cutover blank keys are `CONTRACT_VIOLATION`; pre-cutover blanks remain `LEGACY_UNLINKED`. Never mint or attach from the fallback. |
| A5 payload | `bot_a6/a5_quote_engine.py::build_sheet_quote_payload`, `_build_basic_high_margin_quote_payload`, `_extract_quote_tracking_fields` | Carries `base.caseId` when a permissive text regex finds one; an empty value is possible | Accept a typed envelope from the local domain worker, validate the canonical UUIDv4 form, and pass `case_id`, `quote_group_id`, and a unique `quote_id` as separate fields. No free-text extraction at the provider boundary. |
| Private quote route | `bot_a6/bot_a6.py::casequote_cmd`, `_run_a5_quote_background` | `/casequote` currently prepends `/localquote`, so raw Case Store context takes the local branch. General A5 has a cloud branch. Safety depends on a command-prefix convention, not a data-class guard | Add a structured `data_class=private-local-only`, `allow_cloud=false`, `allow_live_write=false` envelope and enforce it again at the provider/GAS boundary. The current `/localquote` behavior is a useful defense but is not the contract. |
| Private local artifacts | `bot_a6/case_store.py::CaseStore.__init__/from_env`; `tools/ai_workbook/openclaw_adapter.py::run_local_task` | Case Store defaults to a repo-local database unless `CASE_STORE_DB_PATH` overrides it; neither branch enforces owner-only modes. OpenClawAdapter writes the full prompt/output/terminal bundle under repo `workbook/reviews` | The private adapter must use a dedicated non-repo root with directory/file modes `0700/0600`, loopback-only local inference, no provider override, and redacted aggregate receipts. It must fail if cloud keys or proxy settings are present. |
| Quote endpoint | `bot_a6/bot_a6.py::_trigger_gas_quote_sync`; `scripts/apps-script/ApiEndpoint.gs::doPost`; `scripts/apps-script/Code.gs::handleQuoteRequest_` | Client sends only `Content-Type`; server has no visible request-signature/idempotency gate; `handleQuoteRequest_` rebuilds `formData` without copying `params.caseId` | Both sender and verifier must implement an authenticated signed request, nonce/replay window, and server idempotency before accepting a typed envelope. `case_id` is never a bearer token or authorization capability. |
| Quote creation | `scripts/apps-script/Code.gs::createQuote` | Ignores inbound `base.caseId`, creates a second-resolution `Q...` value, copies a Drive Sheet before the final `SALES_INTAKE` append, and writes the generated Q value as case metadata | Preserve the parent `case_id`; create a distinct opaque `quote_id`; retain the Google file ID only as `quote_spreadsheet_id`. Missing/mismatched parent means zero write. Use an operation ledger so retry can find and reconcile an orphan copy after response loss instead of creating another file. |
| Quote variants | `scripts/apps-script/Code.gs::createQuoteVariants_` | Calls `createQuote()` once per variant; each call creates its own `Q...` value | Variants inherit one case and quote-group key, have unique quote IDs and spreadsheet IDs, and use one idempotency key per variant. |
| Intake write | `scripts/apps-script/Code.gs::writeToIntake_` | Builds a positional A:O row only after quote creation; the variable called `quoteId` is actually parsed from a spreadsheet URL | `SALES_INTAKE` becomes one pre-quote case row and acknowledges the case independently. Put one-to-many quote/variant records in a `QUOTE_REGISTRY` child table. Resolve columns by validated names, upsert by idempotency key, and require exact-key readback. |
| Orders / charges | No `Orders`, `OrderCharges`, `order_id`, or `charge_id` writer was found under tracked `scripts/apps-script/*.gs` or `bot_a6/*.py` | The prior read-only source receipt shows `Orders` has `order_id` only and `OrderCharges` has `order_id, description, charge_type, amount` | Do not invent a writer. Confirm the authoritative source and deployment digest first; then add immutable case/quote parents and charge idempotency through that source. |
| Asset log | `scripts/a4_s11_2024_resume_classifier.py::sheet_append_rows`, `_flush_pending` | Appends A:G. Local `appended=1` is set only after the HTTP response, so response loss followed by retry can duplicate a file row | Use `file_id` exact-key pre-read/upsert/post-read, keep immutable `origin_case_id`, and put deliberate reuse in a separate case-asset link. |

The fixture validator snapshots these anchors by SHA-256 and expected fragments.
Any drift yields `HOLD`; it does not silently adapt or claim the deployment has
changed.

## Target identity envelope

Every prospective operation carries:

- `contract_version`, `stage`, `stage_event_ref`, `payload_fingerprint`;
- `case_id` and, after intake, `parent_ref`;
- the stage-specific key (`quote_id`, `order_id`, `charge_id`, or `file_id`);
- `idempotency_key`, `data_class`, and `created_at`.

`stage_event_ref` is a local keyed HMAC. New third-party research payloads,
telemetry, logs, and receipts must not contain the raw provider event ID or raw
`case_id`. Existing authorized internal Google destinations must carry the
exact case key to satisfy the join contract. Identity never grants
authorization to quote, publish, charge, message, or expose private data.

### Case-open authority and cardinality

`handleLineWebhook_` may acknowledge a message event, but it cannot decide a
case boundary. The local ledger first stores the event as `PENDING_UNASSIGNED`.
An explicit, idempotent case-open action then creates one case and links one or
more message HMACs to it; a later authorized assignment may link another
message. Fixtures must cover two simultaneous cases for one LINE user and
reject ambiguous message assignment. The old 168-hour cluster remains
display-only.

The public LINE webhook target cannot be the present direct GAS Web App. A
header-capable ingress must retain the untouched raw body, verify
`x-line-signature`, and only then construct an authenticated internal envelope
containing a nonce, received-at time, raw-body digest, and deterministic event
reference. The downstream GAS/local worker verifies that envelope and its
replay window; it never treats knowledge of `case_id` as authorization. This is
a hard precondition, not a future enhancement. The basis is Google's official
[Web Apps event-object reference](https://developers.google.com/apps-script/guides/web)
and LINE's official
[webhook-signature procedure](https://developers.line.biz/en/docs/messaging-api/verify-webhook-signature/).

`SALES_INTAKE` has one prospective row per case and is written before quote
side effects. `QUOTE_REGISTRY` has one row per quote variant and holds
`quote_group_id`, `quote_id`, and `quote_spreadsheet_id`. This removes the
current cycle in which `SALES_INTAKE` cannot acknowledge until after a quote
already exists.

## Named-header targets

Unknown extra columns and column reordering are allowed. NFKC/trimmed names
are matched case-insensitively against the canonical names; aliases are not guessed.
Missing, duplicate, blank, numeric, non-string, or wrong-version headers stop
the whole batch before a write. Existing columns, formulas, dashboards, and
K/L/M status behavior are not reordered; approved new columns are appended.
Customer-supplied strings are written as literal values and inputs beginning
with formula-control characters are rejected or escaped. Only reviewed system
formulas may use formula input mode.

| Table | Required prospective keys |
|---|---|
| `SALES_INTAKE` | `case_id`, `drive_case_folder_id`, `scope_version`, `scope_confirmed_at`, `contract_version`, `payload_fingerprint`, `idempotency_key` |
| `QUOTE_REGISTRY` | `quote_id`, `quote_group_id`, `case_id`, `quote_spreadsheet_id`, `variant_label`, `idempotency_key`, `contract_version`, `payload_fingerprint` |
| `Orders` | `order_id`, `case_id`, `quote_id`, `scope_version`, `scope_confirmed_at`, `drive_case_folder_id`, `contract_version`, `payload_fingerprint`, `idempotency_key` |
| `OrderCharges` | `charge_id`, `order_id`, `case_id`, `quote_id`, `idempotency_key`, `source_evidence_hash`, `contract_version`, `payload_fingerprint` |
| `MAPLAB_ASSET_LOG` | `file_id`, `origin_case_id`, `quote_id`, `order_id`, `delivery_type`, `delivered_at`, `delivery_verified_by`, `contract_version`, `payload_fingerprint`, `idempotency_key` |

The prior read-only header receipt is the fixture snapshot, not permission to
write. In particular, the current asset header contains numeric values and the
current five tables are missing required foreign keys; compatibility therefore
correctly fails closed.

The static fixture pins the full prior header digests: `SALES_INTAKE`
`b1ac8e43...`, `Orders` `672d0fa6...`, `OrderCharges` `2b34bd9c...`, and
`MAPLAB_ASSET_LOG` `8ce84e88...`. A changed digest is review-required; this is
not a fresh live readback.

## Durable outbox and readback gate

```text
local intake transaction
  -> PENDING (unique stage_event_ref + idempotency_key + payload fingerprint)
  -> exact-key destination pre-read
  -> destination write or deterministic no-op
  -> SENT_UNVERIFIED
  -> exact-one live readback of key, parents, fingerprint, contract version
  -> COMMITTED
```

- A response loss never authorizes a second append. Retry starts with exact-key
  readback using the same idempotency key.
- Zero rows remain `PENDING`; two rows, changed payload, wrong parent, or wrong
  case become `CONFLICT` and stop downstream work.
- `Case Store` and `SALES_INTAKE` are two independent acknowledgements. Quote
  creation remains closed until both exact readbacks agree.
- A local state of `SENT_UNVERIFIED` or an HTTP 2xx is not completion.
- The operational implementation must reproduce the prior restart and
  two-worker race tests in the actual worker; this plan's tiny state-machine
  fixture only validates the gate semantics. It does not validate a durable
  outbox runtime.
- LINE GAS, quote GAS, the local worker, and asset writer have no shared
  transaction. Treat the flow as a saga with independent acknowledgements;
  never claim distributed atomicity.
- Quote operations store the intended `quote_id`, target filename, and payload
  fingerprint before `makeCopy`. A retry first searches by the operation key,
  reconciles an existing orphan, and only then decides whether a new copy is
  allowed.

## Ordered migration and rollback

| Phase | Preconditions and bounded change | Acceptance readback | Rollback |
|---|---|---|---|
| 0. Truth and ingress freeze | Read-only digest of the actually deployed LINE source, quote GAS, current headers, and authoritative Orders/charges writer. Select a header-capable ingress design that exposes the untouched raw body plus `x-line-signature`; direct GAS Web App ingress is ineligible. No write or deploy | Digests and header hashes match a reviewed source inventory; ingress threat model and signed internal-envelope contract are reviewed. Without both, LINE remains disabled | No state changed; retain `PROPOSAL_ONLY` |
| 1. Local ledger/outbox shadow | Add a private local ledger and worker behind a disabled feature flag; owner-only `0700/0600` root, loopback-only model, cloud keys/proxies removed; synthetic events only | Restart, response-loss, replay-conflict, two-worker, and file-mode tests pass | Disable worker; keep ledger for audit, do not delete/re-key |
| 2. Authenticated prospective case-open shadow | Only after a header-capable ingress fixture verifies LINE signature over untouched raw bytes, rejects changed bytes/missing header/replay, and GAS rejects direct unsigned input: after a recorded ingestion cursor, store authenticated messages as pending; only an explicit case-open authority may mint/link. Exercise two concurrent cases for one user | Signature-positive fixture plus changed-body, missing-header, stale/replayed-envelope, and direct-GAS rejection; exact source-event replay, ambiguous assignment rejection, and window-independent identity | Disable ingress/worker flags; LINE ingestion fails closed; post-cutover shadow rows remain audit records |
| 3. Nullable schema preparation | In a separately approved live-write task, append named nullable keys and schema version to `SALES_INTAKE`, `QUOTE_REGISTRY`, Orders/charges, and assets; no reorder or historical fill | Header hash, permissions, formulas, dashboards, row count, and sample null rows read back unchanged except approved appended columns | Stop writers and hide/deprecate new columns; never delete a populated key |
| 4. Dual acknowledgement | Create one canary case row before quote; Case Store and `SALES_INTAKE` outbox adapters acknowledge independently | Exact-one readback on both destinations before quote eligibility | Freeze new quote writes, drain/reconcile the outbox, and leave canary key/receipt immutable |
| 5. Quote registry and key separation | Through an authenticated, signed, idempotent endpoint, preserve `case_id`; add `quote_group_id`, unique `quote_id`, `quote_spreadsheet_id`, and one `QUOTE_REGISTRY` row per canary variant | All variants share case/group, have unique quote/file IDs, orphan recovery is exact-one, and intake readback matches | Freeze new quote writes, drain/reconcile pending/orphan operations; do not fall back to blank-key legacy writes |
| 6. Order/charge adapter | Only after authoritative writer truth is confirmed, propagate immutable case/quote parents and charge idempotency | Order exact-one; every charge parent/key/fingerprint exact-one | Disable adapter; retain keys; never rewrite historical orders |
| 7. Asset upsert | Replace blind append for canary case assets with `file_id` upsert and immutable origin; separate reuse links | Response-loss retry produces one file row and one intended link | Disable adapter; retain origin and links; never delete evidence |
| 8. Evidence shadow | Join only new prospective cases and verify the four evidence pillars | Aggregate receipt only; no auto-charge or customer send | Stop shadow evaluator; confirmed amount stays zero for incomplete chains |

Before cutover, rollback means disable the shadow worker. After cutover,
rollback must freeze new quote writes and drain/reconcile the outbox; it may
not restore a blank-key writer for prospective events. Rollback never means
delete foreign keys, recycle IDs, fuzzy-link history, or remove an audit
ledger. No phase may advance on a file receipt alone; the named live readback
is required.

## Fixture compatibility matrix

The local validator must keep these outcomes stable:

1. Current `SALES_INTAKE`, absent `QUOTE_REGISTRY`, `Orders`, `OrderCharges`,
   and `MAPLAB_ASSET_LOG` fixtures reject for missing required keys; the asset
   fixture also rejects numeric headers.
2. A complete target schema still accepts column reordering and unknown extras.
3. Duplicate `case_id`, blank/non-string/numeric headers, or missing required
   keys reject the whole batch.
4. A private raw-context route rejects cloud providers, non-loopback endpoints,
   cloud environments, and 0755/0644 artifact sinks; it accepts only the
   owner-only local domain worker.
5. An outbox row commits only after an exact fingerprint readback; missing
   readback stays pending and mismatched readback becomes conflict.
6. Any changed source anchor, unexpected fixture result, or unsafe receipt
   value changes the decision to `HOLD` and keeps `live_adoption=false`.
7. Customer formula injection such as an `=IMPORT...` value rejects; a
   separately constructed, reviewed status formula may pass.
Permanent deeper adapter tests required before live review include: same-event
same-payload replay, changed-payload conflict, two independent case
acknowledgements, two concurrent cases for one user, ambiguous assignment
rejection, quote-variant parent preservation, orphan-copy recovery,
order/charge foreign-key equality, asset response-loss idempotency, cutover
cursor handling, and the continued ban on historical fuzzy backfill. The later
header-capable LINE ingress adapter must also reject a missing/invalid header,
altered raw body, stale or replayed internal envelope, and any direct unsigned
GAS request. Those ingress fixtures are intentionally not implemented or
validated by this static plan validator; passing the current 25 fixtures must
not be read as signature/envelope runtime proof.

## Private-local-only quote routing

The guard is policy data, not a command string:

```text
if data_class == private-local-only:
    provider must equal local-domain-worker
    endpoint must be loopback
    artifact root and files must be owner-only 0700/0600 and outside the repo
    provider/model overrides and cloud keys/proxies must be absent
    allow_cloud must be false
    allow_live_write must be false unless a separate approved action supplies it
    raw context must never appear in telemetry, receipt, exception, or handoff
```

Enforce this at route selection and again immediately before any provider or
GAS call. Tests must replace cloud, network, and GAS functions with spies and
assert zero calls for a private Case Store context. `/localquote` may remain a
user-facing alias, but it cannot be the only safety control. The existing
repo review-bundle sink is forbidden for raw private context.

## Deployed-source truth boundary

The following remain deliberately unresolved, not guessed:

- the authoritative deployed LINE project and its exact source revision;
- the chosen header-capable LINE ingress and signed internal-envelope contract;
- the authoritative `Orders`/`OrderCharges` writer;
- whether live headers changed after the prior read-only receipt;
- the operational worker topology that can make ledger persistence precede
  webhook acknowledgement.

These are an `OWNER_REVIEW` boundary for a future live-change proposal, not a
blocker to this no-write plan. Before any live patch, the next task must obtain
read-only deployed-source/header digests and choose the ingress authority. No
deployment, schema write, secret movement, or private third-party egress was
performed here.

## Artifacts and stop-loss

- Validator: `scripts/maplab_case_id_integration_plan.py`
- Tests: `tests/test_maplab_case_id_integration_plan.py`
- Private aggregate receipt:
  `/Users/pagemacmini/.maplab/margin-leak-audit/20260828-case-id-integration-plan-v1.json`

Passing means the plan matches the current repo snapshot and all synthetic
gates behave as declared. It does not mean the repo source equals deployed
source, does not authorize live adoption, and does not confirm a billable leak.
