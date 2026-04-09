# Google Ads API 鑰匙技能書

版本：v1.0 | 建立：2026-04-09 | 維護者：A1

---

## 鑰匙位置

存放在 `~/.claude/.mcp.json` 的 `google-ads` 區塊：

| 變數 | 說明 |
|------|------|
| `GOOGLE_ADS_CLIENT_ID` | OAuth 2.0 用戶端 ID（Web 類型） |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth 2.0 用戶端密鑰 |
| `GOOGLE_ADS_REFRESH_TOKEN` | 長效 Refresh Token（需手動更新） |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads API Developer Token |
| `GOOGLE_ADS_CUSTOMER_ID` | Ads 帳號 ID（不含 dash） |

目前使用的 Client ID（Web 類型）：存放在 `~/.claude/.mcp.json` 的 `GOOGLE_ADS_CLIENT_ID` 欄位，不記錄在 repo。

---

## 取用方法

### 透過 MCP（推薦）

A1 Claude Code session 中直接呼叫 `google-ads` MCP tools：
```
mcp__google-ads__get_campaign_performance(...)
mcp__google-ads__get_ad_performance(...)
mcp__google-ads__list_accounts(...)
```

---

## ⚠️ Refresh Token 更新 SOP（踩坑紀錄 2026-04-09）

### 必讀：OAuth 用戶端類型必須是「網頁應用程式」

**桌面應用程式類型沒有 redirect URI 設定選項**，無法用於下列任何方法。  
建立憑證時務必選「**網頁應用程式（Web Application）**」。

---

### 方法 A：本機 Python 腳本（推薦，不需要手動貼 URI）

當 Refresh Token 過期或被撤銷時，用此方法重新授權：

**前置條件：** Google Cloud Console 的 OAuth 用戶端「已授權的重新導向 URI」需加入：
```
http://localhost:8765/callback
```

**腳本：**

```python
#!/usr/bin/env python3
"""
取得 Google Ads OAuth Refresh Token
用法：python3 get_google_ads_token.py
瀏覽器會自動開啟，登入後自動寫入 token
"""
import http.server
import urllib.parse
import webbrowser
import requests
import json
import re
import os

# 從環境變數讀取，不要 hardcode 進腳本
import os
CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8765/callback"
SCOPE = "https://www.googleapis.com/auth/adwords"
MCP_JSON_PATH = os.path.expanduser("~/.claude/.mcp.json")

auth_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={urllib.parse.quote(SCOPE)}"
    "&response_type=code"
    "&access_type=offline"
    "&prompt=consent"
)

received_code = None

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global received_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        received_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h1>OK! Token received. You can close this tab.</h1>")
    def log_message(self, *args):
        pass

print("Opening browser for Google authorization...")
webbrowser.open(auth_url)

server = http.server.HTTPServer(("localhost", 8765), Handler)
server.handle_request()

# Exchange code for tokens
resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": received_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
})
tokens = resp.json()
refresh_token = tokens.get("refresh_token")

if not refresh_token:
    print("ERROR: No refresh token received:", tokens)
    exit(1)

print(f"New refresh_token: {refresh_token}")

# Write to .mcp.json
with open(MCP_JSON_PATH, "r") as f:
    content = f.read()

content = re.sub(
    r'("GOOGLE_ADS_REFRESH_TOKEN"\s*:\s*")[^"]*(")',
    f'\\g<1>{refresh_token}\\2',
    content
)

with open(MCP_JSON_PATH, "w") as f:
    f.write(content)

print("✅ .mcp.json updated! Run /mcp in Claude Code to reconnect.")
```

**執行方式：**
```bash
python3 ~/maplab-ai-handbook/scripts/get_google_ads_token.py
```

瀏覽器自動開啟 → 登入 Google（Ads 管理員帳號）→ 允許 → 自動寫入 `.mcp.json`。

完成後在 Claude Code 跑 `/mcp` 確認 google-ads 狀態為 connected。

---

### 方法 B：OAuth Playground（備用）

只在腳本不可用時使用。需先在 Cloud Console 加：
```
https://developers.google.com/oauthplayground
```

進入 [OAuth Playground](https://developers.google.com/oauthplayground)：
1. 右上齒輪 ⚙️ → 勾「Use your own OAuth credentials」
2. 填入 Client ID + Client Secret
3. 左側 Scope 選 `https://www.googleapis.com/auth/adwords`
4. Authorize APIs → 登入 → Exchange code for tokens
5. 複製 `refresh_token` → 手動更新 `.mcp.json`

---

## Cloud Console 快速導航

- 憑證頁面：`https://console.cloud.google.com/apis/credentials`
- 找「OAuth 2.0 用戶端 ID」表格 → Web 類型那一列 → 鉛筆 ✏️ 編輯
- 「已授權的重新導向 URI」加入所需 URI → 儲存 → 等 30 秒生效

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ 讀取廣告成效 | 活動、廣告群組、關鍵字效能 |
| ✅ 讀取帳戶資訊 | 帳號列表、幣別設定 |
| ✅ 查詢 GAQL | 自訂報表查詢 |
| ✅ 更新廣告狀態 | 啟動/暫停廣告活動 |
| ✅ 更新預算 | 修改廣告活動預算 |

---

## 禁止操作

- ❌ 刪除廣告活動（需 Owner 親自確認）
- ❌ 修改出價策略（Smart Bidding 設定）
- ❌ 建立全新廣告活動（需 Owner 審核）

---

## 踩坑紀錄

### 坑 1：桌面應用程式型 OAuth 沒有 redirect URI
**現象**：`redirect_uri_mismatch` 400 錯誤，或 OAuth Playground 選項被擋。  
**原因**：桌面應用程式型 OAuth client 不支援 redirect URI 設定。  
**解法**：到 Cloud Console 建立「網頁應用程式」類型的新 OAuth 用戶端。

### 坑 2：OAuth Playground 用 Google 自己的 Client
**現象**：拿到 refresh token 但 MCP 回傳 `unauthorized_client`。  
**原因**：未在 Playground 設定 Use your own OAuth credentials，token 配對了 Google 的 client 而非自己的。  
**解法**：齒輪 → 勾選 Use your own OAuth credentials → 填自己的 Client ID/Secret。

### 坑 3：Refresh Token 只發一次
**現象**：重跑授權流程沒有拿到新的 `refresh_token`。  
**原因**：Google 只在第一次授權（或加 `prompt=consent`）時回傳 refresh token。  
**解法**：授權 URL 加 `&prompt=consent&access_type=offline`（腳本已內建）。
