# IOS-KOL Radar Test Receipt — 2026-06-18

## Scope

Owner flagged that the IOS-KOL Telegram radar fix was not trustworthy without tests and a durable receipt.

This receipt covers the fix in:

- `/Users/pagemacmini/Documents/New project/scripts/sync_influencer_agents.py`
- `/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/sync_influencer_agents.py`
- `/Users/pagemacmini/Documents/New project/tests/test_influencer_sync.py`

MAPLAB cold-start governance was also updated so future sessions must declare a test plan and receipt path before claiming completion.

## Test Commands Run

## 2026-06-20 Castbox / SoundOn Podcast Addendum

Owner provided:

```text
http://castbox.fm/app/castbox/feed/1a64de3cc9215d1a2fc86338e14e4d2772edc5a4/track/18dbb6bb4844a5e0675576351dbc7773c16848f4
```

Verification result:

- Castbox app URL is not 股癌 Gooaye. It maps to《兆華與股惑仔》by 李兆華.
- Stable source is SoundOn RSS: `https://feeds.soundon.fm/podcasts/91be014b-9f55-4bf3-a910-b232eda82d11.xml`.
- RSS probe returned 200 XML, 1125 items.
- Latest verified episode at test time: `EP1122｜華許忠於本色，美伊簽署MOU，市場放下心？台、日、韓都創歷史新高！功率、被動元件、封測、CPO，故事正展開？ft.操盤手 黃豐凱`
- Episode guid: `0f189f4d-f530-465d-b1fe-1cf03e281a21`.

Code/runtime changes:

- Added runtime source `理財達人秀／兆華與股惑仔 Podcast`.
- Podcast RSS rows are owner-visible only as `Podcast/RSS 摘要（待逐字稿）`.
- General RSS articles remain excluded from formal single-episode keypoints.
- `build_cross_checks()` now supports scoped `source_ids`, so changed podcast rows are cross-checked even when they are older than the global latest rows.
- Source script and runtime script were synchronized.

Tests run on 2026-06-20:

```bash
cd "/Users/pagemacmini/Documents/New project"
PYTHONPYCACHEPREFIX=/private/tmp/ios_kol_pycache \
.venv/bin/python -m py_compile scripts/sync_influencer_agents.py tests/test_influencer_sync.py
```

Result: pass.

```bash
cd "/Users/pagemacmini/Documents/New project"
PYTHONPYCACHEPREFIX=/private/tmp/ios_kol_pycache \
.venv/bin/python -m pytest -q tests/test_influencer_sync.py \
-k 'podcast_rss or zhaohua or episode_keypoints_digest or youtube_rss_metadata_poll_creates_owner_visible_title_seed or subprocess_env'
```

Result:

```text
6 passed, 37 deselected, 3 warnings
```

```bash
cd "/Users/pagemacmini/Documents/New project"
PYTHONPYCACHEPREFIX=/private/tmp/ios_kol_pycache \
.venv/bin/python -m pytest -q tests/test_influencer_sync.py
```

Result:

```text
42 passed, 1 failed, 4 warnings
```

Remaining failure:

```text
tests/test_influencer_sync.py::test_mock_x_and_political_chip_audits
AttributeError: scripts.run_influencer_hermes_report has no attribute load_opinion_leader_stale_handles
```

Assessment: same unrelated Hermes/report helper contract gap; not in the IOS-KOL podcast RSS digest path.

Runtime syntax check on 2026-06-20:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/ios_kol_runtime_pycache \
"/Users/pagemacmini/Documents/New project/.venv/bin/python" \
-m py_compile \
"/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/sync_influencer_agents.py"
```

Result: pass.

Production DB smoke:

```text
influencer_insights.id = 611
influencer_cross_checks.id = 76153
Telegram send = not sent; preview only
```

Owner-facing preview confirmed:

- Header starts with `IOS-KOL 網紅雷達經理｜團隊指派 OpenClaw/ASR 回報`.
- Channel is `理財達人秀／兆華與股惑仔 Podcast`.
- Status is `Podcast/RSS 摘要（待逐字稿）`.
- No `Q1.` / `A1.` format is used.
- Source URL points to the SoundOn episode page.

Operational note:

- An initial smoke command was run without explicit `--db-path`, which created a small wrong relative DB artifact under the MAPLAB repo. It was removed immediately.
- Follow-up production smoke used the explicit runtime DB path and verified the exact row/cross-check ids above.

### 1. Targeted unit tests

Command:

```bash
cd "/Users/pagemacmini/Documents/New project"
.venv/bin/python -m pytest -q tests/test_influencer_sync.py -k 'episode_keypoints_digest or youtube_rss_metadata_poll_creates_owner_visible_title_seed or subprocess_env'
```

Result:

```text
4 passed, 37 deselected
```

Coverage intent:

- Episode digest must use event summary, not Q/A.
- Core KOL rows must keep `游庭皓的財經皓角`, `理財達人秀`, and `股癌 Gooaye` visible.
- Metadata-only rows must be marked as RSS/title-description summary, not full transcript summary.
- Python subprocess env must strip `PYTHONHOME`, `PYTHONPATH`, and `__PYVENV_LAUNCHER__`.

### 2. Source syntax check

Command:

```bash
cd "/Users/pagemacmini/Documents/New project"
PYTHONPYCACHEPREFIX=/private/tmp/codex_pycache_source .venv/bin/python -m py_compile scripts/sync_influencer_agents.py
```

Result:

```text
pass
```

### 3. Runtime syntax check

Command:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/codex_pycache_runtime \
/Users/pagemacmini/.local/share/investmentos-telegram-operator/.venv/bin/python \
-m py_compile /Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/sync_influencer_agents.py
```

