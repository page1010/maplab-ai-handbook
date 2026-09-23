#!/bin/bash
# ga4_clarity_install.sh — 用 Owner 已登入的 Chrome 完成 GA4 / Clarity 安裝前置查核。
#
# 背景(2026-09-22 22:5x,Owner msg「chrome 上有登入好的你直接做完」):
#   GA4 property 與 Clarity 專案都在 Owner 自己的帳號底下,機器過不了登入牆;
#   Owner 授權直接用他已登入的 Chrome 做完。a0_chrome_tab.sh 只有預設 AppleEvent
#   逾時(實測 -1712 逾時失敗,GA4 是重前端頁面,載入遠超過預設等待),所以另開這支:
#   開頁 -> 等到頁面真的畫完 -> 用加長 timeout 讀回 innerText。
#
# 用法:
#   ga4_clarity_install.sh read <url> [等待秒數]   # 開頁並讀回頁面文字(預設等 25 秒)
#   ga4_clarity_install.sh ga4                     # 直接開 GA4 資料串流列表並讀回
#   ga4_clarity_install.sh clarity                 # 直接開 Clarity 專案列表並讀回
#   ga4_clarity_install.sh front                   # 只讀目前最前面那個分頁(加長 timeout)
#
# 安全邊界(不得放寬):
#   - 只讀頁面文字,不輸入帳密、不碰 cookie 值、不把任何憑證印出或寫檔。
#   - 頁面文字可能含 Owner 帳號 email,故只印出前 4000 字且不寫進 repo。
#   - 建立 property / 專案這種「在 Owner 帳號裡新增東西」的動作,本腳本不自動按;
#     要按的時候由 A0 逐步操作並在回報中寫清楚按了什麼(留得住稽核)。
set -uo pipefail

MODE="${1:-front}"
WAIT="${3:-25}"

case "$MODE" in
  ga4)     URL="https://analytics.google.com/analytics/web/#/p0/admin/streams/table/" ;;
  clarity) URL="https://clarity.microsoft.com/projects" ;;
  read)    URL="${2:?需要網址}" ;;
  front)   URL="" ;;
  *) echo "unknown mode: $MODE"; exit 2 ;;
esac

if [ -n "$URL" ]; then
  open -a "Google Chrome" "$URL"
  echo "[open] $URL (等 ${WAIT}s 讓前端畫完)"
  sleep "$WAIT"
fi

# 加長 AppleEvent timeout:GA4/Clarity 都是重前端,預設等待一定不夠(已實測 -1712)。
osascript <<'APPLESCRIPT' 2>&1 | head -c 4000
with timeout of 180 seconds
  tell application "Google Chrome"
    set t to title of active tab of front window
    set u to URL of active tab of front window
    set txt to execute active tab of front window javascript "document.body.innerText.slice(0,4000)"
  end tell
end timeout
return "TITLE: " & t & linefeed & "URL: " & u & linefeed & "----" & linefeed & txt
APPLESCRIPT
echo
echo "[note] 若出現 -1728 或空白,多半是 Chrome 的 View > Developer > Allow JavaScript from Apple Events 沒開;"
echo "[note] 若出現 -1712,是頁面還沒畫完,加大等待秒數再跑一次。"
