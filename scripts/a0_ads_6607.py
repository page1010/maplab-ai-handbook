#!/usr/bin/env python3
# a0_ads_6607.py — Owner msg 6607 廣告帳號操作(act_318634712)。
# 鐵律:META_ADS_TOKEN 只在行程內流動,絕不印出;輸出只含 id/名稱/狀態/預算/HTTP code。
# 用法: inventory               唯讀盤點(campaigns+active adsets+recommendations+最低預算)
import sys, json, re, urllib.request, urllib.parse

ENVF = "/Users/pagemacmini/maplab-ai-handbook/bot/.env"
ACT = "act_318634712"
BASE = "https://graph.facebook.com/v21.0"

def token():
    with open(ENVF) as f:
        for line in f:
            m = re.match(r"^META_ADS_TOKEN=(.+)$", line.strip())
            if m:
                return m.group(1)
    raise SystemExit("no-token-in-env")

TOK = token()

def get(path, params=None):
    p = dict(params or {})
    p["access_token"] = TOK
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        body = body.replace(TOK, "<TOKEN>")
        return e.code, {"error_body": body}

NEW9 = ["52726872600330","52726872597530","52726872592730","52726872573130",
        "52726872557130","52726872533330","52726872516730","52726872490530","52726872474730"]
ACTIVE5 = ["52707985344330","52707916771930","52645018404530","52644997255130","52580537493330"]

def prep():
    for cid in NEW9:
        code, ads = get(f"{cid}/adsets", {"fields": "id,name,status,daily_budget,lifetime_budget", "limit": "10"})
        sets = [(a["id"], a.get("status"), a.get("daily_budget"), a.get("lifetime_budget"), a.get("name")) for a in ads.get("data", [])]
        code2, adl = get(f"{cid}/ads", {"fields": "id,name,status", "limit": "20"})
        alist = [(x["id"], x.get("status"), x.get("name")) for x in adl.get("data", [])]
        print(f"NEW {cid} adsets={sets} ads={alist}")
    for cid in ACTIVE5:
        code, ins = get(f"{cid}/insights", {"date_preset": "last_30d", "fields": "spend"})
        sp = ins.get("data", [{}])
        print(f"OLD {cid} 30d_spend={sp[0].get('spend') if sp else 0}")
    code, e = get("52580537493330/adsets", {"fields": "id,name,status,daily_budget,lifetime_budget,budget_remaining", "limit": "10"})
    print(f"Eadsets={[(a['id'], a.get('status'), a.get('daily_budget'), a.get('lifetime_budget'), a.get('budget_remaining')) for a in e.get('data', [])]}")

