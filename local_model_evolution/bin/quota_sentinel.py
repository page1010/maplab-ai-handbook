#!/usr/bin/env python3
"""Read-only provider capability and quota-confidence probe.

The *.yml files are JSON-formatted YAML so this first version remains stdlib-only.
It never reads environment variables, credential files, or usage APIs. A successful
CLI health probe proves availability only; it never proves remaining quota.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROVIDERS = ROOT / "config" / "providers.yml"
DEFAULT_RESETS = ROOT / "config" / "reset_calendar.yml"
DEFAULT_OUTPUT = ROOT / "state" / "provider_status.json"


def load_yaml_compatible_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def probe_health(argv: list[str]) -> tuple[str, str]:
    binary = shutil.which(argv[0])
    if binary is None:
        return "missing", "binary_not_found"
    try:
        result = subprocess.run(
            [binary, *argv[1:]],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=12,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "unknown", "health_probe_timeout"
    return ("available", "health_probe_exit_0") if result.returncode == 0 else (
        "unknown",
        f"health_probe_exit_{result.returncode}",
    )


def provider_status(provider: dict[str, Any], reset: dict[str, Any]) -> dict[str, Any]:
    health = "not_probed"
    health_evidence = "probe_disabled"
    if provider.get("probe_enabled") and provider.get("health_probe"):
        health, health_evidence = probe_health(provider["health_probe"])

    kind = provider["kind"]
    local_runtime = kind == "local_runtime"
    usage_confidence = "verified" if local_runtime and health == "available" else "unknown"
    usage_source = "authenticated_cli_health" if local_runtime and health == "available" else "unknown"
    remaining_fraction = None
    teacher_jobs_allowed = False
    reason = (
        "local_runtime_has_no_provider_quota"
        if local_runtime
        else "remaining_quota_unknown_or_provider_blocked_by_policy"
    )

    return {
        "provider_id": provider["id"],
        "display_name": provider["display_name"],
        "kind": kind,
        "health": health,
        "health_evidence": health_evidence,
        "usage_source": usage_source,
        "usage_confidence": usage_confidence,
        "remaining_fraction": remaining_fraction,
        "reset_rule": reset.get("reset_rule", "unknown"),
        "reset_timezone": reset.get("reset_timezone", "unknown"),
        "reset_confidence": reset.get("confidence", "unknown"),
        "policy": provider["policy"],
        "teacher_jobs_allowed": teacher_jobs_allowed,
        "decision_reason": reason,
    }


def build_status(providers_path: Path, resets_path: Path) -> dict[str, Any]:
    providers = load_yaml_compatible_json(providers_path)
    resets = load_yaml_compatible_json(resets_path)
    reset_map = resets["providers"]
    statuses = [
        provider_status(provider, reset_map.get(provider["id"], {}))
        for provider in providers["providers"]
    ]
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(ZoneInfo("Asia/Taipei")).isoformat(timespec="seconds"),
        "mode": "dry_run",
        "safe_reserve_fraction": providers["safe_reserve_fraction"],
        "secrets_read": False,
        "usage_apis_called": False,
        "teacher_jobs_created": 0,
        "teacher_jobs_executed": 0,
        "global_teacher_job_decision": "blocked",
        "global_decision_reason": "all_nonlocal_remaining_quota_values_are_unknown",
        "providers": statuses,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", type=Path, default=DEFAULT_PROVIDERS)
    parser.add_argument("--resets", type=Path, default=DEFAULT_RESETS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true", help="Required safety acknowledgement")
    args = parser.parse_args()
    if not args.dry_run:
        parser.error("v0.1 only supports --dry-run")

    status = build_status(args.providers, args.resets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "mode": status["mode"],
        "providers": len(status["providers"]),
        "usage_apis_called": status["usage_apis_called"],
        "teacher_jobs_created": status["teacher_jobs_created"],
        "decision": status["global_teacher_job_decision"],
        "output": str(args.output),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
