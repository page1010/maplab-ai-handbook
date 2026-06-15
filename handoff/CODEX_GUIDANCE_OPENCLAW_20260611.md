# 給 Codex / 任何 agent：OpenClaw 重開機後修復（已驗證正解）

來源：B1 Claude Code，2026-06-11 起，2026-06-14 修正為實測正解。

## ⚠️ 本文件前一版有錯（叫人修主 Chrome :9222）——那是 runbook 明令別碰的壞路。以下是正解。

## 系統全貌（30 秒看懂）

OpenClaw 有 3 個 browser profile：
| profile | 是什麼 | 重開機後 |
|---------|--------|----------|
| `user-cdp`（舊預設、**壞路**）| attachOnly，接你主 Chrome :9222 | Chrome 148+ 安全限制，預設 profile 開不了 :9222 → 接不到 |
| `openclaw`（**現行正解**）| OpenClaw 自管的獨立 Chrome :18800，已用 Google SSO 登入 ChatGPT | gateway 會自啟，但**管理的 Chrome 不會自啟** ← 唯一斷點 |
| `user` | existing-session | 未用 |

**權威來源：** `/Users/pagemacmini/Documents/New project/docs/runbooks/IOS_MOMENTUM_OPENCLAW_GPT_FASTPATH.md`
終態決策：「**預設 profile 留在 `openclaw`，不要切回 `user-cdp`**」。

## 重開機後唯一要做的事（一行，不碰主 Chrome）

```bash
openclaw browser --browser-profile openclaw start
openclaw browser doctor          # 應全 OK，browser: running
openclaw browser --browser-profile openclaw tabs   # 列得出 = 好了
```

gateway（`ai.openclaw.gateway`，RunAtLoad=true）重開機會自己活，**不用重啟它**。
斷的永遠只是它管理的那個 Chrome :18800 沒被拉起來。

## 禁止 / 別再走的彎路

- ❌ 不要去開主 Chrome 的 `--remote-debugging-port=9222`（Chrome 148 安全限制，預設 profile 根本開不了；runbook 也說別切回 user-cdp）
- ❌ 不要 `nohup` / `launchctl submit` 自製 detached spawner（前一個 session 在這上面燒了幾小時，無效）
- ❌ 不要重啟 gateway 來「修」——gateway 沒壞

## 依賴警告

`openclaw` profile 的命脈是那個 managed Chrome 持續登入 ChatGPT。若哪天登出，
custom GPT 圓桌（`chatgpt.com/g/...ai-hermes-yuan-zhuo-hui-yi/project`）會抓不到 →
需 Owner 在 managed profile 用「用 Google 繼續」重新登入（走 Google SSO，不碰密碼/secrets）。

## 開機自啟（根治，待裝）

`~/Library/LaunchAgents/com.openclaw.browser-autostart.plist` 已備好（B1 寫，待 Owner load）：
重開機後自動跑上面那行 start，省掉手動。登記於 `agent-hq/runtime/REGISTRY.md`。
