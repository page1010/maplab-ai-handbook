#!/usr/bin/env python3
"""Fail-closed validation for the private Hermes 20-case human annotations.

The validator never emits case content, case hashes, or reviewer identity.  It
only returns aggregate gate state and immutable artifact hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GUIDE_PATH = ROOT / "docs" / "hermes-line-rubric-v2-annotation-guide.json"
DEFAULT_PRIVATE_PREFLIGHT_PATH = Path(
    "/Users/pagemacmini/.maplab/a6-hermes-training/"
    "supervisor_jobs/MAPJOB-20260827-224251-d291ad/"
    "rubric_v2_annotation_guide_preflight_v1.json"
)

ANNOTATION_SCHEMA = "maplab.hermes.line-rubric-human-annotations.v1"
VALIDATION_SCHEMA = "maplab.hermes.line-rubric-human-annotations-validation.v1"
PREFLIGHT_SCHEMA = "maplab.hermes.line-rubric-annotation-preflight.v1"
GUIDE_SCHEMA = "maplab.hermes.line-rubric-annotation-guide.v1"

EXPECTED_PRIVATE_PREFLIGHT_SHA256 = (
    "10e41cf26ad327b4f848a9d5818f8c4df140c33655a5619d41c9c3b4b4d89d39"
)
EXPECTED_ANNOTATION_GUIDE_SHA256 = (
    "d62cf9bf9480cec8244e02c5da65c7c4273e6c394e2247a5e0fd120f2cd8032f"
)
EXPECTED_COMMERCIAL_AUTHORITY_SHA256 = (
    "84d9733b2ad7de062ffc979846a6ea3bbbfcee6248d5b898e88baf13ad0bfe27"
)

CRITERIA_ORDER = (
    "answers_current_question",
    "next_question_is_necessary",
    "does_not_reask_known",
    "facts_are_grounded",
    "price_policy_availability_are_grounded",
    "at_most_three_questions",
    "mobile_readable",
)
HASH_RE = re.compile(r"[0-9a-f]{64}")
ALLOWED_REVIEWER_ROLES = {
    "owner",
    "business_reviewer",
    "sales_reviewer",
    "operations_reviewer",
    "human_reviewer",
    "adjudicator",
}
FORBIDDEN_REVIEWER_MARKERS = re.compile(
    r"(?:^|[^a-z0-9])(ai|agent|automation|bot|codex|claude|hermes|llm|model|ollama|openai|synthetic)(?:$|[^a-z0-9])",
    re.IGNORECASE,
)


class AnnotationValidationError(ValueError):
    """A sanitized, stable fail-closed error code."""


class _DuplicateKeyError(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_regular_file(path: Path, label: str, *, private: bool) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise AnnotationValidationError(f"{label}_file_invalid")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise AnnotationValidationError(f"{label}_not_single_regular_file")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise AnnotationValidationError(f"{label}_wrong_owner")
    if private and stat.S_IMODE(info.st_mode) != 0o600:
        raise AnnotationValidationError(f"{label}_mode_not_0600")
    if private:
        parent = path.parent
        parent_info = parent.stat()
        if (
            parent.is_symlink()
            or not parent.is_dir()
            or (hasattr(os, "getuid") and parent_info.st_uid != os.getuid())
            or stat.S_IMODE(parent_info.st_mode) != 0o700
        ):
            raise AnnotationValidationError(f"{label}_parent_not_owner_only_0700")


def load_json(path: Path, label: str, *, private: bool) -> dict[str, Any]:
    _validate_regular_file(path, label, private=private)
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except (_DuplicateKeyError, OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AnnotationValidationError(f"{label}_json_invalid") from error
    if not isinstance(value, dict):
        raise AnnotationValidationError(f"{label}_json_not_object")
    return value


def _require_exact_keys(value: Any, expected: Iterable[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise AnnotationValidationError(f"{label}_keys_invalid")
    return value


def _require_nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AnnotationValidationError(f"{label}_invalid")
    return value


def _parse_utc_timestamp(value: Any, label: str) -> datetime:
    text = _require_nonempty_text(value, label)
    if not text.endswith("Z"):
        raise AnnotationValidationError(f"{label}_invalid")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as error:
        raise AnnotationValidationError(f"{label}_invalid") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise AnnotationValidationError(f"{label}_invalid")
    return parsed


def _validate_reviewed_at_utc(value: Any, *, not_before: datetime) -> None:
    text = _require_nonempty_text(value, "reviewer_reviewed_at_utc")
    parsed = _parse_utc_timestamp(text, "reviewer_reviewed_at_utc")
    if parsed < not_before:
        raise AnnotationValidationError("reviewer_timestamp_predates_guide")
    if parsed > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise AnnotationValidationError("reviewer_timestamp_in_future")


def _validate_guide(guide: dict[str, Any], expected_authority_sha256: str) -> datetime:
    if guide.get("schema_version") != GUIDE_SCHEMA:
        raise AnnotationValidationError("annotation_guide_schema_invalid")
    if guide.get("criteria_order") != list(CRITERIA_ORDER):
        raise AnnotationValidationError("annotation_guide_criteria_invalid")
    if guide.get("current_commercial_authority_snapshot_sha256") != expected_authority_sha256:
        raise AnnotationValidationError("commercial_authority_binding_invalid")

    boundary = guide.get("data_boundary")
    if not isinstance(boundary, dict) or {
        "guide_contains_private_line_content": boundary.get("guide_contains_private_line_content"),
        "guide_contains_customer_identifiers": boundary.get("guide_contains_customer_identifiers"),
        "private_preflight_must_remain_immutable": boundary.get("private_preflight_must_remain_immutable"),
        "annotations_must_be_written_to_separate_private_file": boundary.get(
            "annotations_must_be_written_to_separate_private_file"
        ),
        "model_or_third_party_annotation_allowed": boundary.get(
            "model_or_third_party_annotation_allowed"
        ),
    } != {
        "guide_contains_private_line_content": False,
        "guide_contains_customer_identifiers": False,
        "private_preflight_must_remain_immutable": True,
        "annotations_must_be_written_to_separate_private_file": True,
        "model_or_third_party_annotation_allowed": False,
    }:
        raise AnnotationValidationError("annotation_guide_human_boundary_invalid")

    contract = guide.get("human_annotation_contract")
    if not isinstance(contract, dict):
        raise AnnotationValidationError("annotation_guide_human_contract_missing")
    if contract.get("schema_version") != ANNOTATION_SCHEMA:
        raise AnnotationValidationError("annotation_guide_human_schema_invalid")
    if contract.get("reviewer_is_human_required") is not True:
        raise AnnotationValidationError("annotation_guide_human_attestation_invalid")
    if contract.get("independent_review_attestation_required") is not True:
        raise AnnotationValidationError("annotation_guide_independence_attestation_invalid")
    if contract.get("all_20_case_hashes_exactly_once") is not True:
        raise AnnotationValidationError("annotation_guide_case_count_contract_invalid")
    if contract.get("overall_must_be_recomputed") is not True:
        raise AnnotationValidationError("annotation_guide_overall_contract_invalid")
    if contract.get("ai_or_synthetic_labels_count_as_human_gold") is not False:
        raise AnnotationValidationError("annotation_guide_machine_labels_not_excluded")
    if contract.get("output_location") != "separate owner-only 0600 file":
        raise AnnotationValidationError("annotation_guide_output_location_invalid")
    if contract.get("required_parent_bindings") != [
        "private_preflight_sha256",
        "annotation_guide_sha256",
        "commercial_authority_snapshot_sha256",
    ]:
        raise AnnotationValidationError("annotation_guide_parent_binding_contract_invalid")
    if contract.get("reviewer_required_fields") != [
        "reviewer_id",
        "reviewer_name",
        "reviewer_role",
        "is_human",
        "reviewed_at_utc",
        "independent_review_attestation",
    ]:
        raise AnnotationValidationError("annotation_guide_reviewer_fields_invalid")
    if contract.get("case_required_fields") != [
        "case_hash",
        "criteria",
        "unsafe_claim",
        "overall_pass",
        "rationale",
        "evidence_refs",
    ]:
        raise AnnotationValidationError("annotation_guide_case_fields_invalid")
    execution_gate = guide.get("execution_gate")
    if not isinstance(execution_gate, dict) or (
        execution_gate.get("annotation_may_start_after_this_guide") is not True
        or execution_gate.get("scorer_calibration_may_start") is not False
        or execution_gate.get("render_or_e1_may_start") is not False
        or execution_gate.get("customer_send_allowed") is not False
    ):
        raise AnnotationValidationError("annotation_guide_execution_gate_closed")
    created_at = _parse_utc_timestamp(guide.get("created_at"), "annotation_guide_created_at")
    if created_at > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise AnnotationValidationError("annotation_guide_created_at_in_future")
    return created_at


def _preflight_case_hashes(preflight: dict[str, Any]) -> tuple[str, ...]:
    if preflight.get("schema_version") != PREFLIGHT_SCHEMA:
        raise AnnotationValidationError("private_preflight_schema_invalid")
    cases = preflight.get("cases")
    if not isinstance(cases, list) or len(cases) != 20:
        raise AnnotationValidationError("private_preflight_case_count_invalid")
    hashes: list[str] = []
    for case in cases:
        if not isinstance(case, dict):
            raise AnnotationValidationError("private_preflight_case_invalid")
        case_hash = case.get("case_hash")
        if not isinstance(case_hash, str) or not HASH_RE.fullmatch(case_hash):
            raise AnnotationValidationError("private_preflight_case_hash_invalid")
        hashes.append(case_hash)
    if len(set(hashes)) != 20:
        raise AnnotationValidationError("private_preflight_case_hash_duplicate")
    return tuple(hashes)


def _validate_reviewer(value: Any, *, guide_created_at: datetime) -> None:
    reviewer = _require_exact_keys(
        value,
        (
            "reviewer_id",
            "reviewer_name",
            "reviewer_role",
            "is_human",
            "reviewed_at_utc",
            "independent_review_attestation",
        ),
        "reviewer",
    )
    for key in ("reviewer_id", "reviewer_name", "reviewer_role"):
        _require_nonempty_text(reviewer[key], f"reviewer_{key}")
    if reviewer["reviewer_role"] not in ALLOWED_REVIEWER_ROLES:
        raise AnnotationValidationError("reviewer_role_not_allowed")
    reviewer_identity_contract = (
        f"{reviewer['reviewer_id']} {reviewer['reviewer_name']} {reviewer['reviewer_role']}"
    )
    if FORBIDDEN_REVIEWER_MARKERS.search(reviewer_identity_contract):
        raise AnnotationValidationError("reviewer_machine_identity_rejected")
    if reviewer["is_human"] is not True:
        raise AnnotationValidationError("reviewer_is_human_not_attested")
    if reviewer["independent_review_attestation"] is not True:
        raise AnnotationValidationError("reviewer_independence_not_attested")
    _validate_reviewed_at_utc(reviewer["reviewed_at_utc"], not_before=guide_created_at)


def _validate_case(value: Any) -> str:
    case = _require_exact_keys(
        value,
        ("case_hash", "criteria", "unsafe_claim", "overall_pass", "rationale", "evidence_refs"),
        "annotation_case",
    )
    case_hash = case["case_hash"]
    if not isinstance(case_hash, str) or not HASH_RE.fullmatch(case_hash):
        raise AnnotationValidationError("annotation_case_hash_invalid")

    criteria = _require_exact_keys(case["criteria"], CRITERIA_ORDER, "annotation_criteria")
    if any(criteria[name] not in {"PASS", "FAIL"} for name in CRITERIA_ORDER):
        raise AnnotationValidationError("annotation_criteria_value_invalid")
    if type(case["unsafe_claim"]) is not bool:
        raise AnnotationValidationError("annotation_unsafe_claim_not_bool")
    if type(case["overall_pass"]) is not bool:
        raise AnnotationValidationError("annotation_overall_not_bool")
    recomputed = all(criteria[name] == "PASS" for name in CRITERIA_ORDER) and not case["unsafe_claim"]
    if case["overall_pass"] is not recomputed:
        raise AnnotationValidationError("annotation_overall_recompute_mismatch")

    _require_nonempty_text(case["rationale"], "annotation_rationale")
    evidence_refs = case["evidence_refs"]
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise AnnotationValidationError("annotation_evidence_refs_invalid")
    if any(not isinstance(item, str) or not item.strip() for item in evidence_refs):
        raise AnnotationValidationError("annotation_evidence_ref_invalid")
    return case_hash


def validate_annotations(
    annotations_path: Path,
    preflight_path: Path = DEFAULT_PRIVATE_PREFLIGHT_PATH,
    guide_path: Path = DEFAULT_GUIDE_PATH,
    *,
    expected_preflight_sha256: str = EXPECTED_PRIVATE_PREFLIGHT_SHA256,
    expected_guide_sha256: str = EXPECTED_ANNOTATION_GUIDE_SHA256,
    expected_authority_sha256: str = EXPECTED_COMMERCIAL_AUTHORITY_SHA256,
) -> dict[str, Any]:
    annotations_path = Path(os.path.abspath(annotations_path.expanduser()))
    preflight_path = Path(os.path.abspath(preflight_path.expanduser()))
    guide_path = Path(os.path.abspath(guide_path.expanduser()))

    annotations = load_json(annotations_path, "human_annotations", private=True)
    preflight = load_json(preflight_path, "private_preflight", private=True)
    guide = load_json(guide_path, "annotation_guide", private=False)

    if sha256_file(preflight_path) != expected_preflight_sha256:
        raise AnnotationValidationError("private_preflight_sha256_mismatch")
    if sha256_file(guide_path) != expected_guide_sha256:
        raise AnnotationValidationError("annotation_guide_sha256_mismatch")
    guide_created_at = _validate_guide(guide, expected_authority_sha256)
    expected_case_hashes = _preflight_case_hashes(preflight)

    top = _require_exact_keys(
        annotations,
        ("schema_version", "parent_bindings", "reviewer", "cases"),
        "annotations",
    )
    if top["schema_version"] != ANNOTATION_SCHEMA:
        raise AnnotationValidationError("annotations_schema_invalid")
    bindings = _require_exact_keys(
        top["parent_bindings"],
        (
            "private_preflight_sha256",
            "annotation_guide_sha256",
            "commercial_authority_snapshot_sha256",
        ),
        "annotation_parent_bindings",
    )
    expected_bindings = {
        "private_preflight_sha256": expected_preflight_sha256,
        "annotation_guide_sha256": expected_guide_sha256,
        "commercial_authority_snapshot_sha256": expected_authority_sha256,
    }
    if bindings != expected_bindings:
        raise AnnotationValidationError("annotation_parent_binding_mismatch")

    _validate_reviewer(top["reviewer"], guide_created_at=guide_created_at)
    cases = top["cases"]
    if not isinstance(cases, list) or len(cases) != 20:
        raise AnnotationValidationError("annotation_case_count_invalid")
    actual_case_hashes = [_validate_case(case) for case in cases]
    if len(set(actual_case_hashes)) != 20:
        raise AnnotationValidationError("annotation_case_hash_duplicate")
    if set(actual_case_hashes) != set(expected_case_hashes):
        raise AnnotationValidationError("annotation_case_set_mismatch")

    return {
        "schema_version": VALIDATION_SCHEMA,
        "status": "PASS",
        "eligible_for_scorer_calibration": True,
        "case_count": 20,
        "criteria_count": len(CRITERIA_ORDER),
        "annotation_sha256": sha256_file(annotations_path),
        "parent_bindings": expected_bindings,
        "reviewer_identity_emitted": False,
        "case_identity_emitted": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PRIVATE_PREFLIGHT_PATH)
    parser.add_argument("--guide", type=Path, default=DEFAULT_GUIDE_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = validate_annotations(args.annotations, args.preflight, args.guide)
    except AnnotationValidationError as error:
        result = {
            "schema_version": VALIDATION_SCHEMA,
            "status": "NO_GO",
            "eligible_for_scorer_calibration": False,
            "errors": [str(error)],
            "reviewer_identity_emitted": False,
            "case_identity_emitted": False,
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
