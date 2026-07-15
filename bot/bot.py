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
from typing import Any, Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
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


def _hermes_fallback_enabled() -> bool:
    return not _falsey_env("HERMES_FALLBACK_ENABLED", "1")


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


def _route_from_dispatch_context(context_text: str) -> Optional[DispatchRoute]:
    catalog = _dispatch_catalog()
    context = _dispatch_norm(context_text)
    if _dispatch_has_any(
        context,
        (
            "投放成效判讀",
            "googleads",
            "google廣告",
            "metaads",
            "meta廣告",
            "廣告成效",
            "roas",
            "cpc",
            "cpa",
        ),
    ):
        return catalog["ads"]
    if _dispatch_has_any(context, ("報價任務", "quote", "試算", "毛利", "競品菜單")):
        return catalog["quote"]
    if _dispatch_has_any(context, ("系統巡查", "任務推進", "三層阻塞審查", "taskcard", "任務卡")):
        return catalog["patrol"]
    return None


def _dispatch_route_for_text(text: str, context_text: str = "") -> Optional[DispatchRoute]:
    normalized = _dispatch_norm(text)
    if not normalized:
        return None

    catalog = _dispatch_catalog()
    quote_markers = ("報價", "quote", "試算", "毛利", "成本", "競品菜單")
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
    followup_markers = (
        "誰做",
        "召喚了嗎",
        "召喚了",
        "派工",
        "派給",
        "貼到codex",
        "丟給codex",
        "openclaw",
        "hermes",
        "不是回覆",
        "要做",
        "去做",
    )

    if _dispatch_has_any(normalized, quote_markers):
        return catalog["quote"]
    if _dispatch_has_any(normalized, ads_markers) or (
        "廣告" in normalized
        and _dispatch_has_any(normalized, ("成效", "評估", "投放", "meta", "google", "預算"))
    ):
        return catalog["ads"]
    if _dispatch_has_any(normalized, patrol_markers) or ("角色" in normalized and "巡查" in normalized):
        return catalog["patrol"]
    if _dispatch_has_any(normalized, followup_markers) or "召喚" in normalized:
        return _route_from_dispatch_context(context_text) or catalog["generic"]
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
) -> None:
    """Background task: call Claude then push result via send_message."""
    async with _claude_semaphore:
        model_answer = await claude_ask_with_fallback(chat_id, user_message, system_extra)
        text = _sanitize_for_telegram(model_answer.text)
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
) -> None:
    """Reply immediately, then run Claude in background. Reports busy if semaphore is taken."""
    if _claude_semaphore.locked():
        await update.message.reply_text("⏳ Bot 正在處理上一則訊息，請稍候再試。")
        return
    await update.message.reply_text("⏳ 處理中…")
    asyncio.create_task(
        _run_claude_background(
            context.bot, chat_id, user_message, system_extra, log_label, log_user_msg
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    local_answer = _local_runtime_question_answer(text)
    if local_answer:
        await update.message.reply_text(local_answer)
        _record_history(chat_id, text, local_answer)
        log_and_commit(text, local_answer, "runtime-local")
        return

    dispatch_context = _latest_telegram_log_snippet(limit=3500)
    dispatch_route = _dispatch_route_for_text(text, dispatch_context)
    if dispatch_route:
        packet = _write_dispatch_packet(text, dispatch_context, route=dispatch_route)
        receipt = _dispatch_receipt(packet)
        await update.message.reply_text(receipt)
        _record_history(chat_id, text, receipt)
        log_and_commit(text, receipt, "dispatch-local")
        asyncio.create_task(_run_openclaw_dispatch_background(context.bot, chat_id, packet))
        return
    git_pull_silent()
    try:
        status_snippet = read_file("CURRENT_STATUS.md")[:1500]
    except Exception:
        status_snippet = ""
    system_extra = (
        "以下是目前 MAPLAB 專案狀態摘要（供參考）：\n\n"
        f"{status_snippet}"
    )
    await _run_claude_guarded(update, context, chat_id, text, system_extra, "", text)


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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"Bot running — owner={OWNER_CHAT_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
