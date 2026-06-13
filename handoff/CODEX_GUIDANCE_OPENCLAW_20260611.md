# 給 Codex：OpenClaw 修復指引（停止 nohup/launchctl submit 方向）

來源：B1 Claude Code，2026-06-11 21:45，Owner 要求轉達系統全貌。

## 你在鑽的兔子洞

你在解「如何讓背景程序脫離 Codex exec runner」（nohup → process group → launchctl submit）。
**這個問題不需要解。** pitfalls.md 錯誤 007 已記錄過同類彎路：能用系統原生機制就不要自製
process/IPC hack。

## 系統全貌（你沒看到的部分）

1. **OpenClaw gateway 沒有壞**。launchd `ai.openclaw.gateway` 有 `RunAtLoad=true`，
   重開機後已自動啟動（PID 921, port 18789）。不需要修、不需要重啟、不需要 detach 任何東西。
2. 真正斷掉的是 **CDP Chrome**：OpenClaw 的 `user-cdp` profile 是 `attachOnly: true`，
   它只「連接」一個帶 `--remote-debugging-port=9222` 旗標的 Chrome，不自己開。
3. 停電前那個 Chrome 是某個 session 手動開的——**沒有任何 launchd/login item 負責帶旗標
   重開它**。這才是根因：關鍵 runtime 依賴沒有開機自啟機制。

## 正確修法（兩步，不要再多）

**Step 1 — 立即恢復**（會關掉現有 Chrome 視窗、自動還原分頁）：
```bash
osascript -e 'quit app "Google Chrome"'; sleep 3
open -a "Google Chrome" --args --remote-debugging-port=9222 --restore-last-session
sleep 5; openclaw browser status   # 預期 running: true
```

**Step 2 — 根治**：建 `~/Library/LaunchAgents/com.hq.chrome-cdp.plist`（RunAtLoad 帶旗標
開 Chrome），並登記到 `/Users/pagemacmini/agent-hq/runtime/REGISTRY.md`。
規則（agent-hq 治理）：未登記的排程 = 野生 job，B4 patrol 可砍。

## 禁止事項

- 不要用 `launchctl submit`（一次性、不登記、重開機又沒了——跟這次斷掉的原因一模一樣）
- 不要再做 detached process spawner
- 注意：launchd 啟動的程序讀不到 `~/Library/CloudStorage`（TCC），今天已踩過（REGISTRY 有記錄）
