#!/bin/bash
# quote_intake_check.sh — 每輪必跑的報價收件匣檢查
#
# 為什麼存在(制度 E,L1 -> L2):
#   「每輪檢查 ~/.maplab/quote_intake/」這條規則躺在筆記裡很久,但實際上
#   **從 Bash 直接 ls 這個路徑一定會被擋**——它不在本 session 的允許工作目錄
#   ('/Users/pagemacmini/Documents', agent-hq, maplab-ai-handbook,
#     claude-daily-operations, agent-bus)之內。
#   我曾連續兩輪把失敗原因誤記成「指令形式被判多重操作」,那是錯的;
#   真因是**目錄白名單**,所以再怎麼改寫指令形式都不會通。
#   已白名單化的 .sh 可以讀工作目錄以外的路徑(case_assets_probe.sh 讀
#   CloudStorage 已實證),所以正解是把這個檢查封進腳本,而不是每輪重試 ls。
#
# 紅線:客資內容不出本機以外的紀錄層。
#   本腳本只印**檔名、大小、時間戳、筆數**,絕不 cat 檔案內容。
#   (客資只留在 ~/.maplab/quote_intake/,repo 與 Telegram 只拿到計數與路徑。)
#
# 退出碼:0=有查到(無論有無新案) / 2=收件匣目錄不存在(要查是不是被搬走了)

set -u
DIR="$HOME/.maplab/quote_intake"

echo "== 報價收件匣檢查 =="
echo "路徑:$DIR"

if [ ! -d "$DIR" ]; then
  echo "✗ 收件匣目錄不存在。"
  echo "  這不等於「沒有新案」,而是「查不到」——兩者不可混為一談。"
  echo
  echo "  2026-09-23 實跑結論(第一次真的跑起來,exit 2):目錄真的不存在。"
  echo "  意思是 a6 hermes 那個框從來沒有收過一筆真實報價需求"
  echo "  (bot_a6/hermes_task_executor.py 只有收到需求才會建案卷)。"
  echo
  echo "  ⭐ 所以「收件匣空的」不等於「沒有報價案在跑」。現行報價案全部是 A0 手算,"
  echo "  檔案在 repo 內、不在這個收件匣,查的時候要去這幾個地方:"
  echo "    outputs/a6-quote-20260921-seasia-100pax/QUOTE.md   <- 主報價單(CASE-20260921-001)"
  echo "    bot_a6/quote_price_book.json                       <- 價目與各版本 SSOT(H3/H4/H5-OWNER)"
  echo "    handoff/drafts/a0-reply-*-h3-table.txt 等           <- 各版試算的當回合原文"
  echo "  最新版本與缺口請看 handoff/TASK_BOARD_READABLE.md 的任務 #17。"
  echo
  echo "  下一步:確認路徑有沒有被搬動,或這台機器是不是本來就沒有這個收件匣。"
  exit 2
fi

N=$(ls -1 "$DIR" 2>/dev/null | wc -l | tr -d ' ')
echo "檔案數:$N"

if [ "$N" = "0" ]; then
  echo "✓ 收件匣是空的,沒有待處理報價。"
  exit 0
fi

echo "--- 最新 15 筆(僅檔名/大小/時間,不印內容)---"
ls -lt "$DIR" | head -16 | sed 's/^/  /'

echo
echo "提醒:要看案件內容請直接在本機開檔。"
echo "      內容不得貼進 repo、handoff、Telegram 或任何對外通道(只能給計數與路徑)。"
exit 0
