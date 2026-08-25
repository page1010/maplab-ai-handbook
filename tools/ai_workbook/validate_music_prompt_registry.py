#!/usr/bin/env python3
"""Validate MAPLAB's versioned music prompt experiment registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


STAGES = {
    "draft_superseded",
    "planned",
    "generated_unselected",
    "selected_release",
    "rejected",
}
REQUIRED = {
    "schema_version",
    "experiment_id",
    "case_id",
    "task_id",
    "created_at",
    "provider",
    "model",
    "stage",
    "lyrics_version",
    "style_prompt_version",
    "style_prompt_path",
    "rights_basis",
    "subscription_plan",
    "generated_at",
    "provider_song_id",
    "audio_asset",
    "evaluation",
    "decision_note",
}
SCORES = {
    "brand_voice",
    "mandarin_clarity",
    "hook_memory",
    "visual_fit",
    "vocal_naturalness",
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    repo = Path(__file__).resolve().parents[2]

    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
            continue

        missing = sorted(REQUIRED - row.keys())
        if missing:
            errors.append(f"line {line_number}: missing {', '.join(missing)}")
            continue

        experiment_id = row["experiment_id"]
        if experiment_id in seen:
            errors.append(f"line {line_number}: duplicate experiment_id {experiment_id}")
        seen.add(experiment_id)

        if row["stage"] not in STAGES:
            errors.append(f"line {line_number}: invalid stage {row['stage']}")

        prompt_path = repo / row["style_prompt_path"]
        if not prompt_path.is_file():
            errors.append(f"line {line_number}: missing style prompt {row['style_prompt_path']}")

        evaluation = row["evaluation"]
        if set(evaluation) != SCORES:
            errors.append(f"line {line_number}: evaluation keys must match registry schema")
        for key, value in evaluation.items():
            if value is not None and (not isinstance(value, int) or not 1 <= value <= 5):
                errors.append(f"line {line_number}: {key} must be null or integer 1-5")

        if row["stage"] in {"generated_unselected", "selected_release", "rejected"}:
            if not row["generated_at"] or not row["provider_song_id"]:
                errors.append(f"line {line_number}: generated stage needs timestamp and provider_song_id")

        if row["stage"] == "selected_release":
            asset = row["audio_asset"]
            if asset.get("method") != "provider_download":
                errors.append(f"line {line_number}: release audio must use provider_download")
            if not asset.get("path") or not asset.get("sha256"):
                errors.append(f"line {line_number}: release audio needs path and sha256")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default="workbook/music_prompt_registry/experiments.jsonl",
        type=Path,
    )
    args = parser.parse_args()
    errors = validate(args.path)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
