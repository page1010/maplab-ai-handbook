#!/usr/bin/env python3
"""Create Hermes/Codex reaction packets from MAPLAB patrol output.

The daily Telegram patrol is reliable collection and delivery. This bridge adds
the missing reaction layer: who owns the issue, what can move without Owner,
what should be written back to task cards, and what Codex/A1/B1 should do next.

Default behavior is deterministic. It does not call an LLM, does not read .env,
and does not modify external systems.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


TAIPEI = ZoneInfo("Asia/Taipei") if ZoneInfo else timezone.utc
SCHEMA = "maplab.hermes_patrol_reaction.v1"
LEDGER_SCHEMA = "maplab.learning_loop.reaction_ledger.v1"


@dataclass
class TaskCard:
    task_id: str
    agent: str
    path: str
    status: str
    last_activity: str
    next_step: str
    blocker: str
    days_ago: int | None
    bucket: str

    @property
    def stale(self) -> bool:
        return self.days_ago is not None and self.days_ago >= 2

    @property
    def owner_related(self) -> bool:
        text = f"{self.status} {self.next_step} {self.blocker}".lower()
        return "owner" in text or "批准" in text or "授權" in text

    def compact(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent": self.agent,
            "path": self.path,
            "status": self.status,
            "last_activity": self.last_activity,
            "days_ago": self.days_ago,
            "bucket": self.bucket,
            "owner_related": self.owner_related,
            "next_step": self.next_step[:320],
            "blocker": self.blocker[:320],
        }


def repo_default() -> Path:
    return Path(__file__).resolve().parents[1]


def now_taipei() -> datetime:
    return datetime.now(TAIPEI)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def repo_relative(path: Path, repo: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def clean_text(value: str) -> str:
    return value.encode("utf-8", errors="replace").decode("utf-8", errors="replace")


def clean_json(value: Any) -> Any:
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        return [clean_json(item) for item in value]
    if isinstance(value, dict):
        return {clean_text(str(key)): clean_json(item) for key, item in value.items()}
    return value


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=TAIPEI)
    return parsed


def task_field(text: str, name: str, default: str = "") -> str:
    pattern = re.compile(rf"^\s*-\s+\*\*{re.escape(name)}\*\*:\s*(.*)$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else default


def infer_agent(task_id: str) -> str:
    match = re.search(r"(IOS-[A-Z]+|A\d+|B\d+|WIN)", task_id)
    return match.group(1) if match else "??"


def parse_days(last_activity: str, now: datetime) -> int | None:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", last_activity or "")
    if not match:
        return None
    then = datetime.strptime(match.group(1), "%Y-%m-%d").replace(tzinfo=TAIPEI)
    return max(0, (now - then).days)


def classify_status(status: str) -> str:
    if "✅" in status or ("完成" in status and "未完成" not in status):
        return "done"
    if "⏸" in status or "阻塞" in status:
        return "blocked"
    if "💤" in status or "暫停" in status:
        return "paused"
    if "🔲" in status or "待開始" in status:
        return "not_started"
    if "🔄" in status or "進行中" in status:
        return "active"
    return "unmarked"


def load_tasks(repo: Path, now: datetime) -> list[TaskCard]:
    tasks: list[TaskCard] = []
    for path in sorted((repo / "handoff" / "tasks").glob("T-*.md")):
        text = read_text(path)
        task_id = path.stem
        status = task_field(text, "狀態", "未標記")
        last_activity = task_field(text, "最後活動", "未知")
        tasks.append(
            TaskCard(
                task_id=task_id,
                agent=infer_agent(task_id),
                path=str(path.relative_to(repo)),
                status=status,
                last_activity=last_activity,
                next_step=task_field(text, "接續點", ""),
                blocker=task_field(text, "阻塞", "無"),
                days_ago=parse_days(last_activity, now),
                bucket=classify_status(status),
            )
        )
    return tasks


def run_probe(cmd: list[str], timeout: int = 12) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=timeout)
        return proc.returncode, proc.stdout + proc.stderr
    except Exception as exc:
        return 127, str(exc)


def parse_hermes_status(text: str) -> dict[str, str | None]:
    def line_value(label: str) -> str | None:
        match = re.search(rf"^\s*{re.escape(label)}:\s*(.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else None

    def containing(word: str) -> str | None:
        for line in text.splitlines():
            if word in line:
                return line.strip()
        return None

    return {
        "model": line_value("Model"),
        "provider": line_value("Provider"),
        "gateway_status": line_value("Status"),
        "gateway_manager": line_value("Manager"),
        "gateway_service": line_value("Service"),
        "telegram": containing("Telegram"),
        "scheduled_jobs": containing("Jobs:"),
    }


def hermes_status() -> dict[str, Any]:
    hermes = shutil.which("hermes")
    status: dict[str, Any] = {"cli_path": hermes, "checked": False, "returncode": None, "status": {}}
    if not hermes:
        return status
    code, output = run_probe([hermes, "status", "--all"])
    status["checked"] = True
    status["returncode"] = code
    status["status"] = parse_hermes_status(output)
    return status


def chrome_extension_status(repo: Path) -> dict[str, Any]:
    popup_html = read_text(repo / "chrome-extension" / "popup.html")
    popup_js = read_text(repo / "chrome-extension" / "popup.js")
    index_path = repo / "chrome-extension" / "task-modules" / "index.json"
    modules: list[dict[str, Any]] = []
    try:
        modules = json.loads(read_text(index_path)).get("modules", [])
    except Exception:
        modules = []
    hermes_modules = [
        m.get("role_id")
        for m in modules
        if "hermes" in [str(x).lower() for x in (m.get("runtime_targets") or [])]
    ]
    return {
        "runtime_selector_has_hermes": 'value="hermes"' in popup_html,
        "prompt_builder_has_hermes_instruction": "hermes:" in popup_js,
        "module_count": len(modules),
        "modules_with_hermes_target": hermes_modules,
        "module_gap": len(hermes_modules) == 0,
    }


def counts(tasks: list[TaskCard]) -> dict[str, int]:
    data = {
        "total": len(tasks),
        "blocked": 0,
        "active": 0,
        "stale_active": 0,
        "unmarked": 0,
        "paused_or_not_started": 0,
        "done": 0,
        "owner_related": 0,
    }
    for task in tasks:
        if task.bucket == "blocked":
            data["blocked"] += 1
        elif task.bucket == "active":
            data["active"] += 1
            if task.stale:
                data["stale_active"] += 1
        elif task.bucket == "unmarked":
            data["unmarked"] += 1
        elif task.bucket in {"paused", "not_started"}:
            data["paused_or_not_started"] += 1
        elif task.bucket == "done":
            data["done"] += 1
        if task.owner_related:
            data["owner_related"] += 1
    return data


def top(tasks: list[TaskCard], bucket: str, limit: int = 8) -> list[dict[str, Any]]:
    selected = [task for task in tasks if task.bucket == bucket]
    selected.sort(key=lambda t: (t.days_ago is None, -(t.days_ago or 0), t.task_id))
    return [task.compact() for task in selected[:limit]]


def token_signals(raw_text: str) -> dict[str, bool]:
    lower = raw_text.lower()
    invalid_grant = "invalid_grant" in lower
    expired = "expired" in lower or "token refresh failed" in lower
    return {
        "google_oauth_invalid_grant_seen": invalid_grant,
        "google_oauth_expired_seen": expired,
        "owner_reauth_needed": invalid_grant or expired,
    }


def codex_prompt_for(card_id: str, role: str, why: str, next_step: str) -> str:
    return (
        f"你是 MAPLAB {role}，運行在 Codex。\n"
        "先讀 CURRENT_STATUS.md、pitfalls.md、workbook/hermes/patrol/latest.json，"
        "再讀相關 Task Card。\n\n"
        f"觸發 reaction: {card_id}\n"
        f"原因: {why}\n"
        f"本輪目標: {next_step}\n\n"
        "輸出：更新相對角色下一步或產 task packet；若需要 Owner，必須是 5 分鐘內可完成的具體行動。"
    )


def reaction_cards(tasks: list[TaskCard], raw_text: str, extension: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    signals = token_signals(raw_text)
    if signals["owner_reauth_needed"]:
        cards.append(
            {
                "id": "google-oauth-reauth-card",
                "severity": "high",
                "owner_role": "A1",
                "target_task_card": "handoff/tasks/T-A1-SYNC-GUARD-001.md",
                "why": "Google OAuth token refresh is invalid_grant; repeating the patrol text will not solve it.",
                "next_step": "Prepare an Owner 5-minute OAuth reauthorization card, then rerun Sheets/Drive smoke.",
                "next_step_patch_hint": "把阻塞改成精準 OAuth reauth action，不要每日原文轉發 invalid_grant。",
                "codex_followup_prompt": codex_prompt_for(
                    "google-oauth-reauth-card",
                    "A1",
                    "patrol saw invalid_grant in Google OAuth",
                    "produce the reauth card and verification command",
                ),
            }
        )

    long_blocked = [t for t in tasks if t.bucket == "blocked" and t.days_ago is not None and t.days_ago >= 14]
    if long_blocked:
        names = ", ".join(t.task_id for t in long_blocked[:6])
        cards.append(
            {
                "id": "long-blocked-three-layer-review",
                "severity": "high" if len(long_blocked) >= 3 else "medium",
                "owner_role": "A0/A1",
                "target_task_card": "handoff/tasks/",
                "why": f"{len(long_blocked)} blocked tasks are older than 14 days: {names}.",
                "next_step": "Run three-layer blocker review and split false blockers into direct-do / delegated / true Owner action.",
                "next_step_patch_hint": "每張卡改寫接續點：誰負責、下一個命令、何時才需要 Owner。",
                "codex_followup_prompt": codex_prompt_for(
                    "long-blocked-three-layer-review",
                    "A0/A1",
                    f"{len(long_blocked)} blockers are stale",
                    "patch the top stale task cards with concrete next steps",
                ),
            }
        )

    stale_active = [t for t in tasks if t.bucket == "active" and t.days_ago is not None and t.days_ago >= 7]
    if stale_active:
        names = ", ".join(t.task_id for t in stale_active[:6])
        cards.append(
            {
                "id": "stale-active-dispatch",
                "severity": "medium",
                "owner_role": "A0/B1",
                "target_task_card": "handoff/tasks/",
                "why": f"{len(stale_active)} active tasks have no activity for 7+ days: {names}.",
                "next_step": "Turn each stale active task into continue / pause / refactor / close with an exact next owner.",
                "next_step_patch_hint": "不要保留模糊進行中；寫入下一個可執行動作或暫停理由。",
                "codex_followup_prompt": codex_prompt_for(
                    "stale-active-dispatch",
                    "B1/A1",
                    "active tasks are stale",
                    "confirm progress and push the next direct task downward",
                ),
            }
        )

    unmarked = [t for t in tasks if t.bucket == "unmarked"]
    if unmarked:
        cards.append(
            {
                "id": "task-card-status-normalization",
                "severity": "medium",
                "owner_role": "A1",
                "target_task_card": "handoff/tasks/",
                "why": f"{len(unmarked)} task cards have unmarked status, so patrol cannot decide reliably.",
                "next_step": "Normalize 接續狀態 blocks from existing task-card evidence.",
                "next_step_patch_hint": "補狀態、最後活動、接續點、阻塞；缺資料標缺資料，不要腦補。",
                "codex_followup_prompt": codex_prompt_for(
                    "task-card-status-normalization",
                    "A1",
                    "task card metadata is unmarked",
                    "normalize status blocks for the unmarked cards",
                ),
            }
        )

    if extension.get("module_gap"):
        cards.append(
            {
                "id": "chrome-extension-hermes-target-sync",
                "severity": "medium",
                "owner_role": "A1",
                "target_task_card": "handoff/tasks/T-A1-EXT-001-dynamic-role-modules.md",
                "why": "Popup has Hermes runtime selector, but role module JSONs do not list Hermes as a formal target.",
                "next_step": "Update the task-module generator/config so role handoffs can route to Hermes with repo + packet context.",
                "next_step_patch_hint": "讓 runtime target hermes 寫入 generated role modules，而不只是 popup 下拉選項。",
                "codex_followup_prompt": codex_prompt_for(
                    "chrome-extension-hermes-target-sync",
                    "A1",
                    "Chrome Extension Hermes route is only partial",
                    "patch generator/config and rebuild task modules",
                ),
            }
        )

    if not cards:
        cards.append(
            {
                "id": "no-critical-reaction",
                "severity": "info",
                "owner_role": "A1",
                "target_task_card": "",
                "why": "No deterministic critical reaction was detected.",
                "next_step": "Archive the packet and keep monitoring.",
                "next_step_patch_hint": "No task-card change needed.",
                "codex_followup_prompt": "",
            }
        )
    return cards


def default_ledger_decision(card: dict[str, Any]) -> str:
    card_id = str(card.get("id", ""))
    if card_id == "no-critical-reaction":
        return "closed"
    if "oauth" in card_id or "reauth" in card_id:
        return "owner_5min"
    if "status-normalization" in card_id or "target-sync" in card_id:
        return "direct_do"
    if "memory" in card_id:
        return "memory_candidate"
    return "delegated"


def default_due_at(generated_at: str, decision: str, severity: str) -> str:
    generated = parse_iso_datetime(generated_at) or now_taipei()
    if decision == "closed":
        return generated.isoformat(timespec="seconds")
    days = 1 if decision == "owner_5min" or severity == "high" else 7
    return (generated + timedelta(days=days)).isoformat(timespec="seconds")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def reaction_key_for(card: dict[str, Any]) -> str:
    return "|".join([str(card.get("id", "")), str(card.get("target_task_card", ""))])


def reaction_key_for_entry(entry: dict[str, Any]) -> str:
    if entry.get("reaction_key"):
        return str(entry.get("reaction_key"))
    return "|".join([str(entry.get("reaction_id", "")), str(entry.get("target_task_card", ""))])


def ledger_entry(packet: dict[str, Any], card: dict[str, Any], repo: Path) -> dict[str, Any]:
    decision = default_ledger_decision(card)
    status = "closed" if decision == "closed" else "open"
    generated_at = str(packet["generated_at"])
    reaction_key = reaction_key_for(card)
    ledger_key = "|".join(
        [
            generated_at,
            str(card.get("id", "")),
            str(card.get("target_task_card", "")),
        ]
    )
    entry = {
        "schema_version": LEDGER_SCHEMA,
        "ledger_key": ledger_key,
        "reaction_key": reaction_key,
        "reaction_id": card.get("id", ""),
        "generated_at": generated_at,
        "owner_role": card.get("owner_role", ""),
        "target_task_card": card.get("target_task_card", ""),
        "severity": card.get("severity", ""),
        "decision": decision,
        "next_action": card.get("next_step", ""),
        "assigned_to": card.get("owner_role", ""),
        "due_at": default_due_at(generated_at, decision, str(card.get("severity", ""))),
        "evidence_path": "workbook/hermes/patrol/latest.json",
        "status": status,
        "closed_at": generated_at if status == "closed" else "",
        "why": card.get("why", ""),
        "next_step_patch_hint": card.get("next_step_patch_hint", ""),
        "source": {
            "repo": str(repo),
            "packet_schema": packet.get("schema_version", ""),
            "packet_generated_at": generated_at,
        },
    }
    return clean_json(entry)


def ledger_summary(entries: list[dict[str, Any]], added: int, now: datetime, ledger_path: Path, repo: Path) -> str:
    by_status = Counter(str(e.get("status", "")) for e in entries)
    by_decision = Counter(str(e.get("decision", "")) for e in entries)
    stale_open: list[dict[str, Any]] = []
    overdue_open: list[dict[str, Any]] = []
    for entry in entries:
        if entry.get("status") != "open":
            continue
        generated = parse_iso_datetime(str(entry.get("generated_at", "")))
        due_at = parse_iso_datetime(str(entry.get("due_at", "")))
        if generated and generated <= now - timedelta(days=7):
            stale_open.append(entry)
        if due_at and due_at < now:
            overdue_open.append(entry)

    lines = [
        "# Learning Loop Reaction Ledger Summary",
        "",
        f"- generated_at: `{now.isoformat(timespec='seconds')}`",
        f"- ledger: `{repo_relative(ledger_path, repo)}`",
        f"- entries_added_this_run: `{added}`",
        f"- total_entries: `{len(entries)}`",
        f"- open: `{by_status.get('open', 0)}`",
        f"- closed: `{by_status.get('closed', 0)}`",
        f"- stale_open_7d: `{len(stale_open)}`",
        f"- overdue_open: `{len(overdue_open)}`",
        "",
        "## Decisions",
        "",
    ]
    for decision, count in sorted(by_decision.items()):
        lines.append(f"- {decision or 'unknown'}: `{count}`")
    lines.extend(["", "## Open Reactions", ""])
    open_entries = [e for e in entries if e.get("status") == "open"]
    for entry in open_entries[-20:]:
        lines.append(
            "- "
            f"{entry.get('reaction_id')} | "
            f"decision={entry.get('decision')} | "
            f"assigned_to={entry.get('assigned_to')} | "
            f"due_at={entry.get('due_at')} | "
            f"target={entry.get('target_task_card')}"
        )
    if not open_entries:
        lines.append("- none")
    lines.extend(["", "## Overdue Open Reactions", ""])
    for entry in overdue_open[-20:]:
        lines.append(
            "- "
            f"{entry.get('reaction_id')} | "
            f"assigned_to={entry.get('assigned_to')} | "
            f"due_at={entry.get('due_at')} | "
            f"target={entry.get('target_task_card')}"
        )
    if not overdue_open:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def write_reaction_ledger(repo: Path, packet: dict[str, Any]) -> dict[str, Any]:
    out = repo / "workbook" / "learning_loop"
    out.mkdir(parents=True, exist_ok=True)
    ledger_path = out / "reaction_ledger.jsonl"
    summary_path = out / "reaction_ledger_summary.md"
    existing = load_jsonl(ledger_path)
    seen = {str(entry.get("ledger_key", "")) for entry in existing}
    open_reactions = {reaction_key_for_entry(entry) for entry in existing if entry.get("status") == "open"}
    new_entries = []
    for card in packet.get("reaction_cards", []):
        entry = ledger_entry(packet, card, repo)
        if entry["ledger_key"] in seen or entry["reaction_key"] in open_reactions:
            continue
        new_entries.append(entry)
        seen.add(entry["ledger_key"])
        if entry.get("status") == "open":
            open_reactions.add(str(entry["reaction_key"]))
    if new_entries:
        with ledger_path.open("a", encoding="utf-8") as handle:
            for entry in new_entries:
                handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    entries = existing + new_entries
    now = now_taipei()
    summary_path.write_text(ledger_summary(entries, len(new_entries), now, ledger_path, repo), encoding="utf-8")
    open_count = sum(1 for entry in entries if entry.get("status") == "open")
    return {
        "schema_version": LEDGER_SCHEMA,
        "ledger_path": repo_relative(ledger_path, repo),
        "summary_path": repo_relative(summary_path, repo),
        "entries_added": len(new_entries),
        "total_entries": len(entries),
        "open_entries": open_count,
    }


def build_packet(repo: Path, raw_text: str) -> dict[str, Any]:
    now = now_taipei()
    tasks = load_tasks(repo, now)
    extension = chrome_extension_status(repo)
    cards = reaction_cards(tasks, raw_text, extension)
    return {
        "schema_version": SCHEMA,
        "generated_at": now.isoformat(timespec="seconds"),
        "repo": str(repo),
        "source": {
            "patrol_script": "scripts/patrol.sh",
            "scheduled_wrapper": "scripts/patrol-scheduled.sh",
            "launch_agent": "com.maplab.patrol",
            "telegram_is_surface_only": True,
        },
        "model_policy": {
            "patrol_hot_path_uses_claude": False,
            "patrol_hot_path_uses_local_model": False,
            "hermes_role": "cold-path reaction, memory candidate, role next-step packet",
            "codex_role": "periodically verify repo/project progress and push next actions downward",
        },
        "hermes": hermes_status(),
        "chrome_extension": extension,
        "counts": counts(tasks),
        "signals": token_signals(raw_text),
        "reaction_cards": cards,
        "buckets": {
            "blocked": top(tasks, "blocked"),
            "active": top(tasks, "active"),
            "unmarked": top(tasks, "unmarked"),
            "paused": top(tasks, "paused", 5),
            "not_started": top(tasks, "not_started", 5),
        },
        "memory_management": {
            "truth_sources": [
                "CURRENT_STATUS.md",
                "pitfalls.md",
                "handoff/tasks/T-*.md",
                "workbook/hermes/patrol/latest.json",
            ],
            "write_back_candidates": [
                "pitfalls.md when same patrol failure repeats 7+ days",
                "handoff/tasks/T-*.md when a role next step is stale/unmarked",
                "skills/experience-log.md when a reusable Hermes/Codex routing lesson appears",
            ],
        },
        "raw_patrol_excerpt": raw_text[-6000:] if raw_text else "",
    }


def render_md(packet: dict[str, Any]) -> str:
    lines = [
        "# Hermes Patrol Reaction Packet",
        "",
        f"- generated_at: `{packet['generated_at']}`",
        f"- schema: `{packet['schema_version']}`",
        f"- repo: `{packet['repo']}`",
        "",
        "## Operating Decision",
        "",
        "- Patrol delivery is not resolution.",
        "- Hermes/local layer owns reaction, role next-step packets, and memory candidates.",
        "- Codex/A1/B1 periodically verify repo/project progress and push concrete next steps downward.",
        "",
        "## Runtime",
        "",
    ]
    hs = packet["hermes"].get("status", {})
    lines.extend(
        [
            f"- hermes_cli: `{packet['hermes'].get('cli_path') or 'missing'}`",
            f"- model: `{hs.get('model') or 'unknown'}`",
            f"- provider: `{hs.get('provider') or 'unknown'}`",
            f"- gateway: `{hs.get('gateway_status') or 'unknown'}`",
            f"- telegram: `{hs.get('telegram') or 'unknown'}`",
            "",
            "## Counts",
            "",
        ]
    )
    for key, value in packet["counts"].items():
        lines.append(f"- {key}: `{value}`")
    ledger = packet.get("reaction_ledger", {})
    if ledger:
        lines.extend(
            [
                "",
                "## Reaction Ledger",
                "",
                f"- ledger: `{ledger.get('ledger_path')}`",
                f"- summary: `{ledger.get('summary_path')}`",
                f"- entries_added: `{ledger.get('entries_added')}`",
                f"- open_entries: `{ledger.get('open_entries')}`",
            ]
        )
    lines.extend(["", "## Reaction Cards", ""])
    for card in packet["reaction_cards"]:
        lines.extend(
            [
                f"### {card['id']} [{card['severity']}]",
                "",
                f"- owner_role: `{card['owner_role']}`",
                f"- target_task_card: `{card['target_task_card']}`",
                f"- why: {card['why']}",
                f"- next_step: {card['next_step']}",
                f"- patch_hint: {card['next_step_patch_hint']}",
                "",
                "Codex follow-up prompt:",
                "",
                "```text",
                card.get("codex_followup_prompt", ""),
                "```",
                "",
            ]
        )
    lines.extend(["## Raw Patrol Excerpt", "", "```text", packet.get("raw_patrol_excerpt", ""), "```", ""])
    return "\n".join(lines)


def render_prompt(packet: dict[str, Any]) -> str:
    cards = json.dumps(packet["reaction_cards"], ensure_ascii=False, indent=2)
    return f"""# MAPLAB Hermes Patrol Reaction Prompt

