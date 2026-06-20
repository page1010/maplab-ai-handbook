#!/usr/bin/env python3
"""Compute a file-backed B1-B4 Recursive Self-Improvement report.

This is an internal Investment OS maintenance loop. The numeric score is only
an instrument panel; RSI means Recursive Self-Improvement. The script does not
inspect secrets, broker state, or trading data. It reads local runtime receipts
and MAPLAB review bundles, then writes a JSON and Markdown report.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TAIPEI = ZoneInfo("Asia/Taipei")
DEFAULT_RUNTIME_ROOT = Path("/Users/pagemacmini/.local/share/investmentos-telegram-operator")
DEFAULT_SOURCE_ROOT = Path("/Users/pagemacmini/Documents/New project")


@dataclass
class BundleRecency:
    prefix: str
    path: str | None
    age_hours: float | None


def now_taipei() -> datetime:
    return datetime.now(TAIPEI)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).astimezone(TAIPEI)
    except ValueError:
        return None


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def read_jsonl_tail(path: Path, limit: int = 300) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-limit:]:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def age_hours(path: Path, now: datetime) -> float | None:
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, TAIPEI)
    return max(0.0, (now - mtime).total_seconds() / 3600)


def parse_nightwatch(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "alert_count": None,
        "red_lines": [],
    }
    if not path.exists():
        result["alert_count"] = 1
        result["red_lines"] = ["nightwatch latest report missing"]
        return result

    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\*\*警示\s+(\d+)\s+項\*\*", text)
    if match:
        result["alert_count"] = int(match.group(1))
    red_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- **") or "| 🔴 " in stripped or " | 🔴" in stripped:
            red_lines.append(stripped)
    result["red_lines"] = red_lines
    if result["alert_count"] is None:
        result["alert_count"] = len(red_lines)
    return result


def load_background_jobs(runtime_root: Path, source_root: Path) -> dict[str, Any]:
    candidates = [
        runtime_root / "reviews" / "background_jobs_state.json",
        source_root / "reviews" / "background_jobs_state.json",
    ]
    for path in candidates:
        state = read_json(path)
        if state:
            state["_path"] = str(path)
            return state
    return {"_path": str(candidates[0]), "jobs": {}}


def summarize_jobs(state: dict[str, Any]) -> dict[str, Any]:
    jobs = state.get("jobs")
    if not isinstance(jobs, dict):
        jobs = {}
    bad_statuses = {"failed", "timeout"}
    bad_jobs = []
    for job_id, row in jobs.items():
        if not isinstance(row, dict):
            continue
        if job_id.endswith("-smoke") or job_id in {"timeout-smoke"}:
            continue
        status = str(row.get("status", "")).lower()
        if status in bad_statuses:
            bad_jobs.append(
                {
                    "job_id": job_id,
                    "status": status,
                    "last_message": str(row.get("last_message", ""))[:240],
                }
            )
    return {
        "path": state.get("_path"),
        "updated_at_utc": state.get("updated_at_utc"),
        "job_count": len(jobs),
        "bad_jobs": bad_jobs,
    }


def summarize_shadow(path: Path, now: datetime) -> dict[str, Any]:
    rows = read_jsonl_tail(path)
    cutoff = now - timedelta(hours=24)
    recent = []
    concerns = []
    last_ts: str | None = None
    for row in rows:
        ts = parse_dt(str(row.get("ts", "")))
        if ts:
            last_ts = ts.isoformat()
        if ts and ts >= cutoff:
            recent.append(row)
            if str(row.get("verdict", "")).lower() in {"concern", "drift", "reviewer_error"}:
                concerns.append(row)
    return {
        "path": str(path),
        "exists": path.exists(),
        "last_ts": last_ts,
        "recent_count_24h": len(recent),
        "concern_count_24h": len(concerns),
        "latest_concern": concerns[-1] if concerns else None,
    }


def latest_bundle(repo_root: Path, prefix: str, now: datetime) -> BundleRecency:
    root = repo_root / "workbook" / "reviews"
    matches = [p for p in root.glob(f"{prefix}*") if p.is_dir()]
    if not matches:
        return BundleRecency(prefix=prefix, path=None, age_hours=None)
    latest = max(matches, key=lambda p: p.stat().st_mtime)
    return BundleRecency(prefix=prefix, path=str(latest.relative_to(repo_root)), age_hours=age_hours(latest, now))


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def score_band(score: int) -> str:
    if score >= 85:
        return "healthy"
    if score >= 70:
        return "working_but_leaking"
    if score >= 50:
        return "degraded"
    return "broken"


def find_previous_score(output_dir: Path) -> dict[str, Any] | None:
    reviews_root = output_dir.parent
    candidates = sorted(
        reviews_root.glob("JOB-B1-B4-RSI-*/b_role_recursive_self_improvement.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for candidate in candidates:
        if candidate.resolve() == (output_dir / "b_role_recursive_self_improvement.json").resolve():
            continue
        data = read_json(candidate)
        if data:
            data["_path"] = str(candidate)
            return data
    return None


def build_report(repo_root: Path, runtime_root: Path, source_root: Path, output_dir: Path) -> dict[str, Any]:
    now = now_taipei()
    nightwatch = parse_nightwatch(runtime_root / "reports" / "nightwatch" / "latest.md")
    jobs = summarize_jobs(load_background_jobs(runtime_root, source_root))
    shadow = summarize_shadow(runtime_root / "reports" / "shadow" / "local_model_findings.jsonl", now)

    bundle_prefixes = {
        "B1": "JOB-B1-BUILDER-",
        "B2": "JOB-B2-REVIEW-",
        "B3": "JOB-B3-ARCHIVE-",
        "B4": "JOB-B4-PATROL-",
    }
    bundles = {
        role: latest_bundle(repo_root, prefix, now).__dict__
        for role, prefix in bundle_prefixes.items()
    }

    penalties: list[dict[str, Any]] = []
    alert_count = int(nightwatch.get("alert_count") or 0)
    if alert_count:
        penalties.append({"reason": "nightwatch_red_alerts", "points": min(alert_count * 12, 36), "count": alert_count})
    bad_jobs = jobs["bad_jobs"]
    if bad_jobs:
        penalties.append({"reason": "failed_or_timeout_background_jobs", "points": min(len(bad_jobs) * 8, 32), "count": len(bad_jobs)})
    concern_count = int(shadow.get("concern_count_24h") or 0)
    if concern_count >= 4:
        penalties.append({"reason": "untriaged_shadow_concerns_24h", "points": 12, "count": concern_count})
    elif concern_count:
        penalties.append({"reason": "shadow_concerns_24h", "points": 6, "count": concern_count})
    for role in ("B2", "B3", "B4"):
        age = bundles[role]["age_hours"]
        if age is None or age > 24 * 7:
            penalties.append({"reason": f"{role.lower()}_receipt_stale_or_missing", "points": 8, "age_hours": age})

    total_penalty = sum(int(item["points"]) for item in penalties)
    overall = clamp_score(100 - total_penalty)

    role_scores = {
        "B1": clamp_score(100 - min(len(bad_jobs) * 10, 40)),
        "B2": clamp_score(100 - (24 if concern_count else 0) - (20 if (bundles["B2"]["age_hours"] is None or bundles["B2"]["age_hours"] > 24 * 7) else 0)),
        "B3": clamp_score(100 - (35 if (bundles["B3"]["age_hours"] is None or bundles["B3"]["age_hours"] > 24 * 7) else 0)),
        "B4": clamp_score(100 - min(alert_count * 15, 45) - (20 if (bundles["B4"]["age_hours"] is None or bundles["B4"]["age_hours"] > 24 * 7) else 0)),
    }

    previous = find_previous_score(output_dir)
    previous_score = previous.get("overall_score") if previous else None
    if isinstance(previous_score, int):
        delta = overall - previous_score
        trend = "stronger" if delta > 0 else "weaker" if delta < 0 else "flat"
    else:
        delta = None
        trend = "baseline"

    next_actions = [
        "B2: triage latest shadow concerns into accepted_issue / false_positive / needs_more_evidence.",
        "B1: repair the highest-impact failed background job before adding new automation.",
        "B3: archive this run with a resume prompt and write pitfalls only if the same miss repeats.",
        "B4: rerun the scorer after fixes; require score improvement or fewer red items before calling the loop stronger.",
    ]
    if bad_jobs:
        next_actions.insert(1, f"B1: start with `{bad_jobs[0]['job_id']}` because it is currently failed/timeout in background job state.")
    else:
        next_actions[1] = "B1: do not add new automation until B2/B4 classify the nightwatch and shadow-review red items."
    if nightwatch.get("red_lines"):
        next_actions.insert(0, "B4: treat nightwatch red lines as patrol inputs, not owner-facing conclusions.")

    return {
        "schema_version": "b-role-recursive-self-improvement-v0",
        "generated_at": now.isoformat(),
        "overall_score": overall,
        "band": score_band(overall),
        "trend": trend,
        "delta_vs_previous": delta,
        "previous_score": previous_score,
        "previous_report": previous.get("_path") if previous else None,
        "role_scores": role_scores,
        "evidence": {
            "nightwatch": nightwatch,
            "background_jobs": jobs,
            "shadow_review": shadow,
            "bundle_recency": bundles,
        },
        "penalties": penalties,
        "next_actions": next_actions,
        "boundaries": [
            "This is not a market signal.",
            "This does not place, modify, or recommend trades.",
            "Local model findings require B2 review before formal conclusions.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    role_rows = [
        f"| {role} | {score} |"
        for role, score in report["role_scores"].items()
    ]
    penalties = report["penalties"] or [{"reason": "none", "points": 0}]
    penalty_rows = [
        f"| {item.get('reason')} | {item.get('points')} | {item.get('count', item.get('age_hours', ''))} |"
        for item in penalties
    ]
    bad_jobs = report["evidence"]["background_jobs"]["bad_jobs"]
    bad_job_lines = [
        f"- `{row['job_id']}`: {row['status']} — {row['last_message']}"
        for row in bad_jobs
    ] or ["- None"]
    red_lines = report["evidence"]["nightwatch"]["red_lines"] or ["None"]
    actions = [f"- {item}" for item in report["next_actions"]]
    latest_concern = report["evidence"]["shadow_review"].get("latest_concern")
    concern_text = "None"
    if latest_concern:
        concern_text = f"{latest_concern.get('ts')} / {latest_concern.get('parent_job')} / {latest_concern.get('verdict')}: {latest_concern.get('evidence')}"

    return "\n".join(
        [
            "# B1-B4 Recursive Self-Improvement",
            "",
            f"- Generated: `{report['generated_at']}`",
            f"- Overall score: `{report['overall_score']}`",
            f"- Band: `{report['band']}`",
            f"- Trend: `{report['trend']}`",
            f"- Previous score: `{report['previous_score']}`",
            "",
            "> RSI here means Recursive Self-Improvement. The score is an instrument panel, not a market signal.",
            "",
            "## Role Scores",
            "",
            "| Role | Score |",
            "|------|-------|",
            *role_rows,
            "",
            "## Penalties",
            "",
            "| Reason | Points | Count/Age |",
            "|--------|--------|-----------|",
            *penalty_rows,
            "",
            "## Nightwatch Red Lines",
            "",
            *[f"- {line}" for line in red_lines],
            "",
            "## Failed Or Timeout Jobs",
            "",
            *bad_job_lines,
            "",
            "## Latest Shadow Concern",
            "",
            concern_text,
            "",
            "## Next Actions",
            "",
            *actions,
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute B1-B4 Recursive Self-Improvement")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir
    if output_dir is None:
        stamp = now_taipei().strftime("%Y%m%d")
        output_dir = repo_root / "workbook" / "reviews" / f"JOB-B1-B4-RSI-{stamp}"
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(repo_root, args.runtime_root, args.source_root, output_dir)
    json_path = output_dir / "b_role_recursive_self_improvement.json"
    md_path = output_dir / "b_role_recursive_self_improvement.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(f"overall_score={report['overall_score']} trend={report['trend']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
