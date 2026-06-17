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
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Optional

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
load_dotenv(BOT_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "1077768811"))
REPO_PATH = Path(os.getenv("REPO_PATH", "/Users/pagemacmini/maplab-ai-handbook"))
CLAUDE_OAUTH_TOKEN = os.getenv("CLAUDE_CODE_OAUTH_TOKEN", "")
HERMES_FALLBACK_MODEL = os.getenv("HERMES_FALLBACK_MODEL", "gemma4:latest")
HERMES_FALLBACK_TIMEOUT = int(os.getenv("HERMES_FALLBACK_TIMEOUT", "240"))
HERMES_FALLBACK_TOOLSETS = os.getenv(
    "HERMES_FALLBACK_TOOLSETS",
    "none",
)
HERMES_PHOTO_FALLBACK_TOOLSETS = os.getenv("HERMES_PHOTO_FALLBACK_TOOLSETS", "vision")
HERMES_PROMPT_MAX_CHARS = int(os.getenv("HERMES_PROMPT_MAX_CHARS", "2200"))
HERMES_FALLBACK_HOME = Path(os.getenv("HERMES_FALLBACK_HOME", "/private/tmp/maplab-hermes-fallback"))

TELEGRAM_LOG_DIR = REPO_PATH / "data" / "telegram-logs"
TELEGRAM_PHOTO_DIR = REPO_PATH / "data" / "telegram-photos"
CONV_HISTORY_FILE = BOT_DIR / "conv_history.json"

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

ANTHROPIC_SYSTEM_PROMPT = (
    "【A1 Telegram Bot 前端 → A1 Claude Code 處理】\n"
    "以下是從 Telegram 轉發的 Owner 對話，請以 A1 系統總管身份協助回答。\n"
    "MAPLAB 婚禮/活動攝影工作室 AI 系統（v5.3，Phase 5）。\n"
    "Agents：A0=Cowork 總調度秘書（桌面控制）、A1=系統總管（Claude Code + Telegram bot）、A2=SEO、A3=廣告、A4=照片分類、A5=報價、A7=客服 FAQ。\n"
    "請用繁體中文簡潔回答。"
)


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
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + env.get("PATH", "")

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
            return f"⚠️ Hermes fallback 回應超時（{timeout}秒）"
        if proc.returncode != 0:
            err = stderr.decode(errors="replace")[:500].strip()
            return f"⚠️ Hermes fallback 錯誤: {err or '未知錯誤'}"
        return _sanitize_for_telegram(stdout.decode(errors="replace")) or "（Hermes 無回應）"

    try:
        answer = await _run_prompt(prompt)
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
        return "⚠️ 找不到 hermes 命令，無法啟動 Hermes fallback"
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


async def claude_ask_with_fallback(
    chat_id: int,
    user_message: str,
    system_extra: str = "",
    timeout: int = 600,
) -> str:
    """Use Claude primary, then Hermes only when Claude is unavailable/quota-limited."""
    if _truthy_env("MAPLAB_FORCE_HERMES_FALLBACK"):
        claude_result = ModelResult(
            ok=False,
            answer="⚠️ Claude 錯誤: forced Hermes fallback for test (MAPLAB_FORCE_HERMES_FALLBACK=1)",
            failure_kind="forced",
            stderr="MAPLAB_FORCE_HERMES_FALLBACK=1",
        )
    else:
        claude_result = await _claude_ask_raw(chat_id, user_message, system_extra, timeout)

    if claude_result.ok:
        answer = _sanitize_for_telegram(claude_result.answer)
        _record_history(chat_id, user_message, answer)
        return answer

    if not _hermes_fallback_enabled() or not _should_fallback_to_hermes(claude_result):
        return claude_result.answer

    hermes_answer = await hermes_ask(
        chat_id,
        user_message,
        system_extra=system_extra,
        fallback_reason=claude_result.answer,
    )
    if hermes_answer.startswith("⚠️"):
        return f"{claude_result.answer}\n\n{hermes_answer}"

    answer = f"{_format_hermes_receipt(claude_result.answer, _hermes_toolsets_for_message(user_message))}\n\n{hermes_answer}"
    _record_history(chat_id, user_message, answer)
    return answer


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
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + env.get("PATH", "")

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
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + env.get("PATH", "")

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
        "/runtime — 查看 Claude primary / Hermes fallback 狀態\n"
        "/reset — 生成本階段摘要+待辦，確認後清除對話記錄\n"
        "/help — 本說明\n\n"
        "💬 直接傳訊息也可以問 Claude",
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
    claude_path = shutil.which("claude") or "missing"
    hermes_path = shutil.which("hermes") or "missing"
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
        answer = await claude_ask_with_fallback(chat_id, user_message, system_extra)
        answer = _sanitize_for_telegram(answer)
        MAX = 4096
        for i in range(0, len(answer), MAX):
            await bot.send_message(chat_id=chat_id, text=answer[i:i + MAX])
        log_and_commit(log_user_msg, answer, log_label)


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
    git_pull_silent()
    try:
        status_snippet = read_file("CURRENT_STATUS.md")[:1500]
    except Exception:
        status_snippet = ""
    system_extra = (
        "以下是目前 MAPLAB 專案狀態摘要（供參考）：\n\n"
        f"{status_snippet}"
    )
    chat_id = update.effective_chat.id
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
    app.add_handler(CommandHandler("runtime", runtime_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CommandHandler("clip", clip_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"Bot running — owner={OWNER_CHAT_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
