#!/usr/bin/env python3
"""a0_cdp_shot.py — 走 Chrome 除錯埠出真圖，完全不碰 macOS 螢幕錄製權限。

背景（2026-09-30）：screencapture 一直回 "could not create image from display"，
卡在 TCC 螢幕錄製那層，而 TCC 提示被拒過就不會再彈。根因解法不是求 Owner 去勾，
而是換取像路徑：Chrome 的 Page.captureScreenshot 是瀏覽器自己把 render tree 畫成 PNG，
不經過視窗伺服器，所以零系統權限。

只用標準函式庫（本機三顆 python 都沒有 websockets），自帶最小 WebSocket 客戶端。

用法：
    a0_cdp_shot.py list
    a0_cdp_shot.py shot <分頁網址關鍵字> [輸出檔名]
    a0_cdp_shot.py open <網址> [輸出檔名]      # 新開分頁、等載入、出圖
    a0_cdp_shot.py text <分頁網址關鍵字>        # 讀整頁文字

輸出一律落 ~/.maplab/screenshots/（不入版控）。
"""
import base64
import json
import os
import socket
import struct
import sys
import time
import urllib.parse
import urllib.request

PORT = int(os.environ.get("CDP_PORT", "18800"))
SHOT_DIR = os.path.expanduser("~/.maplab/screenshots")


def cdp_http(path, method="GET"):
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (PORT, path), method=method)
    return json.load(urllib.request.urlopen(req, timeout=15))


def pages():
    return [t for t in cdp_http("/json/list") if t.get("type") == "page"]


class WS:
    """最小 WebSocket 客戶端：只夠講 CDP，不做 ping/pong 與分片重組以外的事。"""

    def __init__(self, ws_url):
        u = urllib.parse.urlparse(ws_url)
        path = u.path + (("?" + u.query) if u.query else "")
        host, port = u.hostname, u.port or PORT
        self.s = socket.create_connection((host, port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            "GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\n"
            "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n" % (path, host, port, key)
        ).encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise RuntimeError("handshake closed")
            buf += chunk
        head, rest = buf.split(b"\r\n\r\n", 1)
        status = head.split(b"\r\n")[0]
        if b"101" not in status:
            raise RuntimeError("no upgrade: %s" % status.decode())
        self.pending = bytearray(rest)
        self.seq = 0

    def _exact(self, n):
        while len(self.pending) < n:
            chunk = self.s.recv(65536)
            if not chunk:
                raise RuntimeError("socket closed")
            self.pending.extend(chunk)
        out = bytes(self.pending[:n])
        del self.pending[:n]
        return out

    def _send(self, method, params):
        self.seq += 1
        payload = json.dumps({"id": self.seq, "method": method, "params": params or {}}).encode()
        mask = os.urandom(4)
        n = len(payload)
        if n < 126:
            hdr = struct.pack("!BB", 0x81, 0x80 | n)
        elif n < 65536:
            hdr = struct.pack("!BBH", 0x81, 0x80 | 126, n)
        else:
            hdr = struct.pack("!BBQ", 0x81, 0x80 | 127, n)
        self.s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))
        return self.seq

    def _recv(self):
        chunks = []
        while True:
            b0, b1 = struct.unpack("!BB", self._exact(2))
            fin, op, n = b0 & 0x80, b0 & 0x0F, b1 & 0x7F
            if n == 126:
                n = struct.unpack("!H", self._exact(2))[0]
            elif n == 127:
                n = struct.unpack("!Q", self._exact(8))[0]
            if b1 & 0x80:
                self._exact(4)
            chunks.append(self._exact(n))
            if op == 0x8:
                raise RuntimeError("server close frame")
            if fin:
                break
        return json.loads(b"".join(chunks).decode("utf-8", "replace"))

    def call(self, method, params=None, max_frames=600):
        want = self._send(method, params)
        for _ in range(max_frames):
            msg = self._recv()
            if msg.get("id") == want:
                return msg
        raise RuntimeError("no reply for %s" % method)

    def js(self, expr):
        r = self.call("Runtime.evaluate", {"returnByValue": True, "expression": expr})
        if "error" in r:
            return None
        return r.get("result", {}).get("result", {}).get("value")

    def viewport(self, w=1600, h=1400):
        self.call("Emulation.setDeviceMetricsOverride",
                  {"width": w, "height": h, "deviceScaleFactor": 1, "mobile": False})

    def screenshot(self, out_path, beyond_viewport=True):
        r = self.call("Page.captureScreenshot",
                      {"format": "png", "captureBeyondViewport": beyond_viewport})
        if "error" in r:
            raise RuntimeError("CDP error: %s" % r["error"])
        data = base64.b64decode(r["result"]["data"])
        os.makedirs(SHOT_DIR, exist_ok=True)
        with open(out_path, "wb") as fh:
            fh.write(data)
        return len(data)


def find_page(needle):
    hits = [t for t in pages() if needle in (t.get("url") or "") or needle in (t.get("title") or "")]
    if not hits:
        raise SystemExit("找不到分頁：%s（用 list 看現有分頁）" % needle)
    return hits[0]


def out_path(name, default):
    return os.path.join(SHOT_DIR, name or default)


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    cmd = argv[1]

    if cmd == "list":
        for t in pages():
            # 網址夾帶權杖，一律砍 query 再印
            url = (t.get("url") or "").split("?")[0].split("#")[0]
            print("%-40s %s" % ((t.get("title") or "")[:40], url[:90]))
        return

    if cmd == "text":
        ws = WS(find_page(argv[2])["webSocketDebuggerUrl"])
        print(ws.js("(document.body.innerText||'').slice(0,20000)"))
        return

    if cmd == "shot":
        t = find_page(argv[2])
        ws = WS(t["webSocketDebuggerUrl"])
        ws.viewport()
        p = out_path(argv[3] if len(argv) > 3 else None, "a0_cdp_shot.png")
        print("title:", (t.get("title") or "")[:80])
        print("OK bytes=%d -> %s" % (ws.screenshot(p), p))
        return

    if cmd == "open":
        url = argv[2]
        tab = cdp_http("/json/new?" + urllib.parse.quote(url, safe=":/?=&"), method="PUT")
        ws = WS(tab["webSocketDebuggerUrl"])
        ws.viewport()
        last = 0
        for _ in range(15):          # 最多等 60 秒，文字長度連兩次不再長就當載完
            time.sleep(4)
            n = ws.js("(document.body.innerText||'').length") or 0
            if n and n == last:
                break
            last = n
        p = out_path(argv[3] if len(argv) > 3 else None, "a0_cdp_open.png")
        print("title:", ws.js("document.title"))
        print("textlen:", last, "dialog:", ws.js("!!document.querySelector('[role=dialog]')"))
        print("OK bytes=%d -> %s" % (ws.screenshot(p), p))
        print("tab_id:", tab["id"], "(記得清掉多開的分頁)")
        return

    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
