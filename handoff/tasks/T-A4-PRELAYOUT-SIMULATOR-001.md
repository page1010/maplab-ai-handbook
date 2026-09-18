# T-A4-PRELAYOUT-SIMULATOR-001 — 外燴預擺照片、器具與桌面模擬

- **狀態**: 🔄 進行中 — FIRST_BATCH_VERIFIED / COLLECTION_INCOMPLETE / SIMULATOR_NOT_IMPLEMENTED
- Owner request: 2026-09-18，本 Codex thread。找 Mina 相簿預擺照片，從原始檔推敲年份，對照報價單人數與餐點；同類照片集中、核對命名與細節說明，為器具模擬系統建立可靠資料。
- Scope: historical + recent records; local private copies only. Do not rename/move/delete originals, modify Sheets, publish, send customer messages, or send private data to third-party models.
- Code/control root: canonical MAPLAB repo. Private photo/catalog root: `/Users/pagemacmini/Documents/MAPLAB_外燴預擺` (local, outside Git).

## Acceptance

1. Visually confirmed pre-layout photos copied into one discoverable folder with source URL/path, original filename, hash, date evidence, quote match confidence and missing fields.
2. Capture date and event date remain separate; dates from renamed year buckets are not EXIF proof. Ambiguous candidate quotes remain candidates.
3. Equipment catalog distinguishes photo-observed type, measured dimensions, stock count and dish capacity. Unknowns remain null, not invented.
4. Local table-size simulator: real catalog, proportional placement, collision/boundary checks, menu assignment, save/reopen; dimensional confidence displayed.
5. Tests, source coverage, remaining gaps, and Resume Prompt retained; no claim of complete collection without denominator.

## Current evidence

- Mina Google Photos account verified in Owner Chrome (2026-09-18).
- User reference photo found in live Mina Photos: `IMG_3327.JPG`, photo date 2026-09-15 12:28:32, 1587×1031, original-quality backup. Overlay says 9/16 B 下午茶敘 180.
- Candidate quote live readback: 2026/9/16 afternoon tea, at most 30 guests, 180 food pieces. Image-to-quote join still under cross-check; never call 180 guest count.
- Historical A4 index covers 2022–2025, not fresh 2026. Ten historical empty-layout/equipment-configuration photos and one close-up were visually reviewed and copied. Plus the Owner reference derivative: 11 layout/configuration photos + 1 equipment close-up, 12 primary photos total.
- Four historical files preserve EXIF capture dates (3 in 2023, 1 in 2025); seven remain unverified-year. H002/H004/H005 have explicitly labelled 2025 inferences supported by quote/date/event clues. N001 is dated by the live Photos UI, not downloaded-original EXIF.
- Live original download was blocked by client; local Takeout same-name IMG_3327.JPG is a different image. Only Owner attachment and separately labelled page rendition are saved for N001. Adjacent IMG_3326 is receipts, not menu-label evidence; excluded.
- Four live quote readbacks / 37 menu entries retained locally. Photo joins are all candidates, not confirmed identities. 180/240 food-piece sums verified; headcount vs servings, units and table count remain separate.
- Private entry: `/Users/pagemacmini/Documents/MAPLAB_外燴預擺/README.md`; each photo has same-name details; quotes, machine-readable catalog, hash evidence and measurement worksheet included.
- Receipt: `reviews/PRELAYOUT-20260918/receipt.md`. Six unit tests PASS; 12/12 source-copy hashes verified; idempotent report rerun PASS. Private data/photos are outside Git; only code and redacted handoff/receipt are committed.
- Equipment families are visual labels only (duplicates possible), zero measured inventory items. No simulator or scale/fit guarantee yet. Recent June–July backup 472 files is metadata-only, unreviewed/un-deduplicated, not claimed complete.

## Next Bounded Action

Review one bounded batch (up to 25 files) from the existing June–July 2026 event-backup folders for actual empty equipment pre-layouts. Preserve originals, use EXIF/Takeout sidecars for year evidence, add only visually confirmed copies by hash, and update the private source manifest plus report. Independently resolve the strongest H002/H004/H005 case match using original-photo metadata or order/event keys; do not rerun broad searches or treat all 472 files as relevant. Do not retry the rejected same-name N001 original or adjacent receipt photo. UI preference does not block data collection; no new simulator UI in this checkpoint.

## Resume Prompt

Read this card, CURRENT_STATUS.md, pitfalls.md, docs/a4/source-of-truth.md and skills/photo-asset-retrieval-guide.md.
Open `/Users/pagemacmini/Documents/MAPLAB_外燴預擺/README.md` and `資料/verification.json` first; 12 primary copies are already verified.
Do not re-download or re-label the same batch. Four EXIF dates are verified; seven historical years remain unknown; three have labelled 2025 inferences.
N001 is the Owner's 9/16 B afternoon-tea image. Photos displays IMG_3327.JPG and 2026-09-15 12:28:32 +08; original bytes remain missing.
Takeout same-name IMG_3327.JPG is a different picture. Adjacent IMG_3326 is not menu evidence. Exclusions are durable.
Candidate quote says at most 30 people / 180 food pieces; other cases also separate servings and guests. All four image joins are still candidate.
Use the next bounded batch above, not a new architecture or full-library download. Keep all private images and raw quote data local, no DeerFlow/OpenRouter.
Refresh private generated handoff with `rtk proxy python3 scripts/prelayout_collection_report.py --root /Users/pagemacmini/Documents/MAPLAB_外燴預擺` after curated source updates.
Run `rtk proxy python3 -m unittest discover -s tests -p test_prelayout_collection_report.py -v`, verify hashes and report idempotence, then update receipt.
Simulated fit requires measured equipment footprint, height, shelf area and current stock; none yet measured. Do not infer from perspective photos or a shopping screenshot.
No cloud publication, source-file mutation, customer messaging, or unapproved data egress. Continue this task, not stale SEO/LINE work.
