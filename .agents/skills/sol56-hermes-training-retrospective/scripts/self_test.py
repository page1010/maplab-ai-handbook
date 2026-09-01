#!/usr/bin/env python3
"""Run positive and contradiction tests against the retrospective report contract."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

from validate_report import SCHEMA_PATH, _validate_cross_fields


def _errors(schema: dict[str, Any], report: dict[str, Any]) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    schema_errors = list(validator.iter_errors(report))
    if schema_errors:
        return [error.message for error in schema_errors]
    return _validate_cross_fields(report)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: self_test.py VALID_REPORT.json", file=sys.stderr)
        return 2

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    valid = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    results: dict[str, str] = {}

    results["valid_report"] = "PASS" if not _errors(schema, valid) else "FAIL"

    read_only_applied = copy.deepcopy(valid)
    read_only_applied["writebacks"]["status"] = "APPLIED"
    results["reject_read_only_applied"] = "PASS" if _errors(schema, read_only_applied) else "FAIL"

    impossible_success = copy.deepcopy(valid)
    impossible_success["verdict"].update(
        {
            "weight_learning": "PROVEN",
            "system_quality": "IMPROVED",
            "safety": "PASS",
            "promotion": "ELIGIBLE",
        }
    )
    results["reject_impossible_success"] = "PASS" if _errors(schema, impossible_success) else "FAIL"

    missing_mapping_code = copy.deepcopy(valid)
    missing_mapping_code["evidence_ledger"]["missing"] = [
        claim
        for claim in missing_mapping_code["evidence_ledger"]["missing"]
        if claim["code"] != "ACTIVITY_MAPPING_MISSING"
    ]
    results["reject_missing_mapping_code"] = "PASS" if _errors(schema, missing_mapping_code) else "FAIL"

    wrong_safety_sum = copy.deepcopy(valid)
    wrong_safety_sum["safety_counts"]["hard_violations_total"] = 4
    results["reject_wrong_safety_sum"] = "PASS" if _errors(schema, wrong_safety_sum) else "FAIL"

    wrong_adoption_sum = copy.deepcopy(valid)
    wrong_adoption_sum["shadow_adoption"]["direct_use"] = 1
    results["reject_wrong_adoption_sum"] = "PASS" if _errors(schema, wrong_adoption_sum) else "FAIL"

    improved_with_null_adoption = copy.deepcopy(valid)
    improved_with_null_adoption["verdict"]["system_quality"] = "IMPROVED"
    results["reject_improved_with_null_adoption"] = (
        "PASS" if _errors(schema, improved_with_null_adoption) else "FAIL"
    )

    complete_mapping_without_links = copy.deepcopy(valid)
    complete_mapping_without_links["activity_map"].update(
        {
            "mapping_status": "COMPLETE",
            "mapping_receipt": "fake-receipt",
            "mapping_missing_reason": None,
            "unmapped_attempts": 0,
            "activity_links": [],
        }
    )
    complete_mapping_without_links["evidence_ledger"]["missing"] = [
        claim
        for claim in complete_mapping_without_links["evidence_ledger"]["missing"]
        if claim["code"] != "ACTIVITY_MAPPING_MISSING"
    ]
    results["reject_complete_mapping_without_links"] = (
        "PASS" if _errors(schema, complete_mapping_without_links) else "FAIL"
    )

    status = "PASS" if all(value == "PASS" for value in results.values()) else "FAIL"
    print(json.dumps({"status": status, "checks": results}, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
