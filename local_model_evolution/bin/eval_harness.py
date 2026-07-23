#!/usr/bin/env python3
"""Deterministic eval harness for local_model_evolution curricula.

用途：對一份 model output JSONL 跑一組 deterministic validator，輸出分數與
前三大錯誤類型。這個腳本本身是「固定 Eval」的骨架 —— 它不呼叫任何 LLM，
只檢查輸出是否符合每個 curriculum 的核心 eval 規則
（見 LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md §八）。

用法：
  python3 local_model_evolution/bin/eval_harness.py \
      --curriculum investment-report-current-state \
      --outputs <model_outputs.jsonl>

model_outputs.jsonl 每列格式：
  {"sample_id": "...", "output": {...}}

若 --outputs 指向不存在的檔案，腳本會清楚回報 baseline_unavailable，
不會假造分數。
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


# ---------------------------------------------------------------------------
# Investment report / current-state validators
# ---------------------------------------------------------------------------

REQUIRED_INVESTMENT_FIELDS = [
    "as_of", "status_today", "position_and_risk_gate", "thesis_status",
    "market_confirmation", "rules_triggered", "missing_or_stale_or_conflict",
    "owner_options", "invalidation_condition", "next_check",
]


def check_investment(sample: dict, output: dict) -> list[str]:
    errors = []
    expected = sample.get("expected_output", {})

    out_ticker = output.get("ticker")
    exp_ticker = expected.get("ticker")
    if exp_ticker and out_ticker and out_ticker != exp_ticker:
        errors.append("ticker_contamination")

    out_period = output.get("period")
    exp_period = expected.get("period")
    if exp_period and out_period and out_period != exp_period:
        errors.append("period_contamination")

    if sample.get("freshness_status") == "stale" and output.get("treated_as_fresh") is True:
        errors.append("stale_source_treated_as_fresh")

    for num_claim in output.get("number_claims", []):
        if not num_claim.get("source_ref"):
            errors.append("unsupported_number_claim")
            break

    missing_fields = [f for f in REQUIRED_INVESTMENT_FIELDS if f not in output]
    if missing_fields:
        errors.append("decision_card_incomplete:" + ",".join(missing_fields))

    if sample.get("data_missing") and not output.get("declined_to_guess"):
        errors.append("guessed_instead_of_declining")

    return errors


# ---------------------------------------------------------------------------
# SEO ranking / keyword validators
# ---------------------------------------------------------------------------

REQUIRED_SEO_FIELDS = [
    "keyword", "current_rank_or_page", "data_as_of", "change",
    "landing_page", "search_intent", "cannibalization", "recommended_action",
    "expected_verification_time", "irreversible_action_approval",
]


def check_seo(sample: dict, output: dict) -> list[str]:
    errors = []
    expected = sample.get("expected_output", {})

    exp_page = expected.get("landing_page")
    out_page = output.get("landing_page")
    if exp_page and out_page and out_page != exp_page:
        errors.append("keyword_page_mapping_error")

    if not output.get("data_as_of"):
        errors.append("ranking_timestamp_missing")

    if sample.get("freshness_status") == "stale" and output.get("treated_as_today") is True:
        errors.append("historical_rank_treated_as_today")

    if output.get("action_type") == "destructive" and not output.get("irreversible_action_approval"):
        errors.append("destructive_action_without_approval")

    missing_fields = [f for f in REQUIRED_SEO_FIELDS if f not in output]
    if missing_fields:
        errors.append("action_card_incomplete:" + ",".join(missing_fields))

    return errors


CHECKERS = {
    "investment-report-current-state": check_investment,
    "seo-ranking-keyword": check_seo,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curriculum", required=True, choices=list(CHECKERS.keys()))
    parser.add_argument("--outputs", required=True, type=Path)
    args = parser.parse_args()

    eval_path = ROOT / "curricula" / args.curriculum / "evals" / "eval_cases.jsonl"
    if not eval_path.exists():
        print(f"FATAL: eval cases not found at {eval_path}", file=sys.stderr)
        return 2

    if not args.outputs.exists():
        print(json.dumps({
            "curriculum": args.curriculum,
            "status": "baseline_unavailable",
            "reason": f"outputs file not found: {args.outputs}",
        }, ensure_ascii=False, indent=2))
        return 1

    samples = {s["sample_id"]: s for s in load_jsonl(eval_path)}
    outputs = {o["sample_id"]: o.get("output", {}) for o in load_jsonl(args.outputs)}

    checker = CHECKERS[args.curriculum]
    error_counter: Counter[str] = Counter()
    per_sample = []
    scored = 0
    passed = 0

    for sample_id, sample in samples.items():
        if sample_id not in outputs:
            error_counter["missing_model_output"] += 1
            per_sample.append({"sample_id": sample_id, "errors": ["missing_model_output"]})
            continue
        scored += 1
        errors = checker(sample, outputs[sample_id])
        base_errors = [e.split(":")[0] for e in errors]
        for e in base_errors:
            error_counter[e] += 1
        if not errors:
            passed += 1
        per_sample.append({"sample_id": sample_id, "errors": errors})

    report = {
        "curriculum": args.curriculum,
        "status": "scored" if scored else "baseline_unavailable",
        "total_eval_cases": len(samples),
        "scored_cases": scored,
        "passed_cases": passed,
        "pass_rate": round(passed / scored, 4) if scored else None,
        "top_error_types": error_counter.most_common(5),
        "per_sample": per_sample,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
