#!/usr/bin/env python3
"""hermes Telegram gateway — A6 bot 交接給 hermes(Owner 2026-08-25 指示)。

原 bot_a6.py(報價助理)在 Telegram 側退役;本閘道接手 A6 bot token,
讓 Owner 有一個獨立視窗直接跟 hermes 對話。
引擎:OpenRouter 免費鏈(ranking.json zh 鏈),不用任何本地模型。
hermes 鐵則:不下單、不發布、不動排程、不碰金鑰、不冒充 Fable5、拿不準就說拿不準。
"""
import json
import os
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BOT_DIR = Path(__file__).resolve().parent
LOG = BOT_DIR / "hermes_gateway.log"
CONV = BOT_DIR / "hermes_conv.json"
RUNBOOK_PATHS = [
    Path.home() / ".hermes/HERMES_TAKEOVER_RUNBOOK.md",
    BOT_DIR.parent / "handoff/HERMES_TAKEOVER_RUNBOOK_20260825.md",
]
RANKING = Path.home() / "investment-os/scripts/free_compute/ranking.json"
FREE_ENV = Path.home() / ".maplab/free_compute.env"
FALLBACK_CHAIN = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-26b-a4b-it:free",
]
MAX_HISTORY = 12
MAX_REPLY = 3500


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="", flush=True)


def load_free_env_key():
    if "OPENROUTER_API_KEY" in os.environ:
        return os.environ["OPENROUTER_API_KEY"]
    try:
        for raw in FREE_ENV.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if raw.startswith("OPENROUTER_API_KEY="):
                return raw.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return None


def load_chain():
    try:
        data = json.loads(RANKING.read_text(encoding="utf-8"))
        chain = data.get("use_cases", {}).get("zh_customer_reply_maplabkitchen", [])
        retired = set(data.get("retired", {}))
        chain = [m for m in chain if m not in retired]
        if chain:
            return chain
    except (OSError, ValueError):
        pass
    return FALLBACK_CHAIN


def load_runbook():
    for p in RUNBOOK_PATHS:
        try:
            return p.read_text(encoding="utf-8")[:9000]
        except OSError:
            continue
    return "(接手手冊讀取失敗——只用鐵則回答,答不了就說要等 Fable5)"


def system_prompt():
    return (
        "你是 hermes,MAPLAB/Investment OS 系統的備援答疑代理,在 A6 bot 的 Telegram 視窗值班。\n"
        "身分規則:你不是 Fable5,不冒充 Fable5;回覆開頭固定標【hermes】。\n"
        "職權:回答 Owner 關於每日投資訊號產品、系統狀態、SEO 專案的問題;判讀與答疑。\n"
        "鐵則(逐條硬性):不下單不轉帳;不發布 WordPress、不動生產設定;不改 launchd 排程;"
        "不讀不寫任何金鑰或 token;投資相關回答結尾標「研究判斷,非下單指令」;"
        "拿不準的事明說拿不準,需要 Fable5/Codex 的事明說要等他們額度回來,絕不腦補。\n"
        "語氣:說人話、直接、短段落;不用反引號;不發收據式空回報。\n"
        "以下是你的接手手冊(你的知識邊界,答題先查這裡):\n\n" + load_runbook()
    )


def tg_call(token, method, payload=None, timeout=60):
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload or {}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def openrouter_chat(key, model, messages):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps({
            "model": model,
            "messages": messages,
            "max_tokens": 1200,
            "temperature": 0.4,
        }).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    choices = data.get("choices") or []
    if not choices:
        return None
    content = (choices[0].get("message") or {}).get("content")
    return content.strip() if content and content.strip() else None


def load_history():
    try:
        return json.loads(CONV.read_text(encoding="utf-8"))[-MAX_HISTORY:]
    except (OSError, ValueError):
        return []


def save_history(history):
    CONV.write_text(json.dumps(history[-MAX_HISTORY:], ensure_ascii=False, indent=1), encoding="utf-8")


def answer(key, chain, history, user_text):
    messages = [{"role": "system", "content": system_prompt()}] + history + [
        {"role": "user", "content": user_text}
    ]
    for model in chain:
        try:
            reply = openrouter_chat(key, model, messages)
        except (urllib.error.URLError, OSError, ValueError) as e:
            log(f"model {model} error: {e}")
            continue
        if reply:
            log(f"answered via {model}")
            return reply
        log(f"model {model} empty reply, fallback")
    return None


def main():
    token = os.environ.get("A6_BOT_TOKEN")
    owner = int(os.environ.get("OWNER_USER_ID", "1077768811"))
    if not token:
        log("FATAL: A6_BOT_TOKEN not in env")
        raise SystemExit(1)
    key = load_free_env_key()
    chain = load_chain()
    log(f"hermes gateway start; chain={chain}; openrouter_key={'yes' if key else 'MISSING'}")
    offset = None
    history = load_history()
    while True:
        try:
            params = {"timeout": 50, "allowed_updates": ["message"]}
            if offset is not None:
                params["offset"] = offset
            updates = tg_call(token, "getUpdates", params, timeout=70)
            for u in updates.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or {}
                chat = msg.get("chat") or {}
                text = (msg.get("text") or "").strip()
                if not text:
                    continue
                if chat.get("id") != owner:
                    log(f"ignore non-owner chat {chat.get('id')}")
                    continue
                if text == "/start":
                    tg_call(token, "sendMessage", {"chat_id": owner, "text": "【hermes】值班中。問我每日投資訊號、系統狀態、SEO 專案都可以;答不了的我會明說要等 Fable5。"})
                    continue
                log(f"owner msg: {text[:120]}")
                if key is None:
                    key = load_free_env_key()
                reply = answer(key, chain, history, text) if key else None
                if reply is None:
                    reply = ("【hermes】引擎這次沒答上來(免費算力鏈全數失敗或鑰匙讀不到)。"
                             "這題先記下,等 Fable5 額度回來處理;紀錄在 hermes_gateway.log。")
                else:
                    if not reply.startswith("【hermes】"):
                        reply = "【hermes】" + reply
                    history = (history + [
                        {"role": "user", "content": text},
                        {"role": "assistant", "content": reply},
                    ])[-MAX_HISTORY:]
                    save_history(history)
                tg_call(token, "sendMessage", {"chat_id": owner, "text": reply[:MAX_REPLY]})
        except KeyboardInterrupt:
            raise
        except Exception:
            log("loop error:\n" + traceback.format_exc())
            time.sleep(10)


if __name__ == "__main__":
    main()
