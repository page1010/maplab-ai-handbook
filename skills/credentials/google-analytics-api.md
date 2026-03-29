# Google Analytics API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

存放在 `~/.claude/.mcp.json` 的 `google-analytics` 區塊：

| 變數 | 路徑 | 說明 |
|------|------|------|
| `GOOGLE_APPLICATION_CREDENTIALS` | `~/.claude/mcp-keys/google-credentials.json` | OAuth 憑證（與 Sheets/Drive 共用） |
| `GOOGLE_PROJECT_ID` | `maplab-ai` | GCP 專案 ID |

---

## 取用方法

### 透過 MCP（推薦）

A1 Claude Code session 中直接呼叫 `google-analytics` MCP tools：
```
mcp__google-analytics__run_report(...)
mcp__google-analytics__get_property_details(...)
mcp__google-analytics__run_realtime_report(...)
```

### Property ID

MAPLAB GA4 Property ID：需從 GA4 控制台查詢，或詢問 Owner。

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ 讀取流量報表 | sessions / users / pageviews |
| ✅ 讀取即時數據 | realtime report |
| ✅ 讀取 Property 設定 | 確認追蹤 ID 等基本資訊 |
| ✅ 讀取 Google Ads 連結 | list_google_ads_links |

---

## 禁止操作

- ❌ 修改 GA4 Property 設定
- ❌ 刪除任何 GA4 數據流或事件
- ❌ 修改 Conversion 設定（需 Owner 確認）

---

## Token 過期恢復

與 Google Sheets/Drive 共用 OAuth token（`google-token.json`）。
過期恢復方式同 `skills/credentials/google-sheets-api.md`。
