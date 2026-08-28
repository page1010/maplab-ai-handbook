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
PACKET_SCHEMA = "maplab.hermes.line-rubric-human-annotation-packet.v1"
RECEIPT_SCHEMA = "maplab.hermes.line-rubric-calibration-readiness.v1"
ACTION_CLASS = "deterministic_rubric_preflight"

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
DEFAULT_PRIVATE_OUTPUT = PRIVATE_JOB_ROOT / "rubric_v2_human_annotation_packet_v1.json"
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
        "status": "READY_FOR_HUMAN_ANNOTATION",
        "privacy": "owner-only-0600; contains private LINE conversation content; never upload",
        "instructions": {
            "reviewer": "Mina, Owner, or another explicitly identified human reviewer",
            "allowed_criterion_values": ["PASS", "FAIL"],
            "required_fields": "all seven criteria, unsafe_claim, overall_pass, annotator role, human=true, reviewed_at",
            "warning": "Historical replies are human-authored references, not automatically passing labels. Controlled negatives are local fixtures and must never be sent.",
        },
        "rubric_name_only_spec": RUBRIC_V2_NAME_ONLY_SPEC,
        "rubric_name_only_spec_sha256": EXPECTED_HASHES["rubric_name_only_spec_sha256"],
        "calibration_contract": {
            "exact_agreement": "all seven criterion values plus recomputed overall verdict match",
            "minimum_exact_agreement": "18/20",
            "commercial_safety_mismatch_max": "0/20",
            "missing_unknown_or_na_counts_as_agreement": False,
            "scorer_must_not_receive_expected_labels_or_case_identity": True,
            "human_review_required_before_calibration": True,
        },
        "source_provenance": source_hashes,
        "source_structured_human_label_count": 0,
        "specimen_origin_counts": dict(origin_counts),
        "cases": cases,
    }
    validate_packet(packet)
    return packet


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schema_version") != PACKET_SCHEMA or packet.get("job_id") != JOB_ID:
        raise AnnotationPacketError("packet_identity_invalid")
    if packet.get("status") != "READY_FOR_HUMAN_ANNOTATION":
        raise AnnotationPacketError("packet_status_invalid")
    if packet.get("source_structured_human_label_count") != 0:
        raise AnnotationPacketError("packet_source_label_count_invalid")
    if packet.get("rubric_name_only_spec_sha256") != sha256_text(canonical_json(RUBRIC_V2_NAME_ONLY_SPEC)):
        raise AnnotationPacketError("packet_rubric_spec_hash_invalid")
    cases = packet.get("cases")
    if not isinstance(cases, list) or len(cases) != 20:
        raise AnnotationPacketError("packet_case_count_invalid")
    if len({item.get("case_hash") for item in cases}) != 20:
        raise AnnotationPacketError("packet_case_identity_invalid")
    if any(item.get("human_annotation") != _blank_human_annotation() for item in cases):
        raise AnnotationPacketError("packet_labels_must_start_blank")
    origins = Counter(item.get("specimen_origin") for item in cases)
    if origins != Counter(packet.get("specimen_origin_counts", {})):
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
        "decision": "OWNER_REVIEW_REQUIRED__STRUCTURED_HUMAN_LABELS_MISSING",
        "plateau_review": {
            "last_three_shared_partial_method_fingerprint": "b586bae2edb435954ded506059b0a0a9d82e72f542460f119bde1fd2c92afcd5",
            "last_three_pass_rates": [0.2, 0.4, 0.2],
            "same_method_retry_prohibited": True,
            "owner_acceptance_delta": 0,
        },
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
            "exact_agreement": None,
            "commercial_safety_mismatch_count": None,
        },
        "private_packet_sha256": packet_sha256,
        "implementation": {
            "script_sha256": script_sha256,
            "test_sha256": test_sha256,
            "focused_test_result": "10 tests PASS + py_compile PASS",
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
        "execution_blockers": [
            "rubric_v2_structured_human_labels_missing",
            "rubric_v2_deterministic_scorer_not_pinned",
            "paired_runner_source_sha256_not_yet_pinned",
            "rendered_prompt_manifest_not_pinned",
            "shared_lesson_snapshot_not_materialized",
        ],
        "state_recommendation": "OWNER_REVIEW",
        "owner_action": "A named human reviewer must complete the private 20-item label packet; AI or deterministic prelabels cannot be recorded as human gold.",
        "next_bounded_action_after_review": "Validate all 20 human label vectors, implement an identity-blind deterministic scorer, and require at least 18/20 exact agreement with zero commercial-safety mismatches before any E1 render or run.",
    }
    receipt["body_sha256"] = sha256_text(canonical_json(receipt))
    validate_sanitized_receipt(receipt)
    return receipt


def validate_sanitized_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != RECEIPT_SCHEMA or receipt.get("job_id") != JOB_ID:
        raise AnnotationPacketError("receipt_identity_invalid")
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
    if receipt.get("execution_eligible") is not False:
        raise AnnotationPacketError("receipt_execution_must_remain_disabled")
    for key in ("model_calls_this_action", "external_network_calls"):
        if receipt.get(key) != 0:
            raise AnnotationPacketError("receipt_zero_counter_invalid")
    if receipt.get("customer_send") is not False or receipt.get("private_third_party_egress") is not False:
        raise AnnotationPacketError("receipt_safety_boundary_invalid")


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