def post(path, params):
    p = dict(params)
    p["access_token"] = TOK
    data = urllib.parse.urlencode(p).encode()
    req = urllib.request.Request(f"{BASE}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400].replace(TOK, "<TOKEN>")
        return e.code, {"error_body": body}

NEW9_ADSETS = ["52726886828730","52726886540530","52726886800730","52726886778130",
               "52726886734930","52726886720930","52726886708930","52726886668930","52726886656930"]
NEW9_ADS = ["52727089601130","52727089386330","52727089364930","52727089430130","52727089408530",
            "52727089349130","52727153917530","52727089328130","52727089347130","52727153890730",
            "52727089319530","52727089287530"]

def apply():
    import time
    steps = []
    # 舊檔:A=創意疲乏關;B=空殼關+改名;E=lifetime用罄關+改名;C/D=降到最低日預算32+改名
    steps.append(("A關", "52707985344330", {"status": "PAUSED"}))
    steps.append(("B關", "52707916771930", {"status": "PAUSED"}))
    steps.append(("B名", "52707916771930", {"name": "TA-2婚禮冷層(舊0723空殼)"}))
    steps.append(("E關", "52580537493330", {"status": "PAUSED"}))
    steps.append(("E名", "52580537493330", {"name": "B4B5企業公關冷層(舊0119,lifetime用罄)"}))
    steps.append(("C預算", "52645018404530", {"daily_budget": "32"}))
    steps.append(("C名", "52645018404530", {"name": "TA-1週歲冷層-高收入媽媽(舊0511)"}))
    steps.append(("D預算", "52644997254930", {"daily_budget": "32"}))
    steps.append(("D名", "52644997255130", {"name": "TA-1週歲冷層-頂層認知(舊0504)"}))
    # 新9:由下而上全開
    for i, aid in enumerate(NEW9_ADS):
        steps.append((f"開ad{i+1}", aid, {"status": "ACTIVE"}))
    for i, sid in enumerate(NEW9_ADSETS):
        steps.append((f"開set{i+1}", sid, {"status": "ACTIVE"}))
    for i, cid in enumerate(NEW9):
        steps.append((f"開camp{i+1}", cid, {"status": "ACTIVE"}))
    ok = bad = 0
    for label, oid, params in steps:
        code, resp = post(oid, params)
        good = code == 200 and resp.get("success", True)
        ok += 1 if good else 0
        bad += 0 if good else 1
        print(f"{label} {oid} http={code} {'OK' if good else resp}")
        time.sleep(2)
    print(f"DONE ok={ok} bad={bad}")

def verify():
    code, data = get(f"{ACT}/campaigns", {"fields": "id,name,effective_status,daily_budget", "limit": "100"})
    for c in data.get("data", []):
        if c.get("effective_status") != "PAUSED":
            print(f"{c['id']} | {c.get('effective_status')} | db={c.get('daily_budget')} | {c.get('name')}")
    ids = ["52707985344330", "52707916771930", "52580537493330", "52645018404530", "52644997255130"]
    for i in ids:
        code, c = get(i, {"fields": "name,effective_status,daily_budget"})
        print(f"OLD {i} | {c.get('effective_status')} | db={c.get('daily_budget')} | {c.get('name')}")
    code, a = get("52644997254930", {"fields": "name,effective_status,daily_budget"})
    print(f"Dset {a.get('effective_status')} db={a.get('daily_budget')}")
    code, ads = get(f"{ACT}/ads", {"fields": "id,name,effective_status", "limit": "100",
                                   "filtering": json.dumps([{"field": "ad.effective_status", "operator": "IN", "value": ["ACTIVE", "PENDING_REVIEW", "IN_PROCESS"]}])})
    for x in ads.get("data", []):
        print(f"AD {x['id']} | {x.get('effective_status')} | {x.get('name')}")

UTM = "utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}"
ALL_ADS = NEW9_ADS + ["52727763559930"]

def utm():
    # 6628 授權:13 則廣告補 url_tags。素材不可改→複製素材(同 object_story_id)+換掛,會重審。
    import time
    ok = bad = 0
    for aid in ALL_ADS:
        code, ad = get(aid, {"fields": "name,creative{id,effective_object_story_id}"})
        cr = ad.get("creative", {})
        story = cr.get("effective_object_story_id")
        if code != 200 or not story:
            print(f"AD {aid} SKIP http={code} story={story} resp={str(ad)[:150]}")
            bad += 1
            time.sleep(2)
            continue
        time.sleep(2)
        code2, newc = post(f"{ACT}/adcreatives", {
            "object_story_id": story, "url_tags": UTM,
            "name": f"UTM-{ad.get('name','')[:40]}"})
        if code2 != 200 or "id" not in newc:
            print(f"AD {aid} CREATIVE-FAIL http={code2} resp={str(newc)[:200]}")
            bad += 1
            time.sleep(2)
            continue
        time.sleep(2)
        code3, upd = post(aid, {"creative": json.dumps({"creative_id": newc["id"]})})
        good = code3 == 200 and upd.get("success", True)
        ok += 1 if good else 0
        bad += 0 if good else 1
        print(f"AD {aid} new_creative={newc['id']} swap http={code3} {'OK' if good else str(upd)[:200]}")
        time.sleep(2)
    print(f"UTM DONE ok={ok} bad={bad}")

def utmverify():
    import time
    for aid in ALL_ADS:
        code, ad = get(aid, {"fields": "effective_status,creative{url_tags}"})
        tags = ad.get("creative", {}).get("url_tags", "")
        print(f"AD {aid} | {ad.get('effective_status')} | url_tags={'SET' if 'utm_campaign' in tags else tags or 'EMPTY'} http={code}")
        time.sleep(2)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "utm":
        return utm()
    if len(sys.argv) > 1 and sys.argv[1] == "utmverify":
        return utmverify()
    if len(sys.argv) > 1 and sys.argv[1] == "prep":
        return prep()
    if len(sys.argv) > 1 and sys.argv[1] == "apply":
        return apply()
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        return verify()
    if len(sys.argv) > 1 and sys.argv[1] == "fixe":
        import time
        time.sleep(31)
        code, resp = post("52580537493330", {"name": "B4B5企業公關冷層(舊0119,lifetime用罄)"})
        print(f"E名重試 http={code} {'OK' if code == 200 else resp}")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "merge":
        code, resp = post(f"{ACT}/ads", {
            "name": "MAPLAB 13 P0週歲派對(舊圖輪替)",
            "adset_id": "52726886656930",
            "creative": json.dumps({"creative_id": "1514190590506380"}),
            "status": "ACTIVE"})
        print(f"MERGE http={code} {resp if code != 200 else resp.get('id')}")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "pxstats":
        code, st = get("228166994905799/stats", {"aggregation": "event"})
        print(f"PXSTATS http={code} {st.get('data', st)}")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "probe3":
        import time
        code, px = get(f"{ACT}/adspixels", {"fields": "id,name,last_fired_time,is_unavailable"})
        print(f"PIXELS http={code} {px.get('data', px)}")
        time.sleep(2)
        for cid, tag in [("52707985344330", "A疲乏"), ("52580537493330", "E企業公關")]:
            code, ss = get(f"{cid}/adsets", {"fields": "id,name,targeting", "limit": "10"})
            for s in ss.get("data", []):
                t = s.get("targeting", {})
                ca = [x.get("name", x.get("id")) for x in t.get("custom_audiences", [])]
                print(f"{tag} adset {s['id']} custom_audiences={ca}")
            time.sleep(2)
            code, al = get(f"{cid}/ads", {"fields": "id,name,status,creative{id,name}", "limit": "20"})
            for x in al.get("data", []):
                cr = x.get("creative", {})
                print(f"{tag} ad {x['id']} | {x.get('status')} | {x.get('name')} | creative={cr.get('id')} {cr.get('name')}")
            time.sleep(2)
        return
    if len(sys.argv) > 1 and sys.argv[1] == "adcheck":
        import time
        for cid in NEW9:
            code, adl = get(f"{cid}/ads", {"fields": "id,effective_status,name", "limit": "20"})
            rows = adl.get("data", [])
            if code != 200 or not rows:
                print(f"CAMP {cid} http={code} n={len(rows)} resp={str(adl)[:200]}")
            for x in rows:
                print(f"AD {x['id']} | {x.get('effective_status')} | {x.get('name')}")
            time.sleep(2)
        return
    code, acct = get(ACT, {"fields": "name,currency,min_daily_budget"})
    print(f"[acct http={code}] name={acct.get('name')} currency={acct.get('currency')} min_daily_budget={acct.get('min_daily_budget')}")

    code, data = get(f"{ACT}/campaigns", {
        "fields": "id,name,status,effective_status,daily_budget,lifetime_budget,objective,created_time,recommendations",
        "limit": "100"})
    print(f"[campaigns http={code}] n={len(data.get('data', []))}")
    actives = []
    for c in data.get("data", []):
        recs = c.get("recommendations", {})
        rec_titles = [r.get("title", "") for r in recs.get("data", [])] if recs else []
        print(f"CAMP {c['id']} | {c.get('effective_status')} | db={c.get('daily_budget')} lb={c.get('lifetime_budget')} | {c.get('objective')} | {c.get('created_time','')[:10]} | {c.get('name')}" + (f" | REC={rec_titles}" if rec_titles else ""))
        if c.get("effective_status") == "ACTIVE":
            actives.append(c["id"])

    for cid in actives:
        code, ads = get(f"{cid}/adsets", {
            "fields": "id,name,status,effective_status,daily_budget,lifetime_budget,recommendations,targeting",
            "limit": "50"})
        print(f"  [adsets of {cid} http={code}]")
        for a in ads.get("data", []):
            t = a.get("targeting", {})
            tgt = {
                "age": f"{t.get('age_min')}~{t.get('age_max')}",
                "genders": t.get("genders"),
                "geo": json.dumps(t.get("geo_locations", {}), ensure_ascii=False)[:200],
                "flex": json.dumps(t.get("flexible_spec", []), ensure_ascii=False)[:300],
                "custom": [x.get("name", x.get("id")) for x in t.get("custom_audiences", [])],
            }
            recs = a.get("recommendations", {})
            rec_titles = [r.get("title", "") for r in recs.get("data", [])] if recs else []
            print(f"  ADSET {a['id']} | {a.get('effective_status')} | db={a.get('daily_budget')} | {a.get('name')}")
            print(f"    tgt={tgt}")
            if rec_titles:
                print(f"    REC={rec_titles}")
        code, adlist = get(f"{cid}/ads", {"fields": "id,name,effective_status", "limit": "50"})
        names = [f"{x.get('effective_status')}:{x.get('name')}" for x in adlist.get("data", [])]
        print(f"  [ads of {cid} http={code}] {names}")

if __name__ == "__main__":
    main()
