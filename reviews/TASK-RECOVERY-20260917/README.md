# Homepage delivery recovery — 2026-09-17

Original task: `win01-homepage-golive-20260914`; parent Codex claim, public browser QA subtask. Owner 5307's deployment authorization remains recorded in the original TASK_BRIEF. This follow-up inspects the already-published homepage and creates local evidence only. No WordPress changes, provider calls, external messages, Drive updates, or Owner browser access.

Status: **LIVE_DEPLOYMENT_CONFIRMED / PUBLIC_UI_QA_COMPLETE / FIXES_REQUIRED**. Browser measurements completed at 2026-09-17 08:38 Asia/Taipei. This recovery session did not publish the homepage.

The browser is a dedicated in-memory playwright-cli session. No existing profile, auth storage, extension connection, or Owner Chrome session is used.

## What was actually verified

The public homepage is page **2033**, published, slug `tainan-catering-home-v5`, template `elementor_canvas`, modified `2026-09-16T21:34:01`. Title remains `台南外燴推薦｜台南到府外燴、台南派對外燴與企業茶會｜MAPLAB - MAPLABKITCHEN`; canonical is `https://www.maplabkitchen.com/`. The original task's old bus `blocked` receipt does not describe the current published state.

| Check | 390 × 844 | 1280 × 800 |
|---|---|---|
| Main navigation HTTP | 200 | 200 |
| Document width / horizontal overflow | 390 / none | 1280 / none |
| Full-page screenshot height | 6901 px | 7064 px |
| Actual images after lazy-load scroll | 11 / 11 loaded, real image URLs | 11 / 11 loaded, real image URLs |
| H1 / canonical / draft banner | One H1 / correct / absent | One H1 / correct / absent |
| LINE links | Nine, all `https://lin.ee/IP8nt4n` | Nine, same target |
| FAQ interaction | Three opened and closed successfully | Three opened and closed successfully |

Seven unique internal links were GET-checked at 08:38:52, all HTTP 200: the four scene articles plus inquiry guide, cost guide and custom-menu guide. The first scene link was also actually clicked in the browser; it navigated to `/daxin-art-museum-opening-catering/` with the matching article title, then browser Back returned to the homepage. LINE was checked for target consistency; no message was sent and conversion was not tested.

Visual readback of the actual screenshots shows the hero, raised 900+/2016 cards, four scene blocks, four feedback screenshots, local-scene image, partner logo wall, three quote steps, FAQ and final CTA. There is no duplicated site header/footer or draft banner. No horizontal text/image clipping was observed. The mobile fixed LINE button is present and can overlay part of a card as the page scrolls; no claim is made that every scroll position was exhaustively tested for overlap.

Parent's separate authenticated readback confirms page **1250 remains a draft** with edit/preview actions, not trash; page **2033 is the published static homepage**. See [authenticated-homepage-readback.md](/Users/pagemacmini/claude-daily-operations/reviews/TASK-RECOVERY-20260917/authenticated-homepage-readback.md), observed approximately 08:37. This does not prove byte-for-byte preservation of old content because no immutable pre-deployment baseline was compared.

## Remaining concrete defects and gaps

1. **Published text differs from the approved local file.** The visible quote heading is `怎麼報僺` instead of local `怎麼報價`; step 3 contains `設置佉置` instead of `設置佈置`. Two image alt values contain `茶ꭇ` and `建設甡業`, while the local file has `茶歇` and `建設產業`. The FAQ anchor is `菜單設計 大量例`, while the local source says `菜單設計 20 例`. These were read from live DOM, not inferred from font shapes. Source anchors before this follow-up: `handoff/landing-draft-v2-20260911/index.html:280,296,305,309,324`.
2. **The recorded typography gate is not met.** `skills/site-build-standard-flow.md` step 6 requires text at least 16 px. Live scene body copy is 14.5 px, quote-step copy 13.5 px, scene/text links 12 px, primary CTA copy 15 px and floating CTA 14 px. The raw leaf-element list in `live-results.json` includes computed measurements for some closed-details descendants, so do not treat its count as an accessibility inventory; the listed primary copy measurements were visible in screenshots. This audit does not silently waive the existing gate.
3. **R24's requested navigation entrances are absent.** No live homepage link points to the existing recruitment page `/join-maplab-catering-partner/`, and there is no case/inspiration category navigation. The original brief records these intended entrances. Their content/layout implementation was not part of this read-only QA.
4. **Performance and business effects remain unproven.** Single local browser load timings are diagnostic only; no field CWV, mobile network LCP, improved conversions/rankings, complete CTA analytics, or one-month review execution was established. **MISSING: evidence that the one-month / October 14 reminder already exists.** Preserve Owner's follow-up intent; this session did not create a scheduler or reminder.
5. **Current delivery evidence must replace stale completion labels.** The old `COVERAGE.md` and earlier screenshots are historical checks; this receipt does not claim every R1–R30 requirement is satisfied or that old task-gate hashes remain current after a Task Brief update.

