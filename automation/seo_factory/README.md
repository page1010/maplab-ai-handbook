# MAPLAB SEO Factory (Local-Only, Pillar First)

This module implements a local-first SEO content factory for MAPLAB Kitchen:

- Pipeline: `Planner -> Writer -> Linker -> Schema Builder -> Verifier -> WP Draft Publisher -> Auditor`
- Scope: first wave focuses on three pillar pages.
- Publishing policy: write WordPress `draft` only.
- Runtime: weekly batch friendly, Ollama-first, with deterministic validation.

## Quick start

1. Create a virtual environment (optional) and install dependencies:

```bash
pip3 install -r automation/seo_factory/requirements.txt
```

2. (Optional) Set environment variables for WordPress draft publishing:

```bash
export WP_BASE_URL="https://www.maplabkitchen.com"
export WP_USERNAME="your_wp_user"
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
```

3. (Optional) Set Ollama endpoint/model:

```bash
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL_SMALL="llama3.1:latest"
export OLLAMA_MODEL_MEDIUM="llama3.1:latest"
export OLLAMA_TIMEOUT_SECONDS="45"
```

4. Run weekly batch in dry-run mode (default):

```bash
python3 automation/seo_factory/run_weekly_batch.py
```

5. Publish drafts to WordPress:

```bash
python3 automation/seo_factory/run_weekly_batch.py --publish
```

## Practical Ollama tests

Run a real local model test + one-pillar pipeline run:

```bash
python3 automation/seo_factory/test_ollama_execution.py --pillar corporate
```

Run one-pillar with draft publishing:

```bash
python3 automation/seo_factory/test_ollama_execution.py --pillar corporate --publish
```

You can also run only selected pillars in weekly batch:

```bash
python3 automation/seo_factory/run_weekly_batch.py --pillars corporate,wedding
```

## Output

Generated artifacts are stored under:

- `automation/seo_factory/output/runs/<trace_id>/artifacts/*.json`
- `automation/seo_factory/output/runs/<trace_id>/reports/*.json`

Main files include:

- `pillar-draft-*.json`: final `DraftArtifact`
- `validation-summary.json`: pass/fail + score + issues
- `publishing-summary.json`: dry-run payload or WP post result
- `audit-log.json`: stage-by-stage record
- `cannibalization-candidates.json`: second-wave recommendation report

## Input data

- Pillar briefs: `automation/seo_factory/config/pillars.json`
- Link policy: `automation/seo_factory/config/link_policy.json`
- Existing post signals (optional): `automation/seo_factory/input/post_signals_sample.json`

To improve recommendations, replace sample signals with GSC/GA exported data transformed into the same schema.
