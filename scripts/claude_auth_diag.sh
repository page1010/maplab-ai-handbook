#!/usr/bin/env bash
# claude_auth_diag.sh — 分辨「排程失敗」到底是 auth 過期還是別的錯。
#
# 為什麼要這支:2026-09-23 手動驗跑複利巡查,log 只吐一行 "Execution error",
# 完全看不出是沒登入還是跑起來之後才出錯(而且它跑了 4 分鐘才死,不像單純 auth 被擋)。
# 這種 log 等於沒有 log。本腳本把三件事分開驗,各自印出可辨識的結論。
#
# 安全邊界(不可放寬):
#   - 絕不印出 token / cookie / 密碼的任何字元;.env 只讀變數「是否存在」與長度級距。
#   - 只讀取狀態與跑一句最小 prompt,不改任何設定、不重新登入、不碰瀏覽器。
#   - 不寫入任何憑證檔。
set -uo pipefail
REPO="$HOME/maplab-ai-handbook"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
CLAUDE_BIN="$(command -v claude || true)"

echo "=== 1. claude 執行檔 ==="
if [ -z "$CLAUDE_BIN" ]; then
  echo "FAIL: 找不到 claude(PATH=$PATH)。這就是 9/20 rc=127 的病,若再出現代表 PATH 修正沒生效。"
  exit 127
fi
echo "OK: $CLAUDE_BIN"

echo
echo "=== 2. 互動憑證(keychain/本機登入態)==="
# 只取 loggedIn 布林,不印帳號、不印 token。
"$CLAUDE_BIN" auth status 2>&1 | python3 -c '
import json,sys
raw=sys.stdin.read()
try:
    d=json.loads(raw)
    print("loggedIn =", bool(d.get("loggedIn")))
except Exception:
    # 不是 JSON 就只印前 200 字,且過濾掉看起來像金鑰的片段
    import re
    s=re.sub(r"[A-Za-z0-9_\-]{24,}","<redacted>",raw)[:200]
    print("非 JSON 輸出(已遮蔽長字串):", s)
'

echo
echo "=== 3. 排程用的長效 token 是否存在(只看有無,不看值)==="
if [ -f "$REPO/.env" ] && grep -q '^CLAUDE_CODE_OAUTH_TOKEN=' "$REPO/.env"; then
  LEN=$(grep '^CLAUDE_CODE_OAUTH_TOKEN=' "$REPO/.env" | cut -d= -f2- | wc -c | tr -d ' ')
  if [ "$LEN" -lt 20 ]; then
    echo "WARN: CLAUDE_CODE_OAUTH_TOKEN 存在但長度只有 $LEN,疑似空值或被截斷。"
  else
    echo "OK: CLAUDE_CODE_OAUTH_TOKEN 存在(長度級距 >=20,值不印出)。"
  fi
else
  echo "FAIL: .env 裡沒有 CLAUDE_CODE_OAUTH_TOKEN。排程會無憑證可用。"
fi

echo
echo "=== 4. 用排程那把 token 跑一句最小 prompt(這步才分得出 auth vs 其他)==="
export CLAUDE_CODE_OAUTH_TOKEN="$(grep '^CLAUDE_CODE_OAUTH_TOKEN=' "$REPO/.env" | cut -d= -f2-)"
OUT="$("$CLAUDE_BIN" -p 'Reply with exactly: PONG' --dangerously-skip-permissions 2>&1)"; rc=$?
# 同樣遮蔽長字串再印,避免任何憑證隨錯誤訊息外洩
SAFE="$(printf '%s' "$OUT" | python3 -c 'import sys,re; print(re.sub(r"[A-Za-z0-9_\-]{24,}","<redacted>",sys.stdin.read())[:600])')"
echo "rc=$rc"
echo "輸出(前 600 字,已遮蔽):"
echo "$SAFE"

echo
echo "=== 判讀 ==="
if [ $rc -eq 0 ] && printf '%s' "$OUT" | grep -qi 'PONG'; then
  echo "結論:排程用的 token 是活的。複利巡查 12:51 的 Execution error 不是 auth 問題,要往別的方向查(prompt 過長 / 工具權限 / 逾時)。"
elif printf '%s' "$OUT" | grep -qiE 'auth|login|unauthor|expired|401'; then
  echo "結論:auth 問題。排程用的長效 token 已失效,需要重新產一把(不要叫 Owner 動終端機,先做成一鍵流程)。"
else
  echo "結論:尚未分清。rc=$rc 但錯誤訊息沒有 auth 關鍵字,把上面輸出貼進 handoff 再判。"
fi
