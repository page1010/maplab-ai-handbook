# Cloudflare API 憑證技能書

> Notion 頁面連結：（待補）
> Token 位置：`bot/.env` → `CLOUDFLARE_API_TOKEN`（受 .gitignore 保護，不進 repo）

## 取得 Token

1. 前往 [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. 點「建立 Token」→「自訂 Token」
3. 依用途勾選權限（見下表）
4. 複製後立刻存到 `bot/.env`，不要貼在對話裡

## 權限對照表

| 用途 | 中文介面（Cloudflare） |
|------|----------------------|
| Cloudflare Pages 部署 | 帳戶 → Cloudflare Pages：編輯 |
| Workers 腳本 | 帳戶 → Workers 指令碼：編輯 |
| DNS 管理 | 區域 → DNS：編輯 |

## 在 Claude Code 讀取 Token

```python
import os
from dotenv import load_dotenv

load_dotenv("/Users/pagemacmini/maplab-ai-handbook/bot/.env")
CF_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
```

## 常用 API 範例

### 列出所有 Zone（網域）
```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" | jq '.result[].name'
```

### 部署 Workers 腳本
```bash
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT_NAME}" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/javascript" \
  --data-binary @worker.js
```

### Cloudflare Pages 觸發部署
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/deployments" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

## 安全提醒

- Token 只存 `.env`，不貼對話、不進 git
- 若懷疑外洩 → 立刻到 [API Tokens 頁面](https://dash.cloudflare.com/profile/api-tokens) rotate
- Token 建議設最小權限（只給需要的功能）
