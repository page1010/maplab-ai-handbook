#!/usr/bin/env python3
"""A4 照片分類搬移 — 截圖/家庭/外燴工作 + 年月資料夾（T-A4-004）。

Owner 需求（2026-06-11）：「可以分類一下嗎 截圖 家庭 外燴工作 ＋年月份資料夾
然後已經有資料夾的不要動」

範圍：
  分類：Takeout/Google 相簿/「20XX 年的相片」年度傾倒區 + _screenshots
  不動：named albums（已經有資料夾的）、MAPLAB_ASSETS、影片、垃圾桶、失敗的影片

目標結構：photos/分類/<截圖|家庭|外燴工作>/<YYYY-MM>/

安全：只 rename 不刪除；每筆移動記 SQLite，--undo 可全量還原。
日期：Takeout sidecar JSON photoTakenTime → EXIF DateTimeOriginal → 資料夾年份。
分類：檔名/格式截圖快篩（免模型）→ gemma4 vision 判 家庭/外燴工作。

用法：
  --limit N    跑一批（預設 200）
  --status     進度
  --undo       還原所有已搬移檔案
"""

import argparse
import base64
import io
import json
import os
import re
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path

PHOTOS_ROOT = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/MAPLAB/photos"
)
TAKEOUT = PHOTOS_ROOT / "Takeout" / "Google 相簿"
SCREENSHOTS_DIR = PHOTOS_ROOT / "_screenshots"
DEST_ROOT = PHOTOS_ROOT / "分類"
DB_PATH = Path("/Users/pagemacmini/maplab-ai-handbook/data/photo_classify.db")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:latest"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif"}
YEAR_DUMP_RE = re.compile(r"^20\d{2} 年的相片$")
SCREENSHOT_NAME_RE = re.compile(
    r"screenshot|螢幕快照|螢幕擷取|截圖|screen_?shot|スクリーン", re.IGNORECASE
)

PROMPT = """看這張照片，判斷它屬於哪一類，只回答一個詞：
- 外燴工作：餐點、自助餐檯、茶點桌、活動會場、菜單、食物特寫、佈置、廚房備餐、外燴現場
- 家庭：家人、小孩、寵物、日常生活、旅遊、自拍、居家
- 截圖：手機或電腦畫面截圖、對話紀錄、文件、網頁
只輸出：外燴工作 或 家庭 或 截圖"""