Result:

```text
pass
```

### 4. Live DB runtime preview

Command:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/codex_pycache_preview \
/Users/pagemacmini/.local/share/investmentos-telegram-operator/.venv/bin/python \
-c "import sqlite3, importlib.util, sys; path='/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/sync_influencer_agents.py'; spec=importlib.util.spec_from_file_location('sync_influencer_agents_runtime', path); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); conn=sqlite3.connect('/Users/pagemacmini/.local/share/investmentos-telegram-operator/data/investment_os.sqlite3'); conn.row_factory=sqlite3.Row; text=m.format_episode_keypoints_digest(conn); print(text); print('\\nCHECKS:', '游庭皓的財經皓角' in text, '理財達人秀' in text, '股癌 Gooaye' in text, 'Q1.' not in text and 'A1.' not in text)"
```

Result:

```text
CHECKS: True True True True
```

Preview verified:

- `游庭皓的財經皓角` appears as `逐字稿摘要`.
- `理財達人秀` appears as `RSS/標題描述摘要（待逐字稿）`.
- `股癌 Gooaye` appears as `待 ASR/逐字稿`.
- No `Q1.` or `A1.` remains in the owner-facing radar output.

### 5. 股癌 YouTube metadata smoke

Command:

```bash
yt-dlp --no-playlist --skip-download --print '%(title)s | %(duration)s' 'https://www.youtube.com/watch?v=qz2KuuV6XJk'
```

Result:

```text
EP671 | 🌼 | 3045
```

Note:

- `yt-dlp` printed an old-version warning for `2026.03.17`, but metadata read succeeded.
- This confirms the video is reachable; full ASR is still a heavier follow-up job.

### 6. Full influencer sync test file

Command:

```bash
cd "/Users/pagemacmini/Documents/New project"
.venv/bin/python -m pytest -q tests/test_influencer_sync.py
```

Result:

```text
40 passed, 1 failed
```

Remaining failure:

```text
tests/test_influencer_sync.py::test_mock_x_and_political_chip_audits
AttributeError: scripts.run_influencer_hermes_report has no attribute load_opinion_leader_stale_handles
```

Assessment:

- This failure is outside the IOS-KOL radar digest path.
- It is an existing Hermes/report helper contract gap and should be handled in a separate task.

## Cold-Start Governance Updated

Files updated:

- `docs/company-values.md`
- `AGENT_STARTUP_PROTOCOL.md`
- `AGENT_RULES.md`
- `CURRENT_STATUS.md`
- `pitfalls.md`

New rule:

```text
有寫但沒測，等於沒完成；有測但沒 receipt，等於下一個 session 無法信任。
```

Startup Check now must include:

- `Test plan`
- `Receipt path`

Final/handoff must include:

- `Tests run`
- `Receipt`

## Verdict

IOS-KOL radar fix is tested for the requested behavior and has a durable receipt.

2026-06-20 addendum verdict:

- The Castbox/SoundOn podcast source is integrated into IOS-KOL radar as a core KOL podcast RSS supplement.
- The output is intentionally marked as `Podcast/RSS 摘要（待逐字稿）`, so it does not overclaim transcript-level certainty.
- The scoped cross-check regression is covered by tests.

Known remaining risk:

- 股癌 still needs full ASR/transcript follow-up to turn `待 ASR/逐字稿` into content summary.
- Full influencer test file has one unrelated Hermes/report failure.
