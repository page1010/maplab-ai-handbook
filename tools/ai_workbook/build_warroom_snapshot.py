#!/usr/bin/env python3
"""
build_warroom_snapshot.py — 戰情判斷 probe
讀 Investment OS DB → 抽「現在的情況(總經 regime)+ 突發 + 判斷」→
  1) 寫 workbook/dashboards/warroom_snapshot.json
  2) 注入 maplab-ops-game-dashboard.html 的 /*__WARROOM_START__*/.../*__WARROOM_END__*/

閉環鐵則:
- DB 路徑由 INVESTMENT_OS_DB_PATH 決定;沒設就讀本地 sandbox。生產環境跑才會整片亮。
- 任何 table 缺/空 → 該層標 DEGRADED,絕不假裝;probe 本身不因缺料而 crash。
- snapshot 缺時 HTML 自帶 DEGRADED 預設,離線照樣開。
"""
import os, re, json, sqlite3, datetime, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))                      # maplab-ai-handbook
HTML = os.path.join(REPO, "workbook/dashboards/maplab-ops-game-dashboard.html")
SNAP = os.path.join(REPO, "workbook/dashboards/warroom_snapshot.json")
DEFAULT_DB = "/Users/pagemacmini/Documents/New project/data/investment_os.sqlite3"
DB = os.environ.get("INVESTMENT_OS_DB_PATH", DEFAULT_DB)
TODAY = datetime.date.today()

def days_since(dstr):
    if not dstr: return None
    s = dstr[:10]
    try:
        if len(s) == 7: s += "-01"
        return (TODAY - datetime.date.fromisoformat(s)).days
    except Exception:
        return None

def fresh_tone(days, ok=7, warn=21):
    if days is None: return "bad"
    if days <= ok: return "ok"
    if days <= warn: return "warn"
    return "bad"

# 目標總經指標:(顯示名, FRED code 子字串, 評分函式 value->(tone,hint))
def t_vix(v):  return ("ok","低波動") if v<17 else (("neutral","偏中") if v<25 else ("bad","恐慌"))
def t_curve(v):return ("ok","未倒掛") if v>0.1 else (("warn","近倒掛") if v>-0.1 else ("bad","倒掛"))
def t_oas(v):  return ("ok","信用緊") if v<3 else (("neutral","中性") if v<5 else ("bad","信用壓力"))
def t_cpie(v): return ("ok","錨定") if v<=2.5 else (("neutral","略高") if v<=3 else ("warn","脫錨"))
def t_neut(v): return ("neutral","")
TARGETS = [
    ("VIX 波動率",      "VIXCLS",       t_vix,   lambda v:f"{v:.1f}"),
    ("10Y-2Y 利差",     "T10Y2Y",       t_curve, lambda v:f"{v:+.2f}"),
    ("10Y 公債殖利率",  "DGS10",        t_neut,  lambda v:f"{v:.2f}%"),
    ("聯邦基金利率",    "DFF",          t_neut,  lambda v:f"{v:.2f}%"),
    ("高收益債利差",    "BAMLH0A0HYM2", t_oas,   lambda v:f"{v:.2f}%"),
    ("10Y 通膨預期",    "T10YIE",       t_cpie,  lambda v:f"{v:.2f}%"),
    ("失業率",          "UNRATE",       t_neut,  lambda v:f"{v:.1f}%"),
    ("S&P 500",         "SP500",        t_neut,  lambda v:f"{v:,.0f}"),
]

