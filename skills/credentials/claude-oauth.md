# Claude Code OAuth 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

| 變數 | 位置 | 說明 |
|------|------|------|
| `ANTHROPIC_API_KEY` | `bot/.env`（本機）| Anthropic API Key（bot.py 呼叫 Claude CLI 用） |
| Claude Code session | `~/.claude/` 設定目錄 | A1 互動模式的認證，由 `claude auth login` 管理 |

> 注意：bot/.env.example 顯示使用 `ANTHROPIC_API_KEY`（非 `CLAUDE_CODE_OAUTH_TOKEN`）。

---

## 取用方法

### bot.py subprocess 環境（A0 觸發）

```python
import os

env = os.environ.copy()
env["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
env["PATH"] = "/opt/homebrew/bin:" + env.get("PATH", "")

# 呼叫 Claude CLI
subprocess.run(["claude", "-p", prompt], env=env, ...)
```

### A1 互動模式重新登入

```bash
# 若 Claude Code session 認證失效
claude auth login
```

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ bot.py 呼叫 Claude CLI | `claude -p "prompt"` subprocess |
| ✅ A1 Claude Code 互動 | 所有 A1 工作（MCP / git / 檔案編輯） |

---

## 禁止操作

- ❌ 把 API Key 明文寫進任何 GitHub 文件
- ❌ 用在非 MAPLAB 系統的其他用途
- ❌ 傳給 Chrome Extension 或其他 Agent 的對話

---

## 限制說明

`claude -p` 模式（print mode）：
- 只做 LLM 推論，不執行 tool call，不呼叫 MCP
- 需要 tool use 時，A0 必須改成開 Code task（A1 interactive）

詳見 `skills/mcp-usage-guide.md` §4。
