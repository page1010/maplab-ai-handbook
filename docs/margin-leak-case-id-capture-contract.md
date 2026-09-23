# MAPLAB Intake-Time Case ID Capture Contract

Status: `PROPOSAL_ONLY / SYNTHETIC_VALIDATED / NO_LIVE_WRITE`

Method: `margin-intake-case-id-contract-v1`

Purpose: prevent future margin-leak evidence from becoming impossible to join.
One opaque case key is created exactly once at new-case intake and every later
system inherits it. This contract does not prove leakage, authorize a charge,
or authorize changes to live Google Sheets, GAS, LINE, prices, or history.

## Verified synthetic outcome — 2026-08-28

The deterministic reference implementation preserved one case key across all
five required stages. Case Store and `SALES_INTAKE` were verified as separate
acknowledgements, and the durable intake ledger converged after restart and a
two-connection race:

| Holdout | Expected and observed |
|---|---|
| Valid five-stage chain | `ACCEPTED`, 5/5 stages |
| Missing Case Store acknowledgement | `CASE_STAGE_INCOMPLETE` before quote |
| Missing `SALES_INTAKE` acknowledgement | `MISSING_PARENT` |
| Case Store and `SALES_INTAKE` disagree | `CASE_ID_MISMATCH` |
| Quote changes case key | `CASE_ID_MISMATCH` |
| OrderCharge changes case key | `CASE_ID_MISMATCH` |
| Asset changes case key | `CASE_ID_MISMATCH` |
| Same event, changed payload | `REPLAY_CONFLICT` |
| Historical fuzzy auto-backfill | `LEGACY_AUTO_LINK_FORBIDDEN` |
| Restart plus two SQLite connections | `ACCEPTED_DURABLE` |

The permanent regression suite also covers duplicate-child semantics, invalid
IDs, wrong parent kinds, multi-charge/multi-asset DAGs, migration provenance,
deterministic manifests, structural receipt allowlisting, and private file
permissions. Intake retry is tested through two SQLite connections and a fresh
ledger instance, not only a process-local lock. Passing means only
`eligible_for_separate_live_review`; it does not mean live adoption.

## Canonical identifier rule

- Shape: `case_<lowercase RFC 4122 UUIDv4>`.
- Ownership: only a `new_case` conversation-intake transaction may mint it.
- Entropy: production minting uses the operating-system CSPRNG. Customer name,
  phone, date, text, row number, Sheet ID, or a seeded/deterministic UUID are
  forbidden inputs.
- Durability: the source event's local keyed HMAC mapping and the new `case_id`
  must be persisted atomically before acknowledgement.
- Replay: same event reference plus same payload fingerprint returns the
  persisted key; same event reference plus different payload fails closed.
- Meaning: `case_id` is identity, not authorization. Existing ACL, tenant,
  environment, approval, and privacy controls still apply.
- Exposure: receipts, logs, filenames, URLs, and third-party research payloads
  contain neither raw source IDs nor raw case IDs.

## Five-stage contract

Every stage envelope has `contract_version`, `stage`, `case_id`,
`stage_event_ref`, `payload_fingerprint`, and—except a new intake—`parent_ref`.
`stage_event_ref` is a local keyed HMAC, not the provider's raw event ID.

| Stage | Authoritative operation | Fail-closed rule |
|---|---|---|
| Conversation intake | Mint once and reserve the source-event mapping | Duplicate content is a no-op; changed replay is a conflict |
| Case Store + `SALES_INTAKE` | Each independently inherits and acknowledges the intake key exactly once | Coverage requires both acknowledgements; missing/duplicate/invalid key or parent means zero downstream write |
| Quote creation | Create a distinct `quote_id`, retaining the parent case key | Never replace a missing case key with a quote timestamp ID |
| `Orders` + `OrderCharges` | Order inherits quote key; every charge equals its parent order key | Parent mismatch or duplicate key with changed content means zero write |
| `ASSET_LOG` | Case-specific asset inherits its parent order key | Shared brand asset is not case delivery evidence; origin is immutable |

