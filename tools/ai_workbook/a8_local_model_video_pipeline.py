#!/usr/bin/env python3
"""Run A8 local-model fallback through to a rendered local MP4."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FALLBACK_RUNNER = ROOT / "tools/ai_workbook/a8_local_model_fallback.py"
VIDEO_RENDERER = ROOT / "tools/ai_workbook/a8_enhanced_video_draft.py"
AWKWARD_COPY_TERMS = [
    "取餐要順",
    "取餐",
    "順暢",
    "流暢的取餐",
    "流暢的取餐動線",
    "分開",
    "詳盡",
    "詳盡的茶點配置",
    "方便交流",
    "促進交流",
    "確保",
    "輕鬆氛圍",
    "動線穩",
    "節奏穩健",
    "節奏更穩",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--motion-spec", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model", default="qwen2.5:14b")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--seconds", type=float, default=2.4)
    parser.add_argument("--opening-seconds", type=float, default=1.55)
    parser.add_argument("--ending-seconds", type=float, default=1.7)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(detail)
    return result.stdout


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"{name} not found")
    return path


def run_local_model(args: argparse.Namespace, fallback_dir: Path) -> dict[str, Any]:
    run(
        [
            sys.executable,
            str(FALLBACK_RUNNER),
            "--manifest",
            args.manifest,
            "--metadata",
            args.metadata,
            "--motion-spec",
            args.motion_spec,
            "--out-dir",
            str(fallback_dir),
            "--model",
            args.model,
            "--timeout",
            str(args.timeout),
        ]
    )
    validation = load_json(fallback_dir / "validation.json")
    if validation.get("valid") is not True:
        raise SystemExit(
            "local model validation failed: "
            + json.dumps(validation, ensure_ascii=False)
        )
    return load_json(fallback_dir / "parsed_output.json")


def storyboard_subtitles(model_output: dict[str, Any]) -> list[str]:
    storyboard = model_output.get("storyboard")
    if not isinstance(storyboard, list) or not storyboard:
        raise SystemExit("local model output has no storyboard")

    subtitles: list[str] = []
    for index, scene in enumerate(storyboard, start=1):
        if not isinstance(scene, dict):
            raise SystemExit(f"storyboard scene {index} is not an object")
        subtitle = str(scene.get("subtitle") or "").strip()
        if not subtitle:
            raise SystemExit(f"storyboard scene {index} has no subtitle")
        for term in AWKWARD_COPY_TERMS:
            if term in subtitle:
                raise SystemExit(f"off-brand subtitle rejected: {term}")
        subtitles.append(subtitle)
    return subtitles


def render_video(
    args: argparse.Namespace,
    source_manifest: dict[str, Any],
    subtitles: list[str],
    render_dir: Path,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(VIDEO_RENDERER),
        "--asset-dir",
        str(source_manifest["asset_dir"]),
        "--out-dir",
        str(render_dir),
        "--title",
        str(source_manifest.get("title") or "台南企業茶點配置"),
        "--category",
        str(source_manifest.get("category") or "corporate_tea"),
        "--opening-title",
        "MAPLAB Kitchen",
        "--opening-subtitle",
        "台南企業會議茶點",
        "--case-label",
        str(source_manifest["case_label"]),
        "--limit",
        str(min(len(source_manifest.get("images", [])) or len(subtitles), len(subtitles))),
        "--seconds",
        str(args.seconds),
        "--opening-seconds",
        str(args.opening_seconds),
        "--ending-seconds",
        str(args.ending_seconds),
        "--transition",
        "fade",
        "--transition-seconds",
        "0.35",
    ]
    for subtitle in subtitles:
        command.extend(["--scene-line", subtitle])
    output = run(command)
    return json.loads(output)


def ffprobe(video_path: Path) -> dict[str, Any]:
    require_tool("ffprobe")
    output = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,r_frame_rate,duration",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video_path),
        ]
    )
    return json.loads(output)


def extract_qa_frames(video_path: Path, out_dir: Path, duration: float) -> list[Path]:
    require_tool("ffmpeg")
    qa_dir = out_dir / "qa_frames"
    qa_dir.mkdir(parents=True, exist_ok=True)
    offsets = [
        ("intro", 0.5),
        ("middle", max(0.5, duration / 2.0)),
        ("outro", max(0.5, duration - 0.8)),
    ]
    frames: list[Path] = []
    for label, offset in offsets:
        frame = qa_dir / f"qa-{label}.jpg"
        run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{offset:.2f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(frame),
            ]
        )
        frames.append(frame)
    return frames


def write_report(
    out_dir: Path,
    args: argparse.Namespace,
    model_output: dict[str, Any],
    render_manifest: dict[str, Any],
    probe: dict[str, Any],
    qa_frames: list[Path],
) -> None:
    report = [
        "# A8 Local Model End-to-End Video Run",
        "",
        f"- Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"- Model: {args.model}",
        "- Local model host: Ollama CLI on this Mac",
        "- MCP: none attached to the local model in this runner",
        "- Tool layer: Python runner -> Swift/AppKit frame renderer -> ffmpeg/ffprobe",
        f"- Fallback JSON: `{out_dir / 'local_model' / 'parsed_output.json'}`",
        f"- Render manifest: `{out_dir / 'rendered_video' / 'review_draft_manifest.json'}`",
        f"- Final video: `{out_dir / 'a8-short-local-model-video.mp4'}`",
        f"- Final cover: `{out_dir / 'a8-short-local-model-cover.jpg'}`",
        "",
        "## Scene Lines From Local Model",
    ]
    for index, scene in enumerate(model_output.get("storyboard", []), start=1):
        subtitle = scene.get("subtitle") if isinstance(scene, dict) else scene
        report.append(f"{index}. {subtitle}")

    report.extend(
        [
            "",
            "## Video Probe",
            "",
            "```json",
            json.dumps(probe, ensure_ascii=False, indent=2),
            "```",
            "",
            "## QA Frames",
        ]
    )
    report.extend(f"- `{frame}`" for frame in qa_frames)
    report.extend(
        [
            "",
            "## Platform Copy",
            "",
            "```json",
            json.dumps(model_output.get("platform_copy", {}), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Render Summary",
            "",
            "```json",
            json.dumps(render_manifest, ensure_ascii=False, indent=2),
            "```",
        ]
    )
    (out_dir / "pipeline_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    out_dir = Path(args.out_dir)
    fallback_dir = out_dir / "local_model"
    render_dir = out_dir / "rendered_video"
    out_dir.mkdir(parents=True, exist_ok=True)

    source_manifest = load_json(manifest_path)
    model_output = run_local_model(args, fallback_dir)
    subtitles = storyboard_subtitles(model_output)
    render_manifest = render_video(args, source_manifest, subtitles, render_dir)

    rendered_video = Path(render_manifest["video"])
    rendered_cover = Path(render_manifest["cover"])
    final_video = out_dir / "a8-short-local-model-video.mp4"
    final_cover = out_dir / "a8-short-local-model-cover.jpg"
    shutil.copyfile(rendered_video, final_video)
    shutil.copyfile(rendered_cover, final_cover)

    probe = ffprobe(final_video)
    stream = probe.get("streams", [{}])[0]
    if stream.get("codec_name") != "h264" or stream.get("width") != 1080 or stream.get("height") != 1920:
        raise SystemExit("rendered video failed H.264 1080x1920 validation")
    duration = float(probe.get("format", {}).get("duration") or stream.get("duration") or 0)
    qa_frames = extract_qa_frames(final_video, out_dir, duration)
    write_report(out_dir, args, model_output, render_manifest, probe, qa_frames)

    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "model": args.model,
                "mcp": "none_attached_direct_ollama_cli",
                "tools": ["a8_local_model_fallback.py", "a8_enhanced_video_draft.py", "swift", "ffmpeg", "ffprobe"],
                "scene_lines": subtitles,
                "video": str(final_video),
                "cover": str(final_cover),
                "probe": probe,
                "report": str(out_dir / "pipeline_report.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
