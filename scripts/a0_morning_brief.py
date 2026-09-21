#!/usr/bin/env python3
"""Weekday 08:50 morning brief pusher (Owner 5583, 2026-09-21).

Read-only observer: reads the spread_paper runtime report, the spread-alert
watcher log and the quota self-estimate, composes one Telegram message and
sends it via the same bot channel the watcher uses. Never writes into
investment-os, never places orders; bot token consumed in-process only
(value never printed or logged).
"""
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

LATEST = '/Users/pagemacmini/investment-os/reports/spread_paper/runtime/latest.json'
BOT_ENV = '/Users/pagemacmini/maplab-ai-handbook/bot/.env'
QUOTA = '/Users/pagemacmini/maplab-ai-handbook/scripts/a0_quota_estimate.py'
WATCH_LOG = os.path.expanduser('~/.maplab/spread_alert.log')
STATE_DIR = os.path.expanduser('~/.maplab')
PID_FILE = os.path.join(STATE_DIR, 'a0_morning_brief.pid')
LOG_FILE = os.path.join(STATE_DIR, 'a0_morning_brief.log')
SEND_AT = (8, 50)  # Taipei, weekdays only
TPE = timezone(timedelta(hours=8))


def log(msg):
    line = datetime.now(TPE).isoformat(timespec='seconds') + ' ' + msg
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
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
        log('push ok=%s len=%d' % (ok, len(text)))
        return ok
    except Exception as exc:
        log('push failed %s' % type(exc).__name__)
        return False


def fmt_twd(v):
    try:
        return format(int(round(v)), ',')
    except (TypeError, ValueError):
        return str(v)


def compose():
    lines = ['【bot 代答・每日早報 %s】' % datetime.now(TPE).strftime('%m/%d %H:%M')]
    try:
        with open(LATEST) as f:
            d = json.load(f)
        at = d.get('at', '')
        fresh = ''
        try:
            age = time.time() - datetime.fromisoformat(at).timestamp()
            fresh = '正常' if age < 300 else '過舊(%d分)' % (age // 60)
        except ValueError:
            fresh = '無法判讀'
        twd = d.get('accounts', {}).get('TWD', {})
        lines.append('引擎:%s,快照%s。模擬帳本:專案含驗收損益 %s 元,權益 %s 元,錨定六籃 %s 元,動用 %s 元。' % (
            '活著' if d.get('pid') else '狀態不明', fresh,
            fmt_twd(twd.get('project_pnl_including_acceptance')),
            fmt_twd(twd.get('research_equity_including_acceptance')),
            fmt_twd(twd.get('anchor_net_pnl_separate')),
            fmt_twd(twd.get('reserved_capital_now'))))
        tw = d.get('strategies', {}).get('tw', {})
        legs = tw.get('legs') or []
        if len(legs) == 2:
            gap = abs((legs[0].get('reference_price') or 0) - (legs[1].get('reference_price') or 0))
            lines.append('大小台價差:%.1f 點(響鈴門檻 10 點),引擎判定 %s。' % (gap, tw.get('reason', '')))
    except Exception as exc:
        lines.append('帳本讀取失敗:%s(請查引擎)。' % type(exc).__name__)
    try:
        with open(WATCH_LOG) as f:
            tail = f.read().strip().splitlines()[-1]
        lines.append('警報器最後心跳:%s。' % tail.split(' ')[0])
    except Exception:
        lines.append('警報器心跳讀不到(請查 daemon)。')
    try:
        q = subprocess.run(['/usr/bin/python3', QUOTA], capture_output=True,
                           text=True, timeout=60).stdout.strip()
        if q:
            lines.append(q)
    except Exception:
        pass
    return '\n'.join(lines)


def seconds_to_next_send():
    now = datetime.now(TPE)
    target = now.replace(hour=SEND_AT[0], minute=SEND_AT[1], second=0, microsecond=0)
    while target <= now or target.weekday() >= 5:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def main():
    import sys
    if '--once' in sys.argv:  # dry-run: compose and print, no send, no pidfile
        print(compose())
        return
    os.makedirs(STATE_DIR, exist_ok=True)
    old = None
    try:
        with open(PID_FILE) as f:
            old = int(f.read().strip())
    except (OSError, ValueError):
        pass
    if old:
        try:
            os.kill(old, 0)
            raise SystemExit('ALREADY_RUNNING pid=%d' % old)
        except ProcessLookupError:
            pass
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    log('daemon started pid=%d' % os.getpid())
    token, chat = load_bot_env()
    while True:
        time.sleep(max(30, seconds_to_next_send()))
        now = datetime.now(TPE)
        if now.weekday() < 5 and (now.hour, now.minute) >= SEND_AT and now.hour < 10:
            send(token, chat, compose())
            time.sleep(120)  # step past the send minute


if __name__ == '__main__':
    main()
