#!/usr/bin/env python3
"""A8 影像管線：自動方向校正 (auto-orient) 可重用步驟。

根因：手機/相機照片常帶 EXIF Orientation 旗標（6=需順時針90、8=需逆時針90 等），
但 ffmpeg 影像輸入與 PIL Image.open 預設「不套用」該旗標，讀的是原始 pixel，
於是帶旗標的照片會側躺。此模組在 A8 所有出圖/出片最前面做一次依旗標的自動轉正，
不做盲目固定角度旋轉（不同照片旗標可能不同，盲轉會把本來正的轉歪）。

用法（可重用於所有 A8 影像步驟）：
    from a8_auto_orient import auto_orient_image      # 給 PIL 流程
    im = auto_orient_image(Image.open(path))
    # 或 CLI 批次：
    python3 a8_auto_orient.py --in <SRC_DIR|FILE> --out <DST_DIR> [--report]
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
from PIL import Image, ImageOps

EXIF_ORIENT_TAG = 274
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}

def read_orientation(im: "Image.Image") -> int:
    try:
        return int(im.getexif().get(EXIF_ORIENT_TAG, 1) or 1)
    except Exception:
        return 1

def auto_orient_image(im: "Image.Image") -> "Image.Image":
    """依 EXIF Orientation 旗標自動轉正（每張各自套用，非固定角度）。"""
    return ImageOps.exif_transpose(im)

def auto_orient_file(src: Path, dst: Path, quality: int = 95) -> dict:
    im = Image.open(src)
    before = im.size
    o = read_orientation(im)
    out = auto_orient_image(im)
    changed = out.size != before or o not in (0, 1)
    dst.parent.mkdir(parents=True, exist_ok=True)
    save = out.convert("RGB") if dst.suffix.lower() in {".jpg", ".jpeg"} else out
    if dst.suffix.lower() in {".jpg", ".jpeg"}:
        save.save(dst, quality=quality)
    else:
        save.save(dst)
    return {"file": src.name, "exif_orientation": o, "size_before": before,
            "size_after": out.size, "rotated": changed}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    src = Path(a.inp); dst = Path(a.out)
    files = [src] if src.is_file() else sorted(p for p in src.iterdir() if p.suffix.lower() in IMG_EXTS)
    rows = []
    for p in files:
        target = dst if src.is_file() else dst / p.name
        rows.append(auto_orient_file(p, target))
    if a.report:
        for r in rows:
            mark = "ROTATED" if r["rotated"] else "kept   "
            print(f"{mark} orient={r['exif_orientation']} {r['size_before']}->{r['size_after']}  {r['file']}")
    print(f"auto-oriented {len(rows)} file(s) -> {dst}")

if __name__ == "__main__":
    main()
