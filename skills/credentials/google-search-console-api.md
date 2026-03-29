# Google Search Console API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

存放在 `~/.claude/.mcp.json` 的 `google-search-console` 區塊：

| 變數 | 路徑 | 說明 |
|------|------|------|
| `GOOGLE_APPLICATION_CREDENTIALS` | `~/.claude/mcp-keys/google-credentials.json` | OAuth 憑證（與 Sheets/Drive 共用） |

> ⚠️ 重要：GSC MCP server 可能需要 **Service Account** 憑證而非 OAuth client，
> 若呼叫失敗（403/permission denied），需確認 google-credentials.json 類型。

---

## 取用方法

### 透過 MCP（推薦）

```
mcp__google-search-console__search_analytics(...)
mcp__google-search-console__enhanced_search_analytics(...)
mcp__google-search-console__detect_quick_wins(...)
mcp__google-search-console__index_inspect(...)
```

### Site URL

MAPLAB GSC Site：`https://maplab.com.tw/`（需確認 sc-domain: 或 https: 前綴格式）

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ 讀取搜尋表現數據 | queries / pages / countries / devices |
| ✅ 讀取索引狀態 | index_inspect（URL 索引檢查） |
| ✅ 讀取 Sitemap 列表 | list_sitemaps |
| ✅ 提交 Sitemap | submit_sitemap（經 Owner 確認後可執行） |

---

## 禁止操作

- ❌ 提交 sitemap 以外的任何設定修改
- ❌ 刪除已驗證的網站屬性
- ❌ 修改 GSC 帳號存取權限

---

## Token 過期恢復

與 Google Sheets/Drive 共用 OAuth token（`google-token.json`）。
過期恢復方式同 `skills/credentials/google-sheets-api.md`。

若仍失敗，可能需要確認 MCP server 是否需要 Service Account（非 OAuth）。
詳見 `skills/mcp-usage-guide.md` 快速診斷清單。
