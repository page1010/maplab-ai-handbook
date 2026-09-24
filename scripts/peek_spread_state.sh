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
echo "== 現貨期貨持有成本雷達:0050 現股 vs 小型元大台灣50期貨(SRF) =="
# ⭐ 2026-09-24(Owner 6076:「小型元大0050期貨剛好對應0050一張 多少點差試算是划算的」)
# 這一段就是任務 #64「現多期空持有套利:先做每日數學雷達,不下單」的第一版。
# 零 LLM 算術層:所有數字由本段程式從公開報價算出,沒有一個是模型口算的。
# 來源:0050 現貨=證交所 MIS 公開行情;SRF 期貨=期交所 MIS 公開行情;
#      契約乘數與原始保證金=investment-os anchor_products.json(源頭為期交所 stockMargining)。
SPOT_RAW=$(curl -s --max-time 12 \
  -H 'Referer: https://mis.twse.com.tw/stock/index.jsp' \
  "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_0050.tw&json=1&delay=0")
FUT_RAW=$(curl -s --max-time 12 -X POST \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://mis.taifex.com.tw' \
  -H 'Referer: https://mis.taifex.com.tw/futures/' \
  -d '{"SymbolID":["SRFJ6-F"]}' \
  "https://mis.taifex.com.tw/futures/api/getQuoteDetail")
SPOT_RAW="$SPOT_RAW" FUT_RAW="$FUT_RAW" python3 - "$D/anchor_products.json" <<'PY' 2>&1
import json,os,sys,datetime
def num(x):
    try: return float(str(x).replace(',',''))
    except Exception: return None
# --- 現貨 0050
spot={}
try:
    d=json.loads(os.environ["SPOT_RAW"])
    a=(d.get("msgArray") or [None])[0] or {}
    spot={"bid":num((a.get("b") or "").split("_")[0]),
          "ask":num((a.get("a") or "").split("_")[0]),
          "last":num(a.get("z")) or num(a.get("y")),
          "prev_close":num(a.get("y")),
          "time":a.get("t"),"date":a.get("d"),"name":a.get("n")}
except Exception as e:
    print("  0050 現貨解析失敗:",e)
# --- 期貨 SRFJ6
fut={}
try:
    d=json.loads(os.environ["FUT_RAW"])
    q=((d.get("RtData") or {}).get("QuoteList") or [None])[0] or {}
    fut={"bid":num(q.get("CBidPrice1")),"ask":num(q.get("CAskPrice1")),
         "last":num(q.get("CLastPrice")),"ref":num(q.get("CRefPrice")),
         "vol":q.get("CTotalVolume"),"time":q.get("CTime"),"date":q.get("CDate"),
         "sym":q.get("SymbolID")}
except Exception as e:
    print("  SRFJ6 期貨解析失敗:",e)
# --- 契約規格(有 source,不是猜)
mult=None; margin=None
try:
    ap=json.load(open(sys.argv[1]))
    srf=(ap.get("products") or {}).get("SRF") or {}
    mult=srf.get("multiplier"); margin=srf.get("initial_margin_fixed")
    print(f"  契約規格(source={ap.get('sources',{}).get('margins',{}).get('url')}):"
          f"乘數={mult} 原始保證金={margin}")
except Exception as e:
    print("  anchor_products 讀取失敗:",e)

print(f"  0050 現貨:{spot}")
print(f"  SRFJ6 期貨:{fut}")

if not (spot.get("last") and fut.get("last") and mult):
    print("  ⚠️ 報價或規格缺一,不做試算(不編數字)"); raise SystemExit

# ⚠️ 陷阱:證交所 MIS 的 z(成交價)在無成交時會缺,回退到 y(昨收)會高估現貨。
# 所以有買賣盤時一律用中價,並標明用的是哪一個。
if spot.get("bid") and spot.get("ask"):
    S=(spot["bid"]+spot["ask"])/2; s_src=f"買賣中價({spot['bid']}/{spot['ask']})"
else:
    S=spot["last"]; s_src=("昨收回退" if spot["last"]==spot.get("prev_close") else "成交價")
if fut.get("bid") and fut.get("ask"):
    F=(fut["bid"]+fut["ask"])/2; f_src=f"買賣中價({fut['bid']}/{fut['ask']})"
else:
    F=fut["last"]; f_src="成交價"
basis=F-S
print(f"  -- 現貨取價 {S} ({s_src});期貨取價 {F} ({f_src})")
print(f"  -- 基差(期貨 - 現貨)= {F} - {S} = {basis:+.2f} 點")
# 可成交基差:賣期買現(正價差收斂) / 買期賣現
if spot.get("ask") and fut.get("bid"):
    print(f"  -- 賣期買現的可成交基差 = 期貨買價 {fut['bid']} - 現貨賣價 {spot['ask']}"
          f" = {fut['bid']-spot['ask']:+.2f} 點")
