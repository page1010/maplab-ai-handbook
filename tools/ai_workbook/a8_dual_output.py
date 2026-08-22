#!/usr/bin/env python3
"""A8 雙輸出：一首 Suno 全曲 + 一組素材 → 同時產
  版A|YouTube 長版 16:9（全曲全素材、長度=歌長、慢切）
  版B|YT Shorts 短版 9:16（hook 前置、30–60s、對拍快切）
需 numpy（/tmp/ttsenv/bin/python）。ffmpeg 系統版。
用法：/tmp/ttsenv/bin/python a8_dual_output.py <suno_full.mp3> <out_prefix> <clip1> [clip2...] [--short-max 45]
輸出：<prefix>_long_16x9.mp4 + <prefix>_short_9x16.mp4（檔名回填 DB outputs）。
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a8_beat_mux import render

def main():
    a = sys.argv
    music, prefix = a[1], a[2]
    short_max = float(a[a.index("--short-max")+1]) if "--short-max" in a else 30.0  # Owner: Shorts ≤30s
    clips = [c for c in a[3:] if not c.startswith("--") and Path(c).exists()]
    if not clips:
        print("need clips"); return
    long_out = f"{prefix}_long_16x9.mp4"
    short_out = f"{prefix}_short_9x16.mp4"
    print("=== 版A YouTube 長版 16:9（全曲、慢切 perbar=8）===")
    render(music, long_out, clips, maxsec=None, perbar=8, aspect="16:9")
    print("=== 版B YT Shorts 9:16（前 %ss hook 前置、快切 perbar=4）===" % short_max)
    render(music, short_out, clips, maxsec=short_max, perbar=4, aspect="9:16")
    print("DUAL_DONE", long_out, short_out)

if __name__ == "__main__":
    main()
