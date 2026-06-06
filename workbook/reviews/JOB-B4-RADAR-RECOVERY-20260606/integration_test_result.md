# Integration Test Result — JOB-B4-RADAR-RECOVERY-20260606

- generated_at: 2026-06-06T21:43+08:00
- smoke_db: `/private/tmp/investos_black_swan_smoke.sqlite3`
- safety: dry-run only; no broker, no order execution, no Telegram send.

## Commands

```bash
.venv/bin/python scripts/fetch_market_signals.py --db-path /private/tmp/investos_black_swan_smoke.sqlite3
.venv/bin/python scripts/evaluate_risk.py --db-path /private/tmp/investos_black_swan_smoke.sqlite3 --dry-run --mode postmarket --date 2026-06-05
.venv/bin/python scripts/evaluate_reentry.py --db-path /private/tmp/investos_black_swan_smoke.sqlite3 --event-date 2026-06-05 --date 2026-06-06
PYTHONPYCACHEPREFIX=/private/tmp/investos-black-swan-pycache python3 -m py_compile scripts/fetch_market_signals.py scripts/evaluate_risk.py scripts/evaluate_reentry.py
PYTHONPYCACHEPREFIX=/private/tmp/investos-black-swan-pycache .venv/bin/python -m pytest -q tests/test_black_swan_engine.py
```

## Fetch Result

- Source: Yahoo Finance v8; Stooq fallback implemented but not needed in final full fetch.
- Symbols fetched successfully: `vix`, `vxf`, `sox`, `ixic`, `tsm`, `es`, `nq`, `jpy`, `dxy`, `oil`, `tnx`, `hyg`, `gld`.
- Final full fetch failures: none.
- Key 2026-06-05 readings:
  - `^SOX`: `-10.256950500275382%`
  - `^IXIC`: `-4.179989127532529%`
  - `TSM`: `-6.686595141180835%`
  - `ES=F`: `-2.6378108143665306%`
  - `NQ=F`: `-4.79447000073799%`
  - `VXF` ETF proxy: `-3.322633669463083%`
  - `HYG`: `-0.5010666625380203%`

## Dry-Run Risk Result

```text
BLACK_SWAN score=13 crisis_type=EPISODIC mode=postmarket
dry_run=true radar_bsi=0
calendar_events=NFP:2026-06-05:today

Actions:
- would_pause_pending_proposed_orders=0
- execution_lock=on
```

Scoring reasons:

- VIX daily change `39.7%` >=20%: `+1`
- SOX daily change `-10.3%` <=-8%: `+4`
- NASDAQ daily change `-4.2%` <=-4%: `+2`
- TSM daily change `-6.7%` <=-5%: `+1`
- VXF daily change `-3.3%` <=-3%: `+1`
- ES futures daily change `-2.6%` <=-2%: `+1`
- NQ futures daily change `-4.8%` <=-2%: `+1`
- NFP on 2026-06-05: `+2`

## Re-Entry Result

```text
recommended_exposure=0%
事件後第 1 天：禁止加回
槓桿禁止恢復：VIX=21.5 尚未低於 20。
- WAIT Gate1 恐慌消退
- PASS Gate2 資金面穩定
- WAIT Gate3 技術修復
```

## Local Verification

- `py_compile`: pass.
- `tests/test_black_swan_engine.py`: `4 passed`.
- Network note: sandboxed run failed DNS for Yahoo/Stooq; escalated public-data fetch succeeded.
