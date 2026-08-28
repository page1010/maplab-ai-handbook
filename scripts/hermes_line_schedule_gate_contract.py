#!/usr/bin/env python3
"""Validate the Hermes LINE LaunchAgent's fail-closed supervisor route.

This checker is intentionally model-free.  It validates the two tracked plist
copies and, unless ``--repo-only`` is used, the installed LaunchAgent.  It does
not load LINE examples, start a worker, or mutate launchd.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import stat
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LABEL = "com.maplab.hermes-line-training"
CANONICAL_PLIST = ROOT / "config" / "launchd" / f"{LABEL}.plist"
MIRROR_PLIST = ROOT / "launchd" / f"{LABEL}.plist"
INSTALLED_PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
SUPERVISOR = ROOT / "scripts" / "hermes_line_training_supervisor.py"
RAW_LOOP = ROOT / "scripts" / "hermes_line_training_loop.py"
JOB_PATH = (
    ROOT
    / "workbook"
    / "reviews"
    / "MAPLAB-DURABLE-JOBS"
    / "MAPJOB-20260827-224251-d291ad"
    / "job.json"
)
DATA_ROOT = Path.home() / ".maplab" / "a6-hermes-training"

EXPECTED_ARGUMENTS = [
    "/usr/bin/python3",
    str(SUPERVISOR),
    "--job-path",
    str(JOB_PATH),
    "--data-root",
    str(DATA_ROOT),
    "--max-rounds",
    "1",
    "--max-seconds",
    "120",
]
EXPECTED_ENVIRONMENT = {
    "HERMES_LINE_DATA_ROOT": str(DATA_ROOT),
    "HERMES_LINE_PROVIDER": "local-only",
    "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
    "PYTHONUNBUFFERED": "1",
}
EXPECTED_KEYS = {
    "Label",
    "ProgramArguments",
    "WorkingDirectory",
    "EnvironmentVariables",
    "Umask",
    "StartCalendarInterval",
    "StandardOutPath",
    "StandardErrorPath",
}


class ScheduleGateError(RuntimeError):
    """The scheduled route does not satisfy the frozen contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _regular_file(path: Path, code: str) -> None:
    if path.is_symlink():
        raise ScheduleGateError(f"{code}_symlink")
    try:
        info = path.stat()
    except OSError as exc:
        raise ScheduleGateError(f"{code}_unavailable") from exc
    if not stat.S_ISREG(info.st_mode):
        raise ScheduleGateError(f"{code}_not_regular")


def load_plist(path: Path) -> dict[str, Any]:
    _regular_file(path, "plist")
    try:
        payload = plistlib.loads(path.read_bytes())
    except (OSError, plistlib.InvalidFileException) as exc:
        raise ScheduleGateError("plist_invalid") from exc
    if not isinstance(payload, dict):
        raise ScheduleGateError("plist_topology_invalid")
    return payload


def validate_payload(payload: dict[str, Any]) -> None:
    if set(payload) != EXPECTED_KEYS:
        raise ScheduleGateError("plist_keys_invalid")
    if payload.get("Label") != LABEL:
        raise ScheduleGateError("plist_label_invalid")
    arguments = payload.get("ProgramArguments")
    if arguments != EXPECTED_ARGUMENTS:
        raise ScheduleGateError("plist_arguments_invalid")
    if str(RAW_LOOP) in arguments or any("hermes_line_training_loop.py" in str(item) for item in arguments):
        raise ScheduleGateError("raw_loop_side_door_present")
    if arguments.count("--job-path") != 1 or arguments.count("--data-root") != 1:
        raise ScheduleGateError("supervisor_binding_invalid")
    if payload.get("WorkingDirectory") != str(ROOT):
        raise ScheduleGateError("working_directory_invalid")
    if payload.get("EnvironmentVariables") != EXPECTED_ENVIRONMENT:
        raise ScheduleGateError("environment_invalid")
    if type(payload.get("Umask")) is not int or payload["Umask"] != 0o77:
        raise ScheduleGateError("umask_invalid")
    if payload.get("StartCalendarInterval") != {"Hour": 2, "Minute": 20}:
        raise ScheduleGateError("schedule_invalid")
    if payload.get("StandardOutPath") != str(ROOT / "state" / "hermes_line_training_stdout.log"):
        raise ScheduleGateError("stdout_path_invalid")
    if payload.get("StandardErrorPath") != str(ROOT / "state" / "hermes_line_training_stderr.log"):
        raise ScheduleGateError("stderr_path_invalid")


def validate_contract(*, include_installed: bool = True) -> dict[str, Any]:
    _regular_file(SUPERVISOR, "supervisor")
    _regular_file(JOB_PATH, "job")
    for path in (CANONICAL_PLIST, MIRROR_PLIST):
        validate_payload(load_plist(path))
    if CANONICAL_PLIST.read_bytes() != MIRROR_PLIST.read_bytes():
        raise ScheduleGateError("tracked_plist_mirror_drift")

    paths = [CANONICAL_PLIST, MIRROR_PLIST]
    if include_installed:
        validate_payload(load_plist(INSTALLED_PLIST))
        if CANONICAL_PLIST.read_bytes() != INSTALLED_PLIST.read_bytes():
            raise ScheduleGateError("installed_plist_drift")
        paths.append(INSTALLED_PLIST)

    return {
        "schema_version": "maplab.hermes.line-schedule-gate-contract.v1",
        "label": LABEL,
        "validated_plist_route": "supervisor-only",
        "validated_plists_contain_raw_loop": False,
        "installed_plist_verified": include_installed,
        # This checker intentionally does not inspect launchd's live cache.
        # A deployment receipt must combine this with `launchctl print`.
        "live_launchd_verified": False,
        "job_path": str(JOB_PATH),
        "data_root": str(DATA_ROOT),
        "max_rounds": 1,
        "max_seconds": 120,
        "schedule": {"Hour": 2, "Minute": 20},
        "plist_sha256": {str(path): sha256_file(path) for path in paths},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-only",
        action="store_true",
        help="Validate the two tracked plist copies without reading the installed LaunchAgent.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = validate_contract(include_installed=not args.repo_only)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
