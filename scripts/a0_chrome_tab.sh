#!/bin/bash
# a0_chrome_tab.sh — read the URL+title of the front Chrome tab (Owner-authorized 5462).
# Read-only; never touches credentials; full-page text needs Chrome View>Developer>
# "Allow JavaScript from Apple Events" and is only attempted when arg1=text.
set -euo pipefail
if [ "${1:-}" = "text" ]; then
  osascript -e 'tell application "Google Chrome" to execute active tab of front window javascript "document.body.innerText.slice(0,20000)"'
else
  osascript -e 'tell application "Google Chrome" to get {URL, title} of active tab of front window'
fi
