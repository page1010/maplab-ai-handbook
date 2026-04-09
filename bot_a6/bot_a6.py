#!/usr/bin/env python3
"""
MAPLAB A6 報價助理 — Telegram 群組 bot (long polling)
業務群組專用：你（Owner）+ 業務，兩人白名單
功能：急件報價、品項修改「你幫我把X改成Y」、查詢案件

Usage:
    python3 bot_a6.py
    (or via launchd for auto-start)
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
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

A6_BOT_TOKEN = os.getenv("A6_BOT_TOKEN")
OWNER_USER_ID = int(os.getenv("OWNER_USER_ID", "1077768811"))
SALES_USER_ID = int(os.getenv("SALES_USER_ID", "0"))  # 業務的 Telegram user ID
REPO_PATH = Path(os.getenv("REPO_PATH", "/Users/pagemacmini/maplab-ai-handbook"))
CLAUDE_OAUTH_TOKEN = os.getenv("CLAUDE_CODE_OAUTH_TOKEN", "")

# 白名單：只有這兩人的訊息會被處理
ALLOWED_USER_IDS: set[int] = {OWNER_USER_ID}
if SALES_USER_ID:
    ALLOWED_USER_IDS.add(SALES_USER_ID)

A6_LOG_DIR = REPO_PATH / "data" / "a6-logs"
CONV_HISTORY_FILE = BOT_DIR / "conv_history_a6.json"

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_FILE = BOT_DIR / "bot_a6.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("maplab_a6_bot")

START_TIME = datetime.now()

# Semaphore: only one Claude call at a time
_claude_semaphore = asyncio.Semaphore(1)

# Conversation history per chat_id (deque maxlen=20)
_conv_history: dict[int, deque] = {}

def _load_a6_recall():
    """
    從 recalls/A6_recall.md 讀取 A6 的完整角色定義 + 操作手冊指引。
    2026-04-09：不再 hardcode system prompt，改讀 repo 裡的 recall 檔案。
    這樣 recall 更新後只要重啟 bot 就生效，不用改 Python code。
    """
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    recall_path = os.path.join(base_dir, 'recalls', 'A6_recall.md')
    try:
        with open(recall_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        # fallback: 如果 recall 檔讀不到，用最小版本避免 bot 啟動失敗
        return (
            "你是 MAPLAB A6 報價加速器。面對業務 Mina，不面對客人。\n"
            "錯誤：recalls/A6_recall.md 讀取失敗 (" + str(e) + ")，請通知 A0 修復。\n"
            "暫時以最小功能運作：接收業務指令，用繁體中文簡潔回答。"
        )

A6_SYSTEM_PROMPT = _load_a6_recall()


def _load_conv_history() -> None:
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

def log_b_layer(user_name: str, user_msg: str, bot_reply: str) -> None:
    """記錄 B 層對話（業務 ↔ A6），供 A5/A7 優化用。"""
    try:
        A6_LOG_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = A6_LOG_DIR / f"{today}.md"
        ts = datetime.now().strftime("%H:%M:%S")
        entry = (
            f"\n## {today} {ts} [B層]\n"
            f"**業務（{user_name}）：** {user_msg}\n\n"
            f"**A6：** {bot_reply}\n\n"
            f"---\n"
        )
        if not log_file.exists():
            header = f"# A6 B層對話紀錄 — {today}\n\n> 業務↔A6 指令/輸出，供 A5 優化用\n"
            log_file.write_text(header, encoding="utf-8")
        with log_file.open("a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        logger.warning(f"log_b_layer failed: {e}")


def git_commit_a6_log() -> None:
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        log_rel = f"data/a6-logs/{today}.md"
        subprocess.run(["git", "add", log_rel], cwd=REPO_PATH, capture_output=True, timeout=10)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=REPO_PATH, capture_output=True, timeout=5
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"log(a6): {today} B層對話自動存檔"],
                cwd=REPO_PATH, capture_output=True, timeout=15,
            )
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=REPO_PATH, capture_output=True, timeout=30,
            )
    except Exception as e:
        logger.warning(f"git_commit_a6_log failed: {e}")


def log_and_commit_a6(user_name: str, user_msg: str, bot_reply: str) -> None:
    import threading
    log_b_layer(user_name, user_msg, bot_reply)
    t = threading.Thread(target=git_commit_a6_log, daemon=True)
    t.start()


# ── Auth guard ─────────────────────────────────────────────────────────────────

def is_allowed(update: Update) -> bool:
    return update.effective_user.id in ALLOWED_USER_IDS


async def deny(update: Update) -> None:
    uid = update.effective_user.id
    logger.warning(f"Unauthorized access from user_id={uid}")
    # 群組裡不要大聲嚷嚷，只 log，不回覆


# ── Helpers ────────────────────────────────────────────────────────────────────

def git_pull_silent() -> None:
    try:
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=REPO_PATH, capture_output=True, timeout=15,
        )
    except Exception:
        pass


async def send_long(update: Update, text: str) -> None:
    MAX = 4096
    for i in range(0, len(text), MAX):
        await update.message.reply_text(text[i:i + MAX])


async def claude_ask(chat_id: int, user_message: str, user_name: str = "", timeout: int = 600) -> str:
    """Call claude -p with A6 system prompt + conversation history."""
    history = _get_history(chat_id)

    parts = [A6_SYSTEM_PROMPT]
    if history:
        parts.append("\n【對話記錄】")
        for msg in history:
            role_label = f"業務（{user_name}）" if msg["role"] == "user" else "A6"
            parts.append(f"{role_label}：{msg['content']}")
        parts.append("【對話記錄結束】")
    parts.append(f"\n業務（本次）：{user_message}\n請用繁體中文簡潔回答。")
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
            return f"⚠️ A6 回應超時（{timeout}秒）"
        if proc.returncode != 0:
            err = stderr.decode(errors="replace")[:300].strip()
            return f"⚠️ Claude 錯誤: {err or '未知錯誤'}"
        answer = stdout.decode(errors="replace").strip() or "（A6 無回應）"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": answer})
        _save_conv_history()
        return answer
    except FileNotFoundError:
        return "⚠️ 找不到 claude 命令，請確認 Mac mini 上已安裝 Claude Code"
    except Exception as e:
        return f"⚠️ 呼叫 A6 失敗: {e}"


# ── Command Handlers ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    await update.message.reply_text(
        f"🟢 MAPLAB A6 報價助理 online\n"
        f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"可用指令：\n"
        f"/help — 指令說明\n"
        f"/ping — 心跳\n\n"
        f"或直接說：\n"
        f"「報價 王小明 婚禮 80人 預算6萬」\n"
        f"「你幫我把主菜換成素食版本」\n"
        f"「查 王小明」"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    await update.message.reply_text(
        "📋 MAPLAB A6 報價助理指令\n\n"
        "【急件報價】\n"
        "報價 [客名] [類型] [人數] [預算]\n"
        "例：報價 王小明 婚禮 80人 預算6萬\n\n"
        "【品項修改】\n"
        "你幫我把 [X] 換成 [Y]\n"
        "例：你幫我把主菜換成素食版本\n\n"
        "【查詢案件】\n"
        "查 [客名]\n"
        "例：查 王小明\n\n"
        "【其他】\n"
        "/ping — 心跳檢查\n"
        "/reset — 清除對話記憶（新案件時用）\n\n"
        "💬 也可以直接說中文，A6 會理解"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    uptime = datetime.now() - START_TIME
    h, rem = divmod(int(uptime.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    await update.message.reply_text(
        f"🏓 A6 pong — {datetime.now().strftime('%H:%M:%S')}\n"
        f"Uptime: {h}h {m}m {s}s\n"
        f"允許用戶數: {len(ALLOWED_USER_IDS)}"
    )


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    chat_id = update.effective_chat.id
    _conv_history.pop(chat_id, None)
    _save_conv_history()
    await update.message.reply_text("🔄 對話記憶已清除，可開始新案件。")


# ── Background Claude runner ───────────────────────────────────────────────────

async def _run_claude_background(
    bot,
    chat_id: int,
    user_message: str,
    user_name: str,
) -> None:
    async with _claude_semaphore:
        answer = await claude_ask(chat_id, user_message, user_name)
        MAX = 4096
        for i in range(0, len(answer), MAX):
            await bot.send_message(chat_id=chat_id, text=answer[i:i + MAX])
        log_and_commit_a6(user_name, user_message, answer)


async def _run_claude_guarded(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_message: str,
) -> None:
    if _claude_semaphore.locked():
        await update.message.reply_text("⏳ A6 正在處理上一則，請稍候。")
        return
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name or "業務"
    await update.message.reply_text("⏳ A6 處理中…")
    asyncio.create_task(
        _run_claude_background(context.bot, chat_id, user_message, user_name)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    text = update.message.text or ""
    if not text.strip():
        return
    await _run_claude_guarded(update, context, text)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Unhandled exception: {context.error}", exc_info=context.error)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not A6_BOT_TOKEN:
        logger.error("A6_BOT_TOKEN not set. Fill in bot_a6/.env")
        sys.exit(1)
    if not SALES_USER_ID:
        logger.warning("SALES_USER_ID not set — only Owner can use A6 bot")

    _load_conv_history()
    logger.info(f"Starting MAPLAB A6 報價助理 (allowed_users={ALLOWED_USER_IDS})…")

    app = (
        Application.builder()
        .token(A6_BOT_TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"A6 Bot running — allowed={ALLOWED_USER_IDS}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
