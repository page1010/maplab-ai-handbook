#!/bin/bash
# a0_gold_clean_phase1.sh — phase 1 of the gold-library cleaning job (Owner 5636 GO).
# Read-only: LOCATE the per-thread LINE conversation CSVs referenced by
# data/line_booking_pairs.csv (filenames like 1000_20250725_20250725_<contact>.csv),
# inventory them, and report counts. NO customer content is pushed to Telegram —
# counts and directory paths only. CloudStorage is never scanned (Owner rule).
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOG="$HOME/.maplab/a0_gold_clean.log"
mkdir -p "$HOME/.maplab"
BOT_ENV="/Users/pagemacmini/maplab-ai-handbook/bot/.env"
PAIRS="/Users/pagemacmini/maplab-ai-handbook/data/line_booking_pairs.csv"

{
  echo "[$(date '+%Y-%m-%dT%H:%M:%S')] phase1 start: locate per-thread conversation CSVs"

  # sample three referenced filenames from the pairs index
  SAMPLES=$(cut -d, -f1 "$PAIRS" | tail -n +2 | head -3)
  echo "sample refs: $SAMPLES"

  FOUND_DIR=""
  for ROOT in "$HOME/.maplab" "$HOME/.hermes" "/Volumes/FABLE5_ARCHIVE" \
              "/Users/pagemacmini/claude-daily-operations" \
              "/Users/pagemacmini/maplab-ai-handbook" "$HOME/Documents" "$HOME/Downloads"; do
    [ -d "$ROOT" ] || continue
    HIT=$(find "$ROOT" -path '*CloudStorage*' -prune -o -type f -name '[0-9]*_20[0-9][0-9][0-9][0-9][0-9][0-9]_20[0-9][0-9][0-9][0-9][0-9][0-9]_*.csv' -print 2>/dev/null | head -1)
    if [ -n "$HIT" ]; then
      FOUND_DIR=$(dirname "$HIT")
      echo "HIT under $ROOT -> $FOUND_DIR"
      break
    fi
  done

  if [ -n "$FOUND_DIR" ]; then
    CNT=$(ls "$FOUND_DIR" | grep -c -E '^[0-9]+_20[0-9]{6}_20[0-9]{6}_.*\.csv$')
    echo "dir=$FOUND_DIR file_count=$CNT"
    ONE=$(ls "$FOUND_DIR" | grep -E '^[0-9]+_20[0-9]{6}_20[0-9]{6}_.*\.csv$' | head -1)
    echo "structure sample ($ONE) header + shape only:"
    head -1 "$FOUND_DIR/$ONE"
    wc -l "$FOUND_DIR/$ONE"
    VERDICT="找到了:$CNT 個對話檔在 $FOUND_DIR,可開清洗"
  else
    echo "NOT FOUND in searched roots"
    VERDICT="本機搜遍常用位置找不到逐檔對話 CSV(雲端硬碟未掃=規則),可能在 Drive 或外接碟未掛載,需下一步指示"
  fi
  echo "[$(date '+%Y-%m-%dT%H:%M:%S')] phase1 done"
} >> "$LOG" 2>&1

TOKEN="$(grep '^TELEGRAM_BOT_TOKEN=' "$BOT_ENV" | cut -d= -f2-)"
CHAT="$(grep '^OWNER_CHAT_ID=' "$BOT_ENV" | cut -d= -f2-)"
if [ -n "${TOKEN:-}" ] && [ -n "${CHAT:-}" ]; then
  curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT}" \
    --data-urlencode "text=【bot 代答・gold 清洗第一階段(5636)】${VERDICT}" >/dev/null
fi
