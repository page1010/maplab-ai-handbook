#!/usr/bin/env python3
"""
MAPLAB Claude Bot — Telegram daemon (long polling)
24/7 persistent listener on Mac mini

Usage:
    python3 bot.py
    (or via launchd / pm2 for auto-start)
"""

import logging
import os
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

# ── Load .env from bot/ directory ──────────────────────────────────────────────
BOT_DIR = Path(__file__).parent
load_dotenv(BOT_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "1077768811"))

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


# ── Handlers ───────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greeting on /start."""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 MAPLAB Claude Bot online\n"
        f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"User: {user.first_name} (id={user.id})\n\n"
        f"/help — 查看指令列表"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands."""
    await update.message.reply_text(
        "📋 可用指令:\n"
        "/start  — 確認 bot 在線\n"
        "/help   — 本說明\n"
        "/ping   — 延遲測試\n"
        "/status — 系統狀態\n"
        "/echo <text> — 回音測試\n\n"
        "其他文字訊息將被記錄並回覆確認。"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Latency / alive check."""
    await update.message.reply_text(
        f"🏓 pong — {datetime.now().strftime('%H:%M:%S')}"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """System status snapshot."""
    import platform
    import psutil

    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        mem_used = mem.used // (1024 ** 3)
        mem_total = mem.total // (1024 ** 3)
        msg = (
            f"🖥️ MAPLAB Mac Mini Status\n"
            f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"OS: {platform.system()} {platform.release()}\n"
            f"CPU: {cpu}%\n"
            f"RAM: {mem_used}GB / {mem_total}GB ({mem.percent}%)\n"
            f"Bot uptime: running ✅"
        )
    except ImportError:
        msg = (
            f"🖥️ MAPLAB Bot Online\n"
            f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"(psutil 未安裝，無法顯示 CPU/RAM)"
        )
    await update.message.reply_text(msg)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/echo <text> — echo back."""
    text = " ".join(context.args) if context.args else "(empty)"
    await update.message.reply_text(f"🔁 {text}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log and acknowledge all other text messages."""
    user = update.effective_user
    text = update.message.text
    logger.info(f"MSG from {user.first_name}({user.id}): {text!r}")
    await update.message.reply_text(
        f"✅ 已收到\n「{text[:200]}」\n\n(Bot 處於 echo 模式，尚未接入 Claude Code)"
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler — logs and keeps running."""
    logger.error(f"Exception while handling update: {context.error}", exc_info=context.error)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Copy bot/.env.example → bot/.env and fill it in.")
        sys.exit(1)

    logger.info("Starting MAPLAB Claude Bot (long polling)…")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"Bot running — owner chat_id={OWNER_CHAT_ID}")

    # run_polling handles reconnects automatically
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,   # ignore stale messages from downtime
    )


if __name__ == "__main__":
    main()
