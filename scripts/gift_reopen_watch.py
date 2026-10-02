#!/usr/bin/env python3
"""gift_reopen_watch.py — Anthropic Claude 玩偶/貼紙兌換頁重開監看(Owner 6582)。

2026-10-02 查證:兩條 Brilliant 兌換連結都顯示 "The invitation to this gift has
expired",動區文章說官方可能不定時重啟。此腳本每小時(launchd StartInterval)
用 openclaw Chrome 的 CDP 實渲染兩頁,頁面不再是 expired 就立刻推播 Owner。

唯讀監看:不填表、不送出任何資料;分頁開完即關。
Telegram token 只在行程內流動,不印出(沿用 spread_alert_watch 同款規則)。
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CDP_SHOT = os.path.join(HERE, 'a0_cdp_shot.py')
BOT_ENV = os.path.join(os.path.dirname(HERE), 'bot', '.env')
STATE_FILE = os.path.expanduser('~/.maplab/gift_watch_state.json')
LOG_FILE = os.path.expanduser('~/.maplab/gift_watch.log')
CDP = 'http://127.0.0.1:18800'
SLUGS = ['claude-code-plushies', 'claude-code-stickers']
ALERT_COOLDOWN = 6 * 3600


def log(msg):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(time.strftime('%Y-%m-%dT%H:%M:%S') + ' ' + msg + '\n')
    except OSError:
        pass


def load_bot_env():
    token = chat = None
    with open(BOT_ENV) as f:
        for raw in f:
            raw = raw.strip()
            if raw.startswith('TELEGRAM_BOT_TOKEN='):
                token = raw.split('=', 1)[1].strip().strip('"').strip("'")
            elif raw.startswith('OWNER_CHAT_ID='):
                chat = raw.split('=', 1)[1].strip().strip('"').strip("'")
    if not token or not chat:
        raise SystemExit('BOT_ENV_MISSING_FIELDS')
    return token, chat


def send(token, chat, text):
    data = urllib.parse.urlencode({'chat_id': chat, 'text': text}).encode()
    req = urllib.request.Request(
        'https://api.telegram.org/bot%s/sendMessage' % token, data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ok = json.load(resp).get('ok', False)
        log('push ok=%s' % ok)
        return ok
    except Exception as exc:
        log('push failed %s' % type(exc).__name__)
        return False


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state):
    tmp = STATE_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


def check_slug(slug):
    """回傳 (status, textlen):status = expired / open / error。開完分頁即關。"""
    url = 'https://app.brilliantmade.com/r/%s' % slug
    try:
        r = subprocess.run(
            [sys.executable, CDP_SHOT, 'open', url, 'giftwatch_%s.png' % slug],
            capture_output=True, text=True, timeout=120)
        out = r.stdout
        t = subprocess.run(
            [sys.executable, CDP_SHOT, 'text', slug],
            capture_output=True, text=True, timeout=60)
        txt = t.stdout or ''
    except Exception as exc:
        log('%s cdp error %s' % (slug, type(exc).__name__))
        return 'error', 0
    finally:
        m = re.search(r'tab_id: ([0-9A-F]+)', locals().get('out', '') or '')
        if m:
            try:
                urllib.request.urlopen('%s/json/close/%s' % (CDP, m.group(1)), timeout=10)
            except Exception:
                pass
    low = txt.lower()
    if 'expired' in low or 'sorry we missed you' in low:
        return 'expired', len(txt)
    if len(txt) < 150:
        return 'error', len(txt)
    return 'open', len(txt)


def main():
    state = load_state()
    now = time.time()
    token = chat = None
    for slug in SLUGS:
        status, n = check_slug(slug)
        log('%s status=%s textlen=%d' % (slug, status, n))
        if status != 'open':
            continue
        last = state.get(slug, 0)
        if now - last < ALERT_COOLDOWN:
            continue
        if token is None:
            token, chat = load_bot_env()
        kind = '玩偶' if 'plushies' in slug else '貼紙'
        send(token, chat,
             '[玩具監看] Anthropic Claude %s兌換頁重新開放了!頁面已不是 expired。'
             '本線下一輪續接會立刻嘗試代填(地址已在案,還缺收件人姓名就會先問)。'
             '網址: https://app.brilliantmade.com/r/%s' % (kind, slug))
        state[slug] = now
        save_state(state)


if __name__ == '__main__':
    main()
