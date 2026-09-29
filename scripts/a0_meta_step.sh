#!/bin/bash
# a0_meta_step.sh — Meta 權杖五步流程的單步執行器(6233 授權自取權杖+6255 授權自動點按)。
# 邊界:帳密/2FA/驗證畫面出現即停手回報;權杖值絕不印出;URL 一律砍 query 再印。
# 本步:在 business.facebook.com 選擇器頁點「Map Lab Kitchen 旅圖」、等載入、回讀頁面文字。
set -u
W=1; T=2
JS='(()=>{const els=[...document.querySelectorAll("a,div[role=\"link\"],div[role=\"button\"],div[role=\"listitem\"]")];const hit=els.find(x=>(x.textContent||"").includes("Map Lab Kitchen"));if(!hit){return "not-found;candidates="+els.slice(0,40).map(x=>(x.textContent||"").trim().slice(0,25)).filter(s=>s).slice(0,15).join("|")}const a=hit.closest("a")||hit;a.click();return "clicked:"+(a.textContent||"").trim().slice(0,40)})()'
run_js() {
  osascript - "$1" "$2" "$3" <<'AS'
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
}
echo "=== click ==="
run_js "$W" "$T" "$JS" 2>&1 | cut -c1-500
sleep 8
echo "=== url(去query) ==="
osascript -e "using terms from application \"Google Chrome\"
tell application \"$HOME/Desktop/Google Chrome.app\" to get URL of tab $T of window $W
end using terms from" 2>&1 | cut -d'?' -f1
echo "=== page text ==="
run_js "$W" "$T" 'document.body.innerText.slice(0,1800)' 2>&1
