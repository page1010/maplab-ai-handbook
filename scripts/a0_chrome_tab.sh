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
if [ "${1:-}" = "history-find" ] && [ -n "${2:-}" ]; then
  HDB="$HOME/.openclaw/browser/openclaw/user-data/Default/History"
  [ -f "$HDB" ] || { echo "查無瀏覽紀錄檔:$HDB"; exit 2; }
  TMP=$(mktemp)
  cp "$HDB" "$TMP"
  HITS=$( { LC_ALL=C grep -a -o -i "https\?://[^\"'[:cntrl:]]*${2}[^\"'[:cntrl:] ]*" "$TMP" || true; } | LC_ALL=C sort -u)
  n=$(printf '%s' "$HITS" | grep -c . || true)
  printf '%s\n' "$HITS" | head -20
  rm -f "$TMP"
  echo "命中 ${n} 筆(關鍵字=${2})"
  exit 0
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