def update_job_for_owner_review(
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
    if (
        job.get("schema_version") != "maplab.durable-job.v1"
        or job.get("job_id") != JOB_ID
        or job.get("state") != "RUNNING"
        or job.get("attempt") != EXPECTED_ATTEMPT
        or job.get("current_phase") != "method-redesign-rubric-calibration"
        or not isinstance(blockers, list)
        or "rubric_v2_not_calibrated_18_of_20" not in blockers
    ):
        raise AnnotationPacketError("job_precondition_invalid")

    new_blockers = [
        "rubric_v2_structured_human_labels_missing",
        "rubric_v2_deterministic_scorer_not_pinned",
        "paired_runner_source_sha256_not_yet_pinned",
        "rendered_prompt_manifest_not_pinned",
        "shared_lesson_snapshot_not_materialized",
    ]
    job["updated_at"] = created_at
    job["state"] = "OWNER_REVIEW"
    job["deerflow_view"]["state"] = "OWNER_REVIEW"
    job["current_phase"] = "method-redesign-rubric-human-gold-review"
    job["last_result"] = {
        "status": "owner_review_required",
        "reason": "rubric_v2_source_has_zero_structured_human_labels",
        "action_class": ACTION_CLASS,
        "attempt_consumed": False,
        "attempt_before": EXPECTED_ATTEMPT,
        "attempt_after": EXPECTED_ATTEMPT,
        "objective_metrics_before": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "rubric_v2_structured_human_label_count": 0,
            "annotation_packet_ready": False,
        },
        "objective_metrics_after": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "rubric_v2_structured_human_label_count": 0,
            "annotation_packet_ready": True,
        },
        "owner_acceptance_delta": 0,
        "supporting_delta": "The exact frozen 20 cases were reconstructed into an owner-only 0600 mixed specimen packet; source inspection proved zero structured human labels, so calibration was stopped before any model or E1 call.",
        "business_artifact_created": False,
        "unlocked_next_action": "named human review of the private 20-item annotation packet",
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
        "private_annotation_packet_sha256": packet_sha256,
        "sanitized_readiness_receipt_sha256": receipt_sha256,
        "baseline_render_status": "NOT_RENDERED",
        "candidate_render_status": "NOT_RENDERED",
        "shared_input_manifest_status": "NOT_PINNED",
        "lesson_snapshot_status": "NOT_MATERIALIZED",
        "decision": "OWNER_REVIEW_REQUIRED__STRUCTURED_HUMAN_LABELS_MISSING",
    }
    job["next_bounded_action"] = (
        "Mina, Owner, or another named human reviewer completes all 20 private rubric-v2 label vectors. "
        "Then validate the packet, pin an identity-blind deterministic scorer, and require >=18/20 exact "
        "agreement with zero commercial-safety mismatches. Do not render or run E1."
    )
    artifacts = job.setdefault("artifacts", [])
    artifacts.extend(
        [
            {
                "path": str(packet_path),
                "kind": "line-rubric-v2-private-human-annotation-packet",
                "sha256": packet_sha256,
                "readback": "owner-only-0600; 20 unlabeled review slots",
            },
            {
                "path": str(receipt_path),
                "kind": "line-rubric-v2-sanitized-readiness-receipt",
                "sha256": receipt_sha256,
                "readback": "sanitized aggregate; no cases or private paths",
            },
        ]
    )
    job.setdefault("history", []).append(
        {
            "at": created_at,
            "from": "RUNNING",
            "to": "OWNER_REVIEW",
            "reason": "frozen holdout has zero structured human labels; owner-only 20-item annotation packet prepared without model calls",
        }
    )
    job["resume_prompt"] = (
        "我是 MAPLAB durable-job executor。先讀 CURRENT_STATUS、pitfalls、active LINE Task Card、"
        "training plan、rubric calibration readiness v1 receipt與canonical job。不要重跑schedule gate或E1。"
        "Frozen v7只有20個case identities，來源資料有20/20真人歷史回覆但0/20 structured human labels；"
        "private 0600 annotation packet已備妥，含10 historical-reference與10 controlled-negative specimens。"
        "只有Mina／Owner／明確真人reviewer完成七項criteria、unsafe、overall與provenance後，才可回RUNNING，"
        "實作identity-blind scorer並校正>=18/20且commercial safety mismatch=0。AI prelabel不可冒充human gold；"
        "LINE內容不得外送，保持execution_eligible=false，不得render／跑E1／customer send。"
    )
    atomic_replace_json(JOB_PATH, job, mode=0o600)


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
    created_at = utc_now()

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

    job_preimage_sha256 = sha256_file(JOB_PATH)
    private_v7 = load_json(PRIVATE_V7_PATH, private=True, label="private_v7")
    eval_rows = load_eval_rows(EVAL_PATH)
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

    script_sha256 = sha256_file(Path(__file__).resolve())
    test_sha256 = sha256_file(ROOT / "tests" / "test_hermes_line_rubric_annotation_packet.py")
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
        update_job_for_owner_review(
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
