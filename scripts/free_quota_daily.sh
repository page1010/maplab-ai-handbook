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
# 同日冪等閘。2026-09-24 修:原本只看「今天的日報在不在」,結果當天新增的 job
# 一律要等到隔天才會跑,新題目當輪無法驗證。改成比對佇列簽章——佇列內容有變就再跑一次,
# 沒變才跳過(既保留冪等,又讓「加了新題目就能立刻驗」成立)。FQ_FORCE=1 可強制重跑。
#
# 時段分班(Owner msg 6093,每天 500 個 job-run):一次跑完 500 件會連續佔住機器好幾個小時,
# 所以改成分班。用法 `bash free_quota_daily.sh <第幾班> <共幾班>`,例如 `… 3 6` = 今天第 3 班、
# 全天共 6 班,每班只跑各題扇出量的六分之一。不給參數 = 一次跑完整天的量(手動補跑用)。
BAND="${1:-0}"; BANDS="${2:-0}"
REPORT="$FQ/report_$TODAY.md"
QSIG_FILE="$FQ/.queue_sig_${TODAY}_b${BAND}"
QSIG="$(cat "$FQ"/queue/*.job.md 2>/dev/null | shasum | cut -c1-12)"
if [ -z "${FQ_FORCE:-}" ] && [ -f "$REPORT" ] && [ "$(wc -c < "$REPORT" | tr -d ' ')" -gt 200 ] \
   && [ "$(cat "$QSIG_FILE" 2>/dev/null)" = "$QSIG" ]; then
  echo "[skip] 本班今日已跑過且佇列未變: $REPORT(要強制重跑請設 FQ_FORCE=1)"; exit 0
fi
printf '%s' "$QSIG" > "$QSIG_FILE"

/usr/bin/python3 - "$HB" "$TODAY" "$WEEK" "$BAND" "$BANDS" <<'PYEOF'
import glob, html, json, os, re, shutil, sys, urllib.request

HB, TODAY, WEEK = sys.argv[1], sys.argv[2], sys.argv[3]
BAND, BANDS = int(sys.argv[4]), int(sys.argv[5])
FQ = HB + "/data/free-quota"
KEY = os.environ["OPENROUTER_API_KEY"]
MODELS = ["nvidia/nemotron-3-super-120b-a12b:free",
          "google/gemma-4-31b-it:free",
          "minimax/minimax-m3:free",
          "dots-studio/dots-3-note-preview:free"]
# Owner msg 6092/6093:目標是每天 1000 個來回。一個 job-run = 產稿 1 + 換模型審稿 1 = 2 次呼叫,
# 所以 1000 來回 ≈ 500 job-run。上限放到 1100 留重試餘裕;FQ_MAX_CALLS 可覆寫。
MAX_CALLS = int(os.environ.get("FQ_MAX_CALLS", "1100"))
# 連續 N 次(全模型都失敗)就收工,免得撞到免費額度牆之後還空轉幾百次。
FAIL_STREAK_MAX = int(os.environ.get("FQ_FAIL_STREAK", "8"))
calls = 0
fail_streak = 0

# ── 2026-09-24 追加(Owner msg 6091/6092):CONTEXT 注入 ──
# 為什麼:6091 實測三段對照證明,同一顆模型同一個問題,不餵資料就整段編造,
# 餵了就答對。原本這支排程跟 hermes_call.sh 犯同一個病——只送題目、不送資料,
# 模型有 26 萬~100 萬 token 上下文,實際餵進去 0 bytes。
# CONTEXT: 後面接 repo 相對路徑(逗號或空白分隔),讀進來當「內部文件」附在題目後,
# 並同樣附給審稿人,審稿人才有辦法核對「草稿有沒有新增文件沒寫的事實」。
CTX_BUDGET = int(os.environ.get("FQ_CTX_BUDGET", "60000"))   # 每題 context 位元組上限

