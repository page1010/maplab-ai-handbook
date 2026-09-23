# 待套補丁:claude-daily-operations 沒有餵長效 token,導致每天全線 BLOCKED

狀態:**已定位、已驗證、尚未套用**(落點在共用 repo `claude-daily-operations`,依規 A0 不自行 commit)
日期:2026-09-23
來源:Owner msg 5944 / 5948,`CULTURE_DECISION_LOGIC.md` 制度 A(修完必附驗證)

---

## 症狀

`cdo state/operations/2026-09-23/` 的 0800 / 0900 / 1200 三份回執全部:

```
## Outcome: BLOCKED
- reason: representative claude smoke returned no parseable token
- auth_status_loggedIn: no
```

一整天沒有任何 phase 產出。

## 根因(已用實測證據確認,不是推測)

**有兩把鑰匙,日常作業流程只翻空的那個抽屜。**

`scripts/claude_auth_diag.sh` 2026-09-23 實跑結果:

| 檢查項 | 結果 |
|---|---|
| `claude` 執行檔 | OK `~/.local/bin/claude` |
| 互動憑證 `claude auth status` | **`loggedIn = False`** |
| `maplab-ai-handbook/.env` 的 `CLAUDE_CODE_OAUTH_TOKEN` | 存在 |
| 用那把 token 跑最小 prompt | **rc=0,回 `PONG`** ← **token 是活的** |

也就是說:**憑證沒壞,Owner 不需要重新授權。** 是 cdo 的流程沒去拿那把能用的 token。

證據鏈:

1. `ops/claude-daily-operations/lib/common.sh:101 cdo_claude_smoke()` 直接呼叫 `"$bin" -p ...`,
   不帶任何 token,所以吃的是互動憑證(keychain)。
2. `ops/claude-daily-operations/lib/common.sh:111 cdo_claude_authed()` 解析 `claude auth status` 的 `loggedIn`,
   同樣只看互動憑證。
3. `grep -rl CLAUDE_CODE_OAUTH_TOKEN ops/claude-daily-operations/` → **零命中**。整個目錄從頭到尾沒讀過那把 token。
4. `launchd/com.maplab.claude-daily-operations.plist` 的 `EnvironmentVariables` **只有 `PATH` 和 `TZ`**,沒有 token。
5. 對照組:同一個 repo 的 `ops/scheduled_task_run.sh:15` **早就在做這件事**——
   `export CLAUDE_CODE_OAUTH_TOKEN="${CLAUDE_CODE_OAUTH_TOKEN:-$(grep '^CLAUDE_CODE_OAUTH_TOKEN=' "$HOME/maplab-ai-handbook/.env" 2>/dev/null | cut -d= -f2-)}"`
   所以這不是新做法,是**把既有做法補到漏掉的那條線上**。

## 補丁(一行,照抄既有寫法)

在 `ops/claude-daily-operations/dispatcher.sh` 的 auth gate(約 line 89 `AUTHED="no"; SMOKE_TOKEN=""`)**之前**插入:

```bash
# 2026-09-23:本流程原本只吃互動憑證(keychain),Owner 沒在電腦前登入時全線 BLOCKED。
# 實測 maplab-ai-handbook/.env 的長效 token 是活的(claude_auth_diag.sh rc=0 回 PONG)。
# 與 ops/scheduled_task_run.sh:15 同一寫法,不新增機制。已存在的環境變數優先,不覆蓋。
export CLAUDE_CODE_OAUTH_TOKEN="${CLAUDE_CODE_OAUTH_TOKEN:-$(grep '^CLAUDE_CODE_OAUTH_TOKEN=' "$HOME/maplab-ai-handbook/.env" 2>/dev/null | cut -d= -f2-)}"
```

**不要改 plist**(改 plist 要 reload 排程,且 token 不該寫進 plist 這種會進版控的檔案)。

## 驗證方式(套用後必跑,制度 A)

1. 手動跑一次 dispatcher 的任一 phase,確認回執不再是 `BLOCKED (smoke)`。
2. 確認 `auth_status_loggedIn` 那一行的語意要一併修——**它現在會誤導**:
   token 活著但 `loggedIn: no` 仍會照印,讓人以為是帳號問題。建議改成同時印
   `token_present` 與 `smoke_ok` 兩個欄位,不要只印互動憑證那一個。
3. 下一個自然排程(隔天 08:08)確認自動跑通。

## 安全邊界

- token **值**絕不印出、絕不寫進 plist、絕不寫進回執或 log。上面的寫法只做 `export`,不 echo。
- 不新增任何憑證檔,不動 Owner 的帳號,不自動重新登入。

## 為什麼 A0 沒有自己套

`claude-daily-operations` 是共用 repo,現在工作區有其他視窗未提交的改動(`git pull cdo` 已連續 26 輪失敗於
`cannot pull with rebase: You have unstaged changes`)。依既有規則 A0 不自行 commit cdo、不對共用 repo 下 `git stash`,
以免吞掉別人做到一半的東西。**補丁內容與驗證方式已在此備齊,套用與提交留給主視窗。**

## 附帶未解項

複利巡查 2026-09-23 12:47 手動驗跑仍失敗(log 全文一行 `Execution error`,跑了 4 分鐘才死)。
**既然 token 已證實是活的,這一件與 auth 無關**,方向改查:巡查提示詞本身
(`skills/compounding-patrol-prompt.md`,5,518 bytes,不算長)、`--dangerously-skip-permissions` 下的工具行為、逾時。
見任務 #29。
