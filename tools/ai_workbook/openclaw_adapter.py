from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .paths import REVIEWS_DIR


@dataclass
class TaskExecution:
    job_id: str
    requested_model: str
    requested_engine: str
    used_engine: str
    used_model: str
    started_at: str
    finished_at: str
    duration_seconds: float
    return_code: int
    stdout: str
    stderr: str
    fallback_used: bool
    command: List[str]
    bundle_dir: Path


class OpenClawAdapter:
    def __init__(self, default_model: Optional[str] = None) -> None:
        self.default_model = default_model or os.getenv("MAPLAB_LOCAL_MODEL", "qwen2.5:14b")

    def run_local_task(
        self,
        job_id: str,
        prompt: str,
        model: Optional[str] = None,
        engine: str = "auto",
        thinking: str = "low",
    ) -> Dict[str, Any]:
        bundle_dir = REVIEWS_DIR / job_id
        screenshots_dir = bundle_dir / "screenshots"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        requested_model = model or self.default_model
        started = datetime.now(timezone.utc)
        task_request_path = bundle_dir / "task_request.md"
        task_request_path.write_text(
            _render_task_request(job_id=job_id, prompt=prompt, model=requested_model, engine=engine, thinking=thinking),
            encoding="utf-8",
        )

        execution = self._execute_prompt(
            job_id=job_id,
            prompt=prompt,
            model=requested_model,
            engine=engine,
            thinking=thinking,
            bundle_dir=bundle_dir,
        )

        finished = datetime.now(timezone.utc)
        duration = (finished - started).total_seconds()

        parsed_payload = _parse_jsonish(execution.stdout)
        response_text = _extract_response_text(parsed_payload, execution.stdout)

        output_json_path = bundle_dir / "output.json"
        output_json_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "requested_engine": engine,
                    "requested_model": requested_model,
                    "used_engine": execution.used_engine,
                    "used_model": execution.used_model,
                    "fallback_used": execution.fallback_used,
                    "command": execution.command,
                    "stdout": execution.stdout,
                    "stderr": execution.stderr,
                    "parsed_stdout": parsed_payload,
                    "response_text": response_text,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        draft_path = bundle_dir / "draft.md"
        draft_path.write_text(response_text.strip() or "# Empty response\n", encoding="utf-8")

        exec_log = {
            "job_id": job_id,
            "requested_engine": engine,
            "requested_model": requested_model,
            "used_engine": execution.used_engine,
            "used_model": execution.used_model,
            "fallback_used": execution.fallback_used,
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "duration_seconds": duration,
            "return_code": execution.return_code,
            "command": execution.command,
            "command_text": shlex.join(execution.command),
            "status": "success" if execution.return_code == 0 else "failed",
        }
        execution_log_path = bundle_dir / "execution_log.json"
        execution_log_path.write_text(json.dumps(exec_log, ensure_ascii=False, indent=2), encoding="utf-8")

        verification_log = {
            "job_id": job_id,
            "verified_by": "OpenClawAdapter",
            "verified_at": finished.isoformat(),
            "verification_targets": [
                {
                    "type": "bundle",
                    "expected": "task_request, output, execution_log, review_request",
                    "observed": "bundle files written locally",
                    "result": "pass" if execution.return_code == 0 else "fail",
                },
                {
                    "type": "runtime",
                    "expected": "OpenClaw first, Ollama fallback if needed",
                    "observed": f"used={execution.used_engine} fallback={execution.fallback_used}",
                    "result": "pass",
                },
            ],
            "overall_result": "pass" if execution.return_code == 0 else "fail",
        }
        verification_log_path = bundle_dir / "verification_log.json"
        verification_log_path.write_text(
            json.dumps(verification_log, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        review_request_path = bundle_dir / "review_request.md"
        review_request_path.write_text(
            _render_review_request(
                job_id=job_id,
                model=execution.used_model,
                engine=execution.used_engine,
                output_path=output_json_path if response_text else draft_path,
                status="waiting_for_review",
            ),
            encoding="utf-8",
        )

        bundle_ready = all(
            path.exists()
            for path in [
                task_request_path,
                output_json_path,
                draft_path,
                execution_log_path,
                verification_log_path,
                review_request_path,
            ]
        )
        response_ready = bool(response_text.strip())
        overall_success = bundle_ready and response_ready

        exec_log["status"] = "success" if overall_success else "failed"
        if overall_success and execution.return_code != 0:
            exec_log["status_note"] = "success_with_warnings"
        execution_log_path.write_text(json.dumps(exec_log, ensure_ascii=False, indent=2), encoding="utf-8")

        verification_log["verification_targets"][0]["result"] = "pass" if overall_success else "fail"
        verification_log["overall_result"] = "pass" if overall_success else "fail"
        verification_log_path.write_text(
            json.dumps(verification_log, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        manifest = _build_manifest(
            bundle_dir,
            [
                task_request_path,
                output_json_path,
                draft_path,
                execution_log_path,
                verification_log_path,
                review_request_path,
            ],
        )
        manifest_path = bundle_dir / "output_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        terminal_log = screenshots_dir / "terminal.log"
        terminal_log.write_text(
            _render_terminal_log(job_id=job_id, prompt=prompt, execution=execution, response_text=response_text),
            encoding="utf-8",
        )

        return {
            "job_id": job_id,
            "bundle_dir": str(bundle_dir),
            "task_request": str(task_request_path),
            "output_json": str(output_json_path),
            "draft_md": str(draft_path),
            "execution_log": str(execution_log_path),
            "verification_log": str(verification_log_path),
            "review_request": str(review_request_path),
            "manifest": str(manifest_path),
            "terminal_log": str(terminal_log),
            "engine_used": execution.used_engine,
            "model_used": execution.used_model,
            "fallback_used": execution.fallback_used,
            "return_code": execution.return_code,
        }

    def _execute_prompt(
        self,
        job_id: str,
        prompt: str,
        model: str,
        engine: str,
        thinking: str,
        bundle_dir: Path,
    ) -> TaskExecution:
        started = datetime.now(timezone.utc)
        openclaw_model = _openclaw_model_ref(model)
        ollama_model = _ollama_model_name(model)
        command = []
        fallback_used = False
        attempted_openclaw: List[Dict[str, Any]] = []

        if engine in {"auto", "openclaw"}:
            for candidate_thinking in _thinking_candidates(thinking):
                command = [
                    "openclaw",
                    "agent",
                    "--local",
                    "--json",
                    "--session-id",
                    job_id,
                    "--model",
                    openclaw_model,
                    "--thinking",
                    candidate_thinking,
                    "--message",
                    prompt,
                ]
                proc = _run_command(command, timeout=int(os.getenv("OPENCLAW_AGENT_TIMEOUT_SECONDS", "120")))
                attempted_openclaw.append(
                    {
                        "thinking": candidate_thinking,
                        "command": command,
                        "return_code": proc.returncode,
                        "stdout": proc.stdout,
                        "stderr": proc.stderr,
                    }
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    finished = datetime.now(timezone.utc)
                    return TaskExecution(
                        job_id=job_id,
                        requested_model=model,
                        requested_engine=engine,
                        used_engine="openclaw",
                        used_model=openclaw_model,
                        started_at=started.isoformat(),
                        finished_at=finished.isoformat(),
                        duration_seconds=(finished - started).total_seconds(),
                        return_code=proc.returncode,
                        stdout=proc.stdout,
                        stderr=proc.stderr,
                        fallback_used=False,
                        command=command,
                        bundle_dir=bundle_dir,
                    )
            fallback_used = True

        command = ["ollama", "run", ollama_model, prompt]
        proc = _run_command(command, timeout=600)
        finished = datetime.now(timezone.utc)
        stderr_text = proc.stderr
        if attempted_openclaw:
            stderr_text = (
                stderr_text
                + "\n\n--- openclaw_attempts ---\n"
                + json.dumps(attempted_openclaw, ensure_ascii=False, indent=2)
            )
        return TaskExecution(
            job_id=job_id,
            requested_model=model,
            requested_engine=engine,
            used_engine="ollama",
            used_model=ollama_model,
            started_at=started.isoformat(),
            finished_at=finished.isoformat(),
            duration_seconds=(finished - started).total_seconds(),
            return_code=proc.returncode,
            stdout=proc.stdout,
            stderr=stderr_text,
            fallback_used=fallback_used,
            command=command,
            bundle_dir=bundle_dir,
        )


def _run_command(command: Sequence[str], timeout: int = 600) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            command,
            returncode=-1,
            stdout="",
            stderr=f"timeout after {timeout}s",
        )


def _parse_jsonish(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except Exception:
        pass
    for candidate in _iter_json_candidates(stripped):
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def _iter_json_candidates(text: str) -> Iterable[str]:
    start = text.find("{")
    while start != -1:
        end = text.rfind("}")
        if end > start:
            yield text[start : end + 1]
        start = text.find("{", start + 1)


def _extract_response_text(parsed: Any, fallback: str) -> str:
    if isinstance(parsed, str):
        return parsed
    if isinstance(parsed, dict):
        for key in [
            "response_text",
            "response",
            "content",
            "text",
            "output",
            "message",
            "final",
            "reply",
            "raw_text",
        ]:
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                return value
        nested = parsed.get("result")
        if isinstance(nested, dict):
            nested_text = _extract_response_text(nested, "")
            if nested_text:
                return nested_text
    return fallback


def _build_manifest(bundle_dir: Path, files: Sequence[Path]) -> Dict[str, Any]:
    manifest = []
    for file_path in files:
        if not file_path.exists():
            continue
        manifest.append(
            {
                "path": str(file_path.relative_to(bundle_dir)),
                "bytes": file_path.stat().st_size,
                "sha256": _sha256(file_path),
            }
        )
    return {
        "bundle_dir": str(bundle_dir),
        "files": manifest,
    }


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_task_request(job_id: str, prompt: str, model: str, engine: str, thinking: str) -> str:
    return f"""# Task Request

job_id: {job_id}
engine: {engine}
model: {model}
thinking: {thinking}
status: queued

## Prompt

```text
{prompt}
```
"""


def _render_review_request(job_id: str, model: str, engine: str, output_path: Path, status: str) -> str:
    return f"""# Review Request

status: {status}
job_id: {job_id}
engine_used: {engine}
model_used: {model}
output_path: {output_path.as_posix()}

## Reviewer checklist

1. Confirm the bundle files exist.
2. Confirm the output matches the requested prompt.
3. Confirm nothing wrote to formal truth sources.
4. Decide whether the task can be closed.
"""


def _render_terminal_log(job_id: str, prompt: str, execution: TaskExecution, response_text: str) -> str:
    return f"""JOB: {job_id}
Requested engine: {execution.requested_engine}
Requested model: {execution.requested_model}
Used engine: {execution.used_engine}
Used model: {execution.used_model}
Fallback used: {execution.fallback_used}
Return code: {execution.return_code}
Duration seconds: {execution.duration_seconds:.2f}

Command:
{shlex.join(execution.command)}

Prompt:
{prompt}

--- stdout ---
{execution.stdout}

--- stderr ---
{execution.stderr}

--- extracted response ---
{response_text}
"""


def _openclaw_model_ref(model: str) -> str:
    if "/" in model:
        return model
    return f"ollama/{model}"


def _ollama_model_name(model: str) -> str:
    if "/" in model:
        return model.split("/", 1)[1]
    return model


def _thinking_candidates(requested: str) -> List[str]:
    candidates = [requested]
    if requested != "off":
        candidates.append("off")
    seen: List[str] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.append(candidate)
    return seen
