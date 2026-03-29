# Notion API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

存放在 **Notion API Keys 保管室**（自存自取）：
- Notion 頁面 ID：`320ab0806d5c80e0be95f298399d2c44`
- 欄位：NOTION_TOKEN（Integration Token）

> 注意：Notion API Keys 保管室是人類查閱用途，Agent 透過 A0 + Notion MCP 存取。

---

## 取用方法

### A. 透過 A0 Notion MCP（推薦）

A0 Cowork（Claude Desktop）有 Notion MCP 連線，A1 需要 Notion 資料時，
請指令給 A0 取得後回寫 GitHub：
```
A0: 讀 Notion API Keys 保管室（ID: 320ab0806d5c80e0be95f298399d2c44），
    把 NOTION_TOKEN 傳給我（只傳給 A1 session，不 commit）
```

### B. 直接 REST API（有 token 的情況）

```python
import requests

NOTION_TOKEN = "secret_xxx..."  # 從 Owner 或 A0 取得，用完不存

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 查詢 database
response = requests.post(
    f"https://api.notion.com/v1/databases/{database_id}/query",
    headers=headers
)
```

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ 讀取 ASSET_LOG | A4 素材追蹤 DB |
| ✅ 寫入 Owner 報告頁面 | A0 產出可視化報告 |
| ✅ 讀取 API Keys 保管室 | 取用其他 API token |

---

## 禁止操作

- ❌ 刪除任何 Notion 頁面
- ❌ 修改 workspace 設定
- ❌ 把 NOTION_TOKEN 存到 GitHub（auto-memory 或文件均不可）

---

## 重要提醒（Notion 定位）

根據 `AGENT_RULES.md SECTION 5`：
- Notion 定位為「Owner 可視化報告介面」，僅供人類查看
- **Agent 的狀態真相以 GitHub commit 為準，不以 Notion 為準**
- Agent 不開 Notion、不讀 Notion 作為決策依據
- 寫入 Notion 只用於產出 Owner 可視化報告

詳見 `AGENT_RULES.md SECTION 5`。
