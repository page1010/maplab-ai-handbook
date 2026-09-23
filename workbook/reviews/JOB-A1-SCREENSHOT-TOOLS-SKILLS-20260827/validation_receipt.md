# Validation Receipt — Screenshot Tool Skills

- Task: `T-A1-SCREENSHOT-TOOLS-SKILLS-002`
- Date: 2026-08-27 Asia/Taipei
- Actor: Codex acting as System Skill Architecture Engineer
- Scope: pinned user skills, repo routers, read-only audits, local smoke tests
- Overall: `PASS_WITH_EXTERNAL_GATES`
- Implementation checkpoint: `d17f3762221c8299fb0b7f0f059f4b5a868d71db`

## Outcome

Two reviewed upstream skills are installed without hooks or credentials, and three MAPLAB-specific routers are committed. Existing Graphify and NotebookLM assets are reused instead of duplicated. Experimental web tools remain prototype-only or HOLD according to their data/account surface.

## Installed or created

| Item | Location / source | Result |
|---|---|---|
| watch v0.2.0 | `/Users/pagemacmini/.codex/skills/watch`; `bradautomates/claude-video@83da59fa78c3eee9e20f515fe75c438bb5166efd` | PASS, local safety adaptation |
| Impeccable v4.1.2 | `/Users/pagemacmini/.codex/skills/impeccable`; `pbakaus/impeccable@63b04e2530f5c7b41ea83c133daab24f34912456` | PASS, no hooks |
| video evidence router | `.agents/skills/maplab-video-evidence-readback` | PASS |
| project knowledge router | `.agents/skills/maplab-project-knowledge-router` | PASS |
| creative prototype router | `.agents/skills/maplab-creative-prototype-router` | PASS |

The upstream installer copied the reviewed skill payloads only. Unsupported cross-harness frontmatter was moved into legal `metadata`; provenance was preserved. No `npx` installer, hook manifest, package auto-install, API key write, service, listener, external content upload, or publish action was performed.

## Tool audit verdicts

- `claude-video`: useful for frame/transcript evidence. Its original setup can auto-install Homebrew dependencies, write `~/.config/watch/.env`, upload extracted audio to Groq/OpenAI, and suggest `rm -rf`; local policy disables those defaults for MAPLAB/private work.
- `notebooklm-py`: not installed. It is unofficial, depends on undocumented Google APIs and authenticated cookies, and exposes write/share/delete capabilities that duplicate the current sanitized browser route.
- Graphify: kept at 0.9.49. No update or semantic/media mode was run.
- Impeccable: useful for frontend critique and refinement; pinned skill installed, detector hooks omitted.
- Pomelli, Stitch, Mixboard: conditionally useful for approved prototype work; not treated as brand truth or production proof.
- Opal: HOLD; private/customer data prohibited and account/region/Drive/share behavior must be verified first.
- Antigravity: existing route retained; no role or permission expansion.

## Validation

- `quick_validate.py`: watch, Impeccable, and all three MAPLAB routers — 5/5 PASS.
- Lifecycle audit from repo: `skills=14 duplicates=0` — PASS.
- `python3 -m py_compile` on project router preflight — PASS.
- `python3 -m unittest tools.ai_workbook.test_build_directional_system_map -v` — 7/7 PASS.
- `python3 tools/ai_workbook/build_directional_system_map.py --check` — `ok=true`, generated outputs fresh.
- `git diff --check` for three new skill folders — PASS.
- Independent seven-scenario forward test — PASS after fixing transcript-block precedence, hash-vs-FOUND, external-action split, Opal private prohibition, and no-Task-Card fallback.

## Watch smoke

- Input: generated 2-second 320x240 H.264 test pattern under `/tmp`.
- Command policy: local file, `--no-whisper`, `efficient`, `--max-frames 8`.
- Result: 4 timestamped JPEG frames, no audio stream, no transcript, no network transcription, exit 0.
- Visual readback: last frame is a valid SMPTE-style test pattern.
- Dependencies already present: FFmpeg 8.1.2, yt-dlp 2026.03.17, Python 3.9.6.
- Work directory retained for bounded inspection: `/private/tmp/maplab-watch-smoke-20260827-output`.

## Project knowledge freshness

- NotebookLM router and source manifest exist.
- Both configured Markdown pack SHA-256 values match the router — route `ready`.
- Graphify binary: `/Users/pagemacmini/.local/bin/graphify`, version 0.9.49.
- Graph report built commit: `e5d931d4`.
- Implementation checkpoint: `d17f3762221c8299fb0b7f0f059f4b5a868d71db`.
- Graph route: `needs_refresh`; any blast-radius answer must start `NEEDS_LIVE_REFRESH` until a clean, reviewed `graphify update .`.

## ComfyUI / RunningHub cloud determination

- `VERIFIED_CAPABILITY`: RunningHub describes itself as a cloud ComfyUI platform with online workflow execution and GPU runtime; its API accepts workflow tasks and charges account coins/runtime. Video workflows are available.
- `VERIFIED_ALTERNATIVE`: ComfyUI's official Comfy Cloud runs workflows on hosted RTX 6000 Pro GPUs and offers an experimental Cloud API.
- `BOUNDARY`: ComfyUI itself can be local or cloud. A workflow launched in RunningHub/Comfy Cloud uses their server compute; local self-hosted ComfyUI uses the Mac/GPU; partner/API nodes can create a hybrid path.
- `LOCAL_READBACK`: no repo RunningHub/Comfy Cloud key reference, ComfyUI executable/app, workflow adapter, or live execution receipt was found.
- `STATUS`: `AVAILABLE_EXTERNALLY / NOT_CONNECTED` — cloud compute is real, but MAPLAB integration and one synthetic paid/live smoke remain future gated work.

## Safety readback

- Secret values printed or committed: zero.
- Customer/private media sent externally: zero.
- Google cookies imported: zero.
- External board/app/campaign/workflow created: zero.
- Impeccable hooks installed/approved: zero.
- Existing unrelated dirty files staged or committed: zero.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| video evidence `SKILL.md` | `baeab3741fe30714f59f47ea3c68698eac7606e4e001337c4d1b40e70785c977` |
| project router `SKILL.md` | `d58058004f0a399fd89aac5d0996e60a2d7a9e03a40a78c37e068b401577b00f` |
| project preflight | `34b33f2e59e205adb3f418fab49e04994c8c4aea2d5f7e6e03504240573373f3` |
| creative router `SKILL.md` | `58e5edeaea5a80367abcac910ee4a150c039697078ed194c8324502aa5f812ab` |
| installed watch `SKILL.md` | `6e878832aa497535f3aae17e0c8332fcb7729c71522c071363fd222472458a56` |
| installed Impeccable `SKILL.md` | `f2f778c5cb6f32cb7c829b17fd2cead4f8a534ab4c317c09174fb63988520f00` |

## VERIFIED / DRIFT / NEXT

- `VERIFIED`: pinned installs, local safety adaptations, validators, discovery, watch extraction, NotebookLM pack integrity, router behavior, official cloud-compute capability.
- `DRIFT`: Graphify graph is stale relative to HEAD; external Labs availability/terms and cloud pricing can change; no live RunningHub/Comfy Cloud account execution has been performed.
- `NEXT`: only if Owner requests cloud video integration, choose one provider and run one 2–5 second synthetic workflow with protected credential, cost, egress, output-hash, and cleanup receipt. Do not use customer footage for the first smoke.
