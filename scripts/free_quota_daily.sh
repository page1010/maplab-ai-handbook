#!/bin/bash
# free_quota_daily.sh v1 — 每日免費算力班表(Owner 5341,2026-09-18「openrouter免費額度全力每天複利運作」)
# 機制:data/free-quota/queue/*.job.md 任務檔逐一送 OpenRouter :free 鏈,產出落檔、記帳、出日報。
# 任務檔格式:首行 OUTPUT: 相對路徑;可選 INPUT_URL:(只限公開頁);可選 DAILY: yes(常駐,輸出加日期);
#           空行後=prompt 全文。一次性任務跑完移 done/。
# 安全邊界:金鑰只 source 不回顯;產出一律草稿不發布;queue 不放客資/憑證;
#          日上限 MAX_CALLS=120,留足 A6 客服/LINE 訓練/晨會額度;同日重跑冪等。
set -u
ENV_FILE="$HOME/.maplab/free_compute.env"
[ -f "$ENV_FILE" ] || { echo "FATAL: env file missing"; exit 1; }
set -a; source "$ENV_FILE"; set +a
[ -n "${OPENROUTER_API_KEY:-}" ] || { echo "FATAL: OPENROUTER_API_KEY empty"; exit 1; }

HB="/Users/pagemacmini/maplab-ai-handbook"
FQ="$HB/data/free-quota"
mkdir -p "$FQ/queue" "$FQ/done"
TODAY=$(date +%Y%m%d)
REPORT="$FQ/report_$TODAY.md"
if [ -f "$REPORT" ] && [ "$(wc -c < "$REPORT" | tr -d ' ')" -gt 200 ]; then
  echo "[skip] 今日班表已跑過: $REPORT"; exit 0
fi

/usr/bin/python3 - "$HB" "$TODAY" <<'PYEOF'
import glob, html, json, os, re, shutil, sys, urllib.request

HB, TODAY = sys.argv[1], sys.argv[2]
FQ = HB + "/data/free-quota"
KEY = os.environ["OPENROUTER_API_KEY"]
MODELS = ["nvidia/nemotron-3-super-120b-a12b:free",
          "google/gemma-4-31b-it:free",
          "minimax/minimax-m3:free",
          "dots-studio/dots-3-note-preview:free"]
MAX_CALLS = 120
calls = 0

def api(prompt):
    global calls
    for m in MODELS:
        if calls >= MAX_CALLS:
            return None, None
        payload = json.dumps({"model": m, "max_tokens": 6000,
                              "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions", data=payload,
            headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
        calls += 1
        try:
            d = json.load(urllib.request.urlopen(req, timeout=240))
            c = (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""
            if c.strip():
                return m, c.strip()
        except Exception:
            continue
    return None, None

def fetch(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}), timeout=90)
        t = r.read().decode("utf-8", "ignore")
        t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
        t = re.sub(r"<[^>]+>", " ", t)
        return html.unescape(re.sub(r"\s+", " ", t))[:9000]
    except Exception:
        return None

rows = []
for jf in sorted(glob.glob(FQ + "/queue/*.job.md")):
    name = os.path.basename(jf)
    head, _, body = open(jf, encoding="utf-8").read().partition("\n\n")
    meta = dict(re.findall(r"^([A-Z_]+):\s*(.+)$", head, re.M))
    out_rel, url, daily = meta.get("OUTPUT"), meta.get("INPUT_URL"), meta.get("DAILY") == "yes"
    if not out_rel or not body.strip():
        rows.append((name, "SKIP", "格式不完整")); continue
    prompt = body.strip()
    if url:
        text = fetch(url)
        if not text:
            rows.append((name, "FAIL", "來源頁抓不到")); continue
        prompt += "\n\n=== 來源頁面全文(已去標籤,含導覽雜訊請自行忽略) ===\n" + text
    model, out = api(prompt)
    if not out:
        rows.append((name, "FAIL", "全模型失敗或達日上限")); continue
    if daily:
        root, ext = os.path.splitext(out_rel)
        out_rel = root + "_" + TODAY + (ext or ".md")
    out_path = os.path.join(HB, out_rel)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("> 草稿未審(free-quota 班表 %s,model=%s)。翻譯/生成稿:不得新增事實,上線前必經人審。\n\n%s\n"
                % (TODAY, model, out))
    if not daily:
        shutil.move(jf, FQ + "/done/" + TODAY + "-" + name)
    rows.append((name, "OK", out_rel + " (" + model.split("/")[-1] + ")"))

with open(FQ + "/usage_log.csv", "a", encoding="utf-8") as f:
    for name, st, note in rows:
        f.write("%s,%s,%s,%s\n" % (TODAY, name, st, note.replace(",", ";")))
with open(FQ + "/report_" + TODAY + ".md", "w", encoding="utf-8") as f:
    f.write("# free-quota 班表日報 %s\n\nAPI 呼叫數(含重試):%d / 上限 %d\n\n" % (TODAY, calls, MAX_CALLS))
    for name, st, note in rows:
        f.write("- [%s] %s — %s\n" % (st, name, note))
print("[done] jobs=%d calls=%d" % (len(rows), calls))
for name, st, note in rows:
    print(" ", st, name, "->", note)
PYEOF

cd "$HB" && git pull --rebase --autostash >/dev/null 2>&1
git -C "$HB" add data/free-quota/ handoff/en-drafts/ 2>/dev/null
git -C "$HB" commit -m "free-quota 班表 $TODAY" >/dev/null 2>&1 && git -C "$HB" push origin chore/agent-login-governance-20260816 >/dev/null 2>&1 && echo "[git] pushed" || echo "[git] 未推送(留本地,下輪補)"
echo ""
cat "$REPORT" 2>/dev/null
