#!/usr/bin/env python3
"""Render an evidence-bound A8 timeline in one lossy video encode.

This is the deterministic equivalent path for cases where a manual NLE is not
used.  It is intentionally narrow: raw video shots, explicit trims/layouts,
pre-rendered transparent overlays, and one audio interval.  It refuses proxies,
blur layouts, implicit crops, and hash drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple


FORBIDDEN_PATH_PARTS = {"approved_sources", "review_draft_work"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path_value: str, config_path: Path) -> Path:
    path = Path(path_value).expanduser()
    return path if path.is_absolute() else (config_path.parent / path).resolve()


def require_binding(binding: Dict[str, Any], config_path: Path, label: str) -> Path:
    if not isinstance(binding, dict) or not binding.get("path") or not binding.get("sha256"):
        raise ValueError(f"{label} requires path and sha256")
    path = resolve(str(binding["path"]), config_path)
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {path}")
    if sha256(path) != str(binding["sha256"]).lower():
        raise ValueError(f"{label} hash drift: {path}")
    return path


def validate_config(config: Dict[str, Any], config_path: Path) -> Tuple[int, int, int, int]:
    canvas = config.get("canvas") or {}
    width = int(canvas.get("width", 0))
    height = int(canvas.get("height", 0))
    fps = int(canvas.get("fps", 0))
    if width <= 0 or height <= 0 or fps <= 0:
        raise ValueError("canvas requires positive width, height, and fps")

    shots = config.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("shots must be a non-empty list")
    total_ms = 0
    for index, shot in enumerate(shots):
        source = require_binding(shot.get("source") or {}, config_path, f"shot {index} source")
        lowered = {part.lower() for part in source.parts}
        if lowered.intersection(FORBIDDEN_PATH_PARTS) or shot.get("is_proxy") is not False:
            raise ValueError(f"shot {index} must bind a raw original, not a proxy")
        in_ms = int(shot.get("in_ms", -1))
        out_ms = int(shot.get("out_ms", -1))
        duration_ms = int(shot.get("duration_ms", -1))
        if in_ms < 0 or out_ms <= in_ms or duration_ms <= 0:
            raise ValueError(f"shot {index} requires valid in_ms/out_ms/duration_ms")
        layout = shot.get("layout") or {}
        mode = layout.get("mode")
        if mode == "blur_sidebars" or mode == "blind_center_crop":
            raise ValueError(f"shot {index} uses a forbidden implicit layout")
        if mode not in {"fit_brand_canvas", "manual_crop"}:
            raise ValueError(f"shot {index} layout must be fit_brand_canvas or manual_crop")
        if mode == "manual_crop":
            crop = layout.get("crop") or {}
            if not all(isinstance(crop.get(key), int) for key in ("width", "height", "x", "y")):
                raise ValueError(f"shot {index} manual_crop requires integer width/height/x/y")
        total_ms += duration_ms

    audio = config.get("audio") or {}
    require_binding(audio, config_path, "audio")
    audio_in = int(audio.get("in_ms", -1))
    audio_out = int(audio.get("out_ms", -1))
    if audio_in < 0 or audio_out <= audio_in:
        raise ValueError("audio requires valid in_ms/out_ms")
    if abs((audio_out - audio_in) - total_ms) > 20:
        raise ValueError("audio interval and summed shot durations must match within 20ms")

    for index, overlay in enumerate(config.get("overlays") or []):
        require_binding(overlay, config_path, f"overlay {index}")
        start_ms = int(overlay.get("start_ms", -1))
        end_ms = int(overlay.get("end_ms", -1))
        if start_ms < 0 or end_ms <= start_ms or end_ms > total_ms:
            raise ValueError(f"overlay {index} requires a valid interval inside the output")

    return width, height, fps, total_ms


def build_command(config: Dict[str, Any], config_path: Path, output: Path, overwrite: bool) -> List[str]:
    width, height, fps, total_ms = validate_config(config, config_path)
    shots = config["shots"]
    overlays = config.get("overlays") or []
    audio = config["audio"]

    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y" if overwrite else "-n"]
    for shot in shots:
        command.extend(["-i", str(resolve(shot["source"]["path"], config_path))])
    for overlay in overlays:
        command.extend(["-loop", "1", "-framerate", str(fps), "-i", str(resolve(overlay["path"], config_path))])
    audio_input_index = len(shots) + len(overlays)
    command.extend(["-i", str(resolve(audio["path"], config_path))])

    filters: List[str] = []
    video_labels: List[str] = []
    for index, shot in enumerate(shots):
        source_ms = shot["out_ms"] - shot["in_ms"]
        speed_factor = shot["duration_ms"] / source_ms
        layout = shot["layout"]
        chain = [
            f"[{index}:v]trim=start={shot['in_ms'] / 1000:.6f}:end={shot['out_ms'] / 1000:.6f}",
            f"setpts=(PTS-STARTPTS)*{speed_factor:.9f}",
            f"trim=duration={shot['duration_ms'] / 1000:.6f}",
            f"fps={fps}",
        ]
        if layout["mode"] == "fit_brand_canvas":
            chain.extend([
                f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos",
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0xFAF7F2",
            ])
        else:
            crop = layout["crop"]
            chain.extend([
                f"crop={crop['width']}:{crop['height']}:{crop['x']}:{crop['y']}",
                f"scale={width}:{height}:flags=lanczos",
            ])
        label = f"shot{index}"
        chain.extend(["setsar=1", "format=yuv420p"])
        filters.append(",".join(chain) + f"[{label}]")
        video_labels.append(f"[{label}]")

    filters.append("".join(video_labels) + f"concat=n={len(shots)}:v=1:a=0[base]")
    current_label = "base"
    for offset, overlay in enumerate(overlays):
        input_index = len(shots) + offset
        overlay_label = f"overlay{offset}"
        next_label = f"layer{offset}"
        filters.append(
            f"[{input_index}:v]trim=duration={total_ms / 1000:.6f},setpts=PTS-STARTPTS,format=rgba[{overlay_label}]"
        )
        filters.append(
            f"[{current_label}][{overlay_label}]overlay=0:0:enable='between(t,{overlay['start_ms'] / 1000:.6f},{overlay['end_ms'] / 1000:.6f})'[{next_label}]"
        )
        current_label = next_label

    filters.append(
        f"[{audio_input_index}:a]atrim=start={audio['in_ms'] / 1000:.6f}:end={audio['out_ms'] / 1000:.6f},asetpts=PTS-STARTPTS[audio]"
    )
    command.extend([
        "-filter_complex", ";".join(filters),
        "-map", f"[{current_label}]",
        "-map", "[audio]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-c:a", "aac",
        "-b:a", "256k",
        "-movflags", "+faststart",
        "-t", f"{total_ms / 1000:.6f}",
        str(output),
    ])
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an A8 explicit timeline with one video encode")
    parser.add_argument("config", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    config_path = args.config.expanduser().resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output = resolve(config["output"]["path"], config_path)
    lineage_path = resolve(config["lineage_path"], config_path)
    command = build_command(config, config_path, output, args.overwrite)
    if args.dry_run:
        print(json.dumps({"ok": True, "command": command}, ensure_ascii=False, indent=2))
        return 0
    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True)
    lineage = {
        "schema_version": "maplab.a8.ffmpeg-one-pass-lineage/v1",
        "config_path": str(config_path),
        "config_sha256": sha256(config_path),
        "command": command,
        "no_intermediate_video": True,
        "actual_lossy_video_encode_depth": 1,
        "output": {"path": str(output), "sha256": sha256(output)},
    }
    lineage_path.write_text(json.dumps(lineage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(lineage, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
