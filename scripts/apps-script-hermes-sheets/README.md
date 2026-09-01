# Hermes-only Google Sheets bridge

This directory is an **isolated Apps Script project** for Hermes. It does not
reuse, copy, or call the legacy quote Apps Script project or its master
spreadsheet.

## Boundary

The HTTP entrypoint accepts exactly two actions:

- `createQuoteShell`: create a new, clean spreadsheet containing verified
  intake facts and an otherwise blank Mina work area.
- `appendQuoteRevisionRequest`: append the customer's requested change to the
  internal revision ledger. The server derives the next revision number.

It cannot quote, calculate, select menu items, confirm availability, confirm a
booking, or make a dietary-safety decision. Unknown actions and unknown payload
keys fail closed.

No deployment or credential is included here. Before a future isolated test,
the deployer must set these Script Properties manually:

- `HERMES_SHEETS_HMAC_SECRET`: a high-entropy shared secret; never commit it.
- `HERMES_REGISTRY_SPREADSHEET_ID`: ID of a dedicated internal registry
  spreadsheet. The script creates/validates `HERMES_SHEET_REQUESTS` and
  `QUOTE_REVISIONS` tabs there.
- `HERMES_QUOTE_FOLDER_ID` (optional): a dedicated Drive folder for newly
  created shells. If absent, Drive keeps the new file in the deployer's default
  location.

The web app manifest allows anonymous HTTP only because authentication is the
application-level HMAC envelope. A missing secret, missing registry ID, stale
timestamp, repeated nonce, invalid signature, or schema mismatch is rejected.

## Signed envelope

Send JSON with exactly these outer keys:

```json
{
  "authVersion": "hmac-sha256-v1",
  "actor": "hermes-sheets-assistant",
  "issuedAt": 1788249600,
  "nonce": "mHQ73mKx8X7YmkVRmA7YwQ",
  "action": "createQuoteShell",
  "signedPayload": "{\"action\":\"createQuoteShell\",...}",
  "signature": "64-lowercase-hex-characters"
}
```

`signedPayload` is the exact JSON string that is signed and later parsed. The
outer and inner `action` values must match. Generate the lowercase hex HMAC over
this exact UTF-8 message (there is no trailing newline):

```text
hmac-sha256-v1
{actor}
{issuedAt}
{nonce}
{action}
{signedPayload}
```

The actor is fixed to `hermes-sheets-assistant`; `issuedAt` is Unix seconds and
must be within five minutes; a nonce can be used only once during the replay
window.

## Inner payloads

`createQuoteShell` uses schema `hermes-line-sheets-assistant-v1`. It requires:

```text
action, schemaVersion, caseId, source, clientName, company, contactRefHash,
businessCategory, eventDate, eventTime, venue, indoorOutdoor, headcount,
serviceFormat, dietaryNotesVerbatim, logisticsNotesVerbatim,
summaryConfirmed, summaryConfirmedAt, summaryText, summaryDigest,
confirmationMessageDigest, confirmationSourceRefHash,
availabilityStatus, dietaryReviewStatus, commercialReviewStatus
```

The three states are fixed to `UNVERIFIED`, `PENDING_HUMAN`, and
`PENDING_MINA`. `summaryDigest` must equal SHA-256 of the exact UTF-8
`summaryText`; confirmation message/source references remain hash-only. The
server uses `(caseId, summaryDigest)` as the idempotency key. Reusing a case ID
with a different summary digest is a conflict.

`appendQuoteRevisionRequest` uses schema `hermes-sheets-revision-v1` and
requires exactly:

```text
action, schemaVersion, caseId, quoteId, source, contactRefHash,
customerChangeVerbatim, changeDigest, changeStatus
```

`changeDigest` must equal SHA-256 of the exact customer text. The caller must
not send `revisionNo`; the server checks the `caseId` to `quoteId` registry
binding and assigns the next positive integer under a script lock. Repeating
the same change digest returns the prior revision as an idempotent success.

## Safety notes

- Every spreadsheet is created with `SpreadsheetApp.create`; no master file,
  hidden item list, formula, prior-client value, or commercial default is
  copied.
- Customer strings are written as plain text and apostrophe-escaped when they
  could be interpreted as a Sheets formula.
- The endpoint returns IDs and bounded status only; it never echoes customer
  text, signatures, or secrets.
- Do not `clasp push` or deploy this project without Owner authorization and an
  isolated synthetic-case readback.
