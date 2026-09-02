# Chrome Extension 冷啟動路徑 SOP — 2026-09-02

依據既有架構圖（`docs/remote-role-cold-start-launcher.md` §1 與
`docs/cross-project-agent-summon-workflow-map.md` §2）的資料鏈：

```text
module index → role module → CURRENT_STATUS → role recall → runtime handoff
```

每條路徑給：用途、驗證指令、預期結果、2026-09-02 盤查實測、故障處置。
任何一次「extension 打開後行為怪怪的」，照此表由上往下查，不要憑感覺重裝。

## 路徑總表

| # | 路徑 | 用途 | 2026-09-02 實測 |
|---|------|------|------|
| P1 | 本地打包檔（unpacked 目錄） | module index / role module 首選來源 | ✅ |
| P2 | GitHub raw（public maplab repo） | P1 之後的 fallback；非本機 runtime 的正本 | ✅ 200 |
| P3 | GitHub Contents API + token | private repo fallback（raw 不吃 token） | 設計正常，依 popup 設定的 token |
| P4 | CURRENT_STATUS.md 快照 | handoff prompt 附帶即時系統狀態 | ✅ 200 |
| P5 | recalls/<role>_recall.md | 角色靜態身份 | ✅（缺檔自動 fallback 到 packaged excerpt） |
| P6 | runtime handoff 外部連結 | commits frontier + investment-os SYSTEM_MAP | ⚠️ investment-os raw 404 |
| P7 | Bot 剪貼簿 `/clip` | Telegram `/clip` → popup 抓取 | ✅ 已修（9876→9875，v5.7.1） |
| P8 | 指令橋 `/poll` `/result` | Telegram → 瀏覽器指令 | ❌ 停擺（見 P8） |
| P9 | system-map 離線地圖 | 🗺 指向性地圖按鈕 | ✅ 本地檔存在 |

## P1 本地打包檔

Chrome 載入 `~/Desktop/chrome-extension`（symlink → 實體
`~/maplab-ai-handbook/chrome-extension/`；agent-hq 亦有 symlink，見
`agent-hq/CHROME_EXTENSION.md`）。popup 的 `fetchJsonFile` 先走
`chrome.runtime.getURL`，成功就不打網路。

驗證：

```bash
ls -l ~/Desktop/chrome-extension ~/agent-hq/chrome-extension
python3 -c "import json; json.load(open('/Users/pagemacmini/maplab-ai-handbook/chrome-extension/task-modules/index.json')); print('index ok')"
```

預期：兩個 symlink 都指向 maplab 實體；index 可解析。
故障處置：symlink 斷 → `ln -sfn ~/maplab-ai-handbook/chrome-extension ~/Desktop/chrome-extension`；改版後用 `scripts/update_extension.sh` 重載。

已知缺口：`task-modules/COMPOUNDING-PATROL.json` 存在於磁碟但**不在
index.json**，召喚選單看不到它（要用需先補 index 條目）。

## P2 GitHub raw（DEFAULT_BASE）

`https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main`。
maplab repo 是 public，raw 可匿名讀——這也是實體不搬進 private agent-hq 的原因。

驗證：

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main/chrome-extension/task-modules/index.json
```

預期 200。404 → 檢查 repo 是否被轉 private 或改名（那會斷掉所有非本機 runtime 的冷啟動）；非 200 → 網路/GitHub 狀態。

## P3 GitHub Contents API + token

raw 對 private repo 不支援 Authorization header（歷史坑，A1.json 有記載），
所以 `fetchFile` 對帶 token 的請求走 `api.github.com/repos/.../contents/`。
token 存在 `chrome.storage.local.githubToken`，只能在 popup 設定頁驗，CLI 驗不到。

故障徵兆：public 檔讀得到、private 檔全失敗 → token 過期，去 popup 重填。

## P4 CURRENT_STATUS.md

handoff prompt 尾端附即時快照；🔴 CRITICAL 標記驅動 overdue 偵測
（與 checkpoint.sh/patrol.sh 同一邏輯）。

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://raw.githubusercontent.com/page1010/maplab-ai-handbook/main/CURRENT_STATUS.md
```

