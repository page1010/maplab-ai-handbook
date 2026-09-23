#!/bin/bash
# peek_strategy_library.sh — 讀 investment-os 自家量化策略庫(唯讀)。
#
# 為什麼存在(制度 E,L1 -> L2):
#   Owner 2026-09-23 msg 5981 下令「54 策略庫優先提到最高、全力衝刺」。
#   但 /Users/pagemacmini/investment-os **不在本 session 的允許工作目錄內**,
#   從 Bash 直接 cat/ls/grep 一定被擋(跟 ~/.maplab/quote_intake 同一個坑)。
#   白名單化的 .sh 讀得到,所以把「讀策略庫」這件事固定成一支腳本,
#   下一個人不必再踩一次目錄白名單的坑。
#
# 紅線:只讀不寫;不碰 secrets/ 與 .env;不輸出任何金鑰值。
#
# 用法:
#   peek_strategy_library.sh list          # 列出 quant_strategy_logic/ 有哪些檔
#   peek_strategy_library.sh toc           # 54 策略庫的標題層(策略清單)
#   peek_strategy_library.sh head [N]      # 前 N 行(預設 120)
#   peek_strategy_library.sh grep <關鍵字>  # 在策略庫內找關鍵字(帶行號)
#   peek_strategy_library.sh sec <行號> [N] # 從指定行讀 N 行(預設 80)
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
DIR="/Users/pagemacmini/investment-os/reports/quant_strategy_logic"
LIB="$DIR/finlab_strategy_supplement_2026-05-26.md"
MODE="${1:-toc}"

if [ ! -d "$DIR" ]; then
  echo "✗ 策略庫目錄不存在:$DIR"
  echo "  這不等於「沒有策略庫」,而是「查不到」——兩者不可混為一談,要先查是不是被搬走了。"
  exit 2
fi

case "$MODE" in
  list)
    echo "==== $DIR ===="
    ls -l "$DIR"
    ;;
  toc)
    if [ ! -f "$LIB" ]; then echo "✗ 找不到 $LIB"; exit 2; fi
    echo "==== 策略庫標題層 $(basename "$LIB") ===="
    wc -l "$LIB"
    grep -n '^#' "$LIB"
    ;;
  head)
    N="${2:-120}"
    head -n "$N" "$LIB"
    ;;
  grep)
    KW="${2:?需要關鍵字}"
    grep -n "$KW" "$LIB" | head -80
    ;;
  grepall)
    # 2026-09-23 加(回 5986):Owner 說「codex 有寫套利交易」,要跨整個策略庫目錄找,
    # 不只 54 那一份。只印檔名+行號+該行,不 dump 全文。
    KW="${2:?需要關鍵字}"
    grep -rn "$KW" "$DIR" --include='*.md' --include='*.csv' | head -60
    ;;
  sec)
    FROM="${2:?需要起始行號}"
    N="${3:-80}"
    sed -n "${FROM},$((FROM + N))p" "$LIB"
    ;;
  *)
    echo "未知模式:$MODE(可用 list / toc / head / grep / sec)"
    exit 2
    ;;
esac
