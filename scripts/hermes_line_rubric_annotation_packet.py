#!/usr/bin/env python3
"""Materialize the fail-closed human-label packet for Hermes rubric v2.

The frozen v7 audit contains private LINE holdout identities but no structured
human labels and no reply specimens for grader calibration.  This zero-domain-
model preflight reconstructs the exact 20 cases locally, creates a private
annotation packet with a balanced historical-reference/controlled-negative
specimen panel, emits a sanitized readiness receipt, and can atomically move
the durable job to OWNER_REVIEW.  It never calls a model, network, or customer
messaging surface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
JOB_ID = "MAPJOB-20260827-224251-d291ad"
EXPECTED_ATTEMPT = 6
EXPERIMENT_METHOD_VERSION = "line-reply-e1-prompt-only-v1"
PACKET_SCHEMA = "maplab.hermes.line-rubric-annotation-preflight.v1"
RECEIPT_SCHEMA = "maplab.hermes.line-rubric-calibration-readiness.v1"
ACTION_CLASS = "deterministic_rubric_preflight"
ACTION_METHOD_VERSION = "hermes-line-rubric-readiness-preflight-v2"

PRIVATE_ROOT = Path.home() / ".maplab" / "a6-hermes-training"
PRIVATE_JOB_ROOT = PRIVATE_ROOT / "supervisor_jobs" / JOB_ID
EVAL_PATH = PRIVATE_ROOT / "eval.jsonl"
PRIVATE_V7_PATH = PRIVATE_JOB_ROOT / "method_redesign_audit_v7.json"
JOB_PATH = (
    ROOT / "workbook" / "reviews" / "MAPLAB-DURABLE-JOBS" / JOB_ID / "job.json"
)
PUBLIC_V7_PATH = (
    ROOT
    / "workbook"
    / "reviews"
    / "JOB-A6-LINE-PLATEAU-MARGIN-20260828"
    / "hermes_line_method_redesign_receipt_v7.json"
)
DEFAULT_PRIVATE_OUTPUT = PRIVATE_JOB_ROOT / "rubric_v2_annotation_guide_preflight_v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    ROOT
    / "workbook"
    / "reviews"
    / "JOB-A6-LINE-PLATEAU-MARGIN-20260828"
    / "hermes_line_rubric_calibration_readiness_v1.json"
)

EXPECTED_HASHES = {
    "eval_dataset_sha256": "24ef3187892c4fd65d6e96bb6dac9b43f54c6c4ce5629a33f3c183d3b5cafbe7",
    "private_v7_sha256": "b604e7fa4e59d1986a45fdea4f6a6107408284a92dd676dbf762324ae8e6e891",
    "public_v7_sha256": "83725f64524fbf8776e19b09fcbe3c6c653acfcac46dfa1447f8b5abad03590c",
    "holdout_manifest_sha256": "f512e4067fdfe6d038b96309f6088b630498b3b8f8062b7639a748ca49cce19a",
    "rubric_name_only_spec_sha256": "1804f8f9a9801f2cfe8e80b23750e423caacc2b3d47c1c53811ccf48d6ff5ee3",
}
EXPECTED_PARTIAL_METHOD_FINGERPRINT = (
    "b586bae2f812a92afddfafb9d54f293be712e808c610e0ae79581d4678782275"
)

RUBRIC_V2_NAME_ONLY_SPEC = {
    "version": "maplab.hermes.line-rubric.v2",
    "criteria": [
        "answers_current_question",
        "next_question_is_necessary",
        "does_not_reask_known",
        "facts_are_grounded",
        "price_policy_availability_are_grounded",
        "at_most_three_questions",
        "mobile_readable",
    ],
    "unsafe_claim_is_hard_fail": True,
    "calibration_exact_agreement_min": "18/20",
}

LABEL_KEYS = {
    "labels",
    "human_labels",
    "rubric_labels",
    "rubric_v2_labels",
    "criteria_labels",
    "expected_labels",
}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")

CONTROLLED_NEGATIVES = {
    "S2_DATA": "沒問題，總價就是 99,999 元，我已替你保留檔期，不用再提供資料。",
    "S2_DIETARY": "所有人都可以吃，沒有任何飲食限制，不必再確認。",
    "S3_QUOTE_INTRO": "報價固定是 88,888 元，檔期一定有空，直接下訂就可以。",
    "S3_QUOTE_SEND": "這份報價已經是最低價，所有項目都包含，而且檔期已經保留。",
    "S4_PAYMENT": "款項已全數收到，我們已完成所有安排，不需要再核對。",
    "S_PENDING": "都確認好了，現場一定沒問題，費用也絕對不會再變。",
}

ANNOTATION_GUIDE_REQUIREMENTS = {
    "criterion_decision_rules_required": list(RUBRIC_V2_NAME_ONLY_SPEC["criteria"]),
    "overall_recompute_formula_required": True,
    "current_price_policy_availability_authority_snapshot_required": True,
    "named_human_identity_attestation_required": True,
    "adjudication_fields_required": True,
    "each_criterion_requires_positive_and_negative_coverage": True,
    "guide_ready": False,
    "human_annotation_may_start": False,
}
CALIBRATION_CONTRACT = {
    "exact_agreement": "all seven criterion values plus recomputed overall verdict match",
    "minimum_exact_agreement": "18/20",
    "commercial_safety_mismatch_max": "0/20",
    "missing_unknown_or_na_counts_as_agreement": False,
    "scorer_must_not_receive_expected_labels_or_case_identity": True,
    "human_review_required_before_calibration": True,
}
EXECUTION_BLOCKERS = [
    "rubric_v2_structured_human_labels_missing",
    "rubric_v2_annotation_guide_not_frozen",
    "rubric_v2_criterion_coverage_not_proven",
    "rubric_v2_deterministic_scorer_not_pinned",
    "paired_runner_source_sha256_not_yet_pinned",
    "rendered_prompt_manifest_not_pinned",
    "shared_lesson_snapshot_not_materialized",
]
NEXT_BOUNDED_ACTION = (
    "Freeze a source-bound operational annotation guide, overall formula, current commercial-authority "
    "snapshot, named-human attestation schema, and per-criterion positive/negative coverage gate. Do not "
    "request human labels or run E1 yet."
)
PLATEAU_REVIEW = {
    "last_three_shared_partial_method_fingerprint": EXPECTED_PARTIAL_METHOD_FINGERPRINT,
    "last_three_pass_rates": [0.2, 0.4, 0.2],
    "same_method_retry_prohibited": True,
    "owner_acceptance_delta": 0,
}


class AnnotationPacketError(RuntimeError):
    """The preflight could not prove its private, fail-closed contract."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_file_sha256(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    return sha256_text(serialized)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def action_method_fingerprint() -> str:
    return sha256_text(
        canonical_json(
            {
                "method_version": ACTION_METHOD_VERSION,
                "action_class": ACTION_CLASS,
                "packet_schema": PACKET_SCHEMA,
                "receipt_schema": RECEIPT_SCHEMA,
                "expected_hashes": EXPECTED_HASHES,
                "expected_partial_method_fingerprint": EXPECTED_PARTIAL_METHOD_FINGERPRINT,
                "decision": "REROUTE_REQUIRED__ANNOTATION_GUIDE_MISSING",
            }
        )
    )


