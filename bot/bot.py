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
import subprocess
import sys
import threading
from collections import deque
from pathlib import Path
from datetime import datetime

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

TELEGRAM_LOG_DIR = REPO_PATH / "data" / "telegram-logs"
CONV_HISTORY_FILE = BOT_DIR / "conv_history.json"

# ── Clipboard Server ────────────────────────────────────────────────────────────
CLIP_FILE = Path("/tmp/maplab_clip.json")
CLIP_SERVER_PORT = 9876

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

START_TIME = datetime.now()

# Semaphore: only one Claude call at a time
_claude_semaphore = asyncio.Semaphore(1)

# Conversation history per chat_id (deque maxlen=20 messages)
_conv_history: dict[int, deque] = {}

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


async def claude_ask(chat_id: int, user_message: str, system_extra: str = "", timeout: int = 600) -> str:
    """Call claude -p with conversation history injected into prompt (OAuth, Max 訂閱，不計 API 費用).

    Since OAuth tokens can't be used directly with Anthropic SDK, we use claude CLI
    and simulate memory by including conversation history in the prompt.
    """
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
            return f"⚠️ Claude 回應超時（{timeout}秒）"
        if proc.returncode != 0:
            err = stderr.decode(errors="replace")[:300].strip()
            return f"⚠️ Claude 錯誤: {err or '未知錯誤'}"
        answer = stdout.decode(errors="replace").strip() or "（Claude 無回應）"
        # Save to history on success
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": answer})
        _save_conv_history()
        return answer
    except FileNotFoundError:
        return "⚠️ 找不到 claude 命令，請確認已安裝 Claude Code"
    except Exception as e:
        return f"⚠️ 呼叫 Claude 失敗: {e}"


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
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--grep=patrol", "-10"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout.strip() or "（無 patrol 相關 commit）"
    except Exception as e:
        output = f"⚠️ git log 失敗：{e}"
    await update.message.reply_text(f"🔍 最近 patrol commits:\n\n{output}")


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
        answer = await claude_ask(chat_id, user_message, system_extra)
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
    app.add_handler(CommandHandler("clip", clip_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"Bot running — owner={OWNER_CHAT_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
