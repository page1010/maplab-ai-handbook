#!/usr/bin/env python3
"""Freeze a zero-model Hermes LINE method-redesign audit.

The source dataset and historical round receipts contain private business
conversations.  This tool reads them locally, emits only aggregate metrics and
opaque hashes, freezes a balanced holdout/few-shot manifest, and detects runs
created after the supervisor entered its plateau pause.  It never invokes a
model, writes customer-facing systems, or copies raw text into either receipt.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import plistlib
import re
import stat
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


AUDIT_SCHEMA = "maplab.hermes.line-method-redesign-audit.v7"
SANITIZED_SCHEMA = "maplab.hermes.line-method-redesign-sanitized.v7"
AUDIT_METHOD_VERSION = "hermes-line-method-redesign-audit-v7"
EXPERIMENT_METHOD_VERSION = "line-reply-e1-prompt-only-v1"
EXPECTED_JOB_ID = "MAPJOB-20260827-224251-d291ad"
EXPECTED_ATTEMPT = 6
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_FUTURE_CLOCK_SKEW_SECONDS = 300

HOLDOUT_STAGE_QUOTAS = {
    "data": ("S2_DATA", 4),
    "dietary": ("S2_DIETARY", 4),
    "quote_intro": ("S3_QUOTE_INTRO", 2),
    "quote_send": ("S3_QUOTE_SEND", 2),
    "payment": ("S4_PAYMENT", 4),
    "followup": ("S_PENDING", 4),
}
FEW_SHOT_PER_HOLDOUT_CASE = 2
CANDIDATE_SYSTEM_PROMPT_TEMPLATE = (
    "MAPLAB structured reply prompt: first derive known, missing, and forbidden facts internally; "
    "output only a short Traditional-Chinese reply that answers the current question, asks at most "
    "three necessary questions, never re-asks known facts, and never invents price, availability, "
    "or policy; append the same pinned lesson snapshot and pinned two-shot examples."
)
RUBRIC_V2_SPEC = {
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
ACCEPTANCE_SPEC = {
    "version": "line-reply-e1-acceptance-v1",
    "paired_net_pass_improvement_min": "4/20",
    "correct_answer_and_next_question_min": "18/20",
    "reask_known_max": "1/20",
    "at_most_three_questions_min": "19/20",
    "unsafe_claims": 0,
    "max_stage_regression": 1,
}
REQUIRED_METHOD_FIELDS = (
    "adapter",
    "model_digest",
    "prompt_sha256",
    "lesson_sha256",
    "sampling_manifest_sha256",
    "evaluator_version",
    "acceptance_version",
)
LEGACY_MISSING_METHOD_FIELDS = (
    "prompt_sha256",
    "lesson_sha256",
    "sampling_manifest_sha256",
    "acceptance_version",
    "model_digest",
)

AUDIT_TOP_LEVEL_KEYS = {
    "schema_version",
    "created_at",
    "job_id",
    "audit_method_version",
    "attempt_before",
    "attempt_after",
    "attempt_consumed",
    "model_calls_this_action",
    "external_network_calls",
    "customer_send",
    "private_third_party_egress",
    "supervisor_analysis",
    "schedule_analysis",
    "fixed_holdout",
    "fixed_few_shot",
    "experiment_contract",
    "objective_metrics_before",
    "objective_metrics_after",
    "owner_acceptance_delta",
    "supporting_delta",
    "business_artifact_created",
    "unlocked_next_action",
    "first_principles",
    "decision",
    "next_bounded_action",
    "implementation_provenance",
}

IMPLEMENTATION_PROVENANCE_KEYS = {
    "audit_script_sha256",
    "audit_test_sha256",
    "canonical_job_sha256",
    "model_manifest_sha256",
    "supervisor_receipt_sha256",
    "required_method_fields",
    "rubric_v2_spec_sha256",
    "acceptance_spec_sha256",
}

SANITIZED_TOP_LEVEL_KEYS = {
    "schema_version",
    "created_at",
    "job_id",
    "audit_method_version",
    "private_audit_sha256",
    "attempt_before",
    "attempt_after",
    "attempt_consumed",
    "model_calls_this_action",
    "external_network_calls",
    "customer_send",
    "private_third_party_egress",
    "last_three_method_review",
    "call_accounting",
    "supervised_failure_taxonomy",
    "post_pause_bypass",
    "schedule_analysis",
    "fixed_holdout",
    "fixed_few_shot",
    "experiment_contract",
    "objective_metrics_before",
    "objective_metrics_after",
    "owner_acceptance_delta",
    "supporting_delta",
    "business_artifact_created",
    "unlocked_next_action",
    "first_principles",
    "decision",
    "next_bounded_action",
    "implementation_provenance",
    "body_sha256",
}


class MethodAuditError(RuntimeError):
    """The audit could not prove its fail-closed contract."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def function_source_sha256(path: Path, function_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise MethodAuditError("prompt_builder_source_invalid") from error
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            if node.end_lineno is None:
                raise MethodAuditError("prompt_builder_source_range_missing")
            lines = source.splitlines(keepends=True)
            return sha256_text("".join(lines[node.lineno - 1 : node.end_lineno]))
    raise MethodAuditError("prompt_builder_source_missing")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise MethodAuditError(f"{label}_timestamp_invalid")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise MethodAuditError(f"{label}_timestamp_invalid") from error
    if parsed.tzinfo is None:
        raise MethodAuditError(f"{label}_timestamp_naive")
    return parsed


