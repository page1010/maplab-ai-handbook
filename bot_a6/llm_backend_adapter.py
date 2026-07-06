"""A6 LLM backend adapter — skeleton only, NOT wired into bot_a6.py yet.

Design doc: projects/a6-llm-backend-adapter.md
Routing rules: skills/codex-offload-guide.md

Goal: make the model that actually generates text for A6 pluggable
(codex -> antigravity -> ollama) without changing the role/division of
labor above it. This module intentionally mirrors the subprocess/HTTP
call patterns already proven in bot_a6.py (_codex_generate_sync,
_ollama_generate_sync) so wiring it in later is a small, reviewable diff.

Do not import this from bot_a6.py until the Antigravity read-only
permission question in the design doc is resolved.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path


class BackendError(RuntimeError):
    """Raised when a backend fails to produce an answer."""


class Backend:
    name = "base"

    def generate(self, prompt: str, timeout: int) -> str:
        raise NotImplementedError


class CodexBackend(Backend):
    name = "codex"

    def __init__(self, repo_path: Path, codex_bin: str, model: str = ""):
        self.repo_path = repo_path
        self.codex_bin = codex_bin
        self.model = model

    def generate(self, prompt: str, timeout: int = 180) -> str:
        codex_path = Path(self.codex_bin)
        if not codex_path.exists():
            raise BackendError(f"codex binary not found: {self.codex_bin}")

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as fh:
            output_path = fh.name

        cmd = [
            str(codex_path),
            "exec",
            "--ephemeral",
            "-C",
            str(self.repo_path),
            "-s",
            "read-only",
            "-o",
            output_path,
        ]
        if self.model:
            cmd.extend(["-m", self.model])
        cmd.append("-")

        env = os.environ.copy()
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:" + env.get("PATH", "")
        try:
            proc = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout,
                cwd=self.repo_path,
                env=env,
            )
            output_file = Path(output_path)
            answer = output_file.read_text(encoding="utf-8").strip() if output_file.exists() else ""
            if proc.returncode != 0:
                raise BackendError(f"codex exit={proc.returncode}: {(proc.stderr or proc.stdout)[:300]}")
            answer = answer or proc.stdout.strip()
            if not answer:
                raise BackendError("codex returned empty answer")
            return answer
        finally:
            Path(output_path).unlink(missing_ok=True)


class AntigravityBackend(Backend):
    """agy --print backend.

    NOT confirmed read-only. See "risk" section in the design doc before
    routing anything customer-facing or write-capable through this.
    """

    name = "antigravity"

    def __init__(self, agy_bin: str = "/opt/homebrew/bin/agy", model: str = ""):
        self.agy_bin = agy_bin
        self.model = model

    def generate(self, prompt: str, timeout: int = 180) -> str:
        agy_path = Path(self.agy_bin)
        if not agy_path.exists():
            raise BackendError(f"agy binary not found: {self.agy_bin}")

        cmd = [str(agy_path), "--print"]
        if self.model:
            cmd.extend(["--model", self.model])
        cmd.append(prompt)

        try:
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise BackendError(f"agy timed out after {timeout}s") from exc

        if proc.returncode != 0:
            raise BackendError(f"agy exit={proc.returncode}: {(proc.stderr or proc.stdout)[:300]}")
        answer = proc.stdout.strip()
        if not answer:
            raise BackendError("agy returned empty answer")
        return answer


class OllamaBackend(Backend):
    """Cold fallback. Kept last in the chain on purpose — llama-server
    holds ~9-14GB RSS while loaded, which is part of the RAM pressure
    flagged 2026-07-06. Only wake it when codex and antigravity both fail.
    """

    name = "ollama"

    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "llama3.1:latest"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, timeout: int = 45) -> str:
        payload = json.dumps(
            {"model": self.model, "prompt": prompt, "stream": False},
            ensure_ascii=False,
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception as exc:
            raise BackendError(f"ollama call failed: {exc}") from exc
        answer = (data.get("response") or "").strip()
        if not answer:
            raise BackendError("ollama returned empty answer")
        return answer


class BackendChain:
    """Try backends in order, return the first success.

    Records (backend_name, error) for every failed attempt so callers
    can surface "who actually answered" / "why did we fall through" in
    /status or logs instead of silently swallowing failures.
    """

    def __init__(self, backends: list[Backend]):
        if not backends:
            raise ValueError("BackendChain needs at least one backend")
        self.backends = backends

    @classmethod
    def from_order(cls, order: list[str], registry: dict[str, Backend]) -> "BackendChain":
        missing = [name for name in order if name not in registry]
        if missing:
            raise ValueError(f"unknown backend(s) in order: {missing}")
        return cls([registry[name] for name in order])

    def generate(self, prompt: str, timeout: int = 180) -> tuple[str, str, list[tuple[str, str]]]:
        """Returns (answer, backend_name_used, failures)."""
        failures: list[tuple[str, str]] = []
        for backend in self.backends:
            try:
                answer = backend.generate(prompt, timeout=timeout)
                return answer, backend.name, failures
            except Exception as exc:  # noqa: BLE001 - deliberately broad, we chain on any failure
                failures.append((backend.name, str(exc)))
        raise BackendError(f"all backends failed: {failures}")


def default_chain(repo_path: Path, order: list[str] | None = None) -> BackendChain:
    """Build a chain from env-configured order, defaulting to
    codex -> antigravity -> ollama (matches the design doc's target
    architecture). Reads the same env var names bot_a6.py already uses
    where they overlap, so wiring this in later doesn't require new config.
    """
    order = order or os.getenv("A6_LLM_BACKEND_ORDER", "codex,antigravity,ollama").split(",")
    order = [name.strip() for name in order if name.strip()]

    registry = {
        "codex": CodexBackend(
            repo_path=repo_path,
            codex_bin=os.getenv("A6_CODEX_BIN", "/Applications/Codex.app/Contents/Resources/codex"),
            model=os.getenv("A6_CODEX_MODEL", ""),
        ),
        "antigravity": AntigravityBackend(
            agy_bin=os.getenv("A6_AGY_BIN", "/opt/homebrew/bin/agy"),
            model=os.getenv("A6_AGY_MODEL", ""),
        ),
        "ollama": OllamaBackend(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            model=os.getenv("OLLAMA_MODEL_CHAT", "llama3.1:latest"),
        ),
    }
    return BackendChain.from_order(order, registry)
