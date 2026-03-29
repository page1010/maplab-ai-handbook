# MCP 使用指南 v1.1

> 建立：2026-03-28 | 更新：2026-03-29 | 作者：A1 | 解決問題：誰能用 MCP、bot.py 為何 MCP 無效、替代方案

> 📁 每個 MCP 服務的鑰匙取用方式詳見 `skills/credentials/` 對應技能書。

---

## 1. MCP 設定位置

| 層級 | 路徑 | 說明 |
|------|------|------|
| **全域（主要）** | `~/.claude/.mcp.json` | Mac mini 所有 Claude Code session 共用 |
| 專案層級 | `{repo}/.mcp.json` | ❌ 本 repo 未建立（不需要，全域已涵蓋） |

**`~/.claude/.mcp.json` 已設定的 Server：**

| Server 名稱 | 工具 | 狀態 |
|------------|------|------|
| `google-sheets` | 讀寫 Google Sheets | ✅ credentials 已設定 |
| `google-drive` | 檔案存取/上傳 | ✅ credentials 已設定 |
| `google-ads` | 廣告數據（唯讀） | ✅ refresh token 已設定 |
| `google-analytics` | 流量數據/報表 | ✅ credentials 已設定 |
| `google-search-console` | SEO 排名/關鍵字 | ✅ credentials 已設定（注意：需 Service Account） |
| `meta-ads` | Facebook/IG 廣告 | ✅ 已設定 |
| `line-bot` | LINE 發訊息 | ✅ 已設定 |
| `cloudinary` | 圖片 CDN | ✅ 已設定 |
| `ffmpeg` | 影音處理 | ✅ 已設定 |
| `threads` | Threads 社群 | ✅ 已設定 |

---

## 2. 誰能用 MCP（完整表格）

| 執行環境 | 能用 MCP？ | 原因 |
|---------|----------|------|
| **A1 — Claude Code（終端機 interactive）** | ✅ 完整可用 | 從 `~/.claude/.mcp.json` 載入，tool call 支援 |
| **A1 — Claude Code（worktree）** | ✅ 完整可用 | 同上，worktree 繼承全域設定 |
| **bot.py `claude -p` subprocess** | ❌ 不可用 | `-p` = print 模式，純文字輸出，不支援 tool call |
| **Chrome 側邊欄 Claude（Side Panel）** | ❌ 不可用 | 瀏覽器隔離環境，無法存取 Mac 本地 MCP server |
| **Chrome 側邊欄 Haiku/Sonnet（API）** | ❌ 不可用 | 雲端 API 無本地 MCP 連線 |
| **GitHub Actions（system-patrol.yml）** | ❌ 不可用 | Runner 沒有 Mac mini 的 MCP 憑證 |

**結論：MCP 只有 Mac mini 終端機的 A1 (Claude Code) 能用。**

---

## 3. OAuth Token 恢復步驟

MCP 斷線通常是 Google OAuth token 過期，分兩種情況：

### 3a. Claude Code 本身的 OAuth（`CLAUDE_CODE_OAUTH_TOKEN`）
```bash
# 重新登入 Claude Code
claude auth login
# 或直接設定 token（從 Chrome Extension 複製）
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-...
```

### 3b. Google API OAuth（Sheets / Drive / Analytics 等）
Google token 存在 `/Users/pagemacmini/.claude/mcp-keys/google-token.json`。
過期後需重新授權：
```bash
# 觸發 MCP server 重新授權（server 會自動在 stdout 印出 auth URL）
# 在 Claude Code session 內呼叫任何 Google 工具，若 token 過期會提示
```
或手動刷新：
```bash
# 以 google-sheets MCP server 為例
uvx mcp-google-sheets@latest
# 跑起來後會印出 OAuth URL → 瀏覽器授權 → token 自動存回
```

詳細的鑰匙取用方式見：
- `skills/credentials/google-sheets-api.md`
- `skills/credentials/google-drive-api.md`
- `skills/credentials/google-analytics-api.md`
- `skills/credentials/google-search-console-api.md`

### 3c. 驗證 MCP 是否正常（在 A1 session 中）
```
# 在 Claude Code 互動模式中直接呼叫 tool：
# 例：讀 Google Sheets MAPLAB_MasterData
# 如果回傳資料 = 正常；如果報 401/403 = token 過期需重新授權
```

---

## 4. bot.py subprocess 環境需要什麼

### 目前 `claude_ask()` 的環境（`bot/bot.py:227-238`）