if spot.get("bid") and fut.get("ask"):
    print(f"  -- 買期賣現的可成交基差 = 期貨賣價 {fut['ask']} - 現貨買價 {spot['bid']}"
          f" = {fut['ask']-spot['bid']:+.2f} 點")

# --- 到期日:股票期貨為到期月第三個星期三
def third_wed(y,m):
    d=datetime.date(y,m,1); n=0
    while True:
        if d.weekday()==2:
            n+=1
            if n==3: return d
        d+=datetime.timedelta(days=1)
EXP=third_wed(2026,10)
today=datetime.date(int(str(fut["date"])[:4]),int(str(fut["date"])[4:6]),int(str(fut["date"])[6:8]))
days=(EXP-today).days
print(f"  -- 到期日(10月第三個星期三)= {EXP},距今 {days} 天")

# --- 成本表:每一格都標「有 source」或「假設待確認」
NOTIONAL=S*mult
tax_fut_rate=0.00002     # 期貨交易稅 十萬分之二(財政部/期交所公告),買賣各一次
tax_spot_sell=0.001      # ETF 證交稅 0.1%(賣出時課)
fee_spot_rate=0.001425   # 券商公定手續費上限,折扣未知 → 假設待確認
fee_fut_per_lot=None     # 期貨手續費 每口每邊,券商報價 → 未知,不編
print(f"  -- 一張 0050 名目金額 = {S} x {mult} = {NOTIONAL:,.0f} 元")
cost=0.0; lines=[]
c=NOTIONAL*tax_fut_rate*2; cost+=c
lines.append(f"期貨交易稅 {tax_fut_rate*100:.3f}% x 買賣兩次 = {c:,.1f} 元(有 source)")
c=NOTIONAL*fee_spot_rate; cost+=c
lines.append(f"現貨買進手續費 {fee_spot_rate*100:.4f}% = {c:,.1f} 元(公定上限,折扣未知=假設待確認)")
c=NOTIONAL*fee_spot_rate; cost+=c
lines.append(f"現貨賣出手續費 {fee_spot_rate*100:.4f}% = {c:,.1f} 元(同上)")
c=NOTIONAL*tax_spot_sell; cost+=c
lines.append(f"ETF 證交稅 {tax_spot_sell*100:.2f}%(賣出)= {c:,.1f} 元(有 source)")
for l in lines: print("     "+l)
print(f"  -- 已知成本合計 = {cost:,.1f} 元,換成點數 = {cost/mult:.2f} 點")

# --- 手續費折扣敏感度:折扣是這題唯一能動的變數,做成表讓 Owner 挑自己那一格
r=0.02
carry=NOTIONAL*r*days/365
tradable = (fut["bid"]-spot["ask"]) if (fut.get("bid") and spot.get("ask")) else None
print(f"  -- 資金成本(年利率 {r*100:.1f}% 為假設待確認,{days} 天)= {carry:,.1f} 元 = {carry/mult:.2f} 點")
print("  -- 打平門檻對手續費折扣的敏感度(賣期買現方向):")
print("     折扣      現貨手續費(買+賣)   門檻(含稅+資金)   今天可成交基差   結論")
for label,disc in (("公定價",1.0),("6 折",0.6),("3 折",0.3),("2.8 折",0.28)):
    f_spot=NOTIONAL*fee_spot_rate*disc*2
    tot=f_spot + NOTIONAL*tax_fut_rate*2 + NOTIONAL*tax_spot_sell + carry
    thr=tot/mult
    if tradable is None:
        verdict="無買賣盤,不判"
        tstr="n/a"
    else:
        tstr=f"{tradable:+.2f} 點"
        verdict = "有邊" if tradable > thr else "沒有邊"
    print(f"     {label:<8} {f_spot:>10,.0f} 元        {thr:>6.2f} 點        {tstr:>9}      {verdict}")
print(f"  -- 期貨手續費未知(券商報價),假設每口每邊 10 元要再加 {10*2/mult:.3f} 點")
print("  ⚠️ 配息是這題的決定變數:持有現貨到期會領到息,期貨不會,所以期貨理論上要貼水。")
print("     觀察到的是正價差,代表市場沒有在定價到期前的除息——這句要用公告驗,下面就是驗。")
PY

echo "  -- 證交所除權除息預告表(公開,查 0050 在到期前有沒有除息):"
curl -s --max-time 12 "https://openapi.twse.com.tw/v1/exchangeReport/TWT48U" \
  | python3 -c "
import sys,json
try: rows=json.load(sys.stdin)
except Exception as e: print('     預告表解析失敗:',e); raise SystemExit
hit=[r for r in rows if isinstance(r,dict) and r.get('Code')=='0050']
print(f'     預告表共 {len(rows)} 筆,0050 命中 {len(hit)} 筆')
for r in hit[:5]: print('     ',json.dumps(r,ensure_ascii=False)[:300])
if not hit:
    print('     0050 不在預告表 → 沒有已公告、即將到來的除權除息日')
"

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
