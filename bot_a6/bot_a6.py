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
import urllib.request
from collections import deque
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from a5_quote_engine import build_a5_quote_prompt, run_a5_local_quote
from case_store import CaseStore, CaseStoreError, render_case_detail, render_case_list

# ── Config ─────────────────────────────────────────────────────────────────────
BOT_DIR = Path(__file__).parent
load_dotenv(BOT_DIR / ".env")

A6_BOT_TOKEN = os.getenv("A6_BOT_TOKEN")
OWNER_USER_ID = int(os.getenv("OWNER_USER_ID", "1077768811"))
SALES_USER_ID = int(os.getenv("SALES_USER_ID", "0"))  # 業務的 Telegram user ID
REPO_PATH = Path(os.getenv("REPO_PATH", "/Users/pagemacmini/maplab-ai-handbook"))
CLAUDE_OAUTH_TOKEN = os.getenv("CLAUDE_CODE_OAUTH_TOKEN", "")
GAS_QUOTE_URL = os.getenv("GAS_QUOTE_URL", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL_CHAT = os.getenv("OLLAMA_MODEL_CHAT", "llama3.1:latest")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))
CASE_STORE_SYNC_ROWS = int(os.getenv("CASE_STORE_SYNC_ROWS", "600"))

# 白名單：只有這兩人的訊息會被處理
ALLOWED_USER_IDS: set[int] = {OWNER_USER_ID}
if SALES_USER_ID:
    ALLOWED_USER_IDS.add(SALES_USER_ID)

A6_LOG_DIR = REPO_PATH / "data" / "a6-logs"
A6_PHOTO_DIR = REPO_PATH / "data" / "a6-photos"
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
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

START_TIME = datetime.now()

# Semaphore: only one Claude call at a time
_claude_semaphore = asyncio.Semaphore(1)

# Conversation history per chat_id (deque maxlen=20)
_conv_history: dict[int, deque] = {}
_chat_modes: dict[int, str] = {}  # quote|chat|seo

MODE_QUOTE = "quote"
MODE_CHAT = "chat"
MODE_SEO = "seo"

MODE_LABELS = {
    MODE_QUOTE: "🧾 A5 報價模式（雲端 A5 + 本地 Ollama 備援）",
    MODE_CHAT: "💬 聊天模式（Ollama）",
    MODE_SEO: "📝 SEO 模式（Ollama）",
}

MENU_BUTTON_QUOTE = "🧾 報價模式"
MENU_BUTTON_CHAT = "💬 一般聊天"
MENU_BUTTON_SEO = "📝 SEO 草稿"
MENU_BUTTON_HELP = "❓ 指令說明"


def _get_mode(chat_id: int) -> str:
    return _chat_modes.get(chat_id, MODE_CHAT)


def _set_mode(chat_id: int, mode: str) -> None:
    if mode in (MODE_QUOTE, MODE_CHAT, MODE_SEO):
        _chat_modes[chat_id] = mode


def _mode_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[MENU_BUTTON_QUOTE, MENU_BUTTON_CHAT], [MENU_BUTTON_SEO, MENU_BUTTON_HELP]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def _looks_like_runtime_status_request(text: str) -> bool:
    stripped = text.strip().lower()
    compact = "".join(stripped.split())
    if stripped in {"/status", "/model", "status", "model"}:
        return True
    model_needles = ("什麼模型", "哪個模型", "跑什麼", "用什麼模型", "現在跑", "現在是跑", "模型狀態")
    if "模型" in compact and any(needle in compact for needle in model_needles):
        return True
    runtime_needles = ("你現在是跑", "runtime", "ollama", "openclaw")
    return any(needle in compact for needle in runtime_needles)


def _looks_like_quote_request(text: str) -> bool:
    stripped = text.strip()
    lowered = stripped.lower()
    compact = "".join(stripped.split())
    if not stripped:
        return False
    explicit_prefixes = ("報價", "新報價", "估價", "做報價", "開報價", "a5", "A5")
    if stripped.startswith(explicit_prefixes):
        return True
    if stripped.startswith("/localquote"):
        return True
    if "你幫我把" in stripped and ("換成" in stripped or "改成" in stripped):
        return True
    quote_terms = (
        "報價", "菜單", "外燴", "餐點", "茶會", "派對", "週歲", "婚禮", "企業",
        "開幕", "晚宴", "桌菜", "buffet", "預算", "統編",
    )
    quantity_terms = ("人", "桌", "份", "盒")
    has_quote_term = any(term in lowered or term in compact for term in quote_terms)
    has_quantity = any(term in compact for term in quantity_terms)
    has_money = any(term in compact for term in ("預算", "萬", "元", "$", "nt", "NT"))
    return has_quote_term and (has_quantity or has_money)


