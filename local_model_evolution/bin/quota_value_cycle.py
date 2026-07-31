#!/usr/bin/env python3
"""Quota Value Cycle controller.

This controller intentionally separates cheap, deterministic quota telemetry from
AI work.  It reads only Codex token_count/rate_limit events, never conversation
content, and writes runtime state outside the repositories by default.

Commands:
  snapshot  Read the latest trusted Codex rate-limit snapshot.
  plan      Gate the cycle and select one high-value, non-duplicated job.
  record    Record a completed/no-delta/blocked/failed job with file receipts.
  report    Produce the current or previous quota-cycle report.
  doctor    Validate config, evidence paths, and runtime directories.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "value_backlog.json"
DEFAULT_SESSION_ROOT = Path.home() / ".codex" / "sessions"
DEFAULT_STATE_DIR = Path.home() / ".codex" / "quota-value-cycle"
TAIPEI = timezone(timedelta(hours=8))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def recent_session_files(session_root: Path, days: int = 14) -> Iterable[Path]:
    if not session_root.exists():
        return []
    cutoff = utc_now().timestamp() - days * 86400
    return (
        path
        for path in session_root.rglob("*.jsonl")
        if path.is_file() and path.stat().st_mtime >= cutoff
    )


def collect_rate_limits(
    session_root: Path, limit_id: str = "codex", days: int = 14
) -> list[dict[str, Any]]:
    """Read rate-limit events only; never retain prompt or response content."""
    snapshots: list[dict[str, Any]] = []
    for path in recent_session_files(session_root, days):
        try:
            with path.open(encoding="utf-8") as handle:
                for line_no, line in enumerate(handle, start=1):
                    if '"rate_limits"' not in line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    payload = event.get("payload", {})
                    rate = payload.get("rate_limits", {})
                    primary = rate.get("primary") or {}
                    if rate.get("limit_id") != limit_id or "used_percent" not in primary:
                        continue
                    snapshots.append(
                        {
                            "observed_at": event.get("timestamp"),
                            "limit_id": limit_id,
                            "used_percent": float(primary["used_percent"]),
                            "window_minutes": primary.get("window_minutes"),
                            "reset_at": primary.get("resets_at"),
                            "source_file": str(path),
                            "source_line": line_no,
                        }
                    )
        except (OSError, UnicodeError):
            continue
    snapshots.sort(key=lambda row: row.get("observed_at") or "")
    return snapshots


def enrich_snapshot(row: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = now or utc_now()
    result = dict(row)
    used = float(result["used_percent"])
    result["remaining_percent"] = max(0.0, 100.0 - used)
    reset_at = result.get("reset_at")
    if reset_at:
        reset_dt = datetime.fromtimestamp(int(reset_at), timezone.utc)
        result["reset_at_utc"] = iso_time(reset_dt)
        result["reset_at_taipei"] = reset_dt.astimezone(TAIPEI).isoformat()
        result["hours_to_reset"] = round((reset_dt - now).total_seconds() / 3600, 3)
    else:
        result["reset_at_utc"] = None
        result["reset_at_taipei"] = None
        result["hours_to_reset"] = None
    result["status"] = "available"
    result["generated_at"] = iso_time(now)
    return result


def unknown_snapshot(limit_id: str, reason: str) -> dict[str, Any]:
    return {
        "status": "unknown",
        "limit_id": limit_id,
        "reason": reason,
        "generated_at": iso_time(utc_now()),
    }


def persist_snapshot(state_dir: Path, snapshot: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    latest_path = state_dir / "latest_snapshot.json"
    latest_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    history_path = state_dir / "quota_snapshots.jsonl"
    previous = read_jsonl(history_path)
    comparable = (
        snapshot.get("observed_at"),
        snapshot.get("used_percent"),
        snapshot.get("reset_at"),
        snapshot.get("status"),
    )
    if not previous or comparable != (
        previous[-1].get("observed_at"),
        previous[-1].get("used_percent"),
        previous[-1].get("reset_at"),
        previous[-1].get("status"),
    ):
        append_jsonl(history_path, snapshot)


def take_snapshot(
    session_root: Path, state_dir: Path, limit_id: str, days: int = 14
) -> dict[str, Any]:
    rows = collect_rate_limits(session_root, limit_id=limit_id, days=days)
    snapshot = (
        enrich_snapshot(rows[-1])
        if rows
        else unknown_snapshot(limit_id, "no trusted rate-limit telemetry found")
    )
    persist_snapshot(state_dir, snapshot)
    return snapshot


def last_job_states(ledger_path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    states: dict[tuple[str, str], dict[str, Any]] = {}
    for row in read_jsonl(ledger_path):
        job_id = row.get("job_id")
        revision = row.get("revision")
        if job_id and revision:
            states[(job_id, revision)] = row
    return states


def candidate_score(candidate: dict[str, Any]) -> int:
    return (
        int(candidate.get("owner_value", 0)) * 5
        + int(candidate.get("step_change", 0)) * 4
        + int(candidate.get("readiness", 0)) * 3
        - int(candidate.get("risk", 0)) * 2
    )


def evidence_exists(candidate: dict[str, Any]) -> bool:
    evidence = candidate.get("evidence", [])
    return bool(evidence) and all(Path(path).exists() for path in evidence)


def eligible_candidates(
    config: dict[str, Any],
    project: str,
    ledger_path: Path,
    now: datetime | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    now = now or utc_now()
    cooldown = timedelta(hours=float(config.get("cooldown_hours", 168)))
    previous = last_job_states(ledger_path)
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for raw in config.get("candidates", []):
        candidate = dict(raw)
        reasons: list[str] = []
        if project != "all" and candidate.get("project") != project:
            reasons.append("project_mismatch")
        if candidate.get("external_mutation"):
            reasons.append("external_mutation_requires_separate_authorization")
        if candidate.get("owner_decision_required"):
            reasons.append("owner_decision_required")
        if not evidence_exists(candidate):
            reasons.append("missing_evidence")
        previous_row = previous.get((candidate.get("id"), candidate.get("revision")))
        if previous_row:
            status = previous_row.get("status")
            if status == "done":
                reasons.append("revision_already_done")
            elif status in {"no_delta", "blocked"}:
                recorded_at = previous_row.get("recorded_at")
                if recorded_at and now - parse_time(recorded_at) < cooldown:
                    reasons.append("no_delta_or_blocked_cooldown")
        candidate["score"] = candidate_score(candidate)
        if reasons:
            rejected.append({"candidate": candidate, "reasons": reasons})
        else:
            eligible.append(candidate)
    eligible.sort(key=lambda row: (-row["score"], row["id"]))
    return eligible, rejected


def make_plan(
    config_path: Path,
    session_root: Path,
    state_dir: Path,
    project: str,
    limit_id: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or utc_now()
    config = load_json(config_path)
    snapshot_rows = collect_rate_limits(session_root, limit_id=limit_id)
    snapshot = (
        enrich_snapshot(snapshot_rows[-1], now=now)
        if snapshot_rows
        else unknown_snapshot(limit_id, "no trusted rate-limit telemetry found")
    )
    persist_snapshot(state_dir, snapshot)
    plan: dict[str, Any] = {
        "generated_at": iso_time(now),
        "project": project,
        "snapshot": snapshot,
        "gate": "blocked",
        "reason": None,
        "selected_job": None,
    }
    if snapshot.get("status") != "available":
        plan["reason"] = "quota_unknown"
    elif snapshot.get("hours_to_reset") is None:
        plan["reason"] = "reset_unknown"
    elif snapshot["remaining_percent"] <= float(config["safe_reserve_percent"]):
        plan["reason"] = "safe_reserve_held"
    elif not 0 <= float(snapshot["hours_to_reset"]) <= float(
        config["activation_window_hours"]
    ):
        plan["reason"] = "outside_activation_window"
    else:
        eligible, rejected = eligible_candidates(
            config, project, state_dir / "job_ledger.jsonl", now=now
        )
        plan["rejected_candidates"] = rejected
        if eligible:
            plan["gate"] = "ready"
            plan["reason"] = "high_value_job_selected"
            plan["selected_job"] = eligible[0]
            plan["ranked_candidates"] = eligible
        else:
            plan["gate"] = "no_action"
            plan["reason"] = "no_eligible_nonduplicate_job"
    plans_dir = state_dir / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.astimezone(TAIPEI).strftime("%Y%m%d-%H%M%S")
    plan_path = plans_dir / f"{stamp}-{project}-plan.json"
    plan["plan_path"] = str(plan_path)
    plan_path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if plan["selected_job"]:
        job = plan["selected_job"]
        card_path = plans_dir / f"{stamp}-{job['id']}.md"
        card = [
            f"# Quota Value Job — {job['title']}",
            "",
            f"- Job ID: `{job['id']}`",
            f"- Revision: `{job['revision']}`",
            f"- Project: `{job['project']}`",
            f"- Score: `{job['score']}`",
            f"- Plan: `{plan_path}`",
            f"- Quota remaining: `{snapshot['remaining_percent']}%`",
            f"- Reset: `{snapshot['reset_at_taipei']}`",
            "",
            "## Acceptance",
            "",
        ]
        card.extend(f"- {item}" for item in job.get("acceptance", []))
        card.extend(
            [
                "",
                "## Required closure",
                "",
                "- Produce a user-meaningful artifact, not another inventory-only checkpoint.",
                "- Run proportional tests.",
                "- Record output paths and scoped commit SHA.",
                "- If no material delta is possible, record `no_delta` and stop.",
                "",
            ]
        )
        card_path.write_text("\n".join(card), encoding="utf-8")
        plan["job_card_path"] = str(card_path)
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return plan


def record_job(args: argparse.Namespace) -> dict[str, Any]:
    state_dir = Path(args.state_dir).expanduser()
    plan = load_json(Path(args.plan))
    job = plan.get("selected_job")
    if not job:
        raise ValueError("plan has no selected_job")
    row = {
        "recorded_at": iso_time(utc_now()),
        "job_id": job["id"],
        "revision": job["revision"],
        "project": job["project"],
        "title": job["title"],
        "status": args.status,
        "summary": args.summary,
        "outputs": [str(Path(path).expanduser().resolve()) for path in args.output],
        "tests": args.test,
        "commit_sha": args.commit_sha,
        "plan_path": str(Path(args.plan).expanduser().resolve()),
        "quota_snapshot": plan.get("snapshot"),
    }
    if args.status == "done" and not row["outputs"]:
        raise ValueError("done requires at least one --output receipt")
    receipts_dir = state_dir / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_now().astimezone(TAIPEI).strftime("%Y%m%d-%H%M%S")
    receipt_path = receipts_dir / f"{stamp}-{job['id']}.md"
    row["receipt_path"] = str(receipt_path)
    lines = [
        f"# Quota Value Receipt — {job['title']}",
        "",
        f"- Status: `{args.status}`",
        f"- Summary: {args.summary}",
        f"- Project: `{job['project']}`",
        f"- Commit: `{args.commit_sha or 'none'}`",
        f"- Plan: `{row['plan_path']}`",
        "",
        "## Outputs",
        "",
    ]
    lines.extend(f"- `{path}`" for path in row["outputs"])
    lines.extend(["", "## Tests", ""])
    lines.extend(f"- {test}" for test in row["tests"])
    lines.extend(
        [
            "",
            "## Next action",
            "",
            "- Select the next highest-value non-duplicate job at the next eligible window.",
            "",
        ]
    )
    receipt_path.write_text("\n".join(lines), encoding="utf-8")
    append_jsonl(state_dir / "job_ledger.jsonl", row)
    return row


def cycle_bounds(
    snapshot: dict[str, Any], cycle: str
) -> tuple[datetime, datetime] | None:
    if snapshot.get("status") != "available":
        return None
    reset_at = snapshot.get("reset_at")
    window_minutes = snapshot.get("window_minutes")
    if not reset_at or not window_minutes:
        return None
    next_reset = datetime.fromtimestamp(int(reset_at), timezone.utc)
    window = timedelta(minutes=int(window_minutes))
    if cycle == "current":
        return next_reset - window, next_reset
    return next_reset - 2 * window, next_reset - window


def build_report(
    state_dir: Path,
    cycle: str,
    output: Path | None = None,
) -> tuple[dict[str, Any], Path]:
    snapshot_path = state_dir / "latest_snapshot.json"
    snapshot = (
        load_json(snapshot_path)
        if snapshot_path.exists()
        else unknown_snapshot("codex", "latest snapshot missing")
    )
    bounds = cycle_bounds(snapshot, cycle)
    ledger = read_jsonl(state_dir / "job_ledger.jsonl")
    selected: list[dict[str, Any]] = []
    if bounds:
        start, end = bounds
        selected = [
            row
            for row in ledger
            if row.get("recorded_at") and start <= parse_time(row["recorded_at"]) < end
        ]
    else:
        start = end = None
    counts: dict[str, int] = {}
    for row in selected:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    report = {
        "generated_at": iso_time(utc_now()),
        "cycle": cycle,
        "cycle_start": iso_time(start) if start else None,
        "cycle_end": iso_time(end) if end else None,
        "counts": counts,
        "jobs": selected,
        "latest_snapshot": snapshot,
    }
    if output is None:
        reports_dir = state_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        stamp = utc_now().astimezone(TAIPEI).strftime("%Y%m%d-%H%M%S")
        output = reports_dir / f"{stamp}-{cycle}-cycle-report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Quota Value Cycle Report — {cycle}",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Cycle start: `{report['cycle_start'] or 'unknown'}`",
        f"- Cycle end: `{report['cycle_end'] or 'unknown'}`",
        f"- Completed: `{counts.get('done', 0)}`",
        f"- No delta: `{counts.get('no_delta', 0)}`",
        f"- Blocked: `{counts.get('blocked', 0)}`",
        f"- Failed: `{counts.get('failed', 0)}`",
        "",
        "## User-helpful outcomes",
        "",
    ]
    if not selected:
        lines.append("- No recorded job in this cycle. This is a red control-plane result, not success.")
    for row in selected:
        lines.extend(
            [
                f"### {row['title']}",
                "",
                f"- Status: `{row['status']}`",
                f"- Summary: {row['summary']}",
                f"- Commit: `{row.get('commit_sha') or 'none'}`",
                f"- Receipt: `{row.get('receipt_path') or 'missing'}`",
            ]
        )
        lines.extend(f"- Output: `{path}`" for path in row.get("outputs", []))
        lines.extend(f"- Test: {test}" for test in row.get("tests", []))
        lines.append("")
    lines.extend(
        [
            "## Quota evidence",
            "",
            f"- Latest used: `{snapshot.get('used_percent', 'unknown')}%`",
            f"- Latest remaining: `{snapshot.get('remaining_percent', 'unknown')}%`",
            f"- Next reset: `{snapshot.get('reset_at_taipei', 'unknown')}`",
            f"- Source: `{snapshot.get('source_file', 'unknown')}:{snapshot.get('source_line', '')}`",
            "",
            "## Governance conclusion",
            "",
            "- A cycle is successful only when at least one `done` job has a file receipt and tests.",
            "- Repeated no-delta checkpoints are suppressed for seven days.",
            "- External writes, production mutation, messages, secrets, and broker/order actions remain outside this controller.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")
    return report, output


def doctor(config_path: Path, session_root: Path, state_dir: Path) -> dict[str, Any]:
    config = load_json(config_path)
    missing_evidence: dict[str, list[str]] = {}
    for candidate in config.get("candidates", []):
        missing = [path for path in candidate.get("evidence", []) if not Path(path).exists()]
        if missing:
            missing_evidence[candidate["id"]] = missing
    state_dir.mkdir(parents=True, exist_ok=True)
    return {
        "status": "pass" if session_root.exists() and not missing_evidence else "fail",
        "config": str(config_path),
        "session_root_exists": session_root.exists(),
        "state_dir": str(state_dir),
        "candidate_count": len(config.get("candidates", [])),
        "missing_evidence": missing_evidence,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--session-root", default=str(DEFAULT_SESSION_ROOT))
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR))
    parser.add_argument("--limit-id", default="codex")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot")
    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument(
        "--project", choices=["maplab", "investment-os", "all"], default="all"
    )
    record_parser = sub.add_parser("record")
    record_parser.add_argument("--plan", required=True)
    record_parser.add_argument(
        "--status", choices=["done", "no_delta", "blocked", "failed"], required=True
    )
    record_parser.add_argument("--summary", required=True)
    record_parser.add_argument("--output", action="append", default=[])
    record_parser.add_argument("--test", action="append", default=[])
    record_parser.add_argument("--commit-sha")
    report_parser = sub.add_parser("report")
    report_parser.add_argument("--cycle", choices=["current", "previous"], default="previous")
    report_parser.add_argument("--output")
    sub.add_parser("doctor")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config_path = Path(args.config).expanduser()
    session_root = Path(args.session_root).expanduser()
    state_dir = Path(args.state_dir).expanduser()
    try:
        if args.command == "snapshot":
            result = take_snapshot(session_root, state_dir, args.limit_id)
        elif args.command == "plan":
            result = make_plan(
                config_path, session_root, state_dir, args.project, args.limit_id
            )
        elif args.command == "record":
            result = record_job(args)
        elif args.command == "report":
            result, report_path = build_report(
                state_dir,
                args.cycle,
                Path(args.output).expanduser() if args.output else None,
            )
            result["report_path"] = str(report_path)
        else:
            result = doctor(config_path, session_root, state_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("status") != "fail" else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"status": "error", "error": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
