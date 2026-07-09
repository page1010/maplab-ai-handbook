# Claude Code OAuth 鑰匙技能書

版本：v1.1 | 建立：2026-03-29 | 最後更新：2026-07-09 | 維護者：A1

---

## 鑰匙位置

| 變數 | 位置 | 說明 |
|------|------|------|
| `CLAUDE_CODE_OAUTH_TOKEN` | `bot/.env`（**bot.py 實際讀取的檔案**，見下方「.env 路徑陷阱」） | Max 訂閱 token，bot.py 呼叫 Claude CLI 用 |
| `CLAUDE_CODE_OAUTH_TOKEN` | `bot_a6/.env` | A6 bot 自己的一份，跟 `bot/.env` 是**兩個獨立檔案**，不會互相同步 |
| Claude Code session | `~/.claude/` 設定目錄 | A1 互動模式的認證，由 `claude auth login` 管理 |

> 2026-07-09 更正：舊版寫「用 `ANTHROPIC_API_KEY`」已過時，實測 `bot/.env`/`bot_a6/.env` 目前都用 `CLAUDE_CODE_OAUTH_TOKEN`（Max 訂閱模式，不計 API 費用）。以檔案實際內容為準，不要假設變數名稱。

---

## ⚠️ .env 路徑陷阱（2026-07-07 踩坑，必讀）

**每個 bot 讀的是自己目錄下的 `.env`，不是 repo 根目錄的 `.env`**：

| Bot | 讀哪個 `.env` | 程式碼位置 |
|-----|--------------|-----------|
| `bot/bot.py`（A1） | `bot/.env` | `load_dotenv(BOT_DIR / ".env")`，`BOT_DIR = Path(__file__).parent` |
| `bot_a6/bot_a6.py`（A6） | `bot_a6/.env` | 同樣模式，`BOT_DIR = Path(__file__).parent` |

**根因教訓**：2026-07-07 Owner 把新 token 存進 **repo 根目錄** `.env`，`scripts/diagnose_a1_claude_bridge.sh` 當時寫死檢查根目錄 `.env`，跑出 4/4 PASS；`claude -p` 手動測試也成功——但這兩個測試測的是「token 本身有效」，不是「bot 讀到的是同一份 token」。`bot/.env` 裡的 token 那行其實還被註解掉（2026-04-09 上次過期後從未恢復），bot 實際仍 401。

**預防**：
1. 換 token / 修 bot 認證問題時，**先搜 `load_dotenv` 的呼叫點**，確認 runtime 實際讀哪個路徑，不要假設「專案根目錄的 `.env` 就是唯一入口」。
2. 有兩個以上看起來同名的設定檔（根目錄 vs 子目錄）時，改完一份要交叉比對另一份是否同步，不要各自維護。
3. **驗收「修好了沒」的最終判準是透過 bot 真正對外的介面跑一次端到端**（例如 Telegram Web 送一則真實訊息、看真實回覆）——腳本/CLI 直測只能證明「元件本身沒壞」，證明不了「元件真的被接上了」。完整事故記錄見 `pitfalls.md` 2026-07-07 條目。

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
