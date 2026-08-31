#!/usr/bin/env python3
"""Runtime-backed capability and status readback for the A6 Hermes gateway.

This module is intentionally standard-library only.  Every command it runs is
fixed in source; Telegram text is never interpolated into argv.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


CONTRACT_VERSION = 2
LOCAL_FALLBACK_ENABLED = False
RUNTIME_ROOT = Path.home() / ".local" / "share" / "maplab-a6-hermes"
STATE_PATH = RUNTIME_ROOT / "gateway_state.json"
HISTORY_PATH = RUNTIME_ROOT / "conversation.json"
QUARANTINE_ROOT = RUNTIME_ROOT / "quarantine"
INBOX_ROOT = RUNTIME_ROOT / "inbox"
INVESTMENT_ROOT = Path.home() / "investment-os"
SIGNAL_REPORT_ROOT = INVESTMENT_ROOT / "reports" / "limit_up_chip_story"
A6_LABEL = "com.maplab.a6bot"
SIGNAL_LABEL = "com.investmentos.strong-stock-story-early"
DEFAULT_ACTIONS = (
    "runtime-status",
    "signal-status",
    "repo-status",
    "recent-commits",
    "a6-self-test",
    "deerflow-status",
    "deerflow-public-research",
)


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)


def write_private_json(path: Path, payload: Any) -> None:
    """Atomically write JSON with owner-only permissions."""
    ensure_private_dir(path.parent)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp, path)
        path.chmod(0o600)
    finally:
        if tmp.exists():
            tmp.unlink()


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return default


def save_gateway_state(
    provider_chain: Iterable[str],
    *,
    last_provider: str | None = None,
    bot_username: str | None = None,
) -> dict[str, Any]:
    previous = read_json(STATE_PATH, {})
    payload = {
        "contract_version": CONTRACT_VERSION,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "configured_provider_chain": list(provider_chain),
        "local_fallback": "gemma4:latest",
        "local_fallback_enabled": LOCAL_FALLBACK_ENABLED,
        "last_provider": last_provider or previous.get("last_provider"),
        "last_provider_at": (
            time.strftime("%Y-%m-%dT%H:%M:%S%z")
            if last_provider
            else previous.get("last_provider_at")
        ),
        "bot_username": bot_username or previous.get("bot_username"),
        "history_path": str(HISTORY_PATH),
        "history_limit_messages": 12,
    }
    write_private_json(STATE_PATH, payload)
    return payload


def launchctl_snapshot(label: str) -> dict[str, Any]:
    target = f"gui/{os.getuid()}/{label}"
    try:
        proc = subprocess.run(
            ("/bin/launchctl", "print", target),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "C"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"label": label, "loaded": False, "error": type(exc).__name__}
    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return {"label": label, "loaded": False, "returncode": proc.returncode}

    def match(pattern: str) -> str | None:
        found = re.search(pattern, output, flags=re.MULTILINE)
        return found.group(1).strip() if found else None

    return {
        "label": label,
        "loaded": True,
        "state": match(r"^\s*state\s*=\s*(.+)$"),
        "pid": match(r"^\s*pid\s*=\s*(\d+)$"),
        "runs": match(r"^\s*runs\s*=\s*(\d+)$"),
        "last_exit_code": match(r"^\s*last exit code\s*=\s*(-?\d+)$"),
    }


def capability_snapshot(
    provider_chain: Iterable[str] | None = None,
    available_actions: Iterable[str] | None = None,
) -> dict[str, Any]:
    state = read_json(STATE_PATH, {})
    history = read_json(HISTORY_PATH, [])
    chain = list(provider_chain or state.get("configured_provider_chain") or [])
    return {
        "contract_version": CONTRACT_VERSION,
        "surface": "Owner-authorized A6 Telegram gateway",
        "launchd": launchctl_snapshot(A6_LABEL),
        "telegram": {
            "can_reply": True,
            "private_owner_chat": True,
            "owner_group_mentions": True,
            "photo_receive": True,
            "model_receives_bot_token": False,
        },
        "local_access": {
            "mode": "fixed-argv allowlist",
            "arbitrary_shell": False,
            "ssh": False,
            "actions": list(available_actions or DEFAULT_ACTIONS),
        },
        "providers": {
            "configured_chain": chain,
            "local_fallback": state.get("local_fallback", "gemma4:latest"),
            "local_fallback_enabled": LOCAL_FALLBACK_ENABLED,
            "last_provider": state.get("last_provider"),
            "last_provider_at": state.get("last_provider_at"),
        },
        "memory": {
            "persistent": True,
            "history_path": str(HISTORY_PATH),
            "history_limit_messages": 12,
            "current_messages": len(history) if isinstance(history, list) else 0,
            "durable_task_receipts": True,
        },
        "direct_connectors": {
            "google_sheets": False,
            "google_drive": False,
            "github_api": False,
        },
    }


def _launchd_text(snapshot: dict[str, Any]) -> str:
    if not snapshot.get("loaded"):
        return "未載入"
    parts = [str(snapshot.get("state") or "loaded")]
    if snapshot.get("pid"):
        parts.append(f"pid={snapshot['pid']}")
    if snapshot.get("last_exit_code") is not None:
        parts.append(f"last_exit={snapshot['last_exit_code']}")
    return ", ".join(parts)


def format_capabilities(
    provider_chain: Iterable[str] | None = None,
    available_actions: Iterable[str] | None = None,
) -> str:
    snap = capability_snapshot(provider_chain, available_actions)
    providers = snap["providers"]
    chain = " → ".join(providers["configured_chain"]) or "尚未載入"
    last = providers.get("last_provider") or "v2 尚無成功回覆樣本"
    fallback = (
        f"最後才用 {providers['local_fallback']}"
        if providers.get("local_fallback_enabled")
        else "本機 fallback 已停用；上游全失敗時會明確回報失敗"
    )
    actions = "／".join(snap["local_access"]["actions"])
    return (
        "【hermes】能力真相 v2（runtime readback）\n"
        f"入口：A6 Telegram gateway；{_launchd_text(snap['launchd'])}。Owner 私聊可用，群組請 @bot 或回覆 bot；照片會私密留檔並回 receipt。\n\n"
        "我能直接做：回覆 Telegram；把自然語句映射到固定白名單執行；讀取 A6 runtime、MAPLAB repo 狀態與指定 Investment OS 訊號狀態。"
        f"目前動作：{actions}。\n\n"
        "權限邊界：不是零存取，但沒有任意 shell／SSH；不能下單、轉帳、發布 WordPress、改排程、讀 token 或 .env。"
        "A6 gateway 沒有 Google Sheets／Drive／GitHub API 直連；Telegram token 只由 gateway 使用，不會交給模型。\n\n"
        f"模型：gateway 會逐一嘗試 {chain}，{fallback}；最近成功 provider：{last}。\n"
        f"記憶：會跨重啟保存最近 {snap['memory']['history_limit_messages']} 則生成式對話 context，執行任務另有長期檔案 receipt。"
    )


def signal_status_snapshot() -> dict[str, Any]:
    reports = sorted(
        SIGNAL_REPORT_ROOT.glob("limit_up_chip_story_*.md"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    ) if SIGNAL_REPORT_ROOT.exists() else []
    latest = reports[0] if reports else None
    report_date = None
    if latest:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", latest.name)
        report_date = match.group(1) if match else None
    return {
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "launchd": launchctl_snapshot(SIGNAL_LABEL),
        "latest_report": str(latest) if latest else None,
        "latest_report_date": report_date,
        "latest_report_mtime": (
            datetime.fromtimestamp(latest.stat().st_mtime).astimezone().isoformat(timespec="seconds")
            if latest
            else None
        ),
    }


def format_signal_status() -> str:
    snap = signal_status_snapshot()
    launchd = snap["launchd"]
    if snap["latest_report"]:
        report = (
            f"最新檔案日期 {snap['latest_report_date'] or 'unknown'}，"
            f"mtime {snap['latest_report_mtime']}，路徑 {snap['latest_report']}"
        )
    else:
        report = "找不到 limit_up_chip_story 報告"
    stale_note = ""
    if snap.get("latest_report_date"):
        today = time.strftime("%Y-%m-%d")
        if snap["latest_report_date"] != today:
            stale_note = f"；不是今天 {today} 的產出，不能當今日名單"
    return (
        "【hermes runtime】16:20 動能名單實況\n"
        f"launchd：{_launchd_text(launchd)}；runs={launchd.get('runs') or 'unknown'}。\n"
        f"報告：{report}{stale_note}。\n"
        "判定依據是本機 launchd 與檔案 mtime，不採用手冊中的歷史快照。"
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("capabilities", "signal-status"))
    args = parser.parse_args()
    if args.command == "capabilities":
        print(format_capabilities())
    else:
        print(format_signal_status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