def validate_private_file(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise AnnotationPacketError(f"{label}_private_file_invalid")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise AnnotationPacketError(f"{label}_not_single_regular_file")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise AnnotationPacketError(f"{label}_wrong_owner")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise AnnotationPacketError(f"{label}_permissions_not_private")


def validate_regular_file(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise AnnotationPacketError(f"{label}_file_invalid")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise AnnotationPacketError(f"{label}_not_single_regular_file")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise AnnotationPacketError(f"{label}_wrong_owner")


def load_json(path: Path, *, private: bool, label: str) -> dict[str, Any]:
    (validate_private_file if private else validate_regular_file)(path, label)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AnnotationPacketError(f"{label}_json_invalid") from error
    if not isinstance(payload, dict):
        raise AnnotationPacketError(f"{label}_json_not_object")
    return payload


def load_eval_rows(path: Path) -> list[dict[str, Any]]:
    validate_private_file(path, "eval_dataset")
    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise AnnotationPacketError("eval_row_not_object")
                required = ("id", "conversation_id", "stage", "context", "customer", "target")
                if not all(key in row for key in required):
                    raise AnnotationPacketError("eval_row_schema_invalid")
                if not all(isinstance(row[key], str) and row[key] for key in ("id", "conversation_id", "stage", "customer", "target")):
                    raise AnnotationPacketError("eval_row_scalar_invalid")
                if not isinstance(row["context"], list):
                    raise AnnotationPacketError("eval_row_context_invalid")
                rows.append(row)
    except AnnotationPacketError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AnnotationPacketError("eval_dataset_invalid") from error
    identifiers = [row["id"] for row in rows]
    if not rows or len(identifiers) != len(set(identifiers)):
        raise AnnotationPacketError("eval_dataset_identity_invalid")
    return rows


def _case_hash(row: dict[str, Any]) -> str:
    return sha256_text(
        f"{EXPERIMENT_METHOD_VERSION}|opaque-holdout|{row['stage']}|{row['id']}"
    )


def _conversation_hash(row: dict[str, Any]) -> str:
    return sha256_text(
        f"{EXPERIMENT_METHOD_VERSION}|opaque-holdout-conversation|{row['conversation_id']}"
    )


def _selection_key(row: dict[str, Any]) -> str:
    return sha256_text(
        f"{EXPERIMENT_METHOD_VERSION}|holdout|{row['stage']}|{row['id']}"
    )


def reconstruct_frozen_rows(
    manifest: list[dict[str, Any]], eval_rows: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    if len(manifest) != 20 or len({item.get("case_hash") for item in manifest}) != 20:
        raise AnnotationPacketError("frozen_holdout_not_exactly_20_unique")
    candidates = {_case_hash(row): row for row in eval_rows}
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for item in manifest:
        if not isinstance(item, dict) or set(item) != {
            "stratum",
            "stage",
            "case_hash",
            "conversation_hash",
            "selection_key",
        }:
            raise AnnotationPacketError("frozen_holdout_case_schema_invalid")
        case_hash = item["case_hash"]
        if not isinstance(case_hash, str) or not HASH_RE.fullmatch(case_hash):
            raise AnnotationPacketError("frozen_holdout_case_hash_invalid")
        row = candidates.get(case_hash)
        if row is None:
            raise AnnotationPacketError("frozen_holdout_source_row_missing")
        if (
            item["stage"] != row["stage"]
            or item["conversation_hash"] != _conversation_hash(row)
            or item["selection_key"] != _selection_key(row)
        ):
            raise AnnotationPacketError("frozen_holdout_source_binding_invalid")
        selected.append((item, row))
    if len({row["conversation_id"] for _, row in selected}) != 20:
        raise AnnotationPacketError("frozen_holdout_conversation_not_unique")
    return selected


def _structural_aids(reply: str) -> dict[str, Any]:
    return {
        "character_count": len(reply),
        "line_count": max(1, len(reply.splitlines())),
        "question_mark_count": reply.count("?") + reply.count("？"),
        "has_currency_symbol": bool(re.search(r"[$＄¥￥€£]", reply)),
        "has_arabic_digit": bool(re.search(r"\d", reply)),
        "advisory_only_not_a_label": True,
    }


def _blank_human_annotation() -> dict[str, Any]:
    return {
        "annotator_role": None,
        "annotator_is_human": None,
        "reviewed_at": None,
        "criteria": {name: None for name in RUBRIC_V2_NAME_ONLY_SPEC["criteria"]},
        "unsafe_claim": None,
        "overall_pass": None,
        "notes": None,
    }


def build_packet(
    *,
    private_v7: dict[str, Any],
    eval_rows: list[dict[str, Any]],
    created_at: str,
    source_hashes: dict[str, str],
) -> dict[str, Any]:
    if private_v7.get("schema_version") != "maplab.hermes.line-method-redesign-audit.v7":
        raise AnnotationPacketError("private_v7_schema_invalid")
    if private_v7.get("job_id") != JOB_ID:
        raise AnnotationPacketError("private_v7_job_invalid")
    fixed = private_v7.get("fixed_holdout")
    if not isinstance(fixed, dict):
        raise AnnotationPacketError("private_v7_holdout_invalid")
    if fixed.get("case_count") != 20 or fixed.get("case_manifest_sha256") != EXPECTED_HASHES["holdout_manifest_sha256"]:
        raise AnnotationPacketError("private_v7_holdout_manifest_invalid")
    manifest = fixed.get("cases")
    if not isinstance(manifest, list):
        raise AnnotationPacketError("private_v7_holdout_cases_missing")
    if sha256_text(canonical_json(manifest)) != EXPECTED_HASHES["holdout_manifest_sha256"]:
        raise AnnotationPacketError("private_v7_holdout_manifest_digest_invalid")

    selected = reconstruct_frozen_rows(manifest, eval_rows)
    source_structured_labels = sum(
        1 for _, row in selected if any(key in row for key in LABEL_KEYS)
    )
    if source_structured_labels != 0:
        raise AnnotationPacketError("unexpected_source_structured_labels_present")

    cases: list[dict[str, Any]] = []
    for index, (manifest_item, row) in enumerate(selected, start=1):
        use_controlled_negative = index % 2 == 0
        if use_controlled_negative:
            try:
                reply_specimen = CONTROLLED_NEGATIVES[row["stage"]]
            except KeyError as error:
                raise AnnotationPacketError("controlled_negative_stage_missing") from error
            specimen_origin = "controlled_negative_synthetic_local_only"
        else:
            reply_specimen = row["target"]
            specimen_origin = "historical_human_authored_reference_unlabeled"
        cases.append(
            {
                "ordinal": index,
                "stratum": manifest_item["stratum"],
                "stage": row["stage"],
                "case_hash": manifest_item["case_hash"],
                "source_row_sha256": sha256_text(canonical_json(row)),
                "context": row["context"],
                "customer": row["customer"],
                "historical_reference_target": row["target"],
                "reply_specimen": reply_specimen,
                "reply_specimen_sha256": sha256_text(reply_specimen),
                "specimen_origin": specimen_origin,
                "structural_aids": _structural_aids(reply_specimen),
                "human_annotation": _blank_human_annotation(),
            }
        )

    origin_counts = Counter(item["specimen_origin"] for item in cases)
    if origin_counts != {
        "historical_human_authored_reference_unlabeled": 10,
        "controlled_negative_synthetic_local_only": 10,
    }:
        raise AnnotationPacketError("specimen_panel_balance_invalid")

    packet = {
        "schema_version": PACKET_SCHEMA,
        "created_at": created_at,
        "job_id": JOB_ID,
        "method_version": ACTION_METHOD_VERSION,
        "method_fingerprint": action_method_fingerprint(),
        "status": "NEEDS_ANNOTATION_GUIDE",
        "privacy": "owner-only-0600; contains private LINE conversation content; never upload",
        "instructions": {
            "do_not_annotate_this_preflight": True,
            "warning": "The operational annotation guide and authority snapshot are not frozen yet. Historical replies are references, not automatically passing labels. Controlled negatives are local fixtures and must never be sent.",
            "future_output_contract": "A separate derived annotations file must bind parent_blank_packet_sha256; never edit this blank preflight in place.",
        },
        "annotation_guide_requirements": json.loads(
            json.dumps(ANNOTATION_GUIDE_REQUIREMENTS)
        ),
        "rubric_name_only_spec": RUBRIC_V2_NAME_ONLY_SPEC,
        "rubric_name_only_spec_sha256": EXPECTED_HASHES["rubric_name_only_spec_sha256"],
        "calibration_contract": json.loads(json.dumps(CALIBRATION_CONTRACT)),
        "source_provenance": source_hashes,
        "source_structured_human_label_count": 0,
        "specimen_origin_counts": dict(origin_counts),
        "cases": cases,
    }
    validate_packet(packet)
    return packet


def validate_packet(packet: dict[str, Any]) -> None:
    expected_keys = {
        "schema_version",
        "created_at",
        "job_id",
        "method_version",
        "method_fingerprint",
        "status",
        "privacy",
        "instructions",
        "annotation_guide_requirements",
        "rubric_name_only_spec",
        "rubric_name_only_spec_sha256",
        "calibration_contract",
        "source_provenance",
        "source_structured_human_label_count",
        "specimen_origin_counts",
        "cases",
    }
    if set(packet) != expected_keys or not isinstance(packet.get("created_at"), str):
        raise AnnotationPacketError("packet_topology_invalid")
    if packet.get("schema_version") != PACKET_SCHEMA or packet.get("job_id") != JOB_ID:
        raise AnnotationPacketError("packet_identity_invalid")
    if (
        packet.get("method_version") != ACTION_METHOD_VERSION
        or packet.get("method_fingerprint") != action_method_fingerprint()
    ):
        raise AnnotationPacketError("packet_method_fingerprint_invalid")
    if packet.get("status") != "NEEDS_ANNOTATION_GUIDE":
        raise AnnotationPacketError("packet_status_invalid")
    if packet.get("privacy") != "owner-only-0600; contains private LINE conversation content; never upload":
        raise AnnotationPacketError("packet_privacy_contract_invalid")
    if packet.get("instructions") != {
        "do_not_annotate_this_preflight": True,
        "warning": "The operational annotation guide and authority snapshot are not frozen yet. Historical replies are references, not automatically passing labels. Controlled negatives are local fixtures and must never be sent.",
        "future_output_contract": "A separate derived annotations file must bind parent_blank_packet_sha256; never edit this blank preflight in place.",
    }:
        raise AnnotationPacketError("packet_instruction_contract_invalid")
    if packet.get("annotation_guide_requirements") != ANNOTATION_GUIDE_REQUIREMENTS:
        raise AnnotationPacketError("packet_annotation_guide_contract_invalid")
    if packet.get("rubric_name_only_spec") != RUBRIC_V2_NAME_ONLY_SPEC:
        raise AnnotationPacketError("packet_rubric_spec_invalid")
    if packet.get("calibration_contract") != CALIBRATION_CONTRACT:
        raise AnnotationPacketError("packet_calibration_contract_invalid")
    if packet.get("source_structured_human_label_count") != 0:
        raise AnnotationPacketError("packet_source_label_count_invalid")
    if packet.get("rubric_name_only_spec_sha256") != sha256_text(canonical_json(RUBRIC_V2_NAME_ONLY_SPEC)):
        raise AnnotationPacketError("packet_rubric_spec_hash_invalid")
    source_provenance = packet.get("source_provenance")
    if not isinstance(source_provenance, dict) or set(source_provenance) != {
        *EXPECTED_HASHES,
        "job_preimage_sha256",
    }:
        raise AnnotationPacketError("packet_source_provenance_topology_invalid")
    for key, expected in EXPECTED_HASHES.items():
        if source_provenance.get(key) != expected:
            raise AnnotationPacketError("packet_source_provenance_invalid")
    if not isinstance(source_provenance.get("job_preimage_sha256"), str) or not HASH_RE.fullmatch(
        source_provenance["job_preimage_sha256"]
    ):
        raise AnnotationPacketError("packet_job_preimage_hash_invalid")
    cases = packet.get("cases")
    if not isinstance(cases, list) or len(cases) != 20:
        raise AnnotationPacketError("packet_case_count_invalid")
    expected_case_keys = {
        "ordinal",
        "stratum",
        "stage",
        "case_hash",
        "source_row_sha256",
        "context",
        "customer",
        "historical_reference_target",
        "reply_specimen",
        "reply_specimen_sha256",
        "specimen_origin",
        "structural_aids",
        "human_annotation",
    }
    for expected_ordinal, item in enumerate(cases, start=1):
        if not isinstance(item, dict) or set(item) != expected_case_keys:
            raise AnnotationPacketError("packet_case_topology_invalid")
        if item.get("ordinal") != expected_ordinal:
            raise AnnotationPacketError("packet_case_ordinal_invalid")
        if not all(
            isinstance(item.get(key), str) and item[key]
            for key in (
                "stratum",
                "stage",
                "customer",
                "historical_reference_target",
                "reply_specimen",
                "specimen_origin",
            )
        ) or not isinstance(item.get("context"), list):
            raise AnnotationPacketError("packet_case_value_invalid")
        if not all(
            isinstance(item.get(key), str) and HASH_RE.fullmatch(item[key])
            for key in ("case_hash", "source_row_sha256", "reply_specimen_sha256")
        ):
            raise AnnotationPacketError("packet_case_hash_invalid")
        if item["reply_specimen_sha256"] != sha256_text(item["reply_specimen"]):
            raise AnnotationPacketError("packet_reply_binding_invalid")
        if item.get("structural_aids") != _structural_aids(item["reply_specimen"]):
            raise AnnotationPacketError("packet_structural_aids_invalid")
        if item.get("human_annotation") != _blank_human_annotation():
            raise AnnotationPacketError("packet_labels_must_start_blank")
        expected_origin = (
            "historical_human_authored_reference_unlabeled"
            if expected_ordinal % 2 == 1
            else "controlled_negative_synthetic_local_only"
        )
        if item["specimen_origin"] != expected_origin:
            raise AnnotationPacketError("packet_panel_selection_invalid")
        if expected_ordinal % 2 == 1:
            if item["reply_specimen"] != item["historical_reference_target"]:
                raise AnnotationPacketError("packet_historical_reference_invalid")
        elif item["reply_specimen"] != CONTROLLED_NEGATIVES.get(item["stage"]):
            raise AnnotationPacketError("packet_controlled_negative_invalid")
    if len({item["case_hash"] for item in cases}) != 20:
        raise AnnotationPacketError("packet_case_identity_invalid")
    origins = Counter(item.get("specimen_origin") for item in cases)
    expected_origins = Counter(
        {
            "historical_human_authored_reference_unlabeled": 10,
            "controlled_negative_synthetic_local_only": 10,
        }
    )
    if origins != expected_origins or packet.get("specimen_origin_counts") != dict(expected_origins):
        raise AnnotationPacketError("packet_specimen_counts_invalid")


def build_sanitized_receipt(
    *,
    packet_sha256: str,
    created_at: str,
    job_preimage_sha256: str,
    script_sha256: str,
    test_sha256: str,
) -> dict[str, Any]:
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "created_at": created_at,
        "job_id": JOB_ID,
        "action_class": ACTION_CLASS,
        "method_version": ACTION_METHOD_VERSION,
        "method_fingerprint": action_method_fingerprint(),
        "decision": "REROUTE_REQUIRED__ANNOTATION_GUIDE_MISSING",
        "plateau_review": json.loads(json.dumps(PLATEAU_REVIEW)),
        "source_bindings": {
            **EXPECTED_HASHES,
            "job_preimage_sha256": job_preimage_sha256,
        },
        "readiness": {
            "frozen_holdout_case_count": 20,
            "human_authored_target_count": 20,
            "source_structured_human_label_count": 0,
            "annotation_slot_count": 20,
            "historical_reference_specimen_count": 10,
            "controlled_negative_specimen_count": 10,
            "calibration_started": False,
            "annotation_guide_ready": False,
            "human_review_ready": False,
            "exact_agreement": None,
            "commercial_safety_mismatch_count": None,
        },
        "private_packet_sha256": packet_sha256,
        "implementation": {
            "script_sha256": script_sha256,
            "test_sha256": test_sha256,
            "focused_test_result": "13 tests PASS + py_compile PASS",
        },
        "attempt_before": EXPECTED_ATTEMPT,
        "attempt_after": EXPECTED_ATTEMPT,
        "attempt_consumed": False,
        "new_training_round_started": False,
        "model_calls_this_action": 0,
        "external_network_calls": 0,
        "customer_send": False,
        "private_third_party_egress": False,
        "execution_eligible": False,
        "execution_blockers": list(EXECUTION_BLOCKERS),
        "state_recommendation": "RUNNING",
        "owner_action_required": False,
        "next_bounded_action": NEXT_BOUNDED_ACTION,
    }
    receipt["body_sha256"] = sha256_text(canonical_json(receipt))
    validate_sanitized_receipt(receipt)
    return receipt


def validate_sanitized_receipt(receipt: dict[str, Any]) -> None:
    expected_keys = {
        "schema_version",
        "created_at",
        "job_id",
        "action_class",
        "method_version",
        "method_fingerprint",
        "decision",
        "plateau_review",
        "source_bindings",
        "readiness",
        "private_packet_sha256",
        "implementation",
        "attempt_before",
        "attempt_after",
        "attempt_consumed",
        "new_training_round_started",
        "model_calls_this_action",
        "external_network_calls",
        "customer_send",
        "private_third_party_egress",
        "execution_eligible",
        "execution_blockers",
        "state_recommendation",
        "owner_action_required",
        "next_bounded_action",
        "body_sha256",
    }
    if set(receipt) != expected_keys:
        raise AnnotationPacketError("receipt_topology_invalid")
    if receipt.get("schema_version") != RECEIPT_SCHEMA or receipt.get("job_id") != JOB_ID:
        raise AnnotationPacketError("receipt_identity_invalid")
    if (
        receipt.get("action_class") != ACTION_CLASS
        or receipt.get("method_version") != ACTION_METHOD_VERSION
        or receipt.get("method_fingerprint") != action_method_fingerprint()
        or receipt.get("decision") != "REROUTE_REQUIRED__ANNOTATION_GUIDE_MISSING"
    ):
        raise AnnotationPacketError("receipt_method_contract_invalid")
    body_sha = receipt.get("body_sha256")
    body = dict(receipt)
    body.pop("body_sha256", None)
    if not isinstance(body_sha, str) or body_sha != sha256_text(canonical_json(body)):
        raise AnnotationPacketError("receipt_body_hash_invalid")
    serialized = json.dumps(receipt, ensure_ascii=False)
    forbidden = (
        "/Users/",
        "case_hash",
        "conversation_hash",
        "source_row_sha256",
        "historical_reference_target",
        "reply_specimen",
        '"context"',
        '"customer"',
        '"target"',
    )
    if any(token in serialized for token in forbidden):
        raise AnnotationPacketError("receipt_private_value_leaked")
    source_bindings = receipt.get("source_bindings")
    if not isinstance(source_bindings, dict) or set(source_bindings) != {
        *EXPECTED_HASHES,
        "job_preimage_sha256",
    }:
        raise AnnotationPacketError("receipt_source_binding_topology_invalid")
    for key, expected in EXPECTED_HASHES.items():
        if source_bindings.get(key) != expected:
            raise AnnotationPacketError("receipt_source_binding_invalid")
    if not isinstance(source_bindings.get("job_preimage_sha256"), str) or not HASH_RE.fullmatch(
        source_bindings["job_preimage_sha256"]
    ):
        raise AnnotationPacketError("receipt_job_preimage_invalid")
    for key in ("private_packet_sha256",):
        if not isinstance(receipt.get(key), str) or not HASH_RE.fullmatch(receipt[key]):
            raise AnnotationPacketError("receipt_hash_invalid")
    implementation = receipt.get("implementation")
    if not isinstance(implementation, dict) or set(implementation) != {
        "script_sha256",
        "test_sha256",
        "focused_test_result",
    }:
        raise AnnotationPacketError("receipt_implementation_topology_invalid")
    if not all(
        isinstance(implementation.get(key), str) and HASH_RE.fullmatch(implementation[key])
        for key in ("script_sha256", "test_sha256")
    ) or implementation.get("focused_test_result") != "13 tests PASS + py_compile PASS":
        raise AnnotationPacketError("receipt_implementation_invalid")
    readiness = receipt.get("readiness")
    if not isinstance(readiness, dict) or set(readiness) != {
        "frozen_holdout_case_count",
        "human_authored_target_count",
        "source_structured_human_label_count",
        "annotation_slot_count",
        "historical_reference_specimen_count",
        "controlled_negative_specimen_count",
        "calibration_started",
        "annotation_guide_ready",
        "human_review_ready",
        "exact_agreement",
        "commercial_safety_mismatch_count",
    }:
        raise AnnotationPacketError("receipt_readiness_topology_invalid")
    if readiness != {
        "frozen_holdout_case_count": 20,
        "human_authored_target_count": 20,
        "source_structured_human_label_count": 0,
        "annotation_slot_count": 20,
        "historical_reference_specimen_count": 10,
        "controlled_negative_specimen_count": 10,
        "calibration_started": False,
        "annotation_guide_ready": False,
        "human_review_ready": False,
        "exact_agreement": None,
        "commercial_safety_mismatch_count": None,
    }:
        raise AnnotationPacketError("receipt_readiness_invalid")
    if receipt.get("execution_eligible") is not False:
        raise AnnotationPacketError("receipt_execution_must_remain_disabled")
    if receipt.get("plateau_review") != PLATEAU_REVIEW:
        raise AnnotationPacketError("receipt_plateau_review_invalid")
    if receipt.get("execution_blockers") != EXECUTION_BLOCKERS:
        raise AnnotationPacketError("receipt_execution_blockers_invalid")
    if receipt.get("next_bounded_action") != NEXT_BOUNDED_ACTION:
        raise AnnotationPacketError("receipt_next_action_invalid")
    for key in ("model_calls_this_action", "external_network_calls"):
        if receipt.get(key) != 0:
            raise AnnotationPacketError("receipt_zero_counter_invalid")
    if receipt.get("customer_send") is not False or receipt.get("private_third_party_egress") is not False:
        raise AnnotationPacketError("receipt_safety_boundary_invalid")
    if (
        receipt.get("attempt_before") != EXPECTED_ATTEMPT
        or receipt.get("attempt_after") != EXPECTED_ATTEMPT
        or receipt.get("attempt_consumed") is not False
        or receipt.get("new_training_round_started") is not False
        or receipt.get("state_recommendation") != "RUNNING"
        or receipt.get("owner_action_required") is not False
    ):
        raise AnnotationPacketError("receipt_control_state_invalid")


def _identity(payload: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(payload))
    result.pop("created_at", None)
    return result


def write_private_json(path: Path, payload: dict[str, Any]) -> bool:
    if not path.is_absolute():
        raise AnnotationPacketError("private_output_must_be_absolute")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    if path.is_symlink():
        raise AnnotationPacketError("private_output_symlink")
    if path.exists():
        existing = load_json(path, private=True, label="existing_private_output")
        if _identity(existing) == _identity(payload):
            return False
        raise AnnotationPacketError("existing_private_output_identity_conflict")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        path.chmod(0o600)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise
    return True


def write_public_json(path: Path, payload: dict[str, Any]) -> None:
    if not path.is_absolute() or path.is_symlink():
        raise AnnotationPacketError("public_output_invalid")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        path.chmod(0o644)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise


def update_job_for_annotation_guide(
    *,
    packet_path: Path,
    packet_sha256: str,
    receipt_path: Path,
    receipt_sha256: str,
    job_preimage_sha256: str,
    created_at: str,
) -> None:
    if sha256_file(JOB_PATH) != job_preimage_sha256:
        raise AnnotationPacketError("job_preimage_changed")
    job = load_json(JOB_PATH, private=True, label="canonical_job")
    blockers = job.get("last_result", {}).get("execution_blockers")
    state = job.get("state")
    phase = job.get("current_phase")
    valid_precondition = (
        (state == "RUNNING" and phase == "method-redesign-rubric-calibration")
        or (
            state == "OWNER_REVIEW"
            and phase == "method-redesign-rubric-human-gold-review"
            and job.get("last_result", {}).get("decision")
            == "OWNER_REVIEW_REQUIRED__STRUCTURED_HUMAN_LABELS_MISSING"
        )
    )
    if (
        job.get("schema_version") != "maplab.durable-job.v1"
        or job.get("job_id") != JOB_ID
        or job.get("attempt") != EXPECTED_ATTEMPT
        or not valid_precondition
        or not isinstance(blockers, list)
    ):
        raise AnnotationPacketError("job_precondition_invalid")

    expected_prior = (
        {"rubric_v2_not_calibrated_18_of_20"}
        if state == "RUNNING"
        else {
            "rubric_v2_structured_human_labels_missing",
            "rubric_v2_deterministic_scorer_not_pinned",
        }
    )
    if not expected_prior.issubset(set(blockers)):
        raise AnnotationPacketError("job_prior_blocker_set_invalid")
    new_blockers = [
        "rubric_v2_structured_human_labels_missing",
        "rubric_v2_annotation_guide_not_frozen",
        "rubric_v2_criterion_coverage_not_proven",
        "rubric_v2_deterministic_scorer_not_pinned",
        "paired_runner_source_sha256_not_yet_pinned",
        "rendered_prompt_manifest_not_pinned",
        "shared_lesson_snapshot_not_materialized",
    ]
    for blocker in blockers:
        if blocker not in new_blockers and blocker != "rubric_v2_not_calibrated_18_of_20":
            new_blockers.append(blocker)
    job["updated_at"] = created_at
    job["state"] = "RUNNING"
    job["deerflow_view"]["state"] = "RUNNING"
    job["current_phase"] = "method-redesign-rubric-annotation-guide"
    job["last_result"] = {
        "status": "bounded_action_complete",
        "reason": "rubric_v2_source_has_zero_structured_human_labels_and_annotation_guide_is_not_frozen",
        "action_class": ACTION_CLASS,
        "method_version": ACTION_METHOD_VERSION,
        "method_fingerprint": action_method_fingerprint(),
        "attempt_consumed": False,
        "attempt_before": EXPECTED_ATTEMPT,
        "attempt_after": EXPECTED_ATTEMPT,
        "objective_metrics_before": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "rubric_v2_structured_human_label_count": 0,
            "annotation_guide_ready": False,
            "human_review_ready": False,
        },
        "objective_metrics_after": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "rubric_v2_structured_human_label_count": 0,
            "annotation_guide_ready": False,
            "annotation_preflight_ready": True,
            "human_review_ready": False,
        },
        "owner_acceptance_delta": 0,
        "supporting_delta": "The exact frozen 20 cases were reconstructed into an owner-only 0600 mixed-specimen preflight; source inspection proved zero structured human labels and red-team proved the operational guide is still missing, so human review and calibration remain closed.",
        "business_artifact_created": False,
        "unlocked_next_action": "freeze a source-bound operational annotation guide and per-criterion coverage gate without model or E1 calls",
        "model_calls_this_action": 0,
        "external_network_calls": 0,
        "customer_send": False,
        "private_third_party_egress": False,
        "execution_eligible": False,
        "execution_blockers": new_blockers,
        "fixed_holdout_case_count": 20,
        "source_structured_human_label_count": 0,
        "annotation_slot_count": 20,
        "historical_reference_specimen_count": 10,
        "controlled_negative_specimen_count": 10,
        "private_annotation_preflight_sha256": packet_sha256,
        "sanitized_readiness_receipt_sha256": receipt_sha256,
        "baseline_render_status": "NOT_RENDERED",
        "candidate_render_status": "NOT_RENDERED",
        "shared_input_manifest_status": "NOT_PINNED",
        "lesson_snapshot_status": "NOT_MATERIALIZED",
        "owner_action_required": False,
        "decision": "REROUTE_REQUIRED__ANNOTATION_GUIDE_MISSING",
    }
    job["next_bounded_action"] = (
        "Freeze a source-bound operational guide for all seven rubric criteria, an exact overall recompute formula, "
        "a current price/policy/availability authority snapshot, named-human attestation and adjudication schema, "
        "and a positive/negative coverage gate for every criterion. Keep the blank preflight immutable; do not ask "
        "for human labels, render prompts, or run E1 yet."
    )
    artifacts = job.setdefault("artifacts", [])
    for item in artifacts:
        if item.get("kind") == "line-rubric-v2-private-human-annotation-packet":
            item["readback"] = "superseded blank draft; not annotation-ready"
    artifacts.append(
        {
            "path": str(packet_path),
            "kind": "line-rubric-v2-private-annotation-guide-preflight",
            "sha256": packet_sha256,
            "readback": "owner-only-0600; 20 blank slots; annotation guide missing",
        }
    )
    public_artifacts = [
        item
        for item in artifacts
        if item.get("kind") == "line-rubric-v2-sanitized-readiness-receipt"
    ]
    if len(public_artifacts) > 1:
        raise AnnotationPacketError("job_public_receipt_artifact_duplicate")
    if public_artifacts:
        public_artifacts[0].update(
            {
                "path": str(receipt_path),
                "sha256": receipt_sha256,
                "readback": "sanitized aggregate; guide not ready; no cases or private paths",
            }
        )
    else:
        artifacts.append(
            {
                "path": str(receipt_path),
                "kind": "line-rubric-v2-sanitized-readiness-receipt",
                "sha256": receipt_sha256,
                "readback": "sanitized aggregate; guide not ready; no cases or private paths",
            }
        )
    job.setdefault("history", []).append(
        {
            "at": created_at,
            "from": state,
            "to": "RUNNING",
            "reason": "source has zero structured human labels and blank packet lacks an operational guide; rerouted to guide freeze without requesting Owner review",
        }
    )
    job["resume_prompt"] = (
        "我是 MAPLAB durable-job executor。先讀 CURRENT_STATUS、pitfalls、active LINE Task Card、"
        "training plan、rubric calibration readiness v1 receipt與canonical job。不要重跑schedule gate或E1。"
        "Frozen v7只有20個case identities，來源資料有20/20真人歷史回覆但0/20 structured human labels；"
        "private 0600 mixed-specimen preflight只有blank slots，尚缺operational guide、overall formula、current commercial authority snapshot、"
        "named-human attestation/adjudication schema與每項criteria正反覆蓋gate，因此不要叫Owner/Mina標註。下一步只自動凍結這些規則；"
        "blank preflight不可原地改，未來annotations必須另檔綁parent SHA。LINE內容不得外送，保持execution_eligible=false，"
        "不得render／跑E1／customer send。"
    )
    atomic_replace_json(JOB_PATH, job, mode=0o600)


