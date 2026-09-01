#!/usr/bin/env python3
"""Validate a Sol 5.6 Hermes retrospective receipt and reject cross-field contradictions."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "references"
    / "training-retrospective-report.schema.json"
)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_cross_fields(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    safety = report["safety_counts"]
    safety_parts = [
        safety["unauthorized_commercial_claims"],
        safety["privacy_leaks"],
        safety["customer_sends"],
        safety["other_hard_violations"],
    ]
    if _is_int(safety["hard_violations_total"]) and all(_is_int(v) for v in safety_parts):
        if safety["hard_violations_total"] != sum(safety_parts):
            errors.append("safety_counts.hard_violations_total must equal the four category counts")

    activity = report["activity_map"]
    attempts = activity["provider_attempts"]
    responses = activity["responses"]
    if _is_int(attempts) and _is_int(responses) and responses > attempts:
        errors.append("activity_map.responses cannot exceed provider_attempts")
    for field in ("retry_attempts", "fallback_attempts", "unmapped_attempts"):
        value = activity[field]
        if _is_int(attempts) and _is_int(value) and value > attempts:
            errors.append(f"activity_map.{field} cannot exceed provider_attempts")
    if activity["mapping_status"] == "MISSING" and _is_int(attempts):
        if activity["unmapped_attempts"] != attempts:
            errors.append("MISSING mapping requires unmapped_attempts to equal provider_attempts")

    links = activity["activity_links"]
    attempt_ids = [link["provider_attempt_id"] for link in links]
    if len(attempt_ids) != len(set(attempt_ids)):
        errors.append("activity_links provider_attempt_id values must be unique")
    if _is_int(attempts) and len(links) > attempts:
        errors.append("activity_links cannot contain more rows than provider_attempts")
    if activity["mapping_status"] == "COMPLETE" and _is_int(attempts):
        if len(links) != attempts:
            errors.append("COMPLETE mapping requires exactly one activity_link per provider_attempt")
        derived_counts = {
            "responses": sum(link["outcome"] == "response" for link in links),
            "retry_attempts": sum(link["retry_of_attempt_id"] is not None for link in links),
            "fallback_attempts": sum(link["fallback_from_attempt_id"] is not None for link in links),
            "examples": len({link["example_id"] for link in links if link["example_id"] is not None}),
            "evaluation_rounds": len(
                {link["evaluation_round_id"] for link in links if link["evaluation_round_id"] is not None}
            ),
        }
        for field, derived in derived_counts.items():
            if _is_int(activity[field]) and activity[field] != derived:
                errors.append(f"COMPLETE mapping {field} must equal the value derived from activity_links")
    if activity["mapping_status"] == "PARTIAL" and _is_int(attempts) and _is_int(activity["unmapped_attempts"]):
        if len(links) + activity["unmapped_attempts"] != attempts:
            errors.append("PARTIAL mapping requires activity_links plus unmapped_attempts to equal provider_attempts")
    if activity["mapping_status"] == "MISSING" and links:
        errors.append("MISSING mapping cannot include activity_links")

    adoption = report["shadow_adoption"]
    labels = [adoption["direct_use"], adoption["minor_edit"], adoption["major_edit"], adoption["reject"]]
    if _is_int(adoption["eligible_denominator"]) and all(_is_int(v) for v in labels):
        if adoption["eligible_denominator"] != sum(labels):
            errors.append("shadow_adoption eligible_denominator must equal all four label counts")
    if all(_is_int(adoption[key]) for key in ("panel_size", "eligible_denominator", "excluded_cases")):
        if adoption["panel_size"] != adoption["eligible_denominator"] + adoption["excluded_cases"]:
            errors.append("shadow_adoption panel_size must equal eligible_denominator plus excluded_cases")
    if _is_int(activity["shadow_cases"]) and _is_int(adoption["panel_size"]):
        if activity["shadow_cases"] != adoption["panel_size"]:
            errors.append("activity_map.shadow_cases must equal shadow_adoption.panel_size")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_report.py REPORT.json", file=sys.stderr)
        return 2

    report_path = Path(sys.argv[1]).resolve()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    schema_errors = sorted(validator.iter_errors(report), key=lambda error: list(error.absolute_path))
    if schema_errors:
        errors = [
            f"schema:{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in schema_errors
        ]
    else:
        errors = _validate_cross_fields(report)

    result = {
        "schema_version": report.get("schema_version"),
        "report": str(report_path),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
