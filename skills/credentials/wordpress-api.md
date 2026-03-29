# WordPress REST API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

WordPress Application Password 存放在 **Notion API Keys 保管室**：
- Notion 頁面 ID：`320ab0806d5c80e0be95f298399d2c44`
- 欄位：WordPress Email + Application Password

> ⚠️ Agent 不直接開 Notion。請 Owner 提供，或讓 A0 透過 Notion MCP 取出後傳遞。

---

## 取用方法

### 產生 Base64 Authorization Header

```bash
# 替換為實際的 email 和 application_password
echo -n "your_email@example.com:xxxx xxxx xxxx xxxx xxxx xxxx" | base64
```

輸出結果填入 HTTP header：
```
Authorization: Basic <base64_output>
```

### curl 範例（建立草稿頁面）

```bash
WP_URL="https://maplab.com.tw/wp-json/wp/v2"
AUTH="Basic $(echo -n 'email:app_password' | base64)"

curl -X POST "$WP_URL/pages" \
  -H "Authorization: $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "頁面標題",
    "content": "<p>HTML 內容</p>",
    "status": "draft",
    "meta": {
      "_yoast_wpseo_title": "SEO 標題",
      "_yoast_wpseo_metadesc": "Meta 描述"
    }
  }'
```

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ 建立草稿頁面 | status: "draft"（不自動發布） |
| ✅ 讀取現有頁面 HTML | GET /wp/v2/pages/{id} |
| ✅ 更新 SEO meta | Yoast meta 欄位 |
| ✅ 上傳圖片到媒體庫 | POST /wp/v2/media |

---

## 禁止操作

- ❌ 自動發布頁面（status 不可設為 "publish"，必須保持 "draft"）
- ❌ 刪除頁面（DELETE 操作）
- ❌ 修改 WordPress 用戶權限

---

## 操作 SOP

完整的 WordPress 操作流程（選圖、上傳媒體庫、建頁面、SEO 設定）
詳見 `skills/gdrive-to-wordpress-upload-guide.md`。