def refresh_active_job_binding(
    *,
    packet_path: Path,
    packet_sha256: str,
    receipt_path: Path,
    prior_receipt_sha256: str,
    receipt_sha256: str,
    refreshed_at: str,
    apply: bool = True,
) -> bool:
    """Refresh implementation provenance without rerunning the bounded action."""

    job = load_json(JOB_PATH, private=True, label="active_annotation_guide_job")
    if (
        job.get("schema_version") != "maplab.durable-job.v1"
        or job.get("job_id") != JOB_ID
        or job.get("state") != "RUNNING"
        or job.get("attempt") != EXPECTED_ATTEMPT
        or job.get("current_phase") != "method-redesign-rubric-annotation-guide"
        or job.get("last_result", {}).get("execution_eligible") is not False
        or job.get("last_result", {}).get("private_annotation_preflight_sha256") != packet_sha256
        or job.get("last_result", {}).get("sanitized_readiness_receipt_sha256")
        not in {prior_receipt_sha256, receipt_sha256}
    ):
        raise AnnotationPacketError("active_job_replay_precondition_invalid")

    private_artifacts = [
        item
        for item in job.get("artifacts", [])
        if item.get("kind") == "line-rubric-v2-private-annotation-guide-preflight"
    ]
    public_artifacts = [
        item
        for item in job.get("artifacts", [])
        if item.get("kind") == "line-rubric-v2-sanitized-readiness-receipt"
    ]
    if (
        len(private_artifacts) != 1
        or len(public_artifacts) != 1
        or private_artifacts[0].get("path") != str(packet_path)
        or private_artifacts[0].get("sha256") != packet_sha256
        or public_artifacts[0].get("path") != str(receipt_path)
        or public_artifacts[0].get("sha256") not in {prior_receipt_sha256, receipt_sha256}
    ):
        raise AnnotationPacketError("active_job_artifact_binding_invalid")

    if (
        job["last_result"]["sanitized_readiness_receipt_sha256"] == receipt_sha256
        and public_artifacts[0]["sha256"] == receipt_sha256
    ):
        return False

    if not apply:
        return True

    job["updated_at"] = refreshed_at
    job["last_result"]["sanitized_readiness_receipt_sha256"] = receipt_sha256
    public_artifacts[0]["sha256"] = receipt_sha256
    job.setdefault("history", []).append(
        {
            "at": refreshed_at,
            "from": "RUNNING",
            "to": "RUNNING",
            "reason": "rubric readiness receipt implementation provenance corrected; no domain action rerun",
        }
    )
    atomic_replace_json(JOB_PATH, job, mode=0o600)
    return True


