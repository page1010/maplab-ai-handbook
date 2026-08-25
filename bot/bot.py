#!/usr/bin/env python3
"""
MAPLAB A1 遠端讀檔終端 — Telegram daemon (long polling)
24/7 persistent listener on Mac mini
直接讀取 repo markdown 文件回傳，無 Claude API 呼叫

Usage:
    python3 bot.py
    (or via launchd for auto-start)
"""

import asyncio
import hashlib
import http.server
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ── Config ─────────────────────────────────────────────────────────────────────
BOT_DIR = Path(__file__).parent
if str(BOT_DIR) not in sys.path:
    sys.path.insert(0, str(BOT_DIR))
from model_switch import ModelSwitchState, HERMES_STICKY_COOLDOWN_SECS
from conv_log import log_exchange as _log_exchange_jsonl
load_dotenv(BOT_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "1077768811"))
REPO_PATH = Path(os.getenv("REPO_PATH", "/Users/pagemacmini/maplab-ai-handbook"))
CLAUDE_OAUTH_TOKEN = os.getenv("CLAUDE_CODE_OAUTH_TOKEN", "")
HERMES_FALLBACK_MODEL = os.getenv("HERMES_FALLBACK_MODEL", "gemma4:latest")
HERMES_FALLBACK_TIMEOUT = int(os.getenv("HERMES_FALLBACK_TIMEOUT", "60"))
HERMES_FALLBACK_TOOLSETS = os.getenv(
    "HERMES_FALLBACK_TOOLSETS",
    "none",
)
HERMES_PHOTO_FALLBACK_TOOLSETS = os.getenv("HERMES_PHOTO_FALLBACK_TOOLSETS", "vision")
HERMES_PROMPT_MAX_CHARS = int(os.getenv("HERMES_PROMPT_MAX_CHARS", "2200"))
HERMES_FALLBACK_HOME = Path(os.getenv("HERMES_FALLBACK_HOME", "/private/tmp/maplab-hermes-fallback"))
OLLAMA_FALLBACK_URL = os.getenv("OLLAMA_FALLBACK_URL", "http://127.0.0.1:11434/api/generate")
RUNTIME_BIN_DIRS = [
    str(Path.home() / ".local" / "bin"),
    "/opt/homebrew/bin",
    "/usr/local/bin",
    "/usr/bin",
    "/bin",
    "/usr/sbin",
    "/sbin",
]

TELEGRAM_LOG_DIR = REPO_PATH / "data" / "telegram-logs"
TELEGRAM_PHOTO_DIR = REPO_PATH / "data" / "telegram-photos"
CONV_HISTORY_FILE = BOT_DIR / "conv_history.json"
DISPATCH_DIR = Path(
    os.getenv("MAPLAB_DISPATCH_DIR", str(REPO_PATH / "workbook" / "telegram-dispatch"))
)

# ── Stock Discussion Group ingress (Owner 2026-08-24) ───────────────────────────
# The bot is already a member of the group chat -5589898264 (see
# claude-daily-operations/state/a0_groups.json) and receives Owner's own
# messages there (bots never see other bots' messages, so anything reaching
# handle_group_message is always a human). Owner's ruling from 能力測試 D:
# general group chit-chat must stay completely silent — only an explicit
# 研調:/辯論:/討論: trigger (optionally after an @bot mention) gets any
# reply at all. See handle_group_message() below.
STOCK_DISCUSSION_GROUP_BOT_USERNAME = os.getenv("STOCK_DISCUSSION_GROUP_BOT_USERNAME", "maplab_claude_bot")
INVESTMENT_OS_DIR = Path(os.getenv("INVESTMENT_OS_DIR", "/Users/pagemacmini/investment-os"))
INVESTMENT_OS_VENV_PYTHON = Path(
    os.getenv("INVESTMENT_OS_VENV_PYTHON", str(INVESTMENT_OS_DIR / ".venv" / "bin" / "python"))
)
DISCUSSION_ORCHESTRATOR_RELATIVE_SCRIPT = "scripts/run_stock_discussion.py"
DISCUSSION_ORCHESTRATOR_TIMEOUT_S = int(os.getenv("DISCUSSION_ORCHESTRATOR_TIMEOUT_S", "1500"))
TAIPEI_TZ = ZoneInfo("Asia/Taipei")

# ── Clipboard Server ────────────────────────────────────────────────────────────
CLIP_FILE = Path("/tmp/maplab_clip.json")
CLIP_SERVER_PORT = 9875

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_FILE = BOT_DIR / "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("maplab_bot")
_TOKEN_URL_RE = re.compile(r"bot[0-9]+:[A-Za-z0-9_-]+")


def _redact_runtime_secrets(text: str) -> str:
    safe = str(text or "")
    if BOT_TOKEN:
        safe = safe.replace(BOT_TOKEN, "<TELEGRAM_BOT_TOKEN>")
    return _TOKEN_URL_RE.sub("bot<TELEGRAM_BOT_TOKEN>", safe)


class _RedactRuntimeSecretsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact_runtime_secrets(record.getMessage())
        record.args = ()
        return True


for _handler in logging.getLogger().handlers:
    _handler.addFilter(_RedactRuntimeSecretsFilter())
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

START_TIME = datetime.now()

# Semaphore: only one Claude call at a time
_claude_semaphore = asyncio.Semaphore(1)

# Conversation history per chat_id (deque maxlen=20 messages)
_conv_history: dict[int, deque] = {}

# Pending reset confirmations: chat_id → generated summary text
_pending_reset: dict[int, str] = {}

def _build_system_prompt() -> str:
    """Build system prompt by injecting A1 recall section from AGENT_RECALL_PROMPTS.md.

    Extracts the code-block content under '## A1｜系統總管中心' and appends a brief
    snapshot of the latest 3 CURRENT_STATUS facts. Falls back to static prompt on error.
    """
    recall_text = ""
    try:
        recall_file = REPO_PATH / "AGENT_RECALL_PROMPTS.md"
        if recall_file.exists():
            raw = recall_file.read_text(encoding="utf-8")
            # Extract the code block under the A1 section heading
            in_a1 = False
            in_block = False
            block_lines: list[str] = []
            for line in raw.splitlines():
                if "## A1｜系統總管中心" in line:
                    in_a1 = True
                    continue
                if in_a1 and line.strip().startswith("## "):
                    break  # next section
                if in_a1 and line.strip() == "```" and not in_block:
                    in_block = True
                    continue
                if in_a1 and in_block and line.strip() == "```":
                    break
                if in_a1 and in_block:
                    # Stop before the 斷點 section (breakpoint info is stale; status comes from CURRENT_STATUS)
                    if line.startswith("【斷點"):
                        break
                    block_lines.append(line)
            if block_lines:
                recall_text = "\n".join(block_lines).strip()
    except Exception as e:  # noqa: BLE001
        import logging as _log
        _log.getLogger(__name__).warning(f"[bot] recall load failed: {e}")

    status_snippet = ""
    try:
        status_file = REPO_PATH / "CURRENT_STATUS.md"
        if status_file.exists():
            lines = status_file.read_text(encoding="utf-8").splitlines()
            # Grab up to 3 "最新事實核對" bullet lines (lines starting with "- 2026-")
            facts: list[str] = []
            for line in lines:
                if line.startswith("- 2026-") and len(facts) < 3:
                    # Trim to ~120 chars to keep prompt compact
                    facts.append(line[:120] + ("…" if len(line) > 120 else ""))
            if facts:
                status_snippet = "\n\n【最新系統狀態（截錄自 CURRENT_STATUS.md）】\n" + "\n".join(facts)
    except Exception:  # noqa: BLE001
        pass

    if recall_text:
        return (
            "【A1 Telegram Bot 前端 → A1 Claude Code 處理】\n"
            "以下是從 Telegram 轉發的 Owner 對話，請以 A1 系統總管身份協助回答。請用繁體中文簡潔回答。\n\n"
            "=== A1 召回檔（AGENT_RECALL_PROMPTS.md ## A1 段落）===\n"
            + recall_text
            + status_snippet
        )
    # Fallback: static prompt (pre-2026-07-10 behaviour)
    return (
        "【A1 Telegram Bot 前端 → A1 Claude Code 處理】\n"
        "以下是從 Telegram 轉發的 Owner 對話，請以 A1 系統總管身份協助回答。\n"
        "MAPLAB 婚禮/活動攝影工作室 AI 系統（v6.0，Phase 6）。\n"
        "Agents：A0=Cowork 總調度秘書（桌面控制）、A1=系統總管（Claude Code + Telegram bot）、"
        "A2=SEO、A3=廣告、A4=照片分類、A5=報價、A7=客服 FAQ。\n"
        "請用繁體中文簡潔回答。"
        + status_snippet
    )


ANTHROPIC_SYSTEM_PROMPT = _build_system_prompt()


def _load_conv_history() -> None:
    """Load persisted conversation history from disk on startup."""
    if not CONV_HISTORY_FILE.exists():
        return
    try:
        data = json.loads(CONV_HISTORY_FILE.read_text(encoding="utf-8"))
        for chat_id_str, msgs in data.items():
            d = deque(maxlen=20)
            d.extend(msgs[-20:])
            _conv_history[int(chat_id_str)] = d
        logger.info(f"Loaded conv history for {len(_conv_history)} chat(s)")
    except Exception as e:
        logger.warning(f"Failed to load conv history: {e}")


def _save_conv_history() -> None:
    """Persist conversation history to disk after each exchange."""
    try:
        data = {str(k): list(v) for k, v in _conv_history.items()}
        CONV_HISTORY_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as e:
        logger.warning(f"Failed to save conv history: {e}")


def _get_history(chat_id: int) -> deque:
    if chat_id not in _conv_history:
        _conv_history[chat_id] = deque(maxlen=20)
    return _conv_history[chat_id]


# ── Conversation Logger ─────────────────────────────────────────────────────────

