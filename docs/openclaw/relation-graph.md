# MAPLAB OpenClaw Relation Graph

This document defines the minimum graph structure for work that must stay connected across tasks.

## Purpose

The graph exists so outputs are not isolated.

We want to know:

- what produced this
- what depends on this
- who should read this next
- what still blocks closure

## Node types

- `task`
- `output`
- `review_bundle`
- `agent`
- `blocker`
- `decision`
- `source_doc`

## Edge types

- `task -> output`
- `task -> blocker`
- `task -> agent`
- `output -> next_task`
- `output -> decision`
- `output -> review_bundle`
- `task -> source_doc`

## Minimum graph data

Each node should carry enough metadata to be useful:

- `id`
- `type`
- `title`
- `status`
- `path` or `reference`
- `updated_at`

Each edge should carry:

- `from`
- `to`
- `relation`
- `confidence`

## Operational rule

When a task closes, update the graph with:

- the final output node
- the review bundle node
- the next task node, if any
- any blockers that remain open

## Why this matters

Without the graph, OpenClaw becomes a chat box with memory loss.

With the graph, we can answer:

1. What does this affect?
2. What should happen next?
3. What can be reused?
4. What is still unresolved?
