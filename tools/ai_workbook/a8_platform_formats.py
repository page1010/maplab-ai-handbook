#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
a8_platform_formats.py — MAPLAB A8 各平台影片格式 config + review-only 匯出。

用途：
  一份 config = 各平台正確「比例/解析度/片長上限/安全區/縮圖尺寸」的單一真相來源，
  PLATFORM_FORMATS 是平台規格的單一真相來源。
  舊 export_for_platforms() 會呼叫 a8_beat_mux（中心裁切＋多代 H.264），只可做
  review diagnostic；不得把它的輸出當 final 或 upload candidate。

規格出處（2026-08 查證，見 docs/platform_formats_sources.md）：
  YouTube Shorts / IG Reels / FB Reels / TikTok = 9:16 1080x1920 H.264 mp4。
  YouTube 長版 = 16:9 1920x1080；縮圖 1280x720 (16:9)。
  Owner 定案：我方 Shorts/垂直短片一律壓 ≤30s（平台本身允許更長）。

review-only 依賴：a8_beat_mux.render（對拍剪輯，含 aspect/maxsec）＋ ffmpeg（縮圖）。
file-only、不花錢。
"""
import sys, subprocess, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


REVIEW_CLASSIFICATION = "REVIEW_ONLY_NOT_FOR_UPLOAD"


def _review_render(*args, **kwargs):
    """Lazy import keeps read-only specs usable without loading the legacy renderer."""
    from a8_beat_mux import render

    return render(*args, **kwargs)

# 我方 Shorts/垂直短片統一上限（Owner 定案）。平台本身允許更長，但我們刻意壓 ≤30s。
VERTICAL_MAX_SEC = 30.0

# ── 平台格式 config（單一真相來源）────────────────────────────────────
# aspect/w/h：輸出比例與解析度  max_sec：我方片長上限(None=全曲不限)  perbar：對拍切點密度(小=快切)
# thumb：(寬,高) 縮圖  safe：字幕/重點安全區(佔畫面比例，避開 UI)  note：備註
PLATFORM_FORMATS = {
    "youtube_long": {
        "label": "YouTube 長版",
        "aspect": "16:9", "w": 1920, "h": 1080, "max_sec": None, "perbar": 8,
        "thumb": (1280, 720), "thumb_ratio": "16:9",
        "fps": 30, "container": "mp4", "vcodec": "h264", "acodec": "aac",
        "safe": {"top": 0.05, "bottom": 0.08, "left": 0.05, "right": 0.05},
        "note": "全曲＋全素材、慢切。縮圖 1280x720 (16:9)，JPG/PNG，<1MB 即夠(平台上限已放寬到 50MB)。"
    },
    "youtube_shorts": {
        "label": "YouTube Shorts",
        "aspect": "9:16", "w": 1080, "h": 1920, "max_sec": VERTICAL_MAX_SEC, "perbar": 4,
        "thumb": (1080, 1920), "thumb_ratio": "9:16",
        "fps": 30, "container": "mp4", "vcodec": "h264", "acodec": "aac",
        "safe": {"top": 0.10, "bottom": 0.10, "left": 0.05, "right": 0.10},
        "note": "≤30s、hook 前置、前3秒下 hook、對拍快切。縮圖從影格擷取(桌面可上傳)；標題/描述加 #Shorts。"
    },
    "instagram_reels": {
        "label": "IG Reels",
        "aspect": "9:16", "w": 1080, "h": 1920, "max_sec": VERTICAL_MAX_SEC, "perbar": 4,
        "thumb": (1080, 1920), "thumb_ratio": "9:16",
        "fps": 30, "container": "mp4", "vcodec": "h264", "acodec": "aac",
        "safe": {"top": 0.10, "bottom": 0.20, "left": 0.05, "right": 0.10},
        "note": "字幕避開下 20%(留給平台字幕)、右 10%(互動鍵)、上 10%。Feed 會裁成 4:5，重點置中。"
    },
    "tiktok": {
        "label": "TikTok",
        "aspect": "9:16", "w": 1080, "h": 1920, "max_sec": VERTICAL_MAX_SEC, "perbar": 4,
        "thumb": (1080, 1920), "thumb_ratio": "9:16",
        "fps": 30, "container": "mp4", "vcodec": "h264", "acodec": "aac",
        "safe": {"top": 0.08, "bottom": 0.15, "left": 0.05, "right": 0.12},
        "note": "上有帳號、右有動作鍵、下有 caption 區；重點/字幕留在中間安全區。封面(cover)另從影格選。"
    },
    "facebook_reels": {
        "label": "Facebook Reels",
        "aspect": "9:16", "w": 1080, "h": 1920, "max_sec": VERTICAL_MAX_SEC, "perbar": 4,
        "thumb": (1080, 1920), "thumb_ratio": "9:16",
        "fps": 30, "container": "mp4", "vcodec": "h264", "acodec": "aac",
        "safe": {"top": 0.10, "bottom": 0.20, "left": 0.05, "right": 0.10},
        "note": "2025-06 起 FB 影片一律當 Reels。封面 9:16 ≥1080 寬；另可備 1:1 縮圖給版面。"
    },
    "instagram_feed": {
        "label": "IG Feed(直式)",
        "aspect": "4:5", "w": 1080, "h": 1350, "max_sec": VERTICAL_MAX_SEC, "perbar": 4,
        "thumb": (1080, 1350), "thumb_ratio": "4:5",
        "fps": 30, "container": "mp4", "vcodec": "h264", "acodec": "aac",
        "safe": {"top": 0.06, "bottom": 0.10, "left": 0.05, "right": 0.05},
        "note": "直式 Feed 貼文 4:5 佔版面最大。若只想發 Reels 可略過此格式。"
    },
}

# 群組別名：一次選一組平台
GROUPS = {
    "all": list(PLATFORM_FORMATS.keys()),
    "vertical": ["youtube_shorts", "instagram_reels", "tiktok", "facebook_reels"],  # 9:16 短片全發
    "youtube": ["youtube_long", "youtube_shorts"],  # Owner 主目標：長版＋Shorts
}


def resolve_platforms(names):
    """展開群組別名 → 去重後的平台清單（保序）。"""
    out = []
    for n in names:
        if n in GROUPS:
            out.extend(GROUPS[n])
        elif n in PLATFORM_FORMATS:
            out.append(n)
        else:
            print(f"  ! 未知平台/群組：{n}（略過）")
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return uniq


def _render_key(spec):
    """相同輸出規格共用一次 render。"""
    return (spec["aspect"], spec["w"], spec["h"], spec["max_sec"], spec["perbar"])


def make_thumbnail(video, out_jpg, size, at_sec=1.0):
    """從影片擷取一格 → crop 置中 → scale 到縮圖尺寸。"""
    w, h = size
    vf = (f"crop='min(iw,ih*{w}/{h})':'min(ih,iw*{h}/{w})',"
          f"scale={w}:{h}:flags=lanczos")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(at_sec), "-i", str(video),
           "-vframes", "1", "-vf", vf, "-q:v", "3", str(out_jpg)]
    subprocess.run(cmd, check=True)
    return out_jpg


def export_for_platforms(
    music,
    prefix,
    clips,
    platforms,
    outdir=".",
    thumbs=True,
    *,
    review_only=False,
):
    """
    依平台清單輸出 review diagnostic。相同 render 規格只 render 一次。

    這條 legacy renderer 會中心裁切並產生多代 H.264，因此預設 fail closed。
    呼叫者必須明確傳 review_only=True；manifest 也會逐項標為不可上傳。
    """
    if review_only is not True:
        raise RuntimeError(
            "final export refused: a8_beat_mux uses blind center crop and multiple "
            "lossy video encodes; use specs for dimensions or pass review_only=True "
            "for an internal diagnostic only"
        )
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    plats = resolve_platforms(platforms)
    if not plats:
        print("no valid platforms"); return {}

    # 1) 依 render_key 分組，同規格 render 一次
    key_to_base = {}
    manifest = {}
    for p in plats:
        spec = PLATFORM_FORMATS[p]
        key = _render_key(spec)
        if key not in key_to_base:
            base = str(outdir / f"{prefix}__base_{spec['aspect'].replace(':','x')}_{int(spec['max_sec']) if spec['max_sec'] else 'full'}.mp4")
            print(f"=== render {spec['label']} 規格 {spec['aspect']} {spec['w']}x{spec['h']} "
                  f"max={spec['max_sec']} perbar={spec['perbar']} ===")
            _review_render(
                music,
                base,
                clips,
                maxsec=spec["max_sec"],
                perbar=spec["perbar"],
                aspect=spec["aspect"],
            )
            key_to_base[key] = base
        base = key_to_base[key]
        # 2) 每平台一份 review 檔（複製 base）
        final = str(outdir / f"{prefix}_{p}.mp4")
        if final != base:
            shutil.copyfile(base, final)
        entry = {
            "classification": REVIEW_CLASSIFICATION,
            "video": final,
            "thumb": None,
            "spec": {k: spec[k] for k in ("aspect", "w", "h", "max_sec", "thumb", "safe", "note")},
            "release_restrictions": [
                "blind_center_crop_not_subject_safe",
                "multiple_lossy_video_encodes",
                "acceptance_receipt_required_from_a_different_final_path",
            ],
        }
        # 3) 每平台縮圖
        if thumbs:
            tj = str(outdir / f"{prefix}_{p}_thumb.jpg")
            try:
                make_thumbnail(final, tj, spec["thumb"])
                entry["thumb"] = tj
            except Exception as e:
                print(f"  ! {p} 縮圖失敗：{e}")
        manifest[p] = entry
        print(f"  ✓ {p}: {Path(final).name}" + (f" + {Path(entry['thumb']).name}" if entry["thumb"] else ""))

    # 清掉中間 base（若與最終檔不同名）
    for base in set(key_to_base.values()):
        if base not in [m["video"] for m in manifest.values()] and Path(base).exists():
            Path(base).unlink()
    return manifest


def _print_specs():
    print("MAPLAB A8 平台格式表（Owner 垂直片上限 %.0fs）\n" % VERTICAL_MAX_SEC)
    for p, s in PLATFORM_FORMATS.items():
        mx = "全曲" if s["max_sec"] is None else f"≤{int(s['max_sec'])}s"
        print(f"[{p}] {s['label']}: {s['aspect']} {s['w']}x{s['h']} | 片長 {mx} | 縮圖 {s['thumb'][0]}x{s['thumb'][1]} | "
              f"安全區 上{int(s['safe']['top']*100)}% 下{int(s['safe']['bottom']*100)}% 右{int(s['safe']['right']*100)}%")
        print(f"     {s['note']}")
    print("\n群組：", {g: v for g, v in GROUPS.items()})


def main():
    a = sys.argv
    if len(a) < 2 or a[1] in ("-h", "--help", "specs"):
        if len(a) >= 2 and a[1] == "specs":
            _print_specs(); return
        print("用法：")
        print("  a8_platform_formats.py specs                     # 印各平台格式表")
        print("  a8_platform_formats.py export                    # 拒絕舊 final exporter")
        print("  a8_platform_formats.py review-export <music> <prefix> <clip...> [--platforms youtube vertical|all|<name>...] [--outdir DIR] [--no-thumbs]")
        return 0
    if a[1] == "export":
        print(
            "REFUSED: legacy exporter blind-crops and performs multiple lossy video "
            "encodes. Use 'specs' for dimensions; use 'review-export' only for an "
            "internal diagnostic."
        )
        return 2
    if a[1] == "review-export":
        if len(a) < 5:
            print("need music, prefix, and at least one clip")
            return 2
        music, prefix = a[2], a[3]
        rest = a[4:]
        platforms = ["youtube"]
        outdir = "."
        thumbs = True
        if "--platforms" in rest:
            i = rest.index("--platforms")
            platforms = []
            for x in rest[i+1:]:
                if x.startswith("--"):
                    break
                platforms.append(x)
            rest = rest[:i]
        if "--outdir" in a:
            outdir = a[a.index("--outdir")+1]
        if "--no-thumbs" in a:
            thumbs = False
        clips = [c for c in rest if not c.startswith("--") and Path(c).exists()]
        if not clips:
            print("need clips")
            return 2
        m = export_for_platforms(
            music,
            prefix,
            clips,
            platforms,
            outdir=outdir,
            thumbs=thumbs,
            review_only=True,
        )
        print("\nMANIFEST")
        for p, e in m.items():
            print(
                f"  {p}: {e['video']} | {e['classification']}"
                + (f" | thumb {e['thumb']}" if e["thumb"] else "")
            )
        return 0
    else:
        print("unknown cmd; try: specs | export | review-export")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
