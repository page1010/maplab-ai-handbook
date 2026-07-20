# Meta Ads API 鑰匙技能書

版本：v1.1 | 建立：2026-03-29 | 更新：2026-07-20 | 維護者：A1

> ⚠️ **唯讀狀態查詢（現在跑什麼活動/受眾/素材/大概花費）請先看
> `skills/ad-platform-browser-check.md`**——Owner 2026-07-20 指定，不要為了例行查詢去維護會定期過期的
> API 通行證。本檔的 API/MCP 路徑保留給精確報表、批量資料或程式化操作（需 Owner 核准的動作不變）。

---

## 鑰匙位置

存放在 `~/.claude/.mcp.json` 的 `meta-ads` 區塊：

| 變數 | 說明 |
|------|------|
| `META_APP_ID` | Meta App ID |
| `META_APP_SECRET` | Meta App Secret |
| `META_ACCESS_TOKEN` | App-level access token |

---

## 取用方法

### 透過 MCP（唯一推薦方式）

A1 Claude Code session 中直接呼叫 `meta-ads` MCP tools：
```
# 讀廣告數據
mcp__meta-ads__get_campaigns(...)
mcp__meta-ads__get_insights(...)
mcp__meta-ads__get_ads(...)
```

MCP server 自動從 `~/.claude/.mcp.json` 載入憑證，不需手動取 token。

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ 讀取廣告活動數據 | campaigns / adsets / ads |
| ✅ 讀取成效指標 | insights（CPM / CTR / ROAS 等） |
| ✅ 讀取受眾資訊 | demographic data |
| ✅ 搜尋廣告素材 | get_ad_creatives |

---

## 禁止操作

- ❌ 修改廣告設定（update_campaign / update_adset）— 需 Owner 確認
- ❌ 新建廣告活動（create_campaign）— 需 Owner 確認
- ❌ 觸發廣告花費（任何可能產生費用的操作需 Owner 授權）
- ❌ 把 token 從 .mcp.json 複製出來存到其他地方

---

## Access Token 說明

目前使用 App-level token（`META_APP_ID|META_APP_SECRET` 格式）。
此 token 只能存取公開數據和該 App 有授權的帳號。
若報 OAuthException → 需要重新取得 User Access Token（Owner 在 Meta Business Manager 操作）。
