# MAPLAB OpenClaw Memory Governance

This document defines how MAPLAB turns GitHub truth into OpenClaw workspace memory without losing reviewability.

## Goal

We want a local AI transfer station that:

1. Reads the right project truth.
2. Produces directed outputs, not orphan notes.
3. Leaves a review bundle for every meaningful run.
4. Preserves only the useful parts of long conversations.
5. Feeds the next task with a clean handoff.

## Layers

### 1) GitHub truth source

GitHub holds the durable record.

Keep here:

- `CURRENT_STATUS.md`
- `AGENT_RULES.md`
- `AGENT_RECALL_PROMPTS.md`
- `CHANGELOG.md`
- `handoff/tasks/*.md`
- `docs/openclaw/*.md`
- `docs/governance/*.md`
- `projects/*.md`

Do not use GitHub as a live chat log.

### 2) OpenClaw workspace memory

`~/.openclaw/workspace` should contain the compressed working memory for the local assistant.

Keep here:

- workspace bootstrap docs
- role summaries
- task routing notes
- current operating checklist
- short summaries of the last useful decisions

Do not keep:

- full chat transcripts
- duplicated copies of large repo docs
- unreviewed secrets
- dead-end experiments that add no reuse value

### 3) Review bundles

Every meaningful local run must write a bundle under:

`workbook/reviews/JOB-xxx/`

Bundle contents should include:

- `task_request.md`
- `draft.md` or `output.json`
- `execution_log.json`
- `output_manifest.json`
- `verification_log.json`
- `review_request.md`
- `screenshots/terminal.log`

If the task touches Sheets, WordPress, or other write surfaces, include diffs or screenshots too.

### 4) Archive

If a path is useful once but should not be repeated, store it in `archive/` or convert it into a short lesson.

Archive:

- failed paths that taught nothing new
- old prompts that are superseded
- intermediate drafts that no longer help operations

Convert to a lesson:

- a repeatable best practice
- a permission boundary
- a model-routing rule
- a bundle shape that saves time later

## Directed output rule

Every artifact should answer:

- Who consumes this?
- What should happen next?
- Where does this write back?
- What does this affect?

Minimum metadata for any task artifact:

- `consumer`
- `next_action`
- `write_back`
- `related_tasks`
- `risk_level`

## Relationship graph rule

We do not want isolated outputs.

Every stage should connect:

- task -> output
- task -> blocker
- output -> next task
- task -> agent
- output -> owner decision

The graph should let us answer:

1. What depends on this?
2. What is this waiting on?
3. Who should take the next step?
4. Which outputs are reusable?

## Closed-loop stage rule

Every stage must close with a short record:

- What we tried
- What was produced
- What was verified
- What remains open
- What should happen next

That record becomes the seed for the next session.

## OpenClaw setup strategy

OpenClaw should not load the whole repo as memory.
Instead:

1. Read GitHub truth.
2. Compress the current task into workspace memory.
3. Load only the role-specific docs needed for this task.
4. Run the task.
5. Emit a review bundle.
6. Write back only the durable lesson.

## Good memory candidates

- role boundaries that are stable
- verified file locations
- output schemas
- permission rules
- known fallback paths
- successful shortest paths

## Bad memory candidates

- unverified guesses
- duplicated long-form docs
- temporary prompts
- dead-end experiments
- any secret values or tokens

## Minimum operating promise

If a task finishes, it leaves evidence.
If it changes something, it says where.
If it cannot finish, it leaves the next best step.
