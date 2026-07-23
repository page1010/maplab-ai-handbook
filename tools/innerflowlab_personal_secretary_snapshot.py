#!/usr/bin/env python3
"""Build and optionally push a sanitized InnerFlowLab secretary snapshot."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROLE_DEFINITIONS = (
    ("A0", "總調度秘書"),
    ("A1", "系統總管"),
    ("A2", "搜尋流量"),
    ("A3", "社群廣告"),
    ("A4", "影像資產"),
    ("A5", "報價引擎"),
    ("A6", "業務快反應"),
    ("A7", "客服轉單"),
    ("A8", "影音產線"),
    ("B1", "IOS Builder"),
    ("B2", "IOS Reviewer"),
    ("B3", "IOS Archivist"),
    ("B4", "IOS System Patrol"),
    ("B5", "影子系統總管"),
    ("IOS-ALPHA", "阿爾法共振經理"),
    ("IOS-BLACKSWAN", "黑天鵝監控官"),
    ("IOS-CHIP", "籌碼經理"),
    ("IOS-EVIDENCE", "研究證據經理"),
    ("IOS-FAMILY", "家族基金經理"),
    ("IOS-FB", "FB / 社群情報經理"),
    ("IOS-HEDGE", "盤後對沖經理"),
    ("IOS-HYGIENE", "系統衛生官"),
    ("IOS-INVENTORY", "庫存審查經理"),
    ("IOS-KOL", "網紅雷達經理"),
    ("IOS-LEFT", "左側預期差經理"),
    ("IOS-MACRO", "總經大師"),
    ("IOS-MOMENTUM", "每日動能經理"),
    ("IOS-RIGHT", "右側交易經理"),
    ("IOS-SELL", "實單哨兵"),
    ("IOS-SIM", "模擬倉經理"),
    ("IOS-SURFACE", "介面契約守門員"),
)

IOS_JOBS = {
    "dashboard": "com.investmentos.dashboard",
    "telegram_operator": "com.investmentos.telegram-operator",
    "market_event_island": "com.investmentos.market-event-island",
    "black_swan_scanner": "com.investmentos.black-swan-scanner",
    "real_holdings_sentinel": "com.investmentos.real-holdings-sentinel",
    "self_healing_loop": "com.investmentos.self-healing-loop",
    "system_truth": "com.investmentos.system-truth-gen",
    "cross_project_mirror": "com.investmentos.cross-project-mirror",
    "live_position_watchdog": "com.investmentos.live-position-gpt-watchdog",
    "live_position_research": "com.investmentos.ai-hermes-live-position-research",
    "strong_stock_story": "com.investmentos.strong-stock-story-early",
}

MAPLAB_JOBS = {
    "A1": "com.maplab.patrol",
    "A6": "com.maplab.a6bot",
}


@dataclass(frozen=True)
class LaunchJob:
    pid: int | None
    last_exit: int | None

    @property
    def status(self) -> str:
        if self.pid:
            return "running"
        if self.last_exit == 0:
            return "standby"
        if self.last_exit is None:
            return "unknown"
        return "warning"


def parse_launchctl(output: str) -> dict[str, LaunchJob]:
    jobs: dict[str, LaunchJob] = {}
    for raw in output.splitlines():
        parts = raw.split("\t")
        if len(parts) != 3:
            continue
        pid_raw, exit_raw, label = parts
        pid = int(pid_raw) if pid_raw.isdigit() else None
        try:
            last_exit = int(exit_raw)
        except ValueError:
            last_exit = None
        jobs[label] = LaunchJob(pid=pid, last_exit=last_exit)
    return jobs


def read_launchctl() -> dict[str, LaunchJob]:
    proc = subprocess.run(
        ["launchctl", "list"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        return {}
    return parse_launchctl(proc.stdout)


def file_freshness(path: Path, now: datetime) -> str:
    if not path.exists():
        return "missing"
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_hours = max(0, int((now - modified).total_seconds() // 3600))
    if age_hours < 2:
        return f"{age_hours}h"
    if age_hours < 48:
        return f"{age_hours}h"
    return f"{age_hours // 24}d stale"


def role_evidence(maplab_repo: Path, role_id: str) -> tuple[str, str]:
    module = maplab_repo / "chrome-extension" / "task-modules" / f"{role_id}.json"
    recall = maplab_repo / "recalls" / f"{role_id}_recall.md"
    if role_id.startswith("IOS-") and not recall.exists():
        recall = maplab_repo / "recalls" / "IOS_strategy_role_recall.md"
    missing = []
    if not module.exists():
        missing.append("module")
    if not recall.exists():
        missing.append("recall")
    if missing:
        return "warning", "missing " + "/".join(missing)

    try:
        envelope = json.loads(module.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "warning", f"{module.relative_to(maplab_repo)} invalid JSON"

    stale_sources: list[str] = []
    for source in envelope.get("read_first", []):
        if not isinstance(source, dict):
            continue
        relative_path = source.get("path")
        expected_hash = source.get("source_sha256")
        if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
            continue
        source_path = maplab_repo / relative_path
        if not source_path.is_file():
            stale_sources.append(relative_path)
            continue
        actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            stale_sources.append(relative_path)

    if stale_sources:
        return (
            "standby",
            (
                f"召喚可用；上下文維護警示：{module.relative_to(maplab_repo)} has "
                f"{len(stale_sources)} stale source hash(es); rebuild required"
            ),
        )
    return "standby", f"{module.relative_to(maplab_repo)} + {recall.relative_to(maplab_repo)}"


def build_snapshot(
    maplab_repo: Path,
    ios_repo: Path,
    now: datetime | None = None,
    ios_runtime_root: Path | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    runtime_root = ios_runtime_root or ios_repo
    jobs = read_launchctl()
    roles: list[dict[str, str]] = []

    for role_id, name in ROLE_DEFINITIONS:
        status, evidence = role_evidence(maplab_repo, role_id)
        runtime_label = MAPLAB_JOBS.get(role_id)
        if runtime_label and runtime_label in jobs:
            runtime = jobs[runtime_label]
            if status != "warning":
                status = runtime.status
            result = f"runtime {runtime_label}: pid={runtime.pid or '-'}, exit={runtime.last_exit}"
        elif status == "warning":
            result = "召喚條件不完整；缺少必要模組或 recall，不能判定可用"
        else:
            result = "召喚模組與 recall 可用；屬按需角色，不以常駐 PID 判定"
        roles.append({
            "id": role_id,
            "name": name,
            "status": status,
            "result": result,
            "evidence": evidence,
        })

    modules: list[dict[str, str]] = []
    module_summaries = {
        "dashboard": "只讀決策、研究與風控顯示面",
        "telegram_operator": "Owner 手機訊息與固定命令路由",
        "market_event_island": "市場事件資料與排程",
        "black_swan_scanner": "黑天鵝條件掃描",
        "real_holdings_sentinel": "實單只讀風險哨兵",
        "self_healing_loop": "治理 finding 的掃描與覆查",
        "system_truth": "跨 repo 與 runtime 真相地圖",
        "cross_project_mirror": "MAPLAB 與 Investment OS 的狀態鏡像",
        "live_position_watchdog": "持倉研究工作的新鮮度守門",
        "live_position_research": "持倉研究判讀；持倉快照過期時必須失敗關閉",
        "strong_stock_story": "強勢股故事產物的 schema 與有效性檢查",
    }
    for module_id, label in IOS_JOBS.items():
        job = jobs.get(label, LaunchJob(pid=None, last_exit=None))
        modules.append({
            "id": module_id,
            "name": module_id.replace("_", " ").title(),
            "status": job.status,
            "summary": f"{module_summaries[module_id]}；pid={job.pid or '-'}，exit={job.last_exit}",
            "freshness": "launchctl live check",
        })

    modules.extend([
        {
            "id": "ios_alpha",
            "name": "IOS-ALPHA 阿爾法共振",
            "status": (
                "warning"
                if (
                    jobs.get(
                        "com.investmentos.convergence-engine",
                        LaunchJob(pid=None, last_exit=None),
                    ).status == "warning"
                    or "stale" in file_freshness(
                        ios_repo / "data" / "convergence_phone.md",
                        now,
                    )
                    or file_freshness(
                        ios_repo / "data" / "convergence_phone.md",
                        now,
                    ) == "missing"
                )
                else "ready"
            ),
            "summary": (
                "Reddit、RSS、Polymarket 與市場事件的跨源共振；"
                "WordPress 僅顯示去敏手機卡與新鮮度，不執行研究或交易。"
            ),
            "freshness": file_freshness(
                ios_repo / "data" / "convergence_phone.md",
                now,
            ),
        },
        {
            "id": "runtime_database",
            "name": "Investment OS Runtime Database",
            "status": "ready" if (runtime_root / "data" / "investment_os.sqlite3").exists() else "warning",
            "summary": "真正 runtime DB；網站只讀去敏摘要，不讀 raw SQLite",
            "freshness": file_freshness(runtime_root / "data" / "investment_os.sqlite3", now),
        },
        {
            "id": "exposure_ledger",
            "name": "Exposure Ledger",
            "status": "ready" if (runtime_root / "state" / "exposure_ledger.json").exists() else "warning",
            "summary": "曝險與死亡清單的去敏風險摘要",
            "freshness": file_freshness(runtime_root / "state" / "exposure_ledger.json", now),
        },
        {
            "id": "system_map",
            "name": "System Truth Map",
            "status": "ready" if (ios_repo / "SYSTEM_MAP.md").exists() else "warning",
            "summary": "runtime、repo drift 與治理 dispatch 摘要",
            "freshness": file_freshness(ios_repo / "SYSTEM_MAP.md", now),
        },
        {
            "id": "current_status",
            "name": "Investment OS Current Status",
            "status": "ready" if (ios_repo / "CURRENT_STATUS.md").exists() else "warning",
            "summary": "Investment OS 單一狀態入口",
            "freshness": file_freshness(ios_repo / "CURRENT_STATUS.md", now),
        },
    ])

    alerts: list[dict[str, str]] = []
    maplab_status = maplab_repo / "CURRENT_STATUS.md"
    if maplab_status.exists() and "<<<<<<<" in maplab_status.read_text(encoding="utf-8", errors="replace"):
        alerts.append({
            "severity": "error",
            "title": "MAPLAB 單一真相源存在 merge conflict",
            "detail": "先由 A1 收斂 CURRENT_STATUS.md，再重建角色模組或做高風險變更。",
        })
    stale_role_ids = [
        role["id"]
        for role in roles
        if "stale source hash" in role["evidence"]
    ]
    if stale_role_ids:
        alerts.append({
            "severity": "warning",
            "title": "角色召喚模組的來源線索已過期",
            "detail": (
                f"{', '.join(stale_role_ids)} 的 source hash 與目前 repo 不一致；"
                "角色可召喚不等於上下文最新，需重建 task modules 後再驗證。"
            ),
        })
    stale_health = runtime_root / "state" / "live_health.json"
    if stale_health.exists() and "stale" in file_freshness(stale_health, now):
        alerts.append({
            "severity": "warning",
            "title": "live_health 快照過期",
            "detail": f"repo 快照新鮮度為 {file_freshness(stale_health, now)}；此刻狀態以 launchctl 為準。",
        })
    for module in modules:
        if module["status"] == "warning":
            alerts.append({
                "severity": "warning",
                "title": f"{module['name']} 尚未綠燈",
                "detail": module["summary"],
            })

    return {
        "generated_at": now.astimezone().isoformat(timespec="seconds"),
        "roles": roles,
        "modules": modules,
        "alerts": alerts[:20],
    }


def push_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    base_url = os.environ.get("IFL_WP_BASE_URL", "").rstrip("/")
    username = os.environ.get("IFL_WP_USER", "")
    app_password = os.environ.get("IFL_WP_APP_PASSWORD", "")
    missing = [
        name
        for name, value in (
            ("IFL_WP_BASE_URL", base_url),
            ("IFL_WP_USER", username),
            ("IFL_WP_APP_PASSWORD", app_password),
        )
        if not value
    ]
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

    endpoint = base_url + "/wp-json/innerflowlab-secretary/v1/snapshot"
    body = json.dumps(snapshot, ensure_ascii=False).encode("utf-8")
    token = base64.b64encode(f"{username}:{app_password}".encode("utf-8")).decode("ascii")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "InnerFlowLab-Secretary-Exporter/0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"WordPress returned HTTP {exc.code}: {detail}") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maplab-repo", type=Path, required=True)
    parser.add_argument("--ios-repo", type=Path, required=True)
    parser.add_argument(
        "--ios-runtime-root",
        type=Path,
        default=Path("/Users/pagemacmini/.local/share/investmentos-telegram-operator"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--push", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    snapshot = build_snapshot(
        args.maplab_repo.resolve(),
        args.ios_repo.resolve(),
        ios_runtime_root=args.ios_runtime_root.resolve(),
    )
    rendered = json.dumps(snapshot, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.push:
        result = push_snapshot(snapshot)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
