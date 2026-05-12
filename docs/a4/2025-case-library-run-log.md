# A4 2025 Case Library Run Log

## Purpose

Build a desktop-only 2025 case material library from fact-first asset matching.
The goal is to give A2/A3 a usable local folder of verified case素材 without committing private customer photos or internal quote evidence to GitHub.

## Output

- Local desktop folder: `/Users/pagemacmini/Desktop/2025案例`
- Local preview page: `/Users/pagemacmini/Desktop/2025案例/index.html`
- Local manifest: `/Users/pagemacmini/Desktop/2025案例/case_manifest.json`
- Local review bundle: `workbook/reviews/JOB-2025-CASE-LIBRARY/`

## Generated Case Structure

The local folder is split by SEO audience and scene:

- `ToB/會議茶點`
- `ToB/企業茶會`
- `ToB/開幕茶會`
- `ToB/品牌活動_建案`
- `ToC/生日週歲派對`
- `ToC/家庭聚會_入厝`
- `ToC/性別揭曉派對`

Each case folder contains:

- `assets/`: downloaded source assets from Drive.
- `previews/`: JPG previews converted for quick review.
- `internal_evidence.md`: internal-only evidence chain with quote sheet and Drive links.
- `public_case_notes.md`: public-safe notes for WordPress/ad drafting.
- `case_manifest.json`: structured case data.

## Method

1. Run the A4 fact-first matcher:
   `python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 500`
2. Build the desktop library:
   `python3 tools/ai_workbook/cli.py case-library-2025 --max-assets-per-case 12`
3. Render-check the local HTML with headless Chrome.

## Account Provenance

- Drive API auth used by Codex: `pagewu1010@gmail.com`.
- `MAPLAB_ASSETS` folder owner: `MINA CHUANG <lb99104@gmail.com>`.
- Selected image files checked in Drive are owned by `MINA CHUANG <lb99104@gmail.com>`.
- Local quote sheet mirror used by the matcher: `/Users/pagemacmini/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/外燴 訂單`.

Interpretation: the photos are Mina-owned Drive assets, accessed through Page's Drive API permission. The quote sheets are read from Mina's local Google Drive sync folder.

## Google Photos Cross-check Path

Google Photos is treated as a secondary visual supplement source, not the primary fact key.

Use the date key from `case_manifest.json`, open Google Photos in Chrome, and search by date/event term. Any extra photos found there should be saved as candidates under the matching case folder, for example:

- `google_photos_candidates/`
- `google_photos_crosscheck.md`

Only promote those photos into the public case set after human visual QA.

## Public Safety Rule

Do not commit copied photos, private quote details, phone numbers, private addresses, or local customer evidence.
GitHub should preserve the method and governance trail; the desktop folder is the private working set.

## QA Notes

- High-confidence cases use Drive photo metadata date + quote sheet date + TimeTree/event signal + ASSET_LOG SEO/OCR fields.
- Cases with multiple same-day events must still receive human visual QA before WordPress use.
- A case with fewer than three assets should be treated as a placeholder until more素材 is found.
