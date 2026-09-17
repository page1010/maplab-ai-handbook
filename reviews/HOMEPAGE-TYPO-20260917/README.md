# Homepage two-character correction — 2026-09-17

- Executor: Codex / Mac mini; original task `win01-homepage-golive-20260914`.
- Scope: Owner's two circled screenshot typos only. No redesign, new page, price changes, customer messages, credential export, or homepage reassignment.
- Result: **LIVE_TWO_TYPOS_VERIFIED**. Page 2033 remains published at https://www.maplabkitchen.com/.

## Exact change

| Before | After | Matches before |
| --- | --- | --- |
| 怎麼報僺 | 怎麼報價 | 1 |
| 付訂保留檔期，活動當天我們提前到場設置佉置。 | 付訂保留檔期，活動當天我們提前到場設置佈置。 | 1 |

Approved local source: `handoff/landing-draft-v2-20260911/index.html:305,309`, already correct and therefore not overwritten. The authenticated WordPress page list identifies 2033 as the static homepage and 1250 as retained draft.

## Actual execution and verification

1. Opened a dedicated authenticated Chrome tab, page 2033's WordPress code editor. Read the existing HTML field rather than replacing it with the local file.
2. Both exact preconditions matched once. After replacement, the complete editable value matched the expected patch: length 15193 before/after, exactly **2 changed characters**, both old phrases absent. No CSS, markup, URLs or other copy changed in the submitted value.
3. Clicked Save once. WordPress displayed **頁面已更新。**
4. Fresh independent public browser readback showed the corrected H2 and full STEP 3 sentence. Visually inspected screenshots at 390×844 and 1280×900; both showed corrected text and `horizontalOverflow=false`. Screenshots are in this Codex turn's tool evidence, not claimed as local PNG artifacts.
5. Public REST readback at approximately 2026-09-17 16:02 +08:00:

```json
{
  "id": 2033,
  "slug": "tainan-catering-home-v5",
  "status": "publish",
  "modified": "2026-09-17T16:00:59",
  "link": "https://www.maplabkitchen.com/",
  "template": "elementor_canvas",
  "content_chars": 15790,
  "correct_heading": true,
  "correct_step3": true,
  "old_heading": false,
  "old_step3": false
}
```

Read-only replay endpoint: `https://www.maplabkitchen.com/wp-json/wp/v2/pages/2033?_fields=id,slug,status,modified,link,template,content`. Check rendered content contains `<h2>怎麼報價</h2>` and the complete corrected sentence, and does not contain `怎麼報僺` or `設置佉置`.

## Boundaries / tool notes

- Impeccable's scoped-copy workflow preserved the existing approved wording and visual design; Playwright-backed UI readback verified actual publication rather than local-only content.
- Mechanical detector on the unchanged approved local HTML returned `[]` in **DEGRADED regex mode** (parser modules absent). This is not full design/contrast acceptance.
- Optional in-app content export was unsupported. Optional post-reload editor field evaluation timed out twice; no second write or retry Save was made. Therefore post-save proof is WordPress's success message plus independently read public DOM and REST, not an asserted post-reload raw-editor byte equality.
- The earlier alt-text anomalies, FAQ/local difference, font-size gate and R24 navigation findings remain outside this screenshot fix. No claim of complete homepage QA, SEO improvement or conversion lift.
- Do not replay the old QA script unchanged: it locates `怎麼報僺`; use the corrected H2 for future checks.

## Resume Prompt

Continue the original homepage task, not a duplicate project. These two screenshot typos were saved once and live-verified on 2026-09-17; do not repeat their edit. Read this receipt and `reviews/TASK-RECOVERY-20260917/README.md`, then refresh the live page before selecting one remaining original acceptance gap. Preserve page 2033, page 1250's draft, Owner 5307 authorization and October 14 review intent. The present request is complete; broader homepage acceptance remains open.
