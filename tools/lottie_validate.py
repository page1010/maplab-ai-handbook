#!/usr/bin/env python3
"""Validate minimal Lottie JSON structure for MAPLAB motion assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _collect_keyframe_times(value: Any, times: list[float]) -> None:
    if isinstance(value, dict):
        if _is_number(value.get("t")):
            times.append(float(value["t"]))
        for child in value.values():
            _collect_keyframe_times(child, times)
    elif isinstance(value, list):
        for child in value:
            _collect_keyframe_times(child, times)


def validate_lottie(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return {"ok": False, "errors": ["root must be a JSON object"], "warnings": [], "metrics": {}}

    for field in ("v", "fr", "ip", "op", "w", "h", "layers"):
        if field not in data:
            errors.append(f"missing required field: {field}")

    fr = data.get("fr")
    ip = data.get("ip")
    op = data.get("op")
    width = data.get("w")
    height = data.get("h")
    layers = data.get("layers")

    if not isinstance(data.get("v"), str):
        errors.append("v must be a string")
    if not _is_number(fr) or fr <= 0:
        errors.append("fr must be a positive number")
    if not _is_number(ip):
        errors.append("ip must be a number")
    if not _is_number(op):
        errors.append("op must be a number")
    if _is_number(ip) and _is_number(op) and op <= ip:
        errors.append("op must be greater than ip")
    if not isinstance(width, int) or width <= 0:
        errors.append("w must be a positive integer")
    if not isinstance(height, int) or height <= 0:
        errors.append("h must be a positive integer")
    if not isinstance(layers, list) or not layers:
        errors.append("layers must be a non-empty list")

    duration = None
    if _is_number(fr) and _is_number(ip) and _is_number(op) and fr > 0 and op > ip:
        duration = round((op - ip) / fr, 3)
        if duration > 6:
            warnings.append(f"duration {duration}s is long for loading/icon motion")
        if duration < 0.5:
            warnings.append(f"duration {duration}s may be too short")

    if isinstance(width, int) and isinstance(height, int):
        if width > 2048 or height > 2048:
            warnings.append("canvas is larger than 2048px; verify performance")
        if width != height:
            warnings.append("canvas is not square; icon/loading assets usually should be square")

    shape_layers = 0
    asset_refs = 0
    keyframe_times: list[float] = []
    if isinstance(layers, list):
        for index, layer in enumerate(layers):
            if not isinstance(layer, dict):
                errors.append(f"layer[{index}] must be an object")
                continue
            layer_type = layer.get("ty")
            if "ks" not in layer:
                warnings.append(f"layer[{index}] missing transform ks")
            if layer_type == 4:
                shape_layers += 1
                shapes = layer.get("shapes")
                if not isinstance(shapes, list) or not shapes:
                    errors.append(f"shape layer[{index}] must have non-empty shapes")
            if layer_type == 2:
                asset_refs += 1
                warnings.append(f"layer[{index}] references external image asset")
            _collect_keyframe_times(layer, keyframe_times)

    if shape_layers == 0:
        warnings.append("no shape layers found; verify renderer compatibility")
    if asset_refs:
        warnings.append("image assets reduce portability; prefer pure shape layers")
    if len(layers) > 20:
        warnings.append("more than 20 layers; consider simplifying")
    if _is_number(ip) and _is_number(op):
        outside = [t for t in keyframe_times if t < ip or t > op]
        if outside:
            errors.append(f"{len(outside)} keyframe time(s) outside ip/op")

    metrics = {
        "version": data.get("v"),
        "width": width,
        "height": height,
        "frame_rate": fr,
        "in_point": ip,
        "out_point": op,
        "duration_seconds": duration,
        "layer_count": len(layers) if isinstance(layers, list) else None,
        "shape_layer_count": shape_layers,
        "image_asset_layer_count": asset_refs,
        "keyframe_count": len(keyframe_times),
    }
    return {"ok": not errors, "errors": errors, "warnings": warnings, "metrics": metrics}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate minimal Lottie JSON structure.")
    parser.add_argument("path", type=Path, help="Path to a Lottie .json file")
    args = parser.parse_args()

    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except Exception as exc:
        result = {"ok": False, "errors": [f"cannot read/parse JSON: {exc}"], "warnings": [], "metrics": {}}
    else:
        result = validate_lottie(data)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
