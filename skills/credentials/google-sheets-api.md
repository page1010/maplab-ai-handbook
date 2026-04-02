# Google Sheets API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

| 檔案 | 路徑 | 說明 |
|------|------|------|
| OAuth 憑證 | `~/.claude/mcp-keys/google-credentials.json` | OAuth 2.0 client_id / client_secret |
| Access Token | `~/.claude/mcp-keys/google-token.json` | access_token + refresh_token（自動刷新） |

---

## 取用方法

### A. 透過 MCP（推薦，A1 Claude Code session 內）

直接呼叫 `google-sheets` MCP tool，不需要手動取 token：
```
# 在 Claude Code interactive session 內直接呼叫：
# mcp__google-sheets__get_sheet_data(...)
```

### B. Python（Colab / 腳本）

```python
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# 載入 token（本地執行，路徑需有存取權限）
TOKEN_PATH = "/Users/pagemacmini/.claude/mcp-keys/google-token.json"
CREDENTIALS_PATH = "/Users/pagemacmini/.claude/mcp-keys/google-credentials.json"

with open(TOKEN_PATH) as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data.get("access_token"),
    refresh_token=token_data.get("refresh_token"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=json.load(open(CREDENTIALS_PATH))["installed"]["client_id"],
    client_secret=json.load(open(CREDENTIALS_PATH))["installed"]["client_secret"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

# 若 token 過期，自動刷新
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
```

---

## 可用範圍

| 允許操作 | 對象 |
|---------|------|
| ✅ 讀取 / 寫入 | MAPLAB_外燴系統_v0.1（Items, QUOTE_DRAFT, DST 等所有工作表）（舊名 MAPLAB_MasterData）|
| ✅ 讀取 | MAPLAB_外燴系統_v0.1 |
| ✅ 讀取 | 所有共用到此帳號的 Spreadsheet |

---

## 禁止操作

- ❌ 刪除工作表（deleteDimension / deleteSheet）
- ❌ 修改 Items E 欄成本資料（Owner 手動維護，Agent 不動）
- ❌ 修改 Owner 手動設定的試算表格式

---

## Token 過期恢復

```bash
# 在終端機執行，觸發 MCP server 重新授權
uvx mcp-google-sheets@latest
# 啟動後會印出 OAuth URL → 瀏覽器授權 → token 自動寫回 google-token.json
```

或在 Claude Code session 中直接呼叫任何 Sheets tool，若 401 會提示重新授權。

詳見 `skills/mcp-usage-guide.md` §3b。
