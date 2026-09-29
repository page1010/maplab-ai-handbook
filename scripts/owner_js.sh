#!/bin/bash
# owner_js.sh — 在 Owner 那份 Chrome(~/Desktop)指定分頁執行一段 JavaScript 並回傳結果。
# 依據:6233(授權自取權杖)+6255(授權自勾/自動點按)。
# 邊界:只用於 Owner 明示授權的當次目的;帳密/2FA/驗證畫面出現即停手回報;
#       回傳含權杖值時呼叫端必須遮蔽、絕不印全值、絕不落 repo/log;URL 一律砍 query 再印。
set -u
W="$1"; T="$2"; JS="$3"
osascript - "$W" "$T" "$JS" <<'AS'
on run argv
  set w to (item 1 of argv) as integer
  set t to (item 2 of argv) as integer
  set js to item 3 of argv
  set appPath to (system attribute "HOME") & "/Desktop/Google Chrome.app"
  using terms from application "Google Chrome"
    tell application appPath
      return execute tab t of window w javascript js
    end tell
  end using terms from
end run
AS