def load_ctx(spec):
    """spec = 'AGENT_CORE.md, CURRENT_STATUS.md#tail400' -> (文字, 讀到的檔清單, 缺的檔清單)

    支援切片:`檔名#tailN` 取最後 N 行,`檔名#headN` 取前 N 行。
    2026-09-24 教訓:CURRENT_STATUS.md 單檔 245,954 bytes,不切片就會吃光整個
    context 預算,後面的檔一律讀不到(當日實測「讀到1檔,讀不到2檔」)。
    """
    got, missing, parts, used = [], [], [], 0
    for item in re.split(r"[,\s]+", spec.strip()):
        if not item:
            continue
        rel, _, slc = item.partition("#")
        p = os.path.join(HB, rel)
        if not os.path.isfile(p):
            missing.append(rel); continue
        try:
            t = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            missing.append(rel); continue
        m = re.match(r"(tail|head)(\d+)$", slc)
        mr = re.match(r"L(\d+)-(\d+)$", slc)
        if m:
            n = int(m.group(2)); lines = t.splitlines()
            lines = lines[-n:] if m.group(1) == "tail" else lines[:n]
            t = "\n".join(lines)
            rel = rel + "#" + slc
        elif mr:
            a, b = int(mr.group(1)), int(mr.group(2))
            t = "\n".join(t.splitlines()[a - 1:b])
            rel = rel + "#" + slc
            if not t.strip():
                missing.append(rel + "(行號範圍超出檔尾)"); continue
        room = CTX_BUDGET - used
        if room <= 0:
            missing.append(rel + "(超出 context 預算未讀)"); continue
        if len(t) > room:
            t = t[:room] + "\n…(本檔被 context 預算截斷,未讀完)"
        used += len(t)
        got.append(rel)
        parts.append("----- 檔案:%s -----\n%s" % (rel, t))
    return "\n\n".join(parts), got, missing

def load_items(spec_list, spec_chunk, n):
    """回傳今天要跑的 item 清單(每個 item 會取代 body 與 CONTEXT 裡的 {{ITEM}})。

    FANOUT       = 靜態清單檔(FQ 下相對路徑),一行一個 item,# 開頭為註解。
    FANOUT_CHUNK = `檔名:每段行數[, 檔名:行數 …]`,依檔案實際長度自動切成
                   `檔名#L1-60`、`檔名#L61-120` … 這樣清單會自己跟著檔案長大,
                   不必手抄一百行(Owner msg 6093:整理 100 件/天)。
    每天從不同起點取 n 個(起點 = 今天日期 % 池子大小),所以連著跑不會每天做同一段。
    """
    def read_list(rel):
        p = os.path.join(FQ, rel.strip())
        if not os.path.isfile(p):
            return []
        return [l.strip() for l in open(p, encoding="utf-8")
                if l.strip() and not l.strip().startswith("#")]

    pool = []
    if spec_list:
        # `a.txt x b.txt` = 交叉組合(場景 × 風格),兩份 30 行的清單就有 900 種題目,
        # 不必手抄一百行。組合用 ｜ 串起來當 item。
        legs = [read_list(x) for x in spec_list.split(" x ")]
        legs = [g for g in legs if g]
        if len(legs) == 1:
            pool += legs[0]
        elif len(legs) > 1:
            for a in legs[0]:
                for b in legs[1]:
                    pool.append(a + "｜" + b)
    for c in re.split(r"\s*,\s*", (spec_chunk or "").strip()):
        if not c:
            continue
        rel, _, step = c.partition(":")
        fp = os.path.join(HB, rel.strip())
        if not os.path.isfile(fp):
            continue
        total = sum(1 for _ in open(fp, encoding="utf-8", errors="ignore"))
        step = int(step or 60)
        for a in range(1, total + 1, step):
            pool.append("%s#L%d-%d" % (rel.strip(), a, min(a + step - 1, total)))
    if not pool:
        return []
    start = int(TODAY) % len(pool)
    # 交叉組合是按第一欄排好的,直接連號取會整批撞同一個場景;用一個與池子互質的步長跳著取。
    step = next((s for s in (97, 89, 83, 79, 73, 71, 67, 61, 59, 53, 47, 43, 41, 37, 31,
                             29, 23, 19, 17, 13, 11, 7, 1)
                 if len(pool) % s != 0 or s == 1), 1)
    seen, out = set(), []
    i = 0
    while len(out) < min(n, len(pool)) and i < len(pool) * 3:
        k = (start + i * step) % len(pool)
        if k not in seen:
            seen.add(k); out.append(pool[k])
        i += 1
    return out

