#!/usr/bin/env python3
"""Build a local A8 vertical short-video dry run from a folder of images."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-dir", required=True, help="Folder containing source images")
    parser.add_argument("--out-dir", required=True, help="Output review bundle folder")
    parser.add_argument("--title", required=True, help="Short video title overlay")
    parser.add_argument("--subtitle", default="", help="Short subtitle overlay")
    parser.add_argument("--case-label", default="", help="Public-safe case label")
    parser.add_argument("--limit", type=int, default=5, help="Maximum images to use")
    parser.add_argument("--seconds", type=float, default=3.0, help="Seconds per image")
    parser.add_argument("--keep-segments", action="store_true", help="Keep intermediate segment files")
    return parser.parse_args()


def ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found")
    return path


def choose_font() -> str | None:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def escape_drawtext(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace("\n", "\\n")
    )


def escape_filter_path(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(" ", "\\ ")
    )


def run_ffmpeg(command: list[str]) -> None:
    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip())


def ffmpeg_has_filter(ffmpeg_bin: str, name: str) -> bool:
    result = subprocess.run(
        [ffmpeg_bin, "-hide_banner", "-filters"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return f" {name} " in result.stdout


def list_images(asset_dir: Path, limit: int) -> list[Path]:
    images = sorted(p for p in asset_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not images:
        raise SystemExit(f"no images found in {asset_dir}")
    return images[:limit]


def make_segment(
    ffmpeg_bin: str,
    image: Path,
    out_path: Path,
    title: str,
    subtitle: str,
    seconds: float,
    font: str | None,
    use_drawtext: bool,
) -> None:
    title_text = escape_drawtext(title)
    subtitle_text = escape_drawtext(subtitle)
    font_part = f"fontfile={escape_filter_path(font)}:" if font else ""
    base_vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if use_drawtext:
        vf = (
            f"{base_vf},"
            "drawbox=x=0:y=0:w=iw:h=360:color=black@0.34:t=fill,"
            f"drawtext={font_part}text='{title_text}':x=72:y=86:fontsize=62:"
            "fontcolor=white:line_spacing=8,"
            f"drawtext={font_part}text='{subtitle_text}':x=72:y=236:fontsize=38:"
            "fontcolor=white@0.92,"
            "format=yuv420p"
        )
    else:
        vf = f"{base_vf},format=yuv420p"
    run_ffmpeg(
        [
            ffmpeg_bin,
            "-y",
            "-loop",
            "1",
            "-t",
            str(seconds),
            "-i",
            str(image),
            "-vf",
            vf,
            "-r",
            "30",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(out_path),
        ]
    )


def concat_segments(ffmpeg_bin: str, segments: list[Path], out_path: Path, concat_file: Path) -> None:
    concat_file.write_text(
        "".join(f"file '{segment.resolve()}'\n" for segment in segments),
        encoding="utf-8",
    )
    run_ffmpeg(
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
    run_ffmpeg(
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


def write_platform_pack(out_dir: Path, args: argparse.Namespace, images: list[Path]) -> None:
    case_label = args.case_label or args.title
    metadata = {
        "youtube_shorts": {
            "title": f"{case_label} | 台南企業外燴茶點 #Shorts",
            "description": (
                "大臺南會展中心企業會議茶點紀錄。"
                "以好拿取的點心、飲品補給與乾淨桌面配置，讓中場休息和交流節奏更穩。"
            ),
            "hashtags": ["#台南外燴", "#企業外燴", "#會議茶點", "#MAPLAB", "#Shorts"],
        },
        "tiktok": {
            "caption": f"{case_label}。會議中場休息的茶點配置，重點是好拿取、畫面乾淨、節奏不打斷。",
            "hashtags": ["#台南外燴", "#企業茶點", "#活動餐點", "#MAPLAB"],
        },
        "pinterest": {
            "board": "MAPLAB Catering / Corporate Refreshments",
            "pin_title": f"{case_label} - 台南企業外燴茶點封面",
            "pin_description": "大臺南會展中心企業會議茶點與飲品桌面配置參考。",
        },
    }
    (out_dir / "platform_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# A8 Platform Metadata Pack",
        "",
        f"Case: {case_label}",
        f"Source images: {len(images)}",
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
        "",
        "## Source Files",
    ]
    lines.extend(f"- `{image}`" for image in images)
    (out_dir / "platform_metadata.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    asset_dir = Path(args.asset_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    segments_dir = out_dir / "segments"
    out_dir.mkdir(parents=True, exist_ok=True)
    segments_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = ffmpeg()
    font = choose_font()
    use_drawtext = ffmpeg_has_filter(ffmpeg_bin, "drawtext")
    images = list_images(asset_dir, args.limit)
    segments: list[Path] = []

    for index, image in enumerate(images, start=1):
        segment = segments_dir / f"segment-{index:02d}.mp4"
        make_segment(
            ffmpeg_bin,
            image,
            segment,
            args.title,
            args.subtitle,
            args.seconds,
            font,
            use_drawtext,
        )
        segments.append(segment)

    video_path = out_dir / "a8-short-dry-run.mp4"
    cover_path = out_dir / "a8-short-cover.jpg"
    concat_segments(ffmpeg_bin, segments, video_path, out_dir / "segments.txt")
    extract_cover(ffmpeg_bin, video_path, cover_path)
    write_platform_pack(out_dir, args, images)
    if not args.keep_segments:
        shutil.rmtree(segments_dir, ignore_errors=True)
        (out_dir / "segments.txt").unlink(missing_ok=True)

    manifest = {
        "asset_dir": str(asset_dir),
        "out_dir": str(out_dir),
        "title": args.title,
        "subtitle": args.subtitle,
        "case_label": args.case_label,
        "images": [str(image) for image in images],
        "video": str(video_path),
        "cover": str(cover_path),
        "font": font,
        "text_overlay": "rendered" if use_drawtext else "metadata_only_ffmpeg_drawtext_unavailable",
        "status": "dry_run_rendered",
    }
    (out_dir / "dry_run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
