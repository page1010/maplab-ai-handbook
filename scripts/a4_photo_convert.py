#!/usr/bin/env python3
"""A4 照片轉檔管線 — HEIC/JPG → webp，去重＋一對一 manifest。

依 skills/a4-photo-convert-sop.md v1.0（Owner msg 4751）。
Drive 唯讀；輸出寫本機 data/photo_convert/<slug>/。
根治缺陷1（跨夾雙重計數）與缺陷2（同名 webp 覆蓋）：內容雜湊去重後重新編號，
manifest.csv 保留 source_basename 與雜湊，一原檔一 webp。

用法：
  /usr/bin/python3 scripts/a4_photo_convert.py \
      --case "0621說事實木地板開幕" --case "20260621說事實木地板開幕" \
      --slug maplab-tainan-opening-tea
  可重跑：已存在的 webp 跳過。sips 失敗的檔記進 manifest error 欄不中斷。
"""

import argparse
import csv
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ASSETS_ROOT = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/MAPLAB/MAPLAB_ASSETS"
)
OUT_ROOT = Path("/Users/pagemacmini/maplab-ai-handbook/data/photo_convert")
IMG_EXTS = {".heic", ".jpg", ".jpeg", ".png"}
MAX_SIDE = 1600
QUALITY = 82


def sha1_of(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def to_webp(src: Path, dst: Path) -> str:
    """回傳空字串=成功，否則錯誤訊息。"""
    try:
        from PIL import Image
    except ImportError:
        return "PIL missing (要用系統 /usr/bin/python3)"
    work = src
    tmp = None
    if src.suffix.lower() == ".heic":
        tmp = Path(tempfile.mkstemp(suffix=".jpg")[1])
        r = subprocess.run(
            ["sips", "-s", "format", "jpeg", str(src), "--out", str(tmp)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            tmp.unlink(missing_ok=True)
            return f"sips failed: {r.stderr.strip()[:120]}"
        work = tmp
    try:
        im = Image.open(work)
        im = im.convert("RGB")
        w, h = im.size
        scale = MAX_SIDE / max(w, h)
        if scale < 1:
            im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=QUALITY)
        return ""
    except Exception as e:  # noqa: BLE001 — 單檔失敗記錄後續跑
        return f"convert failed: {e}"
    finally:
        if tmp:
            tmp.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", required=True,
                    help="MAPLAB_ASSETS 下的案夾名，可重複（同案多夾一起去重）")
    ap.add_argument("--slug", required=True, help="webp 檔名前綴")
    args = ap.parse_args()

    seen = {}  # sha1 -> (folder, path)
    for folder in args.case:
        root = ASSETS_ROOT / folder
        if not root.is_dir():
            print(f"⚠️ 案夾不存在：{root}", file=sys.stderr)
            continue
        for p in sorted(root.rglob("*")):
            if p.suffix.lower() in IMG_EXTS and p.is_file():
                digest = sha1_of(p)
                seen.setdefault(digest, (folder, p))

    if not seen:
        print("❌ 沒有找到任何圖檔")
        return 1

    out_dir = OUT_ROOT / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    ordered = sorted(seen.items(), key=lambda kv: kv[1][1].name)
    for i, (digest, (folder, src)) in enumerate(ordered, 1):
        webp_name = f"{args.slug}-{i:02d}.webp"
        dst = out_dir / webp_name
        if dst.exists():
            err = ""
        else:
            err = to_webp(src, dst)
        rows.append({
            "seq": i, "webp_name": webp_name, "source_basename": src.name,
            "source_folder": folder, "sha1": digest,
            "bytes_out": dst.stat().st_size if dst.exists() else 0,
            "error": err,
        })
        print(f"[{i:02d}/{len(ordered)}] {src.name} -> {webp_name} {'OK' if not err else 'ERR: ' + err}")

    manifest = out_dir / "manifest.csv"
    with open(manifest, "w", newline="") as f:
        f.write("# executed_by=A4, sop=a4-photo-convert-sop v1.0\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    ok = sum(1 for r in rows if not r["error"])
    print(f"✅ 去重後 {len(rows)} 張、成功 {ok}、失敗 {len(rows) - ok}；manifest：{manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
