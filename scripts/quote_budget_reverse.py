#!/usr/bin/env python3
"""quote_budget_reverse.py — 預算反推報價引擎(零模型依賴;A6/任何 agent 可直接呼叫,Fable 空也能報)。
規則來源:docs/business-requirements/quote-pricing-logic.md(毛利≥70%,成本上限=預算×0.30)、
skills/a5-quote-margin-path-sop.md(配數:成本15-16→30-40件/20-23→30/30→25/40→20)。
成本正典:data/items_master.json(Items 分頁快照)。查不到的品項用最相近品類,並標 ASSUMED。
用法: quote_budget_reverse.py --budget 30000 --people 100 --items "打拋豬薄餅,綠咖哩鹹派,..." [--margin 0.70] [--json]
"""
import argparse, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "data", "items_master.json")

# 同義/相近品類對照(找不到精確品項時用)
ALIASES = {
    "薄餅": ["烤薄餅", "薄餅"], "pizza": ["薄餅"], "披薩": ["薄餅"],
    "鹹派": ["鹹派"], "三明治": ["三明治"], "蝦棗": ["蝦棗"], "可頌": ["可頌"], "漢堡": ["小漢堡"],
}
BEEF = ("牛",); MUSHROOM = ("菇", "松露"); TOMATO = ("番茄", "茄")

def load_master():
    d = json.load(open(MASTER, encoding="utf-8"))
    return d if isinstance(d, list) else d.get("items", d.get("rows", []))

def cost_for(name, rows):
    """回 (cost, basis, assumed)。先精確含名,再 alias 品類平均。"""
    for r in rows:
        if name in r.get("standard_name", "") and str(r.get("default_cost", "")).strip():
            return float(r["default_cost"]), r["standard_name"], False
    for key, needles in ALIASES.items():
        if key in name:
            cs = [float(r["default_cost"]) for r in rows if any(n in r.get("standard_name", "") for n in needles) and str(r.get("default_cost", "")).strip()]
            if cs:
                return round(sum(cs) / len(cs), 1), f"{key}類平均({len(cs)}項)", True
    return 20.0, "無對照,預設 20", True

def qty_band(cost):
    if cost <= 16: return 35
    if cost <= 23: return 30
    if cost <= 30: return 25
    return 20

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, required=True); ap.add_argument("--people", type=int, required=True)
    ap.add_argument("--items", required=True); ap.add_argument("--margin", type=float, default=0.70)
    ap.add_argument("--json", action="store_true"); a = ap.parse_args()
    rows = load_master(); names = [s.strip() for s in a.items.split(",") if s.strip()]
    cap = a.budget * (1 - a.margin)
    scale = max(1.0, a.people / 40.0)  # 配數基準以 40 人實案為 1x
    lines = []
    for n in names:
        c, basis, assumed = cost_for(n, rows)
        q = int(round(qty_band(c) * scale / 2))  # 多品項分攤:每品約半基準
        lines.append({"item": n, "unit_cost": c, "qty": q, "subtotal": round(c * q), "basis": basis, "assumed": assumed,
                      "flags": [f for f, ks in (("含牛?", BEEF), ("含菇?", MUSHROOM), ("含番茄?", TOMATO)) if any(k in n for k in ks)]})
    total = sum(l["subtotal"] for l in lines)
    # 超過成本上限就等比縮
    if total > cap:
        f = cap / total
        for l in lines: l["qty"] = max(1, int(l["qty"] * f)); l["subtotal"] = round(l["unit_cost"] * l["qty"])
        total = sum(l["subtotal"] for l in lines)
    margin = (a.budget - total) / a.budget
    out = {"budget": a.budget, "people": a.people, "cost_cap": cap, "total_cost": total, "margin_pct": round(margin * 100, 1),
           "pass_floor": margin >= a.margin, "pieces": sum(l["qty"] for l in lines), "per_person": round(sum(l["qty"] for l in lines) / a.people, 2), "lines": lines,
           "note": "成本=食材層(Items 正典);人力/運輸/耗材未計。ASSUMED 品項請廚房確認。"}
    if a.json: print(json.dumps(out, ensure_ascii=False, indent=1)); return
    print(f"預算 {a.budget:.0f} / {a.people} 人 / 毛利底線 {a.margin*100:.0f}% → 成本上限 {cap:.0f}")
    for l in lines: print(f"- {l['item']}: 成本 {l['unit_cost']} × {l['qty']} = {l['subtotal']}  [{l['basis']}{' ASSUMED' if l['assumed'] else ''}] {' '.join(l['flags'])}")
    print(f"合計 {out['pieces']} 件({out['per_person']}/人) 成本 {total:.0f} → 毛利 {out['margin_pct']}% {'✅' if out['pass_floor'] else '❌ 低於底線'}")
    print(out["note"])

if __name__ == "__main__": main()
