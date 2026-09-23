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
if [ "${1:-}" = "list" ]; then
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
