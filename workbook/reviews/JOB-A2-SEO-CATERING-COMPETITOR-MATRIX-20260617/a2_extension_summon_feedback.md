# A2 Extension Summon Feedback

Date: 2026-06-17
Summoned by: A0 / Codex via file-backed dynamic role module route
Role module: `chrome-extension/task-modules/A2.json`

## A2 Finding

A0's main error was not that no skill existed. The repo already had `skills/extension-agent-summon-guide.md`, and `skills/superpowers-guide.md` already routed `Extension / 召喚 / Agent Commander` tasks to that skill.

A0 failed to use the existing skill before acting.

## Handoff Correction

- The available summon route is the file-backed dynamic role module, not only the popup UI.
- The Chrome Extension popup is an interface. The handoff contract is built from `chrome-extension/task-modules/A2.json`, task cards, research bundles, and role recall.
- If `chrome-extension://.../popup.html` cannot be opened by a runtime, A0 must not treat that as a blocker.
- A0 should use `chrome-extension/task-modules/{role}.json` plus the `buildModuleHandoff()` structure to dispatch the role, then wait for the summoned role's report.

## Required A0 Flow

1. Read `skills/extension-agent-summon-guide.md` and `skills/superpowers-guide.md`.
2. Build the A2 runtime handoff from `chrome-extension/task-modules/A2.json`.
3. Include the current task under `## 1.1 本次召喚任務`.
4. Send the handoff to the A2 runtime / subagent.
5. Wait for A2 to read the task card and research bundle.
6. Use A2's report to repair `T-A2-SEO-CATERING-MATRIX-001.md` and `claude_task_prompt.md`.

## A2 Verdict

A0 should not stop at "prompt for Owner review" and should not say "extension UI unavailable, so handoff is blocked." If the UI is unavailable, file-backed dynamic role module handoff is still the correct path.
