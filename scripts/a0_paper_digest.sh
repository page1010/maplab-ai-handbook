#!/bin/bash
# a0_paper_digest.sh — 摘要 spread_paper 當日實跑:事件分佈、原生委託結果、持倉與當日已實現損益。
# 只讀不寫交易系統;輸出落 ~/.maplab/a0_paper_digest_<date>.txt 供 A0 讀後人話回報。
# 純確定性程式,零 LLM。帳號指紋可引用,原始帳號 ID 不輸出。
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
PY=/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python
DAY="${1:-$(date -u '+%Y-%m-%d')}"
OUT="$HOME/.maplab/a0_paper_digest_${DAY}.txt"

# 2026-09-23:改為同時印到 stdout。原本只寫檔 + tail -3,但 ~/.maplab/ 不在本 session
# 的允許工作目錄內,寫出去的檔案 A0 自己讀不到(跟 quote_intake 同一個坑)。
# 白名單化的 .sh 可以讀,所以由腳本自己把內容印出來,不要求呼叫端去 cat 一個讀不到的路徑。
"$PY" - "$DAY" "$OUT" <<'PY' 2>&1
import json, sys
from collections import Counter
from pathlib import Path

day, out_path = sys.argv[1], Path(sys.argv[2])
ROOT = Path("/Users/pagemacmini/investment-os")
ev_path = ROOT/"reports/spread_paper/runtime"/f"{day}.jsonl"
led_path = ROOT/"state/spread_paper/ledger.json"
lines = []

kinds = Counter()
orders, halts, decisions, notifies = [], [], Counter(), 0
if ev_path.exists():
    with ev_path.open() as f:
        for raw in f:
            try:
                e = json.loads(raw)
            except Exception:
                continue
            ev = e.get("event", "?")
            kinds[ev] += 1
            if ev == "broker_terminal_result":
                r = e.get("result", {}) or {}
                leg = e.get("leg", {}) or {}
                orders.append(f"{e.get('at','')[11:19]} {e.get('market')} {leg.get('code')} "
                              f"{leg.get('side')}{leg.get('qty')} 限{leg.get('limit_price')} "
                              f"成交{r.get('filled_qty')}@{r.get('avg_price')} {r.get('status')} {e.get('action')}")
            elif ev == "halt":
                halts.append(f"{e.get('at','')[11:19]} {e.get('market')} {e.get('reason')}")
            elif ev in ("decision", "cycle_decision", "evaluation"):
                d = e.get("reason") or (e.get("decision") or {}).get("reason")
                decisions[f"{e.get('market')}:{d}"] += 1
            elif ev == "notification_result":
                notifies += 1
else:
    lines.append(f"當日事件檔不存在:{ev_path}")

lines.append(f"[事件檔] {ev_path.name} 事件總數 {sum(kinds.values())}")
for k, n in kinds.most_common():
    lines.append(f"  {k}: {n}")
lines.append(f"[原生委託結果] {len(orders)} 筆")
lines += [f"  {o}" for o in orders[-20:]]
lines.append(f"[停止旗標] {len(halts)} 次")
lines += [f"  {h}" for h in halts[-10:]]
if decisions:
    lines.append("[決策原因分佈]")
    for k, n in decisions.most_common(15):
        lines.append(f"  {k}: {n}")
lines.append(f"[Telegram 通知] {notifies} 則")

if led_path.exists():
    led = json.loads(led_path.read_text())
    lines.append(f"[帳本] cycles={led.get('cycles')} 起始={led.get('started_at','')[:19]} "
                 f"資本={led.get('capital')} halted={led.get('halted')}")
    lines.append(f"[持倉] active {len(led.get('active', {}))} 個")
    for mk, b in led.get("active", {}).items():
        legs = "；".join(f"{l.get('code')} {l.get('side')}{l.get('qty')}"
                         f"@{(l.get('entry') or {}).get('avg_price')}" for l in b.get("legs", []))
        lines.append(f"  {mk} [{b.get('kind')}/{b.get('state')}] {b.get('strategy_name','')} "
                     f"保留{b.get('capital_reserved')} 進場{str(b.get('opened_at'))[:10]} {legs}")
    closed_today = [b for b in led.get("closed", []) if str(b.get("closed_at", ""))[:10] == day]
    lines.append(f"[當日平倉] {len(closed_today)} 個")
    for b in closed_today:
        lines.append(f"  {b.get('market')} {b.get('kind')} {b.get('exit_reason')} "
                     f"淨損益 {round((b.get('pnl') or {}).get('net_pnl', 0), 2)} {b.get('currency')}")
    lines.append(f"[歷史平倉總數] {len(led.get('closed', []))}")

    # 2026-09-23 加:ORB 全歷史逐筆,供計算實際風報比(不是設計值 50:100,是成交後的實數)。
    orb = [b for b in led.get("closed", []) if b.get("kind") == "ORB"]
    lines.append(f"[ORB 全歷史] {len(orb)} 筆")
    tot = 0.0
    for b in orb:
        pnl = round((b.get("pnl") or {}).get("net_pnl", 0), 2)
        tot += pnl
        legs = []
        for l in b.get("legs", []):
            en = (l.get("entry") or {}).get("avg_price")
            ex = (l.get("exit") or {}).get("avg_price")
            legs.append(f"{l.get('side')}{l.get('qty')} {en}->{ex}")
        lines.append(f"  {str(b.get('opened_at'))[:10]} {b.get('strategy_name','')} "
                     f"{b.get('exit_reason')} 淨 {pnl} | " + "；".join(legs))
    lines.append(f"[ORB 累計淨損益] {round(tot,2)} TWD")

    # 事件檔裡 cycle_summary 實際存了什麼欄位 —— 決定「能不能用錄下來的資料重播做移動停利測試」。
    if ev_path.exists():
        with ev_path.open() as f:
            for raw in f:
                try:
                    e = json.loads(raw)
                except Exception:
                    continue
                if e.get("event") == "cycle_summary":
                    lines.append("[cycle_summary 欄位] " + ", ".join(sorted(e.keys())))
                    lines.append("[cycle_summary 樣本] " + json.dumps(e, ensure_ascii=False)[:600])
                    break

out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"==== digest {day} ({len(lines)} 行) ====")
print("\n".join(lines))
PY
