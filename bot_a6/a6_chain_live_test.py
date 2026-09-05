#!/usr/bin/env python3
"""One-off live test: new free-model chain end-to-end, delivered via A6 Telegram.

Owner-requested 2026-08-30: after removing the local ollama fallback, prove the
rewired chain answers for real — one plain test ping and one quote-round draft —
and send both into the Owner's Telegram so the result is visible.

Secrets: token/key are read by this process from .env / free_compute.env and
passed straight to the APIs; they are never printed or logged.
"""
import json
import os
import sys
import urllib.request

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BOT_DIR)

import hermes_telegram_gateway as gw  # noqa: E402


def load_env(path):
    env = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def send(token, chat_id, text):
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": text[:3500]}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp).get("ok")


def main():
    env = load_env(os.path.join(BOT_DIR, ".env"))
    free_env = load_env(os.path.expanduser("~/.maplab/free_compute.env"))
    token = env["A6_BOT_TOKEN"]
    chat_id = env["OWNER_USER_ID"]
    key = free_env.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY", "")
    chain = gw.load_chain()

    test_q = "鏈路測試:請用一句繁體中文回覆確認你在線,並說出你是哪個模型。"
    quote_q = (
        "客戶詢價(合成測試,非真實客訊):台南室內開幕茶會,約40位成人來賓,"
        "Finger Food+甜點+飲品,希望含餐檯佈置。請以 maplabkitchen 客服身分,"
        "先確認細節再介紹服務範圍(餐點規劃、陳列規劃師行前設計、現場陳列、"
        "乾燥花藝基本裝飾、桌巾餐具、撤場;長桌租借每張350;車馬費另計;"
        "食安考量餐點擺放約二個半至三小時後撤場)。規則:資料不足處一律用問句釐清,"
        "不得編造經驗或數字;需詢問是否供酒與攝影期待產出(平面照/影片/曝光素材)。"
    )

    results = []
    for label, q in (("ping", test_q), ("quote", quote_q)):
        reply, model = None, None
        msgs = [{"role": "user", "content": q}]
        for m in chain:
            try:
                r = gw.openrouter_chat(key, m, msgs)
            except Exception as exc:  # noqa: BLE001
                print(f"{label}: {m} -> {type(exc).__name__}", flush=True)
                continue
            if r:
                reply, model = r, m
                break
        results.append((label, model, reply))
        print(f"{label}: answered_by={model} len={len(reply) if reply else 0}", flush=True)

    header = "【hermes・鏈路實測】本機 ollama 已拔除,以下由免費鏈即時生成:\n\n"
    for label, model, reply in results:
        tag = "① 在線確認" if label == "ping" else "② 報價回覆試跑(合成客訊)"
        body = reply if reply else "(整條鏈都未回覆——請回報 Fable5)"
        ok = send(token, chat_id, f"{header if label == 'ping' else ''}{tag}\n供應模型:{model}\n\n{body}")
        print(f"telegram_send {label}: ok={ok}", flush=True)


if __name__ == "__main__":
    main()
