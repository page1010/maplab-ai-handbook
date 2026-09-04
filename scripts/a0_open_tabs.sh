#!/bin/bash
# a0_open_tabs.sh — 在 Owner 桌面 Chrome 開分頁（bot 窗白名單通道用）
# 用法：a0_open_tabs.sh [url ...]；不帶參數＝開五個拿鑰匙預設頁
# 安全邊界：只開網址，不輸入任何帳密/憑證；secrets 不經此腳本。
set -uo pipefail

if [ "$#" -gt 0 ]; then
  URLS=("$@")
else
  URLS=(
    "https://studio.youtube.com/"
    "https://console.cloud.google.com/apis/credentials?project=maplab-ai"
    "https://myaccount.google.com/apppasswords"
    "https://suno.com/account"
    "https://www.instagram.com/direct/inbox/"
  )
fi

open -a "Google Chrome" "${URLS[@]}"
echo "opened=${#URLS[@]} exit=$?"
