# MAPLAB private-root and deployed-readback hardening plan

## Status

- Evidence time: `2026-08-27T23:05:41.090374+00:00`
- Status: `STATIC_DESIGN_INVENTORY_VALIDATED`
- Live adoption: `HOLD`
- Method: `margin-private-root-deployed-readback-plan-v1`
- Method fingerprint: `fa7086a124459dfa1ca3c872be7e4247d0e490e85dcc2e0ec3838626586bdde2`
- Private receipt: `~/.maplab/margin-leak-audit/20260828-private-root-readback-plan-v1.json`
- Receipt mode contract: parent `0700`, file `0600`

This is a no-write hardening design, not a completed migration. It inventories
the current consumers and unsafe modes, defines fail-closed cutover/readback/
rollback contracts, and validates 39 policy predicates with generated states.
It does **not** validate a working resolver, copy ledger, cross-filesystem
rename, crash recovery, or concurrent cutover runtime. It did not
move or chmod a live target, restart a service, use a credential, call Google,
deploy Apps Script, read customer rows, or change a customer-facing system.
Only the private evidence receipt was atomically written and permissioned.

## Plateau review and method change

The prior three method fingerprints are distinct:

- `a1573a74b88222ae10c2b8edcbeaa9c7bdf2f139596df6be6c33db7b2bea2123`
- `201cf84e8090c12ba743f47f9073dc733a87dd7a57874729b6ce302e4c627133`
- `d282b0fee8655a3cbc075bc332c0eb9ab2e5f18bac05abefdb7d63f97c5f53c0`

This bounded action did not rerun the prior deployment inventory. It changed
the repair point to a consumer-complete private-root migration contract and a
version-bound Apps Script readback design. There is no claimed live
improvement. The next experiment must remain synthetic until the resolver and
copy-ledger prototype passes its fixed holdout.

## Current facts

| Surface | Bounded current observation | Consequence |
|---|---|---|
| Case Store | Directory `0755`; database and fallback `0644`; repo-contained | Not owner-only; do not call it hardened |
| `bot_a6` environment | Parent `0755`; file `0644`; repo-contained | Secrets/config remain exposed to local users allowed by mode |
| Provider credentials | `free_compute.env` is `0600` under a `0755` `.maplab` parent; a setup writer copies the key into `.hermes/.env` under `0700/0600` | Two secret authorities plus an unsafe source parent require one sealed authority and removal of the copy writer; payload was not read |
| Hermes LINE training | Mode-only inventory: root `0700`, 4 child directories at `0700`, 38 files at `0600`, no symlinks | Current `owner_only` remains false until effective UID, ACL, regular type, hardlink and runtime binding are read back; modes alone are not proof |
| OpenClaw review | 44 adapter bundles, 352 adapter artifacts at `0644`; shared `workbook/reviews` namespace | A wholesale move would mix private adapter evidence with unrelated review jobs |
| OpenClaw legacy seals | 44/44 manifests untrusted, 116 manifest mismatches, 44 terminal logs and 44 routing outputs outside the legacy seal, 44 physical bundle-path and 44 review-path embeds | Migrate from actual bytes and a new ledger, never from the old manifest as truth |
| Telegram dispatch | Separate live root, 21 packet directories, 83 files at `0644`, 43 tracked; launcher has no owner-only umask | Must use a separate private root and launcher contract from OpenClaw review |
| Temporary clipboard | `/clip` currently has no file, but code still targets a system-temp file and the Extension reads it | Absence now is not a safe architecture; replace with single-use loopback or owner-only generation and no temp fallback |
| Scheduled backup | 8 generations contain 48 env-like, 16 Case Store, 3,240 shared-review fixed artifact, 600 dispatch and 8 backup-index copies at `0644` (3,912 classified private copies); 2 stale worktree copies remain | The review total includes 2,816 adapter and 424 non-adapter copies; a root migration alone would be undone by the next scheduled backup |
| Shared Google token | Grandparent/parent `0755`, token `0644`; 19 tracked-repo + 4 known external consumers | Three external source files match by hash; secret-bearing `.mcp.json` is metadata-only/unread, so live cutover consumer truth remains incomplete |
| Installed service files | A6, backup, Telegram and Hermes LINE-training LaunchAgent files match pinned source copies at `0644` | Runtime binding was not read back; file match is not a live cutover proof |
| `~/.clasprc.json` | `0644` | Explicitly excluded from readback; do not use clasp for this proof |

The inventory pins 67 source files and 62 consumer anchors across Case Store,
bot environment, provider credentials, Hermes LINE training, OpenClaw review,
Telegram dispatch, backup, and GAS binding surfaces. It also records 23 known
shared-token consumers and four installed LaunchAgent files. A separate
tracked-source scanner exactly accounts for the 10 active provider-key/training-
root references and reads no private payload.
Every tracked-repo Google consumer and every repo consumer anchor is covered by
the source-pin manifest; path presence alone is not accepted as drift proof.
These are bounded current manifests, not
a claim that an undiscovered future process cannot exist.

