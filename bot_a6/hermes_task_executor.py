#!/usr/bin/env python3
"""Governed local task executor for the Owner-only A6 Hermes gateway.

This module deliberately exposes a small capability allowlist.  It never accepts
shell text from Telegram, never reads secret files, and writes a durable task and
receipt for every accepted or rejected request.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TASK_ROOT = REPO_ROOT / "workbook" / "reviews" / "A6-HERMES-TASKS"
MAX_OUTPUT_CHARS = 12_000
DENY_PATTERN = re.compile(
    r"(下單|買入|賣出|轉帳|匯款|發布|publish|wordpress|"
    r"token|密鑰|secret|\.env|刪除|rm\s|sudo|券商|broker)",
    re.IGNORECASE,
)
SCHEDULE_MUTATION_PATTERN = re.compile(
    r"((修改|改動|重啟|重跑|啟動|停用|關閉|載入|卸載|刪除|modify|restart|rerun|start|stop|load|unload).{0,20}"
    r"(launchd|launchctl|排程|schedule|cron))|"
    r"(launchctl.{0,20}(bootstrap|bootout|kickstart|enable|disable))",
    re.IGNORECASE,
)
PYTHON = str(Path(sys.executable).resolve())


@dataclass(frozen=True)
class Action:
    name: str
    argv: tuple[str, ...]
    timeout: int
    description: str


ACTIONS = {
    "runtime-status": Action(
        "runtime-status",
        (PYTHON, str(REPO_ROOT / "bot_a6" / "hermes_capability_runtime.py"), "capabilities"),
        20,
        "讀取 A6 Hermes 當前能力、provider、記憶與 launchd 狀態",
    ),
    "signal-status": Action(
        "signal-status",
        (PYTHON, str(REPO_ROOT / "bot_a6" / "hermes_capability_runtime.py"), "signal-status"),
        20,
        "讀取 16:20 動能名單的 launchd 與最新報告實況",
    ),
    "repo-status": Action(
        "repo-status",
        ("git", "status", "--short"),
        20,
        "讀取 MAPLAB repo 的未提交變更摘要",
    ),
    "recent-commits": Action(
        "recent-commits",
        ("git", "log", "-8", "--oneline", "--decorate"),
        20,
        "讀取最近八筆 commit",
    ),
    "a6-self-test": Action(
        "a6-self-test",
        (
            str(REPO_ROOT / "bot" / "venv" / "bin" / "python3"),
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_hermes*.py",
            "-v",
        ),
        90,
        "執行 A6 Hermes 治理式 executor 自我測試",
    ),
}

ALIASES = {
    "runtime-status": (
        "runtime-status",
        "hermesruntime狀態",
        "hermes狀態",
        "gateway狀態",
        "a6狀態",
        "執行環境狀態",
    ),
    "signal-status": (
        "signal-status",
        "動能名單",
        "強股故事",
        "strong-stock-story",
        "16:20名單",
        "訊號狀態",
    ),
    "repo-status": ("repo-status", "git status", "repo狀態", "專案狀態", "未提交變更"),
    "recent-commits": ("recent-commits", "最近commit", "最近提交", "版本紀錄"),
    "a6-self-test": ("a6-self-test", "測試a6", "a6測試", "測試hermes", "自我測試"),
}


def classify(request: str) -> tuple[str | None, str | None]:
    normalized = re.sub(r"\s+", "", request).lower()
    if DENY_PATTERN.search(request) or SCHEDULE_MUTATION_PATTERN.search(request):
        return None, "涉及禁止或高風險能力，已 fail closed"
    for action_name, aliases in ALIASES.items():
        if any(re.sub(r"\s+", "", alias).lower() in normalized for alias in aliases):
            return action_name, None
    return None, "不在目前的安全動作白名單"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    path.chmod(0o600)


def execute(
    request: str,
    owner_user_id: int,
    *,
    chat_id: int | None = None,
    chat_type: str | None = None,
) -> dict:
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    task_id = f"A6H-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    task_dir = TASK_ROOT / task_id
    task_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    task_dir.chmod(0o700)
    action_name, rejection = classify(request)
    task = {
        "schema_version": 2,
        "task_id": task_id,
        "created_at": now,
        "request": request[:2000],
        "requester": {
            "channel": "telegram",
            "owner_user_id": owner_user_id,
            "chat_id": chat_id,
            "chat_type": chat_type,
        },
        "action": action_name,
        "policy": "fixed-argv-allowlist-v2",
    }
    _write_json(task_dir / "task.json", task)

    if rejection:
        receipt = {**task, "status": "rejected", "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "reason": rejection}
    else:
        action = ACTIONS[action_name]
        try:
            proc = subprocess.run(
                action.argv,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=action.timeout,
                check=False,
                env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin", "LANG": "zh_TW.UTF-8"},
            )
            output = ((proc.stdout or "") + (proc.stderr or ""))[:MAX_OUTPUT_CHARS]
            receipt = {
                **task,
                "status": "completed" if proc.returncode == 0 else "failed",
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "description": action.description,
                "returncode": proc.returncode,
                "output": output,
                "output_truncated": len((proc.stdout or "") + (proc.stderr or "")) > MAX_OUTPUT_CHARS,
            }
        except subprocess.TimeoutExpired:
            receipt = {**task, "status": "failed", "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "reason": f"worker timeout after {action.timeout}s"}
    _write_json(task_dir / "receipt.json", receipt)
    summary = [
        f"# {task_id}", "", f"- 狀態：`{receipt['status']}`", f"- 動作：`{action_name or 'none'}`",
        f"- 建立：`{now}`", f"- 收據：`{task_dir / 'receipt.json'}`",
    ]
    receipt_md = task_dir / "receipt.md"
    fd = os.open(receipt_md, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write("\n".join(summary) + "\n")
    receipt_md.chmod(0o600)
    receipt["receipt_path"] = str(task_dir / "receipt.json")
    return receipt


def telegram_summary(receipt: dict) -> str:
    status = receipt["status"]
    lines = [f"【hermes executor】{status}", f"任務：{receipt['task_id']}", f"動作：{receipt.get('action') or 'none'}"]
    if receipt.get("reason"):
        lines.append(f"原因：{receipt['reason']}")
    output = receipt.get("output", "").strip()
    if output:
        lines.extend(["結果：", output[:1800]])
    lines.append(f"receipt：{receipt['receipt_path']}")
    if status == "rejected":
        lines.append("可用：runtime-status／signal-status／repo-status／recent-commits／a6-self-test")
    return "\n".join(lines)
