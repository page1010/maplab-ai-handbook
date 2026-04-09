#!/usr/bin/env python3
"""
Google Ads OAuth2 本機授權腳本
用途：拿 refresh_token，不需要 OAuth Playground 或 Cloud Console 設定
作法：用 localhost redirect，本機起一個暫時的 HTTP server 接 code
"""

import http.server
import urllib.parse
import webbrowser
import json
import urllib.request
import threading

# 從環境變數讀取，避免 secrets 進入 git history
# 設定方式：export GOOGLE_ADS_CLIENT_ID="..." GOOGLE_ADS_CLIENT_SECRET="..."
# 或在 ~/.claude/.mcp.json 的 google-ads 區塊查詢現有值
import os
CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")
if not CLIENT_ID or not CLIENT_SECRET:
    raise SystemExit("ERROR: 請設定環境變數 GOOGLE_ADS_CLIENT_ID 和 GOOGLE_ADS_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8765/callback"
SCOPE = "https://www.googleapis.com/auth/adwords"

auth_code = None
server_done = threading.Event()

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h2>OK! \xe6\x8e\x88\xe6\xac\x8a\xe6\x88\x90\xe5\x8a\x9f\xef\xbc\x8c\xe8\xab\x8b\xe5\x9b\x9e terminal \xe6\x9f\xa5\xe7\x9c\x8b\xe7\xb5\x90\xe6\x9e\x9c</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: no code")
        server_done.set()

    def log_message(self, format, *args):
        pass  # 不印 log

def main():
    # 1. 建授權 URL
    auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={urllib.parse.quote(SCOPE)}"
        "&response_type=code"
        "&access_type=offline"
        "&prompt=consent"
    )

    # 2. 起本機 server
    server = http.server.HTTPServer(("localhost", 8765), CallbackHandler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    # 3. 開瀏覽器
    print("\n正在開啟瀏覽器進行 Google 授權...")
    print("請登入你的 Google 帳號並允許存取 Google Ads\n")
    webbrowser.open(auth_url)

    # 4. 等回調
    server_done.wait(timeout=120)
    server.shutdown()

    if not auth_code:
        print("ERROR: 沒收到授權碼，請重試")
        return

    # 5. 換 refresh token
    token_data = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=token_data,
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())

    refresh_token = tokens.get("refresh_token")
    if refresh_token:
        print("=" * 60)
        print("✅ 成功取得 refresh_token：")
        print(refresh_token)
        print("=" * 60)
        print("\n接下來在 Claude Code 裡把這個 token 貼給 A1 寫入 .mcp.json")
    else:
        print("ERROR: 沒有 refresh_token，回傳內容：", tokens)

if __name__ == "__main__":
    main()