## Root contracts

All target roots are external to the repository, directory mode `0700`, file
mode `0600`, symlink-free, owned through the full parent chain by the effective
user, regular-file-only, hardlink-free, and free of ACL entries. Modes alone do
not prove ownership. The resolver must validate both logical surface and
generation; callers must not learn or persist a physical path.

### Case Store

- Introduce one compatibility resolver before changing data.
- Quiesce the authoritative writer; no constructor may silently create schema
  or fall back to a stale seed during migration.
- Copy SQLite with `Connection.backup()`, then verify `quick_check`, schema,
  row counts, and logical-table hashes.
- Verify the fallback JSON with an exact digest.
- `fsync` file and parent, atomically publish the generation, then perform an
  environment-path compare-and-swap and supervised restart.
- Before the first new write, rollback may restore the old configuration. After
  the first new write, the external generation remains authoritative and the
  system forward-repairs; it never resumes writes to a stale repo database.

### `bot_a6` environment

- Replace shell `source` with a strict parser and an allowlisted key set.
- Pass only a logical external config locator through launchd.
- Read back key names and redacted value fingerprints, then verify service
  health. Never emit values or pass a token on the command line.
- Roll back only to a prior sealed external generation; never restore a repo
  `.env` path.

### Provider credentials

- Treat `free_compute.env` and `.hermes/.env` as two current authorities, not
  as harmless copies. This inventory reads only existence and mode metadata.
- Source-pin the active gateway direct reader, inherited task/DeerFlow
  consumers, and `hermes_gateway_setup.sh` copy writer. Unexpected tracked
  references fail the manifest gate.
- Pin the OpenRouter YAML key placeholder, endpoint and ZDR/data-collection
  policy as a provider-credential consumer. The local provider YAML and
  disabled-extension registry are also source-pinned and consumer-anchored so
  the bridge cannot silently drift to a different runtime config.
- Replace the setup copy with one sealed external authority and
  consumer-scoped projections. Read back key names and redacted fingerprints,
  never values; require zero duplicate authorities before cutover.
- Before refresh, rollback may select the prior sealed generation. After
  refresh, forward-repair consumers and never fall back to the `0755` parent.

### Hermes LINE training root

- Preserve the current private-data boundary; do not copy its 38 files into the
  repository or any cloud provider. Do not call the current root owner-only
  until effective UID, ACL, regular-type and hardlink checks also pass.
- Patch the loop, supervisor, A6 task executor, both A6 plist copies, the
  scheduled source plist, and the installed LaunchAgent to a generation-bound
  logical locator.
- Read back root/child mode histograms, symlink count, and all source plus
  installed runtime bindings. File-mode evidence alone is not runtime proof.
- Rollback switches to a prior sealed owner-only generation; it never uses a
  repo or cloud fallback.

### OpenClaw review and Telegram dispatch

These are three roots, not one migration:

1. Adapter review bundles move through a signature-scoped logical locator.
   Reject traversal, symlinks, duplicate job IDs, and non-exclusive creates.
   Create an actual-byte migration ledger. Seal only after terminal output,
   routing, and A5 post-processing are final.
2. Live Telegram dispatch packets use a separate root and an owner-only
   launcher umask. New writes must be external-only; repo fallback is forbidden.
3. The 53 current non-adapter fixed-name artifacts are classified private too.
   Move them through a separate shared-review logical locator with an
   actual-byte ledger, and require all future classified fixed-name writes to
   be external-only. Its readback must account for all 53 current artifacts;
   rollback switches only its sealed generation and never restores private
   bytes to the repo. The two current concrete writers
   (`tools/wp_rankmath_recovery.py` and `tools/google_reindex_submit.py`) are
   source-pinned and consumer-anchored; either must be patched before cutover.
4. `/clip` must leave the system-temp path. The replacement is single-use,
   expiry-bounded, owner-only, and has no temp-file fallback.

The shared `workbook/reviews` namespace may remain only for non-private control
and reference files. Adapter artifacts and all 53 classified non-adapter fixed
artifacts leave it. Rollback switches a logical generation; it never writes
private artifacts back to the repository.

### Backup policy

Before retiring any source path, change the scheduled backup allowlist across
all three backed-up roots. The zero-sensitive gate covers every non-example env
file, Case Store database/fallback, all shared-review fixed artifacts, entire
Telegram dispatch root, and backup index—not only four suffixes. The first
post-change index must report zero classified repo paths and an owner-only
private snapshot. Historical deletion or credential rotation is destructive/
external work and is not authorized by this plan.

