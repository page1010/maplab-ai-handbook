"""
Shared model-switching state for MAPLAB bots.
Trading bot import: from model_switch import ModelSwitchState, HERMES_STICKY_COOLDOWN_SECS
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

HERMES_STICKY_COOLDOWN_SECS: int = int(os.getenv("HERMES_STICKY_COOLDOWN_SECS", "300"))

_STICKY_TRIGGER_KINDS = frozenset({"quota", "rate_limit", "auth"})


class ModelSwitchState:
    """Asyncio-safe model switch state (single-writer, event loop)."""

    def __init__(self) -> None:
        self._manual_hermes: bool = False
        self._sticky_until: Optional[datetime] = None

    def force_hermes(self) -> None:
        """Manual /hermes: lock to Hermes indefinitely."""
        self._manual_hermes = True
        self._sticky_until = None

    def force_claude(self) -> None:
        """Manual /claude: release all sticky state, back to Claude primary."""
        self._manual_hermes = False
        self._sticky_until = None

    def mark_claude_failure(self, failure_kind: str) -> None:
        """Call after Claude fails — starts cooldown for quota/rate/auth kinds."""
        if failure_kind in _STICKY_TRIGGER_KINDS and not self._manual_hermes:
            self._sticky_until = datetime.now() + timedelta(seconds=HERMES_STICKY_COOLDOWN_SECS)

    def should_skip_claude(self) -> bool:
        """Returns True if Claude should be skipped this request."""
        if self._manual_hermes:
            return True
        if self._sticky_until:
            if datetime.now() < self._sticky_until:
                return True
            self._sticky_until = None
        return False

    def status_line(self) -> str:
        now = datetime.now()
        if self._manual_hermes:
            return "🟡 手動強制 Hermes 模式（/claude 可切回）"
        if self._sticky_until and now < self._sticky_until:
            remaining = int((self._sticky_until - now).total_seconds())
            return f"🟡 Hermes 冷卻中（Claude quota/rate_limit/auth 失敗後自動切，{remaining}s 後恢復嘗試）"
        return "🟢 Claude primary（quota/rate_limit/auth 失敗後自動切 Hermes 冷卻）"

    def active_label(self, hermes_model: str) -> str:
        if self.should_skip_claude():
            return f"Hermes/{hermes_model}"
        return "Claude"
