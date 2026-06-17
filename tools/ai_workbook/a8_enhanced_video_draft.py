#!/usr/bin/env python3
"""Build an A8 review draft with rendered subtitles and MAPLAB watermark."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SWIFT_RENDERER = ROOT / "tools/ai_workbook/a8_render_story_frame.swift"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_SCENE_LINES = [
    "台南企業會議茶點",
    "好拿取，交流不中斷",
    "休息時間，動線要穩",
    "甜點與飲品分區",
    "日期、人數、場地先傳給我們",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--case-label", required=True)
    parser.add_argument("--scene-line", action="append", default=[])
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--seconds", type=float, default=2.8)
    parser.add_argument("--watermark", default="MAPLAB Kitchen")
    parser.add_argument("--keep-work", action="store_true")
    return parser.parse_args()


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"{name} not found")
    return path


def run(command: list[str]) -> None:
    env = None
    if Path(command[0]).name == "swift" or command[0] == "swift":
        env = {
            **dict(os.environ),
            "CLANG_MODULE_CACHE_PATH": "/private/tmp/clang_module_cache",
            "SWIFT_MODULE_CACHE_PATH": "/private/tmp/swift_module_cache",
        }
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(detail)


def list_images(asset_dir: Path, limit: int) -> list[Path]:
    images = sorted(p for p in asset_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not images:
        raise SystemExit(f"no images found in {asset_dir}")
    return images[:limit]


def scene_lines(args: argparse.Namespace, count: int) -> list[str]:
    lines = args.scene_line or DEFAULT_SCENE_LINES
    if len(lines) < count:
        lines = lines + [lines[-1]] * (count - len(lines))
    return lines[:count]


def render_frames(
    swift_bin: str,
    images: list[Path],
    out_dir: Path,
    args: argparse.Namespace,
    lines: list[str],
) -> list[Path]:
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    frames: list[Path] = []
    for index, image in enumerate(images, start=1):
        frame = frames_dir / f"frame-{index:02d}.png"
        scene_tag = f"{index:02d}/{len(images):02d}"
        run(
            [
                swift_bin,
                str(SWIFT_RENDERER),
                str(image),
                str(frame),
                args.title,
                lines[index - 1],
                args.watermark,
                scene_tag,
            ]
        )
        frames.append(frame)
    return frames


def make_segment(ffmpeg_bin: str, frame: Path, segment: Path, seconds: float) -> None:
    run(
        [
            ffmpeg_bin,
            "-y",
            "-loop",
            "1",
            "-t",
            str(seconds),
            "-i",
            str(frame),
            "-r",
            "30",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(segment),
        ]
    )


def concat(ffmpeg_bin: str, segments: list[Path], out_path: Path, concat_file: Path) -> None:
    concat_file.write_text(
        "".join(f"file '{segment.resolve()}'\n" for segment in segments),
        encoding="utf-8",
    )
    run(
        [
            ffmpeg_bin,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(out_path),
        ]
    )


def extract_cover(ffmpeg_bin: str, video_path: Path, cover_path: Path) -> None:
    run(
        [
            ffmpeg_bin,
            "-y",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(cover_path),
        ]
    )


def write_metadata(out_dir: Path, args: argparse.Namespace, images: list[Path], lines: list[str]) -> None:
    metadata = {
        "youtube_shorts": {
            "title": f"{args.case_label} | 台南企業外燴茶點 #Shorts",
            "description": (
                "大臺南會展中心企業會議茶點紀錄。"
                "以好拿取、畫面乾淨、休息時間不打斷交流為主。"
            ),
            "hashtags": ["#台南外燴", "#企業外燴", "#會議茶點", "#MAPLAB", "#Shorts"],
            "music_note": "建議上傳後使用平台授權音樂庫，不在本機嵌入未授權配樂。",
        },
        "tiktok": {
            "caption": f"{args.case_label}。會議休息時間的茶點配置，重點是好拿取、動線穩。",
            "hashtags": ["#台南外燴", "#企業茶點", "#活動餐點", "#MAPLAB"],
            "music_note": "建議使用 TikTok app/Studio 授權音源後再發布。",
        },
        "pinterest": {
            "board": "MAPLAB Catering / Corporate Refreshments",
            "pin_title": f"{args.case_label}｜台南企業外燴茶點",
            "pin_description": "大臺南會展中心企業會議茶點與飲品桌面配置參考。",
        },
    }
    (out_dir / "review_draft_platform_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines_out = [
        "# A8 Review Draft Metadata",
        "",
        f"- Case label: {args.case_label}",
        f"- Scene count: {len(images)}",
        "- Audio: none in local draft; add licensed platform music before publishing.",
        "",
        "## Scene Lines",
    ]
    lines_out.extend(f"{index}. {line}" for index, line in enumerate(lines, start=1))
    lines_out.extend(
        [
            "",
            "## YouTube Shorts",
            f"- Title: {metadata['youtube_shorts']['title']}",
            f"- Description: {metadata['youtube_shorts']['description']}",
            f"- Hashtags: {' '.join(metadata['youtube_shorts']['hashtags'])}",
            "",
            "## TikTok",
            f"- Caption: {metadata['tiktok']['caption']}",
            f"- Hashtags: {' '.join(metadata['tiktok']['hashtags'])}",
            "",
            "## Pinterest",
            f"- Board: {metadata['pinterest']['board']}",
            f"- Pin title: {metadata['pinterest']['pin_title']}",
            f"- Pin description: {metadata['pinterest']['pin_description']}",
        ]
    )
    (out_dir / "review_draft_platform_metadata.md").write_text(
        "\n".join(lines_out) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    asset_dir = Path(args.asset_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    work_dir = out_dir / "review_draft_work"
    segments_dir = work_dir / "segments"
    out_dir.mkdir(parents=True, exist_ok=True)
    segments_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = require_tool("ffmpeg")
    swift_bin = require_tool("swift")
    if not SWIFT_RENDERER.exists():
        raise SystemExit(f"missing renderer: {SWIFT_RENDERER}")

    images = list_images(asset_dir, args.limit)
    lines = scene_lines(args, len(images))
    frames = render_frames(swift_bin, images, work_dir, args, lines)

    segments: list[Path] = []
    for index, frame in enumerate(frames, start=1):
        segment = segments_dir / f"segment-{index:02d}.mp4"
        make_segment(ffmpeg_bin, frame, segment, args.seconds)
        segments.append(segment)

    video_path = out_dir / "a8-short-review-draft.mp4"
    cover_path = out_dir / "a8-short-review-cover.jpg"
    concat(ffmpeg_bin, segments, video_path, work_dir / "segments.txt")
    extract_cover(ffmpeg_bin, video_path, cover_path)
    write_metadata(out_dir, args, images, lines)

    manifest = {
        "asset_dir": str(asset_dir),
        "out_dir": str(out_dir),
        "case_label": args.case_label,
        "title": args.title,
        "images": [str(image) for image in images],
        "scene_lines": lines,
        "video": str(video_path),
        "cover": str(cover_path),
        "watermark": args.watermark,
        "subtitle_overlay": "swift_appkit_rendered",
        "audio": "none_local_draft_add_platform_licensed_music_before_publish",
        "status": "review_draft_rendered",
    }
    (out_dir / "review_draft_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if not args.keep_work:
        shutil.rmtree(work_dir, ignore_errors=True)

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