def main():
    src_kind = "生產 (INVESTMENT_OS_DB_PATH)" if os.environ.get("INVESTMENT_OS_DB_PATH") else "local sandbox"
    metrics, dates = [], []
    macro_n = 0
    try:
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        cur = con.cursor()
        try: macro_n = cur.execute("SELECT COUNT(*) FROM macro_series").fetchone()[0]
        except Exception: macro_n = 0
        for name, code, tone_fn, fmt in TARGETS:
            try:
                row = cur.execute(
                    "SELECT value,date FROM macro_series WHERE indicator_name LIKE ? "
                    "AND value IS NOT NULL ORDER BY date DESC LIMIT 1", (f"%{code}%",)).fetchone()
            except Exception:
                row = None
            if not row: continue
            v, d = row[0], row[1]
            tone, hint = tone_fn(v)
            metrics.append({"k":name,"v":fmt(v),"d":d,"tone":tone,"hint":hint})
            dates.append(d)
        # shocks
        def tbl_latest(tbl, datecol):
            try:
                n = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                ld = cur.execute(f"SELECT MAX({datecol}) FROM {tbl}").fetchone()[0]
                return n, ld
            except Exception:
                return 0, None
        news_n, news_ld = tbl_latest("market_news_alerts", "run_date")
        ev_n,   ev_ld   = tbl_latest("market_event_calendar", "run_date")
        ra_n,   ra_ld   = tbl_latest("risk_alerts", "created_at")
        # fresh shocks only (<=14d)
        shock_items = []
        if ra_n and days_since(ra_ld) is not None and days_since(ra_ld) <= 14:
            try:
                for r in cur.execute("SELECT message FROM risk_alerts ORDER BY created_at DESC LIMIT 3"):
                    if r[0]: shock_items.append(str(r[0])[:140])
            except Exception: pass
        # judgment table
        jrow = None
        try:
            jrow = cur.execute("SELECT date, decision FROM risk_master_decisions ORDER BY date DESC LIMIT 1").fetchone()
        except Exception:
            jrow = None
        con.close()
        db_err = None
    except Exception as e:
        db_err = str(e)
        news_n=ev_n=ra_n=0; news_ld=ev_ld=ra_ld=None; shock_items=[]; jrow=None

    # ---- 現在的情況 ----
    now_latest = max(dates) if dates else None
    now_days = days_since(now_latest)
    bad = [m for m in metrics if m["tone"]=="bad"]
    warn = [m for m in metrics if m["tone"]=="warn"]
    if not metrics:
        regime = {"label":"總經資料缺","tone":"bad","basis":"macro_series 讀不到 — 檢查 DB 路徑"}
    elif bad:
        regime = {"label":"壓力上升 / Risk-Off","tone":"bad",
                  "basis":"出現壓力訊號:"+ "、".join(m["k"] for m in bad)}
    elif warn:
        regime = {"label":"中性偏謹慎","tone":"neutral",
                  "basis":"有警示訊號:"+ "、".join(m["k"] for m in warn)}
    else:
        regime = {"label":"平穩 / Risk-On","tone":"ok",
                  "basis":"波動低、信用利差緊、殖利率曲線未倒掛"}

    # ---- 突發 ----
    if shock_items:
        shocks = {"tone":"warn","freshness":{"latest":ra_ld[:10] if ra_ld else "—","days":days_since(ra_ld),"tone":fresh_tone(days_since(ra_ld),3,7)},
                  "items":shock_items,"note":""}
    else:
        sl = ev_ld or ra_ld or "—"
        shocks = {"tone":"degraded",
                  "freshness":{"latest":(sl[:10] if sl and sl!='—' else "—"),"days":days_since(sl),"tone":"bad"},
                  "items":[],
                  "note":f"本地 news_alerts={news_n}、事件曆最新 {ev_ld or '—'}、risk_alerts 最新 {ra_ld[:10] if ra_ld else '—'}。突發層在生產 DB,設 INVESTMENT_OS_DB_PATH 跑才會亮。"}

    # ---- 判斷 ----
    j_basis = [f"{m['k']} {m['v']}（{m['hint']}）" for m in metrics if m["tone"]=="ok"][:4]
    j_missing = []
    if not shock_items: j_missing.append(f"突發新聞警報 {news_n} 筆")
    if jrow and days_since(jrow[0]) is not None and days_since(jrow[0]) <= 7:
        headline = f"風控決策層({jrow[0]}）：{str(jrow[1])[:120]}"
        conf, jtone = "中", "ok" if regime["tone"]=="ok" else "warn"
    else:
        if jrow: j_missing.append(f"風控決策層最新 {jrow[0]} 過舊")
        else: j_missing.append("風控決策層無資料")
        if regime["tone"]=="ok":
            headline = "總體平穩、無突發升級訊號(突發層缺料,僅依現在的情況)"
            jtone = "warn"
        elif regime["tone"]=="bad":
            headline = "現在的情況已見壓力訊號,需人工覆核(突發層缺料)"
            jtone = "bad"
        else:
            headline = "中性偏謹慎,等突發層補齊再定調"
            jtone = "warn"
        conf = "低 (缺突發層)"
    judgment = {"headline":headline,"tone":jtone,"confidence":conf,"basis":j_basis,"missing":j_missing,
                "next":("設 INVESTMENT_OS_DB_PATH 指向生產 DB 後重跑,補突發+決策層,信心才升" if j_missing else "")}

    warroom = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "db_source": f"{src_kind} · {os.path.basename(DB)} · macro {macro_n} 筆" + (f" · DB錯誤:{db_err}" if db_err else ""),
        "now": {"regime":regime,"freshness":{"latest":now_latest or "—","days":now_days,"tone":fresh_tone(now_days)},"metrics":metrics},
        "shocks": shocks,
        "judgment": judgment,
    }

    # write sidecar
    with open(SNAP,"w",encoding="utf-8") as f:
        json.dump(warroom, f, ensure_ascii=False, indent=2)

    # inject into HTML between markers
    with open(HTML,encoding="utf-8") as f: html = f.read()
    blob = json.dumps(warroom, ensure_ascii=False, indent=2)
    new = re.sub(r"/\*__WARROOM_START__\*/.*?/\*__WARROOM_END__\*/",
                 "/*__WARROOM_START__*/"+blob+"/*__WARROOM_END__*/", html, flags=re.DOTALL)
    if new == html and "/*__WARROOM_START__*/" not in html:
        print("WARN: markers not found in HTML — skipped injection");
    else:
        with open(HTML,"w",encoding="utf-8") as f: f.write(new)

    print(f"[warroom] db={DB}")
    print(f"[warroom] regime={regime['label']} | metrics={len(metrics)} | now_latest={now_latest} ({now_days}d)")
    print(f"[warroom] shocks={'(' + str(len(shocks['items'])) + ')' if shocks['items'] else 'DEGRADED'} | judgment_conf={judgment['confidence']}")
    print(f"[warroom] wrote {os.path.relpath(SNAP,REPO)} + injected HTML")

if __name__ == "__main__":
    main()
