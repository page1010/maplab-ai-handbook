# Creative prototype tool matrix

Verified from first-party or upstream sources on 2026-08-27. Recheck availability, terms, region, and account state at execution time.

| Tool | Use now | Best fit | MAPLAB boundary | Primary source |
|---|---|---|---|---|
| Impeccable 4.1.2 | yes, pinned skill without hooks | frontend critique, design system, accessibility, responsive polish | local brand/visual specs win; external assets and publishing stay gated | https://github.com/pbakaus/impeccable |
| Google Stitch | conditional | UI canvas, prototype, DESIGN.md/code handoff | require live authenticated availability or official MCP/SDK; prototype is not production proof | https://github.com/google-labs-code/stitch-skills |
| Pomelli | conditional | campaign concepts from a public/approved brand site | official eligibility currently lists Taiwan, English, and 18+; no public API/CLI/MCP was verified; generated Business DNA is a proposal and publishing stays gated | https://support.google.com/labs/answer/16945066 |
| Opal | hold | experimental no-code mini-app/workflow | personal account, English, 18+; stores projects/uploads in a Google Drive `Opal` folder and can link-share or publish; Taiwan availability was not conclusively documented; synthetic data first | https://support.google.com/gemini/answer/16802014 |
| Antigravity | existing, restricted | Google ecosystem/browser artifact and second opinion | Taiwan is supported, but current MAPLAB governance permits no unverified write lease, credential bridge, MCP write, or role expansion | https://antigravity.google/docs/overview |
| Mixboard | conditional | moodboards and visual concept exploration | available in 180+ countries without a per-country list; Labs privacy warns against confidential inputs and permits retention/human review; public/approved/synthetic assets only | https://labs.google/fx/privacy |

Stitch's web service and Google codelab are Google surfaces, while the `google-labs-code` SDK/skills repositories state that they are not officially supported Google products. MCP setup requires a scoped API key and may require a GCP project/billing. No dedicated executable skill is fabricated for Pomelli, Opal, or Mixboard because no stable public automation interface was verified. This router can still prepare an exact brief and route an approved browser session when the service is live.
