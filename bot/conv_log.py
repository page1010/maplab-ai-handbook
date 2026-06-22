"""
Structured JSONL conversation logger — one line per exchange, with model field.
Output: data/telegram-conv/YYYY-MM-DD.jsonl (gitignored, never enters public repo)
Trading bot import: from conv_log import log_exchange
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("maplab_bot.conv_log")

_CONV_LOG_SUBDIR = "telegram-conv"


def get_log_path(repo_path: Path) -> Path:
    log_dir = repo_path / "data" / _CONV_LOG_SUBDIR
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    return log_dir / f"{today}.jsonl"


def log_exchange(
    repo_path: Path,
    chat_id: int,
    user_message: str,
    bot_reply: str,
    model: str,
    failure_kind: Optional[str] = None,
) -> None:
    """Append one conversation exchange to today's JSONL log file."""
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "chat_id": chat_id,
        "model": model,
        "failure_kind": failure_kind or None,
        "user": user_message[:2000],
        "reply": bot_reply[:2000],
    }
    try:
        path = get_log_path(repo_path)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        logger.warning(f"conv_log write failed: {exc}")