```python
env = os.environ.copy()          # ✅ 複製完整環境，HOME 有帶到
env["CLAUDE_CODE_OAUTH_TOKEN"] = CLAUDE_OAUTH_TOKEN  # ✅ Claude 認證
env["PATH"] = "/opt/homebrew/bin:..."  # ✅ 找得到 claude 命令
# ❌ cwd 未設定 → 在 bot 啟動目錄跑，不是 maplab-ai-handbook/
```

### 環境變數清單

| 變數 | 來源 | 必要性 | 說明 |
|------|------|--------|------|
| `HOME` | `os.environ.copy()` ✅ | 必要 | Claude Code 從 `$HOME/.claude/` 讀設定 |
| `CLAUDE_CODE_OAUTH_TOKEN` | bot/.env ✅ | 必要 | Claude Max 訂閱認證 |
| `PATH` | 手動補 ✅ | 必要 | 找到 `/opt/homebrew/bin/claude` |
| `cwd` | ❌ 未設定 | 建議設定 | 設為 `REPO_PATH` 讓 Claude Code 能讀到 CLAUDE.md |

### cwd 未設定的影響
- Claude Code 在 bot.py 啟動目錄跑（通常是 `/Users/pagemacmini/maplab-ai-handbook/bot`）
- **不影響 MCP**（MCP 從 `~/.claude/.mcp.json` 全域載入，與 cwd 無關）
- **會影響**：Claude Code 讀取 project-level CLAUDE.md（需在 repo 根目錄）

### 為什麼 bot.py 的 claude -p 就算環境正確也不能用 MCP
`claude -p "prompt"` = **print 模式**（非 interactive agent 模式）：
- 輸入：一個 prompt 字串
- 輸出：純文字回應
- 限制：不執行 tool call，不呼叫 MCP server，只做 LLM 推論

MCP tool use 需要 **agentic loop**（Claude ↔ tool ↔ Claude），`-p` 模式不進入這個 loop。

---

## 5. Chrome 側邊欄的 Agent 為什麼不能用 MCP

Chrome Extension 的 Claude（無論 Side Panel 或 popup）是透過：
1. **Anthropic 雲端 API**（`api.anthropic.com`）呼叫 LLM
2. **Extension 本地 JS** 處理 UI

MCP server 是 **本地 process**（跑在 Mac mini 上，如 `uvx mcp-google-sheets`）。
雲端 API 無法連接 Mac mini 本地 port → **架構上不通**。

```
[Chrome Extension] → HTTPS → [Anthropic API] → LLM 回應
                                    ↑
                         無法連接 Mac mini 本地 MCP
```

---

## 6. Chrome 側邊欄 Agent 替代方案（要讀 Sheets 怎麼做）

### 方案 A：讓 A1 讀取後寫入 markdown（推薦）
1. 在 Telegram 傳 `/ask 請讀 MAPLAB_MasterData Items 表` → A0 轉給 A1
2. A1（Claude Code）用 MCP 讀 Sheets → 結果寫入 `data/snapshot-xxx.md`
3. Chrome Extension 讀 `raw.githubusercontent.com` 取得快照

### 方案 B：直接用 Google Sheets API（繞過 MCP）
Chrome Extension 可以用 **Google Sheets REST API + OAuth token**：
```javascript
// 需要使用者授權（Google Sign-In in Extension）
const resp = await fetch(
  `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${RANGE}`,
  { headers: { Authorization: `Bearer ${accessToken}` } }
);
```
限制：需要 Extension 實作 Google OAuth flow，較複雜。

### 方案 C：透過 A1 webhook（未來擴充）
在 Mac mini 跑一個本地 Flask server，Extension 呼叫 `localhost:PORT/sheets?range=...`，
Flask 用 MCP 或 gspread 回傳資料。

**目前最實用：方案 A（A1 定期更新快照 → Chrome 讀 markdown）**

---

## 7. 快速診斷清單

| 症狀 | 可能原因 | 解法 |
|------|---------|------|
| A1 session MCP 工具不出現 | MCP server 未啟動 | 重啟 Claude Code session |
| Google Sheets 呼叫 401 | OAuth token 過期 | 重新執行 MCP server 授權流程 |
| bot.py `/ask` 問 Sheets 資料，Claude 不知道 | `claude -p` 不支援 tool | 改用方案 A（A1 寫快照） |
| Chrome Extension Claude 說「我無法存取 Sheets」 | 架構限制，非 bug | 用方案 A 或 B |
| `~/.claude/.mcp.json` 找不到 | HOME 未正確設定 | 確認 subprocess 有 `HOME` 變數 |
