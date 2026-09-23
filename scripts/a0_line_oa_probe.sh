#!/bin/bash
# a0_line_oa_probe.sh — read-only recon of the Owner's LINE OA canned/preset
# templates via the local Chrome login session (Owner-sanctioned Chrome cookie
# borrow, msg 5553/5606). One-shot; read-only; cookie VALUES are never logged,
# printed, or committed — only in-process to build the request header.
# Preset template text is the Owner's OWN business content (not customer PII),
# so it may be logged locally and reported back; raw customer chat is NOT touched.
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOG="$HOME/.maplab/a0_line_oa_probe.log"
mkdir -p "$HOME/.maplab"
BOT_ENV="/Users/pagemacmini/maplab-ai-handbook/bot/.env"

/usr/bin/python3 - "$LOG" <<'PY'
import sys, json, urllib.request, urllib.error
LOG = sys.argv[1]
def w(msg):
    with open(LOG, "a") as f:
        f.write(msg + "\n")

import datetime
# time passed in from shell to avoid new-Date restriction is not needed here (real subprocess)
w("[probe start] LINE OA canned-template recon")

# 1) extract Chrome cookies for .line.biz in-process (values never written out)
try:
    from yt_dlp.cookies import extract_cookies_from_browser
    jar = extract_cookies_from_browser("chrome")
except Exception as e:
    w("[FATAL] cannot load chrome cookies via yt_dlp: %r" % e)
    sys.exit(0)

def cookie_header(domain_sub):
    parts = []
    for c in jar:
        if c.domain and (domain_sub in c.domain):
            parts.append("%s=%s" % (c.name, c.value))
    return "; ".join(parts), len(parts)

def get(url, host):
    hdr, n = cookie_header("line.biz")
    if n == 0:
        w("[skip] no line.biz cookies in Chrome for %s" % url)
        return None
    req = urllib.request.Request(url, headers={
        "Cookie": hdr,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "x-requested-with": "XMLHttpRequest",
        "Referer": "https://%s/" % host,
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", "replace")
            w("[%s] %s  (%d bytes, cookies=%d)" % (r.status, url, len(body), n))
            return body
    except urllib.error.HTTPError as e:
        w("[HTTP %s] %s" % (e.code, url))
        return None
    except Exception as e:
        w("[ERR] %s  %r" % (url, e))
        return None

# 2) discover botId list (chat.line.biz frontend API)
bot_ids = []
for url in ["https://chat.line.biz/api/v2/bots",
            "https://chat.line.biz/api/v1/bots"]:
    body = get(url, "chat.line.biz")
    if body:
        try:
            data = json.loads(body)
            items = data.get("list") or data.get("bots") or (data if isinstance(data, list) else [])
            for b in items:
                bid = b.get("botId") or b.get("id")
                name = b.get("name") or b.get("displayName") or ""
                if bid:
                    bot_ids.append(bid)
                    w("  bot: id=%s name=%s" % (bid, name))
        except Exception as e:
            w("  [parse bots fail] %r ; head=%s" % (e, body[:200]))
        break

# 3) for each bot, try candidate canned/fixed/suggestion template endpoints
cand = [
    "https://chat.line.biz/api/v2/bots/{b}/suggestions",
    "https://chat.line.biz/api/v2/bots/{b}/fixedMenus",
    "https://chat.line.biz/api/v2/bots/{b}/messageTemplates",
    "https://chat.line.biz/api/v2/bots/{b}/templates",
    "https://chat.line.biz/api/v2/bots/{b}/cannedMessages",
    "https://chat.line.biz/api/v2/bots/{b}/quickReplies",
]
for b in bot_ids:
    for tmpl in cand:
        url = tmpl.format(b=b)
        body = get(url, "chat.line.biz")
        if body and body.strip() not in ("", "[]", "{}"):
            w("  ---payload %s---" % url)
            w(body[:4000])

w("[probe done]")
PY

# self-push a short verdict to Owner (bot 代答); NO cookie values, summary only
TOKEN="$(grep '^TELEGRAM_BOT_TOKEN=' "$BOT_ENV" | cut -d= -f2-)"
CHAT="$(grep '^OWNER_CHAT_ID=' "$BOT_ENV" | cut -d= -f2-)"
TAIL="$(tail -n 25 "$LOG" 2>/dev/null)"
if echo "$TAIL" | grep -q "payload"; then
  VERDICT="讀到罐頭模板了,內容我整理後下則回報"
elif echo "$TAIL" | grep -q "no line.biz cookies"; then
  VERDICT="Chrome 沒有 line.biz 登入 cookie(可能沒開過網頁版或已登出),退回請 Owner 開著 chat.line.biz 登入頁"
elif echo "$TAIL" | grep -qE "HTTP 401|HTTP 403"; then
  VERDICT="cookie 被 LINE 端拒(401/403),session 可能過期,請 Owner 重登一次網頁版"
else
  VERDICT="通道有回應但未命中模板端點,改用截圖最快"
fi
if [ -n "${TOKEN:-}" ] && [ -n "${CHAT:-}" ]; then
  curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT}" \
    --data-urlencode "text=【bot 代答・LINE OA 模板探測(5606)】${VERDICT}" >/dev/null
fi
