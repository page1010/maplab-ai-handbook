---
type: "path_query"
date: "2026-08-25T13:37:22.092788+00:00"
question: "How does the canonical directional map generator connect NotebookLM and freshness checks?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["build_notebooklm_pack()", "build_directional_system_map.py", "check_generated_outputs()"]
---

# Q: How does the canonical directional map generator connect NotebookLM and freshness checks?

## Answer

Expanded from graph vocabulary: directional, system, map, manifest, render, workflow, role, artifact, sheet. Graphify verified build_notebooklm_pack calls redaction and hashing helpers; build_notebooklm_pack and check_generated_outputs are two hops apart through build_directional_system_map.py.

## Outcome

- Signal: useful

## Source Nodes

- build_notebooklm_pack()
- build_directional_system_map.py
- check_generated_outputs()