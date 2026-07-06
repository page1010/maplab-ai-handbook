# SEO/WP Runtime 取密技能書（Notion Vault）

版本：v1.0 | 建立：2026-07-02 | 維護者：A0

---

## 設計原則

**密碼永不進 Claude 對話、log 檔、repo 或任何文字輸出。**
Runtime 取密流程：
```
$NOTION_TOKEN (env var)
  → Notion API 查 vault 頁面
  → 取 WP email + App Password（記憶體短暫存活）
  → POST /wp-json/wp/v2/posts (status=draft)
  → 只輸出 WP draft ID + preview URL
  → 清除憑證（del 變數）
```

---

## Vault 位置

| 保管室 | Notion 頁面 ID |
|--------|----------------|
| API Keys 保管室 | `320ab0806d5c80e0be95f298399d2c44` |

預期格式（頁面 blocks 內）：
```
WordPress Email: xxx@xxx.com
Application Password: xxxx xxxx xxxx xxxx xxxx xxxx
```

---

## WP Endpoint（已確認）

```
https://www.maplabkitchen.com/wp-json/wp/v2/posts
```
- 對外讀取用 `GET`（公開）
- 建 draft 用 `POST`，需 Basic Auth（email + App Password）
- `status` 必須保持 `"draft"`，不得設為 `"publish"`

---

## 執行腳本

```bash
scripts/wp_publish_draft.py
```

### 用法 A：Notion Vault 路徑（Production）

```bash
NOTION_TOKEN='secret_xxx' python3 scripts/wp_publish_draft.py \
  workbook/outputs/seo-gap-drafts/<slug>.md \
  GAP-N
```

### 用法 B：直接 env var（Dev/測試）

```bash
WP_USER='email@xxx.com' WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx' \
  python3 scripts/wp_publish_draft.py \
  workbook/outputs/seo-gap-drafts/<slug>.md \
  GAP-N
```

### 安全規則
- 腳本 `stderr` 輸出會顯示 `wp_user[:3]***`（前三碼遮罩），不輸出完整值
- `stdout` 只輸出 JSON：`{wp_post_id, preview_url, status, gap_id, slug}`
- 不把任何憑證傳給 Claude / 貼回對話

---

## 接入 SEO Loop Step 5

```python
# seo_loop_orchestrator.py Step 5（待接入）
# 條件：escalation status = approved（Owner 視覺閘過）
import subprocess, os

result = subprocess.run(
    ["python3", "scripts/wp_publish_draft.py", draft_path, gap_id],
    capture_output=True, text=True,
    env={**os.environ},  # NOTION_TOKEN 已在 launchd EnvironmentVariables 設好
)
preview_url = json.loads(result.stdout).get("preview_url")
```

launchd plist 在 `EnvironmentVariables` 中設：
```xml
<key>NOTION_TOKEN</key>
<string>secret_xxx</string>
```
這樣 plist 裡的 token 只存在 launchd 設定，不進 repo。

---

## Notion 頁面解析容錯

腳本 `fetch_wp_credentials_from_vault()` 掃描全部 blocks，
支援格式：
- `WordPress Email: email@xxx`
- `WP_USER=email@xxx`
- `Application Password: xxxx xxxx`
- `WP_APP_PASSWORD=xxxx xxxx`

若格式不符 → 腳本 exit 1 + 說明未找到憑證的 block 數量。

---

## 禁止操作

- ❌ `status: "publish"`（只能 draft）
- ❌ 把 NOTION_TOKEN 或 App Password 寫進 scripts/、state/、任何 log
- ❌ 把密碼印到 stdout / 貼進 Claude 對話
- ❌ 刪除或覆蓋已存在的 WP 文章
