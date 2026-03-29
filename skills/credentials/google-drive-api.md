# Google Drive API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

與 Google Sheets **共用同一組 OAuth 憑證**：

| 檔案 | 路徑 | 說明 |
|------|------|------|
| OAuth 憑證 | `~/.claude/mcp-keys/google-credentials.json` | OAuth 2.0 client_id / client_secret |
| Access Token | `~/.claude/mcp-keys/google-token.json` | access_token + refresh_token（自動刷新） |

---

## 取用方法

### A. 透過 MCP（推薦，A1 Claude Code session 內）

直接呼叫 `google-drive` MCP tool：
```
# mcp__google-drive__get_file(...)
# mcp__google-drive__list_files(...)
```

注意：`google-drive` MCP server 使用 `GOOGLE_CREDENTIALS_PATH`，
與 Sheets 的 `CREDENTIALS_PATH` 略有不同（但指向同一個 json 檔）。

### B. Python（token 取用方式同 google-sheets-api.md）

Scope 需加入 Drive：
```python
scopes=["https://www.googleapis.com/auth/drive.readonly"]
```

---

## 可用範圍

| 允許操作 | 對象 |
|---------|------|
| ✅ 讀取 | 報價單資料夾（Owner 分享的 Google Drive 目錄） |
| ✅ 讀取 | ASSET_LOG（素材紀錄） |
| ✅ 讀取 | 照片素材資料夾（A4 pipeline 來源） |
| ✅ 上傳 | 素材到指定資料夾（A4 / A8 pipeline） |

---

## 禁止操作

- ❌ 刪除任何檔案（moveToTrash / delete）
- ❌ 修改共用權限（shareFile 需 Owner 確認）
- ❌ 移動 Owner 手動整理的資料夾結構

---

## Token 過期恢復

同 google-sheets-api.md — 重新執行 MCP server 授權即可（兩者共用 token）。