def api(prompt, exclude=None):
    global calls, fail_streak
    if fail_streak >= FAIL_STREAK_MAX:
        return None, None
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
                fail_streak = 0
                return m, c.strip()
        except Exception:
            continue
    fail_streak += 1
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

def run_unit(name, body, meta, out_rel, url, daily, item, idx):
    """跑一個 job-run(產稿 1 呼叫 + 換模型審稿 1 呼叫)。回傳一列 rows。"""
    prompt = body
    text = None
    ctx_txt, ctx_got, ctx_missing = "", [], []
    if meta.get("CONTEXT"):
        spec = meta["CONTEXT"].replace("{{ITEM}}", item or "")
        ctx_txt, ctx_got, ctx_missing = load_ctx(spec)
        if ctx_missing and not ctx_got:
            return (name, "FAIL", "CONTEXT 全部讀不到:" + ",".join(ctx_missing))
        prompt = ("以下是 MAPLAB 的內部文件。只根據文件內容回答;文件沒寫的一律寫「文件未提及」,"
                  "不得自行補充、不得推測、不得編造數字或價格。\n\n"
                  "=== 內部文件開始 ===\n" + ctx_txt + "\n=== 內部文件結束 ===\n\n"
                  "任務:\n" + prompt)
    if url:
        text = fetch(url)
        if not text:
            return (name, "FAIL", "來源頁抓不到")
        prompt += "\n\n=== 來源頁面全文(已去標籤,含導覽雜訊請自行忽略) ===\n" + text
    model, out = api(prompt)
    if not out:
        return (name, "FAIL", "全模型失敗或達日上限")
    root, ext = os.path.splitext(out_rel)
    ext = ext or ".md"
    if item is not None:
        out_rel = "%s_%s/%03d%s" % (root, TODAY, idx + 1, ext)
    elif daily:
        out_rel = root + "_" + TODAY + ext
    out_path = os.path.join(HB, out_rel)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("> 草稿未審(free-quota 班表 %s,model=%s%s)。翻譯/生成稿:不得新增事實,上線前必經人審。\n\n%s\n"
                % (TODAY, model, (",item=" + item) if item else "", out))
    if meta.get("REVIEW") == "no":
        return (name, "OK", out_rel + " (" + model.split("/")[-1] + " | 未審)")
    # 換模型審稿(Owner 5349):A 產 B 審,審稿人拿任務原始要求+草稿(有來源頁就附上)逐條挑錯
    if ctx_txt:
        rv_prompt = ("你是嚴格審稿人,審另一個模型依內部文件寫出的草稿。逐條核對:1)草稿裡每一個事實/數字/價格/承諾"
                     "是否都能在內部文件裡找到出處,找不到的一律當作編造並指出 2)文件沒寫的地方草稿有沒有老實寫"
                     "「文件未提及」 3)是否偏離任務要求。")
    elif text:
        rv_prompt = ("你是嚴格審稿人,審另一個模型的草稿。逐條核對:1)草稿有無新增來源頁沒有的事實/數字/價格/承諾 "
                     "2)專名與數字是否一字不差 3)是否偏離任務要求。")
    else:
        rv_prompt = ("你是嚴格審稿人,審另一個模型的草稿(無來源頁,屬合成練習)。逐條核對:1)是否清楚標示為模擬/SYNTHETIC "
                     "2)有無疑似真實人名/店名/客資 3)是否符合任務要求。")
    rv_prompt += ("第一行只寫 VERDICT: PASS 或 VERDICT: ISSUES,之後逐條列問題(無問題寫「無」),最後一行給一句改進建議。"
                  "\n\n=== 任務原始要求 ===\n" + body[:2500]
                  + "\n\n=== 草稿 ===\n" + out[:6000]
                  + ("\n\n=== 內部文件(唯一可接受的事實來源) ===\n" + ctx_txt[:20000] if ctx_txt else "")
                  + ("\n\n=== 來源頁面全文(已去標籤) ===\n" + text[:6000] if text else ""))
    rv_model, rv = api(rv_prompt, exclude=model)
    verdict = "審稿失敗"
    if rv:
        verdict = "審PASS" if "PASS" in rv.splitlines()[0].upper() else "審ISSUES"
        rv_dir = FQ + "/reviews"
        os.makedirs(rv_dir, exist_ok=True)
        suffix = ("_%03d" % (idx + 1)) if item is not None else ""
        with open(rv_dir + "/" + name.replace(".job.md", "") + "_" + TODAY + suffix + ".review.md",
                  "w", encoding="utf-8") as f:
            f.write("# 換模型審稿 %s\n產稿=%s 審稿=%s 產出=%s\n\n%s\n" % (name, model, rv_model, out_rel, rv))
    ctx_note = ""
    if ctx_got or ctx_missing:
        ctx_note = " | ctx讀到%d檔" % len(ctx_got)
        if ctx_missing:
            ctx_note += ",讀不到:" + ",".join(ctx_missing)
    return (name, "OK", out_rel + " (" + model.split("/")[-1] + " | " + verdict + ctx_note + ")")

