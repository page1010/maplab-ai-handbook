#!/bin/bash
# Read-only recon of spread_paper engine state (bot window borrow channel).
# Prints file listing and small state files. Never writes into investment-os.
set -u
D="/Users/pagemacmini/investment-os/state/spread_paper"
echo "== listing =="
ls -la "$D" 2>&1
for sub in "$D"/*/; do
  echo "== sub: $sub =="
  ls -la "$sub" 2>&1 | head -20
done
echo "== small json files (head) =="
for f in "$D"/*.json; do
  sz=$(stat -f%z "$f" 2>/dev/null || echo 0)
  echo "-- $f ($sz bytes)"
  if [ "$sz" -lt 6000 ]; then cat "$f"; else head -c 2000 "$f"; fi
  echo
done

# ⭐ 2026-09-24(Owner 6075:「小微價差幾點 模擬單有做看看嗎」)新增三段。
# 為什麼:價差幾點與模擬單有沒有真的送出,只有引擎自己寫出的 ledger 與 log 答得準,
# 規劃卡會落後(5419 教訓)。以下全部唯讀:不寫、不下單、不印帳號 ID、不印金鑰。
L="$D/ledger.json"
echo "== 引擎在跑嗎(鎖檔 + 最後寫入時間) =="
ls -l "$D/runner.lock" 2>&1
echo "-- ledger 最後寫入:$(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "$L" 2>&1)"
echo "-- 現在時間:$(date '+%Y-%m-%d %H:%M:%S')"

echo
echo "== 台指系列符號在 ledger 的命中次數(看小台/微台腿到底有沒有接上) =="
for sym in TXF MXF TMF MTX; do
  n=$( { LC_ALL=C grep -o -c "\"$sym" "$L" || true; } )
  echo "  $sym : $n"
done

echo
echo "== ledger 頂層結構(只印 key 與長度,不印整串值) =="
python3 - "$L" <<'PY' 2>&1
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception as e:
    print("ledger 讀取失敗:",e); raise SystemExit(0)
def shape(o,depth=0):
    pad="  "*depth
    if isinstance(o,dict):
        for k,v in list(o.items())[:25]:
            if isinstance(v,(dict,list)):
                print(f"{pad}{k}: {type(v).__name__}({len(v)})")
                if depth<1: shape(v,depth+1)
            else:
                print((f"{pad}{k}: {v!r}")[:200])
    elif isinstance(o,list):
        if o:
            print(f"{pad}[0] 樣本:"); shape(o[0],depth+1)
shape(d)
PY

echo
echo "== 小台/微台(MXF / TMF)在 ledger 裡的實際位置與內容 =="
python3 - "$L" <<'PY' 2>&1
import json,sys,re
try:
    d=json.load(open(sys.argv[1]))
except Exception as e:
    print("ledger 讀取失敗:",e); raise SystemExit(0)
WANT=("MXF","TMF")
hits=[]
def walk(o,path=""):
    if len(hits)>40: return
    if isinstance(o,dict):
        for k,v in o.items(): walk(v,f"{path}.{k}")
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,f"{path}[{i}]")
    elif isinstance(o,str):
        for w in WANT:
            if w in o: hits.append((path,o)); break
walk(d)
print(f"命中 {len(hits)} 處(上限 40):")
for p,v in hits[:40]:
    print(f"  {p} = {v[:120]}")
PY

echo
echo "== 小台/微台配對交易明細(MXF+TMF 同一筆,含報價證據與 pnl) =="
python3 - "$L" <<'PY' 2>&1
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception as e:
    print("ledger 讀取失敗:",e); raise SystemExit(0)
def fams(rec):
    out=set()
    for lg in (rec.get("legs") or []):
        c=lg.get("code") or ""
        out.add(c[:3])
    return out
for bucket in ("open","closed"):
    recs=d.get(bucket) or []
    if isinstance(recs,dict): recs=list(recs.values())
    print(f"--- {bucket}:共 {len(recs)} 筆")
    for i,r in enumerate(recs):
        if not isinstance(r,dict): continue
        f=fams(r)
        if not ({"MXF","TMF"} & f): continue
        print(f"  [{bucket}[{i}]] families={sorted(f)} tag={r.get('tag')}")
        print(f"    opened_at={r.get('opened_at')} closed_at={r.get('closed_at')} exit_reason={r.get('exit_reason')}")
        for lg in (r.get("legs") or []):
            keep={k:lg.get(k) for k in
                  ("code","family","side","qty","lots","limit_price","avg_price",
                   "fill_price","filled_qty","status","multiplier","order_id") if k in lg}
            print(f"    leg {keep}")
        dec=r.get("decision") or {}
        for k in ("edge_points","spread_points","edge","gross_edge","net_edge",
                  "all_in_cost","ratio","equiv_ratio","reason"):
            if k in dec: print(f"    decision.{k} = {dec[k]}")
        for q in (dec.get("quote_evidence") or []):
            if isinstance(q,dict):
                print(f"    quote {{k:v for code/bid/ask/ts}} = "
                      f"{ {kk:q.get(kk) for kk in ('code','family','bid','ask','last','ts','at') if kk in q} }")
        print(f"    pnl = {r.get('pnl')}")
PY

echo
echo "== 期交所公開即時報價:小台 vs 微台(算現在的價差幾點) =="
# 來源=期交所 MIS 公開行情(無需登入、無憑證)。只讀不下單。
for C in MXFJ6 TMFJ6; do
  echo "-- $C"
  curl -s --max-time 12 -X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://mis.taifex.com.tw' \
    -H 'Referer: https://mis.taifex.com.tw/futures/' \
    -d "{\"SymbolID\":[\"$C-F\"]}" \
    "https://mis.taifex.com.tw/futures/api/getQuoteDetail" \
    | python3 -c "
import sys,json
try: d=json.load(sys.stdin)
except Exception as e: print('  解析失敗:',e); raise SystemExit
rt=(d.get('RtData') or {}).get('QuoteList') or []
if not rt: print('  無資料,原文前 300 字:',json.dumps(d,ensure_ascii=False)[:300]); raise SystemExit
q=rt[0]
for k in ('SymbolID','CBidPrice1','CAskPrice1','CBid','CAsk','CLastPrice','CTime','CDate','CTotalVolume','CRefPrice'):
    if k in q: print(f'  {k} = {q[k]}')
bids=q.get('CBidPrice') or q.get('BidPrice') or []
asks=q.get('CAskPrice') or q.get('AskPrice') or []
if bids: print('  bid1 =',bids[0])
if asks: print('  ask1 =',asks[0])
if not (bids or asks or 'CBidPrice1' in q):
    print('  (無買賣盤欄位) 可用 key =', ','.join(sorted(q.keys()))[:400])
"
done

echo
echo "== stdout log 尾段(有沒有真的報價/送單) =="
tail -40 "$D/service.stdout.log" 2>&1
echo
echo "== stderr log 尾段 =="
tail -20 "$D/service.stderr.log" 2>&1
