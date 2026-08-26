#!/usr/bin/env python3
"""Fail-closed acceptance gate for A8 final video candidates.

This gate deliberately validates evidence, not aesthetics by proxy.  A render exit
code, ffprobe metadata, or a contact sheet alone can never advance a candidate to
OWNER_VIDEO_GATE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SCHEMA_VERSION = "maplab.a8.video-acceptance/v1"
STATES = [
    "AUDIO_SELECTED",
    "TIMING_LOCKED",
    "EDIT_READY",
    "RENDERED_UNVERIFIED",
    "QA_PASS",
    "OWNER_VIDEO_GATE",
    "APPROVED_FOR_UPLOAD",
]
FINAL_ENGINES = {"capcut_manual", "approved_nle_manual", "ffmpeg_one_pass"}


def _error(errors: List[Dict[str, str]], code: str, message: str) -> None:
    if not any(item["code"] == code for item in errors):
        errors.append({"code": code, "message": message})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve(path_value: str, receipt_path: Optional[Path]) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute() or receipt_path is None:
        return path
    return (receipt_path.parent / path).resolve()


def _check_binding(
    errors: List[Dict[str, str]],
    binding: Any,
    code: str,
    label: str,
    receipt_path: Optional[Path],
    verify_files: bool,
) -> None:
    if not isinstance(binding, dict) or not binding.get("path") or not binding.get("sha256"):
        _error(errors, code, f"{label} requires path and sha256")
        return
    if not verify_files:
        return
    path = _resolve(str(binding["path"]), receipt_path)
    if not path.is_file():
        _error(errors, code, f"{label} file does not exist: {path}")
        return
    if _sha256(path) != str(binding["sha256"]).lower():
        _error(errors, code, f"{label} sha256 does not match the file")


def _valid_transition_history(history: Any, target_state: str) -> bool:
    if not isinstance(history, list) or not history:
        return False
    if any(item not in STATES for item in history):
        return False
    indices = [STATES.index(item) for item in history]
    if indices != list(range(indices[0], indices[-1] + 1)):
        return False
    return history[-1] == target_state and history[0] == STATES[0]


def verify_receipt(
    receipt: Dict[str, Any],
    receipt_path: Optional[Path] = None,
    verify_files: bool = True,
) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []

    if receipt.get("schema_version") != SCHEMA_VERSION:
        _error(errors, "SCHEMA_VERSION_INVALID", f"schema_version must be {SCHEMA_VERSION}")

    state = str(receipt.get("state", ""))
    if state not in STATES:
        _error(errors, "STATE_INVALID", "state is not an A8 acceptance state")
    elif not _valid_transition_history(receipt.get("state_history"), state):
        _error(errors, "STATE_TRANSITION_INVALID", "state_history must be contiguous from AUDIO_SELECTED")

    approvals = receipt.get("approvals") or {}
    _check_binding(
        errors,
        approvals.get("lyrics"),
        "LYRICS_BINDING_INVALID",
        "approved lyrics",
        receipt_path,
        verify_files,
    )
    audio = approvals.get("audio") or {}
    _check_binding(
        errors,
        audio,
        "AUDIO_BINDING_INVALID",
        "selected audio",
        receipt_path,
        verify_files,
    )
    audio_qa = audio.get("qa") if isinstance(audio, dict) else {}
    if not isinstance(audio_qa, dict) or not audio_qa.get("actual_audio_asr_pass"):
        _error(errors, "AUDIO_ASR_FAILED", "selected audio requires prompt-free actual-audio ASR PASS")
    if not isinstance(audio_qa, dict) or not audio_qa.get("brand_exact_tokens_pass"):
        _error(errors, "BRAND_TOKEN_FAILED", "all required brand tokens must pass exact-token listening/ASR")
    if not isinstance(audio_qa, dict) or not audio_qa.get("human_listen_pass"):
        _error(errors, "HUMAN_LISTEN_MISSING", "selected audio requires a named human full-listen PASS")

    timing = receipt.get("timing") or {}
    _check_binding(
        errors,
        timing.get("alignment"),
        "LYRIC_ALIGNMENT_MISSING",
        "lyric alignment",
        receipt_path,
        verify_files,
    )
    cues = timing.get("cues")
    if timing.get("approved_lyrics_match") is not True:
        _error(errors, "LYRICS_AUDIO_MISMATCH", "timed/sung lines must exactly match the approved lyrics binding")
    if not isinstance(cues, list) or not cues:
        _error(errors, "LYRIC_ALIGNMENT_MISSING", "timing.cues must contain approved lyric text with in/out times")
    else:
        prior_end = -1
        for cue in cues:
            if not isinstance(cue, dict):
                _error(errors, "LYRIC_CUE_INVALID", "each lyric cue must be an object")
                break
            text = str(cue.get("text", "")).strip()
            start_ms = cue.get("start_ms")
            end_ms = cue.get("end_ms")
            if not text or not isinstance(start_ms, int) or not isinstance(end_ms, int) or start_ms < 0 or end_ms <= start_ms:
                _error(errors, "LYRIC_CUE_INVALID", "each lyric cue needs text and increasing integer start_ms/end_ms")
                break
            if start_ms < prior_end:
                _error(errors, "LYRIC_CUE_OVERLAP", "lyric cues may not overlap")
                break
            prior_end = end_ms
        if timing.get("max_onset_error_ms", 10**9) > 100:
            _error(errors, "LYRIC_ONSET_OUT_OF_TOLERANCE", "30fps lyric onset error must be <=100ms")
        if timing.get("max_tail_error_ms", 10**9) > 200:
            _error(errors, "LYRIC_TAIL_OUT_OF_TOLERANCE", "lyric tail error must be <=200ms")
        lead_in_ms = timing.get("hook_lead_in_ms")
        if not isinstance(lead_in_ms, int) or not 200 <= lead_in_ms <= 500:
            _error(errors, "HOOK_CUT_INVALID", "hook must keep 200-500ms before the first sung token")
        if timing.get("starts_mid_word") is not False:
            _error(errors, "HOOK_CUT_INVALID", "hook may not start in the middle of a word")

    sources = receipt.get("sources")
    if not isinstance(sources, list) or not sources:
        _error(errors, "RAW_PROVENANCE_UNBOUND", "at least one raw source is required")
    else:
        for source in sources:
            if not isinstance(source, dict) or not source.get("raw_path") or not source.get("raw_sha256"):
                _error(errors, "RAW_PROVENANCE_UNBOUND", "every source requires raw_path and raw_sha256")
                break
            raw_path = str(source.get("raw_path", "")).lower()
            if "approved_sources" in raw_path or source.get("is_proxy") is not False:
                _error(errors, "RAW_PROVENANCE_UNBOUND", "final timeline must bind raw originals, not H.264 proxies")
            if source.get("privacy_status") != "APPROVED":
                _error(errors, "SOURCE_PRIVACY_UNAPPROVED", "every raw source needs an APPROVED privacy verdict")
            trim = source.get("trim") or {}
            if not isinstance(trim.get("in_ms"), int) or not isinstance(trim.get("out_ms"), int) or trim["out_ms"] <= trim["in_ms"]:
                _error(errors, "SOURCE_TRIM_INVALID", "every source needs a valid safe in/out window")
            if source.get("layout") == "blur_sidebars":
                _error(errors, "BLUR_LAYOUT_FORBIDDEN", "blurred sidebars are not an approved final layout")
            if source.get("crop_strategy") == "blind_center_crop":
                _error(errors, "BLIND_CROP_FORBIDDEN", "blind center crop is forbidden")
            if verify_files and source.get("raw_path") and source.get("raw_sha256"):
                path = _resolve(str(source["raw_path"]), receipt_path)
                if not path.is_file() or _sha256(path) != str(source["raw_sha256"]).lower():
                    _error(errors, "RAW_PROVENANCE_UNBOUND", "raw source path/hash does not match")

    edit = receipt.get("edit") or {}
    engine = edit.get("engine")
    if engine not in FINAL_ENGINES:
        _error(errors, "FINAL_EDITOR_MISSING", "final edit engine must be CapCut/manual NLE or one-pass FFmpeg")
    _check_binding(errors, edit.get("timeline_receipt"), "TIMELINE_RECEIPT_MISSING", "timeline receipt", receipt_path, verify_files)
    if engine in {"capcut_manual", "approved_nle_manual"}:
        _check_binding(errors, edit.get("project"), "EDITOR_PROJECT_MISSING", "editable NLE project", receipt_path, verify_files)
    if engine == "ffmpeg_one_pass" and edit.get("no_intermediate_video") is not True:
        _error(errors, "INTERMEDIATE_VIDEO_FORBIDDEN", "ffmpeg final path must declare no_intermediate_video=true")
    if edit.get("lyric_and_marketing_tracks_separate") is not True:
        _error(errors, "TEXT_TRACKS_CONFLATED", "lyrics and marketing overlays must be separate tracks")

    encoding = receipt.get("encoding") or {}
    if encoding.get("actual_lossy_video_encode_depth") != 1:
        _error(errors, "ENCODE_DEPTH_EXCEEDED", "final output must have exactly one lossy video encode")
    if encoding.get("max_lossy_video_encode_depth") != 1:
        _error(errors, "ENCODE_POLICY_INVALID", "max_lossy_video_encode_depth must be 1")
    _check_binding(errors, encoding.get("lineage"), "ENCODE_LINEAGE_MISSING", "encoding lineage", receipt_path, verify_files)

    output = receipt.get("output") or {}
    _check_binding(errors, output, "OUTPUT_BINDING_INVALID", "rendered output", receipt_path, verify_files)
    duration_ms = output.get("duration_ms") if isinstance(output, dict) else None

    qa = receipt.get("visual_qa") or {}
    _check_binding(errors, qa.get("timeline_contact_sheet"), "TIMELINE_QA_MISSING", "timeline contact sheet", receipt_path, verify_files)
    playback = qa.get("full_playback") or {}
    for speed in ("1x", "0.5x"):
        record = playback.get(speed) or {}
        if record.get("verdict") != "PASS" or not isinstance(record.get("watched_duration_ms"), int):
            _error(errors, "FULL_PLAYBACK_MISSING", f"full playback at {speed} requires duration and PASS")
        elif isinstance(duration_ms, int) and record["watched_duration_ms"] < duration_ms:
            _error(errors, "FULL_PLAYBACK_MISSING", f"full playback at {speed} did not cover the whole output")
    if qa.get("target_device_pass") is not True:
        _error(errors, "TARGET_DEVICE_QA_MISSING", "target-device visual QA must pass")
    if qa.get("blur_sidebars_absent") is not True or qa.get("blind_crop_absent") is not True:
        _error(errors, "VISUAL_LAYOUT_FAILED", "visual QA must confirm no blur sidebars and no blind crop")

    return errors


def _print_result(receipt_path: Path, errors: Iterable[Dict[str, str]]) -> int:
    error_list = list(errors)
    result = {
        "receipt": str(receipt_path),
        "ok": not error_list,
        "error_count": len(error_list),
        "errors": error_list,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not error_list else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an A8 video acceptance receipt")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--no-file-check", action="store_true", help="validate schema only; never use for release")
    args = parser.parse_args()
    receipt_path = args.receipt.expanduser().resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    return _print_result(
        receipt_path,
        verify_receipt(receipt, receipt_path=receipt_path, verify_files=not args.no_file_check),
    )


if __name__ == "__main__":
    raise SystemExit(main())