def _runtime_status_text(chat_id: int) -> str:
    uptime = datetime.now() - START_TIME
    h, rem = divmod(int(uptime.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    a5_engine = os.getenv("A5_LOCAL_ENGINE", "auto")
    a5_model = os.getenv("A5_LOCAL_MODEL", "llama3.1:latest")
    openclaw_model = os.getenv("OPENCLAW_MODEL", "qwen2.5:14b")
    openclaw_dispatch = os.getenv("OPENCLAW_MODEL_DISPATCH", "qwen2.5-coder:7b")
    return (
        "🟢 A6 runtime 狀態\n"
        f"目前模式：{MODE_LABELS[_get_mode(chat_id)]}\n"
        f"Uptime：{h}h {m}m {s}s\n\n"
        "模型路徑：\n"
        f"- 一般聊天：Ollama `{OLLAMA_MODEL_CHAT}`\n"
        f"- A5 本地報價備援：{a5_engine} `{a5_model}`\n"
        f"- OpenClaw 預設：`{openclaw_model}`\n"
        f"- OpenClaw dispatch：`{openclaw_dispatch}`\n\n"
        "這類模型/狀態問題會直接由 A6 回覆，不會啟動 A5 報價流程。\n"
        "要報價時請明確輸入「報價 ...」或使用 `/localquote ...`。"
    )


def _load_a6_recall():
    """
    從 recalls/A6_recall_compact.md 讀取精簡版 recall（~20 行）。
    2026-04-09 P1 修正：原本讀 A6_recall.md（159 行）太長，
    claude -p 把整個 recall 當回覆吐出來。
    改讀精簡版，完整手冊留在 skills/ 讓 A6 需要時自己讀。
    """
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 優先讀精簡版，fallback 讀完整版的前 30 行
    compact_path = os.path.join(base_dir, 'recalls', 'A6_recall_compact.md')
    full_path = os.path.join(base_dir, 'recalls', 'A6_recall.md')
    try:
        if os.path.exists(compact_path):
            with open(compact_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return ''.join(lines[:200])  # 只取前 200 行
        else:
            raise FileNotFoundError('neither compact nor full recall found')
    except Exception as e:
        return (
            "你是 MAPLAB A6 報價加速器。面對業務 Mina，不面對客人。\n"
            "錯誤：recall 檔讀取失敗 (" + str(e) + ")，請通知 A0 修復。\n"
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


def _build_ollama_prompt(chat_id: int, user_message: str, mode: str, user_name: str = "") -> str:
    history = _get_history(chat_id)
    if mode == MODE_SEO:
        system = (
            "你是 MAPLAB Kitchen 的 SEO 助手。請用繁體中文回答，輸出要可直接執行。"
            "避免虛構資料，若資訊不足要明確標示假設。"
        )
    else:
        system = (
            "你是 MAPLAB A6 的地端聊天助理。請用繁體中文、簡潔、實用地回覆，"
            "語氣專業友善，避免過度冗長。"
        )

    parts = [system]
    if history:
        parts.append("\n【對話記錄】")
        for msg in history:
            role_label = f"使用者（{user_name or '業務'}）" if msg["role"] == "user" else "助理"
            parts.append(f"{role_label}：{msg['content']}")
        parts.append("【對話記錄結束】")
    parts.append(f"\n使用者（本次）：{user_message}\n請直接回答。")
    return "\n".join(parts)


def _ollama_generate_sync(prompt: str) -> str:
    payload = json.dumps(
        {"model": OLLAMA_MODEL_CHAT, "prompt": prompt, "stream": False},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    return (data.get("response") or "").strip()


async def ollama_ask(chat_id: int, user_message: str, mode: str, user_name: str = "") -> str:
    prompt = _build_ollama_prompt(chat_id, user_message, mode, user_name)
    try:
        answer = await asyncio.to_thread(_ollama_generate_sync, prompt)
        if not answer:
            return "⚠️ Ollama 無回應，請稍後再試。"
        history = _get_history(chat_id)
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": answer})
        _save_conv_history()
        return answer
    except Exception as e:
        return f"⚠️ Ollama 呼叫失敗：{e}"


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
            cwd=os.getenv('REPO_PATH', '/Users/pagemacmini/maplab-ai-handbook'),
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


async def a5_cloud_quote_ask(chat_id: int, user_message: str, user_name: str = "", timeout: int = 600) -> str:
    """Call the cloud CLI path with an A5 quote prompt.

    If this path fails or quota is exhausted, the caller falls back to the local
    A5 quote engine instead of leaving the Telegram user with a dead end.
    """
    history = _get_history(chat_id)
    full_prompt = build_a5_quote_prompt(
        user_message=user_message,
        user_name=user_name,
        history=history,
        runtime="cloud-a5",
    )

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
            cwd=os.getenv('REPO_PATH', '/Users/pagemacmini/maplab-ai-handbook'),
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return f"⚠️ A5 雲端報價引擎回應超時（{timeout}秒）"
        if proc.returncode != 0:
            err = stderr.decode(errors="replace")[:500].strip()
            return f"⚠️ A5 雲端報價引擎錯誤: {err or '未知錯誤'}"
        answer = stdout.decode(errors="replace").strip() or "（A5 雲端報價引擎無回應）"
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": answer})
        _save_conv_history()
        return answer
    except FileNotFoundError:
        return "⚠️ 找不到 claude 命令，改用本地 A5 備援"
    except Exception as e:
        return f"⚠️ 呼叫 A5 雲端報價引擎失敗: {e}"


# ── Command Handlers ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    chat_id = update.effective_chat.id
    _set_mode(chat_id, MODE_CHAT)
    await update.message.reply_text(
        f"🟢 MAPLAB A6 報價助理 online\n"
        f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"目前模式：{MODE_LABELS[_get_mode(chat_id)]}\n\n"
        f"一般問題會直接由 A6 回覆；只有明確輸入「報價 ...」或 `/localquote ...` 才會進 A5。\n\n"
        f"可用指令：\n"
        f"/help — 指令說明\n"
        f"/ping — 心跳\n"
        f"/status — runtime / 模型狀態\n\n"
        f"或直接說：\n"
        f"「你現在是跑什麼模型」\n"
        f"「報價 王小明 婚禮 80人 預算6萬」\n"
        f"「/linecases today」\n"
        f"「/case Penny」\n"
        f"「A5 幫我先做一版 30人週歲派對 2萬內」\n"
        f"「你幫我把主菜換成素食版本」\n"
        f"「查 王小明」",
        reply_markup=_mode_keyboard(),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "📋 MAPLAB A6 報價助理指令\n\n"
        f"【模式切換】\n"
        f"/mode quote — A5 報價模式（雲端 A5；失敗時本地 Ollama/OpenClaw 備援）\n"
        f"/mode chat — 一般聊天（Ollama）\n"
        f"/mode seo — SEO 助手（Ollama）\n"
        f"目前模式：{MODE_LABELS[_get_mode(chat_id)]}\n\n"
        "一般問題預設留在 A6；只有明確報價需求才會進 A5。\n\n"
        "【急件報價】\n"
        "報價 [客名] [類型] [人數] [預算]\n"
        "例：報價 王小明 婚禮 80人 預算6萬\n\n"
        "【本地備援測試】\n"
        "/localquote [需求] — 直接走本機 Ollama/OpenClaw，不寫 Google Sheet\n\n"
        "【LINE Case Store】\n"
        "/linecases today — 同步 LINE CONVERSATION_LOG，列出今日案件候選\n"
        "/linecases [關鍵字] — 搜尋 LINE 案件候選\n"
        "/case [關鍵字或 case_id] — 查看單一案件脈絡\n"
        "/casequote [關鍵字或 case_id] — 把案件脈絡交給 A5 報價\n\n"
        "【品項修改】\n"
        "你幫我把 [X] 換成 [Y]\n"
        "例：你幫我把主菜換成素食版本\n\n"
        "【查詢案件】\n"
        "查 [客名]\n"
        "例：查 王小明\n\n"
        "【其他】\n"
        "/ping — 心跳檢查\n"
        "/status — runtime / 模型狀態\n"
        "/model — 同 /status\n"
        "/reset — 清除對話記憶（新案件時用）\n\n"
        "💬 也可以直接說中文，A6 會理解"
    )


async def mode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    chat_id = update.effective_chat.id
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "用法：/mode quote | /mode chat | /mode seo\n"
            f"目前模式：{MODE_LABELS[_get_mode(chat_id)]}",
            reply_markup=_mode_keyboard(),
        )
        return
    raw = args[0].strip().lower()
    if raw not in (MODE_QUOTE, MODE_CHAT, MODE_SEO):
        await update.message.reply_text("⚠️ 模式只接受 quote / chat / seo")
        return
    _set_mode(chat_id, raw)
    await update.message.reply_text(
        f"✅ 已切換：{MODE_LABELS[raw]}",
        reply_markup=_mode_keyboard(),
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
        f"允許用戶數: {len(ALLOWED_USER_IDS)}\n"
        f"目前模式：{MODE_LABELS[_get_mode(update.effective_chat.id)]}"
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    await update.message.reply_text(
        _runtime_status_text(update.effective_chat.id),
        reply_markup=_mode_keyboard(),
    )


async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    chat_id = update.effective_chat.id
    _conv_history.pop(chat_id, None)
    _save_conv_history()
    await update.message.reply_text("🔄 對話記憶已清除，可開始新案件。")


async def localquote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    args = context.args or []
    quote_request = " ".join(args).strip()
    if not quote_request:
        await update.message.reply_text(
            "用法：/localquote [報價需求]\n"
            "例：/localquote 報價 王小明 婚禮 80人 預算6萬"
        )
        return
    await _run_a5_quote_guarded(update, context, f"/localquote {quote_request}")


def _sync_case_store() -> tuple[CaseStore, object]:
    store = CaseStore.from_env(REPO_PATH)
    result = store.sync_from_sheet(max_rows=CASE_STORE_SYNC_ROWS)
    return store, result


async def linecases_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    raw_query = " ".join(context.args or []).strip()
    query = raw_query or "today"
    await update.message.reply_text("⏳ 正在同步 LINE CONVERSATION_LOG 到 Case Store…")
    try:
        store, result = await asyncio.to_thread(_sync_case_store)
        if query.lower() in {"today", "今天", "今日"}:
            cases = store.recent_cases(limit=8, today_only=True)
            body = render_case_list(cases, "今日 LINE 案件候選")
        elif query.lower() in {"recent", "近期"}:
            cases = store.recent_cases(limit=8)
            body = render_case_list(cases, "近期 LINE 案件候選")
        else:
            cases = store.search_cases(query, limit=8)
            body = render_case_list(cases, f"搜尋：{query}")
        prefix = (
            f"✅ Case Store 同步完成\n"
            f"Sheet rows: {result.fetched_rows}｜messages: {result.message_upserts}｜"
            f"cases: {result.case_upserts}｜latest row: {result.latest_row}\n"
            f"source: {result.source}\n\n"
        )
        await send_long(update, prefix + body)
    except CaseStoreError as exc:
        await update.message.reply_text(f"⚠️ Case Store 同步失敗：{exc}")
    except Exception as exc:
        logger.exception("linecases_cmd failed")
        await update.message.reply_text(f"⚠️ Case Store 指令失敗：{exc}")


async def case_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    query = " ".join(context.args or []).strip()
    if not query:
        await update.message.reply_text("用法：/case [客名、case_id、關鍵字或 LINE user id]")
        return
    await _reply_case_detail(update, query)


async def _reply_case_detail(update: Update, query: str) -> None:
    await update.message.reply_text("⏳ 正在讀取 Case Store…")
    try:
        store, result = await asyncio.to_thread(_sync_case_store)
        cases = store.search_cases(query, limit=3)
        if not cases:
            await update.message.reply_text(
                f"找不到案件：{query}\n"
                f"已同步到 latest row {result.latest_row}。"
            )
            return
        if len(cases) > 1:
            await send_long(update, render_case_list(cases, f"找到多筆：{query}"))
            return
        case = cases[0]
        messages = store.get_case_messages(case.case_id, limit=14)
        await send_long(update, render_case_detail(case, messages))
    except CaseStoreError as exc:
        await update.message.reply_text(f"⚠️ Case Store 同步失敗：{exc}")
    except Exception as exc:
        logger.exception("case_cmd failed")
        await update.message.reply_text(f"⚠️ Case Store 指令失敗：{exc}")


async def casequote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    query = " ".join(context.args or []).strip()
    if not query:
        await update.message.reply_text("用法：/casequote [客名、case_id、關鍵字或 LINE user id]")
        return
    await update.message.reply_text("⏳ 正在把 Case Store 案件脈絡交給 A5…")
    try:
        store, _result = await asyncio.to_thread(_sync_case_store)
        case, context_text = store.build_quote_context(query)
        if not case:
            await update.message.reply_text(context_text)
            return
        await _run_a5_quote_guarded(update, context, f"/localquote {context_text}")
    except CaseStoreError as exc:
        await update.message.reply_text(f"⚠️ Case Store 同步失敗：{exc}")
    except Exception as exc:
        logger.exception("casequote_cmd failed")
        await update.message.reply_text(f"⚠️ Case Store 指令失敗：{exc}")


# ── Background Claude runner ───────────────────────────────────────────────────

def _trigger_gas_quote_sync(form_data: dict) -> Optional[dict]:
    """POST formData to GAS Web App, supporting createQuote and createQuoteVariants."""
    if not GAS_QUOTE_URL:
        logging.warning("GAS_QUOTE_URL not set, skipping GAS trigger")
        return None
    try:
        import urllib.request
        import urllib.error
        payload = json.dumps({"action": "createQuote", **form_data}).encode()
        req = urllib.request.Request(
            GAS_QUOTE_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')
        logging.error(f"GAS trigger HTTP {e.code}: {body}")
        return {"success": False, "error": f"HTTP {e.code}: {body[:200]}"}
    except urllib.error.URLError as e:
        logging.error(f"GAS trigger URL error: {e.reason}")
        return {"success": False, "error": f"連線失敗: {e.reason}"}
    except Exception as e:
        logging.error(f"GAS trigger failed: {e}")
        return {"success": False, "error": str(e)}


def _format_gas_quote_result(gas_result: dict) -> tuple[str, bool]:
    """Return (message, is_multi_variant) for GAS quote responses."""
    result = gas_result.get("result") or {}
    quotes = result.get("quotes") or []
    if quotes:
        lines = ["📄 **報價單已自動產出！**"]
        for quote in quotes:
            label = quote.get("label", "")
            title = quote.get("title", "")
            total = quote.get("totalRevenue")
            margin = quote.get("overallMargin")
            food_margin = quote.get("foodMargin")
            food_cost_ratio = quote.get("foodCostRatio")
            url = quote.get("url", "")
            total_text = f"NT${total:,.0f}" if isinstance(total, (int, float)) else ""
            food_margin_text = f"餐點毛利 {food_margin * 100:.1f}%" if isinstance(food_margin, (int, float)) else ""
            food_ratio_text = f"食材占比 {food_cost_ratio * 100:.1f}%" if isinstance(food_cost_ratio, (int, float)) else ""
            overall_text = f"整體毛利 {margin * 100:.1f}%" if isinstance(margin, (int, float)) else ""
            name = title if title.startswith(label) else f"{label} {title}".strip()
            summary = "｜".join(x for x in [name, total_text] if x)
            metrics = "｜".join(x for x in [food_margin_text, food_ratio_text, overall_text] if x)
            lines.append(f"{summary}\n{metrics}\n{url}" if metrics else f"{summary}\n{url}")
        return "\n\n".join(lines), True

    url = gas_result.get("url", "")
    case_id = gas_result.get("caseId", "")
    return f"📄 **報價單已自動產出！**\n連結：{url}\n案件編號：{case_id}", False


def _trigger_gas_slide_sync() -> Optional[dict]:
    """POST createSlide action to GAS Web App, return {success, url} or None"""
    if not GAS_QUOTE_URL:
        return None
    try:
        import urllib.request
        payload = json.dumps({"action": "createSlide"}).encode()
        req = urllib.request.Request(
            GAS_QUOTE_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logging.error(f"GAS createSlide failed: {e}")
        return None


def _trigger_gas_add_item(form_data: dict) -> Optional[dict]:
    """POST addItem payload to GAS Web App, return {success, item_id, ...} or None"""
    if not GAS_QUOTE_URL:
        logging.warning("GAS_QUOTE_URL not set, skipping addItem trigger")
        return None
    try:
        import urllib.request
        import urllib.error
        payload = json.dumps({"action": "addItem", **form_data}).encode()
        req = urllib.request.Request(
            GAS_QUOTE_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')
        logging.error(f"GAS addItem HTTP {e.code}: {body}")
        return {"success": False, "error": f"HTTP {e.code}: {body[:200]}"}
    except urllib.error.URLError as e:
        logging.error(f"GAS addItem URL error: {e.reason}")
        return {"success": False, "error": f"連線失敗: {e.reason}"}
    except Exception as e:
        logging.error(f"GAS addItem failed: {e}")
        return {"success": False, "error": str(e)}


def _extract_form_data(claude_reply: str) -> Optional[dict]:
    """從 Claude 回覆中找 ```json block，解析 formData"""
    import re
    match = re.search(r'```json\s*(\{.*?\})\s*```', claude_reply, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if 'clientName' in data or 'action' in data:
                return data
        except json.JSONDecodeError:
            pass
    # fallback: 報價完成特徵關鍵字（任一符合就嘗試觸發 GAS）
    completion_keywords = ['報價完成', 'cells 全部寫入', '報價定稿', '報價總覽', '費用總覽']
    if any(kw in claude_reply for kw in completion_keywords):
        return {"action": "createQuote", "fromMaster": True}
    # 毛利率 + % 同時出現（報價完成的結構特徵）
    if '毛利率' in claude_reply and '%' in claude_reply:
        return {"action": "createQuote", "fromMaster": True}
    return None


async def _heartbeat(bot, chat_id: int, start_time: float, cancel_event: asyncio.Event) -> None:
    """每 60 秒發一次心跳，直到 cancel_event 被設定。"""
    await asyncio.sleep(60)
    while not cancel_event.is_set():
        elapsed = int((asyncio.get_event_loop().time() - start_time) / 60)
        if elapsed >= 5:
            msg = f"⏳ 這次分析較複雜，A6 還在處理中...（已等 {elapsed} 分鐘）"
        else:
            msg = f"⏳ A6 仍在分析中，請稍候...（已等 {elapsed} 分鐘）"
        try:
            await bot.send_message(chat_id=chat_id, text=msg)
        except Exception:
            pass
        await asyncio.sleep(60)


def _looks_like_cloud_failure(answer: str) -> bool:
    lowered = answer.lower()
    needles = [
        "⚠️",
        "quota",
        "rate limit",
        "usage limit",
        "exceeded",
        "billing",
        "overloaded",
        "找不到 claude",
        "雲端報價引擎錯誤",
        "雲端報價引擎失敗",
        "回應超時",
    ]
    return any(needle in lowered for needle in needles)


async def _run_a5_quote_background(
    bot,
    chat_id: int,
    user_message: str,
    user_name: str,
) -> None:
    async with _claude_semaphore:
        cancel_event = asyncio.Event()
        start_time = asyncio.get_event_loop().time()
        heartbeat_task = asyncio.create_task(
            _heartbeat(bot, chat_id, start_time, cancel_event)
        )
        local_fallback = False
        force_local = user_message.strip().startswith("/localquote")
        quote_message = user_message.strip()
        if force_local:
            quote_message = quote_message[len("/localquote"):].strip() or user_message
        try:
            if force_local:
                answer = "⚠️ 已依指令直接切到本機 A5 備援。"
            else:
                answer = await a5_cloud_quote_ask(chat_id, user_message, user_name)
            if force_local or _looks_like_cloud_failure(answer):
                local_fallback = True
                if force_local:
                    notice = "🧪 A5 本地備援測試：直接走 Ollama/OpenClaw，不寫 Google Sheet。"
                else:
                    notice = "⚠️ A5 雲端路徑不可用，切到本機 Ollama/OpenClaw 備援產草稿。"
                await bot.send_message(chat_id=chat_id, text=notice)
                history = list(_get_history(chat_id))
                result = await asyncio.to_thread(
                    run_a5_local_quote,
                    quote_message,
                    user_name,
                    history,
                )
                answer = result.answer
                history_ref = _get_history(chat_id)
                history_ref.append({"role": "user", "content": quote_message})
                history_ref.append({"role": "assistant", "content": answer})
                _save_conv_history()
        finally:
            cancel_event.set()
            heartbeat_task.cancel()

        if not local_fallback:
            form_data = _extract_form_data(answer)
            if form_data:
                if form_data.get('action') == 'addItem':
                    add_result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: _trigger_gas_add_item(form_data))
                    if add_result and add_result.get('success'):
                        item_id = add_result.get('item_id', '')
                        answer += f"\n\n✅ 品項已新增 item_id: {item_id}"
                    else:
                        error_msg = add_result.get('error', '未知錯誤') if add_result else 'GAS 無回應'
                        answer += f"\n\n⚠️ 品項新增失敗（{error_msg}）。"
                else:
                    gas_result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: _trigger_gas_quote_sync(form_data))
                    if gas_result and gas_result.get('success'):
                        quote_msg, is_multi_variant = _format_gas_quote_result(gas_result)
                        answer += f"\n\n{quote_msg}"

                        if not is_multi_variant:
                            slide_result = await asyncio.get_event_loop().run_in_executor(
                                None, lambda: _trigger_gas_slide_sync())
                            if slide_result and slide_result.get('success'):
                                slide_url = slide_result.get('url', '')
                                answer += f"\n\n📊 **提案簡報已自動產出！**\n連結：{slide_url}"
                            else:
                                slide_error = slide_result.get('error', '未知錯誤') if slide_result else 'GAS 無回應'
                                answer += f"\n\n⚠️ 提案簡報自動產出失敗（{slide_error}）。資料已寫入母版，可手動點選單產出。"
                    else:
                        error_msg = gas_result.get('error', '未知錯誤') if gas_result else 'GAS 無回應'
                        answer += f"\n\n⚠️ 報價單自動產出失敗（{error_msg}）。資料已寫入母版，可手動點選單產出。"
        else:
            answer += "\n\n⚠️ 本次為本地備援草稿，沒有自動寫入 Google Sheet 或產生正式報價單。"

        MAX = 4096
        for i in range(0, len(answer), MAX):
            await bot.send_message(chat_id=chat_id, text=answer[i:i + MAX])
        log_and_commit_a6(user_name, user_message, answer)


async def _run_a5_quote_guarded(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_message: str,
) -> None:
    if _claude_semaphore.locked():
        await update.message.reply_text("⏳ A5 正在處理上一則報價，請稍候。")
        return
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name or "業務"
    await update.message.reply_text("⏳ A5 報價模式處理中…")
    asyncio.create_task(
        _run_a5_quote_background(context.bot, chat_id, user_message, user_name)
    )


async def _run_claude_background(
    bot,
    chat_id: int,
    user_message: str,
    user_name: str,
) -> None:
    async with _claude_semaphore:
        cancel_event = asyncio.Event()
        start_time = asyncio.get_event_loop().time()
        heartbeat_task = asyncio.create_task(
            _heartbeat(bot, chat_id, start_time, cancel_event)
        )
        try:
            answer = await claude_ask(chat_id, user_message, user_name)
        finally:
            cancel_event.set()
            heartbeat_task.cancel()

        # 嘗試觸發 GAS
        form_data = _extract_form_data(answer)
        if form_data:
            if form_data.get('action') == 'addItem':
                # addItem 路徑：新增品項，不走 createQuote/createSlide
                add_result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: _trigger_gas_add_item(form_data))
                if add_result and add_result.get('success'):
                    item_id = add_result.get('item_id', '')
                    answer += f"\n\n✅ 品項已新增 item_id: {item_id}"
                else:
                    error_msg = add_result.get('error', '未知錯誤') if add_result else 'GAS 無回應'
                    answer += f"\n\n⚠️ 品項新增失敗（{error_msg}）。"
            else:
                # 原本的 createQuote + createSlide 流程
                gas_result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: _trigger_gas_quote_sync(form_data))
                if gas_result and gas_result.get('success'):
                    quote_msg, is_multi_variant = _format_gas_quote_result(gas_result)
                    answer += f"\n\n{quote_msg}"

                    # 單份 createQuote 成功後才觸發 Slide；多方案報價不讀 master 產簡報。
                    if not is_multi_variant:
                        slide_result = await asyncio.get_event_loop().run_in_executor(
                            None, lambda: _trigger_gas_slide_sync())
                        if slide_result and slide_result.get('success'):
                            slide_url = slide_result.get('url', '')
                            answer += f"\n\n📊 **提案簡報已自動產出！**\n連結：{slide_url}"
                        else:
                            slide_error = slide_result.get('error', '未知錯誤') if slide_result else 'GAS 無回應'
                            answer += f"\n\n⚠️ 提案簡報自動產出失敗（{slide_error}）。資料已寫入母版，可手動點選單產出。"
                else:
                    error_msg = gas_result.get('error', '未知錯誤') if gas_result else 'GAS 無回應'
                    answer += f"\n\n⚠️ 報價單自動產出失敗（{error_msg}）。資料已寫入母版，可手動點選單產出。"

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


async def _run_ollama_background(
    bot,
    chat_id: int,
    user_message: str,
    user_name: str,
    mode: str,
) -> None:
    async with _claude_semaphore:
        answer = await ollama_ask(chat_id, user_message, mode, user_name)
        MAX = 4096
        for i in range(0, len(answer), MAX):
            await bot.send_message(chat_id=chat_id, text=answer[i:i + MAX])
        log_and_commit_a6(user_name, user_message, answer)


async def _run_ollama_guarded(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_message: str,
    mode: str,
) -> None:
    if _claude_semaphore.locked():
        await update.message.reply_text("⏳ A6 正在處理上一則，請稍候。")
        return
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name or "業務"
    await update.message.reply_text("⏳ Ollama 處理中…")
    asyncio.create_task(
        _run_ollama_background(context.bot, chat_id, user_message, user_name, mode)
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages: download image and pass to Claude Code for analysis."""
    if not is_allowed(update):
        await deny(update)
        return

    # Download the largest photo resolution
    photo = update.message.photo[-1]
    photo_file = await context.bot.get_file(photo.file_id)
    A6_PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(photo_file.file_path or "photo.jpg").suffix or ".jpg"
    local_path = A6_PHOTO_DIR / f"{ts}_{photo.file_unique_id}{file_ext}"
    await photo_file.download_to_drive(str(local_path))
    logger.info(f"A6 photo saved: {local_path}")

    caption = update.message.caption or ""
    caption_note = f"\nOwner/業務 附的文字說明：{caption}" if caption else ""

    user_message = (
        f"收到一張圖片，已存在 {local_path}，請用 Read 工具讀取並分析圖片內容。{caption_note}\n"
        f"如果是品項/食物照片，辨識品名並協助新增品項（addItem）。"
        f"如果是截圖/對話截圖，分析內容並回應。"
    )
    await _run_claude_guarded(update, context, user_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await deny(update)
        return
    text = update.message.text or ""
    if not text.strip():
        return
    chat_id = update.effective_chat.id

    if text == MENU_BUTTON_QUOTE:
        _set_mode(chat_id, MODE_QUOTE)
        await update.message.reply_text(f"✅ 已切換：{MODE_LABELS[MODE_QUOTE]}", reply_markup=_mode_keyboard())
        return
    if text == MENU_BUTTON_CHAT:
        _set_mode(chat_id, MODE_CHAT)
        await update.message.reply_text(f"✅ 已切換：{MODE_LABELS[MODE_CHAT]}", reply_markup=_mode_keyboard())
        return
    if text == MENU_BUTTON_SEO:
        _set_mode(chat_id, MODE_SEO)
        await update.message.reply_text(f"✅ 已切換：{MODE_LABELS[MODE_SEO]}", reply_markup=_mode_keyboard())
        return
    if text == MENU_BUTTON_HELP:
        await help_cmd(update, context)
        return

    stripped = text.strip()
    if _looks_like_runtime_status_request(stripped):
        await status_cmd(update, context)
        return
    if stripped.startswith("查 "):
        await _reply_case_detail(update, stripped[2:].strip())
        return

    mode = _get_mode(chat_id)
    if _looks_like_quote_request(stripped):
        await _run_a5_quote_guarded(update, context, text)
    elif mode == MODE_SEO:
        await _run_ollama_guarded(update, context, text, MODE_SEO)
    else:
        await _run_ollama_guarded(update, context, text, MODE_CHAT)


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
    app.add_handler(CommandHandler("mode", mode_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("model", status_cmd))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CommandHandler("localquote", localquote_cmd))
    app.add_handler(CommandHandler("linecases", linecases_cmd))
    app.add_handler(CommandHandler("case", case_cmd))
    app.add_handler(CommandHandler("casequote", casequote_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    logger.info(f"A6 Bot running — allowed={ALLOWED_USER_IDS}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
