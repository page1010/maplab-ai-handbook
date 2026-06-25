#!/usr/bin/env python3
"""
B-role health snapshot — 只讀，不寫任何 DB 或生產檔案。
輸出 JSON 給地端模型判斷。
依 skills/local-agent-b-role-maintenance.md §1 定義。
"""
import sqlite3, json, os, glob
from datetime import datetime, timezone

DB = os.path.expanduser(
    '~/.local/share/investmentos-telegram-operator/data/investment_os.sqlite3')
REPO = os.path.expanduser('~/maplab-ai-handbook')
IOS_RUNTIME = os.path.expanduser(
    '~/.local/share/investmentos-telegram-operator')
IOS_DEV = os.path.expanduser('~/Documents/New project')

result = {'snapshot_time': datetime.now(timezone.utc).isoformat()}

# 1. DB row counts
try:
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True, timeout=5)
    for t in ['influencer_insights', 'influencer_cross_checks', 'market_signals',
              'simulated_positions', 'research_signals', 'api_error_logs',
              'agent_outputs', 'evidence_items']:
        try:
            result[f'db_{t}'] = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        except Exception:
            result[f'db_{t}'] = 'TABLE_MISSING'
    conn.close()
    result['db_accessible'] = True
except Exception as e:
    result['db_accessible'] = False
    result['db_error'] = str(e)

# 2. Background jobs state
jobs_file = os.path.join(IOS_RUNTIME, 'reviews/background_jobs_state.json')
if os.path.exists(jobs_file):
    try:
        jobs = json.load(open(jobs_file)).get('jobs', {})
        result['jobs_failed'] = [k for k, v in jobs.items() if v.get('status') in ('failed', 'timeout', 'error')]
        result['jobs_total'] = len(jobs)
    except Exception:
        result['jobs_failed'] = ['parse_error']
else:
    result['jobs_failed'] = ['state_file_missing']

# 3. Shadow concern count (runtime path)
sc_file = os.path.join(IOS_RUNTIME, 'reports/shadow/local_model_findings.jsonl')
if os.path.exists(sc_file):
    result['shadow_concern_count'] = sum(1 for _ in open(sc_file))
else:
    result['shadow_concern_count'] = 0

# 4. Nightwatch age (days) — try runtime first, then dev
nw_file = os.path.join(IOS_DEV, 'reports/nightwatch/latest.md')
nw_file_rt = os.path.join(IOS_RUNTIME, 'reports/nightwatch/latest.md')
for nw in [nw_file_rt, nw_file]:
    if os.path.exists(nw):
        age_sec = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(nw))).total_seconds()
        result['nightwatch_age_days'] = round(age_sec / 86400, 1)
        break
else:
    result['nightwatch_age_days'] = 999

# 5. B-role receipt ages (days)
for role, pattern in [
    ('b2', 'JOB-B2-REVIEW-*/dataflow_review.md'),
    ('b3', 'JOB-B3-ARCHIVE-*/b_role_rsi_archive.md'),
    ('b4', 'JOB-B4-PATROL-*/fit_check.md'),
]:
    files = sorted(glob.glob(os.path.join(REPO, 'workbook/reviews', pattern)))
    if files:
        age_sec = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(files[-1]))).total_seconds()
        result[f'{role}_receipt_age_days'] = round(age_sec / 86400, 1)
    else:
        result[f'{role}_receipt_age_days'] = 999

# 6. RSI score from latest JSON (if scorer has run)
rsi_files = sorted(glob.glob(
    os.path.join(REPO, 'workbook/reviews/JOB-B*/b_role_recursive_self_improvement.json')))
if rsi_files:
    try:
        with open(rsi_files[-1]) as f:
            rsi_data = json.load(f)
        result['rsi_score'] = rsi_data.get('score')
        result['rsi_band'] = rsi_data.get('band')
        result['rsi_date'] = rsi_data.get('generated_at', '')[:10]
    except Exception:
        result['rsi_score'] = None
        result['rsi_band'] = 'parse_error'
else:
    result['rsi_score'] = None
    result['rsi_band'] = 'no_json_found'

print(json.dumps(result, indent=2, ensure_ascii=False))
