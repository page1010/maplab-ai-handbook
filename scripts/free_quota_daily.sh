#!/bin/bash
# free_quota_daily.sh v2 — 每日免費算力班表(Owner 5341,2026-09-18「openrouter免費額度全力每天複利運作」)
# v2(Owner 5349):重複跑的重點是回饋——每份產出強制「換模型審稿」(A 產 B 審,對照來源挑錯),
#                審稿落 data/free-quota/reviews/;每週一次檢討 job 問三題(對準目標?好訓練?有效驗證?)。
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
WEEK=$(date +%G-W%V)
REPORT="$FQ/report_$TODAY.md"
if [ -f "$REPORT" ] && [ "$(wc -c < "$REPORT" | tr -d ' ')" -gt 200 ]; then
  echo "[skip] 今日班表已跑過: $REPORT"; exit 0
fi

/usr/bin/python3 - "$HB" "$TODAY" "$WEEK" <<'PYEOF'
import glob, html, json, os, re, shutil, sys, urllib.request

HB, TODAY, WEEK = sys.argv[1], sys.argv[2], sys.argv[3]
FQ = HB + "/data/free-quota"
KEY = os.environ["OPENROUTER_API_KEY"]
MODELS = ["nvidia/nemotron-3-super-120b-a12b:free",
          "google/gemma-4-31b-it:free",
          "minimax/minimax-m3:free",
          "dots-studio/dots-3-note-preview:free"]
MAX_CALLS = 120
calls = 0

def api(prompt, exclude=None):
    global calls
    for m in MODELS:
        if m == exclude:
            continue
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
    text = None
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
    # 換模型審稿(Owner 5349):A 產 B 審,審稿人拿任務原始要求+草稿(有來源頁就附上)逐條挑錯
    if text:
        rv_prompt = ("你是嚴格審稿人,審另一個模型的草稿。逐條核對:1)草稿有無新增來源頁沒有的事實/數字/價格/承諾 "
                     "2)專名與數字是否一字不差 3)是否偏離任務要求。")
    else:
        rv_prompt = ("你是嚴格審稿人,審另一個模型的草稿(無來源頁,屬合成練習)。逐條核對:1)是否清楚標示為模擬/SYNTHETIC "
                     "2)有無疑似真實人名/店名/客資 3)是否符合任務要求。")
    rv_prompt += ("第一行只寫 VERDICT: PASS 或 VERDICT: ISSUES,之後逐條列問題(無問題寫「無」),最後一行給一句改進建議。"
                  "\n\n=== 任務原始要求 ===\n" + body.strip()[:2500]
                  + "\n\n=== 草稿 ===\n" + out[:6000]
                  + ("\n\n=== 來源頁面全文(已去標籤) ===\n" + text[:6000] if text else ""))
    rv_model, rv = api(rv_prompt, exclude=model)
    verdict = "審稿失敗"
    if rv:
        verdict = "審PASS" if "PASS" in rv.splitlines()[0].upper() else "審ISSUES"
        rv_dir = FQ + "/reviews"
        os.makedirs(rv_dir, exist_ok=True)
        with open(rv_dir + "/" + name.replace(".job.md", "") + "_" + TODAY + ".review.md", "w", encoding="utf-8") as f:
            f.write("# 換模型審稿 %s\n產稿=%s 審稿=%s 產出=%s\n\n%s\n" % (name, model, rv_model, out_rel, rv))
    rows.append((name, "OK", out_rel + " (" + model.split("/")[-1] + " | " + verdict + ")"))

# 每週檢討 job(Owner 5349 三題):同一 ISO 週只跑一次,結論落檔供砍題/換題決策
week_flag = FQ + "/.week_" + WEEK
if not os.path.exists(week_flag) and calls < MAX_CALLS:
    qlist = "\n".join(os.path.basename(p) for p in sorted(glob.glob(FQ + "/queue/*.job.md"))) or "(空)"
    try:
        log_tail = "".join(open(FQ + "/usage_log.csv", encoding="utf-8").readlines()[-60:])
    except Exception:
        log_tail = "(無紀錄)"
    rv_files = sorted(glob.glob(FQ + "/reviews/*.review.md"))[-10:]
    rv_heads = ""
    for p in rv_files:
        lines = open(p, encoding="utf-8").read().splitlines()
        rv_heads += os.path.basename(p) + ": " + next((l for l in lines if "VERDICT" in l.upper()), "?") + "\n"
    mr_prompt = ("背景:這是台南外燴品牌 maplabkitchen 的每日免費算力班表,目標=複利累積接單素材(英文站草稿、"
                 "詢價應對訓練題),未來複製到泰國接案。以下是本週任務清單、執行紀錄與審稿判定。"
                 "請誠實回答三題,各給結論+一句理由:1)這批任務是否仍對準「接單/泰國複製」目標?哪些偏了? "
                 "2)題目設計是不是好的訓練方法?哪題該砍該換,換成什麼? 3)目前驗證(換模型審稿+對照來源)是有效驗證"
                 "還是模型自誇?怎麼補強?最後列「下週建議動作」最多三條。不得捏造數據。"
                 "\n\n=== 本週 queue ===\n" + qlist
                 + "\n\n=== usage_log 近況 ===\n" + log_tail[:4000]
                 + "\n\n=== 審稿判定 ===\n" + (rv_heads or "(無)"))
    m, mr = api(mr_prompt)
    if mr:
        with open(FQ + "/weekly_review_" + TODAY + ".md", "w", encoding="utf-8") as f:
            f.write("> 週檢討草稿(free-quota 班表 %s,model=%s)。結論供參,砍題/換題由 A0 決定並留紀錄。\n\n%s\n" % (TODAY, m, mr))
        open(week_flag, "w").write(TODAY + "\n")
        rows.append(("weekly_review", "OK", "weekly_review_" + TODAY + ".md (" + m.split("/")[-1] + ")"))
    else:
        rows.append(("weekly_review", "FAIL", "全模型失敗或達日上限"))

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