注意：raw 有 CDN 快取（~5 分鐘）。剛 push 的狀態沒出現屬正常，不是故障。

## P5 role recall

`loadAgentRecall` 先抓 `recalls/<role>_recall.md`，失敗自動 fallback 到
role module 內的 `packaged_role_recall_excerpt`。目前 16 個 IOS-* 角色
沒有獨立 recall 檔（IOS-SELL 除外），**靠 fallback 是設計內行為**，
不是故障；但 packaged excerpt 是打包時快照，更新角色規則時記得同步
module JSON。

## P6 runtime handoff 外部連結

兩個外部依賴：

1. **commits frontier** — popup 載入時打 GitHub commits API 取 top5。
   無 token 也可（public repo），顯示「需先點重新抓取」屬正常 lazy 行為。
2. **investment-os raw**（`IS_RAW`，popup.js ~L636）— 非本機 runtime
   （gemini/hermes/openclaw 網頁端）召喚 IOS-* 角色時，Step 1 讀
   `https://raw.githubusercontent.com/page1010/investment-os/main/SYSTEM_MAP.md`。

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://raw.githubusercontent.com/page1010/investment-os/main/SYSTEM_MAP.md
```

2026-09-02 實測 **404**（repo private 或路徑不存在）。影響：網頁 runtime
召喚 IOS 角色時定向路線 Step 1 連結全部打不開；本機 runtime
（claude_code/codex）不受影響（走本地路徑）。處置選項（Owner gate）：
investment-os 提供 public 鏡像片段、或 handoff 對網頁 runtime 改附
sanitized 摘要。在此之前，網頁端 IOS 召喚以 prompt 內文為準，不追連結。

## P7 Bot 剪貼簿（已修）

鏈：Telegram `/clip 文字` → bot.py 寫 `/tmp/maplab_clip.json` → bot.py 內建
HTTP server **127.0.0.1:9875** `/clip` → popup「📋 從 Bot 抓取」。

v5.2 時代 bot 用 9876；2026-06-11 `9cb76ef` 把 bot clip server 改到 9875、
另拆 `http_bridge.py`(9876)，但 popup 沒跟著改 → 「從 Bot 抓取」自 6/11 起
一直打到沒人聽的 9876。v5.7.1（2026-09-02）已改回 9875。

驗證：

```bash
lsof -nP -iTCP:9875 -sTCP:LISTEN
curl -s http://127.0.0.1:9875/clip
```

預期：bot.py 的 Python 進程在聽；curl 回 JSON（沒 /clip 過就是空 text）。
沒人聽 9875 → bot 掛了，走 `scripts/a0_bot_restart.sh`（launchd 30 秒重生）。

## P8 指令橋 9876（停擺，待 Owner 決定）

`background.js` 每 5 秒 poll `127.0.0.1:9876/poll`、回報 `/result`，由
`bot/http_bridge.py` 提供（`bot/run_bridge_daemon.sh` 手動啟動，無 launchd）。
bridge.log 最後活動 2026-06-17，之後從未運行——此路徑等於自 6/17 起停用。
background poll 失敗是靜默的，不影響 popup 其他功能。

要復活（Owner 決定後）：

```bash
bash ~/maplab-ai-handbook/bot/run_bridge_daemon.sh
lsof -nP -iTCP:9876 -sTCP:LISTEN
```

長期復活需要 launchd plist（新常設服務 = Owner gate）。不復活則考慮
從 background.js 移除 poll，減少每 5 秒一次的無效請求。

## P9 離線指向性地圖

`system-map/index.html` 打包在 extension 內，由
`config/system-map/maplab-directional-map.json` 生成（v5.7.0 單一資料源）。

```bash
ls ~/maplab-ai-handbook/chrome-extension/system-map/index.html
```

## 例行盤查（每月或 extension 行為異常時）

依 P1→P9 順序跑各驗證指令；任何 ❌ 按該節處置。改了 extension 源碼必做：
改 source → `scripts/update_extension.sh` 重載 → chrome://extensions 無錯
→ popup 實畫面三層驗證，並寫 CHANGELOG（含 commit hash 與原因）。
