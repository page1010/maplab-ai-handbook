#!/bin/bash
# free_quota_launchd_wrapper.sh — launchd 定時喚醒入口(#89)
# 由 com.maplab.freequota.plist 於台北 02/06/10/14/18/22 各叫醒一次。
# 依當下小時換算班次號後呼叫 free_quota_daily.sh。launchd 直接執行,
# 行程不掛在任何 Claude 續接窗底下,不需要 detach 模式。
# 手動測試:bash scripts/free_quota_launchd_wrapper.sh
set -u
HOUR="$(date +%H)"
case "$HOUR" in
  02) BAND=1 ;;
  06) BAND=2 ;;
  10) BAND=3 ;;
  14) BAND=4 ;;
  18) BAND=5 ;;
  22) BAND=6 ;;
  *)
    # 非整點喚醒(補跑/漏班重載)時,取最近一個已過班次
    if   [ "$HOUR" -ge 22 ]; then BAND=6
    elif [ "$HOUR" -ge 18 ]; then BAND=5
    elif [ "$HOUR" -ge 14 ]; then BAND=4
    elif [ "$HOUR" -ge 10 ]; then BAND=3
    elif [ "$HOUR" -ge 06 ]; then BAND=2
    else BAND=1
    fi
    ;;
esac
exec bash "$(dirname "$0")/free_quota_daily.sh" "$BAND" 6
