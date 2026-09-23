#!/usr/bin/env python3
"""MXF/TMF spread alert watcher (Owner 5527, 2026-09-20).

Read-only observer of the spread_paper engine's runtime report. Never writes
into investment-os, never places orders, never reads credentials beyond the
Telegram bot token consumed in-process (value never printed or logged).

Alerts pushed to Owner via Telegram:
  1. spread    - same-month MXF-TMF point gap >= threshold (the opportunity bell)
  2. entry     - engine itself judged ENTRY (edge cleared full round-trip costs)
  3. halt      - engine halted a lane (needs reconciliation)
  4. stale     - latest.json stopped updating (engine heartbeat lost)
  5. quality   - persistent in-session quote-quality failure (extreme-day marker)
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

LATEST = '/Users/pagemacmini/investment-os/reports/spread_paper/runtime/latest.json'
BOT_ENV = '/Users/pagemacmini/maplab-ai-handbook/bot/.env'
STATE_DIR = os.path.expanduser('~/.maplab')
STATE_FILE = os.path.join(STATE_DIR, 'spread_alert_state.json')
PID_FILE = os.path.join(STATE_DIR, 'spread_alert.pid')
LOG_FILE = os.path.join(STATE_DIR, 'spread_alert.log')

SPREAD_ALERT_POINTS = 10.0      # |MXF-TMF| points that ring the bell
SPREAD_STRONG_POINTS = 30.0
STALE_SECONDS = 180
QUALITY_PERSIST_SECONDS = 600
QUALITY_REASONS = {'CROSS_LEG_QUOTE_SKEW', 'QUOTE_STALE_OR_CLOCK_SKEW',
                   'QUOTE_MISSING', 'BOOK_CROSSED_OR_LOCKED',
                   'INSUFFICIENT_DISPLAYED_DEPTH'}
COOLDOWN = {'spread': 600, 'spread_strong': 300, 'entry': 600,
            'halt': 3600, 'stale': 1800, 'quality': 3600, 'boot': 0}
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


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {'last_alert': {}, 'reason_since': {}}


def save_state(state):
    tmp = STATE_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


def cooled(state, kind, now_ts):
    return now_ts - state['last_alert'].get(kind, 0) >= COOLDOWN.get(kind, 600)


def mark(state, kind, now_ts):
    state['last_alert'][kind] = now_ts
    save_state(state)


def in_session(now_tpe):
    wd, t = now_tpe.weekday(), now_tpe.time()
    day = t >= datetime.strptime('08:40', '%H:%M').time() and t <= datetime.strptime('13:50', '%H:%M').time()
    night = t >= datetime.strptime('14:55', '%H:%M').time()
    early = t <= datetime.strptime('05:05', '%H:%M').time()
    if wd == 5:  # Saturday: only the tail of Friday's night session
        return early
    if wd == 6:
        return False
    if wd == 0:  # Monday has no carried-over early session
        return day or night
    return day or night or early


def tw_points(tw):
    legs = tw.get('legs')
    if not legs or len(legs) != 2:
        return None
    try:
        mxf = next(l['reference_price'] for l in legs if l.get('multiplier') == 50)
        tmf = next(l['reference_price'] for l in legs if l.get('multiplier') == 10)
    except StopIteration:
        return None
    return mxf - tmf, mxf, tmf


def check_once(token, chat, state):
    now = datetime.now(timezone.utc)
    now_ts = time.time()
    try:
        with open(LATEST) as f:
            latest = json.load(f)
    except (OSError, ValueError):
        if cooled(state, 'stale', now_ts):
            send(token, chat, '[價差警報器] 讀不到引擎狀態檔 latest.json,可能引擎或磁碟異常。')
            mark(state, 'stale', now_ts)
        return

    at = latest.get('at')
    try:
        age = (now - datetime.fromisoformat(at)).total_seconds()
    except (TypeError, ValueError):
        age = None
    if age is not None and age > STALE_SECONDS:
        if cooled(state, 'stale', now_ts):
            send(token, chat, '[價差警報器] 引擎心跳異常:狀態檔已 %d 分鐘沒更新(pid %s)。模擬引擎可能停了,建議查看。' % (age // 60, latest.get('pid')))
            mark(state, 'stale', now_ts)
        return  # numbers below would be stale too
    if age is not None and age <= STALE_SECONDS:
        state['last_alert'].pop('stale', None)

    halted = latest.get('halted') or {}
    if halted and cooled(state, 'halt', now_ts):
        send(token, chat, '[價差警報器] 引擎有策略線被停止,需要對帳:%s' % json.dumps(halted, ensure_ascii=False))
        mark(state, 'halt', now_ts)

    tw = (latest.get('strategies') or {}).get('tw') or {}
    reason = tw.get('reason', 'UNKNOWN')

    pts = tw_points(tw)
    if pts:
        diff, mxf, tmf = pts
        adiff = abs(diff)
        net_edge = tw.get('net_edge')
        if adiff >= SPREAD_STRONG_POINTS and cooled(state, 'spread_strong', now_ts):
            send(token, chat, '[價差警報器] 大裂縫!同月小台微台價差 %.1f 點(小台 %.0f / 微台 %.0f)。引擎判定 %s,扣全部成本後淨值 %s 元。%s' % (
                diff, mxf, tmf, reason, '%.0f' % net_edge if net_edge is not None else '不明',
                '引擎條件滿足會自動進模擬單並通知。' if reason == 'ENTRY' else '尚未過引擎成本檻,要動手是你的裁量。'))
            mark(state, 'spread_strong', now_ts)
            mark(state, 'spread', now_ts)
        elif adiff >= SPREAD_ALERT_POINTS and cooled(state, 'spread', now_ts):
            send(token, chat, '[價差警報器] 同月小台微台價差 %.1f 點(小台 %.0f / 微台 %.0f),超過 %d 點警戒線。引擎判定 %s,扣全成本淨值 %s 元。' % (
                diff, mxf, tmf, int(SPREAD_ALERT_POINTS), reason,
                '%.0f' % net_edge if net_edge is not None else '不明'))
            mark(state, 'spread', now_ts)

    if reason == 'ENTRY' and cooled(state, 'entry', now_ts):
        send(token, chat, '[價差警報器] 引擎判定小微價差可進場(淨利差已蓋過全成本),正常流程會自動進模擬單並另行通知成交。')
        mark(state, 'entry', now_ts)

    now_tpe = datetime.now(TPE)
    if in_session(now_tpe) and reason in QUALITY_REASONS:
        since = state['reason_since'].get(reason)
        if since is None:
            state['reason_since'] = {reason: now_ts}
            save_state(state)
        elif now_ts - since >= QUALITY_PERSIST_SECONDS and cooled(state, 'quality', now_ts):
            send(token, chat, '[價差警報器] 盤中報價品質連續異常超過 %d 分鐘(%s)。這是極端行情或線路問題的徵兆;若市場劇烈波動,大價差可能出現但未必成交得到。' % (QUALITY_PERSIST_SECONDS // 60, reason))
            mark(state, 'quality', now_ts)
    else:
        if state.get('reason_since'):
            state['reason_since'] = {}
            save_state(state)


def daemonize():
    """Double-fork so the watcher survives the launching window (5404 lesson)."""
    if os.fork() > 0:
        print('DAEMON_LAUNCHED')
        os._exit(0)
    os.setsid()
    if os.fork() > 0:
        os._exit(0)
    devnull = os.open(os.devnull, os.O_RDWR)
    logfd = os.open(LOG_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.dup2(devnull, 0)
    os.dup2(logfd, 1)
    os.dup2(logfd, 2)


def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    if '--daemon' in sys.argv:
        daemonize()
    if os.path.exists(PID_FILE):
        try:
            old = int(open(PID_FILE).read().strip())
            os.kill(old, 0)
            raise SystemExit('ALREADY_RUNNING pid=%d' % old)
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    token, chat = load_bot_env()
    state = load_state()
    log('watcher started pid=%d' % os.getpid())
    if '--boot-notify' in sys.argv:
        send(token, chat, '[價差警報器] 上線(測試訊息)。監看中:同月小台微台價差>=%d點推播、>=%d點強推播、引擎可進場、引擎心跳斷線、盤中報價品質異常。狀態檔來源=模擬引擎即時報價。' % (int(SPREAD_ALERT_POINTS), int(SPREAD_STRONG_POINTS)))
    last_hb = 0.0
    while True:
        try:
            check_once(token, chat, state)
        except Exception as exc:
            log('check error %s: %s' % (type(exc).__name__, exc))
        if time.time() - last_hb >= 3600:
            log('heartbeat alive')
            last_hb = time.time()
        time.sleep(10 if in_session(datetime.now(TPE)) else 60)


if __name__ == '__main__':
    main()