def log_conversation(owner_msg: str, bot_reply: str, context_label: str = "") -> None:
    """Append a conversation exchange to the daily telegram log file."""
    try:
        TELEGRAM_LOG_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = TELEGRAM_LOG_DIR / f"{today}.md"
        ts = datetime.now().strftime("%H:%M:%S")
        label = f" `[{context_label}]`" if context_label else ""
        entry = (
            f"\n## {today} {ts}{label}\n"
            f"**Owner：** {owner_msg}\n\n"
            f"**Bot：** {bot_reply}\n\n"
            f"---\n"
        )
        # Create header if new file
        if not log_file.exists():
            header = f"# Telegram 對話紀錄 — {today}\n\n> 自動產生，供 agent 恢復記憶用\n"
            log_file.write_text(header, encoding="utf-8")
        with log_file.open("a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        logger.warning(f"log_conversation failed: {e}")


def git_commit_log_sync() -> None:
    """Stage and commit today's telegram log. Non-blocking caller should use thread."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        log_rel = f"data/telegram-logs/{today}.md"
        subprocess.run(
            ["git", "add", log_rel],
            cwd=REPO_PATH, capture_output=True, timeout=10,
        )
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=REPO_PATH, capture_output=True, timeout=5,
        )
        if result.returncode != 0:  # There are staged changes
            subprocess.run(
                ["git", "commit", "-m", f"log(telegram): {today} 對話紀錄自動存檔"],
                cwd=REPO_PATH, capture_output=True, timeout=15,
            )
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=REPO_PATH, capture_output=True, timeout=30,
            )
    except Exception as e:
        logger.warning(f"git_commit_log failed: {e}")


def log_and_commit(owner_msg: str, bot_reply: str, context_label: str = "") -> None:
    """Log conversation and async commit in background thread."""
    import threading
    log_conversation(owner_msg, bot_reply, context_label)
    t = threading.Thread(target=git_commit_log_sync, daemon=True)
    t.start()


# ── Auth guard ─────────────────────────────────────────────────────────────────

def is_owner(update: Update) -> bool:
    return update.effective_user.id == OWNER_CHAT_ID


async def deny(update: Update) -> None:
    logger.warning(f"Unauthorized access from {update.effective_user.id}")
    await update.message.reply_text("⛔ 未授權")


# ── Helpers ────────────────────────────────────────────────────────────────────

def git_pull_silent() -> None:
    """Silent git pull --rebase. Fail gracefully."""
    try:
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=REPO_PATH,
            capture_output=True,
            timeout=15,
        )
    except Exception:
        pass


def read_file(rel_path: str) -> str:
    """Read a file relative to REPO_PATH. Return content or error string."""
    p = REPO_PATH / rel_path
    if not p.exists():
        return f"⚠️ 找不到檔案：{rel_path}"
    return p.read_text(encoding="utf-8")


async def send_long(update: Update, text: str) -> None:
    """Send text, splitting at 4096 chars if needed."""
    MAX = 4096
    for i in range(0, len(text), MAX):
        await update.message.reply_text(text[i:i + MAX])


def _truthy_env(name: str, default: str = "") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _falsey_env(name: str, default: str = "") -> bool:
    return os.getenv(name, default).strip().lower() in {"0", "false", "no", "off"}


LOCAL_MODEL_POLICY_FILE = Path(
    os.getenv(
        "LOCAL_MODEL_POLICY_FILE",
        "/Users/pagemacmini/claude-daily-operations/state/local_model_policy.json",
    )
)


def _local_model_disabled(model: str) -> bool:
    """Owner 2026-08-22 memory policy: models listed in disabled_models must not be loaded."""
    try:
        policy = json.loads(LOCAL_MODEL_POLICY_FILE.read_text(encoding="utf-8"))
        disabled = {str(m).strip() for m in policy.get("disabled_models", [])}
        base = model.split(":")[0]
        return model in disabled or any(d.split(":")[0] == base for d in disabled)
    except Exception:
        return False


def _hermes_fallback_enabled() -> bool:
    if _falsey_env("HERMES_FALLBACK_ENABLED", "1"):
        return False
    model = os.getenv("HERMES_FALLBACK_MODEL", HERMES_FALLBACK_MODEL)
    if _local_model_disabled(model):
        logger.warning("hermes fallback skipped: model %s disabled by local_model_policy", model)
        return False
    return True


def _runtime_path(base_path: str = "") -> str:
    seen = set()
    parts = []
    for item in [*RUNTIME_BIN_DIRS, *(base_path or os.getenv("PATH", "")).split(":")]:
        if item and item not in seen:
            seen.add(item)
            parts.append(item)
    return ":".join(parts)


def _runtime_which(command: str) -> str:
    return shutil.which(command, path=_runtime_path()) or ""


def _hermes_model_label() -> str:
    return os.getenv("HERMES_FALLBACK_MODEL", HERMES_FALLBACK_MODEL)


def _hermes_toolsets() -> str:
    return os.getenv("HERMES_FALLBACK_TOOLSETS", HERMES_FALLBACK_TOOLSETS).strip()


def _message_has_image_path(user_message: str) -> bool:
    text = user_message or ""
    image_markers = (".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif", ".tif", ".tiff")
    return "data/telegram-photos/" in text or any(marker in text.lower() for marker in image_markers)


def _hermes_toolsets_for_message(user_message: str) -> str:
    if "HERMES_FALLBACK_TOOLSETS" in os.environ:
        return _hermes_toolsets()
    if _message_has_image_path(user_message):
        return os.getenv("HERMES_PHOTO_FALLBACK_TOOLSETS", HERMES_PHOTO_FALLBACK_TOOLSETS).strip()
    return HERMES_FALLBACK_TOOLSETS.strip()


def _is_no_tools_toolset(toolsets: str) -> bool:
    return toolsets.strip().lower() in {"", "none", "no-tools", "notools"}


def _ensure_no_tools_hermes_home() -> Path:
    """Create an isolated no-tools Hermes profile for gemma4 text fallback."""
    home = Path(os.getenv("HERMES_FALLBACK_HOME", str(HERMES_FALLBACK_HOME)))
    home.mkdir(parents=True, exist_ok=True)
    config = home / "config.yaml"
    config.write_text(
        "\n".join(
            [
                "model:",
                f"  default: {_hermes_model_label()}",
                "  provider: custom",
                f"  base_url: {os.getenv('HERMES_FALLBACK_BASE_URL', 'http://127.0.0.1:11434/v1')}",
                f"  api_key: {os.getenv('HERMES_FALLBACK_API_KEY', 'local-ollama-dummy')}",
                "  context_length: 131072",
                "platform_toolsets:",
                "  cli: []",
                "streaming:",
                "  enabled: false",
                "display:",
                "  streaming: false",
                "  personality: none",
                "agent:",
                "  max_turns: 4",
                "  reasoning_effort: low",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return home


def _hermes_prompt_max_chars() -> int:
    raw = os.getenv("HERMES_PROMPT_MAX_CHARS", str(HERMES_PROMPT_MAX_CHARS)).strip()
    try:
        return max(1200, int(raw))
    except ValueError:
        return HERMES_PROMPT_MAX_CHARS


@dataclass(frozen=True)
class ModelResult:
    ok: bool
    answer: str
    failure_kind: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class ModelAnswer:
    text: str
    model: str
    failure_kind: str = ""


_switch = ModelSwitchState()


@dataclass(frozen=True)
class DispatchRoute:
    task_type: str
    title: str
    primary_role: str
    roles: tuple[str, ...]
    worker: str
    runtime_target: str
    task_cards: tuple[str, ...]
    goal: str
    data_needed: tuple[str, ...]
    guardrails: tuple[str, ...]


_ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def _sanitize_for_telegram(text: str) -> str:
    return _CONTROL_RE.sub("", _ANSI_RE.sub("", text or "")).strip()


def _classify_claude_failure(stderr_text: str, fallback_kind: str = "") -> str:
    if fallback_kind:
        return fallback_kind
    text = (stderr_text or "").lower()
    quota_markers = (
        "usage limit",
        "quota",
        "exceeded",
        "limit reached",
        "max",
        "credit",
        "credits",
        "insufficient_quota",
        "subscription",
        "找不到 claude",
        "回應超時",
        "呼叫 claude 失敗",
        "額度",
        "沒額度",
        "無額度",
        "用量",
    )
    rate_markers = ("rate limit", "too many requests", "429")
    auth_markers = (
        "auth",
        "oauth",
        "unauthorized",
        "not logged in",
        "expired",
        "invalid grant",
        "invalid_grant",
        "forbidden",
        "401",
        "403",
    )
    unavailable_markers = (
        "overloaded",
        "temporarily unavailable",
        "service unavailable",
        "connection",
        "network",
        "econn",
        "operation not permitted",
    )
    if any(marker in text for marker in auth_markers):
        return "auth"
    if any(marker in text for marker in rate_markers):
        return "rate_limit"
    if any(marker in text for marker in quota_markers):
        return "quota"
    if any(marker in text for marker in unavailable_markers):
        return "primary_unavailable"
    return "unknown"


def _should_fallback_to_hermes(result: ModelResult) -> bool:
    if _truthy_env("MAPLAB_FORCE_HERMES_FALLBACK"):
        return True
    return result.failure_kind in {
        "quota",
        "rate_limit",
        "auth",
        "cli_missing",
        "timeout",
        "primary_unavailable",
        "forced",
        "sticky_hermes",
    }


def _trim(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    suffix = "\n…（截斷）"
    if limit <= len(suffix):
        return text[:limit]
    return text[: limit - len(suffix)] + suffix


def _read_optional(rel_path: str, limit: int) -> str:
    path = REPO_PATH / rel_path
    try:
        if path.exists():
            return _trim(path.read_text(encoding="utf-8"), limit)
    except Exception as exc:
        return f"（讀取 {rel_path} 失敗：{exc}）"
    return f"（找不到 {rel_path}）"


def _read_relevant_pitfalls(limit: int = 4500) -> str:
    path = REPO_PATH / "pitfalls.md"
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"（讀取 pitfalls.md 失敗：{exc}）"
    headings = (
        "Hermes fallback means the Telegram Claude bot fallback path",
        "Artifact substitution",
        "Secret safety must not become a work blocker",
        "Permission gates can violate fast iteration culture",
    )
    lines = text.splitlines()
    selected: list[str] = []
    keep = False
    for line in lines:
        if line.startswith("## "):
            keep = any(h in line for h in headings)
        if keep:
            selected.append(line)
    return _trim("\n".join(selected) or text, limit)


def _latest_telegram_log_snippet(limit: int = 2500) -> str:
    try:
        logs = sorted(TELEGRAM_LOG_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime)
    except Exception:
        logs = []
    if not logs:
        return "（沒有 Telegram log snippet）"
    latest = logs[-1]
    try:
        return f"source={latest.relative_to(REPO_PATH)}\n" + _trim(latest.read_text(encoding="utf-8"), limit)
    except Exception as exc:
        return f"（讀取 Telegram log 失敗：{exc}）"


def _record_history(chat_id: int, user_message: str, answer: str) -> None:
    history = _get_history(chat_id)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": answer})
    _save_conv_history()


def _dispatch_catalog() -> dict[str, DispatchRoute]:
    return {
        "ads": DispatchRoute(
            task_type="ads-performance-review",
            title="投放成效判讀任務",
            primary_role="A3",
            roles=("A3", "A2", "A1"),
            worker="Codex primary; OpenClaw read-only browser proof if logged-in Ads UI is needed",
            runtime_target="codex/openclaw",
            task_cards=(
                "handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md",
                "projects/maplab-ads-monitor.md",
                "projects/seo-ads-agent.md",
            ),
            goal=(
                "讀近 7/14/30 天 Google Ads + Meta Ads 成效，拆出花費、曝光、點擊、CTR、"
                "CPC、轉換、CPA、ROAS，輸出保留/暫停/調整預算與素材下一步。"
            ),
            data_needed=(
                "Google Ads: spend, impressions, clicks, CTR, CPC, conversions, CPA, ROAS by 7/14/30 days",
                "Meta Ads: spend, impressions, clicks, CTR, CPC, conversions/leads, CPA/ROAS by 7/14/30 days",
                "Landing-page conversion context from A2 when ad data suggests page or SEO mismatch",
            ),
            guardrails=(
                "read-only first; do not change budget, campaign status, targeting, creative, Pixel, GTM, or landing pages",
                "if login/API data is missing, report the missing source and the exact 5-minute Owner action",
                "recommendations must separate verified metrics, inference, and approval-needed changes",
            ),
        ),
        "quote": DispatchRoute(
            task_type="quote-intake",
            title="報價/試算派工任務",
            primary_role="A6",
            roles=("A6", "A5"),
            worker="Codex/A6 intake; A5 quote engine or GAS/Sheet when a sheet artifact is required",
            runtime_target="codex/a6/a5",
            task_cards=(
                "handoff/tasks/T-A6-001.md",
                "handoff/tasks/T-A5-002.md",
                "projects/line-quote-assistant.md",
                "projects/maplab-master-data.md",
            ),
            goal=(
                "整理活動需求、品項、數量、預算、毛利/成本口徑與待確認欄位，"
                "再交給 A6/A5 產出報價草稿或 Sheet payload。"
            ),
            data_needed=(
                "event type, date/time, location, headcount, budget, service fee and logistics assumptions",
                "menu preferences, dietary restrictions, item mapping, margin/cost risk",
                "whether the required output is draft text, Sheet payload, or a formal quote link",
            ),
            guardrails=(
                "do not invent a Google Sheet or quote URL",
                "do not expose internal costs to customers",
                "if Sheet/GAS write is required, route through A5 and report the real artifact URL only after creation",
            ),
        ),
        "research": DispatchRoute(
            task_type="investment-research-note",
            title="投資研究筆記歸檔任務",
            primary_role="B3",
            roles=("B3", "A1"),
            worker="Codex writes/updates workbook/stock-notes/ cards as B3 Investment OS Archivist; no trading action",
            runtime_target="codex",
            task_cards=(
                "handoff/tasks/T-B1-B4-investment-os-role-split.md",
                "workbook/stock-notes/",
            ),
            goal=(
                "把 Owner 討論過的個股敘事、財務快照、風險點、來源連結整理成 workbook/stock-notes/ 卡片，"
                "並附上與 Owner 現有持股的機會成本比較觀點，供後續覆核追蹤（漲跌/敘事是否兌現）。"
            ),
            data_needed=(
                "ticker, company name, sector narrative",
                "revenue/growth snapshot and PE or valuation estimate with source and query date",
                "opportunity-cost comparison against Owner's current holdings",
                "chip/institutional flow signal if available, and risk points",
            ),
            guardrails=(
                "不下單、不建立模擬單、不給買賣建議 — 只整理事實與研究觀點，最終決策由 Owner 判斷",
                "every number must carry its source link and the date it was pulled",
                "flag when a narrative claim cannot be verified rather than presenting it as fact",
            ),
        ),
        "patrol": DispatchRoute(
            task_type="system-patrol-dispatch",
            title="系統巡查/任務推進派工",
            primary_role="A0",
            roles=("A0", "A1"),
            worker="Codex/A0/A1; Hermes may consume the packet as a cold-path reaction layer",
            runtime_target="codex/hermes",
            task_cards=(
                "CURRENT_STATUS.md",
                "pitfalls.md",
                "TASK_QUEUE.md",
                "workbook/hermes/patrol/latest.json",
            ),
            goal=(
                "把巡查或任務推進要求拆成已完成、卡住、可由 agent 自解、需 Owner 5 分鐘動作，"
                "並對 blocker 跑三層阻塞審查。"
            ),
            data_needed=(
                "CURRENT_STATUS.md task table and blockers",
                "relevant task cards and latest Hermes patrol packet",
                "exact role owner and next command for each still-open item",
            ),
            guardrails=(
                "do not relay stale blockers without assigning a next owner",
                "do not ask Owner until false blockers are removed",
                "write back only scoped status/task-card changes after evidence is checked",
            ),
        ),
        "generic": DispatchRoute(
            task_type="command-window-dispatch",
            title="Telegram 外部指揮派工",
            primary_role="A0",
            roles=("A0", "A1"),
            worker="Codex primary; OpenClaw/Hermes can act as intake or read-only worker",
            runtime_target="codex/openclaw/hermes",
            task_cards=("CURRENT_STATUS.md", "pitfalls.md", "TASK_QUEUE.md"),
            goal=(
                "把 Owner 的 Telegram 指令轉成角色、冷啟動來源、worker、可驗收輸出與回報節點，"
                "避免只回覆一段建議。"
            ),
            data_needed=(
                "Owner original request",
                "latest Telegram context if this is a follow-up question",
                "role module/task-card evidence before execution",
            ),
            guardrails=(
                "do not treat '召喚' as complete until a packet/worker receipt exists",
                "do not perform live external changes without explicit approval",
                "if route is ambiguous, create an A0/A1 intake packet instead of pretending completion",
            ),
        ),
    }


def _dispatch_norm(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").lower())


def _dispatch_has_any(haystack: str, markers: tuple[str, ...]) -> bool:
    return any(marker in haystack for marker in markers)


def _dispatch_route_for_text(text: str, context_text: str = "") -> Optional[DispatchRoute]:
    normalized = _dispatch_norm(text)
    if not normalized:
        return None

    catalog = _dispatch_catalog()
    quote_markers = ("報價", "quote", "試算", "毛利", "競品菜單")
    research_markers = (
        "個股",
        "股票",
        "股價",
        "本益比",
        "籌碼面",
        "法人佈局",
        "持股",
        "機會成本",
    )
    ads_markers = (
        "google廣告",
        "googleads",
        "meta廣告",
        "metaads",
        "廣告成效",
        "投放成效",
        "roas",
        "cpc",
        "cpa",
        "ctr",
    )
    patrol_markers = ("巡查", "任務推進", "任務卡", "taskcard", "三層阻塞審查")

    if _dispatch_has_any(normalized, research_markers):
        return catalog["research"]
    if _dispatch_has_any(normalized, quote_markers):
        return catalog["quote"]
    if _dispatch_has_any(normalized, ads_markers) or (
        "廣告" in normalized
        and _dispatch_has_any(normalized, ("成效", "評估", "投放", "meta", "google", "預算"))
    ):
        return catalog["ads"]
    if _dispatch_has_any(normalized, patrol_markers) or ("角色" in normalized and "巡查" in normalized):
        return catalog["patrol"]
    # NOTE(2026-08-21): removed the vague followup_markers/context-guess branch
    # (words like 派工/要做/去做/召喚 + stale _route_from_dispatch_context).
    # It kept reusing a contaminated recent-log snippet, so once one message
    # got misfiled (e.g. into ads-performance-review), every ambiguous
    # follow-up all evening re-inherited that same wrong label instead of
    # reaching real Claude. Ambiguous text now falls through to
    # _run_claude_guarded (real Claude judges it) instead of a regex guess.
    return None


def _path_label(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_PATH))
    except ValueError:
        return str(path)


def _dispatch_prompt_for(
    route: DispatchRoute,
    dispatch_id: str,
    owner_text: str,
    context_text: str = "",
) -> str:
    task_cards = "\n".join(f"- {item}" for item in route.task_cards)
    data_needed = "\n".join(f"- {item}" for item in route.data_needed)
    guardrails = "\n".join(f"- {item}" for item in route.guardrails)
    context_block = _trim(context_text or "（無額外 Telegram context）", 2400)
    return (
        f"你是 MAPLAB {route.primary_role}，運行在 Codex。\n"
        f"Telegram 派工 ID: {dispatch_id}\n"
        f"任務類型: {route.title}\n"
        f"主責/協作: {', '.join(route.roles)}\n\n"
        "## Cold Start\n"
        "1. 先讀 CURRENT_STATUS.md。\n"
        "2. 再讀 pitfalls.md，尤其是 Telegram command window / artifact substitution / Hermes fallback 相關教訓。\n"
        "3. 再讀本派工列出的 task cards / docs。\n"
        "4. 第一句先說：我是 [role]，環境 Codex，任務 [task]。\n\n"
        "## Owner 原始指令\n"
        "```text\n"
        f"{owner_text.strip()}\n"
        "```\n\n"
        "## 最近 Telegram context\n"
        "```text\n"
        f"{context_block}\n"
        "```\n\n"
        "## 必讀來源\n"
        f"{task_cards}\n\n"
        "## 本輪目標\n"
        f"{route.goal}\n\n"
        "## 需要取得/驗證的資料\n"
        f"{data_needed}\n\n"
        "## 邊界\n"
        f"{guardrails}\n\n"
        "## 輸出契約\n"
        "請回報：\n"
        "1. Startup Check：角色、環境、任務、資料來源。\n"
        "2. 已做的事：真的讀了哪些檔案/資料或執行了哪些 read-only checks。\n"
        "3. 結論：分成 verified facts、reasonable inference、missing data、next action。\n"
        "4. 若需要 Owner：只列 5 分鐘內可完成的具體動作。\n"
        "5. 若要寫回：列出要改的檔案與理由，未核准不得碰 live external settings。\n"
    )


def _openclaw_dispatch_timeout() -> int:
    raw = os.getenv("MAPLAB_OPENCLAW_DISPATCH_TIMEOUT", "180").strip()
    try:
        return max(15, int(raw))
    except ValueError:
        return 180


def _openclaw_dispatch_enabled() -> bool:
    return _truthy_env("MAPLAB_OPENCLAW_DISPATCH_ENABLED", "1")


def _write_dispatch_packet(
    owner_text: str,
    context_text: str = "",
    route: Optional[DispatchRoute] = None,
) -> dict[str, Any]:
    selected_route = route or _dispatch_route_for_text(owner_text, context_text)
    if not selected_route:
        raise ValueError("message does not match a dispatch route")

    ts = datetime.now()
    dispatch_id = f"TG-DISPATCH-{ts.strftime('%Y%m%d-%H%M%S')}-{selected_route.task_type}"
    packet_dir = DISPATCH_DIR / dispatch_id
    packet_dir.mkdir(parents=True, exist_ok=True)
    prompt = _dispatch_prompt_for(selected_route, dispatch_id, owner_text, context_text)
    prompt_path = packet_dir / "prompt.md"
    packet_path = packet_dir / "packet.json"
    readme_path = packet_dir / "README.md"
    openclaw_result_path = packet_dir / "openclaw_result.json"

    packet: dict[str, Any] = {
        "schema_version": "maplab.telegram_dispatch.v1",
        "dispatch_id": dispatch_id,
        "created_at": ts.isoformat(timespec="seconds"),
        "status": "queued_for_codex",
        "source": {
            "surface": "telegram",
            "owner_chat_id": str(OWNER_CHAT_ID),
            "message": owner_text,
            "context_excerpt": _trim(context_text, 1200),
        },
        "route": {
            "task_type": selected_route.task_type,
            "title": selected_route.title,
            "primary_role": selected_route.primary_role,
            "roles": list(selected_route.roles),
            "worker": selected_route.worker,
            "runtime_target": selected_route.runtime_target,
            "task_cards": list(selected_route.task_cards),
            "goal": selected_route.goal,
            "data_needed": list(selected_route.data_needed),
            "guardrails": list(selected_route.guardrails),
        },
        "artifacts": {
            "packet": _path_label(packet_path),
            "prompt": _path_label(prompt_path),
            "readme": _path_label(readme_path),
            "openclaw_result": _path_label(openclaw_result_path),
        },
        "codex_command": f"codex exec --cd {REPO_PATH} --sandbox workspace-write - < {prompt_path}",
        "openclaw_command": (
            "openclaw agent --agent main "
            f"--session-key agent:main:{dispatch_id} --message \"$(cat {prompt_path})\" --timeout {_openclaw_dispatch_timeout()} --json"
        ),
    }

    prompt_path.write_text(prompt, encoding="utf-8")
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    readme_path.write_text(
        "\n".join(
            [
                f"# {dispatch_id}",
                "",
                f"- status: {packet['status']}",
                f"- primary_role: {selected_route.primary_role}",
                f"- roles: {', '.join(selected_route.roles)}",
                f"- worker: {selected_route.worker}",
                f"- runtime_target: {selected_route.runtime_target}",
                f"- prompt: `{_path_label(prompt_path)}`",
                f"- packet: `{_path_label(packet_path)}`",
                "",
                "## Owner Request",
                "",
                "```text",
                owner_text.strip(),
                "```",
            ]
        ),
        encoding="utf-8",
    )
    index_path = DISPATCH_DIR / "index.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "dispatch_id": dispatch_id,
                    "created_at": packet["created_at"],
                    "status": packet["status"],
                    "primary_role": selected_route.primary_role,
                    "task_type": selected_route.task_type,
                    "prompt": packet["artifacts"]["prompt"],
                    "packet": packet["artifacts"]["packet"],
                },
                ensure_ascii=False,
            )
            + "\n"
        )

    try:
        CLIP_FILE.parent.mkdir(parents=True, exist_ok=True)
        CLIP_FILE.write_text(
            json.dumps(
                {
                    "text": prompt,
                    "ts": ts.strftime("%H:%M:%S"),
                    "source": "telegram_dispatch",
                    "dispatch_id": dispatch_id,
                    "prompt": packet["artifacts"]["prompt"],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.warning(f"dispatch clipboard write failed: {exc}")

    return packet


def _dispatch_receipt(packet: dict[str, Any]) -> str:
    route = packet["route"]
    openclaw_status = "will_start" if _openclaw_dispatch_enabled() else "disabled"
    return (
        f"✅ 已建立派工包：{packet['dispatch_id']}\n"
        "這不是只回覆：已落檔，並寫入 Codex clipboard bridge。\n"
        f"- 主責：{route['primary_role']}（協作：{', '.join(route['roles'])}）\n"
        f"- worker：{route['worker']}\n"
        f"- status：{packet['status']}\n"
        f"- openclaw_worker：{openclaw_status}\n"
        f"- packet：{packet['artifacts']['packet']}\n"
        f"- prompt：{packet['artifacts']['prompt']}\n"
        "下一步：worker 必須用這個 dispatch_id 回報；沒有 receipt 就不能再說已召喚。"
    )


def _openclaw_visible_text(stdout_text: str) -> str:
    text = (stdout_text or "").strip()
    if not text:
        return ""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text
    payloads = (((data or {}).get("result") or {}).get("payloads") or [])
    visible = "\n".join(
        str(payload.get("text") or "").strip()
        for payload in payloads
        if str(payload.get("text") or "").strip()
    )
    return visible or text


async def _run_openclaw_dispatch_background(
    bot,
    chat_id: int,
    packet: dict[str, Any],
) -> None:
    if not _openclaw_dispatch_enabled():
        return
    openclaw_path = _runtime_which("openclaw")
    if not openclaw_path:
        await bot.send_message(chat_id=chat_id, text=f"⚠️ OpenClaw dispatch skipped：找不到 openclaw CLI（{packet['dispatch_id']}）")
        return

    prompt_path = REPO_PATH / packet["artifacts"]["prompt"]
    result_path = REPO_PATH / packet["artifacts"]["openclaw_result"]
    try:
        prompt = prompt_path.read_text(encoding="utf-8")
    except Exception as exc:
        await bot.send_message(chat_id=chat_id, text=f"⚠️ OpenClaw dispatch skipped：讀不到 prompt（{exc}）")
        return

    env = os.environ.copy()
    env["PATH"] = _runtime_path(env.get("PATH", ""))
    cmd = [
        openclaw_path,
        "agent",
        "--agent",
        "main",
        "--session-key",
        f"agent:main:{packet['dispatch_id']}",
        "--message",
        prompt,
        "--timeout",
        str(_openclaw_dispatch_timeout()),
        "--json",
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=REPO_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=_openclaw_dispatch_timeout() + 10)
        except asyncio.TimeoutError:
            proc.kill()
            await bot.send_message(chat_id=chat_id, text=f"⚠️ OpenClaw dispatch timeout：{packet['dispatch_id']}")
            return

        result = {
            "dispatch_id": packet["dispatch_id"],
            "returncode": proc.returncode,
            "stdout": _redact_runtime_secrets(stdout.decode(errors="replace")),
            "stderr": _redact_runtime_secrets(stderr.decode(errors="replace")),
            "finished_at": datetime.now().isoformat(timespec="seconds"),
        }
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        if proc.returncode == 0:
            visible_text = _openclaw_visible_text(result["stdout"])
            snippet = _trim(visible_text or "OpenClaw returned no visible text", 1600)
            await bot.send_message(
                chat_id=chat_id,
                text=f"🧷 OpenClaw worker 回報：{packet['dispatch_id']}\n{snippet}",
            )
        else:
            diagnostic = _trim((result["stderr"] or result["stdout"] or "unknown error").strip(), 1000)
            await bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ OpenClaw worker 失敗：{packet['dispatch_id']}\n{diagnostic}",
            )
    except Exception as exc:
        safe = _redact_runtime_secrets(str(exc))
        await bot.send_message(chat_id=chat_id, text=f"⚠️ OpenClaw dispatch exception：{packet['dispatch_id']}\n{safe}")


def _looks_like_degraded_hermes_output(text: str) -> bool:
    cleaned = _sanitize_for_telegram(text)
    if not cleaned:
        return True
    compact = cleaned.replace(" ", "").replace("\n", "")
    if compact in {"HERII", "HERIThe", "HERTheI", "HERI**"}:
        return True
    if len(compact) <= 8 and compact.upper().startswith("HER"):
        return True
    return False


def _extract_exact_reply_request(user_message: str) -> str:
    """Return the fixed reply requested by Owner, if the message clearly asks for one."""
    text = (user_message or "").strip()
    if not text:
        return ""
    patterns = (
        r"(?:請)?(?:只|僅)(?:回覆|輸出|回答)\s*[「『\"'`]?([^」』\"'`，,。！？!\?\n]+)",
        r"(?:please\s+)?(?:only\s+)?(?:reply|output|print)\s+(?:exactly\s+)?[\"'`]?([A-Za-z0-9_:\-./ ]{2,160})",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        candidate = match.group(1).strip()
        candidate = re.sub(r"\s*(?:不要|不需|無需|不用|別).*$", "", candidate).strip()
        candidate = candidate.strip("「」『』\"'` .。")
        if 1 <= len(candidate) <= 160:
            return candidate
    return ""


def _exact_reply_contract_violation(user_message: str, answer: str) -> str:
    expected = _extract_exact_reply_request(user_message)
    if expected and _sanitize_for_telegram(answer) != expected:
        return expected
    return ""


def build_hermes_exact_repair_prompt(expected: str) -> str:
    return (
        "上一輪違反固定輸出契約。\n"
        "Do not explain. Do not add labels. Output exactly this string and nothing else:\n"
        f"{expected}"
    )


def build_hermes_repair_prompt(user_message: str, fallback_reason: str = "") -> str:
    return _trim(
        (
            "你是 MAPLAB Hermes fallback。Claude primary 不可用，"
            f"原因：{_trim(fallback_reason or 'unknown', 120)}。\n"
            "上一輪輸出格式壞掉。請重新回答本次 Owner 訊息。\n"
            "規則：如果 Owner 要固定字串，只輸出固定字串；否則用繁體中文，三行內：P0 / Answer / Next。\n"
            f"Owner: {user_message}"
        ),
        900,
    )


def build_hermes_minimal_prompt(user_message: str, fallback_reason: str = "") -> str:
    return _trim(
        (
            "MAPLAB Hermes fallback. Claude primary failed.\n"
            f"Reason: {_trim(fallback_reason or 'unknown', 120)}\n"
            "Answer the Owner in Traditional Chinese. Stay on the Telegram command-window task.\n"
            "Format exactly 3 lines unless Owner asks for an exact fixed string:\n"
            "P0: ...\nAnswer: ...\nNext: ...\n"
            f"Owner: {user_message}"
        ),
        700,
    )


def _local_model_prompt(user_message: str, fallback_reason: str = "") -> str:
    return build_hermes_minimal_prompt(user_message, fallback_reason)


def _ollama_generate_sync(prompt: str, timeout: int) -> str:
    payload = json.dumps(
        {
            "model": _hermes_model_label(),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 220,
            },
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_FALLBACK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return _sanitize_for_telegram(data.get("response", ""))


async def ollama_direct_ask(
    user_message: str,
    fallback_reason: str = "",
    trigger: str = "",
    timeout: int = 45,
) -> str:
    prompt = _local_model_prompt(user_message, fallback_reason)
    try:
        answer = await asyncio.to_thread(_ollama_generate_sync, prompt, timeout)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return f"⚠️ Ollama direct fallback 錯誤: {_trim(str(exc), 240)}"
    if not answer:
        return "⚠️ Ollama direct fallback 無回應"
    prefix = (
        "P0: Hermes CLI 未產生可用 final，已用本機 Ollama/gemma4 直連備援。\n"
        f"Trace: trigger={_trim(trigger or 'hermes_unavailable', 80)}\n"
    )
    return prefix + answer


def build_hermes_prompt(
    chat_id: int,
    user_message: str,
    system_extra: str = "",
    fallback_reason: str = "",
    toolsets: str = "",
) -> str:
    """Build a staged, compact fallback prompt for gemma4."""
    history = list(_get_history(chat_id))
    history_lines = []
    for msg in history[-4:]:
        role_label = "Owner" if msg["role"] == "user" else "助理"
        history_lines.append(f"{role_label}: {_trim(str(msg['content']), 240)}")

    memory_card = (
        f"repo={REPO_PATH}; entrypoint=bot/bot.py; primary=Claude CLI; fallback=Hermes/gemma4.\n"
        "Trigger: only quota/rate/auth/timeout/cli_missing/primary_unavailable.\n"
        "Owner need: Telegram external command window. Do not turn it into Extension/patrol/panel/dashboard cleanup.\n"
        "Culture: direct-do/draft/smoke first; live computer-control/send/delete/publish/secrets require final confirmation.\n"
        "Anchors to mention if needed: CURRENT_STATUS.md, pitfalls.md, docs/company-values.md, docs/agent-behavior-framework.md, latest Telegram log."
    )
    history_block = _trim("\n".join(history_lines), 500) if history_lines else "none"
    extra_block = _trim(system_extra, 300) if system_extra else "none"

    active_toolsets = toolsets or _hermes_toolsets_for_message(user_message)
    prompt = f"""MAPLAB HERMES FALLBACK V0

<stage_0_identity>
You are Hermes fallback for MAPLAB A1 Telegram bot. Claude primary failed.
reason={_trim(fallback_reason or 'unknown', 180)}
model={_hermes_model_label()}
toolset={active_toolsets or 'none'}
</stage_0_identity>

<stage_1_memory_card>
{memory_card}
</stage_1_memory_card>

<stage_2_tripwire>
Before answering, check if the request is drifting away from the Telegram bot fallback P0.
Wrong path examples: Extension target sync, patrol panel, dashboard polish, broad metadata cleanup.
</stage_2_tripwire>

<stage_3_context>
recent_chat={history_block}
extra={extra_block}
</stage_3_context>

<stage_4_owner_message>
{user_message}
</stage_4_owner_message>

<stage_5_output_contract>
If Owner asks for an exact fixed string, output that fixed string only.
Otherwise answer in Traditional Chinese:
P0: one line
Answer: concise answer
Next: one concrete next action or confirmation needed
Trace: Hermes fallback, {_hermes_model_label()}, {datetime.now().strftime('%Y-%m-%d %H:%M')}
</stage_5_output_contract>
"""
    return _trim(prompt, _hermes_prompt_max_chars())


async def hermes_ask(
    chat_id: int,
    user_message: str,
    system_extra: str = "",
    fallback_reason: str = "",
    timeout: Optional[int] = None,
) -> str:
    """Call Hermes one-shot fallback. Hermes loads repo rules/memory from CWD."""
    toolsets = _hermes_toolsets_for_message(user_message)
    prompt = build_hermes_prompt(chat_id, user_message, system_extra, fallback_reason, toolsets=toolsets)
    timeout = timeout or HERMES_FALLBACK_TIMEOUT
    env = os.environ.copy()
    env["PATH"] = _runtime_path(env.get("PATH", ""))

    if _is_no_tools_toolset(toolsets):
        env["HERMES_HOME"] = str(_ensure_no_tools_hermes_home())

    async def _run_prompt(prompt_text: str) -> str:
        command = ["hermes", "-m", _hermes_model_label()]
        if not _is_no_tools_toolset(toolsets):
            command.extend(["-t", toolsets])
        command.extend(["-z", prompt_text])
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(REPO_PATH),
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return f"⚠️ Hermes fallback 回應超時（{timeout}秒）"
        if proc.returncode != 0:
            err = stderr.decode(errors="replace")[:500].strip()
            return f"⚠️ Hermes fallback 錯誤: {err or '未知錯誤'}"
        return _sanitize_for_telegram(stdout.decode(errors="replace")) or "（Hermes 無回應）"

    try:
        answer = await _run_prompt(prompt)
        if answer.startswith("⚠️ Hermes fallback 錯誤") and "no final response" in answer:
            repaired = await _run_prompt(build_hermes_minimal_prompt(user_message, fallback_reason))
            if not repaired.startswith("⚠️"):
                return repaired
            return await ollama_direct_ask(
                user_message,
                fallback_reason,
                trigger=f"{answer}; retry={repaired}",
            )
        if answer.startswith("⚠️ Hermes fallback 回應超時"):
            return await ollama_direct_ask(user_message, fallback_reason, trigger=answer)
        if not answer.startswith("⚠️") and _looks_like_degraded_hermes_output(answer):
            repair_prompt = build_hermes_repair_prompt(user_message, fallback_reason)
            repaired = await _run_prompt(repair_prompt)
            if not repaired.startswith("⚠️") and not _looks_like_degraded_hermes_output(repaired):
                return repaired
        exact_expected = _exact_reply_contract_violation(user_message, answer)
        if not answer.startswith("⚠️") and exact_expected:
            repaired = await _run_prompt(build_hermes_exact_repair_prompt(exact_expected))
            if not repaired.startswith("⚠️") and _sanitize_for_telegram(repaired) == exact_expected:
                return exact_expected
            return exact_expected
        return answer
    except FileNotFoundError:
        return await ollama_direct_ask(user_message, fallback_reason, trigger="hermes command not found")
    except Exception as exc:
        return f"⚠️ 呼叫 Hermes fallback 失敗: {exc}"


def _format_hermes_receipt(fallback_reason: str, toolsets: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "🟡 Claude primary unavailable，Hermes fallback 接手\n"
        f"- primary_failed_reason: {_trim(fallback_reason, 220)}\n"
        "- fallback=Hermes\n"
        f"- model: {_hermes_model_label()}\n"
        f"- toolsets: {toolsets or 'none'}\n"
        f"- agent: A1 Telegram bot -> Hermes fallback\n"
        f"- date: {now}\n"
        "- memory_sources: compact memory card with anchors to CURRENT_STATUS.md, pitfalls.md, company-values, agent-behavior-framework, latest Telegram log\n"
        "- allowed_actions: Telegram fallback 只做 read/draft/smoke/image-analysis；live send/delete/publish/secrets/computer-control 需最後確認\n"
        "- next_check: 回覆後檢查 Telegram receipt、bot log、gemma4 validator"
    )


def _local_runtime_question_answer(text: str) -> str:
    normalized = (text or "").strip().lower()
    model_question = ("什麼模型" in normalized or "哪個模型" in normalized or "what model" in normalized)
    capability_question = ("可以做什麼" in normalized or "能做什麼" in normalized or "capabil" in normalized)
    if not (model_question and capability_question):
        return ""
    claude_path = _runtime_which("claude") or "missing"
    hermes_path = _runtime_which("hermes") or "missing"
    return (
        "我是 MAPLAB A1 Telegram bot。\n"
        f"- primary: Claude CLI ({claude_path})\n"
        f"- fallback: Hermes/gemma4 ({hermes_path}, model={_hermes_model_label()})\n"
        "- fallback trigger: Claude quota/rate/auth/timeout/cli_missing/primary_unavailable\n"
        "- 我可以做：查任務/狀態、整理下一步、草稿、read/draft/smoke、圖片分析、在 Claude 不可用時用本機模型備援。\n"
        "- 我不能直接做：live send/delete/publish/secrets/computer-control，除非你最後確認。"
    )


def _local_dispatch_answer(text: str) -> str:
    normalized = (text or "").strip().lower()
    if not normalized:
        return ""

    quote_markers = ("報價", "quote", "試算", "毛利", "成本", "競品菜單")
    patrol_markers = ("巡查", "任務推進", "任務卡", "角色", "召喚", "推進")
    ads_markers = ("google廣告", "google ads", "meta廣告", "meta ads", "廣告成效", "roas", "cpc", "cpa")

    if any(marker in normalized for marker in quote_markers):
        return (
            "P0: 這是報價任務，A1 不應硬算或假裝已建 Sheet。\n"
            "召喚：A6 先接需求/OCR/競品品項對應；A5 負責成本表、毛利公式、Google Sheet/報價單產出。\n"
            "我能先做：整理品項、數量、毛利規則、待確認欄位，產生給 A6/A5 的 task packet。\n"
            "下一步：把這段轉給 A6；若要試算表連結，A6/A5 需要走 A5 報價引擎或 GAS/Sheet 權限。"
        )

    if any(marker in normalized for marker in ads_markers):
        return (
            "P0: 這是投放成效判讀任務。\n"
            "召喚：A3 為主責，讀 Google Ads / Meta Ads 成效、預算、CPC/CPA/ROAS；A2 協作落地頁、SEO/內容與轉換頁問題；A1 負責權限與任務卡寫回。\n"
            "我能先做：列出要抓的欄位與判斷框架，不假裝已登入 Ads Manager。\n"
            "下一步：請 A3 讀近 7/14/30 天 Google Ads + Meta Ads：花費、曝光、點擊、CTR、CPC、轉換、CPA、ROAS，輸出保留/暫停/調整預算與素材下一步。"
        )

    if all(marker in normalized for marker in ("角色", "巡查")) or "任務推進" in normalized:
        return (
            "P0: 這是系統巡查與任務推進，不是單純聊天。\n"
            "召喚：A0 做總調度與優先順序；A1 做系統狀態、task card、cold-start truth source 寫回；各角色只處理自己的下一步。\n"
            "我能先做：把巡查結果分成已完成、卡住、可由 agent 自解、需 Owner 5 分鐘動作，並寫成 task packet。\n"
            "下一步：A0/A1 先讀 CURRENT_STATUS.md、pitfalls.md、task cards，對每個 blocked 項跑三層阻塞審查，再派給 A2/A3/A5/A6/A7。"
        )

    return ""


async def claude_ask_with_fallback(
    chat_id: int,
    user_message: str,
    system_extra: str = "",
    timeout: int = 600,
) -> ModelAnswer:
    """Use Claude primary, then Hermes only when Claude is unavailable/quota-limited.
    Returns ModelAnswer with .text (display string) and .model (which model answered)."""

    # Sticky cooldown or forced env var: skip Claude entirely this request
    if _truthy_env("MAPLAB_FORCE_HERMES_FALLBACK") or _switch.should_skip_claude():
        if _truthy_env("MAPLAB_FORCE_HERMES_FALLBACK"):
            skip_reason = "⚠️ Claude 跳過: MAPLAB_FORCE_HERMES_FALLBACK=1"
            skip_kind = "forced"
        else:
            skip_reason = "⚠️ Claude 跳過: Hermes 冷卻中（quota/rate_limit/auth 失敗後自動切）"
            skip_kind = "sticky_hermes"
        claude_result = ModelResult(
            ok=False,
            answer=skip_reason,
            failure_kind=skip_kind,
            stderr=skip_kind,
        )
    else:
        claude_result = await _claude_ask_raw(chat_id, user_message, system_extra, timeout)

    if claude_result.ok:
        answer = _sanitize_for_telegram(claude_result.answer)
        labeled = f"🟢 [Claude]\n{answer}"
        _record_history(chat_id, user_message, labeled)
        return ModelAnswer(text=labeled, model="Claude")

    # Record failure for sticky cooldown (only triggers on quota/rate_limit/auth)
    _switch.mark_claude_failure(claude_result.failure_kind)

    if not _hermes_fallback_enabled() or not _should_fallback_to_hermes(claude_result):
        return ModelAnswer(text=claude_result.answer, model="Claude", failure_kind=claude_result.failure_kind)

    hermes_answer = await hermes_ask(
        chat_id,
        user_message,
        system_extra=system_extra,
        fallback_reason=claude_result.answer,
    )
    if hermes_answer.startswith("⚠️"):
        text = f"{claude_result.answer}\n\n{hermes_answer}"
        return ModelAnswer(text=text, model="Hermes/error", failure_kind=claude_result.failure_kind)

    toolsets = _hermes_toolsets_for_message(user_message)
    answer = f"{_format_hermes_receipt(claude_result.answer, toolsets)}\n\n{hermes_answer}"
    _record_history(chat_id, user_message, answer)
    model_label = f"Hermes/{_hermes_model_label()}"
    return ModelAnswer(text=answer, model=model_label, failure_kind=claude_result.failure_kind)


async def _claude_ask_raw(chat_id: int, user_message: str, system_extra: str = "", timeout: int = 600) -> ModelResult:
    """Call claude -p and return a structured result without mutating history."""

    history = _get_history(chat_id)

    # Build prompt with history + current message
    parts = [ANTHROPIC_SYSTEM_PROMPT]
    if system_extra:
        parts.append(system_extra)
    if history:
        parts.append("\n【對話記錄】")
        for msg in history:
            role_label = "Owner" if msg["role"] == "user" else "助理"
            parts.append(f"{role_label}：{msg['content']}")
        parts.append("【對話記錄結束】")
    parts.append(f"\nOwner（本次）：{user_message}\n請用繁體中文簡潔回答。")
    full_prompt = "\n".join(parts)

    env = os.environ.copy()
    if CLAUDE_OAUTH_TOKEN:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = CLAUDE_OAUTH_TOKEN
    env["PATH"] = _runtime_path(env.get("PATH", ""))

    try:
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", "--dangerously-skip-permissions",
            full_prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return ModelResult(
                ok=False,
                answer=f"⚠️ Claude 回應超時（{timeout}秒）",
                failure_kind="timeout",
                stderr=f"timeout after {timeout}s",
            )
        if proc.returncode != 0:
            err = stderr.decode(errors="replace").strip()
            out = stdout.decode(errors="replace").strip()
            diagnostic = _trim(err or out or "未知錯誤", 500)
            return ModelResult(
                ok=False,
                answer=f"⚠️ Claude 錯誤: {_trim(diagnostic, 300)}",
                failure_kind=_classify_claude_failure(f"{err}\n{out}"),
                stderr=diagnostic,
            )
        answer = _sanitize_for_telegram(stdout.decode(errors="replace")) or "（Claude 無回應）"
        return ModelResult(ok=True, answer=answer)
    except FileNotFoundError:
        return ModelResult(
            ok=False,
            answer="⚠️ 找不到 claude 命令，請確認已安裝 Claude Code",
            failure_kind="cli_missing",
            stderr="claude command not found",
        )
    except Exception as e:
        err = str(e)
        return ModelResult(
            ok=False,
            answer=f"⚠️ 呼叫 Claude 失敗: {err}",
            failure_kind=_classify_claude_failure(err, "primary_unavailable"),
            stderr=err,
        )


async def claude_ask(chat_id: int, user_message: str, system_extra: str = "", timeout: int = 600) -> str:
    """Call Claude primary and return text. This helper does not invoke Hermes fallback."""
    result = await _claude_ask_raw(chat_id, user_message, system_extra, timeout)
    if result.ok:
        _record_history(chat_id, user_message, result.answer)
    return result.answer


async def _generate_phase_summary(chat_id: int) -> str:
    """Generate a phase summary from current conversation history (one-shot, no history modification)."""
    history = list(_get_history(chat_id))
    if not history:
        return "（無對話記錄）"

    history_text = "\n".join(
        f"{'Owner' if m['role'] == 'user' else '助理'}：{m['content']}"
        for m in history
    )
    prompt = (
        f"{ANTHROPIC_SYSTEM_PROMPT}\n\n"
        "請根據以下對話歷史，產生一份「階段摘要」，格式如下：\n\n"
        "## 本階段完成事項\n（條列）\n\n"
        "## 待辦 / 未完成\n（條列，標注優先級）\n\n"
        "## 重要決策紀錄\n（本階段的重要決定）\n\n"
        "## 接手時需知道的事\n（下個 session 最重要的接續點）\n\n"
        f"【對話記錄】\n{history_text}\n【對話記錄結束】\n\n"
        "請用繁體中文，條列式，簡潔。"
    )

    env = os.environ.copy()
    if CLAUDE_OAUTH_TOKEN:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = CLAUDE_OAUTH_TOKEN
    env["PATH"] = _runtime_path(env.get("PATH", ""))

    try:
        proc = await asyncio.create_subprocess_exec(
            "claude", "-p", "--dangerously-skip-permissions",
            prompt,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        except asyncio.TimeoutError:
            proc.kill()
            return "⚠️ 摘要生成超時（120秒）"
        if proc.returncode != 0:
            err = stderr.decode(errors="replace")[:300].strip()
            return f"⚠️ Claude 錯誤: {err or '未知錯誤'}"
        return stdout.decode(errors="replace").strip() or "（Claude 無回應）"
    except FileNotFoundError:
        return "⚠️ 找不到 claude 命令"
    except Exception as e:
        return f"⚠️ 摘要生成失敗: {e}"


# ── Command Handlers ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    await update.message.reply_text(
        f"🟢 MAPLAB A1 遠端終端 online\n"
        f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Repo: {REPO_PATH}\n\n"
        f"/help — 查看指令列表"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    await update.message.reply_text(
        "📋 *MAPLAB A1 終端指令*\n\n"
        "/status — 系統總覽（CURRENT\\_STATUS.md）\n"
        "/owner — Owner 待處理事項清單\n"
        "/task \\[ID\\] — 查特定任務，例如 /task T\\-A2\\-001\n"
        "/patrol — 最近巡查報告（git log patrol commits）\n"
        "/queue — 待認領任務（TASK\\_QUEUE.md）\n"
        "/agent \\[A1\\-A8\\] — 特定 Agent 狀態\n"
        "/commit — 最近 5 條 git log\n"
        "/blocker — 所有 blocker\n"
        "/refresh — 手動 git pull\n"
        "/ping — 心跳檢查\n"
        "/ask \\[問題\\] — 直接問 Claude（OAuth，免費）\n"
        "/codex\\_dispatch \\[任務\\] — 建立 Codex/OpenClaw 派工包\n"
        "/runtime — 查看 Claude primary / Hermes fallback 狀態\n"
        "/hermes — 強制切換到 Hermes/gemma4 模式\n"
        "/claude — 切回 Claude primary 模式\n"
        "/model — 查看目前使用的模型與切換狀態\n"
        "/reset — 生成本階段摘要+待辦，確認後清除對話記錄\n"
        "/help — 本說明\n\n"
        "💬 直接傳訊息也可以問 Claude\n"
        "每則回覆標示模型：🟢 \\[Claude\\] 或 🟡 Hermes receipt",
        parse_mode="MarkdownV2",
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    uptime = datetime.now() - START_TIME
    h, rem = divmod(int(uptime.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    await update.message.reply_text(
        f"🏓 pong — {datetime.now().strftime('%H:%M:%S')}\n"
        f"Uptime: {h}h {m}m {s}s"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    git_pull_silent()
    content = read_file("CURRENT_STATUS.md")
    # Trim to first 3000 chars if huge
    if len(content) > 3000:
        content = content[:3000] + "\n…（截斷，完整版請開 CURRENT_STATUS.md）"
    await send_long(update, f"📊 *CURRENT_STATUS.md*\n\n{content}")


async def task_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    if not context.args:
        await update.message.reply_text("用法：/task [任務ID]，例如 /task T-A2-001")
        return
    task_id = context.args[0].upper()
    git_pull_silent()

    # Search in handoff/tasks/
    task_file = REPO_PATH / "handoff" / "tasks" / f"{task_id}.md"
    if task_file.exists():
        content = task_file.read_text(encoding="utf-8")
    else:
        # Try searching subdirectories
        matches = list((REPO_PATH / "handoff").rglob(f"{task_id}*.md"))
        if matches:
            content = matches[0].read_text(encoding="utf-8")
        else:
            content = f"⚠️ 找不到任務：{task_id}\n\n可用任務：\n"
            for f in sorted((REPO_PATH / "handoff" / "tasks").glob("*.md")):
                if f.name != "TASK_CARD_TEMPLATE.md":
                    content += f"• {f.stem}\n"

    if len(content) > 3500:
        content = content[:3500] + "\n…（截斷）"
    await send_long(update, f"📋 *{task_id}*\n\n{content}")


async def patrol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    git_pull_silent()
    try:
        result = subprocess.run(
            ["bash", str(REPO_PATH / "scripts" / "patrol.sh")],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip() or result.stderr.strip() or "（patrol.sh 無輸出）"
    except Exception as e:
        output = f"⚠️ patrol.sh 執行失敗：{e}"
    await send_long(update, f"🔍 {output}")


async def queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    git_pull_silent()
    content = read_file("TASK_QUEUE.md")
    # Filter lines with 🔲 (pending)
    lines = content.splitlines()
    pending = [l for l in lines if "🔲" in l or "TASK_QUEUE" in l or l.startswith("#")]
    if pending:
        output = "\n".join(pending)
    else:
        output = content
    if len(output) > 3500:
        output = output[:3500] + "\n…（截斷）"
    await send_long(update, f"📥 *TASK_QUEUE — 待認領*\n\n{output}")


async def agent_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    if not context.args:
        await update.message.reply_text("用法：/agent [A1-A8]，例如 /agent A2")
        return
    agent = context.args[0].upper()
    git_pull_silent()
    content = read_file("CURRENT_STATUS.md")
    lines = content.splitlines()
    # Extract section for this agent
    section_lines = []
    in_section = False
    for line in lines:
        if agent in line and line.startswith("#"):
            in_section = True
        elif in_section and line.startswith("#") and agent not in line:
            in_section = False
        if in_section or agent in line:
            section_lines.append(line)

    output = "\n".join(section_lines[:80]) if section_lines else f"找不到 {agent} 的相關資訊"
    await send_long(update, f"🤖 *{agent} 狀態*\n\n{output}")


async def commit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout.strip() or "（無 commit）"
    except Exception as e:
        output = f"⚠️ git log 失敗：{e}"
    await update.message.reply_text(f"📝 最近 5 commits:\n\n{output}")


async def owner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    git_pull_silent()
    content = read_file("CURRENT_STATUS.md")
    lines = content.splitlines()
    # Extract "Owner Action Required" section
    section_lines = []
    in_section = False
    for line in lines:
        if "Owner Action Required" in line:
            in_section = True
            section_lines.append(line)
        elif in_section:
            if line.startswith("## ") or line.startswith("### "):
                break
            section_lines.append(line)
    output = "\n".join(section_lines).strip() if section_lines else "✅ 目前無 Owner 待處理事項"
    await send_long(update, f"🔴 *Owner Action Required*\n\n{output}")


async def blocker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    git_pull_silent()
    content = read_file("CURRENT_STATUS.md")
    lines = content.splitlines()
    # Find blocker sections
    blocker_lines = []
    in_block = False
    for line in lines:
        low = line.lower()
        if "blocker" in low or "blocked" in low or "🚫" in line or "❌" in line:
            in_block = True
            blocker_lines.append(line)
        elif in_block and line.strip() == "":
            blocker_lines.append("")
            in_block = False
        elif in_block:
            blocker_lines.append(line)

    output = "\n".join(blocker_lines).strip() if blocker_lines else "✅ 目前無 blocker"
    await send_long(update, f"🚫 *Blockers*\n\n{output}")


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    await update.message.reply_text("🔄 執行 git pull --rebase…")
    try:
        result = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = result.stdout.strip() + "\n" + result.stderr.strip()
        await update.message.reply_text(f"✅ 完成:\n{out[:500]}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ 失敗：{e}")


async def runtime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    claude_path = _runtime_which("claude") or "missing"
    hermes_path = _runtime_which("hermes") or "missing"
    force_flag = _truthy_env("MAPLAB_FORCE_HERMES_FALLBACK")
    await update.message.reply_text(
        "🧭 MAPLAB A1 runtime\n"
        f"- primary: Claude CLI (`{claude_path}`)\n"
        f"- fallback: {'enabled' if _hermes_fallback_enabled() else 'disabled'}\n"
        f"- fallback_engine: Hermes CLI (`{hermes_path}`)\n"
        f"- fallback_model: {_hermes_model_label()}\n"
        f"- text_fallback_toolsets: {HERMES_FALLBACK_TOOLSETS or 'none'}\n"
        f"- photo_fallback_toolsets: {os.getenv('HERMES_PHOTO_FALLBACK_TOOLSETS', HERMES_PHOTO_FALLBACK_TOOLSETS) or 'none'}\n"
        f"- override_toolsets: {os.getenv('HERMES_FALLBACK_TOOLSETS', '(not set)')}\n"
        f"- force_fallback_test: {'ON' if force_flag else 'off'}\n"
        "- fallback_trigger: quota/rate_limit/auth/cli_missing/timeout/primary_unavailable only\n"
        "- fallback_allowed_actions: read/draft/smoke/image-analysis only; live computer-control requires confirmation\n"
        "- tuning_note: gemma4 text fallback uses staged prompt + no-tools profile + degraded-output retry; photo fallback uses vision only"
    )


async def hermes_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force all messages to use Hermes/gemma4 (skip Claude entirely)."""
    if not is_owner(update):
        await deny(update)
        return
    _switch.force_hermes()
    model = _hermes_model_label()
    await update.message.reply_text(
        f"🟡 已強制切換到 Hermes/{model} 模式\n"
        "- 所有訊息跳過 Claude，直走 Hermes\n"
        "- /claude 切回 Claude primary\n"
        "- /model 查看目前狀態"
    )


async def claude_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resume Claude primary (clear sticky state and manual override)."""
    if not is_owner(update):
        await deny(update)
        return
    _switch.force_claude()
    await update.message.reply_text(
        "🟢 已切回 Claude primary 模式\n"
        f"- quota/rate_limit/auth 失敗後自動切 Hermes（冷卻 {HERMES_STICKY_COOLDOWN_SECS}s）\n"
        "- /hermes 可手動強制切 Hermes"
    )


async def model_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show or change the active model. /model [name] changes Hermes model in memory."""
    if not is_owner(update):
        await deny(update)
        return
    if context.args:
        new_model = context.args[0]
        os.environ["HERMES_FALLBACK_MODEL"] = new_model
        await update.message.reply_text(
            f"✅ Hermes 模型已改為：{new_model}\n"
            "注意：僅本次執行期間有效，重啟後恢復 .env 設定。"
        )
        return
    model = _hermes_model_label()
    claude_path = _runtime_which("claude") or "missing"
    hermes_path = _runtime_which("hermes") or "missing"
    await update.message.reply_text(
        f"🧭 目前模型狀態\n"
        f"- {_switch.status_line()}\n"
        f"- active_label: {_switch.active_label(model)}\n"
        f"- hermes_model: {model}\n"
        f"- claude_cli: {claude_path}\n"
        f"- hermes_cli: {hermes_path}\n"
        f"- sticky_cooldown_secs: {HERMES_STICKY_COOLDOWN_SECS}\n\n"
        "指令：/hermes 強制 Hermes | /claude 切回 Claude | /model [name] 改 Hermes 模型"
    )


async def _run_claude_background(
    bot,
    chat_id: int,
    user_message: str,
    system_extra: str,
    log_label: str,
    log_user_msg: str,
    reply_prefix: str = "",
) -> None:
    """Background task: call Claude then push result via send_message.

    reply_prefix (optional) is prepended to the outbound text so callers that
    route here as a fallback (e.g. after an A0-session resume attempt fails)
    can stamp an explicit identity label — the bot must never let a one-shot
    fallback answer read as if it came from Fable5/A0 itself.
    """
    async with _claude_semaphore:
        model_answer = await claude_ask_with_fallback(chat_id, user_message, system_extra)
        text = _sanitize_for_telegram(model_answer.text)
        if reply_prefix:
            text = f"{reply_prefix}{text}"
        MAX = 4096
        for i in range(0, len(text), MAX):
            await bot.send_message(chat_id=chat_id, text=text[i:i + MAX])
        log_and_commit(log_user_msg, text, log_label)
        _log_exchange_jsonl(
            REPO_PATH, chat_id, log_user_msg, text,
            model=model_answer.model,
            failure_kind=model_answer.failure_kind or None,
        )


async def _run_claude_guarded(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_message: str,
    system_extra: str,
    log_label: str,
    log_user_msg: str,
    reply_prefix: str = "",
) -> None:
    """Reply immediately, then run Claude in background. Reports busy if semaphore is taken."""
    if _claude_semaphore.locked():
        await update.message.reply_text("⏳ Bot 正在處理上一則訊息，請稍候再試。")
        return
    await update.message.reply_text("⏳ 處理中…")
    asyncio.create_task(
        _run_claude_background(
            context.bot, chat_id, user_message, system_extra, log_label, log_user_msg, reply_prefix
        )
    )


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Two-step phase reset: generate summary → confirm → save file + clear history.

    Usage:
        /reset          — generate and show phase summary + todos
        /reset confirm  — save summary to file and clear conversation history
        /reset cancel   — cancel pending reset
    """
    if not is_owner(update):
        await deny(update)
        return
    chat_id = update.effective_chat.id
    arg = context.args[0].lower() if context.args else ""

    # Step: cancel
    if arg == "cancel":
        if chat_id in _pending_reset:
            _pending_reset.pop(chat_id)
            await update.message.reply_text("↩️ 已取消 /reset")
        else:
            await update.message.reply_text("目前沒有待確認的 /reset")
        return

    # Step 2: confirm → save + clear
    if arg == "confirm":
        if chat_id not in _pending_reset:
            await update.message.reply_text("⚠️ 沒有待確認的摘要，請先執行 /reset")
            return
        summary = _pending_reset.pop(chat_id)
        TELEGRAM_LOG_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        ts_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        summary_file = TELEGRAM_LOG_DIR / f"phase-summary-{ts_str}.md"
        header = f"# Phase Summary — {today}\n\n> /reset 執行時自動產生\n\n"
        summary_file.write_text(header + summary, encoding="utf-8")
        # Clear history
        if chat_id in _conv_history:
            _conv_history[chat_id].clear()
        _save_conv_history()
        # Git commit in background
        rel_path = f"data/telegram-logs/phase-summary-{ts_str}.md"
        def _commit_summary():
            try:
                subprocess.run(["git", "add", rel_path], cwd=REPO_PATH, capture_output=True, timeout=10)
                subprocess.run(
                    ["git", "commit", "-m", f"log(phase-reset): {today} 階段摘要存檔"],
                    cwd=REPO_PATH, capture_output=True, timeout=15,
                )
                subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, timeout=30)
            except Exception as e:
                logger.warning(f"git commit phase-summary failed: {e}")
        threading.Thread(target=_commit_summary, daemon=True).start()
        await update.message.reply_text(
            f"✅ 階段摘要已存檔：{summary_file.name}\n"
            "對話記錄已清除，新階段開始。"
        )
        return

    # Step 1: generate summary
    history = list(_get_history(chat_id))
    if not history:
        await update.message.reply_text("目前沒有對話記錄可以摘要。")
        return
    if _claude_semaphore.locked():
        await update.message.reply_text("⏳ Bot 正在處理其他訊息，請稍候再試。")
        return

    await update.message.reply_text("⏳ 生成階段摘要中，請稍候…")

    async def _do_summary():
        async with _claude_semaphore:
            summary = await _generate_phase_summary(chat_id)
            _pending_reset[chat_id] = summary
            MAX = 4096
            for i in range(0, len(summary), MAX):
                await context.bot.send_message(chat_id=chat_id, text=summary[i:i + MAX])
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    "─────────────────\n"
                    "以上是本階段摘要與待辦。\n\n"
                    "✅ 確認存檔並清除記錄：/reset confirm\n"
                    "❌ 取消：/reset cancel"
                ),
            )

    asyncio.create_task(_do_summary())


async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    if not context.args:
        await update.message.reply_text("用法：/ask [問題]，例如 /ask A2 現在在做什麼？")
        return
    prompt = " ".join(context.args)
    chat_id = update.effective_chat.id
    await _run_claude_guarded(update, context, chat_id, prompt, "", "/ask", prompt)


async def codex_dispatch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    if not context.args:
        await update.message.reply_text("用法：/codex_dispatch [任務]，例如 /codex_dispatch 請 A3 判讀近 7/14/30 天廣告成效")
        return

    text = " ".join(context.args)
    chat_id = update.effective_chat.id
    context_text = _latest_telegram_log_snippet(limit=3500)
    try:
        packet = _write_dispatch_packet(text, context_text)
    except ValueError:
        route = _dispatch_catalog()["generic"]
        packet = _write_dispatch_packet(text, context_text, route=route)
    receipt = _dispatch_receipt(packet)
    await update.message.reply_text(receipt)
    _record_history(chat_id, text, receipt)
    log_and_commit(text, receipt, "codex-dispatch")
    asyncio.create_task(_run_openclaw_dispatch_background(context.bot, chat_id, packet))


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages: download image and pass to Claude Code for analysis."""
    if not is_owner(update):
        await deny(update)
        return
    git_pull_silent()

    # Download the largest photo resolution
    photo = update.message.photo[-1]  # last = highest resolution
    photo_file = await context.bot.get_file(photo.file_id)
    TELEGRAM_PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(photo_file.file_path or "photo.jpg").suffix or ".jpg"
    local_path = TELEGRAM_PHOTO_DIR / f"{ts}_{photo.file_unique_id}{file_ext}"
    await photo_file.download_to_drive(str(local_path))
    logger.info(f"Photo saved: {local_path}")

    # Caption = user's text alongside the photo (if any)
    caption = update.message.caption or ""
    caption_note = f"\nOwner 附的文字說明：{caption}" if caption else ""

    try:
        status_snippet = read_file("CURRENT_STATUS.md")[:1500]
    except Exception:
        status_snippet = ""
    system_extra = (
        "以下是目前 MAPLAB 專案狀態摘要（供參考）：\n\n"
        f"{status_snippet}"
    )

    user_message = (
        f"Owner 傳了一張圖片，已存在 {local_path}，請用 Read 工具讀取並分析圖片內容。{caption_note}\n"
        f"根據圖片內容和 Owner 的說明來回應。如果是品項照片，協助辨識品名和用途。"
    )
    log_msg = f"[📷 圖片] {caption}" if caption else "[📷 圖片]"
    chat_id = update.effective_chat.id
    await _run_claude_guarded(update, context, chat_id, user_message, system_extra, "photo", log_msg)


A0_INBOX_FILE = Path(
    os.getenv(
        "A0_INBOX_FILE",
        "/Users/pagemacmini/claude-daily-operations/state/a0_inbox.jsonl",
    )
)


def _a0_inbox_append(chat_id: int, text: str, message_id: Optional[int] = None, source: Optional[str] = None) -> str:
    """Append-only tap for the A0 dispatch window; must never break the bot.

    Returns the "ts" string written for this entry (even if the write
    itself failed) so callers can use the exact same value as
    reply_to_inbox_ts when correlating a later receipt in A0_REPLIES_FILE —
    see scripts/a0_reply.sh and _a0_has_replied_for().

    `source` (Owner 2026-08-24): callers tapping a Stock Discussion Group
    message pass source="group" so A0 can see the entry has a negative
    chat_id (see handle_group_message) without it ever being routed through
    the offline resume/relay path — that path is guarded separately by
    chat_id<0 checks in _a0_resume_or_fallback/_a0_wait_then_maybe_resume.
    """
    ts = datetime.now().isoformat(timespec="seconds")
    try:
        A0_INBOX_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {"ts": ts, "chat_id": chat_id, "text": text[:4000]}
        if message_id is not None:
            entry["message_id"] = message_id
        if source is not None:
            entry["source"] = source
        with A0_INBOX_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        logger.exception("a0 inbox append failed")
    return ts


def _is_a0_direct(text: str) -> bool:
    return bool(re.match(r"^\s*@?[Aa]0\b", text))


A0_HEARTBEAT_FILE = Path(
    os.getenv(
        "A0_HEARTBEAT_FILE",
        "/Users/pagemacmini/claude-daily-operations/state/a0_heartbeat.json",
    )
)
A0_ALIVE_MAX_AGE_S = int(os.getenv("A0_ALIVE_MAX_AGE_S", "180"))


def _a0_alive() -> bool:
    """True when the Fable5 A0 window has written a heartbeat recently."""
    try:
        age = datetime.now().timestamp() - A0_HEARTBEAT_FILE.stat().st_mtime
        return age <= A0_ALIVE_MAX_AGE_S
    except Exception:
        return False


# ── A0/Fable5 offline notice (Owner 2026-08-23 14:15 + 14:53) ───────────────
#
# Owner ruling: "新 context 不是人物代碼而是問題" — the problem was never
# which persona label the offline path used, it was that the bot kept
# spinning up brand-new Fable5 contexts. Priority is avoiding that next time,
# not decorating it. While A0 looks offline the bot must not generate any
# new-context Fable5 persona at all; it queues silently and continues the
# *same* session. The one thing Owner still wants to see is a single,
# non-Fable5 notice per outage — not one per queued message — telling them
# the bot noticed A0 is down and is queuing/continuing, not answering as
# Fable5 itself.

A0_OUTAGE_NOTICE_FILE = Path(
    os.getenv(
        "A0_OUTAGE_NOTICE_FILE",
        "/Users/pagemacmini/claude-daily-operations/state/a0_outage_notice.json",
    )
)
A0_OUTAGE_NOTICE_LABEL = "【bot 通知，非 Fable5】"
A0_RESUME_FAILED_NOTICE_LABEL = "【bot 通知，非 Fable5】"


def _a0_outage_key() -> str:
    """Identifies "this outage period": the mtime of the last heartbeat A0
    actually wrote. Stable for as long as A0 stays offline (the heartbeat
    file doesn't change while nobody is writing it) and automatically
    becomes a new value the moment A0 comes back and writes a fresh
    heartbeat — so a stale notice-state entry can never be mistaken for the
    current outage. Missing heartbeat file entirely still yields a stable
    (if degenerate) key so notice-once behaviour still holds."""
    try:
        return str(A0_HEARTBEAT_FILE.stat().st_mtime)
    except Exception:
        return "no-heartbeat-file"


def _a0_outage_heartbeat_hhmm() -> str:
    """HH:MM of the last A0 heartbeat, for the outage notice text. Never
    raises — falls back to "?" when the heartbeat file is missing/unreadable."""
    try:
        return datetime.fromtimestamp(A0_HEARTBEAT_FILE.stat().st_mtime).strftime("%H:%M")
    except Exception:
        return "?"


def _a0_read_outage_notice_state() -> dict:
    try:
        return json.loads(A0_OUTAGE_NOTICE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _a0_write_outage_notice_state(state: dict) -> None:
    try:
        A0_OUTAGE_NOTICE_FILE.parent.mkdir(parents=True, exist_ok=True)
        A0_OUTAGE_NOTICE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    except Exception:
        logger.exception("a0 outage notice state write failed")


def _a0_clear_outage_notice_state() -> None:
    """Called once A0 is confirmed alive again, so the next outage starts
    from a clean slate instead of inheriting stale notified/failed flags."""
    try:
        if A0_OUTAGE_NOTICE_FILE.exists():
            A0_OUTAGE_NOTICE_FILE.unlink()
    except Exception:
        logger.exception("a0 outage notice state clear failed")


async def _a0_maybe_notify_outage(bot, chat_id: int) -> None:
    """Send the "A0 is offline, your message is queued and being handled via
    the same session" notice — but only once per outage period. Every
    subsequent message during the same outage just silently bumps the queued
    count in state; Owner explicitly asked for no repeat noise ("之後同一
    離線期內的訊息不再重複通知，只靜默排隊+續接"). Never raises."""
    key = _a0_outage_key()
    state = _a0_read_outage_notice_state()
    queued = int(state.get("queued", 0)) + 1 if state.get("key") == key else 1
    already_notified = state.get("key") == key and state.get("notified")
    state = {"key": key, "notified": True, "queued": queued, "failed_notified": state.get("failed_notified") if state.get("key") == key else False}
    _a0_write_outage_notice_state(state)
    if already_notified:
        return
    hhmm = _a0_outage_heartbeat_hhmm()
    text = (
        f"{A0_OUTAGE_NOTICE_LABEL} Fable5 主程式離線（心跳 {hhmm} 起），"
        f"你的訊息已排隊 {queued} 則，正以同一 session 續接，需數分鐘。"
    )
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception:
        logger.exception("a0 outage notice send failed")


async def _a0_maybe_notify_resume_failed(bot, chat_id: int) -> None:
    """Same once-per-outage discipline as _a0_maybe_notify_outage, but for
    the "the same-session resume itself came back empty/failed" case (Owner
    2026-08-23: 續接結果若為空/失敗 → 不代答，只在 log 記錄，並每離線期一次
    補一句通知). Never raises."""
    key = _a0_outage_key()
    state = _a0_read_outage_notice_state()
    already_notified = state.get("key") == key and state.get("failed_notified")
    state = dict(state) if state.get("key") == key else {}
    state["key"] = key
    state["failed_notified"] = True
    _a0_write_outage_notice_state(state)
    if already_notified:
        return
    text = f"{A0_RESUME_FAILED_NOTICE_LABEL} 續接失敗，訊息仍排隊，待主程式喚醒。"
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception:
        logger.exception("a0 resume-failed notice send failed")


# ── A0/Fable5 session resume (Owner 2026-08-22 21:32 + 21:37) ───────────────
#
# 21:32: a heartbeat-triggered stateless one-shot fallback has no prior
# context, so it's useless — "切了沒前文的模型沒意義". When A0 looks offline
# (or Owner forces it with a leading "代答"), the bot must headlessly RESUME
# A0's own Claude Code session (`claude -p --resume <session_id>`) instead of
# starting a fresh one-shot, and every outbound reply must say plainly
# whether it is Fable5 (resumed) or not (bot fallback).
#
# 21:37 follow-up: an immediate "📨 已收到" ack while A0 is alive reads as
# noise ("ack 被視為洗板"). The bot now stays silent while A0 looks alive and
# gives it up to A0_WAIT_TIMEOUT_S to actually answer via its own reply
# channel (scripts/a0_reply.sh, which appends a receipt to A0_REPLIES_FILE).
# No receipt by the deadline ⇒ A0 didn't actually pick the message up, so the
# bot resumes A0's session itself.

A0_SESSION_FILE = Path(
    os.getenv(
        "A0_SESSION_FILE",
        "/Users/pagemacmini/claude-daily-operations/state/a0_session.json",
    )
)
A0_SESSION_ID_DEFAULT = os.getenv("A0_SESSION_ID", "3a3df70f-b5ce-4c45-9d85-6651d7022e4b")
A0_RESUME_MODEL_DEFAULT = os.getenv("A0_RESUME_MODEL", "claude-fable-5")
A0_RESUME_CWD = os.getenv("A0_RESUME_CWD", "/Users/pagemacmini/Documents")
A0_RESUME_TIMEOUT_S = int(os.getenv("A0_RESUME_TIMEOUT_S", "900"))

A0_REPLIES_FILE = Path(
    os.getenv(
        "A0_REPLIES_FILE",
        "/Users/pagemacmini/claude-daily-operations/state/a0_replies.jsonl",
    )
)
A0_WAIT_TIMEOUT_S = float(os.getenv("A0_WAIT_TIMEOUT_S", "150"))
A0_WAIT_POLL_INTERVAL_S = float(os.getenv("A0_WAIT_POLL_INTERVAL_S", "5"))

A0_RESUME_LABEL = "【Fable5 本人・同 session 續接】"
BOT_FALLBACK_LABEL = "【bot 代答，非 Fable5】"

# ── A0/Fable5 fresh-context relay (Owner 22:35 2026-08-22) ──────────────────
#
# VERIFIED 22:32: `claude -p --resume <session>` was timing out at 180s
# because that session's context sits at ~98% — every resume has to reload a
# huge amount of prior transcript before it can even start answering. Owner
# 22:35: "想清楚後派工給 codex 幫助你" → fix is a fresh-context relay that
# takes the place of resume as the *default* routing: instead of resuming the
# near-full session, spin up a brand-new one-shot `claude -p` call whose
# system prompt is assembled from FABLE5_HANDOFF.md's RESUME PROMPT section +
# standing memory + the most recent inbox/reply exchanges — cheap to load,
# and enough for a genuinely fresh Fable5 context to answer sensibly (or say
# "不知道") without pretending it has the old session's live working memory.
#
# `--resume` is kept as an opt-in via A0_RELAY_MODE=resume for cases where
# the live session actually is healthy and worth reconnecting to.
#
# ── REVERSED — Owner ruling 2026-08-23 14:15 + 14:53 ────────────────────────
#
# "新 context 不是人物代碼而是問題" — the fresh-context relay above is exactly
# the "new Fable5 persona" Owner wants stopped by default: offline handling
# must not synthesize a brand-new context that speaks as Fable5. Default
# routing flips back to `resume` (the SAME live session, not a new one) —
# the 22:35 timeout concern is addressed instead by raising
# A0_RESUME_TIMEOUT_S (180 → 900) rather than by inventing a new persona.
# The fresh-context relay path stays in the code (still selectable) but is
# opt-in ONLY: it fires solely when A0_RELAY_MODE is explicitly set to
# "fresh" in the environment, and doing so logs a warning every time. Any
# other value (unset, "resume", or anything else) uses resume — the default
# must never silently reach the fresh path.

A0_RELAY_MODE = os.getenv("A0_RELAY_MODE", "resume").strip().lower()  # "resume" (default) | "fresh" (explicit opt-in only, warns)
A0_FRESH_RELAY_TIMEOUT_S = int(os.getenv("A0_FRESH_RELAY_TIMEOUT_S", "120"))

FABLE5_HANDOFF_FILE = Path(
    os.getenv(
        "FABLE5_HANDOFF_FILE",
        "/Users/pagemacmini/claude-daily-operations/state/FABLE5_HANDOFF.md",
    )
)
FABLE5_HANDOFF_HEAD_LINES = int(os.getenv("FABLE5_HANDOFF_HEAD_LINES", "40"))
FABLE5_MEMORY_DIR = Path(
    os.getenv(
        "FABLE5_MEMORY_DIR",
        "/Users/pagemacmini/.claude/projects/-Users-pagemacmini-Documents/memory",
    )
)
FABLE5_MEMORY_FILES = (
    "owner-communication-standard.md",
    "fable5-standing-mandate-20260822.md",
)
A0_RECENT_EXCHANGE_COUNT = int(os.getenv("A0_RECENT_EXCHANGE_COUNT", "10"))

A0_FRESH_RELAY_LABEL = "【Fable5 本人(新 context)】"


def _read_head_lines(path: Path, n: int) -> str:
    """First n lines of path; never raises — missing/unreadable file → ""."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[:n])
    except Exception:
        return ""


def _read_tail_lines(path: Path, n: int) -> str:
    """Last n non-blank lines of path; never raises — "" on any failure."""
    try:
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        return "\n".join(lines[-n:])
    except Exception:
        return ""


def _read_fable5_memory_files() -> str:
    """Full text of the standing-mandate / communication-standard memory
    files, concatenated with headers. Missing individual files are skipped
    silently (never raises)."""
    parts = []
    for name in FABLE5_MEMORY_FILES:
        try:
            content = (FABLE5_MEMORY_DIR / name).read_text(encoding="utf-8")
        except Exception:
            continue
        parts.append(f"### {name}\n{content}")
    return "\n\n".join(parts)


def _a0_fresh_relay_system_prompt() -> str:
    """Assemble the system prompt for the fresh-context Fable5 relay:
    FABLE5_HANDOFF.md's RESUME PROMPT header + standing memory + the most
    recent inbox/reply exchanges, so a brand-new one-shot session has enough
    to answer like Fable5 without resuming the near-full live session."""
    handoff = _read_head_lines(FABLE5_HANDOFF_FILE, FABLE5_HANDOFF_HEAD_LINES)
    memory = _read_fable5_memory_files()
    recent_inbox = _read_tail_lines(A0_INBOX_FILE, A0_RECENT_EXCHANGE_COUNT)
    recent_replies = _read_tail_lines(A0_REPLIES_FILE, A0_RECENT_EXCHANGE_COUNT)
    return (
        "=== FABLE5_HANDOFF.md（前"
        f"{FABLE5_HANDOFF_HEAD_LINES}行，含 RESUME PROMPT）===\n"
        f"{handoff}\n\n"
        "=== memory 索引全文（owner-communication-standard, "
        "fable5-standing-mandate-20260822）===\n"
        f"{memory}\n\n"
        f"=== 最近 {A0_RECENT_EXCHANGE_COUNT} 則 a0_inbox（Owner 訊息）===\n"
        f"{recent_inbox}\n\n"
        f"=== 最近 {A0_RECENT_EXCHANGE_COUNT} 則 a0_replies（Fable5 回覆收據）===\n"
        f"{recent_replies}\n\n"
        "=== 指令 ===\n"
        "你是 Fable5 本人（全新 context，沒有先前 session 的記憶，只有以上摘要可用）。"
        "用說人話三段式回 Owner（發生什麼／對你的意義／要不要你做）；不知道就說不知道；"
        "不要宣稱已派工或已稽核；回覆開頭必須標「【Fable5 本人(新 context)】」。"
    )


async def _a0_fresh_relay_ask(user_message: str, timeout: int = A0_FRESH_RELAY_TIMEOUT_S) -> ModelResult:
    """Default A0 routing since 2026-08-22 22:35: a fresh-context one-shot
    Claude session (not a `--resume` of the near-full live session) primed
    with FABLE5_HANDOFF.md + standing memory + recent inbox/replies via
    --system-prompt (falling back to prepending the prompt inline if this
    CLI build rejects the flag). Never raises — failures come back as
    ModelResult(ok=False, ...) so the caller can fall back further."""
    system_prompt = _a0_fresh_relay_system_prompt()
    _, model = _a0_session_config()
    model = model or A0_RESUME_MODEL_DEFAULT

    env = os.environ.copy()
    if CLAUDE_OAUTH_TOKEN:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = CLAUDE_OAUTH_TOKEN
    env["PATH"] = _runtime_path(env.get("PATH", ""))

    def _build_cmd(inline_system: bool) -> list:
        cmd = ["claude", "-p", "--output-format", "text"]
        if model:
            cmd += ["--model", model]
        if inline_system:
            cmd.append(f"{system_prompt}\n\n=== Owner 訊息 ===\n{user_message}")
        else:
            cmd += ["--system-prompt", system_prompt, user_message]
        return cmd

    async def _run(cmd):
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=A0_RESUME_CWD,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            return proc, await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            # Codex route-A minimal fix: asyncio.wait_for() only abandons
            # the communicate() *read*, it does not touch the child process
            # — without an explicit kill()+wait() here the subprocess kept
            # running as an orphan and its output (if it ever finished)
            # could not be told apart from a fresh attempt's output. Kill
            # and reap it here, inside _run(), while `proc` is still in
            # scope, then re-raise so the caller's existing TimeoutError
            # handling builds the ModelResult. Late output from this
            # process is never read again, so it can never be sent.
            proc.kill()
            await proc.wait()
            raise

    try:
        try:
            proc, (stdout, stderr) = await _run(_build_cmd(inline_system=False))
        except asyncio.TimeoutError:
            return ModelResult(
                ok=False,
                answer=f"⚠️ Fable5 fresh relay 逾時（{timeout}秒）",
                failure_kind="timeout",
                stderr=f"timeout after {timeout}s",
            )

        err = stderr.decode(errors="replace").strip()
        if proc.returncode != 0 and re.search(r"unknown option|unrecognized option", err, re.IGNORECASE):
            # This CLI build doesn't accept --system-prompt; retry with the
            # prompt folded into the message instead of failing outright.
            try:
                proc, (stdout, stderr) = await _run(_build_cmd(inline_system=True))
            except asyncio.TimeoutError:
                return ModelResult(
                    ok=False,
                    answer=f"⚠️ Fable5 fresh relay 逾時（{timeout}秒）",
                    failure_kind="timeout",
                    stderr=f"timeout after {timeout}s",
                )
            err = stderr.decode(errors="replace").strip()

        if proc.returncode != 0:
            out = stdout.decode(errors="replace").strip()
            diagnostic = _trim(err or out or "未知錯誤", 500)
            return ModelResult(
                ok=False,
                answer=f"⚠️ fresh relay 錯誤: {_trim(diagnostic, 300)}",
                failure_kind="fresh_relay_failed",
                stderr=diagnostic,
            )
        answer = _sanitize_for_telegram(stdout.decode(errors="replace"))
        if not answer:
            return ModelResult(
                ok=False, answer="⚠️ fresh relay 無回應（空輸出）",
                failure_kind="fresh_relay_empty", stderr="empty stdout",
            )
        return ModelResult(ok=True, answer=answer)
    except FileNotFoundError:
        return ModelResult(
            ok=False,
            answer="⚠️ 找不到 claude 命令，請確認已安裝 Claude Code",
            failure_kind="cli_missing",
            stderr="claude command not found",
        )
    except Exception as e:
        err = str(e)
        return ModelResult(ok=False, answer=f"⚠️ fresh relay 呼叫失敗: {err}", failure_kind="fresh_relay_error", stderr=err)


def _a0_session_config() -> tuple[str, str]:
    """Resolve (session_id, model) for `claude -p --resume`.

    A0_SESSION_FILE (kept fresh by A0 itself) wins when present and has
    usable fields; otherwise falls back to the A0_SESSION_ID / A0_RESUME_MODEL
    defaults (env-overridable, hardcoded default session id otherwise).
    A missing/corrupt file must never break message handling.
    """
    session_id = A0_SESSION_ID_DEFAULT
    model = A0_RESUME_MODEL_DEFAULT
    try:
        data = json.loads(A0_SESSION_FILE.read_text(encoding="utf-8"))
        file_session = str(data.get("session_id") or "").strip()
        file_model = str(data.get("model") or "").strip()
        if file_session:
            session_id = file_session
        if file_model:
            model = file_model
    except Exception:
        pass
    return session_id, model


def _is_a0_answer_command(text: str) -> bool:
    """Owner prefixes a message with 代答 to force the resume/fallback path
    immediately, without waiting to see whether A0 answers on its own."""
    return bool(re.match(r"^\s*代答", text or ""))


def _a0_has_replied_for(reply_to_inbox_ts: str) -> bool:
    """True when A0_REPLIES_FILE has a receipt *paired* to this exact inbox
    message via its "reply_to_inbox_ts" field (scripts/a0_reply.sh writes
    this — Codex route-A minimal fix, 2026-08-22).

    Previously this only checked receipt.ts >= since_ts, which is coarse:
    any receipt written after the message arrived counted, even one that
    was actually answering a *different*, later Owner message that happened
    to get a fast reply first. Matching on the paired reply_to_inbox_ts
    instead means a receipt only counts for the inbox message it actually
    answered. Receipts without a reply_to_inbox_ts field (legacy format)
    never match — never raises: a missing/corrupt file just means "no
    receipt yet".
    """
    if not reply_to_inbox_ts:
        return False
    try:
        if not A0_REPLIES_FILE.exists():
            return False
        lines = A0_REPLIES_FILE.read_text(encoding="utf-8").splitlines()
        for line in reversed(lines[-200:]):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("reply_to_inbox_ts") == reply_to_inbox_ts:
                return True
        return False
    except Exception:
        return False


A0_HANDLED_DIR = Path(
    os.getenv(
        "A0_HANDLED_DIR",
        "/Users/pagemacmini/claude-daily-operations/state/a0_handled",
    )
)


def _a0_claim_single_reply(reply_to_inbox_ts: str, chat_id: int) -> bool:
    """Atomically claim the right to auto-answer one inbox message, so the
    bot never sends two automatic replies (fresh-relay/resume/fallback) for
    the same Owner message — Codex route-A minimal fix, 2026-08-22.

    Uses O_CREAT|O_EXCL to create a marker file named after a hash of
    (chat_id, reply_to_inbox_ts); this is safe across concurrent asyncio
    tasks (e.g. the immediate "代答" path racing the wait-timer path for the
    same message) because file creation with O_EXCL is atomic at the OS
    level. Returns True the first time a given message is claimed, False on
    every subsequent attempt for that same message.

    Fails open (returns True) on any filesystem error: this guard's job is
    to prevent *duplicate* replies, not to gate whether Owner gets answered
    at all, so a marker-directory outage must not silently swallow a
    message.
    """
    try:
        A0_HANDLED_DIR.mkdir(parents=True, exist_ok=True)
        key = f"{chat_id}:{reply_to_inbox_ts}"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
        marker = A0_HANDLED_DIR / f"{digest}.claimed"
        fd = os.open(str(marker), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.write(fd, key.encode("utf-8"))
        finally:
            os.close(fd)
        return True
    except FileExistsError:
        return False
    except Exception:
        logger.exception("a0 single-reply claim failed; proceeding anyway")
        return True


# Short "續接開場" prelude prepended to every same-session resume call (Owner
# 2026-08-23 14:15 + 14:53, item 3): tell the resumed session plainly that
# it is the bot continuing A0's own session while A0 itself is offline —
# not a new persona — and what to actually do about it (pull, read the
# handoff's RESUME PROMPT, diff a0_inbox/a0_replies, answer only this one
# message with a receipt) rather than claim work that hasn't happened.
A0_RESUME_PRELUDE = (
    "【續接開場】你是 bot，在 A0/Fable5 主程式離線期間以「同一個」既有 session 續接——"
    "不是開新 context、不是新的 Fable5 人格。請依序：\n"
    "1) 先執行 git pull cdo；\n"
    "2) 讀 handoff 檔案最頂部的 RESUME PROMPT 區段；\n"
    "3) 比對 a0_inbox 與 a0_replies，找出尚未回覆的訊息；\n"
    "4) 只回覆 Owner 這一則訊息（用 scripts/a0_reply.sh 留收據）。\n"
    "回覆開頭必須標「【Fable5 本人・同 session 續接】」；"
    "不得宣稱已派工、已稽核或已完成任何實際上還沒做的事。\n\n"
    "=== Owner 訊息 ===\n"
)


async def _a0_resume_ask(user_message: str, timeout: int = A0_RESUME_TIMEOUT_S) -> ModelResult:
    """Headlessly resume A0's own Claude Code session so the reply keeps full
    context, instead of a stateless one-shot.

    Calls `claude -p --resume <session_id> --output-format text [--model ...]`
    with cwd=A0_RESUME_CWD, prefixed with A0_RESUME_PRELUDE so the resumed
    session knows this is a same-session continuation, not a new context.
    Never raises — failures come back as ModelResult(ok=False, ...) so the
    caller can decide how to handle a failed/empty resume.
    """
    session_id, model = _a0_session_config()
    if not session_id:
        return ModelResult(ok=False, answer="⚠️ 沒有可用的 A0 session id", failure_kind="no_session")

    env = os.environ.copy()
    if CLAUDE_OAUTH_TOKEN:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = CLAUDE_OAUTH_TOKEN
    env["PATH"] = _runtime_path(env.get("PATH", ""))

    cmd = ["claude", "-p", "--resume", session_id, "--output-format", "text"]
    # 2026-08-25 Owner「解決腳本推送問題」: resume 視窗過去沒有任何 permission
    # 旗標，a0_reply.sh 每次都被權限閘攔下，只能靠 bot 轉送最終文字。這裡只放行
    # 三支既有回報腳本（回 Owner 留收據、群組成果回交），其餘命令維持原本閘門。
    # 單一逗號串而非 variadic 多值：--allowedTools 是 variadic 旗標，若用多個
    # 裸值且後面剛好沒有 --model，最後的 prompt 位置參數會被吃進工具清單。
    _a0_reply_allow = ",".join(
        f"Bash({prefix}/Users/pagemacmini/maplab-ai-handbook/scripts/{script}:*)"
        for script in ("a0_reply.sh", "a0_reply_from_file.sh", "notify_group.sh")
        for prefix in ("bash ", "")
    )
    cmd += ["--allowedTools", _a0_reply_allow]
    if model:
        cmd += ["--model", model]
    cmd.append(A0_RESUME_PRELUDE + user_message)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=A0_RESUME_CWD,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            # Codex route-A minimal fix: a bare kill() leaves the child a
            # zombie and leaves its late stdout unread/unbounded — always
            # kill *and* wait() so the subprocess is fully reaped before we
            # give up on it. Late output from this process must never be
            # used; we return here without reading stdout/stderr again.
            proc.kill()
            await proc.wait()
            return ModelResult(
                ok=False,
                answer=f"⚠️ Fable5 session resume 逾時（{timeout}秒）",
                failure_kind="timeout",
                stderr=f"timeout after {timeout}s",
            )
        if proc.returncode != 0:
            err = stderr.decode(errors="replace").strip()
            out = stdout.decode(errors="replace").strip()
            diagnostic = _trim(err or out or "未知錯誤", 500)
            return ModelResult(
                ok=False,
                answer=f"⚠️ resume 錯誤: {_trim(diagnostic, 300)}",
                failure_kind="resume_failed",
                stderr=diagnostic,
            )
        answer = _sanitize_for_telegram(stdout.decode(errors="replace"))
        if not answer:
            return ModelResult(ok=False, answer="⚠️ resume 無回應（空輸出）", failure_kind="resume_empty", stderr="empty stdout")
        return ModelResult(ok=True, answer=answer)
    except FileNotFoundError:
        return ModelResult(
            ok=False,
            answer="⚠️ 找不到 claude 命令，請確認已安裝 Claude Code",
            failure_kind="cli_missing",
            stderr="claude command not found",
        )
    except Exception as e:
        err = str(e)
        return ModelResult(ok=False, answer=f"⚠️ resume 呼叫失敗: {err}", failure_kind="resume_error", stderr=err)


async def _a0_resume_or_fallback(bot, chat_id: int, text: str, reply_to_inbox_ts: str = "") -> None:
    """Shared relay chain: try to reach A0/Fable5 first — via a same-session
    resume of A0's own live session by default (A0_RELAY_MODE unset/"resume"),
    or via the fresh-context relay ONLY when A0_RELAY_MODE is explicitly set
    to "fresh" (Owner 2026-08-23 ruling: offline handling must never
    synthesize a new-context Fable5 persona by default). Used both when A0
    looks offline immediately and when the wait timer (see
    _a0_wait_then_maybe_resume) expires with no reply receipt.

    reply_to_inbox_ts identifies which a0_inbox.jsonl entry this automatic
    answer is for. When present, this claims a single-reply marker (Codex
    route-A minimal fix, 2026-08-22) before doing any relay work, so the
    immediate "代答" path and the wait-timer path can never both send an
    automatic answer for the same Owner message — the second claimant just
    logs and returns."""
    if chat_id < 0:
        # Group chat_ids are always negative in Telegram. Group ingress
        # (Stock Discussion Group, see handle_group_message) is dispatched
        # entirely through its own trigger/orchestrator path and must never
        # synthesize an A0/Fable5 "代答" into a group — general group
        # chit-chat stays silent (能力測試 D) and even Owner's own group
        # messages only get a reply when they hit a research/debate trigger.
        # As of 2026-08-24 no caller actually reaches this function with a
        # negative chat_id (handle_group_message never calls it), but this
        # guard is defense-in-depth against any future code path doing so.
        logger.info("A0 relay/fallback skipped for group chat_id=%s (group ingress never auto-answers via A0 relay)", chat_id)
        return
    if reply_to_inbox_ts and not _a0_claim_single_reply(reply_to_inbox_ts, chat_id):
        logger.info("A0 auto-reply already claimed for chat_id=%s reply_to_inbox_ts=%s; skipping duplicate", chat_id, reply_to_inbox_ts)
        return
    # A0 actually looking offline (not just an Owner-forced "代答" while A0 is
    # alive) is what "an outage" means for notice purposes — send the single
    # once-per-outage "queued, continuing on same session" notice here.
    if not _a0_alive():
        await _a0_maybe_notify_outage(bot, chat_id)
    git_pull_silent()
    if A0_RELAY_MODE == "fresh":
        logger.warning(
            "A0_RELAY_MODE=fresh explicitly set — using new-context fresh relay "
            "instead of same-session resume; this path is opt-in only and "
            "never the default (Owner 2026-08-23 ruling)."
        )
        relay_result = await _a0_fresh_relay_ask(text)
        relay_label = A0_FRESH_RELAY_LABEL
        relay_log_label = "a0-fresh-relay"
    else:
        relay_result = await _a0_resume_ask(text)
        relay_label = A0_RESUME_LABEL
        relay_log_label = "a0-resume"
    if relay_result.ok:
        answer = _sanitize_for_telegram(f"{relay_label}\n{relay_result.answer}")
        MAX = 4096
        for i in range(0, len(answer), MAX):
            await bot.send_message(chat_id=chat_id, text=answer[i:i + MAX])
        _record_history(chat_id, text, answer)
        log_and_commit(text, answer, relay_log_label)
        return

    logger.warning("A0 relay failed (%s, mode=%s): %s", relay_result.failure_kind, A0_RELAY_MODE, relay_result.stderr)

    if A0_RELAY_MODE != "fresh":
        # Same-session resume (the default path): Owner 2026-08-23 item 3 —
        # an empty/failed resume must never be papered over with a bot
        # one-shot answer standing in for Fable5. Just log it and, once per
        # outage, tell Owner the message is still queued.
        await _a0_maybe_notify_resume_failed(bot, chat_id)
        return

    # Fresh-context relay (explicit opt-in only) failing still falls back to
    # a clearly-labelled one-shot bot answer, as before opt-in was required.
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "⚠️ Fable5 fresh-context relay 失敗，訊息已存入 A0 inbox 待其上線處理。\n"
                "以下為 bot 一次性代答（非 Fable5 本人，不含派工）："
            ),
        )
    except Exception:
        logger.exception("offline notice failed")
    try:
        status_snippet = read_file("CURRENT_STATUS.md")[:1500]
    except Exception:
        status_snippet = ""
    system_extra = (
        "你是 bot 的一次性代答模型，不是 Fable5/A0 本人；不得自稱 Fable5、"
        "不得宣稱已派工或已稽核。以下是目前 MAPLAB 專案狀態摘要（供參考）：\n\n"
        f"{status_snippet}"
    )
    await _run_claude_background(
        bot, chat_id, text, system_extra, "bot-fallback", text,
        reply_prefix=f"{BOT_FALLBACK_LABEL}\n",
    )


async def _a0_wait_then_maybe_resume(bot, chat_id: int, text: str, reply_to_inbox_ts: str) -> None:
    """A0 looked alive, so stay silent (no ack) and give it up to
    A0_WAIT_TIMEOUT_S to actually answer through scripts/a0_reply.sh. If no
    receipt paired to reply_to_inbox_ts shows up in A0_REPLIES_FILE by the
    deadline, treat A0 as having missed the message and resume its session
    headlessly."""
    if chat_id < 0:
        # Same group-chat_id guard as _a0_resume_or_fallback — see that
        # function's docstring. No caller reaches this with a negative
        # chat_id as of 2026-08-24; defense-in-depth only.
        logger.info("A0 wait-then-resume skipped for group chat_id=%s", chat_id)
        return
    loop = asyncio.get_event_loop()
    deadline = loop.time() + A0_WAIT_TIMEOUT_S
    poll = max(A0_WAIT_POLL_INTERVAL_S, 0.01)
    while loop.time() < deadline:
        if _a0_has_replied_for(reply_to_inbox_ts):
            return
        await asyncio.sleep(min(poll, max(deadline - loop.time(), 0)))
    if _a0_has_replied_for(reply_to_inbox_ts):
        return
    await _a0_resume_or_fallback(bot, chat_id, text, reply_to_inbox_ts)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Group/supergroup messages are routed to handle_group_message (registered
    # before this handler — see main()) and must never reach the private-chat
    # deny()/A0-relay flow below, even if handler registration order ever
    # changes: deny() replying "⛔ 未授權" into a group would violate 能力測試
    # D's "一般群聊保持靜默" ruling. Defense-in-depth only as of 2026-08-24.
    if getattr(update.effective_chat, "type", None) in ("group", "supergroup"):
        return
    if not is_owner(update):
        await deny(update)
        return
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    message_id = getattr(update.message, "message_id", None)
    reply_to_inbox_ts = _a0_inbox_append(chat_id, text, message_id)

    # 2026-08-22 (Owner decision, TELEGRAM_ROUTING.md): this bot is the
    # Fable5 finance working-meeting line. Every Owner message goes to the
    # A0/Fable5 window when it is alive. The keyword dispatch classifier
    # (quote-intake / ads-performance-review / OpenClaw packets) is OFF on
    # this line — Owner: "派工是無用那請把它關掉", "不要自己幫我報價".
    # Explicit slash commands (/codex_dispatch etc.) are unaffected.
    #
    # See the "A0/Fable5 session resume" block above for the 21:32 + 21:37
    # decisions this routing implements: no ack noise while A0 is alive, a
    # bounded silent wait for A0's own reply receipt, and a context-preserving
    # session resume (not a stateless one-shot) whenever the bot has to step
    # in — unless Owner forces an immediate answer with a "代答" prefix.
    force_answer_now = _is_a0_answer_command(text)
    a0_is_alive = _a0_alive()
    if a0_is_alive:
        # Heartbeat is fresh again ⇒ any prior outage is over. Clear the
        # once-per-outage notice state so the *next* outage gets its own
        # fresh notice instead of silently reusing a stale "already
        # notified" flag (Owner 2026-08-23: 心跳恢復後清除).
        _a0_clear_outage_notice_state()

    if a0_is_alive and not force_answer_now:
        asyncio.create_task(_a0_wait_then_maybe_resume(context.bot, chat_id, text, reply_to_inbox_ts))
        return

    if not force_answer_now:
        local_answer = _local_runtime_question_answer(text)
        if local_answer:
            await update.message.reply_text(local_answer)
            _record_history(chat_id, text, local_answer)
            log_and_commit(text, local_answer, "runtime-local")
            return

    # A0 offline (or Owner forced an immediate answer): resume A0's own
    # session so the reply keeps full context; fall back to a clearly
    # labelled one-shot only if the resume itself fails.
    await _a0_resume_or_fallback(context.bot, chat_id, text, reply_to_inbox_ts)



async def on_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """2026-08-24: bot 被拉進/踢出群組時,記 log 並落 A0 inbox(含群組 chat_id),
    讓 A0/Fable5 知道討論群入口在哪。不回覆群組、不做其他事。"""
    cm = update.my_chat_member
    if cm is None:
        return
    chat = cm.chat
    status = cm.new_chat_member.status if cm.new_chat_member else "?"
    by = cm.from_user.id if cm.from_user else "?"
    title = getattr(chat, "title", None) or ""
    logger.info(f"my_chat_member: chat={chat.id} type={chat.type} title={title!r} status={status} by={by}")
    try:
        _a0_inbox_append(chat.id, f"[群組事件] bot 在 {chat.type} '{title}' 狀態→{status}(操作者 {by})", None)
    except Exception as e:  # pragma: no cover
        logger.warning(f"my_chat_member inbox append failed: {e}")


# ── Stock Discussion Group ingress (Owner 2026-08-24) ───────────────────────────
#
# The bot is already a member of group chat_id -5589898264 and receives
# Owner's own messages there (bots never see other bots' messages — see
# claude-daily-operations/state/a0_groups.json). Owner's ruling from 能力測試
# D: general group chit-chat must stay completely silent; only Owner's own
# messages starting with 研調:/研調：/辯論:/辯論：/討論:/討論： (optionally after an
# @bot mention) trigger anything, and everything else — including any
# message from a non-Owner group member — gets no reply at all, not even
# deny(). On trigger, this spawns investment-os's
# scripts/run_stock_discussion.py as a background subprocess (never blocks
# the polling loop) and always follows the ack with either a summary or a
# one-line failure — never silent after acking.

_GROUP_TRIGGER_KEYWORDS = ("研調", "辯論", "討論")
_GROUP_TRIGGER_RE = re.compile(r"^(研調|辯論|討論)[:：]\s*(.*)$", re.DOTALL)
_GROUP_MENTION_RE = re.compile(
    rf"^\s*@{re.escape(STOCK_DISCUSSION_GROUP_BOT_USERNAME)}\b\s*", re.IGNORECASE
)
# 討論 is treated as a plain-language alias for 研調 (research mode); 辯論 is
# the only trigger that maps to debate mode. The ack line only ever shows
# "開工(研調)" or "開工(辯論)" per this task's spec — 討論 shows as 研調.
_GROUP_TRIGGER_MODE = {"研調": "research", "討論": "research", "辯論": "debate"}
_GROUP_MODE_ACK_LABEL = {"research": "研調", "debate": "辯論"}

# In-process concurrency guard + reply-to-summary follow-up tracking. Both
# are best-effort, in-memory, reset on bot restart — acceptable because the
# orchestrator itself is idempotent per (text, date) via its own Phase 1
# file lock (see run_stock_discussion.topic_id_for/phase1_locked), so a bot
# restart mid-run only risks a duplicate *trigger*, not corrupted output.
_GROUP_DISCUSSION_RUNNING: set[str] = set()
_GROUP_TOPICS: dict[str, dict[str, str]] = {}
_GROUP_MSG_TO_TOPIC: dict[int, str] = {}


def _stock_discussion_today() -> str:
    """Asia/Taipei today, matching investment-os's
    scripts/run_stock_discussion.py:today_str() default so the bot's id8 and
    the orchestrator's own topic_id land on the same date."""
    return datetime.now(TAIPEI_TZ).date().isoformat()


def _stock_discussion_topic_id(text: str, date_str: str) -> str:
    """Replicates run_stock_discussion.topic_id_for() exactly:
    sha256(text+date)[:16]. Duplicated rather than imported because bot.py
    runs out of bot/venv in this repo, not investment-os's own .venv — see
    investment-os/scripts/run_stock_discussion.py:topic_id_for and
    investment-os/scripts/discussion_ingress_stub.md."""
    return hashlib.sha256((text + date_str).encode("utf-8")).hexdigest()[:16]


def _group_trigger_match(text: str) -> Optional["re.Match[str]"]:
    """Group-chat trigger detection (Owner 2026-08-24): text starting with
    研調:/研調：/辯論:/辯論：/討論:/討論：(full- or half-width colon), or the same
    prefixes after an @bot-username mention. Returns the match against the
    prefix-stripped text (group 1 = keyword, group 2 = statement with the
    prefix removed), or None when nothing matches — everything else in the
    group must stay silent."""
    stripped = _GROUP_MENTION_RE.sub("", text or "", count=1)
    return _GROUP_TRIGGER_RE.match(stripped.lstrip())


def _group_discussion_out_dir(date_str: str, topic_id: str, mode: str) -> Path:
    """Mirrors run_stock_discussion.run()'s out_dir selection: research mode
    uses reports/discussion/<date>/<topic_id>/, debate mode uses
    .../<topic_id>__debate/ (see that module's `mode` handling)."""
    name = topic_id if mode == "research" else f"{topic_id}__{mode}"
    return INVESTMENT_OS_DIR / "reports" / "discussion" / date_str / name


def _read_group_discussion_summary(date_str: str, topic_id: str, mode: str) -> str:
    """Reads the orchestrator's summary.txt (<=3 lines, always written by
    run()); falls back to the first 3 non-empty lines of integrated.md if
    summary.txt is somehow missing. Never raises — returns "" on any
    failure so the caller can post a clear failure line instead."""
    out_dir = _group_discussion_out_dir(date_str, topic_id, mode)
    try:
        text = (out_dir / "summary.txt").read_text(encoding="utf-8").strip()
        if text:
            return text
    except Exception:
        pass
    try:
        lines = [ln.strip() for ln in (out_dir / "integrated.md").read_text(encoding="utf-8").splitlines() if ln.strip()]
        return "\n".join(lines[:3])
    except Exception:
        return ""


async def _run_group_discussion_orchestrator(
    bot, chat_id: int, id8: str, topic_id: str, statement_text: str, mode: str, date_str: str
) -> None:
    """Runs investment-os/scripts/run_stock_discussion.py as a background
    subprocess (asyncio.create_subprocess_exec — never blocks the polling
    loop) with --send-telegram (TelbotFin renders the same integrated
    result to Owner's private chat, unchanged from the existing manual
    flow), then posts a <=3-line summary — or, on any failure/timeout, one
    failure line — back to the SAME group. Never silent after the ack."""
    cmd = [
        str(INVESTMENT_OS_VENV_PYTHON),
        DISCUSSION_ORCHESTRATOR_RELATIVE_SCRIPT,
        "--text", statement_text,
        "--today", date_str,
        "--send-telegram",
    ]
    if mode == "debate":
        cmd += ["--mode", "debate"]
    try:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(INVESTMENT_OS_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as e:
            await bot.send_message(chat_id=chat_id, text=f"topic-id {id8} 失敗:{_trim(str(e), 80)},稍後重試")
            return
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=DISCUSSION_ORCHESTRATOR_TIMEOUT_S)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            await bot.send_message(chat_id=chat_id, text=f"topic-id {id8} 失敗:逾時{DISCUSSION_ORCHESTRATOR_TIMEOUT_S}秒,稍後重試")
            return
        if proc.returncode != 0:
            err = (stderr.decode(errors="replace") or stdout.decode(errors="replace") or "未知錯誤").strip()
            await bot.send_message(chat_id=chat_id, text=f"topic-id {id8} 失敗:{_trim(err, 80)},稍後重試")
            return
        summary_text = _read_group_discussion_summary(date_str, topic_id, mode)
        if not summary_text:
            await bot.send_message(chat_id=chat_id, text=f"topic-id {id8} 失敗:找不到整合結果,稍後重試")
            return
        msg = await bot.send_message(chat_id=chat_id, text=f"【Fable5 整合】topic-id {id8}\n{summary_text}")
        msg_id = getattr(msg, "message_id", None)
        if msg_id is not None:
            _GROUP_MSG_TO_TOPIC[msg_id] = topic_id
    except Exception as e:
        logger.exception("group discussion orchestrator run failed")
        try:
            await bot.send_message(chat_id=chat_id, text=f"topic-id {id8} 失敗:{_trim(str(e), 80)},稍後重試")
        except Exception:
            logger.exception("group discussion failure notice send failed")
    finally:
        _GROUP_DISCUSSION_RUNNING.discard(topic_id)


async def _dispatch_group_discussion(bot, chat_id: int, statement_text: str, mode: str) -> None:
    """Acks in the group with the topic-id, then spawns the orchestrator in
    the background. A second trigger for a topic_id already running gets a
    "仍在進行" ack instead of a duplicate run (concurrency guard, Owner
    2026-08-24 spec)."""
    date_str = _stock_discussion_today()
    topic_id = _stock_discussion_topic_id(statement_text, date_str)
    id8 = topic_id[:8]
    if topic_id in _GROUP_DISCUSSION_RUNNING:
        await bot.send_message(chat_id=chat_id, text=f"topic-id {id8} 仍在進行")
        return
    _GROUP_DISCUSSION_RUNNING.add(topic_id)
    ack_label = _GROUP_MODE_ACK_LABEL.get(mode, "研調")
    ack_msg = await bot.send_message(chat_id=chat_id, text=f"收到 topic-id {id8} 開工({ack_label})")
    ack_msg_id = getattr(ack_msg, "message_id", None)
    if ack_msg_id is not None:
        _GROUP_MSG_TO_TOPIC[ack_msg_id] = topic_id
    _GROUP_TOPICS[topic_id] = {"text": statement_text, "mode": mode, "date": date_str, "id8": id8}
    asyncio.create_task(_run_group_discussion_orchestrator(bot, chat_id, id8, topic_id, statement_text, mode, date_str))


async def _handle_group_followup(bot, chat_id: int, parent_message_id: int, new_text: str) -> None:
    """Owner replying (in the group) to the bot's ack or summary message for
    a prior topic is treated as a follow-up: re-run the orchestrator with
    the original topic text plus an explicit "追問(承接 topic-id <parent
    id8>): <new text>" continuation, so the new topic's own input_pack
    carries a legible reference back to the parent discussion (Owner
    2026-08-24: "new topic whose text references the parent id8"). Reuses
    the parent's mode (研調 stays 研調, 辯論 stays 辯論)."""
    parent_topic_id = _GROUP_MSG_TO_TOPIC.get(parent_message_id)
    parent = _GROUP_TOPICS.get(parent_topic_id) if parent_topic_id else None
    if parent is None:
        return
    parent_id8 = parent.get("id8") or (parent_topic_id or "")[:8]
    followup_text = f"{parent['text']}\n追問(承接 topic-id {parent_id8}): {new_text.strip()}"
    await _dispatch_group_discussion(bot, chat_id, followup_text, parent.get("mode", "research"))


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Registered before handle_message (see main()) so it exclusively
    handles every group/supergroup text message — handle_message never sees
    them. General group chit-chat, and anything from a non-Owner sender,
    stays completely silent per 能力測試 D: no reply, no deny(), not even an
    inbox tap for non-Owner senders. Owner's own group messages are tapped
    to the same a0_inbox.jsonl used for the private line (tagged
    source="group") so A0 has visibility, but — per this task's spec — that
    tap must never feed the offline resume/relay path; see the chat_id<0
    guards in _a0_resume_or_fallback/_a0_wait_then_maybe_resume."""
    if update.message is None:
        return
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    message_id = getattr(update.message, "message_id", None)
    sender_id = update.effective_user.id if update.effective_user else None

    if sender_id != OWNER_CHAT_ID:
        # Non-owner group member: fully silent. No deny(), no inbox tap —
        # this bot only ever acts on Owner's own group messages.
        return

    _a0_inbox_append(chat_id, text, message_id, source="group")

    reply_to = getattr(update.message, "reply_to_message", None)
    reply_to_id = getattr(reply_to, "message_id", None) if reply_to is not None else None
    if reply_to_id is not None and reply_to_id in _GROUP_MSG_TO_TOPIC:
        await _handle_group_followup(context.bot, chat_id, reply_to_id, text)
        return

    match = _group_trigger_match(text)
    if match is None:
        return  # 一般群聊保持靜默 — no trigger, no reply at all.
    keyword = match.group(1)
    statement = (match.group(2) or "").strip()
    if not statement:
        # Trigger prefix with nothing after it — nothing to research; stay
        # silent rather than spawn a run on empty input.
        return
    mode = _GROUP_TRIGGER_MODE.get(keyword, "research")
    await _dispatch_group_discussion(context.bot, chat_id, statement, mode)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Unhandled exception: {context.error}", exc_info=context.error)


# ── /clip command ───────────────────────────────────────────────────────────────

async def clip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store text to local clipboard file for Extension to fetch."""
    if not is_owner(update):
        await deny(update)
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        current = ""
        if CLIP_FILE.exists():
            try:
                current = json.loads(CLIP_FILE.read_text(encoding="utf-8")).get("text", "")[:80]
            except Exception:
                pass
        await update.message.reply_text(
            "用法：/clip [文字] — 儲存文字到 Extension 剪貼板\n"
            f"目前剪貼板：{current or '（空）'}"
        )
        return
    ts = datetime.now().strftime("%H:%M:%S")
    CLIP_FILE.write_text(
        json.dumps({"text": text, "ts": ts}, ensure_ascii=False),
        encoding="utf-8",
    )
    await update.message.reply_text(
        f"📋 已存入剪貼板（{len(text)} 字）\n"
        f"開 Extension popup → 點「📋 從 Bot 抓取」→「⚡ 注入」"
    )


# ── Local HTTP Clipboard Server ─────────────────────────────────────────────────

class _ClipHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/clip":
            self.send_response(404)
            self.end_headers()
            return
        if CLIP_FILE.exists():
            content = CLIP_FILE.read_bytes()
        else:
            content = json.dumps({"text": "", "ts": ""}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        pass  # suppress HTTP access logs


def _start_clip_server() -> None:
    try:
        server = http.server.HTTPServer(("127.0.0.1", CLIP_SERVER_PORT), _ClipHandler)
        logger.info(f"Clipboard server running on 127.0.0.1:{CLIP_SERVER_PORT}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Clipboard server failed to start: {e}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Copy bot/.env.example → bot/.env and fill it in.")
        sys.exit(1)

    _load_conv_history()
    logger.info(f"Starting MAPLAB A1 遠端終端 (repo={REPO_PATH})…")

    # Start local clipboard HTTP server in background thread
    t = threading.Thread(target=_start_clip_server, daemon=True)
    t.start()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("owner", owner_cmd))
    app.add_handler(CommandHandler("task", task_cmd))
    app.add_handler(CommandHandler("patrol", patrol))
    app.add_handler(CommandHandler("queue", queue))
    app.add_handler(CommandHandler("agent", agent_cmd))
    app.add_handler(CommandHandler("commit", commit_cmd))
    app.add_handler(CommandHandler("blocker", blocker))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(CommandHandler("ask", ask_cmd))
    app.add_handler(CommandHandler("codex_dispatch", codex_dispatch_cmd))
    app.add_handler(CommandHandler("runtime", runtime_cmd))
    app.add_handler(CommandHandler("hermes", hermes_cmd))
    app.add_handler(CommandHandler("claude", claude_cmd))
    app.add_handler(CommandHandler("model", model_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CommandHandler("clip", clip_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    # Registered BEFORE handle_message and in the same default handler group
    # (0): PTB dispatches only the first matching handler per group per
    # update, so any group/supergroup text message is fully claimed here and
    # never reaches handle_message's private-chat deny()/A0-relay flow.
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, handle_group_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(ChatMemberHandler(on_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_error_handler(on_error)

    logger.info(f"Bot running — owner={OWNER_CHAT_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
