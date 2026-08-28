#!/usr/bin/env python3
"""Bounded, resumable supervisor for private Hermes LINE reply training.

The durable router owns the canonical ``job.json``.  This supervisor consumes
that absolute path, runs several local-only evaluation rounds, checkpoints after
every round, and updates the canonical job without copying conversation text
into it.  Re-running the same job path resumes the same private supervisor
receipt until the seven-round quality streak is reached.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
LOOP_SCRIPT = SCRIPT_PATH.with_name("hermes_line_training_loop.py")
DURABLE_JOB_ROOT = REPO_ROOT / "workbook" / "reviews" / "MAPLAB-DURABLE-JOBS"
sys.path.insert(0, str(SCRIPT_PATH.parent))

import hermes_line_training_loop as training_loop  # noqa: E402


DEFAULT_MAX_ROUNDS = 5
DEFAULT_MAX_SECONDS = 1800
HARD_MAX_ROUNDS = 12
HARD_MAX_SECONDS = 3600
DEFAULT_BATCH = 5
DEFAULT_TARGET_STREAK = 7
DEFAULT_TARGET_PASS_RATE = 0.85
DEFAULT_REGRESSION_THRESHOLD = 2
DEFAULT_PLATEAU_THRESHOLD = 2
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600
JOB_ID_RE = re.compile(r"^MAPJOB-[A-Za-z0-9._-]{1,96}$")
RUN_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,160}$")
CANONICAL_JOB_STATES = {
    "ACCEPTED",
    "RUNNING",
    "WAITING_EXTERNAL",
    "OWNER_REVIEW",
    "BLOCKED",
    "FAILED",
    "COMPLETED",
}
RESUMABLE_JOB_STATES = {"ACCEPTED", "RUNNING", "BLOCKED", "COMPLETED"}
ALLOWED_TRANSITIONS = {
    "ACCEPTED": {"RUNNING", "BLOCKED", "FAILED"},
    "RUNNING": {"RUNNING", "BLOCKED", "FAILED", "COMPLETED"},
    "BLOCKED": {"RUNNING", "BLOCKED", "FAILED"},
    "FAILED": {"FAILED"},
    "COMPLETED": {"COMPLETED"},
    "WAITING_EXTERNAL": {"WAITING_EXTERNAL"},
    "OWNER_REVIEW": {"OWNER_REVIEW"},
}


class SupervisorError(RuntimeError):
    """The supervisor contract or canonical durable job is invalid."""


class RoundExecutionError(RuntimeError):
    def __init__(self, reason: str, *, exit_code: int | None = None, timed_out: bool = False):
        super().__init__(reason)
        self.reason = reason
        self.exit_code = exit_code
        self.timed_out = timed_out


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _private_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.parent.chmod(PRIVATE_DIR_MODE)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, PRIVATE_FILE_MODE)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(PRIVATE_FILE_MODE)
        os.replace(temporary, path)
        path.chmod(PRIVATE_FILE_MODE)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def _private_json(path: Path, payload: dict) -> None:
    _private_write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _acquire_job_lock(job_path: Path) -> int | None:
    """Acquire one non-blocking lock for the full supervisor invocation."""

    lock_path = job_path.parent / ".line-training-supervisor.lock"
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(lock_path, flags, PRIVATE_FILE_MODE)
    except OSError as exc:
        raise SupervisorError("supervisor_lock_unavailable") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
            raise SupervisorError("supervisor_lock_not_private")
        if hasattr(os, "getuid") and info.st_uid != os.getuid():
            raise SupervisorError("supervisor_lock_wrong_owner")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(descriptor)
        return None
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _release_job_lock(descriptor: int) -> None:
    try:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _transition_after_error_if_idle(
    job_path: Path,
    *,
    expected_job: dict,
    state: str,
    reason: str,
    result: dict,
    next_action: str,
) -> bool:
    """Persist an error only when no supervisor invocation owns this job."""

    descriptor = _acquire_job_lock(job_path)
    if descriptor is None:
        return False
    try:
        canonical_path, current_job = read_durable_job(job_path)
        if current_job != expected_job:
            return False
        if current_job.get("state") not in {"ACCEPTED", "RUNNING", "BLOCKED"}:
            return False
        transition_durable_job(
            canonical_path,
            current_job,
            state,
            reason=reason,
            result=result,
            next_action=next_action,
        )
        return True
    finally:
        _release_job_lock(descriptor)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dataset_fingerprint(data_root: Path) -> str:
    digest = hashlib.sha256()
    for name in ("manifest.json", "train.jsonl", "eval.jsonl"):
        path = data_root / name
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


def read_durable_job(job_path: str | Path) -> tuple[Path, dict]:
    raw = Path(job_path).expanduser()
    if not raw.is_absolute():
        raise SupervisorError("job_path_must_be_absolute")
    if raw.is_symlink():
        raise SupervisorError("durable_job_missing_or_symlinked")
    path = raw.resolve()
    root = DURABLE_JOB_ROOT.resolve()
    if (
        path.name != "job.json"
        or path.parent.parent != root
        or not JOB_ID_RE.fullmatch(path.parent.name)
    ):
        raise SupervisorError("invalid_durable_job_path")
    if path.is_symlink() or not path.is_file():
        raise SupervisorError("durable_job_missing_or_symlinked")
    if hasattr(os, "getuid") and path.stat().st_uid != os.getuid():
        raise SupervisorError("durable_job_wrong_owner")
    if _mode(path) & 0o077 or _mode(path.parent) & 0o077:
        raise SupervisorError("durable_job_permissions_not_private")
    try:
        job = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SupervisorError("durable_job_unreadable") from exc
    if not isinstance(job, dict) or job.get("schema_version") != "maplab.durable-job.v1":
        raise SupervisorError("durable_job_schema_mismatch")
    if job.get("job_type") != "hermes-line-training":
        raise SupervisorError("durable_job_type_mismatch")
    if job.get("job_id") != path.parent.name or Path(str(job.get("job_path") or "")).resolve() != path:
        raise SupervisorError("durable_job_identity_mismatch")
    if job.get("adapter") != "hermes-line-training-supervisor":
        raise SupervisorError("durable_job_adapter_mismatch")
    if job.get("data_class") != "private-local-only":
        raise SupervisorError("durable_job_data_class_mismatch")
    authorization = job.get("authorization")
    if not isinstance(authorization, dict):
        raise SupervisorError("durable_job_authorization_invalid")
    if authorization.get("offline_training") is not True:
        raise SupervisorError("offline_training_not_authorized")
    if authorization.get("customer_send") is not False:
        raise SupervisorError("customer_send_must_be_false")
    if job.get("state") not in CANONICAL_JOB_STATES:
        raise SupervisorError("durable_job_state_invalid")
    attempt = job.get("attempt", 0)
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 0:
        raise SupervisorError("durable_job_attempt_invalid")
    return path, job


def _job_markdown(job_path: Path, job: dict) -> str:
    return "\n".join(
        [
            f"# {job['job_id']}",
            "",
            f"- Type: `{job['job_type']}`",
            f"- State: `{job['state']}`",
            f"- Adapter: `{job['adapter']}`",
            f"- Current phase: `{job.get('current_phase', 'offline-training')}`",
            f"- Next: {job.get('next_bounded_action', '')}",
            f"- Receipt: `{job_path}`",
            "",
            "## Resume Prompt",
            "",
            str(job.get("resume_prompt") or ""),
            "",
        ]
    )


def write_durable_job(job_path: Path, job: dict) -> None:
    job["updated_at"] = utc_iso()
    _private_json(job_path, job)
    _private_write(job_path.with_suffix(".md"), _job_markdown(job_path, job))


def transition_durable_job(
    job_path: Path,
    job: dict,
    state: str,
    *,
    reason: str,
    result: dict,
    next_action: str,
    current_phase: str | None = None,
) -> None:
    if state not in CANONICAL_JOB_STATES:
        raise SupervisorError("durable_job_state_invalid")
    previous = job.get("state")
    if state not in ALLOWED_TRANSITIONS.get(str(previous), set()):
        raise SupervisorError(f"durable_job_transition_forbidden:{previous}:{state}")
    job["state"] = state
    job["current_phase"] = current_phase or (
        "offline-training" if state != "COMPLETED" else "terminal"
    )
    job["last_result"] = result
    job["next_bounded_action"] = next_action
    if previous != state or not job.get("history"):
        job.setdefault("history", []).append(
            {"at": utc_iso(), "from": previous, "to": state, "reason": reason}
        )
    job["history"] = job.get("history", [])[-200:]
    write_durable_job(job_path, job)


def _new_receipt(job: dict, data_root: Path, receipt_path: Path) -> dict:
    return {
        "schema_version": "maplab.hermes.line-supervisor.v1",
        "job_id": job["job_id"],
        "durable_job_path": str(Path(job["job_path"]).resolve()),
        "created_at": utc_iso(),
        "updated_at": utc_iso(),
        "status": "accepted",
        "local_only": True,
        "provider_policy": "loopback-ollama-only",
        "external_network_calls": 0,
        "loopback_ollama_calls": 0,
        "customer_send": False,
        "data_root": str(data_root),
        "receipt": str(receipt_path),
        "rounds": [],
        "invocations": [],
        "success_streak": 0,
        "regression_streak": 0,
        "plateau_streak": 0,
        "method_review_required": False,
        "best_pass_rate": None,
        "last_pass_rate": None,
        "lowest_stage": None,
        "diagnostic_mode": False,
        "next_stage": None,
    }


def load_or_create_receipt(job: dict, data_root: Path) -> tuple[Path, dict]:
    if not JOB_ID_RE.fullmatch(str(job.get("job_id") or "")):
        raise SupervisorError("invalid_job_id")
    supervisor_root = data_root / "supervisor_jobs"
    training_loop.ensure_private_dir(supervisor_root)
    receipt_dir = supervisor_root / job["job_id"]
    if receipt_dir.exists() or receipt_dir.is_symlink():
        if receipt_dir.is_symlink() or not receipt_dir.is_dir() or _mode(receipt_dir) & 0o077:
            raise SupervisorError("supervisor_receipt_dir_not_private")
        if hasattr(os, "getuid") and receipt_dir.stat().st_uid != os.getuid():
            raise SupervisorError("supervisor_receipt_dir_wrong_owner")
    else:
        training_loop.ensure_private_dir(receipt_dir)
    receipt_path = receipt_dir / "receipt.json"
    if not receipt_path.exists():
        receipt = _new_receipt(job, data_root, receipt_path)
        _private_json(receipt_path, receipt)
        return receipt_path, receipt
    if receipt_path.is_symlink() or _mode(receipt_path) & 0o077:
        raise SupervisorError("supervisor_receipt_permissions_not_private")
    if hasattr(os, "getuid") and receipt_path.stat().st_uid != os.getuid():
        raise SupervisorError("supervisor_receipt_wrong_owner")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SupervisorError("supervisor_receipt_unreadable") from exc
    if (
        receipt.get("job_id") != job["job_id"]
        or receipt.get("data_root") != str(data_root)
        or receipt.get("local_only") is not True
        or receipt.get("provider_policy") != "loopback-ollama-only"
        or receipt.get("external_network_calls") != 0
        or not isinstance(receipt.get("loopback_ollama_calls"), int)
        or isinstance(receipt.get("loopback_ollama_calls"), bool)
        or receipt.get("customer_send") is not False
    ):
        raise SupervisorError("supervisor_receipt_contract_mismatch")
    return receipt_path, receipt


def _sanitized_child_env(data_root: Path) -> dict[str, str]:
    allowed = ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL")
    child = {key: os.environ[key] for key in allowed if os.environ.get(key)}
    child.update(
        {
            "HERMES_LINE_DATA_ROOT": str(data_root),
            "HERMES_LINE_PROVIDER": "local-only",
            "NO_PROXY": "127.0.0.1,localhost,::1",
            "no_proxy": "127.0.0.1,localhost,::1",
            "PYTHONUNBUFFERED": "1",
        }
    )
    if os.environ.get("HERMES_LINE_OLLAMA_URL"):
        child["HERMES_LINE_OLLAMA_URL"] = os.environ["HERMES_LINE_OLLAMA_URL"]
    if os.environ.get("HERMES_LINE_LOCAL_MODEL"):
        child["HERMES_LINE_LOCAL_MODEL"] = os.environ["HERMES_LINE_LOCAL_MODEL"]
    return child


def run_round_subprocess(
    *,
    data_root: Path,
    batch: int,
    seed: int,
    stage: str,
    timeout_seconds: float,
) -> dict:
    per_request_timeout = max(1, min(180, int(timeout_seconds / max(batch, 1))))
    command = [
        sys.executable,
        str(LOOP_SCRIPT),
        "--data-root",
        str(data_root),
        "--batch",
        str(batch),
        "--seed",
        str(seed),
        "--timeout",
        str(per_request_timeout),
    ]
    if stage:
        command.extend(["--stage", stage])
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=_sanitized_child_env(data_root),
            capture_output=True,
            text=True,
            timeout=max(1.0, timeout_seconds),
            check=False,
            start_new_session=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise RoundExecutionError("round_wall_timeout", timed_out=True) from exc
    if completed.returncode != 0:
        reason = f"round_exit_{completed.returncode}"
        raise RoundExecutionError(reason, exit_code=completed.returncode)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RoundExecutionError("round_output_invalid") from exc
    return payload


def inspect_round(payload: dict, data_root: Path) -> dict:
    if not isinstance(payload, dict):
        raise RoundExecutionError("round_output_invalid")
    receipt_value = payload.get("receipt")
    if not isinstance(receipt_value, str):
        raise RoundExecutionError("round_receipt_missing")
    receipt_raw = Path(receipt_value).expanduser()
    if not receipt_raw.is_absolute() or receipt_raw.is_symlink():
        raise RoundExecutionError("round_receipt_outside_private_root")
    receipt_path = receipt_raw.resolve()
    result_root = (data_root / "runs").resolve()
    if receipt_path.parent != result_root:
        raise RoundExecutionError("round_receipt_outside_private_root")
    if not receipt_path.is_file() or _mode(receipt_path) & 0o077:
        raise RoundExecutionError("round_receipt_not_private")
    try:
        receipt_bytes = receipt_path.read_bytes()
        full = json.loads(receipt_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RoundExecutionError("round_receipt_unreadable") from exc
    if not isinstance(full, dict) or full.get("schema_version") != "maplab.hermes.line-run.v2":
        raise RoundExecutionError("round_receipt_schema_invalid")
    run_id = full.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise RoundExecutionError("round_run_id_invalid")
    if receipt_path.name != f"{run_id}.json":
        raise RoundExecutionError("round_receipt_identity_mismatch")
    providers = full.get("providers") or []
    model = full.get("model")
    inference_parameters = full.get("inference_parameters")
    results = full.get("results")
    batch_value = full.get("batch")
    seed_value = full.get("seed")
    requested_stage = full.get("requested_stage")
    loopback_calls = full.get("loopback_ollama_calls")
    if (
        full.get("local_only") is not True
        or full.get("evaluator_version") != training_loop.EVALUATOR_VERSION
        or full.get("provider_policy") != "loopback-ollama-only"
        or full.get("ollama_endpoint") != training_loop.DEFAULT_OLLAMA_URL
        or not isinstance(model, str)
        or not model
        or inference_parameters != training_loop.INFERENCE_PARAMETERS
        or full.get("external_network_calls") != 0
        or not isinstance(results, list)
        or not results
        or not isinstance(batch_value, int)
        or isinstance(batch_value, bool)
        or batch_value != len(results)
        or not isinstance(seed_value, int)
        or isinstance(seed_value, bool)
        or (requested_stage is not None and (not isinstance(requested_stage, str) or not requested_stage))
        or not isinstance(loopback_calls, int)
        or isinstance(loopback_calls, bool)
        or loopback_calls != batch_value
        or not isinstance(providers, list)
        or not providers
        or any(not isinstance(provider, str) or not provider.startswith("local/ollama/") for provider in providers)
        or any(
            not isinstance(item, dict)
            or not isinstance(item.get("provider"), str)
            or not item["provider"].startswith("local/ollama/")
            for item in results
        )
    ):
        raise RoundExecutionError("provider_policy_violation")
    if any(
        item.get("inference_seed") != seed_value * 1000 + index
        for index, item in enumerate(results)
    ):
        raise RoundExecutionError("round_inference_seed_mismatch")
    evaluation_scores: list[float] = []
    derived_passed = 0
    derived_unsupported = 0
    for item in results:
        evaluation = item.get("evaluation")
        if not isinstance(evaluation, dict):
            raise RoundExecutionError("round_metrics_invalid")
        passed_value = evaluation.get("pass")
        score_value = evaluation.get("score")
        unsupported_money = evaluation.get("unsupported_money")
        if (
            not isinstance(passed_value, bool)
            or not isinstance(score_value, (int, float))
            or isinstance(score_value, bool)
            or not math.isfinite(float(score_value))
            or not 0.0 <= float(score_value) <= 100.0
            or not isinstance(unsupported_money, list)
            or any(not isinstance(value, str) for value in unsupported_money)
        ):
            raise RoundExecutionError("round_metrics_invalid")
        derived_passed += int(passed_value)
        derived_unsupported += int(bool(unsupported_money))
        evaluation_scores.append(float(score_value))
    result_providers = {item["provider"] for item in results}
    if set(providers) != result_providers or result_providers != {f"local/ollama/{model}"}:
        raise RoundExecutionError("provider_policy_violation")
    lesson_value = full.get("lesson_delta")
    if not isinstance(lesson_value, str):
        raise RoundExecutionError("lesson_delta_missing")
    lesson_raw = Path(lesson_value).expanduser()
    if not lesson_raw.is_absolute() or lesson_raw.is_symlink():
        raise RoundExecutionError("lesson_delta_not_private")
    lesson_path = lesson_raw.resolve()
    lesson_root = (data_root / "lesson_deltas").resolve()
    if (
        lesson_path.parent != lesson_root
        or not lesson_path.is_file()
        or _mode(lesson_path) & 0o077
    ):
        raise RoundExecutionError("lesson_delta_not_private")
    if lesson_path.name != f"{run_id}.md":
        raise RoundExecutionError("lesson_delta_identity_mismatch")
    try:
        pass_rate = float(full["pass_rate"])
        mean_score = float(full["mean_score"])
        unsupported_rate = float(full["unsupported_price_rate"])
        passed = full["passed"]
        unsupported_count = full["unsupported_price_count"]
        if (
            not math.isfinite(pass_rate)
            or not 0.0 <= pass_rate <= 1.0
            or not math.isfinite(mean_score)
            or not 0.0 <= mean_score <= 100.0
            or not math.isfinite(unsupported_rate)
            or not 0.0 <= unsupported_rate <= 1.0
            or not isinstance(passed, int)
            or isinstance(passed, bool)
            or not 0 <= passed <= batch_value
            or not isinstance(unsupported_count, int)
            or isinstance(unsupported_count, bool)
            or not 0 <= unsupported_count <= batch_value
            or pass_rate != round(passed / batch_value, 4)
            or unsupported_rate != round(unsupported_count / batch_value, 4)
            or passed != derived_passed
            or pass_rate != round(derived_passed / batch_value, 4)
            or unsupported_count != derived_unsupported
            or unsupported_rate != round(derived_unsupported / batch_value, 4)
            or mean_score != round(sum(evaluation_scores) / batch_value, 1)
        ):
            raise ValueError("incoherent round metrics")
        return {
            "run_id": run_id,
            "evaluator_version": full["evaluator_version"],
            "model": model,
            "inference_parameters": inference_parameters,
            "receipt": str(receipt_path),
            "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "lesson_delta": str(lesson_path),
            "lesson_delta_sha256": _sha256(lesson_path),
            "pass_rate": pass_rate,
            "mean_score": mean_score,
            "passed": passed,
            "unsupported_price_rate": unsupported_rate,
            "unsupported_price_count": unsupported_count,
            "lowest_stage": full.get("lowest_stage"),
            "providers": providers,
            "batch": batch_value,
            "seed": seed_value,
            "requested_stage": requested_stage,
            "external_network_calls": int(full.get("external_network_calls", -1)),
            "loopback_ollama_calls": loopback_calls,
        }
    except (TypeError, ValueError) as exc:
        raise RoundExecutionError("round_metrics_invalid") from exc


def validate_round_history(receipt: dict, data_root: Path, contract: dict) -> dict:
    rounds = receipt.get("rounds")
    if not isinstance(rounds, list):
        raise SupervisorError("supervisor_round_history_invalid")
    seen_run_ids: set[str] = set()
    seen_receipts: set[str] = set()
    seen_receipt_hashes: set[str] = set()
    seen_lessons: set[str] = set()
    seen_lesson_hashes: set[str] = set()
    loopback_total = 0
    success_streak = 0
    regression_streak = 0
    plateau_streak = 0
    best_pass_rate: float | None = None
    previous_pass_rate: float | None = None
    last_unsupported_rate: float | None = None
    lowest_stage = None
    diagnostic_mode = False
    next_stage = None
    method_review_required = False
    for history_index, item in enumerate(rounds):
        if not isinstance(item, dict):
            raise SupervisorError("supervisor_round_history_invalid")
        try:
            metrics = inspect_round({"receipt": item.get("receipt")}, data_root)
        except RoundExecutionError as exc:
            raise SupervisorError("supervisor_round_history_tampered") from exc
        if (
            metrics["evaluator_version"] != contract["evaluator_version"]
            or metrics["inference_parameters"] != contract["inference_parameters"]
            or metrics["model"] != contract["model"]
        ):
            raise SupervisorError("supervisor_round_qualification_mismatch")
        compared_keys = (
            "run_id",
            "receipt",
            "receipt_sha256",
            "lesson_delta",
            "lesson_delta_sha256",
            "pass_rate",
            "mean_score",
            "passed",
            "unsupported_price_rate",
            "unsupported_price_count",
            "lowest_stage",
            "providers",
            "batch",
            "seed",
            "requested_stage",
            "external_network_calls",
            "loopback_ollama_calls",
            "evaluator_version",
            "model",
            "inference_parameters",
        )
        if any(item.get(key) != metrics[key] for key in compared_keys):
            raise SupervisorError("supervisor_round_history_tampered")
        if (
            item.get("round_index") != history_index + 1
            or metrics["seed"] != int(contract["seed_base"]) + history_index
        ):
            raise SupervisorError("supervisor_round_seed_schedule_invalid")
        run_id = metrics["run_id"]
        receipt_value = metrics["receipt"]
        lesson_value = metrics["lesson_delta"]
        receipt_hash = metrics["receipt_sha256"]
        lesson_hash = metrics["lesson_delta_sha256"]
        identities = (
            (run_id, seen_run_ids),
            (receipt_value, seen_receipts),
            (receipt_hash, seen_receipt_hashes),
            (lesson_value, seen_lessons),
            (lesson_hash, seen_lesson_hashes),
        )
        if any(value in seen for value, seen in identities):
            raise SupervisorError("supervisor_round_history_replayed")
        for value, seen in identities:
            seen.add(value)
        loopback_total += metrics["batch"]
        diagnostic = item.get("diagnostic_mode") is True
        requested_stage = item.get("requested_stage")
        qualifying_round = (
            not diagnostic
            and contract.get("requested_stage") is None
            and requested_stage is None
        )
        if qualifying_round and metrics["batch"] != int(contract["base_batch"]):
            raise SupervisorError("supervisor_round_qualification_mismatch")
        if diagnostic and metrics["batch"] != min(5, int(contract["base_batch"])):
            raise SupervisorError("supervisor_round_qualification_mismatch")
        quality_gate_passed = (
            metrics["pass_rate"] >= float(contract["target_pass_rate"])
            and metrics["unsupported_price_rate"] == 0
            and metrics["unsupported_price_count"] == 0
        )
        successful = qualifying_round and quality_gate_passed
        if (
            item.get("qualifying_round") is not qualifying_round
            or item.get("quality_gate_passed") is not quality_gate_passed
            or item.get("successful") is not successful
        ):
            raise SupervisorError("supervisor_round_qualification_tampered")
        improved_or_equal = previous_pass_rate is None or metrics["pass_rate"] >= previous_pass_rate
        if previous_pass_rate is not None and metrics["pass_rate"] < previous_pass_rate:
            regression_streak += 1
        else:
            regression_streak = 0
        if qualifying_round:
            success_streak = success_streak + 1 if successful else 0
            if not method_review_required:
                plateau_streak = 0 if successful else min(
                    DEFAULT_PLATEAU_THRESHOLD, plateau_streak + 1
                )
                method_review_required = plateau_streak >= DEFAULT_PLATEAU_THRESHOLD
        best_pass_rate = (
            metrics["pass_rate"]
            if best_pass_rate is None
            else max(best_pass_rate, metrics["pass_rate"])
        )
        if method_review_required:
            diagnostic_mode = False
            next_stage = None
            success_streak = 0
        elif regression_streak >= int(contract["regression_threshold"]):
            diagnostic_mode = True
            next_stage = metrics["lowest_stage"]
            success_streak = 0
        elif diagnostic and improved_or_equal:
            diagnostic_mode = False
            next_stage = None
        previous_pass_rate = metrics["pass_rate"]
        last_unsupported_rate = metrics["unsupported_price_rate"]
        lowest_stage = metrics["lowest_stage"]
    if receipt.get("external_network_calls") != 0 or receipt.get("loopback_ollama_calls") != loopback_total:
        raise SupervisorError("supervisor_network_counter_mismatch")
    derived = {
        "success_streak": success_streak,
        "regression_streak": regression_streak,
        "plateau_streak": plateau_streak,
        "best_pass_rate": best_pass_rate,
        "last_pass_rate": previous_pass_rate,
        "last_unsupported_price_rate": last_unsupported_rate,
        "lowest_stage": lowest_stage,
        "diagnostic_mode": diagnostic_mode,
        "next_stage": next_stage,
        "method_review_required": method_review_required,
    }
    optional_migration_fields = {"plateau_streak", "method_review_required"}
    if any(
        receipt.get(key) != value
        for key, value in derived.items()
        if key not in optional_migration_fields
    ):
        raise SupervisorError("supervisor_derived_state_tampered")
    for key in optional_migration_fields:
        if key in receipt and receipt.get(key) != derived[key]:
            raise SupervisorError("supervisor_derived_state_tampered")
        receipt[key] = derived[key]
    if receipt.get("status") not in {
        "accepted",
        "running",
        "bounded_pause",
        "retry_pending",
        "blocked",
        "completed",
    }:
        raise SupervisorError("supervisor_receipt_status_invalid")
    if receipt.get("status") == "completed" and (
        success_streak < int(contract["target_streak"])
        or diagnostic_mode
        or regression_streak >= int(contract["regression_threshold"])
        or method_review_required
    ):
        raise SupervisorError("completed_receipt_invariant_failed")
    return derived


def ensure_fresh_round(receipt: dict, metrics: dict) -> None:
    for prior in receipt.get("rounds", []):
        if any(
            prior.get(key) == metrics[key]
            for key in (
                "run_id",
                "receipt",
                "receipt_sha256",
                "lesson_delta",
                "lesson_delta_sha256",
            )
        ):
            raise RoundExecutionError("round_replay_detected")


def _append_artifact(job: dict, path: str, kind: str) -> None:
    artifacts = list(job.get("artifacts") or [])
    if not any(item.get("path") == path for item in artifacts if isinstance(item, dict)):
        artifacts.append({"path": path, "kind": kind, "readback": "local-private-metrics-only"})
    job["artifacts"] = artifacts[-100:]


def _progress_result(receipt: dict, receipt_path: Path, status: str, reason: str) -> dict:
    return {
        "status": status,
        "reason": reason,
        "supervisor_receipt": str(receipt_path),
        "round_count": len(receipt.get("rounds", [])),
        "success_streak": int(receipt.get("success_streak") or 0),
        "plateau_streak": int(receipt.get("plateau_streak") or 0),
        "method_review_required": bool(receipt.get("method_review_required")),
        "target_streak": int(receipt.get("target_streak") or DEFAULT_TARGET_STREAK),
        "pass_rate": receipt.get("last_pass_rate"),
        "unsupported_price_rate": receipt.get("last_unsupported_price_rate"),
        "lowest_stage": receipt.get("lowest_stage"),
        "local_only": True,
        "customer_send": False,
        "external_network_calls": int(receipt.get("external_network_calls") or 0),
        "loopback_ollama_calls": int(receipt.get("loopback_ollama_calls") or 0),
    }


def _preserve_audited_method_redesign_pointer(job: dict) -> bool:
    """Keep a specific audited subphase from regressing to generic redesign.

    The first plateau transition legitimately creates ``method-redesign``.
    Once a zero-model audit has advanced the control plane to a named subphase
    such as ``method-redesign-schedule-gate`` or rubric calibration, a daily
    scheduler preflight must not overwrite that newer next action merely
    because the frozen supervisor receipt still requires method review.
    """

    phase = job.get("current_phase")
    return isinstance(phase, str) and phase.startswith("method-redesign-")


def _canonical_execution_disabled(job: dict) -> bool:
    """Honor an explicit or redesign-default stop before runtime receipts.

    A named method-redesign subphase is fail-closed: it may resume inference
    only when the canonical checkpoint explicitly sets ``execution_eligible``
    to true. This makes the stop survive a checkpoint that accidentally omits
    the flag instead of treating omission as permission.
    """

    last_result = job.get("last_result")
    execution_eligible = (
        last_result.get("execution_eligible") if isinstance(last_result, dict) else None
    )
    if execution_eligible is False:
        return True
    phase = job.get("current_phase")
    return (
        isinstance(phase, str)
        and phase.startswith("method-redesign-")
        and execution_eligible is not True
    )


def _canonical_supervisor_receipt_artifact(job: dict) -> Path:
    """Return the unique receipt pointer required for an attempted resume."""

    bindings = [
        item.get("path")
        for item in (job.get("artifacts") or [])
        if isinstance(item, dict) and item.get("kind") == "line-training-supervisor-receipt"
    ]
    if len(bindings) != 1 or not isinstance(bindings[0], str):
        raise SupervisorError("supervisor_receipt_artifact_binding_invalid")
    raw = Path(bindings[0]).expanduser()
    if not raw.is_absolute() or raw.is_symlink():
        raise SupervisorError("supervisor_receipt_artifact_path_invalid")
    return raw


def _supervise_locked(
    *,
    job_path: Path,
    job: dict,
    data_root: Path,
    max_rounds: int,
    max_seconds: int,
    batch: int,
    target_streak: int,
    target_pass_rate: float,
    regression_threshold: int,
    stage: str,
    seed_base: int,
    round_runner: Callable[..., dict] = run_round_subprocess,
    monotonic: Callable[[], float] = time.monotonic,
) -> tuple[dict, int]:
    if not 1 <= max_rounds <= HARD_MAX_ROUNDS:
        raise SupervisorError(f"max_rounds_must_be_1_to_{HARD_MAX_ROUNDS}")
    if not 1 <= max_seconds <= HARD_MAX_SECONDS:
        raise SupervisorError(f"max_seconds_must_be_1_to_{HARD_MAX_SECONDS}")
    if not 1 <= batch <= training_loop.MAX_BATCH:
        raise SupervisorError(f"batch_must_be_1_to_{training_loop.MAX_BATCH}")
    if not 1 <= target_streak <= 20:
        raise SupervisorError("target_streak_must_be_1_to_20")
    if not 0.0 <= target_pass_rate <= 1.0:
        raise SupervisorError("target_pass_rate_must_be_0_to_1")
    if not 1 <= regression_threshold <= 5:
        raise SupervisorError("regression_threshold_must_be_1_to_5")

    training_loop.validate_dataset_root(data_root)
    receipt_path, receipt = load_or_create_receipt(job, data_root)
    _, requested_model = training_loop.resolve_local_provider()
    requested_contract = {
        "version": "line-qualification-v1",
        "evaluator_version": training_loop.EVALUATOR_VERSION,
        "inference_parameters": training_loop.INFERENCE_PARAMETERS,
        "model": requested_model,
        "dataset_fingerprint": _dataset_fingerprint(data_root),
        "target_streak": target_streak,
        "target_pass_rate": target_pass_rate,
        "regression_threshold": regression_threshold,
        "base_batch": batch,
        "seed_base": seed_base,
        "requested_stage": stage or None,
    }
    qualification_contract = receipt.get("qualification_contract")
    if qualification_contract is None:
        if receipt.get("rounds"):
            raise SupervisorError("qualification_contract_missing_on_resume")
        qualification_contract = requested_contract
        receipt["qualification_contract"] = qualification_contract
    if not isinstance(qualification_contract, dict):
        raise SupervisorError("qualification_contract_invalid")
    try:
        target_streak = int(qualification_contract["target_streak"])
        target_pass_rate = float(qualification_contract["target_pass_rate"])
        regression_threshold = int(qualification_contract["regression_threshold"])
        batch = int(qualification_contract["base_batch"])
        seed_base = int(qualification_contract["seed_base"])
        locked_stage = qualification_contract.get("requested_stage")
    except (KeyError, TypeError, ValueError) as exc:
        raise SupervisorError("qualification_contract_invalid") from exc
    if (
        qualification_contract.get("version") != "line-qualification-v1"
        or qualification_contract.get("evaluator_version") != training_loop.EVALUATOR_VERSION
        or qualification_contract.get("inference_parameters") != training_loop.INFERENCE_PARAMETERS
        or not isinstance(qualification_contract.get("model"), str)
        or not qualification_contract.get("model")
        or not isinstance(qualification_contract.get("dataset_fingerprint"), str)
        or len(qualification_contract["dataset_fingerprint"]) != 64
        or not isinstance(qualification_contract.get("target_streak"), int)
        or isinstance(qualification_contract.get("target_streak"), bool)
        or not isinstance(qualification_contract.get("target_pass_rate"), (int, float))
        or isinstance(qualification_contract.get("target_pass_rate"), bool)
        or not math.isfinite(float(qualification_contract["target_pass_rate"]))
        or not isinstance(qualification_contract.get("regression_threshold"), int)
        or isinstance(qualification_contract.get("regression_threshold"), bool)
        or not isinstance(qualification_contract.get("base_batch"), int)
        or isinstance(qualification_contract.get("base_batch"), bool)
        or not isinstance(qualification_contract.get("seed_base"), int)
        or isinstance(qualification_contract.get("seed_base"), bool)
        or (locked_stage is not None and not isinstance(locked_stage, str))
    ):
        raise SupervisorError("qualification_contract_invalid")
    if any(
        qualification_contract[key] != requested_contract[key]
        for key in (
            "version",
            "evaluator_version",
            "inference_parameters",
            "model",
            "dataset_fingerprint",
        )
    ):
        raise SupervisorError("qualification_runtime_changed")
    stage = str(locked_stage or "")
    if not 1 <= target_streak <= 20 or not 0.0 <= target_pass_rate <= 1.0:
        raise SupervisorError("qualification_contract_invalid")
    if not 1 <= regression_threshold <= 5 or not 1 <= batch <= training_loop.MAX_BATCH:
        raise SupervisorError("qualification_contract_invalid")
    receipt["requested_contract_last_invocation"] = requested_contract
    receipt["resume_overrides_ignored"] = requested_contract != qualification_contract
    receipt["target_streak"] = target_streak
    receipt["target_pass_rate"] = target_pass_rate
    receipt["regression_threshold"] = regression_threshold
    derived = validate_round_history(receipt, data_root, qualification_contract)
    if derived["method_review_required"]:
        receipt["status"] = "bounded_pause"
        receipt["updated_at"] = utc_iso()
        _private_json(receipt_path, receipt)
        result = _progress_result(
            receipt,
            receipt_path,
            "bounded_pause",
            "plateau_method_review_required",
        )
        if _preserve_audited_method_redesign_pointer(job):
            return result, 0
        transition_durable_job(
            job_path,
            job,
            "RUNNING",
            reason="plateau_method_review_required",
            result=result,
            next_action=(
                "Plateau audit only: make zero model calls. Define a fixed holdout and one "
                "single-variable experiment with hypothesis, expected_delta, stop_loss, and "
                "method_version before creating a new qualification contract."
            ),
            current_phase="method-redesign",
        )
        return result, 0
    if receipt.get("status") == "completed":
        result = _progress_result(receipt, receipt_path, "completed", "target_streak_reached")
        transition_durable_job(
            job_path,
            job,
            "COMPLETED",
            reason="target_streak_reached",
            result=result,
            next_action="Owner reviews the private LINE training metrics; no customer message was sent.",
        )
        return result, 0
    if (
        derived["success_streak"] >= target_streak
        and derived["diagnostic_mode"] is False
        and derived["regression_streak"] < regression_threshold
    ):
        receipt["status"] = "completed"
        receipt["updated_at"] = utc_iso()
        _private_json(receipt_path, receipt)
        result = _progress_result(receipt, receipt_path, "completed", "target_streak_recovered")
        transition_durable_job(
            job_path,
            job,
            "COMPLETED",
            reason="target_streak_recovered",
            result=result,
            next_action="Owner reviews the private LINE training metrics; no customer message was sent.",
        )
        return result, 0

    start = monotonic()
    invocation = {
        "started_at": utc_iso(),
        "starting_round": len(receipt.get("rounds", [])),
        "max_rounds": max_rounds,
        "max_seconds": max_seconds,
    }
    receipt.setdefault("invocations", []).append(invocation)
    receipt["invocations"] = receipt["invocations"][-100:]
    receipt["status"] = "running"
    receipt["updated_at"] = utc_iso()
    _private_json(receipt_path, receipt)
    job["attempt"] = int(job.get("attempt") or 0) + 1
    _append_artifact(job, str(receipt_path), "line-training-supervisor-receipt")
    transition_durable_job(
        job_path,
        job,
        "RUNNING",
        reason="local_bounded_training_started",
        result=_progress_result(receipt, receipt_path, "running", "bounded invocation started"),
        next_action="Run bounded local-only LINE evaluation rounds and checkpoint after every round.",
    )

    rounds_this_invocation = 0
    exit_code = 0
    stop_reason = "max_rounds_reached"
    final_state = "RUNNING"
    final_result_status = "bounded_pause"
    next_action = "Resume this same supervisor job for the next bounded local-only round set."

    while rounds_this_invocation < max_rounds:
        elapsed = monotonic() - start
        remaining = max_seconds - elapsed
        if remaining < 1.0:
            stop_reason = "max_seconds_reached"
            break
        total_rounds = len(receipt.get("rounds", []))
        diagnostic = bool(receipt.get("diagnostic_mode")) and not stage
        round_stage = stage or (str(receipt.get("next_stage") or "") if diagnostic else "")
        round_batch = min(5, batch) if diagnostic else batch
        round_seed = seed_base + total_rounds
        try:
            payload = round_runner(
                data_root=data_root,
                batch=round_batch,
                seed=round_seed,
                stage=round_stage,
                timeout_seconds=remaining,
            )
            metrics = inspect_round(payload, data_root)
            ensure_fresh_round(receipt, metrics)
            if (
                metrics["evaluator_version"] != qualification_contract["evaluator_version"]
                or metrics["inference_parameters"] != qualification_contract["inference_parameters"]
                or metrics["model"] != qualification_contract["model"]
                or metrics["batch"] != round_batch
                or metrics["seed"] != round_seed
                or metrics["requested_stage"] != (round_stage or None)
            ):
                raise RoundExecutionError("round_invocation_mismatch")
        except RoundExecutionError as exc:
            if exc.timed_out:
                stop_reason = "round_wall_timeout"
                final_state = "RUNNING"
                final_result_status = "bounded_pause"
                exit_code = 0
                next_action = "Resume the same job; the last local round exceeded this invocation wall bound."
            elif exc.exit_code in {2, 3} or exc.reason in {
                "provider_policy_violation",
                "round_receipt_outside_private_root",
                "round_receipt_not_private",
                "lesson_delta_missing",
                "lesson_delta_not_private",
                "lesson_delta_identity_mismatch",
                "round_output_invalid",
                "round_receipt_schema_invalid",
                "round_run_id_invalid",
                "round_receipt_identity_mismatch",
                "round_metrics_invalid",
                "round_replay_detected",
                "round_qualification_mismatch",
                "round_invocation_mismatch",
                "round_inference_seed_mismatch",
            }:
                stop_reason = exc.reason
                final_state = "BLOCKED"
                final_result_status = "blocked"
                exit_code = 3
                next_action = "Repair the local corpus/config privacy gate, then resume the same job."
            else:
                stop_reason = exc.reason
                final_state = "RUNNING"
                final_result_status = "retry_pending"
                exit_code = 4
                next_action = "Retry the same bounded local-only round; do not switch to a cloud provider."
            break

        previous = receipt.get("last_pass_rate")
        improved_or_equal = not isinstance(previous, (int, float)) or metrics["pass_rate"] >= previous
        if isinstance(previous, (int, float)) and metrics["pass_rate"] < previous:
            receipt["regression_streak"] = int(receipt.get("regression_streak") or 0) + 1
        else:
            receipt["regression_streak"] = 0
        quality_gate_passed = (
            metrics["pass_rate"] >= target_pass_rate
            and metrics["unsupported_price_rate"] == 0
            and metrics["unsupported_price_count"] == 0
        )
        qualifying_round = not diagnostic and not stage
        successful = quality_gate_passed and qualifying_round
        if qualifying_round:
            receipt["success_streak"] = (
                int(receipt.get("success_streak") or 0) + 1 if successful else 0
            )
            if not receipt.get("method_review_required"):
                receipt["plateau_streak"] = (
                    0
                    if successful
                    else min(
                        DEFAULT_PLATEAU_THRESHOLD,
                        int(receipt.get("plateau_streak") or 0) + 1,
                    )
                )
                receipt["method_review_required"] = (
                    int(receipt.get("plateau_streak") or 0) >= DEFAULT_PLATEAU_THRESHOLD
                )
        best = receipt.get("best_pass_rate")
        receipt["best_pass_rate"] = (
            metrics["pass_rate"] if not isinstance(best, (int, float)) else max(best, metrics["pass_rate"])
        )
        receipt["last_pass_rate"] = metrics["pass_rate"]
        receipt["last_unsupported_price_rate"] = metrics["unsupported_price_rate"]
        receipt["external_network_calls"] = int(receipt.get("external_network_calls") or 0)
        receipt["loopback_ollama_calls"] = int(receipt.get("loopback_ollama_calls") or 0) + metrics[
            "loopback_ollama_calls"
        ]
        receipt["lowest_stage"] = metrics["lowest_stage"]
        if receipt.get("method_review_required"):
            receipt["diagnostic_mode"] = False
            receipt["next_stage"] = None
            receipt["success_streak"] = 0
        elif int(receipt.get("regression_streak") or 0) >= regression_threshold:
            receipt["diagnostic_mode"] = True
            receipt["next_stage"] = metrics["lowest_stage"]
            receipt["success_streak"] = 0
        elif diagnostic and improved_or_equal:
            receipt["diagnostic_mode"] = False
            receipt["next_stage"] = None
        receipt.setdefault("rounds", []).append(
            {
                "round_index": total_rounds + 1,
                "finished_at": utc_iso(),
                "seed": round_seed,
                "requested_stage": round_stage or None,
                "diagnostic_mode": diagnostic,
                "qualifying_round": qualifying_round,
                "quality_gate_passed": quality_gate_passed,
                "successful": successful,
                **metrics,
            }
        )
        receipt["updated_at"] = utc_iso()
        _private_json(receipt_path, receipt)
        _append_artifact(job, metrics["receipt"], "line-training-round-receipt")
        _append_artifact(job, metrics["lesson_delta"], "line-training-lesson-delta")
        rounds_this_invocation += 1
        progress = _progress_result(receipt, receipt_path, "running", "round checkpointed")
        job["last_result"] = progress
        job["next_bounded_action"] = (
            "Plateau audit only; make zero model calls and design a fixed-holdout, "
            "single-variable experiment."
            if receipt.get("method_review_required")
            else "Continue the current bounded local-only round set."
        )
        write_durable_job(job_path, job)
        if receipt.get("method_review_required"):
            stop_reason = "plateau_method_review_required"
            final_state = "RUNNING"
            final_result_status = "bounded_pause"
            next_action = (
                "Plateau audit only: make zero model calls. Define a fixed holdout and one "
                "single-variable experiment with hypothesis, expected_delta, stop_loss, and "
                "method_version before creating a new qualification contract."
            )
            break
        if (
            int(receipt.get("success_streak") or 0) >= target_streak
            and receipt.get("diagnostic_mode") is False
            and int(receipt.get("regression_streak") or 0) < regression_threshold
        ):
            stop_reason = "target_streak_reached"
            final_state = "COMPLETED"
            final_result_status = "completed"
            next_action = "Owner reviews the private metrics; no LINE or Telegram customer message was sent."
            break

    invocation["finished_at"] = utc_iso()
    invocation["rounds_completed"] = rounds_this_invocation
    invocation["reason"] = stop_reason
    receipt["status"] = final_result_status
    receipt["updated_at"] = utc_iso()
    _private_json(receipt_path, receipt)
    result = _progress_result(receipt, receipt_path, receipt["status"], stop_reason)
    transition_durable_job(
        job_path,
        job,
        final_state,
        reason=stop_reason,
        result=result,
        next_action=next_action,
        current_phase=(
            "method-redesign"
            if stop_reason == "plateau_method_review_required"
            else None
        ),
    )
    return result, exit_code


def supervise(
    *,
    job_path: Path,
    job: dict,
    data_root: Path,
    max_rounds: int,
    max_seconds: int,
    batch: int,
    target_streak: int,
    target_pass_rate: float,
    regression_threshold: int,
    stage: str,
    seed_base: int,
    round_runner: Callable[..., dict] = run_round_subprocess,
    monotonic: Callable[[], float] = time.monotonic,
) -> tuple[dict, int]:
    """Run one invocation while exclusively owning and re-reading the job."""

    canonical_path, prelock_job = read_durable_job(job_path)
    if job.get("job_id") != prelock_job.get("job_id"):
        raise SupervisorError("durable_job_identity_changed")
    descriptor = _acquire_job_lock(canonical_path)
    if descriptor is None:
        receipt_path = data_root / "supervisor_jobs" / prelock_job["job_id"] / "receipt.json"
        return (
            {
                "status": "running",
                "reason": "already_running",
                "supervisor_receipt": str(receipt_path),
                "local_only": True,
                "customer_send": False,
                "external_network_calls": 0,
                "loopback_ollama_calls": 0,
            },
            0,
        )
    try:
        canonical_path, locked_job = read_durable_job(canonical_path)
        if locked_job.get("state") not in RESUMABLE_JOB_STATES:
            return (
                {
                    "status": str(locked_job["state"]).lower(),
                    "reason": "canonical_state_gate",
                    "supervisor_receipt": None,
                    "local_only": True,
                    "customer_send": False,
                    "external_network_calls": 0,
                    "loopback_ollama_calls": 0,
                },
                5 if locked_job["state"] == "FAILED" else 4,
            )
        if _canonical_execution_disabled(locked_job):
            return (
                {
                    "status": "bounded_pause",
                    "reason": "canonical_execution_disabled",
                    "supervisor_receipt": None,
                    "local_only": True,
                    "customer_send": False,
                    "external_network_calls": 0,
                    "loopback_ollama_calls": 0,
                },
                0,
            )
        try:
            return _supervise_locked(
                job_path=canonical_path,
                job=locked_job,
                data_root=data_root,
                max_rounds=max_rounds,
                max_seconds=max_seconds,
                batch=batch,
                target_streak=target_streak,
                target_pass_rate=target_pass_rate,
                regression_threshold=regression_threshold,
                stage=stage,
                seed_base=seed_base,
                round_runner=round_runner,
                monotonic=monotonic,
            )
        except (SupervisorError, training_loop.TrainingConfigError, training_loop.DatasetError) as exc:
            reason = str(exc)
            _, current_job = read_durable_job(canonical_path)
            if current_job.get("state") in {"ACCEPTED", "RUNNING", "BLOCKED"}:
                transition_durable_job(
                    canonical_path,
                    current_job,
                    "BLOCKED",
                    reason=reason,
                    result={
                        "status": "blocked",
                        "reason": reason,
                        "local_only": True,
                        "customer_send": False,
                        "supervisor_receipt": None,
                        "external_network_calls": 0,
                        "loopback_ollama_calls": 0,
                    },
                    next_action="Repair the local corpus/config privacy gate, then resume the same durable job.",
                )
            raise
        except Exception as exc:
            reason = f"supervisor_internal_error:{type(exc).__name__}"
            _, current_job = read_durable_job(canonical_path)
            if current_job.get("state") in {"ACCEPTED", "RUNNING", "BLOCKED"}:
                transition_durable_job(
                    canonical_path,
                    current_job,
                    "FAILED",
                    reason=reason,
                    result={
                        "status": "failed",
                        "reason": reason,
                        "local_only": True,
                        "customer_send": False,
                        "supervisor_receipt": None,
                        "external_network_calls": 0,
                        "loopback_ollama_calls": 0,
                    },
                    next_action="Inspect the sanitized supervisor error and resume only after repair.",
                )
            raise
    finally:
        _release_job_lock(descriptor)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resume a canonical Hermes LINE durable job using bounded local-only rounds."
    )
    parser.add_argument("--job-path", required=True)
    parser.add_argument("--data-root")
    parser.add_argument("--max-rounds", type=int, default=DEFAULT_MAX_ROUNDS)
    parser.add_argument("--max-seconds", type=int, default=DEFAULT_MAX_SECONDS)
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    parser.add_argument("--target-streak", type=int, default=DEFAULT_TARGET_STREAK)
    parser.add_argument("--target-pass-rate", type=float, default=DEFAULT_TARGET_PASS_RATE)
    parser.add_argument("--regression-threshold", type=int, default=DEFAULT_REGRESSION_THRESHOLD)
    parser.add_argument("--stage", default="")
    parser.add_argument("--seed-base", type=int)
    return parser


def resolve_supervisor_data_root(job: dict, cli_value: str | None = None) -> Path:
    """Resolve a resumed job to the private dataset recorded in its receipt.

    A durable job must not silently fall back to a machine-wide default after
    its first round.  An explicit CLI value is still authoritative for initial
    setup and diagnostics.  On resume, the canonical receipt pointer binds the
    job to the same private data root even when launchd or an interactive shell
    omitted ``HERMES_LINE_DATA_ROOT``.
    """

    cli_root = training_loop.resolve_data_root(cli_value) if cli_value else None

    # A fail-closed redesign checkpoint must be able to stop even if a
    # historical receipt was lost. It never reaches receipt creation or a
    # model call; this root is used only to construct the zero-write result.
    if _canonical_execution_disabled(job):
        return cli_root or training_loop.resolve_data_root(None)

    attempt = job.get("attempt", 0)
    if attempt == 0:
        if cli_root is not None:
            return cli_root
    else:
        receipt_path = _canonical_supervisor_receipt_artifact(job)
        if not receipt_path.exists():
            raise SupervisorError("supervisor_receipt_artifact_missing")
        if cli_root is not None:
            expected = (
                cli_root
                / "supervisor_jobs"
                / str(job.get("job_id") or "")
                / "receipt.json"
            )
            if receipt_path.resolve() != expected.resolve():
                raise SupervisorError("supervisor_cli_data_root_mismatch")

    last_result = job.get("last_result")
    receipt_value = (
        last_result.get("supervisor_receipt") if isinstance(last_result, dict) else None
    )
    if attempt > 0:
        receipt_value = str(receipt_path)
    if not receipt_value:
        return training_loop.resolve_data_root(None)
    if not isinstance(receipt_value, str):
        raise SupervisorError("supervisor_receipt_path_invalid")

    receipt_path = Path(receipt_value).expanduser()
    if not receipt_path.is_absolute() or receipt_path.is_symlink():
        raise SupervisorError("supervisor_receipt_path_invalid")
    try:
        receipt_info = receipt_path.stat()
    except OSError as exc:
        raise SupervisorError("supervisor_receipt_unavailable") from exc
    if not stat.S_ISREG(receipt_info.st_mode) or stat.S_IMODE(receipt_info.st_mode) & 0o077:
        raise SupervisorError("supervisor_receipt_not_private")
    if hasattr(os, "getuid") and receipt_info.st_uid != os.getuid():
        raise SupervisorError("supervisor_receipt_wrong_owner")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SupervisorError("supervisor_receipt_invalid") from exc
    if not isinstance(receipt, dict) or not isinstance(receipt.get("data_root"), str):
        raise SupervisorError("supervisor_receipt_data_root_missing")

    data_root = training_loop.resolve_data_root(receipt["data_root"])
    expected_receipt = (
        data_root
        / "supervisor_jobs"
        / str(job.get("job_id") or "")
        / "receipt.json"
    )
    if receipt_path.resolve() != expected_receipt.resolve():
        raise SupervisorError("supervisor_receipt_data_root_mismatch")
    return data_root


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    args = build_parser().parse_args(argv)
    job_path: Path | None = None
    job: dict | None = None
    try:
        job_path, job = read_durable_job(args.job_path)
        data_root = resolve_supervisor_data_root(job, args.data_root)
        seed_base = args.seed_base
        if seed_base is None:
            seed_base = int(datetime.now(timezone.utc).strftime("%Y%m%d%H")) * 100
        result, exit_code = supervise(
            job_path=job_path,
            job=job,
            data_root=data_root,
            max_rounds=args.max_rounds,
            max_seconds=args.max_seconds,
            batch=args.batch,
            target_streak=args.target_streak,
            target_pass_rate=args.target_pass_rate,
            regression_threshold=args.regression_threshold,
            stage=args.stage.strip(),
            seed_base=seed_base,
        )
    except (SupervisorError, training_loop.TrainingConfigError, training_loop.DatasetError) as exc:
        if job_path is not None and job is not None:
            reason = str(exc)
            result = {
                "status": "blocked",
                "reason": reason,
                "local_only": True,
                "customer_send": False,
                "supervisor_receipt": None,
                "external_network_calls": 0,
                "loopback_ollama_calls": 0,
            }
            try:
                _transition_after_error_if_idle(
                    job_path,
                    expected_job=job,
                    state="BLOCKED",
                    reason=reason,
                    result=result,
                    next_action="Repair the local corpus/config privacy gate, then resume the same durable job.",
                )
            except (OSError, SupervisorError):
                pass
        print(f"supervisor_error:{exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # defensive terminalization; never include private exception text
        result = {
            "status": "failed",
            "reason": f"supervisor_internal_error:{type(exc).__name__}",
            "local_only": True,
            "customer_send": False,
            "supervisor_receipt": None,
            "external_network_calls": 0,
            "loopback_ollama_calls": 0,
        }
        if job_path is not None and job is not None:
            try:
                _transition_after_error_if_idle(
                    job_path,
                    expected_job=job,
                    state="FAILED",
                    reason=result["reason"],
                    result=result,
                    next_action="Inspect the sanitized supervisor error and resume only after repair.",
                )
            except (OSError, SupervisorError):
                pass
        print(result["reason"], file=sys.stderr)
        return 5
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
