# Prospective case-ID live capture — Owner review

Status: `PROPOSAL_ONLY / NO_LIVE_WRITE`

## Why this decision is now required

The fixed-three historical experiment froze three candidates before reading any
case evidence. All three request rows and source conversation hashes were
verified, but none had an exact, unique chain to approved quote content,
delivery assets, actual incremental cost, and authoritative charged-fee
evidence. The result is 0/3 verified cases and confirmed leakage remains 0.

This closes the historical-join branch. A fourth case, broader name/date match,
more keyword rules, or another infrastructure round would not create the
missing foreign keys. The smallest next real-world step is to capture those
keys when a new request enters the system.

## Proposed shadow-capture contract

Create one opaque, non-PII `case_id` once at verified intake and propagate it
without regeneration through these records:

| Stage | Required immutable keys | Evidence written |
|---|---|---|
| Header-capable LINE ingress | `source_event_id_hash`, `case_id` | signature/readback status and request-row hash |
| Local Case Store and `SALES_INTAKE` | `case_id` | request category, baseline-scope state, acknowledgement IDs |
| Quote revision | `case_id`, `quote_id`, `quote_revision` | approved quote body hash and included/excluded scope |
| Order | `case_id`, `quote_id`, `order_id` | accepted revision and status |
| Actual-cost ledger | `case_id`, `cost_event_id` | actual labor, admin, material, vendor, equipment, transport, or waste cost |
| Delivery / `ASSET_LOG` | `case_id`, `asset_id` | delivered artifact hash, delivery time, and readback status |
| Charge ledger | `case_id`, `order_id`, `charge_id` | authoritative charge semantics, amount, currency, and lifecycle status |

`OrderCharges` cannot be treated as charged revenue until its semantics are
made explicit. The proposed enum separates `customer_charge`, `discount`,
`refund`, `internal_cost`, and `note`; lifecycle separates `proposed`,
`approved`, `invoiced`, `paid`, and `waived`. Only an authoritative same-case
customer charge with valid direction, currency, and status may satisfy the
charged-fee pillar. A missing or partial row never means zero.

## Proposed production path

```text
LINE webhook
  -> header-capable ingress validates x-line-signature + untouched raw body
  -> replay-bounded signed internal envelope
  -> local Case Store mints/reads immutable case_id in one transaction
  -> durable append-only outbox
  -> SALES_INTAKE -> quote revision -> Orders/OrderCharges -> ASSET_LOG/cost ledger
  -> exact readback receipt at every hop
```

Direct Apps Script Web App ingress remains ineligible because its event object
does not expose the header needed for LINE signature verification. The live
writer for `Orders` / `OrderCharges` also remains unresolved. Both must fail
closed before a production canary.

## Shadow-pilot boundary

- Future cases only; no historical backfill by name, date, content, or fuzzy matching.
- Fixed 10-case canary or 14 calendar days, whichever comes first.
- Capture evidence and compute proposal-only leakage; do not change quoted
  prices, customer messages, invoices, or payment status.
- No customer sends, public publishing, new third-party private egress, or
  DeerFlow/OpenRouter access to customer, quote, order, asset, or browser data.
- Raw payloads remain in the local owner-only domain. Repo receipts contain
  only opaque hashes, status, missing codes, and aggregate counts.
- Every write is idempotent on source event / case / revision / charge IDs and
  receives an exact live readback before the next hop is allowed.

Acceptance for the shadow pilot:

1. 10/10 cases have one immutable `case_id` from signed ingress through every
   record actually created for that case.
2. Restart, duplicate delivery, delayed retry, and two-writer races do not mint
   a second case or charge.
3. At least one case can be evaluated from exact request, approved baseline
   quote, delivery, actual-cost, and charged-fee evidence without using a name
   or date join.
4. Missing evidence remains `INSUFFICIENT_EVIDENCE`; no amount is inferred.
5. Owner can inspect a private case packet and a sanitized receipt before any
   pricing/product decision.

## Rollback and readback

Before implementation, take versioned schema/source snapshots and pin deployed
revision hashes. Additive fields are introduced behind a disabled feature flag.
The canary is enabled only after static tests, synthetic signed-ingress tests,
and read-only deployed-source verification pass.

Rollback disables the new ingress/outbox writer and returns readers to the
previous path. It does not delete captured events, rewrite old rows, remove
columns automatically, or regenerate IDs. Any write after the publication
boundary is repaired forward from the append-only outbox. A rollback receipt
must prove the feature flag, deployed revisions, writer state, and live row
readback; process exit or HTTP success alone is not proof.

## Owner choices

1. **Approve shadow implementation (recommended):** authorize a separate,
   bounded task to implement the 10-case / 14-day capture canary, including
   the necessary live Sheet/GAS schema and header-capable ingress changes.
   Prices, customer sends, publication, historical backfill, and deletion stay
   prohibited.
2. **Approve local-only rehearsal:** build and test the signed ingress,
   Case Store, outbox, and synthetic downstream adapters without changing live
   Sheets/GAS. This lowers deployment risk but cannot prove an end-to-end live
   evidence chain.
3. **Defer:** preserve this proposal and stop the hidden-cost historical audit.
   No more cases, fuzzy matching, or infrastructure rounds run until priority
   changes.

No option has been executed by this proposal.