def db_init() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS moves (
            src TEXT PRIMARY KEY, dst TEXT, category TEXT, ym TEXT,
            method TEXT, error TEXT, moved_at TEXT)"""
    )
    return conn


def iter_sources():
    """年度傾倒區 + _screenshots 的圖片；named albums 一律跳過。"""
    if TAKEOUT.is_dir():
        for d in sorted(TAKEOUT.iterdir()):
            if d.is_dir() and YEAR_DUMP_RE.match(d.name):
                for p in sorted(d.rglob("*")):
                    if p.is_file() and p.suffix.lower() in IMG_EXTS:
                        yield p
    if SCREENSHOTS_DIR.is_dir():
        for p in sorted(SCREENSHOTS_DIR.rglob("*")):
            if p.is_file() and p.suffix.lower() in IMG_EXTS:
                yield p


def photo_date(p: Path) -> str:
    """YYYY-MM。sidecar JSON → 檔名毫秒時間戳 → EXIF → 資料夾年份。"""
    m = re.match(r"^(1[3-9]\d{11})", p.stem)  # 13 位 unix millis（2011-2033）
    if m:
        try:
            return datetime.fromtimestamp(int(m.group(1)) / 1000).strftime("%Y-%m")
        except Exception:
            pass
    for sc in (p.with_suffix(p.suffix + ".json"),
               p.parent / (p.name + ".supplemental-metadata.json")):
        if sc.exists():
            try:
                ts = int(json.load(open(sc))["photoTakenTime"]["timestamp"])
                return datetime.fromtimestamp(ts).strftime("%Y-%m")
            except Exception:
                pass
    try:
        from PIL import Image
        exif = Image.open(p).getexif()
        dt = exif.get(36867) or exif.get(306)  # DateTimeOriginal / DateTime
        if dt:
            return f"{dt[:4]}-{dt[5:7]}"
    except Exception:
        pass
    m = re.match(r"^(20\d{2}) ", p.parent.name)
    return f"{m.group(1)}-00" if m else "unknown"


def is_screenshot_fast(p: Path) -> bool:
    if SCREENSHOTS_DIR in p.parents:
        return True
    return bool(SCREENSHOT_NAME_RE.search(p.name))


def classify_with_model(p: Path) -> str:
    from PIL import Image
    img = Image.open(p).convert("RGB")
    img.thumbnail((672, 672))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    payload = {
        "model": MODEL, "prompt": PROMPT,
        "images": [base64.b64encode(buf.getvalue()).decode()],
        "stream": False, "options": {"temperature": 0.1, "num_predict": 10},
    }
    req = urllib.request.Request(
        OLLAMA_URL, json.dumps(payload).encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        out = json.loads(resp.read())["response"]
    for cat in ("外燴工作", "家庭", "截圖"):
        if cat in out:
            return cat
    return "家庭"  # 模糊時偏保守，家庭類不會被拿去商用


def safe_move(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    i = 1
    while dst.exists():
        dst = dst_dir / f"{src.stem}_{i}{src.suffix}"
        i += 1
    os.rename(src, dst)
    # sidecar JSON 跟著走，日期資訊不遺失
    for sc in (src.with_suffix(src.suffix + ".json"),
               src.parent / (src.name + ".supplemental-metadata.json")):
        if sc.exists():
            try:
                os.rename(sc, dst_dir / sc.name)
            except OSError:
                pass
    return dst


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--undo", action="store_true")
    args = ap.parse_args()
    conn = db_init()

    if args.status:
        for row in conn.execute(
            "SELECT category, COUNT(*) FROM moves WHERE error IS NULL GROUP BY category"
        ):
            print(f"{row[0]}: {row[1]}")
        errs = conn.execute("SELECT COUNT(*) FROM moves WHERE error IS NOT NULL").fetchone()[0]
        print(f"失敗: {errs}（總目標 ~98,400 + _screenshots）")
        return

    if args.undo:
        n = 0
        for src, dst in conn.execute(
            "SELECT src, dst FROM moves WHERE error IS NULL AND dst IS NOT NULL"
        ).fetchall():
            if Path(dst).exists():
                Path(src).parent.mkdir(parents=True, exist_ok=True)
                os.rename(dst, src)
                n += 1
        conn.execute("DELETE FROM moves")
        conn.commit()
        print(f"已還原 {n} 個檔案")
        return

    done = {r[0] for r in conn.execute("SELECT src FROM moves")}
    count = 0
    for p in iter_sources():
        if count >= args.limit:
            break
        src = str(p)
        if src in done:
            continue
        try:
            if is_screenshot_fast(p):
                cat, method = "截圖", "fast"
            else:
                cat, method = classify_with_model(p), "model"
            ym = photo_date(p)
            dst = safe_move(p, DEST_ROOT / cat / ym)
            conn.execute(
                "INSERT OR REPLACE INTO moves VALUES (?,?,?,?,?,NULL,datetime('now'))",
                (src, str(dst), cat, ym, method),
            )
        except Exception as e:
            conn.execute(
                "INSERT OR REPLACE INTO moves VALUES (?,NULL,NULL,NULL,NULL,?,datetime('now'))",
                (src, str(e)[:200]),
            )
        conn.commit()
        count += 1
        if count % 100 == 0:
            print(f"...{count}/{args.limit}", flush=True)
    print(f"本批完成 {count} 張")


if __name__ == "__main__":
    main()