One report-only Google iframe CSP console error appeared during browsing; the two-viewport run recorded no page JavaScript exception. It is not evidence of a failed homepage interaction. FAQ verification initially sampled immediately after clicking, before native toggle state settled; the final run explicitly awaited both open and closed states. Mobile logo verification also waits for a real lazy-load URL rather than accepting the SVG placeholder. Final screenshots and `live-results.json` come from this corrected run.

## Evidence files

- [Mobile full page](live-390-full.png), [mobile hero/cards](live-390-top.png), [mobile quote defect](live-390-quote-section.png), [mobile FAQ interaction](live-390-faq-open.png).
- [Desktop full page](live-1280-full.png), [desktop hero](live-1280-top.png), [desktop quote defect](live-1280-quote-section.png), [desktop FAQ interaction](live-1280-faq-open.png).
- [Machine measurements](live-results.json), [replayable browser QA](live_qa.js), [artifact hashes](artifact-manifest.json).
- Public source endpoint used: `https://www.maplabkitchen.com/wp-json/wp/v2/pages/2033?_fields=id,slug,status,modified,link,title,template,content`. No private REST endpoint was read by this subtask.

The playwright-cli skill supplied the isolated session, browser interactions and screenshot workflow. The repo site-build SOP supplied the 390/1280 and typography checks; its stale pre-publication gate is superseded by Owner 5307's recorded instruction, not a reason to ask for approval again. No site-build task-gate file was rewritten during this read-only verification. The named anonymous browser session was closed after QA. Artifact manifest validation passed for all ten measured files; the Task Brief contains only the new eleven-line preface and preserves the complete prior HEAD text.

## Scoped checkpoint

After the QA-only pass, the parent authorized a local scoped commit and a `ready` checkpoint of the existing claim, not `complete`. Only this receipt directory's explicit evidence files and the Task Brief preface are included; unrelated dirty files and transient `.playwright-cli` files are not staged. Nothing is pushed. The run-governance-brief evidence rules inform this handoff: existing deployment is verified, overall acceptance remains AMBER / fixes required, and reminder registration remains missing. No product-direction, `CURRENT_STATUS.md`, scheduler or pitfalls edit was authorized or made.

Highest-value next bounded action: reconcile page 2033's five text/alt differences against the approved local HTML, fix those exact defects in the existing page under the original Owner 5307 authorization, and retake targeted public screenshots; then address the typography/navigation acceptance gaps. This subtask itself does not perform the WordPress writes.

## Resume Prompt

1. Continue original task `win01-homepage-golive-20260914`; do not create another homepage or task identity.
2. Read this receipt and the complete original landing TASK_BRIEF, especially Owner 5307.
3. Page 2033 is already the live static homepage; page 1250 is retained as draft.
4. Revalidate live state immediately before any later mutation.
5. Preserve the approved positioning, source images, raised cards and old-homepage draft.
6. Next bounded action: reconcile published text against local canonical HTML and correct the identified characters, then retake targeted screenshots.
7. Address the documented text-size gate and R24 navigation gap in the existing page, with current scope and concrete acceptance.
8. Update the original bus/claim delivery status using actual receipt evidence; do not infer completion from a worker exit.
9. Preserve October 14 performance-review intent and distinguish a recorded date from a registered reminder.
10. No new publishing permission is needed for the already-authorized original deployment; any new scope still follows its own authorization.
11. Do not invoke `landing_v5_preview.sh` as a local-only command: it also updates Drive.
12. This subtask changed only this evidence directory and the Task Brief's new continuation pointer; the subsequent authorized scoped checkpoint creates a local commit only. No WordPress writes, external sends or push.