You are Hermes Patrol Reaction worker.

Read:
1. CURRENT_STATUS.md
2. pitfalls.md
3. workbook/hermes/patrol/latest.json
4. only the target Task Cards named by reaction cards

Mission:
- Convert repeated patrol findings into role-owned next steps.
- Write guidance for A1/B1/Codex before asking Owner.
- Use three-layer blocker review: other agent, current agent, true Owner action.
- Do not read or print secrets.
- Do not modify external systems.

Deterministic reaction candidates:

```json
{cards}
```

Output exactly:
1. verified facts
2. issues that are repeating or stale
3. role owner for each issue
4. next direct action that does not require Owner
5. true Owner 5-minute action only if unavoidable
6. memory write-back candidate
"""


def render_telegram_card(packet: dict[str, Any]) -> str:
    lines = [
        "📋 Hermes Patrol Reaction",
        "",
        f"generated: {packet['generated_at']}",
        "hot path model: none",
        "reaction owner: Hermes/local layer -> Codex/A1/B1 follow-up",
        "",
        "Top actions:",
    ]
    for card in packet["reaction_cards"][:4]:
        lines.append(f"- [{card['severity']}] {card['id']} -> {card['owner_role']}: {card['next_step']}")
    ledger = packet.get("reaction_ledger", {})
    if ledger:
        lines.extend(["", f"Ledger: {ledger.get('summary_path')}"])
    lines.extend(["", "Panel: local-control-plane/hermes.html", "Packet: workbook/hermes/patrol/latest.md"])
    return "\n".join(lines)


def render_status_js(packet: dict[str, Any]) -> str:
    payload = json.dumps(packet, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return "window.HERMES_STATUS = " + payload + ";\n"


def write_outputs(repo: Path, packet: dict[str, Any]) -> dict[str, str]:
    out = repo / "workbook" / "hermes" / "patrol"
    hist = out / "history"
    panel = repo / "local-control-plane"
    out.mkdir(parents=True, exist_ok=True)
    hist.mkdir(parents=True, exist_ok=True)
    panel.mkdir(parents=True, exist_ok=True)
    stamp = now_taipei().strftime("%Y%m%d-%H%M%S")
    files = {
        "latest_json": out / "latest.json",
        "latest_md": out / "latest.md",
        "hermes_prompt": out / "hermes_prompt.md",
        "telegram_card": out / "telegram_decision_card.md",
        "history_json": hist / f"{stamp}.json",
        "panel_json": panel / "hermes_status.json",
        "panel_js": panel / "hermes_status.js",
    }
    packet["reaction_ledger"] = write_reaction_ledger(repo, packet)
    json_payload = json.dumps(packet, ensure_ascii=False, indent=2) + "\n"
    files["latest_json"].write_text(json_payload, encoding="utf-8")
    files["history_json"].write_text(json_payload, encoding="utf-8")
    files["panel_json"].write_text(json_payload, encoding="utf-8")
    files["latest_md"].write_text(render_md(packet), encoding="utf-8")
    files["hermes_prompt"].write_text(render_prompt(packet), encoding="utf-8")
    files["telegram_card"].write_text(render_telegram_card(packet), encoding="utf-8")
    files["panel_js"].write_text(render_status_js(packet), encoding="utf-8")
    return {name: str(path) for name, path in files.items()}


def read_input(args: argparse.Namespace) -> str:
    chunks: list[str] = []
    if args.raw_text_file:
        chunks.append(read_text(Path(args.raw_text_file)))
    if args.stdin:
        chunks.append(sys.stdin.read())
    if args.raw_text:
        chunks.append(args.raw_text)
    return clean_text("\n".join(chunk for chunk in chunks if chunk))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(repo_default()))
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--raw-text-file")
    parser.add_argument("--raw-text")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    repo = Path(args.repo).expanduser().resolve()
    packet = clean_json(build_packet(repo, read_input(args)))
    outputs = write_outputs(repo, packet)
    if not args.quiet:
        print(json.dumps({"ok": True, "outputs": outputs}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