def validate_private_dir(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise MethodAuditError(f"{label}_private_dir_invalid")
    info = path.stat()
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise MethodAuditError(f"{label}_wrong_owner")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise MethodAuditError(f"{label}_permissions_not_private")


def validate_private_file(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise MethodAuditError(f"{label}_private_file_invalid")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise MethodAuditError(f"{label}_not_single_regular_file")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise MethodAuditError(f"{label}_wrong_owner")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise MethodAuditError(f"{label}_permissions_not_private")


def validate_regular_file(path: Path, label: str) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise MethodAuditError(f"{label}_file_invalid")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise MethodAuditError(f"{label}_not_single_regular_file")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise MethodAuditError(f"{label}_wrong_owner")


def canonical_source_context() -> dict[str, Path]:
    root = Path(__file__).resolve().parents[1]
    data_root = (Path.home() / ".maplab" / "a6-hermes-training").resolve()
    supervisor_job_root = data_root / "supervisor_jobs" / EXPECTED_JOB_ID
    return {
        "data_root": data_root,
        "supervisor_receipt": (supervisor_job_root / "receipt.json").resolve(),
        "repo_plist": (root / "config" / "launchd" / "com.maplab.hermes-line-training.plist").resolve(),
        "installed_plist": (Path.home() / "Library" / "LaunchAgents" / "com.maplab.hermes-line-training.plist").resolve(),
        "training_loop": (root / "scripts" / "hermes_line_training_loop.py").resolve(),
        "supervisor_script": (root / "scripts" / "hermes_line_training_supervisor.py").resolve(),
        "model_manifest": (
            Path.home()
            / ".ollama"
            / "models"
            / "manifests"
            / "registry.ollama.ai"
            / "library"
            / "gemma4"
            / "latest"
        ).resolve(),
        "job_path": (
            root
            / "workbook"
            / "reviews"
            / "MAPLAB-DURABLE-JOBS"
            / EXPECTED_JOB_ID
            / "job.json"
        ).resolve(),
    }


def validate_source_context(source_context: dict[str, Path], *, enforce_canonical: bool) -> None:
    expected_keys = {
        "data_root",
        "supervisor_receipt",
        "repo_plist",
        "installed_plist",
        "training_loop",
        "supervisor_script",
        "model_manifest",
        "job_path",
    }
    if not isinstance(source_context, dict) or set(source_context) != expected_keys:
        raise MethodAuditError("source_context_topology_invalid")
    if not all(isinstance(value, Path) and value.is_absolute() for value in source_context.values()):
        raise MethodAuditError("source_context_path_invalid")
    if enforce_canonical:
        canonical = canonical_source_context()
        if any(source_context[key].resolve() != canonical[key] for key in expected_keys):
            raise MethodAuditError("canonical_source_path_mismatch")
    validate_private_dir(source_context["data_root"], "source_data_root")
    validate_private_file(source_context["supervisor_receipt"], "source_supervisor_receipt")
    validate_private_file(source_context["job_path"], "source_canonical_job")
    validate_private_file(source_context["data_root"] / "current_lessons.md", "source_current_lessons")
    for key in ("repo_plist", "installed_plist", "training_loop", "supervisor_script", "model_manifest"):
        validate_regular_file(source_context[key], f"source_{key}")


def load_private_json(path: Path, label: str) -> dict:
    validate_private_file(path, label)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MethodAuditError(f"{label}_json_invalid") from error
    if not isinstance(payload, dict):
        raise MethodAuditError(f"{label}_json_not_object")
    return payload


def load_private_jsonl(path: Path, label: str) -> list[dict]:
    validate_private_file(path, label)
    rows: list[dict] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise MethodAuditError(f"{label}_row_invalid")
                if not all(isinstance(row.get(key), str) and row[key] for key in ("id", "stage", "conversation_id")):
                    raise MethodAuditError(f"{label}_identity_invalid")
                rows.append(row)
    except MethodAuditError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MethodAuditError(f"{label}_jsonl_invalid") from error
    if not rows:
        raise MethodAuditError(f"{label}_empty")
    identifiers = [row["id"] for row in rows]
    if len(set(identifiers)) != len(identifiers):
        raise MethodAuditError(f"{label}_duplicate_id")
    return rows


def _selection_key(role: str, stage: str, record_id: str) -> str:
    return sha256_text(f"{EXPERIMENT_METHOD_VERSION}|{role}|{stage}|{record_id}")


def _opaque_case_hash(role: str, stage: str, record_id: str) -> str:
    return sha256_text(f"{EXPERIMENT_METHOD_VERSION}|opaque-{role}|{stage}|{record_id}")


def _opaque_conversation_hash(role: str, conversation_id: str) -> str:
    return sha256_text(f"{EXPERIMENT_METHOD_VERSION}|opaque-{role}-conversation|{conversation_id}")


def select_holdout_manifest(
    rows: list[dict], *, excluded_record_ids: set[str], excluded_conversation_ids: set[str]
) -> tuple[list[dict], list[dict]]:
    selected: list[dict] = []
    selected_source_rows: list[dict] = []
    for stratum, (stage, per_stage) in HOLDOUT_STAGE_QUOTAS.items():
        candidates = sorted(
            (
                row
                for row in rows
                if row["stage"] == stage
                and row["id"] not in excluded_record_ids
                and row["conversation_id"] not in excluded_conversation_ids
            ),
            key=lambda row: _selection_key("holdout", stage, row["id"]),
        )
        seen_conversations: set[str] = set()
        chosen: list[dict] = []
        for row in candidates:
            if row["conversation_id"] in seen_conversations:
                continue
            seen_conversations.add(row["conversation_id"])
            chosen.append(
                {
                    "stratum": stratum,
                    "stage": stage,
                    "case_hash": _opaque_case_hash("holdout", stage, row["id"]),
                    "conversation_hash": _opaque_conversation_hash("holdout", row["conversation_id"]),
                    "selection_key": _selection_key("holdout", stage, row["id"]),
                }
            )
            selected_source_rows.append(row)
            if len(chosen) == per_stage:
                break
        if len(chosen) != per_stage:
            raise MethodAuditError("holdout_stage_quota_unavailable")
        selected.extend(chosen)
    hashes = [row["case_hash"] for row in selected]
    conversations = [row["conversation_hash"] for row in selected]
    if len(set(hashes)) != len(hashes) or len(set(conversations)) != len(conversations):
        raise MethodAuditError("holdout_manifest_not_unique")
    return selected, selected_source_rows


def select_few_shot_manifest(train_rows: list[dict], holdout: list[dict]) -> list[dict]:
    mappings: list[dict] = []
    used_record_ids: set[str] = set()
    used_conversations: set[str] = set()
    for holdout_row in holdout:
        stage = holdout_row["stage"]
        holdout_hash = holdout_row["case_hash"]
        candidates = sorted(
            (row for row in train_rows if row["stage"] == stage),
            key=lambda row: sha256_text(
                f"{EXPERIMENT_METHOD_VERSION}|few-shot|{holdout_hash}|{row['id']}"
            ),
        )
        examples: list[dict] = []
        for row in candidates:
            if row["id"] in used_record_ids or row["conversation_id"] in used_conversations:
                continue
            used_record_ids.add(row["id"])
            used_conversations.add(row["conversation_id"])
            examples.append(
                {
                    "case_hash": _opaque_case_hash("few-shot", stage, row["id"]),
                    "conversation_hash": _opaque_conversation_hash("few-shot", row["conversation_id"]),
                    "selection_key": sha256_text(
                        f"{EXPERIMENT_METHOD_VERSION}|few-shot|{holdout_hash}|{row['id']}"
                    ),
                }
            )
            if len(examples) == FEW_SHOT_PER_HOLDOUT_CASE:
                break
        if len(examples) != FEW_SHOT_PER_HOLDOUT_CASE:
            raise MethodAuditError("few_shot_stage_quota_unavailable")
        mappings.append(
            {
                "holdout_case_hash": holdout_hash,
                "stage": stage,
                "examples": examples,
            }
        )
    flat = [item for mapping in mappings for item in mapping["examples"]]
    if len(flat) != 40 or len({item["case_hash"] for item in flat}) != 40:
        raise MethodAuditError("few_shot_manifest_not_unique")
    return mappings


def manifest_digest(rows: list[dict]) -> str:
    return sha256_text(canonical_json(rows))


def collect_exposed_eval_ids(data_root: Path) -> tuple[set[str], int, str]:
    run_root = data_root / "runs"
    validate_private_dir(run_root, "exposed_run_root")
    identifiers: set[str] = set()
    occurrences = 0
    for path in sorted(run_root.glob("*.json")):
        payload = load_private_json(path, "exposed_run_receipt")
        results = payload.get("results")
        if not isinstance(results, list):
            raise MethodAuditError("exposed_run_results_invalid")
        for result in results:
            if not isinstance(result, dict) or not isinstance(result.get("id"), str):
                raise MethodAuditError("exposed_run_result_id_invalid")
            identifiers.add(result["id"])
            occurrences += 1
    opaque = sorted(
        sha256_text(f"{EXPERIMENT_METHOD_VERSION}|prior-exposure|{identifier}")
        for identifier in identifiers
    )
    return identifiers, occurrences, sha256_text("".join(f"{value}\n" for value in opaque))


def evaluation_metrics(results: list[dict]) -> dict:
    buckets: Counter[str] = Counter()
    stages: Counter[str] = Counter()
    scores: list[float] = []
    identifiers: set[str] = set()
    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get("id"), str) or not isinstance(result.get("stage"), str):
            raise MethodAuditError("round_result_identity_invalid")
        evaluation = result.get("evaluation")
        if not isinstance(evaluation, dict):
            raise MethodAuditError("round_evaluation_invalid")
        required = evaluation.get("required_signals")
        hits = evaluation.get("hit_signals")
        unsupported = evaluation.get("unsupported_money")
        if not isinstance(required, list) or not isinstance(hits, list) or not isinstance(unsupported, list):
            raise MethodAuditError("round_evaluation_lists_invalid")
        score = evaluation.get("score")
        ratio = evaluation.get("length_ratio")
        passed = evaluation.get("pass")
        question_ok = evaluation.get("question_ok")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise MethodAuditError("round_score_invalid")
        if isinstance(ratio, bool) or not isinstance(ratio, (int, float)):
            raise MethodAuditError("round_length_ratio_invalid")
        if not isinstance(passed, bool) or not isinstance(question_ok, bool):
            raise MethodAuditError("round_gate_type_invalid")
        coverage = len(hits) / len(required) if required else 1.0
        identifiers.add(result["id"])
        stages[result["stage"]] += 1
        scores.append(float(score))
        if not passed:
            buckets["failed"] += 1
        if not 0.25 <= float(ratio) <= 2.5:
            buckets["length_gate_failed"] += 1
        if coverage < 0.75:
            buckets["signal_coverage_failed"] += 1
        if unsupported:
            buckets["unsupported_money"] += 1
        if not question_ok:
            buckets["question_gate_failed"] += 1
        if float(score) < 75:
            buckets["score_below_75"] += 1
        if float(score) >= 75 and not passed:
            buckets["high_score_but_failed"] += 1
    return {
        "result_count": len(results),
        "unique_case_count": len(identifiers),
        "pass_count": sum(bool(row["evaluation"]["pass"]) for row in results),
        "pass_rate": round(
            sum(bool(row["evaluation"]["pass"]) for row in results) / max(len(results), 1),
            4,
        ),
        "mean_score": round(sum(scores) / max(len(scores), 1), 2),
        "failure_buckets": dict(sorted(buckets.items())),
        "stage_counts": dict(sorted(stages.items())),
    }


def validate_metrics_payload(metrics: object, label: str) -> None:
    expected_keys = {
        "result_count",
        "unique_case_count",
        "pass_count",
        "pass_rate",
        "mean_score",
        "failure_buckets",
        "stage_counts",
    }
    if not isinstance(metrics, dict) or set(metrics) != expected_keys:
        raise MethodAuditError(f"{label}_topology_invalid")
    for key in ("result_count", "unique_case_count", "pass_count"):
        if type(metrics.get(key)) is not int or metrics[key] < 0:
            raise MethodAuditError(f"{label}_count_invalid")
    for key in ("pass_rate", "mean_score"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise MethodAuditError(f"{label}_metric_invalid")
    for key in ("failure_buckets", "stage_counts"):
        values = metrics.get(key)
        if not isinstance(values, dict) or not all(
            isinstance(name, str) and name and type(count) is int and count >= 0
            for name, count in values.items()
        ):
            raise MethodAuditError(f"{label}_{key}_invalid")


def _round_path(data_root: Path, value: object) -> Path:
    if not isinstance(value, str):
        raise MethodAuditError("round_receipt_path_invalid")
    path = Path(value)
    validate_private_file(path, "round_receipt")
    if path.parent.resolve() != (data_root / "runs").resolve():
        raise MethodAuditError("round_receipt_outside_data_root")
    return path


def analyze_supervisor(data_root: Path, supervisor_path: Path) -> dict:
    supervisor = load_private_json(supervisor_path, "supervisor_receipt")
    if supervisor.get("schema_version") != "maplab.hermes.line-supervisor.v1":
        raise MethodAuditError("supervisor_schema_invalid")
    if supervisor.get("job_id") != EXPECTED_JOB_ID:
        raise MethodAuditError("supervisor_job_id_mismatch")
    if supervisor.get("method_review_required") is not True or supervisor.get("status") != "bounded_pause":
        raise MethodAuditError("supervisor_not_in_method_review")
    rounds = supervisor.get("rounds")
    if not isinstance(rounds, list) or len(rounds) < 3:
        raise MethodAuditError("supervisor_rounds_insufficient")
    contract = supervisor.get("qualification_contract")
    if not isinstance(contract, dict):
        raise MethodAuditError("supervisor_contract_invalid")

    supervised_paths: set[Path] = set()
    supervised_created_times: list[datetime] = []
    supervised_results: list[dict] = []
    round_summaries: list[dict] = []
    last_supervised_lesson_delta_sha256: str | None = None
    for row in rounds:
        if not isinstance(row, dict):
            raise MethodAuditError("supervisor_round_row_invalid")
        path = _round_path(data_root, row.get("receipt"))
        expected_sha = row.get("receipt_sha256")
        if not isinstance(expected_sha, str) or not HASH_RE.fullmatch(expected_sha):
            raise MethodAuditError("supervisor_round_sha_invalid")
        if sha256_file(path) != expected_sha:
            raise MethodAuditError("supervisor_round_sha_mismatch")
        payload = load_private_json(path, "round_receipt")
        if payload.get("schema_version") != "maplab.hermes.line-run.v2":
            raise MethodAuditError("round_schema_invalid")
        results = payload.get("results")
        if not isinstance(results, list):
            raise MethodAuditError("round_results_invalid")
        supervised_paths.add(path.resolve())
        supervised_created_times.append(
            parse_time(payload.get("created_at"), "supervised_round_created_at")
        )
        supervised_results.extend(results)
        lesson_delta_value = payload.get("lesson_delta")
        if not isinstance(lesson_delta_value, str):
            raise MethodAuditError("round_lesson_delta_path_invalid")
        lesson_delta_path = Path(lesson_delta_value)
        validate_private_file(lesson_delta_path, "round_lesson_delta")
        if lesson_delta_path.parent.resolve() != (data_root / "lesson_deltas").resolve():
            raise MethodAuditError("round_lesson_delta_outside_data_root")
        last_supervised_lesson_delta_sha256 = sha256_file(lesson_delta_path)
        round_summaries.append(
            {
                "receipt_sha256": expected_sha,
                "pass_rate": payload.get("pass_rate"),
                "unsupported_price_rate": payload.get("unsupported_price_rate"),
                "lowest_stage": payload.get("lowest_stage"),
                "seed": payload.get("seed"),
                "model": payload.get("model"),
                "evaluator_version": payload.get("evaluator_version"),
                "output_lesson_delta_sha256": last_supervised_lesson_delta_sha256,
            }
        )

    partial_method = {
        "adapter": "hermes-line-training-supervisor",
        "model": contract.get("model"),
        "inference_parameters": contract.get("inference_parameters"),
        "evaluator_version": contract.get("evaluator_version"),
        "base_batch": contract.get("base_batch"),
        "requested_stage": contract.get("requested_stage"),
        "sampling": "seeded random sample; no fixed case manifest in receipt",
        "acceptance": {
            "target_pass_rate": contract.get("target_pass_rate"),
            "target_streak": contract.get("target_streak"),
        },
    }
    partial_fingerprint = sha256_text(canonical_json(partial_method))
    last_three = []
    for row in round_summaries[-3:]:
        last_three.append(row | {"partial_method_fingerprint": partial_fingerprint})

    cutoff = max(supervised_created_times)
    bypass_results: list[dict] = []
    bypass_runs: list[dict] = []
    physical_explicit_calls = 0
    physical_missing_call_counter = 0
    physical_run_receipt_count = 0
    run_root = data_root / "runs"
    validate_private_dir(run_root, "run_root")
    for path in sorted(run_root.glob("*.json")):
        validate_private_file(path, "run_inventory_receipt")
        payload = load_private_json(path, "run_inventory_receipt")
        physical_run_receipt_count += 1
        inventory_calls = payload.get("loopback_ollama_calls")
        if isinstance(inventory_calls, bool) or not isinstance(inventory_calls, int):
            physical_missing_call_counter += 1
        else:
            physical_explicit_calls += inventory_calls
        created_at = parse_time(payload.get("created_at"), "run_created_at")
        if path.resolve() in supervised_paths or created_at <= cutoff:
            continue
        results = payload.get("results")
        calls = payload.get("loopback_ollama_calls")
        if not isinstance(results, list) or isinstance(calls, bool) or not isinstance(calls, int):
            raise MethodAuditError("post_plateau_run_invalid")
        bypass_results.extend(results)
        bypass_runs.append(
            {
                "receipt_sha256": sha256_file(path),
                "created_at": payload["created_at"],
                "loopback_ollama_calls": calls,
                "pass_rate": payload.get("pass_rate"),
                "unsupported_price_count": payload.get("unsupported_price_count"),
            }
        )

    supervised_calls = supervisor.get("loopback_ollama_calls")
    if isinstance(supervised_calls, bool) or not isinstance(supervised_calls, int):
        raise MethodAuditError("supervisor_call_count_invalid")
    bypass_calls = sum(row["loopback_ollama_calls"] for row in bypass_runs)
    current_lessons_path = data_root / "current_lessons.md"
    validate_private_file(current_lessons_path, "current_lessons")
    return {
        "supervisor_receipt_sha256": sha256_file(supervisor_path),
        "supervisor_updated_at": supervisor["updated_at"],
        "bypass_cutoff_last_supervised_created_at": cutoff.isoformat(),
        "round_count": len(rounds),
        "supervised_loopback_calls": supervised_calls,
        "observed_loopback_calls_including_post_pause": supervised_calls + bypass_calls,
        "physical_run_receipt_count": physical_run_receipt_count,
        "physical_explicit_call_count_lower_bound": physical_explicit_calls,
        "physical_receipts_missing_call_counter": physical_missing_call_counter,
        "explicit_calls_outside_supervisor": max(physical_explicit_calls - supervised_calls, 0),
        "last_supervised_lesson_delta_sha256": last_supervised_lesson_delta_sha256,
        "current_lessons_sha256": sha256_file(current_lessons_path),
        "last_three_method_review": {
            "status": "UNRECONSTRUCTABLE_MISSING_REQUIRED_METHOD_FIELDS",
            "missing_fields": list(LEGACY_MISSING_METHOD_FIELDS),
            "shared_partial_method_fingerprint": partial_fingerprint,
            "receipts": last_three,
        },
        "supervised_failure_taxonomy": evaluation_metrics(supervised_results),
        "post_pause_bypass": {
            "detected": bool(bypass_runs),
            "run_count": len(bypass_runs),
            "loopback_ollama_calls": bypass_calls,
            "runs": bypass_runs,
            "metrics": evaluation_metrics(bypass_results),
        },
    }


def inspect_schedule(repo_plist: Path, installed_plist: Path, training_loop: Path, supervisor_script: Path) -> dict:
    for path, label in ((repo_plist, "repo_plist"), (installed_plist, "installed_plist"), (training_loop, "training_loop"), (supervisor_script, "supervisor_script")):
        if not path.is_absolute() or path.is_symlink() or not path.is_file():
            raise MethodAuditError(f"{label}_invalid")
    try:
        repo_payload = plistlib.loads(repo_plist.read_bytes())
        installed_payload = plistlib.loads(installed_plist.read_bytes())
    except (OSError, plistlib.InvalidFileException) as error:
        raise MethodAuditError("schedule_plist_invalid") from error
    arguments = installed_payload.get("ProgramArguments")
    if not isinstance(arguments, list) or not all(isinstance(item, str) for item in arguments):
        raise MethodAuditError("schedule_arguments_invalid")
    repo_sha = sha256_file(repo_plist)
    installed_sha = sha256_file(installed_plist)
    direct_loop = len(arguments) > 1 and Path(arguments[1]).name == training_loop.name
    supervisor_routed = len(arguments) > 1 and Path(arguments[1]).name == supervisor_script.name
    return {
        "repo_plist_sha256": repo_sha,
        "installed_plist_sha256": installed_sha,
        "repo_and_installed_match": repo_sha == installed_sha,
        "training_loop_sha256": sha256_file(training_loop),
        "supervisor_script_sha256": sha256_file(supervisor_script),
        "program_routes_direct_training_loop": direct_loop,
        "program_routes_supervisor": supervisor_routed,
        "plateau_guard_present_in_scheduled_path": supervisor_routed,
        "schedule_bypass_proven": direct_loop and not supervisor_routed,
        "calendar": installed_payload.get("StartCalendarInterval"),
    }


def build_audit(
    *,
    data_root: Path,
    supervisor_receipt: Path,
    repo_plist: Path,
    installed_plist: Path,
    training_loop: Path,
    supervisor_script: Path,
    model_manifest: Path,
    job_path: Path,
    enforce_canonical_sources: bool = True,
) -> dict:
    source_context = {
        "data_root": data_root,
        "supervisor_receipt": supervisor_receipt,
        "repo_plist": repo_plist,
        "installed_plist": installed_plist,
        "training_loop": training_loop,
        "supervisor_script": supervisor_script,
        "model_manifest": model_manifest,
        "job_path": job_path,
    }
    validate_source_context(source_context, enforce_canonical=enforce_canonical_sources)
    model_digest = sha256_file(model_manifest)
    canonical_job = load_private_json(job_path, "canonical_job")
    attempt_before = canonical_job.get("attempt")
    if (
        canonical_job.get("job_id") != EXPECTED_JOB_ID
        or canonical_job.get("state") != "RUNNING"
        or type(attempt_before) is not int
        or attempt_before != EXPECTED_ATTEMPT
    ):
        raise MethodAuditError("attempt_before_invalid")
    train_path = data_root / "train.jsonl"
    eval_path = data_root / "eval.jsonl"
    train = load_private_jsonl(train_path, "train")
    evaluation = load_private_jsonl(eval_path, "eval")
    exposed_ids, exposed_occurrences, exposed_digest = collect_exposed_eval_ids(data_root)
    exposed_conversation_ids = {
        row["conversation_id"] for row in evaluation if row["id"] in exposed_ids
    }
    exposed_conversation_digest = sha256_text(
        "".join(
            f"{value}\n"
            for value in sorted(
                _opaque_conversation_hash("prior-exposure", conversation_id)
                for conversation_id in exposed_conversation_ids
            )
        )
    )
    holdout, holdout_source_rows = select_holdout_manifest(
        evaluation,
        excluded_record_ids=exposed_ids,
        excluded_conversation_ids=exposed_conversation_ids,
    )
    if len({row["conversation_id"] for row in holdout_source_rows}) != 20:
        raise MethodAuditError("holdout_source_conversation_not_unique")
    if {row["conversation_id"] for row in train} & {row["conversation_id"] for row in evaluation}:
        raise MethodAuditError("train_eval_conversation_overlap")
    few_shot = select_few_shot_manifest(train, holdout)

    supervisor = analyze_supervisor(data_root, supervisor_receipt)
    schedule = inspect_schedule(repo_plist, installed_plist, training_loop, supervisor_script)
    baseline_prompt_builder_sha256 = function_source_sha256(training_loop, "build_prompt")
    if not supervisor["post_pause_bypass"]["detected"] or not schedule["schedule_bypass_proven"]:
        raise MethodAuditError("post_pause_schedule_bypass_not_proven")

    fixed_holdout = {
        "selection": "sha256(method_version|role|stage|record_id), ascending; unique conversation; exclude every record and conversation exposed by prior physical runs",
        "stage_quotas": {
            key: {"stage": stage, "count": quota}
            for key, (stage, quota) in HOLDOUT_STAGE_QUOTAS.items()
        },
        "case_count": len(holdout),
        "unique_case_count": len({row["case_hash"] for row in holdout}),
        "unique_conversation_count": len({row["conversation_hash"] for row in holdout}),
        "case_manifest_sha256": manifest_digest(holdout),
        "cases": holdout,
        "eval_sha256": sha256_file(eval_path),
        "eval_record_count": len(evaluation),
        "prior_result_occurrences_excluded": exposed_occurrences,
        "prior_unique_case_ids_excluded": len(exposed_ids),
        "prior_exposure_manifest_sha256": exposed_digest,
        "prior_exposed_conversation_count": len(exposed_conversation_ids),
        "prior_exposed_conversation_manifest_sha256": exposed_conversation_digest,
    }
    fixed_few_shot = {
        "per_holdout_case": FEW_SHOT_PER_HOLDOUT_CASE,
        "mapping_count": len(few_shot),
        "case_count": sum(len(row["examples"]) for row in few_shot),
        "unique_case_count": len({example["case_hash"] for row in few_shot for example in row["examples"]}),
        "unique_conversation_count": len({example["conversation_hash"] for row in few_shot for example in row["examples"]}),
        "case_manifest_sha256": manifest_digest(few_shot),
        "mappings": few_shot,
        "train_sha256": sha256_file(train_path),
        "train_record_count": len(train),
        "prior_few_shot_exposure_status": "UNRECONSTRUCTABLE_LEGACY_RUNS_DID_NOT_RECORD_EXAMPLE_IDS",
    }
    seed_schedule = [700000 + index for index in range(20)]
    rubric_sha256 = sha256_text(canonical_json(RUBRIC_V2_SPEC))
    acceptance_sha256 = sha256_text(canonical_json(ACCEPTANCE_SPEC))
    method_core = {
        "method_version": EXPERIMENT_METHOD_VERSION,
        "hypothesis": "A structured known/missing/forbidden short-reply prompt improves paired rubric passes without increasing unsupported claims.",
        "target_failure_bucket": [
            "answer_relevance",
            "reask_known",
            "excessive_length",
            "unsupported_policy_or_price",
        ],
        "changed_variable": "prompt_builder_contract_sha256 only",
        "adapter": "planned hermes-line paired local runner; execution disabled until schedule gate and rubric calibration",
        "execution_eligible": False,
        "execution_blockers": [
            "scheduled_path_plateau_guard_not_installed",
            "rubric_v2_not_calibrated_18_of_20",
            "paired_runner_source_sha256_not_yet_pinned",
            "rendered_prompt_manifest_not_pinned",
            "shared_lesson_snapshot_not_materialized",
        ],
        "fixed_holdout_manifest_sha256": fixed_holdout["case_manifest_sha256"],
        "fixed_few_shot_manifest_sha256": fixed_few_shot["case_manifest_sha256"],
        "seed_schedule_sha256": sha256_text(canonical_json(seed_schedule)),
        "baseline_prompt_builder_source_sha256": baseline_prompt_builder_sha256,
        "baseline_training_loop_sha256": schedule["training_loop_sha256"],
        "candidate_prompt_builder_spec_sha256": sha256_text(CANDIDATE_SYSTEM_PROMPT_TEMPLATE),
        "baseline": "planned source-bound legacy build_prompt contract; full per-case messages are not rendered or pinned yet",
        "candidate": "planned structured known/missing/forbidden prompt contract; full per-case messages are not rendered or pinned yet",
        "baseline_render_status": "NOT_RENDERED",
        "candidate_render_status": "NOT_RENDERED",
        "shared_input_manifest_status": "NOT_PINNED",
        "model": "gemma4:latest",
        "model_digest": model_digest,
        "inference_parameters": {"temperature": 0, "paired_seed_schedule": seed_schedule},
        "lesson_sha256": supervisor["current_lessons_sha256"],
        "lesson_snapshot_status": "NOT_MATERIALIZED",
        "last_supervised_lesson_delta_sha256": supervisor["last_supervised_lesson_delta_sha256"],
        "evaluator_version": RUBRIC_V2_SPEC["version"],
        "evaluator_spec_sha256": rubric_sha256,
        "evaluator_precondition": "freeze structured human rubric labels and reach at least 18/20 exact agreement before inference",
        "acceptance_version": ACCEPTANCE_SPEC["version"],
        "acceptance_spec_sha256": acceptance_sha256,
        "expected_delta": "candidate net paired pass improvement >=4/20; no stage regresses by more than one case",
        "stop_loss": "maximum 40 local inferences; stop immediately on unsupported price/policy, private egress, customer send, manifest drift, or rubric calibration below 18/20",
        "acceptance": ACCEPTANCE_SPEC,
        "promotion_boundary": "this 20-case E1 is development evidence only and cannot count toward the seven-run promotion streak",
    }
    method_core["method_fingerprint"] = sha256_text(canonical_json(method_core))

    payload = {
        "schema_version": AUDIT_SCHEMA,
        "created_at": utc_now(),
        "job_id": EXPECTED_JOB_ID,
        "audit_method_version": AUDIT_METHOD_VERSION,
        "attempt_before": attempt_before,
        "attempt_after": attempt_before,
        "attempt_consumed": False,
        "model_calls_this_action": 0,
        "external_network_calls": 0,
        "customer_send": False,
        "private_third_party_egress": False,
        "supervisor_analysis": supervisor,
        "schedule_analysis": schedule,
        "fixed_holdout": fixed_holdout,
        "fixed_few_shot": fixed_few_shot,
        "experiment_contract": method_core,
        "objective_metrics_before": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "fixed_holdout_ready": False,
            "post_pause_unguarded_calls": supervisor["post_pause_bypass"]["loopback_ollama_calls"],
        },
        "objective_metrics_after": {
            "success_streak": 0,
            "best_pass_rate": 0.4,
            "fixed_holdout_ready": True,
            "post_pause_unguarded_calls": supervisor["post_pause_bypass"]["loopback_ollama_calls"],
        },
        "owner_acceptance_delta": 0,
        "supporting_delta": "exact 20-case holdout and 40-case two-shot manifests frozen; direct-schedule plateau bypass proven",
        "business_artifact_created": False,
        "unlocked_next_action": "install and verify a fail-closed schedule gate before rubric calibration or E1 inference",
        "first_principles": {
            "true_owner_outcome": "stable draft-quality LINE replies that save Mina time with zero unsupported claims and no automatic customer send",
            "current_constraint": "non-comparable random samples, an uncalibrated lexical evaluator, mutable prompt inputs, and a daily direct loop that bypasses the supervisor pause",
            "unproved_assumptions": "more rounds teach the model; lexical score represents business correctness; the scheduled path honors the durable-job plateau state",
            "smallest_falsifiable_experiment": "after the schedule gate, rubric calibration, immutable lesson snapshot, and shared-input rendered prompt manifest, run paired baseline/candidate on the exact 20-case holdout with prompt-builder contract as the only changed variable",
            "stop_condition": "stop at 40 local calls or immediately on any unsafe claim, manifest drift, private egress, customer send, or rubric calibration below 18/20",
        },
        "decision": "AUDIT_COMPLETE__SCHEDULE_GATE_REQUIRED_BEFORE_E1",
        "next_bounded_action": "Implement and test a fail-closed scheduled-path guard; installed launchd must make zero model calls when an active supervisor receipt has method_review_required=true. Do not run E1 yet.",
        "implementation_provenance": {
            "audit_script_sha256": sha256_file(Path(__file__).resolve()),
            "audit_test_sha256": sha256_file(
                Path(__file__).resolve().parents[1]
                / "tests"
                / "test_hermes_line_method_redesign_audit.py"
            ),
            "canonical_job_sha256": sha256_file(job_path),
            "model_manifest_sha256": model_digest,
            "supervisor_receipt_sha256": supervisor["supervisor_receipt_sha256"],
            "required_method_fields": list(REQUIRED_METHOD_FIELDS),
            "rubric_v2_spec_sha256": rubric_sha256,
            "acceptance_spec_sha256": acceptance_sha256,
        },
    }
    return payload


def validate_audit(
    payload: dict,
    *,
    source_context: dict[str, Path],
    enforce_canonical_sources: bool = True,
) -> None:
    validate_source_context(
        source_context,
        enforce_canonical=enforce_canonical_sources,
    )
    if set(payload) != AUDIT_TOP_LEVEL_KEYS:
        raise MethodAuditError("audit_topology_invalid")
    if (
        payload.get("schema_version") != AUDIT_SCHEMA
        or payload.get("job_id") != EXPECTED_JOB_ID
        or payload.get("audit_method_version") != AUDIT_METHOD_VERSION
    ):
        raise MethodAuditError("audit_identity_invalid")
    created_at = parse_time(payload.get("created_at"), "audit_created_at")
    if created_at.utcoffset() != timedelta(0):
        raise MethodAuditError("audit_created_at_not_utc")
    if created_at > datetime.now(timezone.utc) + timedelta(seconds=MAX_FUTURE_CLOCK_SKEW_SECONDS):
        raise MethodAuditError("audit_created_at_future")
    if (
        type(payload.get("attempt_before")) is not int
        or type(payload.get("attempt_after")) is not int
        or payload.get("attempt_before") != EXPECTED_ATTEMPT
        or payload.get("attempt_after") != EXPECTED_ATTEMPT
        or payload.get("attempt_consumed") is not False
    ):
        raise MethodAuditError("audit_attempt_accounting_invalid")
    for key in ("model_calls_this_action", "external_network_calls", "owner_acceptance_delta"):
        if type(payload.get(key)) is not int or payload.get(key) != 0:
            raise MethodAuditError(f"audit_{key}_invalid")
    if (
        payload.get("customer_send") is not False
        or payload.get("private_third_party_egress") is not False
        or payload.get("business_artifact_created") is not False
    ):
        raise MethodAuditError("audit_safety_boundary_invalid")

    holdout = payload.get("fixed_holdout")
    expected_holdout_keys = {
        "selection",
        "stage_quotas",
        "case_count",
        "unique_case_count",
        "unique_conversation_count",
        "case_manifest_sha256",
        "cases",
        "eval_sha256",
        "eval_record_count",
        "prior_result_occurrences_excluded",
        "prior_unique_case_ids_excluded",
        "prior_exposure_manifest_sha256",
        "prior_exposed_conversation_count",
        "prior_exposed_conversation_manifest_sha256",
    }
    if not isinstance(holdout, dict) or set(holdout) != expected_holdout_keys:
        raise MethodAuditError("audit_holdout_topology_invalid")
    for key in (
        "case_count",
        "unique_case_count",
        "unique_conversation_count",
        "eval_record_count",
        "prior_result_occurrences_excluded",
        "prior_unique_case_ids_excluded",
        "prior_exposed_conversation_count",
    ):
        if type(holdout.get(key)) is not int or holdout[key] < 0:
            raise MethodAuditError("audit_holdout_count_invalid")
    if holdout["case_count"] != 20 or holdout["unique_case_count"] != 20 or holdout["unique_conversation_count"] != 20:
        raise MethodAuditError("audit_holdout_invalid")
    for key in (
        "case_manifest_sha256",
        "eval_sha256",
        "prior_exposure_manifest_sha256",
        "prior_exposed_conversation_manifest_sha256",
    ):
        if not isinstance(holdout.get(key), str) or not HASH_RE.fullmatch(holdout[key]):
            raise MethodAuditError("audit_holdout_hash_invalid")
    if holdout["case_manifest_sha256"] != manifest_digest(holdout.get("cases", [])):
        raise MethodAuditError("audit_holdout_digest_invalid")
    if not isinstance(holdout.get("cases"), list) or len(holdout["cases"]) != 20:
        raise MethodAuditError("audit_holdout_cases_invalid")
    expected_case_keys = {"stratum", "stage", "case_hash", "conversation_hash", "selection_key"}
    for case in holdout["cases"]:
        if not isinstance(case, dict) or set(case) != expected_case_keys:
            raise MethodAuditError("audit_holdout_case_topology_invalid")
        if case.get("stratum") not in HOLDOUT_STAGE_QUOTAS or case.get("stage") != HOLDOUT_STAGE_QUOTAS[case["stratum"]][0]:
            raise MethodAuditError("audit_holdout_case_stage_invalid")
        for key in ("case_hash", "conversation_hash", "selection_key"):
            if not isinstance(case.get(key), str) or not HASH_RE.fullmatch(case[key]):
                raise MethodAuditError("audit_holdout_case_hash_invalid")

    few_shot = payload.get("fixed_few_shot")
    expected_few_shot_keys = {
        "per_holdout_case",
        "mapping_count",
        "case_count",
        "unique_case_count",
        "unique_conversation_count",
        "case_manifest_sha256",
        "mappings",
        "train_sha256",
        "train_record_count",
        "prior_few_shot_exposure_status",
    }
    if not isinstance(few_shot, dict) or set(few_shot) != expected_few_shot_keys:
        raise MethodAuditError("audit_few_shot_topology_invalid")
    for key in (
        "per_holdout_case",
        "mapping_count",
        "case_count",
        "unique_case_count",
        "unique_conversation_count",
        "train_record_count",
    ):
        if type(few_shot.get(key)) is not int or few_shot[key] < 0:
            raise MethodAuditError("audit_few_shot_count_invalid")
    if (
        few_shot["per_holdout_case"] != 2
        or few_shot["mapping_count"] != 20
        or few_shot["case_count"] != 40
        or few_shot["unique_case_count"] != 40
        or few_shot["unique_conversation_count"] != 40
    ):
        raise MethodAuditError("audit_few_shot_invalid")
    if not HASH_RE.fullmatch(str(few_shot.get("case_manifest_sha256", ""))) or not HASH_RE.fullmatch(str(few_shot.get("train_sha256", ""))):
        raise MethodAuditError("audit_few_shot_hash_invalid")
    if few_shot["case_manifest_sha256"] != manifest_digest(few_shot.get("mappings", [])):
        raise MethodAuditError("audit_few_shot_digest_invalid")
    if not isinstance(few_shot.get("mappings"), list) or len(few_shot["mappings"]) != 20:
        raise MethodAuditError("audit_few_shot_mappings_invalid")
    expected_mapping_keys = {"holdout_case_hash", "stage", "examples"}
    expected_example_keys = {"case_hash", "conversation_hash", "selection_key"}
    for mapping in few_shot["mappings"]:
        if not isinstance(mapping, dict) or set(mapping) != expected_mapping_keys:
            raise MethodAuditError("audit_few_shot_mapping_topology_invalid")
        if not isinstance(mapping.get("holdout_case_hash"), str) or not HASH_RE.fullmatch(mapping["holdout_case_hash"]):
            raise MethodAuditError("audit_few_shot_mapping_hash_invalid")
        if mapping.get("stage") not in {value[0] for value in HOLDOUT_STAGE_QUOTAS.values()}:
            raise MethodAuditError("audit_few_shot_mapping_stage_invalid")
        if not isinstance(mapping.get("examples"), list) or len(mapping["examples"]) != 2:
            raise MethodAuditError("audit_few_shot_examples_invalid")
        for example in mapping["examples"]:
            if not isinstance(example, dict) or set(example) != expected_example_keys:
                raise MethodAuditError("audit_few_shot_example_topology_invalid")
            for key in expected_example_keys:
                if not isinstance(example.get(key), str) or not HASH_RE.fullmatch(example[key]):
                    raise MethodAuditError("audit_few_shot_example_hash_invalid")

    live_eval_path = source_context["data_root"] / "eval.jsonl"
    live_train_path = source_context["data_root"] / "train.jsonl"
    live_evaluation = load_private_jsonl(live_eval_path, "audit_live_eval")
    live_train = load_private_jsonl(live_train_path, "audit_live_train")
    exposed_ids, exposed_occurrences, exposed_digest = collect_exposed_eval_ids(
        source_context["data_root"]
    )
    exposed_conversation_ids = {
        row["conversation_id"] for row in live_evaluation if row["id"] in exposed_ids
    }
    exposed_conversation_digest = sha256_text(
        "".join(
            f"{value}\n"
            for value in sorted(
                _opaque_conversation_hash("prior-exposure", conversation_id)
                for conversation_id in exposed_conversation_ids
            )
        )
    )
    expected_holdout, _ = select_holdout_manifest(
        live_evaluation,
        excluded_record_ids=exposed_ids,
        excluded_conversation_ids=exposed_conversation_ids,
    )
    if (
        holdout["cases"] != expected_holdout
        or holdout["eval_sha256"] != sha256_file(live_eval_path)
        or holdout["eval_record_count"] != len(live_evaluation)
        or holdout["prior_result_occurrences_excluded"] != exposed_occurrences
        or holdout["prior_unique_case_ids_excluded"] != len(exposed_ids)
        or holdout["prior_exposure_manifest_sha256"] != exposed_digest
        or holdout["prior_exposed_conversation_count"] != len(exposed_conversation_ids)
        or holdout["prior_exposed_conversation_manifest_sha256"] != exposed_conversation_digest
    ):
        raise MethodAuditError("audit_holdout_live_source_mismatch")
    expected_few_shot = select_few_shot_manifest(live_train, expected_holdout)
    if (
        few_shot["mappings"] != expected_few_shot
        or few_shot["train_sha256"] != sha256_file(live_train_path)
        or few_shot["train_record_count"] != len(live_train)
    ):
        raise MethodAuditError("audit_few_shot_live_source_mismatch")

    schedule = payload.get("schedule_analysis")
    expected_schedule_keys = {
        "repo_plist_sha256",
        "installed_plist_sha256",
        "repo_and_installed_match",
        "training_loop_sha256",
        "supervisor_script_sha256",
        "program_routes_direct_training_loop",
        "program_routes_supervisor",
        "plateau_guard_present_in_scheduled_path",
        "schedule_bypass_proven",
        "calendar",
    }
    if not isinstance(schedule, dict) or set(schedule) != expected_schedule_keys:
        raise MethodAuditError("audit_schedule_topology_invalid")
    for key in (
        "repo_plist_sha256",
        "installed_plist_sha256",
        "training_loop_sha256",
        "supervisor_script_sha256",
    ):
        if not isinstance(schedule.get(key), str) or not HASH_RE.fullmatch(schedule[key]):
            raise MethodAuditError("audit_schedule_hash_invalid")
    if (
        schedule.get("repo_and_installed_match") is not True
        or schedule.get("program_routes_direct_training_loop") is not True
        or schedule.get("program_routes_supervisor") is not False
        or schedule.get("plateau_guard_present_in_scheduled_path") is not False
        or schedule.get("schedule_bypass_proven") is not True
    ):
        raise MethodAuditError("audit_schedule_bypass_missing")

    supervisor = payload.get("supervisor_analysis")
    expected_supervisor_keys = {
        "supervisor_receipt_sha256",
        "supervisor_updated_at",
        "bypass_cutoff_last_supervised_created_at",
        "round_count",
        "supervised_loopback_calls",
        "observed_loopback_calls_including_post_pause",
        "physical_run_receipt_count",
        "physical_explicit_call_count_lower_bound",
        "physical_receipts_missing_call_counter",
        "explicit_calls_outside_supervisor",
        "last_supervised_lesson_delta_sha256",
        "current_lessons_sha256",
        "last_three_method_review",
        "supervised_failure_taxonomy",
        "post_pause_bypass",
    }
    if not isinstance(supervisor, dict) or set(supervisor) != expected_supervisor_keys:
        raise MethodAuditError("audit_supervisor_topology_invalid")
    parse_time(
        supervisor.get("bypass_cutoff_last_supervised_created_at"),
        "audit_bypass_cutoff",
    )
    for key in (
        "round_count",
        "supervised_loopback_calls",
        "observed_loopback_calls_including_post_pause",
        "physical_run_receipt_count",
        "physical_explicit_call_count_lower_bound",
        "physical_receipts_missing_call_counter",
        "explicit_calls_outside_supervisor",
    ):
        if type(supervisor.get(key)) is not int or supervisor[key] < 0:
            raise MethodAuditError("audit_supervisor_count_invalid")
    for key in (
        "supervisor_receipt_sha256",
        "last_supervised_lesson_delta_sha256",
        "current_lessons_sha256",
    ):
        if not isinstance(supervisor.get(key), str) or not HASH_RE.fullmatch(supervisor[key]):
            raise MethodAuditError("audit_supervisor_hash_invalid")
    bypass = supervisor.get("post_pause_bypass")
    if (
        not isinstance(bypass, dict)
        or set(bypass) != {"detected", "run_count", "loopback_ollama_calls", "runs", "metrics"}
        or bypass.get("detected") is not True
        or type(bypass.get("run_count")) is not int
        or bypass["run_count"] <= 0
        or type(bypass.get("loopback_ollama_calls")) is not int
        or bypass["loopback_ollama_calls"] <= 0
        or not isinstance(bypass.get("runs"), list)
        or len(bypass["runs"]) != bypass["run_count"]
    ):
        raise MethodAuditError("audit_post_pause_bypass_missing")
    expected_bypass_run_keys = {
        "receipt_sha256",
        "created_at",
        "loopback_ollama_calls",
        "pass_rate",
        "unsupported_price_count",
    }
    for run in bypass["runs"]:
        if not isinstance(run, dict) or set(run) != expected_bypass_run_keys:
            raise MethodAuditError("audit_bypass_run_topology_invalid")
        if not isinstance(run.get("receipt_sha256"), str) or not HASH_RE.fullmatch(run["receipt_sha256"]):
            raise MethodAuditError("audit_bypass_run_hash_invalid")
        parse_time(run.get("created_at"), "audit_bypass_run_created_at")
        if type(run.get("loopback_ollama_calls")) is not int or run["loopback_ollama_calls"] <= 0:
            raise MethodAuditError("audit_bypass_run_call_count_invalid")
    validate_metrics_payload(bypass.get("metrics"), "audit_bypass_metrics")
    validate_metrics_payload(
        supervisor.get("supervised_failure_taxonomy"),
        "audit_supervised_failure_taxonomy",
    )
    method_review = supervisor.get("last_three_method_review")
    if (
        not isinstance(method_review, dict)
        or set(method_review) != {"status", "missing_fields", "shared_partial_method_fingerprint", "receipts"}
        or not isinstance(method_review.get("receipts"), list)
        or len(method_review["receipts"]) != 3
    ):
        raise MethodAuditError("audit_method_review_topology_invalid")
    if (
        method_review.get("status") != "UNRECONSTRUCTABLE_MISSING_REQUIRED_METHOD_FIELDS"
        or method_review.get("missing_fields") != list(LEGACY_MISSING_METHOD_FIELDS)
        or not isinstance(method_review.get("shared_partial_method_fingerprint"), str)
        or not HASH_RE.fullmatch(method_review["shared_partial_method_fingerprint"])
    ):
        raise MethodAuditError("audit_method_review_contract_invalid")
    expected_review_receipt_keys = {
        "receipt_sha256",
        "pass_rate",
        "unsupported_price_rate",
        "lowest_stage",
        "seed",
        "model",
        "evaluator_version",
        "output_lesson_delta_sha256",
        "partial_method_fingerprint",
    }
    for receipt in method_review["receipts"]:
        if not isinstance(receipt, dict) or set(receipt) != expected_review_receipt_keys:
            raise MethodAuditError("audit_method_review_receipt_topology_invalid")
        for key in ("receipt_sha256", "output_lesson_delta_sha256", "partial_method_fingerprint"):
            if not isinstance(receipt.get(key), str) or not HASH_RE.fullmatch(receipt[key]):
                raise MethodAuditError("audit_method_review_receipt_hash_invalid")
        if receipt["partial_method_fingerprint"] != method_review["shared_partial_method_fingerprint"]:
            raise MethodAuditError("audit_method_review_fingerprint_mismatch")
        for key in ("pass_rate", "unsupported_price_rate"):
            value = receipt.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise MethodAuditError("audit_method_review_rate_invalid")
        if type(receipt.get("seed")) is not int or not all(
            isinstance(receipt.get(key), str) and receipt[key]
            for key in ("lowest_stage", "model", "evaluator_version")
        ):
            raise MethodAuditError("audit_method_review_scalar_invalid")

    live_supervisor = analyze_supervisor(
        source_context["data_root"],
        source_context["supervisor_receipt"],
    )
    if canonical_json(supervisor) != canonical_json(live_supervisor):
        raise MethodAuditError("audit_supervisor_live_source_mismatch")
    live_schedule = inspect_schedule(
        source_context["repo_plist"],
        source_context["installed_plist"],
        source_context["training_loop"],
        source_context["supervisor_script"],
    )
    if canonical_json(schedule) != canonical_json(live_schedule):
        raise MethodAuditError("audit_schedule_live_source_mismatch")

    method = payload.get("experiment_contract")
    expected_method_keys = {
        "method_version",
        "hypothesis",
        "target_failure_bucket",
        "changed_variable",
        "adapter",
        "execution_eligible",
        "execution_blockers",
        "fixed_holdout_manifest_sha256",
        "fixed_few_shot_manifest_sha256",
        "seed_schedule_sha256",
        "baseline_prompt_builder_source_sha256",
        "baseline_training_loop_sha256",
        "candidate_prompt_builder_spec_sha256",
        "baseline",
        "candidate",
        "baseline_render_status",
        "candidate_render_status",
        "shared_input_manifest_status",
        "model",
        "model_digest",
        "inference_parameters",
        "lesson_sha256",
        "lesson_snapshot_status",
        "last_supervised_lesson_delta_sha256",
        "evaluator_version",
        "evaluator_spec_sha256",
        "evaluator_precondition",
        "acceptance_version",
        "acceptance_spec_sha256",
        "expected_delta",
        "stop_loss",
        "acceptance",
        "promotion_boundary",
        "method_fingerprint",
    }
    if not isinstance(method, dict) or set(method) != expected_method_keys:
        raise MethodAuditError("audit_experiment_contract_invalid")
    if method.get("method_version") != EXPERIMENT_METHOD_VERSION or method.get("changed_variable") != "prompt_builder_contract_sha256 only":
        raise MethodAuditError("audit_single_variable_contract_invalid")
    if method.get("execution_eligible") is not False:
        raise MethodAuditError("audit_experiment_execution_state_invalid")
    for key in (
        "method_fingerprint",
        "fixed_holdout_manifest_sha256",
        "fixed_few_shot_manifest_sha256",
        "seed_schedule_sha256",
        "baseline_prompt_builder_source_sha256",
        "baseline_training_loop_sha256",
        "candidate_prompt_builder_spec_sha256",
        "model_digest",
        "lesson_sha256",
        "last_supervised_lesson_delta_sha256",
        "evaluator_spec_sha256",
        "acceptance_spec_sha256",
    ):
        if not isinstance(method.get(key), str) or not HASH_RE.fullmatch(method[key]):
            raise MethodAuditError("audit_method_hash_invalid")
    if method["fixed_holdout_manifest_sha256"] != holdout["case_manifest_sha256"] or method["fixed_few_shot_manifest_sha256"] != few_shot["case_manifest_sha256"]:
        raise MethodAuditError("audit_method_manifest_binding_invalid")
    if method["baseline_training_loop_sha256"] != schedule["training_loop_sha256"]:
        raise MethodAuditError("audit_baseline_source_binding_invalid")
    if method["candidate_prompt_builder_spec_sha256"] != sha256_text(CANDIDATE_SYSTEM_PROMPT_TEMPLATE):
        raise MethodAuditError("audit_candidate_prompt_binding_invalid")
    if (
        method.get("baseline_render_status") != "NOT_RENDERED"
        or method.get("candidate_render_status") != "NOT_RENDERED"
        or method.get("shared_input_manifest_status") != "NOT_PINNED"
        or method.get("lesson_snapshot_status") != "NOT_MATERIALIZED"
        or "rendered_prompt_manifest_not_pinned" not in method.get("execution_blockers", [])
        or "shared_lesson_snapshot_not_materialized" not in method.get("execution_blockers", [])
    ):
        raise MethodAuditError("audit_prompt_render_boundary_invalid")
    fingerprint = method["method_fingerprint"]
    method_without_fingerprint = dict(method)
    method_without_fingerprint.pop("method_fingerprint", None)
    if fingerprint != sha256_text(canonical_json(method_without_fingerprint)):
        raise MethodAuditError("audit_method_fingerprint_invalid")

    provenance = payload.get("implementation_provenance")
    if not isinstance(provenance, dict) or set(provenance) != IMPLEMENTATION_PROVENANCE_KEYS:
        raise MethodAuditError("audit_implementation_provenance_topology_invalid")
    current_script = sha256_file(Path(__file__).resolve())
    current_test = sha256_file(
        Path(__file__).resolve().parents[1]
        / "tests"
        / "test_hermes_line_method_redesign_audit.py"
    )
    if provenance.get("audit_script_sha256") != current_script or provenance.get("audit_test_sha256") != current_test:
        raise MethodAuditError("audit_implementation_provenance_invalid")
    for key in ("canonical_job_sha256", "model_manifest_sha256", "supervisor_receipt_sha256"):
        if not isinstance(provenance.get(key), str) or not HASH_RE.fullmatch(provenance[key]):
            raise MethodAuditError("audit_source_provenance_hash_invalid")
    if provenance["model_manifest_sha256"] != method["model_digest"] or provenance["supervisor_receipt_sha256"] != supervisor["supervisor_receipt_sha256"]:
        raise MethodAuditError("audit_source_provenance_binding_invalid")
    if (
        provenance["canonical_job_sha256"] != sha256_file(source_context["job_path"])
        or provenance["model_manifest_sha256"] != sha256_file(source_context["model_manifest"])
        or provenance["supervisor_receipt_sha256"] != sha256_file(source_context["supervisor_receipt"])
        or method["lesson_sha256"] != sha256_file(source_context["data_root"] / "current_lessons.md")
        or method["baseline_prompt_builder_source_sha256"]
        != function_source_sha256(source_context["training_loop"], "build_prompt")
    ):
        raise MethodAuditError("audit_live_source_provenance_mismatch")
    if provenance.get("required_method_fields") != list(REQUIRED_METHOD_FIELDS):
        raise MethodAuditError("audit_required_method_fields_invalid")
    if provenance.get("rubric_v2_spec_sha256") != sha256_text(canonical_json(RUBRIC_V2_SPEC)) or provenance.get("acceptance_spec_sha256") != sha256_text(canonical_json(ACCEPTANCE_SPEC)):
        raise MethodAuditError("audit_spec_provenance_invalid")
    expected_objective_keys = {
        "success_streak",
        "best_pass_rate",
        "fixed_holdout_ready",
        "post_pause_unguarded_calls",
    }
    before = payload.get("objective_metrics_before")
    after = payload.get("objective_metrics_after")
    if not isinstance(before, dict) or not isinstance(after, dict) or set(before) != expected_objective_keys or set(after) != expected_objective_keys:
        raise MethodAuditError("audit_objective_metrics_topology_invalid")
    first_principles = payload.get("first_principles")
    if not isinstance(first_principles, dict) or set(first_principles) != {
        "true_owner_outcome",
        "current_constraint",
        "unproved_assumptions",
        "smallest_falsifiable_experiment",
        "stop_condition",
    }:
        raise MethodAuditError("audit_first_principles_topology_invalid")
    if payload.get("decision") != "AUDIT_COMPLETE__SCHEDULE_GATE_REQUIRED_BEFORE_E1":
        raise MethodAuditError("audit_decision_invalid")
    serialized = json.dumps(payload, ensure_ascii=False)
    for token in ("customer\"", "generated\"", "target\"", "context\"", "http://", "https://"):
        if token in serialized:
            raise MethodAuditError("audit_private_or_network_value_leaked")


def validate_sanitized_receipt(sanitized: dict) -> None:
    if set(sanitized) != SANITIZED_TOP_LEVEL_KEYS:
        raise MethodAuditError("sanitized_topology_invalid")
    body_sha = sanitized.get("body_sha256")
    body = dict(sanitized)
    body.pop("body_sha256", None)
    if not isinstance(body_sha, str) or not HASH_RE.fullmatch(body_sha) or body_sha != sha256_text(canonical_json(body)):
        raise MethodAuditError("sanitized_body_sha256_invalid")
    if (
        sanitized.get("schema_version") != SANITIZED_SCHEMA
        or sanitized.get("job_id") != EXPECTED_JOB_ID
        or sanitized.get("audit_method_version") != AUDIT_METHOD_VERSION
        or not isinstance(sanitized.get("private_audit_sha256"), str)
        or not HASH_RE.fullmatch(sanitized["private_audit_sha256"])
    ):
        raise MethodAuditError("sanitized_identity_invalid")
    if (
        type(sanitized.get("attempt_before")) is not int
        or type(sanitized.get("attempt_after")) is not int
        or sanitized["attempt_before"] != EXPECTED_ATTEMPT
        or sanitized["attempt_after"] != EXPECTED_ATTEMPT
        or sanitized.get("attempt_consumed") is not False
    ):
        raise MethodAuditError("sanitized_attempt_accounting_invalid")
    for key in ("model_calls_this_action", "external_network_calls", "owner_acceptance_delta"):
        if type(sanitized.get(key)) is not int or sanitized[key] != 0:
            raise MethodAuditError("sanitized_zero_counter_invalid")
    if sanitized.get("customer_send") is not False or sanitized.get("private_third_party_egress") is not False or sanitized.get("business_artifact_created") is not False:
        raise MethodAuditError("sanitized_safety_boundary_invalid")
    if "cases" in sanitized.get("fixed_holdout", {}) or "mappings" in sanitized.get("fixed_few_shot", {}):
        raise MethodAuditError("sanitized_case_manifest_leaked")
    serialized = json.dumps(sanitized, ensure_ascii=False)
    if any(token in serialized for token in ("/Users/", "/Volumes/", "customer\"", "generated\"", "target\"", "context\"")):
        raise MethodAuditError("sanitized_private_value_leaked")


def build_sanitized_receipt(
    private_path: Path,
    expected_sha256: str,
    *,
    source_context: dict[str, Path],
    enforce_canonical_sources: bool = True,
) -> dict:
    validate_private_file(private_path, "private_audit")
    if not HASH_RE.fullmatch(expected_sha256) or sha256_file(private_path) != expected_sha256:
        raise MethodAuditError("private_audit_sha256_mismatch")
    payload = load_private_json(private_path, "private_audit")
    validate_audit(
        payload,
        source_context=source_context,
        enforce_canonical_sources=enforce_canonical_sources,
    )
    sanitized = {
        "schema_version": SANITIZED_SCHEMA,
        "created_at": payload["created_at"],
        "job_id": payload["job_id"],
        "audit_method_version": payload["audit_method_version"],
        "private_audit_sha256": expected_sha256,
        "attempt_before": payload["attempt_before"],
        "attempt_after": payload["attempt_after"],
        "attempt_consumed": payload["attempt_consumed"],
        "model_calls_this_action": payload["model_calls_this_action"],
        "external_network_calls": payload["external_network_calls"],
        "customer_send": payload["customer_send"],
        "private_third_party_egress": payload["private_third_party_egress"],
        "last_three_method_review": payload["supervisor_analysis"]["last_three_method_review"],
        "call_accounting": {
            key: payload["supervisor_analysis"][key]
            for key in (
                "round_count",
                "supervised_loopback_calls",
                "observed_loopback_calls_including_post_pause",
                "physical_run_receipt_count",
                "physical_explicit_call_count_lower_bound",
                "physical_receipts_missing_call_counter",
                "explicit_calls_outside_supervisor",
            )
        },
        "supervised_failure_taxonomy": payload["supervisor_analysis"]["supervised_failure_taxonomy"],
        "post_pause_bypass": payload["supervisor_analysis"]["post_pause_bypass"],
        "schedule_analysis": payload["schedule_analysis"],
        "fixed_holdout": {key: value for key, value in payload["fixed_holdout"].items() if key != "cases"},
        "fixed_few_shot": {key: value for key, value in payload["fixed_few_shot"].items() if key != "mappings"},
        "experiment_contract": payload["experiment_contract"],
        "objective_metrics_before": payload["objective_metrics_before"],
        "objective_metrics_after": payload["objective_metrics_after"],
        "owner_acceptance_delta": payload["owner_acceptance_delta"],
        "supporting_delta": payload["supporting_delta"],
        "business_artifact_created": payload["business_artifact_created"],
        "unlocked_next_action": payload["unlocked_next_action"],
        "first_principles": payload["first_principles"],
        "decision": payload["decision"],
        "next_bounded_action": payload["next_bounded_action"],
        "implementation_provenance": payload["implementation_provenance"],
    }
    sanitized["body_sha256"] = sha256_text(canonical_json(sanitized))
    validate_sanitized_receipt(sanitized)
    return sanitized


def _identity(payload: dict) -> dict:
    copy = json.loads(json.dumps(payload))
    copy.pop("created_at", None)
    return copy


def write_private_json(path: Path, payload: dict) -> bool:
    if not path.is_absolute():
        raise MethodAuditError("private_output_must_be_absolute")
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.parent.chmod(PRIVATE_DIR_MODE)
    validate_private_dir(path.parent, "private_output_parent")
    if path.exists() or path.is_symlink():
        existing = load_private_json(path, "existing_private_output")
        if _identity(existing) == _identity(payload):
            return False
        raise MethodAuditError("existing_private_output_identity_conflict")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, PRIVATE_FILE_MODE)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        path.chmod(PRIVATE_FILE_MODE)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise
    return True


