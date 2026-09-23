# Project knowledge truth boundaries

| Layer | Good evidence | Cannot prove |
|---|---|---|
| Graphify | symbols, files, static relationships, candidate blast radius | current runtime, approval, publish state, historical intent |
| NotebookLM safe pack | documented SOP, role, input/output, handoff and canonical path | a recent file change not rebuilt into the pack, live UI, runtime completion |
| CURRENT_STATUS / Task Card | declared current state and bounded assignment | external state without readback |
| receipt | the action and verification recorded for its exact artifact/hash | unrelated artifacts or later drift |
| live API/UI/runtime readback | current visible or machine state at the observation time | durable history unless captured in a receipt |

When layers disagree, do not average them. Report the disagreement, prefer the more direct evidence for the exact claim, and propose the smallest refresh or readback that can converge them.