rows = []
for jf in sorted(glob.glob(FQ + "/queue/*.job.md")):
    name = os.path.basename(jf)
    head, _, body = open(jf, encoding="utf-8").read().partition("\n\n")
    meta = dict(re.findall(r"^([A-Z_]+):\s*(.+)$", head, re.M))
    out_rel, url, daily = meta.get("OUTPUT"), meta.get("INPUT_URL"), meta.get("DAILY") == "yes"
    if not out_rel or not body.strip():
        rows.append((name, "SKIP", "格式不完整")); continue
    body = body.strip()
    # 扇出(Owner msg 6093):一張 job 卡 = 一天 N 件,不是一天一件。沒有 FANOUT 就照舊跑一件。
    items = [None]
    if meta.get("FANOUT") or meta.get("FANOUT_CHUNK"):
        items = load_items(meta.get("FANOUT"), meta.get("FANOUT_CHUNK"),
                           int(meta.get("FANOUT_N", "10")))
        if not items:
            rows.append((name, "FAIL", "FANOUT 清單空的或讀不到")); continue
        if BANDS > 1 and 1 <= BAND <= BANDS:
            items = items[BAND - 1::BANDS]   # 本班只拿自己那一份
            if not items:
                rows.append((name, "SKIP", "本班沒分到題目")); continue
    if items == [None] and BANDS > 1 and BAND != 1:
        rows.append((name, "SKIP", "單件題目只在第 1 班跑")); continue
    ok_n, bad = 0, []
    last = None
    for idx, item in enumerate(items):
        if calls + 2 > MAX_CALLS or fail_streak >= FAIL_STREAK_MAX:
            bad.append("在第 %d/%d 件停手(calls=%d/%d,連續失敗=%d)"
                       % (idx + 1, len(items), calls, MAX_CALLS, fail_streak))
            break
        r = run_unit(name, body.replace("{{ITEM}}", item or ""), meta, out_rel, url, daily, item, idx)
        last = r
        if r[1] == "OK":
            ok_n += 1
        else:
            bad.append(("[%s] " % item if item else "") + r[2])
    if items == [None]:
        rows.append(last if last else (name, "FAIL", "沒有產出"))
    else:
        rows.append((name, "OK" if ok_n else "FAIL",
                     "扇出 %d 件成功 %d 件" % (len(items), ok_n)
                     + ("|" + ";".join(bad[:3]) if bad else "")))
    if not daily and ok_n:
        shutil.move(jf, FQ + "/done/" + TODAY + "-" + name)

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
