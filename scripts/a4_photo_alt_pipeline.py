#!/usr/bin/env python3
"""A4 照片 ALT/SEO 管線 — 地端 gemma4 視覺模型批次產出照片中繼資料。

目的（T-HQ-002）：
  趁 Google Drive 照片還鏡像在本地，用地端模型把 MAPLAB_ASSETS 全部照片
  產出 ALT 文字（SEO 用）、場景標籤、分類建議，寫入 SQLite + CSV。
  CSV 放在 Drive 資料夾內 → 自動同步上雲 → 之後 Drive 改串流，照片離線
  釋出空間，但中繼資料永久可查。

產出貢獻：
  - A2 SEO：WordPress 圖片 ALT 文字直接取用
  - A4 素材庫：用標籤搜尋選圖，不用翻 3 萬張原圖
  - A6 提案：場景關鍵字找提案素材

用法：
  python3 a4_photo_alt_pipeline.py            # 跑一批（預設 200 張，launchd 連續排程）
  python3 a4_photo_alt_pipeline.py --limit 3  # 測試
  python3 a4_photo_alt_pipeline.py --status   # 看進度
  python3 a4_photo_alt_pipeline.py --export   # 手動匯出 CSV 到 Drive

可隨時中斷，已處理的不重跑（以相對路徑+檔案大小為 key）。
"""

import argparse
import base64
import csv
import io
import json
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

ASSETS_ROOT = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/MAPLAB/MAPLAB_ASSETS"
)
# CSV 匯出放 Drive 內 → Google Drive 自動同步上雲
EXPORT_DIR = ASSETS_ROOT / "_alt_index"
DB_PATH = Path("/Users/pagemacmini/maplab-ai-handbook/data/photo_alt_index.db")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:latest"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
MAX_SIDE = 896  # 縮圖再送模型，省時間

PROMPT = """你是 MAPLAB 外燴公司的照片資產整理員。看這張照片，輸出 JSON（只輸出 JSON，不要其他文字）：
{
  "alt_zh": "繁體中文 ALT 文字，<=60字，自然描述畫面，適合 SEO（外燴/茶點/活動情境），不要堆關鍵字",
  "scene": "場景類型，從這些選一個: 企業活動/婚禮/慶生派對/茶點桌面/餐點特寫/人物/場地空景/文件截圖/其他",
  "tags": ["3-6個繁中標籤，如 甜點塔/手指三明治/開幕茶會/戶外"],
  "usable_for_web": true 或 false（畫質清晰且無明顯人臉/私人資訊才 true）
}"""


def db_init() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS photos (
            rel_path TEXT, size INTEGER, alt_zh TEXT, scene TEXT,
            tags TEXT, usable INTEGER, error TEXT, processed_at TEXT,
            PRIMARY KEY (rel_path, size))"""
    )
    return conn


def iter_pending(conn: sqlite3.Connection):
    done = {(r[0], r[1]) for r in conn.execute("SELECT rel_path, size FROM photos")}
    for p in sorted(ASSETS_ROOT.rglob("*")):
        if p.suffix.lower() not in IMG_EXTS or "_alt_index" in p.parts:
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        rel = str(p.relative_to(ASSETS_ROOT))
        if (rel, size) not in done:
            yield p, rel, size


def encode_image(path: Path) -> str:
    from PIL import Image  # 延遲 import，--status 不需要

    img = Image.open(path)
    img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def analyze(path: Path) -> dict:
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "images": [encode_image(path)],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2},
    }
    req = urllib.request.Request(
        OLLAMA_URL, json.dumps(payload).encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(json.loads(resp.read())["response"])


def export_csv(conn: sqlite3.Connection) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = EXPORT_DIR / "photo_alt_index.csv"
    rows = conn.execute(
        "SELECT rel_path, alt_zh, scene, tags, usable, processed_at FROM photos WHERE error IS NULL ORDER BY rel_path"
    ).fetchall()
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["相對路徑", "ALT文字", "場景", "標籤", "可上網", "處理時間"])
        w.writerows(rows)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--export", action="store_true")
    args = ap.parse_args()

    conn = db_init()
    if args.status:
        done = conn.execute("SELECT COUNT(*) FROM photos WHERE error IS NULL").fetchone()[0]
        errs = conn.execute("SELECT COUNT(*) FROM photos WHERE error IS NOT NULL").fetchone()[0]
        print(f"已處理 {done} 張，失敗 {errs} 張（總目標 ~36676）")
        return
    if args.export:
        print(f"已匯出 {export_csv(conn)}")
        return

    count = 0
    for path, rel, size in iter_pending(conn):
        if count >= args.limit:
            break
        try:
            r = analyze(path)
            conn.execute(
                "INSERT OR REPLACE INTO photos VALUES (?,?,?,?,?,?,NULL,datetime('now'))",
                (rel, size, r.get("alt_zh", ""), r.get("scene", ""),
                 json.dumps(r.get("tags", []), ensure_ascii=False),
                 1 if r.get("usable_for_web") else 0),
            )
        except Exception as e:  # 單張失敗不停整批
            conn.execute(
                "INSERT OR REPLACE INTO photos VALUES (?,?,NULL,NULL,NULL,NULL,?,datetime('now'))",
                (rel, size, str(e)[:200]),
            )
        conn.commit()
        count += 1
        if count % 50 == 0:
            print(f"...{count}/{args.limit}", flush=True)

    if count:
        export_csv(conn)
    print(f"本批完成 {count} 張，CSV 已同步 Drive")


if __name__ == "__main__":
    main()
