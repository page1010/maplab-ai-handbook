#!/usr/bin/env python3
"""Read-only GO/NO-GO guard for a bounded, offline Hermes MLX QLoRA run.

This module never starts a model or training process.  A future runner must
require a PASS result immediately before execution and enforce the validated
limits while the child process is alive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import unquote


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from hermes_line_human_annotation_validator import (  # noqa: E402
    AnnotationValidationError,
    CRITERIA_ORDER,
    EXPECTED_ANNOTATION_GUIDE_SHA256,
    EXPECTED_COMMERCIAL_AUTHORITY_SHA256,
    EXPECTED_PRIVATE_PREFLIGHT_SHA256,
    load_json as load_annotation_json,
    sha256_file,
    validate_annotations,
)
import hermes_line_dlp_preflight as dlp_preflight  # noqa: E402


PREFLIGHT_SCHEMA = "maplab.hermes.mlx.training-preflight.v1"
CONFIG_SCHEMA = "maplab.hermes.mlx.training-config.v1"
GOLD_MANIFEST_SCHEMA = "maplab.hermes.mlx.gold-manifest.v1"
HOLDOUT_MANIFEST_SCHEMA = "maplab.hermes.mlx.holdout-manifest.v1"
DLP_MANIFEST_SCHEMA = dlp_preflight.MANIFEST_SCHEMA_VERSION
DLP_RECEIPT_SCHEMA = dlp_preflight.RECEIPT_SCHEMA_VERSION

EXPECTED_MODEL_ID = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
EXPECTED_MODEL_REVISION = "50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b"
EXPECTED_MODEL_HASHES = {
    "model_config_sha256": "574349e5a343236546fda55e4744a76e181f534182d7dc60ff1bad7e7a502849",
    "model_weights_sha256": "2a73c6c248601ab904e035548abd8e6abb65ea27dcb5f342fb0a8910eb44173f",
    "tokenizer_sha256": "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4",
}
MAX_MEMORY_GB = 4.0
MAX_SEQUENCE_LENGTH = 256
MAX_NUM_LAYERS = 2
MAX_ITERATIONS = 200
MAX_WALL_TIME_SECONDS = 3600
MIN_GOLD_EXAMPLES = 30
MAX_GOLD_EXAMPLES = 50
MIN_HOLDOUT_CASES = 20

HASH_RE = re.compile(r"[0-9a-f]{64}")
FORBIDDEN_RUNTIME_MARKERS = (
    "ollama",
    "11434",
    "llama-server",
    "llama_server",
    "localhost",
    "127.0.0.1",
    "[::1]",
    "http://",
    "https://",
    "ollama://",
)
FORBIDDEN_ENV_NAMES = {
    "HERMES_LINE_OLLAMA_URL",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY",
}


class TrainingPreflightError(ValueError):
    """A sanitized, stable fail-closed error code."""


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TrainingPreflightError("dataset_duplicate_json_key")
        result[key] = value
    return result


def _schema(value: dict[str, Any]) -> Any:
    return value.get("schema_version", value.get("schema"))


def _require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        raise TrainingPreflightError(f"{label}_invalid")
    return value


def _require_nonempty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TrainingPreflightError(f"{label}_invalid")
    return value


def _require_exact_keys(value: Any, expected: Iterable[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise TrainingPreflightError(f"{label}_keys_invalid")
    return value


def _private_path(path: Path, label: str, *, directory: bool = False) -> Path:
    path = Path(os.path.abspath(path.expanduser()))
    if not path.is_absolute() or path.is_symlink():
        raise TrainingPreflightError(f"{label}_path_invalid")
    if directory:
        if not path.is_dir():
            raise TrainingPreflightError(f"{label}_directory_missing")
    elif not path.is_file():
        raise TrainingPreflightError(f"{label}_file_missing")
    info = path.stat()
    if info.st_nlink != 1 and not directory:
        raise TrainingPreflightError(f"{label}_hardlink_rejected")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise TrainingPreflightError(f"{label}_wrong_owner")
    expected_mode = 0o700 if directory else 0o600
    if stat.S_IMODE(info.st_mode) != expected_mode:
        raise TrainingPreflightError(f"{label}_mode_not_{expected_mode:o}")
    return path


def _load_private_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return load_annotation_json(
            Path(os.path.abspath(path.expanduser())), label, private=True
        )
    except AnnotationValidationError as error:
        raise TrainingPreflightError(str(error)) from error


def _jsonl_record_count(path: Path, label: str) -> int:
    path = _private_path(path, label)
    count = 0
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                value = json.loads(line, object_pairs_hook=_strict_json_object)
                if not isinstance(value, dict):
                    raise TrainingPreflightError(f"{label}_row_not_object")
                count += 1
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise TrainingPreflightError(f"{label}_jsonl_invalid") from error
    return count


def _under(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _walk_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _walk_string_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_string_values(child)


def _normalized_runtime_text(value: str) -> str:
    normalized = value.lower()
    for _ in range(3):
        decoded = unquote(normalized)
        if decoded == normalized:
            break
        normalized = decoded
    return normalized


def validate_no_ollama_contract(
    config: dict[str, Any], environment: Mapping[str, str]
) -> None:
    for key, value in environment.items():
        upper_key = key.upper()
        if upper_key.startswith("OLLAMA_") or upper_key in FORBIDDEN_ENV_NAMES:
            raise TrainingPreflightError("ollama_or_network_environment_rejected")
        joined = _normalized_runtime_text(f"{key}={value}")
        if any(marker in joined for marker in FORBIDDEN_RUNTIME_MARKERS):
            raise TrainingPreflightError("ollama_or_network_environment_rejected")
    for text in _walk_string_values(config):
        lowered = _normalized_runtime_text(text)
        if any(marker in lowered for marker in FORBIDDEN_RUNTIME_MARKERS):
            raise TrainingPreflightError("ollama_config_or_url_rejected")
    if config.get("fallback_enabled") is not False:
        raise TrainingPreflightError("runtime_fallback_must_be_disabled")
    if config.get("fallback_provider") is not None:
        raise TrainingPreflightError("fallback_provider_rejected")
    if config.get("process_fallback") is not None:
        raise TrainingPreflightError("process_fallback_rejected")


def validate_training_config(
    config_path: Path,
    environment: Mapping[str, str],
    *,
    expected_model_hashes: Mapping[str, str] = EXPECTED_MODEL_HASHES,
) -> dict[str, Any]:
    config = _load_private_json(config_path, "training_config")
    expected_keys = (
        "schema_version",
        "provider",
        "model_id",
        "model_revision",
        "model_path",
        "model_config_sha256",
        "model_weights_sha256",
        "tokenizer_sha256",
        "fine_tune_type",
        "private_root",
        "training_dataset_path",
        "holdout_dataset_path",
        "adapter_output_path",
        "batch_size",
        "grad_accumulation_steps",
        "max_seq_length",
        "num_layers",
        "iterations",
        "memory_limit_gb",
        "terminate_on_memory_limit",
        "wall_time_limit_seconds",
        "mask_prompt",
        "network_allowed",
        "fallback_enabled",
        "fallback_provider",
        "process_fallback",
        "live_route_enabled",
    )
    _require_exact_keys(config, expected_keys, "training_config")
    if config["schema_version"] != CONFIG_SCHEMA:
        raise TrainingPreflightError("training_config_schema_invalid")
    validate_no_ollama_contract(config, environment)
    if config["provider"] != "mlx_lm":
        raise TrainingPreflightError("provider_must_be_mlx_lm")
    if config["model_id"] != EXPECTED_MODEL_ID or config["model_revision"] != EXPECTED_MODEL_REVISION:
        raise TrainingPreflightError("model_identity_not_pinned")
    if config["fine_tune_type"] != "lora_on_4bit_base":
        raise TrainingPreflightError("fine_tune_type_invalid")
    if type(config["batch_size"]) is not int or config["batch_size"] != 1:
        raise TrainingPreflightError("batch_size_must_equal_1")
    if type(config["grad_accumulation_steps"]) is not int or config["grad_accumulation_steps"] != 1:
        raise TrainingPreflightError("grad_accumulation_steps_must_equal_1")
    if type(config["max_seq_length"]) is not int or config["max_seq_length"] != MAX_SEQUENCE_LENGTH:
        raise TrainingPreflightError("max_seq_length_must_equal_256")
    if type(config["num_layers"]) is not int or config["num_layers"] != MAX_NUM_LAYERS:
        raise TrainingPreflightError("num_layers_must_equal_2")
    if type(config["iterations"]) is not int or not 1 <= config["iterations"] <= MAX_ITERATIONS:
        raise TrainingPreflightError("iterations_out_of_bounds")
    memory_limit = config["memory_limit_gb"]
    if isinstance(memory_limit, bool) or not isinstance(memory_limit, (int, float)) or not 0 < memory_limit <= MAX_MEMORY_GB:
        raise TrainingPreflightError("memory_limit_gb_out_of_bounds")
    if config["terminate_on_memory_limit"] is not True:
        raise TrainingPreflightError("memory_limit_termination_required")
    wall_limit = config["wall_time_limit_seconds"]
    if type(wall_limit) is not int or not 60 <= wall_limit <= MAX_WALL_TIME_SECONDS:
        raise TrainingPreflightError("wall_time_limit_out_of_bounds")
    if config["mask_prompt"] is not True:
        raise TrainingPreflightError("mask_prompt_required")
    if config["network_allowed"] is not False:
        raise TrainingPreflightError("network_must_be_disabled")
    if config["live_route_enabled"] is not False:
        raise TrainingPreflightError("live_route_must_be_disabled")

    for key in (
        "private_root",
        "training_dataset_path",
        "holdout_dataset_path",
        "adapter_output_path",
        "model_path",
    ):
        _require_nonempty_text(config[key], key)
    private_root = _private_path(Path(config["private_root"]), "mlx_private_root", directory=True)
    training_path = _private_path(Path(config["training_dataset_path"]), "gold_dataset")
    holdout_path = _private_path(Path(config["holdout_dataset_path"]), "holdout_dataset")
    adapter_path = Path(os.path.abspath(Path(config["adapter_output_path"]).expanduser()))
    if not _under(training_path, private_root) or not _under(holdout_path, private_root):
        raise TrainingPreflightError("private_dataset_outside_private_root")
    if not _under(adapter_path, private_root):
        raise TrainingPreflightError("adapter_output_outside_private_root")
    if adapter_path.exists() or adapter_path.is_symlink():
        raise TrainingPreflightError("adapter_output_must_not_preexist")

    model_path = Path(os.path.abspath(Path(config["model_path"]).expanduser()))
    if model_path.is_symlink() or not model_path.is_dir():
        raise TrainingPreflightError("model_path_invalid")
    model_files = {
        "model_config_sha256": model_path / "config.json",
        "model_weights_sha256": model_path / "model.safetensors",
        "tokenizer_sha256": model_path / "tokenizer.json",
    }
    if set(expected_model_hashes) != set(model_files):
        raise TrainingPreflightError("expected_model_hash_contract_invalid")
    for key, path in model_files.items():
        expected = _require_hash(expected_model_hashes[key], f"expected_{key}")
        if config[key] != expected:
            raise TrainingPreflightError(f"{key}_not_pinned")
        if path.is_symlink() or not path.is_file() or sha256_file(path) != expected:
            raise TrainingPreflightError(f"{key}_mismatch")

    return {
        "config": config,
        "config_sha256": sha256_file(Path(os.path.abspath(config_path.expanduser()))),
        "private_root": private_root,
        "training_path": training_path,
        "holdout_path": holdout_path,
        "adapter_path": adapter_path,
    }


def validate_dlp_contract(
    manifest_path: Path,
    receipt_path: Path,
    *,
    expected_datasets: Mapping[str, tuple[Path, str, int]],
) -> dict[str, Any]:
    manifest = _load_private_json(manifest_path, "dlp_rights_manifest")
    receipt = _load_private_json(receipt_path, "dlp_preflight_receipt")
    try:
        dlp_preflight.validate_manifest_shape(manifest)
        dlp_preflight.validate_receipt(receipt)
    except dlp_preflight.DLPPreflightError as error:
        raise TrainingPreflightError(f"dlp_contract_{error}") from error
    if receipt.get("status") != "PASS" or receipt.get("eligible_for_offline_training") is not True:
        raise TrainingPreflightError("dlp_receipt_not_pass")
    if receipt.get("reason_codes") != []:
        raise TrainingPreflightError("dlp_reason_codes_not_empty")

    manifest_sha = sha256_file(Path(os.path.abspath(manifest_path.expanduser())))
    if receipt.get("manifest", {}).get("sha256") != manifest_sha:
        raise TrainingPreflightError("dlp_manifest_receipt_binding_mismatch")
    if receipt.get("provenance", {}).get("manifest_sha256") != manifest_sha:
        raise TrainingPreflightError("dlp_manifest_provenance_binding_mismatch")

    source_paths = [spec[0] for spec in expected_datasets.values()]
    try:
        rights_errors = dlp_preflight.rights_reasons(
            manifest, source_paths=source_paths, now=datetime.now(timezone.utc)
        )
        binding_errors = dlp_preflight.dataset_binding_reasons(manifest, receipt["scan"])
    except dlp_preflight.DLPPreflightError as error:
        raise TrainingPreflightError(f"dlp_contract_{error}") from error
    if rights_errors:
        raise TrainingPreflightError(f"dlp_rights_{rights_errors[0].lower()}")
    if binding_errors:
        raise TrainingPreflightError("dlp_dataset_binding_mismatch")

    scan = receipt["scan"]
    for key in (
        "invalid_json_records",
        "non_object_records",
        "scan_errors",
        "high_confidence_findings",
        "review_required_findings",
    ):
        if scan.get(key) != 0:
            raise TrainingPreflightError(f"dlp_scan_{key}_not_zero")
    scan_files = scan.get("files")
    if not isinstance(scan_files, list):
        raise TrainingPreflightError("dlp_scan_files_missing")
    by_name = {
        item.get("logical_name"): item
        for item in scan_files
        if isinstance(item, dict) and isinstance(item.get("logical_name"), str)
    }
    if set(by_name) != set(expected_datasets):
        raise TrainingPreflightError("dlp_scan_logical_names_mismatch")
    for logical_name, (path, expected_sha, expected_count) in expected_datasets.items():
        item = by_name[logical_name]
        if (
            item.get("sha256") != expected_sha
            or item.get("record_count") != expected_count
            or item.get("byte_count") != path.stat().st_size
        ):
            raise TrainingPreflightError("dlp_scan_file_binding_mismatch")
    return {
        "manifest_sha256": manifest_sha,
        "receipt_sha256": sha256_file(Path(os.path.abspath(receipt_path.expanduser()))),
    }


def validate_gold_manifest(
    manifest_path: Path,
    *,
    annotations_sha256: str,
    dlp_receipt_sha256: str,
) -> dict[str, Any]:
    manifest = _load_private_json(manifest_path, "gold_manifest")
    expected_keys = (
        "schema_version",
        "status",
        "data_class",
        "dataset_path",
        "dataset_sha256",
        "example_count",
        "conversation_hashes",
        "dlp_logical_name",
        "tokenizer_sha256",
        "max_token_length",
        "source_annotation_sha256",
        "dlp_receipt_sha256",
        "named_human_approval",
    )
    _require_exact_keys(manifest, expected_keys, "gold_manifest")
    if manifest["schema_version"] != GOLD_MANIFEST_SCHEMA or manifest["status"] != "PASS":
        raise TrainingPreflightError("gold_manifest_not_pass")
    if manifest["data_class"] != "owner_corrected_gold":
        raise TrainingPreflightError("gold_data_class_invalid")
    if manifest["named_human_approval"] is not True:
        raise TrainingPreflightError("gold_named_human_approval_missing")
    if manifest["source_annotation_sha256"] != annotations_sha256:
        raise TrainingPreflightError("gold_annotation_binding_mismatch")
    if manifest["dlp_receipt_sha256"] != dlp_receipt_sha256:
        raise TrainingPreflightError("gold_dlp_binding_mismatch")
    if not isinstance(manifest["dlp_logical_name"], str) or not dlp_preflight.LOGICAL_NAME_RE.fullmatch(
        manifest["dlp_logical_name"]
    ):
        raise TrainingPreflightError("gold_dlp_logical_name_invalid")
    tokenizer_sha = _require_hash(manifest["tokenizer_sha256"], "gold_tokenizer_sha256")
    if type(manifest["max_token_length"]) is not int or not 1 <= manifest["max_token_length"] <= MAX_SEQUENCE_LENGTH:
        raise TrainingPreflightError("gold_max_token_length_out_of_bounds")
    dataset_path = _private_path(
        Path(_require_nonempty_text(manifest["dataset_path"], "gold_dataset_path")),
        "gold_dataset",
    )
    dataset_sha = _require_hash(manifest["dataset_sha256"], "gold_dataset_sha256")
    if sha256_file(dataset_path) != dataset_sha:
        raise TrainingPreflightError("gold_dataset_sha256_mismatch")
    count = _jsonl_record_count(dataset_path, "gold_dataset")
    if manifest["example_count"] != count or not MIN_GOLD_EXAMPLES <= count <= MAX_GOLD_EXAMPLES:
        raise TrainingPreflightError("gold_example_count_out_of_bounds")
    conversations = manifest["conversation_hashes"]
    if not isinstance(conversations, list) or not conversations or len(conversations) > count:
        raise TrainingPreflightError("gold_conversation_hashes_invalid")
    if any(not isinstance(item, str) or not HASH_RE.fullmatch(item) for item in conversations):
        raise TrainingPreflightError("gold_conversation_hash_invalid")
    if len(set(conversations)) != len(conversations):
        raise TrainingPreflightError("gold_conversation_hash_duplicate")
    return {
        "dataset_path": dataset_path,
        "dataset_sha256": dataset_sha,
        "example_count": count,
        "conversation_hashes": set(conversations),
        "dlp_logical_name": manifest["dlp_logical_name"],
        "tokenizer_sha256": tokenizer_sha,
        "max_token_length": manifest["max_token_length"],
        "manifest_sha256": sha256_file(Path(os.path.abspath(manifest_path.expanduser()))),
    }


def validate_holdout_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = _load_private_json(manifest_path, "holdout_manifest")
    expected_keys = (
        "schema_version",
        "status",
        "data_class",
        "dataset_path",
        "dataset_sha256",
        "case_count",
        "conversation_hashes",
        "dlp_logical_name",
        "tokenizer_sha256",
        "max_token_length",
        "frozen",
        "excluded_from_training",
        "prior_exposure_count",
    )
    _require_exact_keys(manifest, expected_keys, "holdout_manifest")
    if manifest["schema_version"] != HOLDOUT_MANIFEST_SCHEMA or manifest["status"] != "PASS":
        raise TrainingPreflightError("holdout_manifest_not_pass")
    if manifest["data_class"] != "independent_holdout":
        raise TrainingPreflightError("holdout_data_class_invalid")
    if manifest["frozen"] is not True or manifest["excluded_from_training"] is not True:
        raise TrainingPreflightError("holdout_not_frozen_and_excluded")
    if type(manifest["prior_exposure_count"]) is not int or manifest["prior_exposure_count"] != 0:
        raise TrainingPreflightError("holdout_prior_exposure_not_zero")
    if not isinstance(manifest["dlp_logical_name"], str) or not dlp_preflight.LOGICAL_NAME_RE.fullmatch(
        manifest["dlp_logical_name"]
    ):
        raise TrainingPreflightError("holdout_dlp_logical_name_invalid")
    tokenizer_sha = _require_hash(manifest["tokenizer_sha256"], "holdout_tokenizer_sha256")
    if type(manifest["max_token_length"]) is not int or not 1 <= manifest["max_token_length"] <= MAX_SEQUENCE_LENGTH:
        raise TrainingPreflightError("holdout_max_token_length_out_of_bounds")
    dataset_path = _private_path(
        Path(_require_nonempty_text(manifest["dataset_path"], "holdout_dataset_path")),
        "holdout_dataset",
    )
    dataset_sha = _require_hash(manifest["dataset_sha256"], "holdout_dataset_sha256")
    if sha256_file(dataset_path) != dataset_sha:
        raise TrainingPreflightError("holdout_dataset_sha256_mismatch")
    count = _jsonl_record_count(dataset_path, "holdout_dataset")
    if manifest["case_count"] != count or count < MIN_HOLDOUT_CASES:
        raise TrainingPreflightError("holdout_case_count_insufficient")
    conversations = manifest["conversation_hashes"]
    if not isinstance(conversations, list) or not conversations or len(conversations) > count:
        raise TrainingPreflightError("holdout_conversation_hashes_invalid")
    if any(not isinstance(item, str) or not HASH_RE.fullmatch(item) for item in conversations):
        raise TrainingPreflightError("holdout_conversation_hash_invalid")
    if len(set(conversations)) != len(conversations):
        raise TrainingPreflightError("holdout_conversation_hash_duplicate")
    return {
        "dataset_path": dataset_path,
        "dataset_sha256": dataset_sha,
        "case_count": count,
        "conversation_hashes": set(conversations),
        "dlp_logical_name": manifest["dlp_logical_name"],
        "tokenizer_sha256": tokenizer_sha,
        "max_token_length": manifest["max_token_length"],
        "manifest_sha256": sha256_file(Path(os.path.abspath(manifest_path.expanduser()))),
    }


def load_dataset_binding_from_manifest(
    manifest_path: Path,
    *,
    label: str,
    expected_schema: str,
    count_field: str,
) -> dict[str, Any]:
    """Read only the immutable dataset fields needed by the DLP receipt gate.

    Full gold/holdout semantics are validated separately.  This deliberately
    does not treat a dataset binding as proof that the corresponding manifest
    is otherwise eligible.
    """

    manifest = _load_private_json(manifest_path, f"{label}_manifest")
    if manifest.get("schema_version") != expected_schema:
        raise TrainingPreflightError(f"{label}_manifest_schema_invalid")
    raw_path = manifest.get("dataset_path")
    if not isinstance(raw_path, str) or not raw_path:
        raise TrainingPreflightError(f"{label}_dataset_path_invalid")
    dataset_path = _private_path(Path(raw_path), f"{label}_dataset")
    dataset_sha = _require_hash(
        manifest.get("dataset_sha256"), f"{label}_dataset_sha256"
    )
    if sha256_file(dataset_path) != dataset_sha:
        raise TrainingPreflightError(f"{label}_dataset_sha256_mismatch")
    declared_count = manifest.get(count_field)
    if type(declared_count) is not int or declared_count < 1:
        raise TrainingPreflightError(f"{label}_{count_field}_invalid")
    actual_count = _jsonl_record_count(dataset_path, f"{label}_dataset")
    if actual_count != declared_count:
        raise TrainingPreflightError(f"{label}_{count_field}_mismatch")
    logical_name = manifest.get("dlp_logical_name")
    if not isinstance(logical_name, str) or not dlp_preflight.LOGICAL_NAME_RE.fullmatch(
        logical_name
    ):
        raise TrainingPreflightError(f"{label}_dlp_logical_name_invalid")
    return {
        "dataset_path": dataset_path,
        "dataset_sha256": dataset_sha,
        "record_count": actual_count,
        "dlp_logical_name": logical_name,
    }


def _result(
    gates: dict[str, bool], errors: Iterable[str], state: dict[str, Any]
) -> dict[str, Any]:
    passed = all(gates.values())
    result: dict[str, Any] = {
        "schema_version": PREFLIGHT_SCHEMA,
        "status": "GO" if passed else "NO_GO",
        "eligible_for_bounded_mlx_training": passed,
        "training_execution_performed": False,
        "ollama_used": False,
        "gates": gates,
        "errors": sorted(set(errors)),
        "limits": {
            "batch_size": 1,
            "grad_accumulation_steps": 1,
            "max_seq_length": MAX_SEQUENCE_LENGTH,
            "num_layers": MAX_NUM_LAYERS,
            "max_memory_gb": MAX_MEMORY_GB,
            "max_iterations": MAX_ITERATIONS,
            "max_wall_time_seconds": MAX_WALL_TIME_SECONDS,
            "runtime_enforcement_required": True,
        },
    }
    if passed:
        result["artifact_hashes"] = {
            "annotations": state["labels"]["annotation_sha256"],
            "dlp_manifest": state["dlp"]["manifest_sha256"],
            "dlp_receipt": state["dlp"]["receipt_sha256"],
            "gold_manifest": state["gold"]["manifest_sha256"],
            "holdout_manifest": state["holdout"]["manifest_sha256"],
            "training_config": state["config"]["config_sha256"],
        }
    return result


def evaluate_preflight(
    *,
    annotations_path: Path,
    annotation_preflight_path: Path,
    annotation_guide_path: Path,
    dlp_manifest_path: Path,
    dlp_receipt_path: Path,
    gold_manifest_path: Path,
    holdout_manifest_path: Path,
    training_config_path: Path,
    environment: Mapping[str, str],
    expected_annotation_preflight_sha256: str = EXPECTED_PRIVATE_PREFLIGHT_SHA256,
    expected_annotation_guide_sha256: str = EXPECTED_ANNOTATION_GUIDE_SHA256,
    expected_commercial_authority_sha256: str = EXPECTED_COMMERCIAL_AUTHORITY_SHA256,
    expected_model_hashes: Mapping[str, str] = EXPECTED_MODEL_HASHES,
) -> dict[str, Any]:
    gates = {name: False for name in ("labels", "dlp_rights", "gold", "holdout", "config", "contamination")}
    errors: list[str] = []
    state: dict[str, Any] = {}

    # Validate the no-Ollama/zero-network boundary before reading any private
    # labels or datasets.  An idle Ollama service is not itself a fallback;
    # only the config/environment routes available to this run are relevant.
    try:
        raw_config = _load_private_json(training_config_path, "training_config")
        validate_no_ollama_contract(raw_config, environment)
    except TrainingPreflightError as error:
        errors.append(f"config:{error}")
        return _result(gates, errors, state)

    try:
        state["config"] = validate_training_config(
            training_config_path,
            environment,
            expected_model_hashes=expected_model_hashes,
        )
        gates["config"] = True
    except TrainingPreflightError as error:
        errors.append(f"config:{error}")

    try:
        state["labels"] = validate_annotations(
            annotations_path,
            annotation_preflight_path,
            annotation_guide_path,
            expected_preflight_sha256=expected_annotation_preflight_sha256,
            expected_guide_sha256=expected_annotation_guide_sha256,
            expected_authority_sha256=expected_commercial_authority_sha256,
        )
        gates["labels"] = True
    except AnnotationValidationError as error:
        errors.append(f"labels:{error}")

    try:
        state["holdout"] = validate_holdout_manifest(holdout_manifest_path)
        gates["holdout"] = True
    except TrainingPreflightError as error:
        errors.append(f"holdout:{error}")

    try:
        state["gold_binding"] = load_dataset_binding_from_manifest(
            gold_manifest_path,
            label="gold",
            expected_schema=GOLD_MANIFEST_SCHEMA,
            count_field="example_count",
        )
    except TrainingPreflightError as error:
        errors.append(f"gold:{error}")

    if "gold_binding" in state and gates["holdout"]:
        gold_binding = state["gold_binding"]
        holdout = state["holdout"]
        if gold_binding["dlp_logical_name"] == holdout["dlp_logical_name"]:
            errors.append("dlp_rights:duplicate_dataset_logical_name")
        else:
            expected_datasets = {
                gold_binding["dlp_logical_name"]: (
                    gold_binding["dataset_path"],
                    gold_binding["dataset_sha256"],
                    gold_binding["record_count"],
                ),
                holdout["dlp_logical_name"]: (
                    holdout["dataset_path"],
                    holdout["dataset_sha256"],
                    holdout["case_count"],
                ),
            }
            try:
                state["dlp"] = validate_dlp_contract(
                    dlp_manifest_path,
                    dlp_receipt_path,
                    expected_datasets=expected_datasets,
                )
                gates["dlp_rights"] = True
            except TrainingPreflightError as error:
                errors.append(f"dlp_rights:{error}")
    else:
        errors.append("dlp_rights:dataset_dependencies_not_ready")

    annotations_sha = state.get("labels", {}).get("annotation_sha256")
    if annotations_sha and gates["dlp_rights"] and "gold_binding" in state:
        try:
            state["gold"] = validate_gold_manifest(
                gold_manifest_path,
                annotations_sha256=annotations_sha,
                dlp_receipt_sha256=state["dlp"]["receipt_sha256"],
            )
            gates["gold"] = True
        except TrainingPreflightError as error:
            errors.append(f"gold:{error}")
    else:
        errors.append("gold:labels_or_dlp_dependency_not_ready")

    if gates["gold"] and gates["holdout"]:
        if state["gold"]["dataset_path"] == state["holdout"]["dataset_path"]:
            errors.append("contamination:gold_and_holdout_path_equal")
        elif state["gold"]["dataset_sha256"] == state["holdout"]["dataset_sha256"]:
            errors.append("contamination:gold_and_holdout_bytes_equal")
        elif state["gold"]["conversation_hashes"] & state["holdout"]["conversation_hashes"]:
            errors.append("contamination:conversation_overlap_nonzero")
        else:
            gates["contamination"] = True
    else:
        errors.append("contamination:dataset_dependencies_not_ready")

    if gates["config"]:
        config = state["config"]
        if gates["gold"] and config["training_path"] != state["gold"]["dataset_path"]:
            gates["config"] = False
            errors.append("config:training_dataset_binding_mismatch")
        if gates["holdout"] and config["holdout_path"] != state["holdout"]["dataset_path"]:
            gates["config"] = False
            errors.append("config:holdout_dataset_binding_mismatch")
        if gates["gold"] and (
            state["gold"]["tokenizer_sha256"] != config["config"]["tokenizer_sha256"]
            or state["gold"]["max_token_length"] > config["config"]["max_seq_length"]
        ):
            gates["config"] = False
            errors.append("config:gold_token_envelope_binding_mismatch")
        if gates["holdout"] and (
            state["holdout"]["tokenizer_sha256"] != config["config"]["tokenizer_sha256"]
            or state["holdout"]["max_token_length"] > config["config"]["max_seq_length"]
        ):
            gates["config"] = False
            errors.append("config:holdout_token_envelope_binding_mismatch")

    return _result(gates, errors, state)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--annotation-preflight", type=Path, required=True)
    parser.add_argument("--annotation-guide", type=Path, required=True)
    parser.add_argument("--dlp-manifest", type=Path, required=True)
    parser.add_argument("--dlp-receipt", type=Path, required=True)
    parser.add_argument("--gold-manifest", type=Path, required=True)
    parser.add_argument("--holdout-manifest", type=Path, required=True)
    parser.add_argument("--training-config", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = evaluate_preflight(
        annotations_path=args.annotations,
        annotation_preflight_path=args.annotation_preflight,
        annotation_guide_path=args.annotation_guide,
        dlp_manifest_path=args.dlp_manifest,
        dlp_receipt_path=args.dlp_receipt,
        gold_manifest_path=args.gold_manifest,
        holdout_manifest_path=args.holdout_manifest,
        training_config_path=args.training_config,
        environment=os.environ,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "GO" else 2


if __name__ == "__main__":
    sys.exit(main())
