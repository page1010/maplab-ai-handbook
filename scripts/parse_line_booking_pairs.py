"""
parse_line_booking_pairs.py
---
純檔名 metadata 解析：不讀任何對話內容，不寫入外接硬碟。
輸出 data/line_booking_pairs.csv。
"""

import os, json, csv, re
from datetime import datetime, timedelta
from collections import defaultdict

LINE_DIR = "/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421/"
TIMETREE_JSON = "/Users/pagemacmini/maplab-ai-handbook/data/timetree_events_2022_2026.json"
OUTPUT_CSV = "/Users/pagemacmini/maplab-ai-handbook/data/line_booking_pairs.csv"

MATCH_WINDOW_DAYS = 14   # end_date ±14 天
MIN_OVERLAP_CHARS = 2    # 名字重疊≥2字才標 likely_true_positive


def load_timetree(path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    lookup = raw.get("lookup", {})
    # date_str -> set of first Chinese chars found after 外燴
    tt = defaultdict(set)
    tt_titles = {}  # date_str -> list of event titles (for report)
    for date_str, val in lookup.items():
        titles = val.get("events", [])
        tt_titles[date_str] = titles
        for title in titles:
            m = re.search(r"外燴[\s　]*([^\s　]+)", title)
            if m:
                name_part = m.group(1)
                for ch in name_part:
                    if "一" <= ch <= "鿿":
                        tt[date_str].add(ch)
                        break
    return tt, tt_titles


def parse_filename(fname):
    """Return (index, start_date, end_date, contact_name) or None."""
    stem = fname[:-4] if fname.endswith(".csv") else fname
    parts = stem.split("_", 3)
    if len(parts) < 4:
        return None
    idx, s, e, name = parts
    try:
        sd = datetime.strptime(s, "%Y%m%d").date()
        ed = datetime.strptime(e, "%Y%m%d").date()
    except ValueError:
        return None
    return idx, sd, ed, name


def first_chinese_char(text):
    for ch in text:
        if "一" <= ch <= "鿿":
            return ch
    return None


def name_overlap(line_name, tt_text):
    """Find longest ≥2-char Chinese substring of line_name present in tt_text."""
    best = ""
    for i in range(len(line_name)):
        for j in range(i + MIN_OVERLAP_CHARS, len(line_name) + 1):
            chunk = line_name[i:j]
            if all("一" <= ch <= "鿿" for ch in chunk) and chunk in tt_text:
                if len(chunk) > len(best):
                    best = chunk
    return best


def check_match(contact_name, end_date, tt, tt_titles):
    sn = first_chinese_char(contact_name)
    if not sn:
        return 0, "", "", 0
    for delta in range(-MATCH_WINDOW_DAYS, MATCH_WINDOW_DAYS + 1):
        d = (end_date + timedelta(days=delta)).isoformat()
        if sn in tt.get(d, set()):
            titles_str = "; ".join(tt_titles.get(d, []))
            likely = 1 if len(name_overlap(contact_name, titles_str)) >= MIN_OVERLAP_CHARS else 0
            return 1, d, titles_str, likely
    return 0, "", "", 0


def main():
    tt, tt_titles = load_timetree(TIMETREE_JSON)
    print(f"TimeTree: {len(tt)} 外燴日有姓名可比對")

    fnames = sorted(f for f in os.listdir(LINE_DIR) if f.endswith(".csv"))
    print(f"LINE CSV 檔數: {len(fnames)}")

    rows = []
    no_surname = 0
    for fname in fnames:
        parsed = parse_filename(fname)
        if not parsed:
            continue
        idx, sd, ed, name = parsed
        confirmed, match_date, match_events, likely = check_match(name, ed, tt, tt_titles)
        if first_chinese_char(name) is None:
            no_surname += 1
        rows.append({
            "filename": fname,
            "index": idx,
            "contact_name": name,
            "start_date": sd.isoformat(),
            "end_date": ed.isoformat(),
            "confirmed": confirmed,
            "likely_true_positive": likely,
            "match_timetree_date": match_date,
            "match_timetree_events": match_events,
        })

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "filename", "index", "contact_name",
            "start_date", "end_date",
            "confirmed", "likely_true_positive",
            "match_timetree_date", "match_timetree_events",
        ])
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    confirmed_n = sum(r["confirmed"] for r in rows)
    likely_n = sum(r["likely_true_positive"] for r in rows)
    rate = confirmed_n / total * 100 if total else 0
    precision_est = likely_n / confirmed_n * 100 if confirmed_n else 0

    print(f"\n=== 結果 ===")
    print(f"解析成功: {total} 筆")
    print(f"無中文姓名(無法比對): {no_surname} 筆")
    print(f"confirmed=1 (姓氏+日期): {confirmed_n} 筆 ({rate:.1f}%)")
    print(f"likely_true_positive (≥2字重疊): {likely_n} 筆 (精確率估 {precision_est:.0f}%)")

    # 年份分佈
    from collections import Counter
    by_year = Counter(r["end_date"][:4] for r in rows)
    by_year_conf = Counter(r["end_date"][:4] for r in rows if r["confirmed"])
    print("\n年份分佈 (end_date):")
    for y in sorted(by_year):
        print(f"  {y}: 總 {by_year[y]:4d}  confirmed {by_year_conf.get(y,0):3d}")

    # 抽查 10 筆 confirmed
    sample = [r for r in rows if r["confirmed"]][:10]
    print(f"\n=== 抽查 10 筆 confirmed (人工核對用) ===")
    for r in sample:
        print(f"  [{r['end_date']}] {r['contact_name'][:6]:<6} → TT {r['match_timetree_date']} {r['match_timetree_events'][:30]}")

    print(f"\n輸出: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