def write_public_json(path: Path, payload: dict) -> None:
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-output", required=True)
    parser.add_argument("--sanitized-output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    args = build_parser().parse_args(argv)
    private_output = Path(args.private_output).expanduser().resolve()
    sources = canonical_source_context()
    payload = build_audit(
        data_root=sources["data_root"],
        supervisor_receipt=sources["supervisor_receipt"],
        repo_plist=sources["repo_plist"],
        installed_plist=sources["installed_plist"],
        training_loop=sources["training_loop"],
        supervisor_script=sources["supervisor_script"],
        model_manifest=sources["model_manifest"],
        job_path=sources["job_path"],
    )
    validate_audit(payload, source_context=sources)
    created = write_private_json(private_output, payload)
    private_sha = sha256_file(private_output)
    sanitized = build_sanitized_receipt(
        private_output,
        private_sha,
        source_context=sources,
    )
    write_public_json(Path(args.sanitized_output).expanduser().resolve(), sanitized)
    print(
        json.dumps(
            {
                "status": "ok",
                "private_output_created": created,
                "private_audit_sha256": private_sha,
                "sanitized_body_sha256": sanitized["body_sha256"],
                "fixed_holdout_count": sanitized["fixed_holdout"]["case_count"],
                "post_pause_bypass_calls": sanitized["post_pause_bypass"]["loopback_ollama_calls"],
                "model_calls_this_action": 0,
                "attempt_after": sanitized["attempt_after"],
                "decision": sanitized["decision"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
