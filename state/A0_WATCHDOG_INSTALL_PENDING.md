# A0 Watchdog 安裝待執行

- 狀態：`file_ready_install_and_commit_blocked_by_sandbox`
- 時間：2026-08-23 15:39 +0800
- 原因：目前 Codex workspace-write 沙箱可寫 repo，但不可寫 `/Users/pagemacmini/Library/LaunchAgents/`。
- 已試：目標 plist 原先不存在；`launchctl list com.maplab.a0-continuity` 無輸出、exit 1；複製時回 `Operation not permitted`，所以未執行 bootstrap。
- 影響：程式、測試與 plist 已完成，但 LaunchAgent 尚未載入；目前不會每 600 秒自動 tick。

## 在 Mac 互動式 Terminal 執行的確切指令

```bash
cd /Users/pagemacmini/maplab-ai-handbook
plutil -lint config/launchd/com.maplab.a0-continuity.plist
mkdir -p /Users/pagemacmini/Library/LaunchAgents
cp config/launchd/com.maplab.a0-continuity.plist /Users/pagemacmini/Library/LaunchAgents/com.maplab.a0-continuity.plist
launchctl bootstrap "gui/$(id -u)" /Users/pagemacmini/Library/LaunchAgents/com.maplab.a0-continuity.plist
launchctl list com.maplab.a0-continuity
```

預期最後一行顯示 label `com.maplab.a0-continuity`；剛載入且 heartbeat 存活時，PID 欄可為 `-`，這不代表安裝失敗。不要為驗證而改舊或殺掉真實 `a0_heartbeat.json`。

## Resume Prompt

我是 Codex 共治對等方。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本檔與 `docs/governance/A0_CONTINUITY_WATCHDOG_SPEC_20260823.md`。

上次做到：watchdog 程式、recall prompt、plist、README、五路徑 fake 測試與隔離 DRY_RUN 已完成；安裝被 Codex 沙箱阻擋。

下一步：在 Mac 互動式 Terminal 原樣執行上方六行指令，保存 `launchctl list com.maplab.a0-continuity` 輸出。

交辦給誰：Owner 或可寫 `~/Library/LaunchAgents` 且可操作 user launchd domain 的本機 agent。

如何處理：install -> bootstrap -> list verify；不要重建程式、不要改 heartbeat、不要發 Telegram。

完成證據：目標 plist 的 `plutil -lint` 為 OK，`launchctl list` 出現 label，並在 heartbeat 正常時確認 status/log 可由排程更新。

收斂路徑：安裝驗證 -> 把本檔狀態改為 installed 或另留安裝 receipt -> 後續另經授權才做真實 stale-heartbeat/Telegram eye proof。

Blocker：目前只有 sandbox 對 `~/Library/LaunchAgents` 的寫入限制。

踩過的坑：repo 內 plist 通過 lint 不等於 LaunchAgent 已安裝；沒有 bootstrap/list receipt 不可宣稱上線。

## Scoped commit 也待執行

Codex 已嘗試 scoped `git add`，但目前沙箱也禁止建立 `.git/index.lock`；檢查確認 repo 沒有殘留的 `.git/index.lock`，不是另一個 git process 卡住。請在可寫此 repo `.git` 的本機 Terminal 執行：

```bash
cd /Users/pagemacmini/maplab-ai-handbook
git add -- README.md pitfalls.md scripts/a0_continuity_tick.sh scripts/a0_recall_prompt.md config/launchd/com.maplab.a0-continuity.plist tests/test_a0_continuity_tick.sh tests/fixtures/fake_claude_for_a0.sh state/A0_WATCHDOG_INSTALL_PENDING.md
git diff --cached --check
git diff --cached --name-only
git commit -m "codex: add A0 continuity watchdog"
```

`git diff --cached --name-only` 必須只列上面 8 個檔；不要使用 `git add .`，不要納入既有 automation/workbook dirty files，也不要 push。
