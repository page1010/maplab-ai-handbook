---
type: "explain"
date: "2026-08-25T13:37:22.155013+00:00"
question: "Can the AST-only graph prove the Extension button opens the generated system map?"
contributor: "graphify"
outcome: "dead_end"
source_nodes: ["openDirectionalSystemMap()", "popup.js"]
---

# Q: Can the AST-only graph prove the Extension button opens the generated system map?

## Answer

The AST graph finds openDirectionalSystemMap in chrome-extension/popup.js but only its file containment edge. It cannot infer chrome.runtime.getURL resource lineage to the generated HTML; use manifest/source UI readback and the canonical governance graph for that claim.

## Outcome

- Signal: dead_end

## Source Nodes

- openDirectionalSystemMap()
- popup.js