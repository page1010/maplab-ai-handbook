# MAPLAB Margin-Leak Evidence Join Schema Proposal

Status: `PROPOSAL_ONLY / NO_LIVE_WRITE`

Purpose: make hidden-cost review evidence-based. A customer request, keyword,
filename, or quote pointer is only a review cue. A leakage event is confirmable
only when baseline scope, actual delivery, incremental cost, and charged fee are
joined to the same case.

## Verified live gap — 2026-08-28

The fixed ten-hash bridge read the current Google sources through a local,
read-only worker:

- `SALES_INTAKE`: 45 minimal-field rows; has `case_id`, but the historical LINE
  source hashes do not carry that key.
- `Orders`: 693 minimal-field rows; has `order_id`, but no `case_id` or
  `quote_id` field.
- `OrderCharges`: 184 minimal-field rows; joins to `Orders` by `order_id`, but
  has no source-request or delivery evidence key.
- 2026 quote folder: 159 native Sheets; none of the fixed five 2026 candidates
  had a trustworthy filename identity match.
- `MAPLAB_ASSET_LOG`: has `file_id`, but no `case_id`, `quote_id`, or `order_id`.

Result: zero stable identity chains, zero four-pillar confirmations, and zero
confirmed leakage amount. Receipt:
`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-google-join-bridge-v1.json`
(SHA-256 `c757d2c055b678ee05ba931002ff8732b7f0d5134e041c53eb50b30785e15c4a`).

## Canonical identity chain

```text
source_msg_hash
  -> case_id
  -> quote_id / quote_spreadsheet_id
  -> order_id
  -> charge_id / addon_id / change_order_id
  -> drive_case_folder_id
  -> asset file_id
  -> delivery evidence
```

Names, phone numbers, event descriptions, dates, and filenames may help a
one-time reconciliation, but none is the canonical key.

## Proposed fields

### Local `CONVERSATION_CASE_LINK` shadow registry

Keep this owner-only and local until the pilot is proven:

- `source_msg_id_hash`
- `source_conversation_hash`
- `case_id`
- `link_method`
- `anchor_count`
- `confidence`
- `verified_by`
- `linked_at`
- `evidence_receipt_sha256`

Never copy raw LINE text into this registry.

### `SALES_INTAKE`

Retain `case_id`; propose adding:

- `quote_id`
- `quote_spreadsheet_id`
- `order_id`
- `drive_case_folder_id`
- `scope_version`
- `scope_confirmed_at`

### `Orders`

Retain `order_id`; propose adding:

- `case_id`
- `quote_id`
- `scope_version`
- `scope_confirmed_at`
- `drive_case_folder_id`

### `OrderCharges`

Retain `order_id`; propose adding:

- `charge_id`
- `addon_id`
- `change_order_id`
- `quantity`
- `unit`
- `cost_basis_id`
- `source_evidence_hash`
- `owner_waiver_reason`

### `MAPLAB_ASSET_LOG`

Retain `file_id`; propose adding:

- `case_id`
- `quote_id`
- `order_id`
- `delivery_type`
- `delivered_at`
- `delivery_verified_by`

### `MARGIN_LEAK_EVENT`

Each row must include:

- identity: `leak_id`, `case_id`, `quote_id`, `order_id`, `source_msg_id_hash`;
- scope: baseline version, requested change, classification, waiver reason;
- evidence: quote, delivery, incremental-cost, and charged-fee references;
- economics: labor, admin, material, vendor, equipment, transport, waste,
  target margin, recommended fee, charged fee, unbilled leakage;
- governance: decision status, reviewer, effective date, and receipt hash.

## Integrity rules

1. Do not join by customer name or filename as the final key.
2. Do not infer leakage from a request, quote pointer, public IG post, or model
   output.
3. MAPLAB-caused rework and already-included scope remain non-billable.
4. `confirmed_leakage_amount` stays zero until all four evidence pillars join.
5. Raw customer text, addresses, phone numbers, quote bodies, photos, cookies,
   and credentials remain in the local domain worker.
6. Schema and price changes require a separate approved live-write task; this
   proposal does not authorize modifying Sheets.

## Next bounded experiment: join-first shadow pilot

The conversation-first random sample is now stopped. The next method starts
from evidence-rich 2026 orders instead:

1. Select five `Orders` rows that have a nonblank `client_sheet_url` and at
   least one `OrderCharges` row, using deterministic order-ID hashing.
2. Resolve quote spreadsheet and order charge locally.
3. Search the private LINE archive for the same case using at least two
   independent anchors; raw anchors never leave the process.
4. Write only opaque references, anchor counts, pillar status, and missing
   codes to the owner-only shadow registry.
5. Stop after five. If none has a two-anchor conversation link, do not widen the
   fuzzy matcher; move the repair point to intake-time capture of `case_id`.

Acceptance for the pilot is at least one stable case-to-conversation-to-quote-
to-charge chain, with Google writes, customer sends, model calls, and confirmed
leakage claims all remaining zero until delivery and incremental-cost evidence
are separately verified.
