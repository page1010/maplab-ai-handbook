# OpenClaw for MAPLAB

This folder contains the local execution and memory design for MAPLAB OpenClaw work.

## Read first

1. [memory-governance.md](./memory-governance.md)
2. [output-contract.md](./output-contract.md)
3. [relation-graph.md](./relation-graph.md)
4. [closed-loop-playbook.md](./closed-loop-playbook.md)
5. [dispatch-role.md](./dispatch-role.md)
6. [security-boundaries.md](./security-boundaries.md)

## Purpose

- Keep GitHub as the durable truth source.
- Keep OpenClaw workspace memory compressed and task-focused.
- Keep review bundles as the evidence layer.
- Keep outputs directed and connected.

## Working rule

Do not load the whole repo into memory.
Load the task-specific docs, produce a bundle, and write back only the durable lesson.
