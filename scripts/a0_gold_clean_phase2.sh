#!/bin/bash
# a0_gold_clean_phase2.sh — gold 清洗第二階段:掃外接碟 3,625 份逐檔 LINE 對話 CSV,
# 抽店家(Account)人工回覆並配對前一句客人訊息,標記模板/自動回應,建 gold 候選庫。
# 客資紅線:對話內容只落 ~/.maplab/gold_replies/(本機),repo 與 Telegram 只出統計數字。
# 純確定性程式,零 LLM(5636 額度紀律)。
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
LOG="$HOME/.maplab/a0_gold_clean.log"
BOT_ENV="/Users/pagemacmini/maplab-ai-handbook/bot/.env"
PY=/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python
OUT_DIR="$HOME/.maplab/gold_replies"
mkdir -p "$OUT_DIR"

VERDICT="$("$PY" - <<'PY' 2>>"$LOG"
import csv, json, sys, hashlib
from collections import Counter
from pathlib import Path

CSV_DIR = Path("/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421")
OUT_DIR = Path.home()/".maplab"/"gold_replies"
csv.field_size_limit(10_000_000)

if not CSV_DIR.is_dir():
    print("外接碟未掛載或路徑不見,phase2 中止")
    sys.exit(0)

files = sorted(CSV_DIR.glob("*.csv"))
n_files = len(files)
n_empty = 0
rows_out = []          # (thread, date, time, user_msg, reply)
reply_freq = Counter() # 全庫回覆字面頻次 → 高頻=模板發送
auto_count = 0
account_total = 0

def read_thread(fp):
    # 前三行=帳號名稱/時區/下載時間,第4行=表頭
    with open(fp, newline="", encoding="utf-8-sig", errors="replace") as f:
        rdr = csv.reader(f)
        rows = list(rdr)
    msgs = []
    started = False
    for r in rows:
        if not started:
            if r and r[0] == "傳送者類型":
                started = True
            continue
        if len(r) >= 5:
            msgs.append({"type": r[0], "name": r[1], "date": r[2], "time": r[3], "text": r[4]})
    return msgs

threads = []
for fp in files:
    try:
        msgs = read_thread(fp)
    except Exception:
        n_empty += 1
        continue
    if not msgs:
        n_empty += 1
        continue
    threads.append((fp.name, msgs))

# pass 1: 頻次統計(判模板)
for _, msgs in threads:
    for m in msgs:
        if m["type"] == "Account":
            account_total += 1
            if m["name"] == "自動回應訊息":
                auto_count += 1
            else:
                reply_freq[m["text"].strip()] += 1

TEMPLATE_FREQ = 5  # 同字面出現>=5次=模板發送,不入人工訓練集
template_texts = {t for t, c in reply_freq.items() if c >= TEMPLATE_FREQ}
SIGNATURE = "MAPLAB Kitchen 團隊"  # OA 預設 #1-#5 落款,亦視為模板

n_template = 0
n_gold = 0
for tname, msgs in threads:
    last_user = None
    for m in msgs:
        if m["type"] != "Account":
            last_user = m["text"].strip()
            continue
        if m["name"] == "自動回應訊息":
            continue
        txt = m["text"].strip()
        if not txt:
            continue
        if txt in template_texts or SIGNATURE in txt:
            n_template += 1
            continue
        n_gold += 1
        rows_out.append({"thread": tname, "date": m["date"], "time": m["time"],
                         "user_msg": last_user or "", "reply": txt})

with open(OUT_DIR/"gold_candidates.jsonl", "w", encoding="utf-8") as f:
    for r in rows_out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

stats = {"threads_total": n_files, "threads_parsed": len(threads), "threads_empty_or_failed": n_empty,
         "account_msgs": account_total, "auto_replies": auto_count,
         "template_sends": n_template, "template_distinct": len(template_texts),
         "gold_candidates": n_gold, "template_freq_threshold": TEMPLATE_FREQ}
with open(OUT_DIR/"stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(f"phase2 完成:{n_files} 檔掃畢({n_empty} 空/壞),店家訊息 {account_total} 句="
      f"自動回應 {auto_count}+模板發送 {n_template}(去重 {len(template_texts)} 款)+人工候選 {n_gold};"
      f"候選庫落 ~/.maplab/gold_replies/gold_candidates.jsonl(內容不出本機)")
PY
)"
echo "[$(date '+%Y-%m-%dT%H:%M:%S')] ${VERDICT}" >> "$LOG"

TOKEN="$(grep '^TELEGRAM_BOT_TOKEN=' "$BOT_ENV" | cut -d= -f2-)"
CHAT="$(grep '^OWNER_CHAT_ID=' "$BOT_ENV" | cut -d= -f2-)"
if [ -n "${TOKEN:-}" ] && [ -n "${CHAT:-}" ]; then
  curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT}" \
    --data-urlencode "text=【bot 代答・gold 清洗第二階段(5644)】${VERDICT}" >/dev/null
fi
