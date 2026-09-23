#!/bin/bash
# a0_chrome_tab.sh — read the URL+title of the front Chrome tab (Owner-authorized 5462).
# Read-only; never touches credentials; full-page text needs Chrome View>Developer>
# "Allow JavaScript from Apple Events" and is only attempted when arg1=text.
set -euo pipefail
# list           — 列出所有視窗所有分頁的「視窗序號 分頁序號 網址」,不切換焦點、不點任何東西。
#                  為什麼要有:Owner 問的那一頁常常不在最前面(6059 亞航那次前景是 ChatGPT),
#                  只讀 front tab 會答錯頁。
# text W T       — 讀指定視窗第 W 個、分頁第 T 個的純文字,同樣不切換焦點。
#                  一樣是唯讀:不填欄位、不按按鈕、不讀密碼欄的值。
# safari-list / safari-text W T — 同樣兩件事,但對 Safari。
#   為什麼要有(6060):Owner 說「我移給你了」,Chrome 七個分頁重查仍然沒有那一頁,
#   原因是他根本不在 Chrome。只查一個瀏覽器 = 會回報「找不到」然後停在那裡。
# cdp-list — 列出 openclaw 專屬 Chrome(獨立 user-data-dir,除錯埠 18800)的所有分頁。
#   為什麼要有(6060):這台 Mac 同時跑「兩個」Chrome——Owner 平常用的那個,
#   和 openclaw 專用的那個(--user-data-dir=~/.openclaw/browser/openclaw/user-data)。
#   AppleScript 只看得到其中一個,所以「Chrome 裡沒有那一頁」這句話本身可能是錯的。
# history-find <關鍵字> — 只在瀏覽紀錄裡找「含這個關鍵字」的網址,用來分辨
#   「那一頁從來沒在這台開過」和「開過但已經關掉」。唯讀:複製一份出來查,
#   不改原檔、不列出其他網址、只印命中的那幾條。
#   ⚠️ 2026-09-23 修正(6061):原本只查 openclaw 那個設定檔,**查錯瀏覽器**,
#   所以亞航回報 0 筆是假陰性。現在兩個設定檔都查,並且逐個標明查了哪一個。
#
# ⭐ owner-list / owner-text W T — Owner 自己用的那個 Chrome。
#   為什麼要單獨一組(6061,Owner:「有在chrome 在我用的那個」):
#   這台裝了**兩份 Chrome.app**——Owner 那份在 **~/Desktop/Google Chrome.app**(版本 152,
#   從 Dock 開、不帶任何參數、吃預設設定檔),openclaw 那份在 /Applications(版本 151,
#   帶 --user-data-dir 與 --remote-debugging-port=18800)。
#   `tell application "Google Chrome"` 解析到的是 openclaw 那份,**所以預設的 list 看不到 Owner 的分頁**;
#   要指名到 Owner 那份必須用**完整路徑**去 tell。
#   另外 `pgrep -f "Google Chrome --"` 會**整個漏掉** Owner 那份(它沒有參數,沒有 `--`),
#   查「這台有幾個 Chrome」必須用 `pgrep -fl "MacOS/Google Chrome"` 看主程序路徑。
OWNER_APP="${OWNER_CHROME_APP:-$HOME/Desktop/Google Chrome.app}"
if [ "${1:-}" = "history-find" ] && [ -n "${2:-}" ]; then
  total=0
  for HDB in \
    "$HOME/Library/Application Support/Google/Chrome/Default/History" \
    "$HOME/.openclaw/browser/openclaw/user-data/Default/History"
  do
    if [ ! -f "$HDB" ]; then
      echo "--- 查無此瀏覽紀錄檔(略過):$HDB"
      continue
    fi
    TMP=$(mktemp)
    cp "$HDB" "$TMP"
    # ⛔ 只留 scheme+host+path,問號與井號後面**一律砍掉**。
    # 為什麼(6061 實際踩到):瀏覽紀錄裡的網址會夾帶 accessToken / refreshToken /
    # OAuth authorization code / session id。原版直接印全網址,等於把 Owner 的
    # 登入憑證印進逐字稿與收據裡,違反「金鑰不印出、不落檔、不外傳」。
    # 砍掉 query 之後仍足以回答「這一頁有沒有開過」,那才是這個模式的用途。
    HITS=$( { LC_ALL=C grep -a -o -i "https\?://[^\"'[:cntrl:]?#]*${2}[^\"'[:cntrl:] ?#]*" "$TMP" || true; } \
      | LC_ALL=C sed 's/[^[:print:]].*$//' | LC_ALL=C sort -u)
    n=$(printf '%s' "$HITS" | grep -c . || true)
    rm -f "$TMP"
    echo "--- ${HDB}:命中 ${n} 筆"
    [ "$n" -gt 0 ] && printf '%s\n' "$HITS" | head -20
    total=$((total + n))
  done
  echo "合計命中 ${total} 筆(關鍵字=${2})"
  exit 0
