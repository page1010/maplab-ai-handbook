#!/usr/bin/env bash
# a0_pycheck.sh — bot.py 語法閘。重啟 bot 前必跑;FAIL 就不准 arm restart flag。
# (KeepAlive 會無限重生 crash 的 bot,壞語法上線=全面斷線,故此閘為鐵律。)
set -euo pipefail
/usr/bin/python3 -m py_compile /Users/pagemacmini/maplab-ai-handbook/bot/bot.py
echo "bot.py SYNTAX OK"
