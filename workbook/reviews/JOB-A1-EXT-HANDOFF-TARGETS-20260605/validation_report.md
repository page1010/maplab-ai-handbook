# Chrome Extension Handoff Targets v5.6.1 Validation

Date: 2026-06-05
Owner request: optimize the side-panel handoff target selector for Claude Code,
Codex, GPT, Claude Chrome tab, Antigravity, Gemini, OpenClaw, Hermes, and
Gemini Chrome tab.

## Result

`PASS`

The installed MAPLAB Agent Commander Chrome Extension was reloaded and read back
from Owner Chrome. The live extension reports `manifestVersion=5.6.1`, the
side-panel version badge shows `v5.6.1`, and `#runtimeSelect` exposes 9 handoff
targets.

## Live Readback

Installed target:
`chrome-extension://ifpmihhbfhpbcippnhdnjdecbgkmbgmf/popup.html`

Runtime targets:

1. Claude Code
2. Codex
3. GPT / ChatGPT
4. Claude Chrome tab
5. Antigravity
6. Gemini
7. OpenClaw
8. Hermes
9. Gemini Chrome tab

Prompt smoke:

- Selected role: `IOS-KOL`
- Selected runtime target: `GPT / ChatGPT`
- Prompt label: `IOS-KOL -> GPT / ChatGPT handoff`
- Prompt contains `runtime_target: gpt`: pass
- Prompt contains `runtime_target_label: GPT / ChatGPT`: pass
- Prompt contains GPT-specific boundary instruction: pass

Screenshot:
`chrome_extension_handoff_targets_v561.png`

## Static Validation

- `node --check chrome-extension/popup.js`: pass
- `python3 -m json.tool chrome-extension/manifest.json`: pass
- HTML runtime option count: 9

## Safety

No secrets, cookies, API keys, WordPress publishing, Ads changes, broker actions,
or destructive filesystem actions were touched.
