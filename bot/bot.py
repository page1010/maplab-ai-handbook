#!/usr/bin/env python3
"""
MAPLAB A1 遠端讀檔終端 — Telegram daemon (long polling)
24/7 persistent listener on Mac mini
直接讀取 repo markdown 文件回傳，無 Claude API 呼叫

Usage:
    python3 bot.py
    (or via launchd for auto-start)
"""

import logging
import os
import subprocess
import sys
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
        "/task \\[ID\\] — 查特定任務，例如 /task T\\-A2\\-001\n"
        "/patrol — 最近巡查報告（git log patrol commits）\n"
        "/queue — 待認領任務（TASK\\_QUEUE.md）\n"
        "/agent \\[A1\\-A8\\] — 特定 Agent 狀態\n"
        "/commit — 最近 5 條 git log\n"
        "/blocker — 所有 blocker\n"
        "/refresh — 手動 git pull\n"
        "/ping — 心跳檢查\n"
        "/help — 本說明",
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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner(update):
        await deny(update)
        return
    await update.message.reply_text(
        "ℹ️ 此終端為讀檔模式，不支援自由對話。\n請使用 /help 查看可用指令。"
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Unhandled exception: {context.error}", exc_info=context.error)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Copy bot/.env.example → bot/.env and fill it in.")
        sys.exit(1)

    logger.info(f"Starting MAPLAB A1 遠端終端 (repo={REPO_PATH})…")

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
    app.add_handler(CommandHandler("task", task_cmd))
    app.add_handler(CommandHandler("patrol", patrol))
    app.add_handler(CommandHandler("queue", queue))
    app.add_handler(CommandHandler("agent", agent_cmd))
    app.add_handler(CommandHandler("commit", commit_cmd))
    app.add_handler(CommandHandler("blocker", blocker))
    app.add_handler(CommandHandler("refresh", refresh))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"Bot running — owner={OWNER_CHAT_ID}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