This is a DAG, not a one-row state enum: one case may have quote variants,
multiple charges, and multiple assets. Each child has its own typed identifier
and idempotency key. A duplicate child with identical parent and payload is a
no-op; a duplicate child with different content or a different case is a
conflict. Alias/merge work must use a separate Owner-reviewed ledger and may
not re-key history.

## Current integration gaps found by read-only inspection

These are reasons not to connect the contract live yet:

1. `LineWebhook.gs` writes a new message UUID but leaves `case_id` blank for a
   human to fill.
2. `bot_a6/case_store.py` falls back to a date, LINE-user hash, and first row.
   Its sliding sync window can therefore change the derived case identity.
3. `scripts/apps-script/Code.gs` receives `base.caseId` but creates a separate
   second-resolution `Q...` value. Quote variants can collide or split one
   case, and quote ID is conflated with spreadsheet ID.
4. The live `SALES_INTAKE` header captured by the safe read receipt differs
   from the repo's positional A:O writer. A future adapter must use named-header
   validation, idempotent upsert, and live readback—not positional append.
5. `Orders` and `OrderCharges` do not currently expose the case/quote foreign
   keys required by this contract, and no authoritative writer was found in
   the inspected repo paths.
6. The inspected `ASSET_LOG` writer is append-only and stores no case/quote/
   order link. Response loss followed by retry can duplicate a file row.
7. The existing `/casequote` context can include raw LINE messages and has a
   cloud fallback. Private intake must not auto-enter that route without a
   separately tested private-local-only guard.

No production file above was edited or deployed by this experiment.

## Migration and backfill boundary

- The cutover boundary must be an ingestion cursor or an explicit migration
  snapshot, never the customer's event date.
- New post-cutover cases must receive a key at intake. `PROSPECTIVE_LINKED`
  requires both `prospective_intake` provenance and verified presence in the
  durable intake ledger. Missing downstream keys are `CONTRACT_VIOLATION`, not
  legacy data.
- Historical rows without a key remain `LEGACY_UNLINKED` or
  `INSUFFICIENT_EVIDENCE`.
- A historical row may be attached only through deterministic evidence and an
  Owner-reviewed decision, recorded as `HISTORICAL_VERIFIED`.
- Names, dates, phone numbers, content hashes, filenames, image similarity,
  and fuzzy matching must never mint or attach a historical case key.
- This contract never changes historical rows and keeps
  `confirmed_leakage_amount=0` until baseline scope, actual delivery,
  incremental cost, and charged-fee evidence all join to the same case.

## Required controls before any live adoption proposal

1. Promote the synthetic SQLite intake ledger pattern into an operational local
   identity ledger/outbox with unique source-event and child idempotency
   constraints; separately test crash recovery in the actual worker.
2. Named-header schema validation before writes; duplicated, numeric, missing,
   or wrong-version headers stop the whole batch.
3. Upsert followed by exact live readback before a write is marked committed.
4. Separate `quote_id` from `quote_spreadsheet_id`; variants share case and
   quote-group keys but have unique quote keys.
5. Add immutable parent keys to Orders and OrderCharges and validate every
   charge against its parent order.
6. Upsert assets by `file_id`; keep immutable `origin_case_id` and use a
   separate case-asset link for deliberately reused assets.
7. A private-local-only guard that prevents raw LINE context from entering a
   cloud quote fallback.
8. A migration, rollback, and readback plan approved as a separate task.

## Artifacts and stop-loss

- Reference implementation:
  `scripts/maplab_case_id_capture_contract.py`
- Regression suite:
  `tests/test_maplab_case_id_capture_contract.py`
- Private receipt:
  `/Users/pagemacmini/.maplab/margin-leak-audit/20260828-case-id-capture-contract-v1.json`

The receipt writer rejects fields or values outside its structural top-level,
nested contract, and exact per-scenario allowlists; it also rejects raw case-ID
values and invalid timestamps. The receipt contains only synthetic counts,
bounded status codes, static contract text, and hashes. Network, model, Google
write, customer send, price write, historical mutation, and third-party
private-data egress counts are all zero.
If the valid chain ever loses a stage or a negative scenario is accepted, the
adoption status becomes `HOLD` and the next action is contract repair—not a
live change.
