# 外燴預擺資料整理 — first-batch receipt

- Task: `T-A4-PRELAYOUT-SIMULATOR-001`
- Date: 2026-09-18; local private collection only.
- Outcome: `FIRST_BATCH_VERIFIED / COLLECTION_INCOMPLETE / SIMULATOR_NOT_IMPLEMENTED`.
- Private entry: `/Users/pagemacmini/Documents/MAPLAB_外燴預擺/README.md`.
- No source photo/album/Sheet modifications, cloud publication, customer message or model egress.

## Verified outputs

11 layout/equipment-configuration images + 1 equipment close-up, each with a same-name Markdown detail note. One extra Google Photos page rendition is a separate evidence variant, not another photo in the count. Original source-copy hashes match 12/12. Private directories are 0700; private files 0600.

Four historical images have EXIF capture dates; seven historical images do not. Three of those have separately labelled 2025 estimates, not promoted into confirmed date fields. The new Owner example has a verified live Photos date and filename, but no downloaded original EXIF. Same-name local original was visually rejected as a different image; adjacent image was rejected as non-menu evidence.

Four quote readbacks / 37 menu items retained only in the private folder. Food-piece totals 180 and 240 recompute exactly. Guests, servings, food pieces, tabletop values and unspecified units/counts are separate. All four photo↔quote joins remain candidates.

Machine catalog has 44 proposed visual labels (not 44 distinct SKUs), zero measured/fit-eligible equipment items. A measurement/de-duplication worksheet and next-step instructions are included. Recent backup 472 files is metadata-only and unreviewed; full album coverage is not claimed.

## Actual validation

Command: `rtk proxy python3 -m unittest discover -s tests -p 'test_prelayout_collection_report.py' -v`

Result: **6 tests, OK, 0.002s**. Tests cover unknown-year non-promotion, album-vs-EXIF distinction, external links, path escape rejection, atomic private idempotent output, and hash/duplicate fail-closed behavior.

Command: `rtk proxy python3 scripts/prelayout_collection_report.py --root /Users/pagemacmini/Documents/MAPLAB_外燴預擺`

Result: **PASS**, 12 primary images, 11 layout/configuration, 1 reference, 12 matching source hashes, 4 EXIF-dated, 1 album-dated, 4 candidate quotes, 0 confirmed joins, 0 measured equipment.

Second full report build: **all 35 private output/source files content hashes and mtimes unchanged**. Independent local read-only reviewer verified hash/bytes/pixels and private file modes; no blocking inconsistency. Live quote values were separately read through the existing readonly Google helper; no OAuth token rewrite.

Private validation receipt SHA-256: `fa5cebb81a9c445fe4135b0c89159a6f2886fdb8af4e59be3ba7a042303cc6ed`.

## Resume

Use Task Card's Next Bounded Action: review at most 25 unreviewed recent event-backup files, retain originals and source provenance, and strengthen candidate case joins. Do not repeat the already rejected same-name-file match. No fit claim until real measurement. All private image paths, quote data and menu details stay outside Git.
