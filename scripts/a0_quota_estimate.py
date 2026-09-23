#!/usr/bin/env python3
"""a0_quota_estimate.py — 額度自估一行(Owner msg 5557,2026-09-20)。

從本機 Claude Code 對話紀錄(~/.claude/projects/*/*.jsonl)加總 assistant
usage token,估算「這 5 小時窗」與「本週(週四 22:00 台北時間重置)」的消耗。
自估非官方:官方剩餘額度只在 Owner app 的 /usage 看得到。
只讀 usage 數字,不讀不印對話內容;stdout 只有一行,失敗時無輸出(fail-safe)。
"""
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

TAIPEI = timezone(timedelta(hours=8))


def week_reset(now):
    """最近一次過去的週四 22:00(台北)。"""
    d = now
    while d.weekday() != 3:  # Thursday
        d -= timedelta(days=1)
    r = d.replace(hour=22, minute=0, second=0, microsecond=0)
    if r > now:
        r -= timedelta(days=7)
    return r


def main():
    now = datetime.now(TAIPEI)
    reset = week_reset(now)
    five_h = now - timedelta(hours=5)
    root = os.path.expanduser("~/.claude/projects")
    cutoff_mtime = (reset - timedelta(days=1)).timestamp()

    seen = set()
    out5 = in5 = outw = inw = 0
    for path in glob.glob(os.path.join(root, "*", "*.jsonl")):
        try:
            if os.path.getmtime(path) < cutoff_mtime:
                continue
            with open(path, "r", errors="replace") as f:
                for line in f:
                    if '"usage"' not in line or '"output_tokens"' not in line:
                        continue
                    try:
                        e = json.loads(line)
                    except ValueError:
                        continue
                    if e.get("type") != "assistant":
                        continue
                    u = (e.get("message") or {}).get("usage") or {}
                    ts = e.get("timestamp")
                    if not ts or not u:
                        continue
                    uid = e.get("requestId") or e.get("uuid")
                    if uid in seen:
                        continue
                    seen.add(uid)
                    try:
                        t = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TAIPEI)
                    except ValueError:
                        continue
                    if t < reset:
                        continue
                    o = u.get("output_tokens") or 0
                    i = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
                    outw += o
                    inw += i
                    if t >= five_h:
                        out5 += o
                        in5 += i
        except OSError:
            continue

    def k(n):
        return "%.1fM" % (n / 1e6) if n >= 1e6 else "%dk" % round(n / 1e3)

    days_left = (reset + timedelta(days=7) - now).total_seconds() / 86400
    print(
        "額度自估(非官方,官方看 app /usage):近5h 出%s/入%s;本週累計 出%s/入%s;距週四22:00重置 %.1f天"
        % (k(out5), k(in5), k(outw), k(inw), days_left)
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