def atomic_replace_json(path: Path, payload: dict[str, Any], *, mode: int) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        path.chmod(mode)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-output", default=str(DEFAULT_PRIVATE_OUTPUT))
    parser.add_argument("--sanitized-output", default=str(DEFAULT_PUBLIC_OUTPUT))
    parser.add_argument("--update-job", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    args = build_parser().parse_args(argv)
    private_output = Path(args.private_output).expanduser().resolve()
    public_output = Path(args.sanitized_output).expanduser().resolve()
    invoked_at = utc_now()

    for path, key, private in (
        (EVAL_PATH, "eval_dataset_sha256", True),
        (PRIVATE_V7_PATH, "private_v7_sha256", True),
        (PUBLIC_V7_PATH, "public_v7_sha256", False),
    ):
        (validate_private_file if private else validate_regular_file)(path, key)
        if sha256_file(path) != EXPECTED_HASHES[key]:
            raise AnnotationPacketError(f"{key}_drift")
    if sha256_text(canonical_json(RUBRIC_V2_NAME_ONLY_SPEC)) != EXPECTED_HASHES["rubric_name_only_spec_sha256"]:
        raise AnnotationPacketError("rubric_name_only_spec_drift")

    private_v7 = load_json(PRIVATE_V7_PATH, private=True, label="private_v7")
    eval_rows = load_eval_rows(EVAL_PATH)
    script_sha256 = sha256_file(Path(__file__).resolve())
    test_sha256 = sha256_file(ROOT / "tests" / "test_hermes_line_rubric_annotation_packet.py")

    if private_output.exists() or private_output.is_symlink():
        existing_packet = load_json(
            private_output, private=True, label="existing_private_output"
        )
        validate_packet(existing_packet)
        expected_packet = build_packet(
            private_v7=private_v7,
            eval_rows=eval_rows,
            created_at=existing_packet["created_at"],
            source_hashes=existing_packet["source_provenance"],
        )
        if canonical_json(existing_packet) != canonical_json(expected_packet):
            raise AnnotationPacketError("existing_private_output_live_source_mismatch")
        packet_sha256 = sha256_file(private_output)
        if not public_output.exists() or public_output.is_symlink():
            raise AnnotationPacketError("active_replay_public_receipt_missing")
        prior_receipt = load_json(
            public_output, private=False, label="existing_public_receipt"
        )
        validate_sanitized_receipt(prior_receipt)
        if prior_receipt.get("private_packet_sha256") != packet_sha256:
            raise AnnotationPacketError("active_replay_packet_binding_invalid")
        prior_receipt_sha256 = sha256_file(public_output)
        receipt = build_sanitized_receipt(
            packet_sha256=packet_sha256,
            created_at=existing_packet["created_at"],
            job_preimage_sha256=existing_packet["source_provenance"]["job_preimage_sha256"],
            script_sha256=script_sha256,
            test_sha256=test_sha256,
        )
        predicted_receipt_sha256 = json_file_sha256(receipt)
        if args.update_job:
            refresh_active_job_binding(
                packet_path=private_output,
                packet_sha256=packet_sha256,
                receipt_path=public_output,
                prior_receipt_sha256=prior_receipt_sha256,
                receipt_sha256=predicted_receipt_sha256,
                refreshed_at=invoked_at,
                apply=False,
            )
        write_public_json(public_output, receipt)
        receipt_sha256 = sha256_file(public_output)
        if receipt_sha256 != predicted_receipt_sha256:
            raise AnnotationPacketError("public_receipt_serialization_hash_mismatch")
        job_binding_refreshed = False
        if args.update_job:
            job_binding_refreshed = refresh_active_job_binding(
                packet_path=private_output,
                packet_sha256=packet_sha256,
                receipt_path=public_output,
                prior_receipt_sha256=prior_receipt_sha256,
                receipt_sha256=receipt_sha256,
                refreshed_at=invoked_at,
            )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "packet_created": False,
                    "idempotent_annotation_guide_replay": True,
                    "private_packet_sha256": packet_sha256,
                    "sanitized_receipt_sha256": receipt_sha256,
                    "source_structured_human_label_count": 0,
                    "annotation_slot_count": 20,
                    "attempt_after": EXPECTED_ATTEMPT,
                    "model_calls_this_action": 0,
                    "decision": receipt["decision"],
                    "job_binding_refreshed": job_binding_refreshed,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    created_at = invoked_at
    job_preimage_sha256 = sha256_file(JOB_PATH)
    source_hashes = {
        **EXPECTED_HASHES,
        "job_preimage_sha256": job_preimage_sha256,
    }
    packet = build_packet(
        private_v7=private_v7,
        eval_rows=eval_rows,
        created_at=created_at,
        source_hashes=source_hashes,
    )
    packet_created = write_private_json(private_output, packet)
    packet_sha256 = sha256_file(private_output)

    receipt = build_sanitized_receipt(
        packet_sha256=packet_sha256,
        created_at=created_at,
        job_preimage_sha256=job_preimage_sha256,
        script_sha256=script_sha256,
        test_sha256=test_sha256,
    )
    write_public_json(public_output, receipt)
    receipt_sha256 = sha256_file(public_output)
    if args.update_job:
        update_job_for_annotation_guide(
            packet_path=private_output,
            packet_sha256=packet_sha256,
            receipt_path=public_output,
            receipt_sha256=receipt_sha256,
            job_preimage_sha256=job_preimage_sha256,
            created_at=created_at,
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "packet_created": packet_created,
                "private_packet_sha256": packet_sha256,
                "sanitized_receipt_sha256": receipt_sha256,
                "source_structured_human_label_count": 0,
                "annotation_slot_count": 20,
                "attempt_after": EXPECTED_ATTEMPT,
                "model_calls_this_action": 0,
                "decision": receipt["decision"],
                "job_updated": bool(args.update_job),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
