#!/usr/bin/env python3
"""
MAPLAB Claude Bot — Telegram daemon (long polling) + Claude AI
24/7 persistent listener on Mac mini

Usage:
    python3 bot.py
    (or via launchd for auto-start)
"""

import logging
import os
import sys
from collections import defaultdict, deque
from pathlib import Path
from datetime import datetime

from typing import Optional
import anthropic
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
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
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "1077768811"))
CLAUDE_MODEL = "claude-sonnet-4-6"
HISTORY_LIMIT = 20  # messages per chat_id

SYSTEM_PROMPT = """你是 MAPLAB 的 AI 助手，由 Claude 驅動，常駐在 Page 的 Mac mini 上。
你協助 Page 管理專案、回答問題、追蹤任務、分析數據。
MAPLAB 是一間台灣廚藝學校，主要業務包含廚藝課程、餐飲活動、外燴服務。
回覆請簡潔直接，優先用繁體中文，技術詞彙可用英文。"""

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

# ── Conversation history (in-memory, per chat_id) ──────────────────────────────
# deque(maxlen=HISTORY_LIMIT) stores dicts: {"role": "user"|"assistant", "content": str}
chat_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))

# ── Anthropic client (lazy — None if key missing) ──────────────────────────────
_claude: Optional[anthropic.Anthropic] = None

def get_claude() -> Optional[anthropic.Anthropic]:
    global _claude
    if _claude is None and ANTHROPIC_API_KEY:
        _claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _claude


# ── Claude API call ─────────────────────────────────────────────────────────────

async def ask_claude(chat_id: int, user_text: str) -> str:
    """Append user message to history, call Claude, return reply."""
    client = get_claude()
    if client is None:
        return "⚠️ ANTHROPIC_API_KEY 未設定，無法呼叫 Claude API。\n請在 bot/.env 加入 ANTHROPIC_API_KEY=sk-ant-..."

    history = chat_history[chat_id]
    history.append({"role": "user", "content": user_text})

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=list(history),
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        return reply
    except anthropic.AuthenticationError:
        return "⚠️ API key 無效，請確認 bot/.env 裡的 ANTHROPIC_API_KEY 正確。"
    except anthropic.RateLimitError:
        return "⚠️ Claude API 速率限制，請稍後再試。"
    except Exception as e:
        logger.error(f"Claude API error: {e}", exc_info=True)
        return f"⚠️ Claude API 錯誤：{type(e).__name__}，請稍後再試。"


# ── Telegram Handlers ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    has_key = bool(ANTHROPIC_API_KEY)
    ai_status = "✅ Claude AI 已連線" if has_key else "⚠️ ANTHROPIC_API_KEY 未設定（echo 模式）"
    await update.message.reply_text(
        f"👋 MAPLAB Claude Bot online\n"
        f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"User: {user.first_name} (id={user.id})\n"
        f"AI: {ai_status}\n\n"
        f"/help — 查看指令列表"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📋 可用指令:\n"
        "/start   — 確認 bot 在線\n"
        "/help    — 本說明\n"
        "/ping    — 延遲測試\n"
        "/status  — 系統狀態\n"
        "/echo <text> — 回音測試\n"
        "/reset   — 清除對話歷史\n\n"
        "其他文字訊息 → 直接傳給 Claude AI 回覆"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"🏓 pong — {datetime.now().strftime('%H:%M:%S')}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    import platform
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        mem_used = mem.used // (1024 ** 3)
        mem_total = mem.total // (1024 ** 3)
        hw = f"CPU: {cpu}%\nRAM: {mem_used}GB / {mem_total}GB ({mem.percent}%)"
    except ImportError:
        hw = "(psutil 未安裝)"

    has_key = bool(ANTHROPIC_API_KEY)
    hist_len = len(chat_history.get(update.effective_chat.id, []))
    await update.message.reply_text(
        f"🖥️ MAPLAB Mac Mini\n"
        f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"OS: {platform.system()} {platform.release()}\n"
        f"{hw}\n"
        f"Claude AI: {'✅ ' + CLAUDE_MODEL if has_key else '❌ 未設定 key'}\n"
        f"對話歷史: {hist_len} 條"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args) if context.args else "(empty)"
    await update.message.reply_text(f"🔁 {text}")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history for this chat."""
    chat_id = update.effective_chat.id
    chat_history[chat_id].clear()
    await update.message.reply_text("🗑️ 對話歷史已清除。")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route plain text to Claude AI."""
    user = update.effective_user
    text = update.message.text
    chat_id = update.effective_chat.id
    logger.info(f"MSG from {user.first_name}({user.id}): {text!r}")

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    reply = await ask_claude(chat_id, text)
    await update.message.reply_text(reply)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Unhandled exception: {context.error}", exc_info=context.error)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set. Copy bot/.env.example → bot/.env and fill it in.")
        sys.exit(1)

    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — bot will run in echo/fallback mode")

    logger.info(f"Starting MAPLAB Claude Bot (model={CLAUDE_MODEL})…")

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
    app.add_handler(CommandHandler("echo", echo))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"Bot running — owner={OWNER_CHAT_ID}, AI={'on' if ANTHROPIC_API_KEY else 'OFF (no key)'}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