### Shared Google credential

- The tracked-repo scan uses `git grep` path output only; it does not read
  ignored `.env`, histories, databases, photos, or runtime JSON.
- Three external Python consumers are source-code hash reads. The secret-bearing
  `.mcp.json` consumer is existence/mode metadata only; its current payload is
  deliberately unread, so live cutover consumer truth remains incomplete.
- Before any refresh write, rollback may select a prior sealed external
  generation. After a refresh, the new external credential remains
  authoritative and consumers are forward-repaired; never fall back to the old
  unsafe token.
- The Apps Script readback credential is a different dedicated profile. Shared
  token scope expansion is forbidden.

## Apps Script deployed-source readback

Local `.clasp.json` binding, git history, source checkout, and Apps Script HEAD
are not current deployed truth. The future readback profile must be a dedicated
credential with exactly these scopes and no broader/write scope:

- `https://www.googleapis.com/auth/script.deployments.readonly`
- `https://www.googleapis.com/auth/script.projects.readonly`

For each verified current target, exactly three GET calls are planned:

1. `projects.deployments.get` obtains the deployment configuration and version.
2. `projects.getContent(versionNumber)` reads that exact deployed version; an
   omitted version is HEAD and is rejected.
3. Canonicalize in memory as `api-canonical-tree-v1`: sort by type/name and hash
   exact name, type, and source bytes.
4. Read deployment metadata again and require version/update metadata to be
   unchanged, closing the time-of-check/time-of-use gap.
5. Persist only salted target hashes, file-name/source hashes, counts, and the
   canonical tree hash. Persist no raw source, raw target identifier, URL, or
   credential payload.

The transport allowlist is GET-only, write methods are empty, the shared Google
token is excluded, and clasp is excluded. Official API semantics:

- [Apps Script `projects.deployments.get`](https://developers.google.com/apps-script/api/reference/rest/v1/projects.deployments/get)
- [Apps Script deployments resource](https://developers.google.com/apps-script/api/reference/rest/v1/projects.deployments)
- [Apps Script `projects.getContent`](https://developers.google.com/apps-script/api/reference/rest/v1/projects/getContent)

Current quote deployed revision remains unresolved. The declared LINE checkout
and current binding remain unresolved. Direct GAS webhook handling does not
prove signature-header authority, so LINE remains Phase 0 until a header-capable
ingress is proven.

## Adoption sequence

| Gate | Bounded action | Required proof before next gate |
|---|---|---|
| G0 | Freeze manifests and immutable source snapshots | Pinned source/consumer hashes and quiescence plan |
| G1 | Build a real TemporaryDirectory logical resolver and actual-byte ledger prototype | Distinct/non-overlapping roots plus traversal, ancestor symlink, hardlink/FIFO, duplicate job, `O_EXCL`, interrupted copy, `EXDEV`, fsync, concurrent writer, generation CAS and rollback execution tests pass |
| G2 | Patch backup exclusions in a fixture only | Next synthetic index contains zero sensitive repo paths |
| G3 | Dry-copy fixture DB, fallback, env, review and dispatch bundles | Exact digest, SQLite integrity/schema/count/hash, modes and redacted paths pass |
| G4 | Build dedicated Apps Script readback fixture | Exact scopes, GET-only, version binding and double-read tests pass |
| G5 | Owner-reviewed live migration window | Explicit authorization, cost/credential boundary, rollback rehearsal |
| G6 | Live cutover one surface at a time | Independent readback receipt before the next surface |

G5 and G6 are not authorized by this document. Deletion of old copies,
credential rotation, service restart, live readback, and deployment require the
appropriate later gate.

## Fixed acceptance and stop-loss

The validator currently passes 39/39 generated policy-gate fixtures. These are
predicate tests, not resolver/copy-ledger runtime proof. They reject repo
targets, `0755`/`0644`, bool-as-int modes, symlinks, wrong owner UID, non-regular
types, hardlinks, parent-owner drift, ACL entries, consumer gaps, digest or
readback mismatch, stale manifest trust, backup propagation, repo fallback,
physical-path leakage, active writers, shared/broad credentials, missing scope,
HEAD-only reads, raw source/identifier persistence, API write methods, direct
GAS LINE authority, deployment drift, historical-only targets, and non-GET
transport.

Stop immediately on any private third-party egress, credential/environment
payload read, customer-row read, target chmod/copy/move/restart, API call,
deployment write, customer send, or pricing-system write. The only write in
this bounded action is the hash-safe owner-only receipt.

## Next bounded action

Build a synthetic-only resolver and copy-ledger prototype covering Case Store,
`bot_a6` config, OpenClaw review, Telegram dispatch, and backup exclusions. It
must use generated fixtures only, preserve the current holdout, and make no
live path, process, API, credential, or customer-data change.