elif [ "${1:-}" = "owner-list" ]; then
  osascript -e "tell application \"${OWNER_APP}\"
set out to \"\"
set w to 0
repeat with win in windows
set w to w + 1
set t to 0
repeat with tb in tabs of win
set t to t + 1
set out to out & w & \" \" & t & \" \" & (URL of tb) & linefeed
end repeat
end repeat
return out
end tell"
elif [ "${1:-}" = "history-when" ] && [ -n "${2:-}" ]; then
  # 印出含關鍵字的網址「最後一次造訪時間」,用來判斷一個結帳頁在那邊放多久了。
  # 只印 host+path 與時間,query 一律砍掉(同 history-find 的理由:網址裡有權杖)。
  HDB="$HOME/Library/Application Support/Google/Chrome/Default/History"
  [ -f "$HDB" ] || { echo "查無瀏覽紀錄檔"; exit 2; }
  command -v sqlite3 >/dev/null || { echo "此機無 sqlite3,改用 history-find"; exit 2; }
  TMP=$(mktemp); cp "$HDB" "$TMP"
  sqlite3 "$TMP" "SELECT datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime'),
    substr(url,1,instr(url||'?','?')-1) FROM urls WHERE url LIKE '%${2}%'
    ORDER BY last_visit_time DESC LIMIT 15;" 2>&1 | head -20
  rm -f "$TMP"
  echo "--- 現在時間:$(date '+%Y-%m-%d %H:%M:%S')"
  exit 0
elif [ "${1:-}" = "owner-title" ] && [ -n "${2:-}" ] && [ -n "${3:-}" ]; then
  # 標題不需要「允許 Apple 事件的 JavaScript」,頁面內文才需要。
  # 這個開關預設是關的,Owner 那份 Chrome 就是關著,所以 owner-text 會被擋;
  # 只要標題就能判斷頁面是不是停在錯誤畫面時,先用這個,不必請 Owner 去改設定。
  osascript -e "tell application \"${OWNER_APP}\" to get title of tab ${3} of window ${2}"
elif [ "${1:-}" = "owner-text" ] && [ -n "${2:-}" ] && [ -n "${3:-}" ]; then
  osascript -e "tell application \"${OWNER_APP}\" to execute tab ${3} of window ${2} javascript \"document.body.innerText.slice(0,20000)\""
elif [ "${1:-}" = "cdp-list" ]; then
  curl -s --max-time 10 "http://127.0.0.1:${CDP_PORT:-18800}/json/list" \
    | tr ',' '\n' | grep -E '"(url|title)"'
elif [ "${1:-}" = "safari-list" ]; then
  osascript -e 'tell application "Safari"
set out to ""
set w to 0
repeat with win in windows
set w to w + 1
set t to 0
repeat with tb in tabs of win
set t to t + 1
set out to out & w & " " & t & " " & (URL of tb) & linefeed
end repeat
end repeat
return out
end tell'
elif [ "${1:-}" = "safari-text" ] && [ -n "${2:-}" ] && [ -n "${3:-}" ]; then
  osascript -e "tell application \"Safari\" to do JavaScript \"document.body.innerText.slice(0,20000)\" in tab ${3} of window ${2}"
elif [ "${1:-}" = "list" ]; then
  osascript -e 'tell application "Google Chrome"
set out to ""
set w to 0
repeat with win in windows
set w to w + 1
set t to 0
repeat with tb in tabs of win
set t to t + 1
set out to out & w & " " & t & " " & (URL of tb) & linefeed
end repeat
end repeat
return out
end tell'
elif [ "${1:-}" = "text" ] && [ -n "${2:-}" ] && [ -n "${3:-}" ]; then
  osascript -e "tell application \"Google Chrome\" to execute tab ${3} of window ${2} javascript \"document.body.innerText.slice(0,20000)\""
elif [ "${1:-}" = "text" ]; then
  osascript -e 'tell application "Google Chrome" to execute active tab of front window javascript "document.body.innerText.slice(0,20000)"'
else
  osascript -e 'tell application "Google Chrome" to get {URL, title} of active tab of front window'
fi
