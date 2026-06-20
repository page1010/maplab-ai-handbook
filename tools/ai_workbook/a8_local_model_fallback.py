#!/usr/bin/env python3
"""Run a validator-gated A8 local-model fallback draft."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "qwen2.5:14b"
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
REQUIRED_KEYS = {
    "fallback_verdict",
    "storyboard",
    "platform_copy",
    "risks",
    "needs_cloud_tool",
    "validator_notes",
}
PUBLIC_COPY_BLOCKLIST = [
    "/Users/",
    "workbook/",
    ".webp",
    ".mp4",
    "0612",
    "工研院",
    "在宅醫療",
    "跨部會",
]
UNSUPPORTED_VISUAL_TERMS = [
    "工作人員",
    "人群",
    "來賓",
    "笑",
    "交談",
    "對話",
    "完美",
    "團隊",
    "蒸氣",
    "咖啡",
]
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
BRAND_REWRITE_MAP = {
    "會議中場，取餐要順": "茶點動線清楚",
    "小份量點心，方便交流": "交流節奏不被打斷",
    "飲品與甜點分區": "飲品甜點分區",
    "桌面乾淨，節奏更穩": "桌面留白乾淨",
    "台南活動茶點規劃": "台南企業茶會",
    "取餐要順": "茶點動線清楚",
    "取餐": "茶點",
    "順暢": "清楚",
    "分開": "分區",
    "詳盡": "完整",
    "方便交流": "交流節奏不被打斷",
    "促進交流": "保留交流節奏",
    "確保": "讓",
    "動線穩": "桌面留白乾淨",
    "節奏穩健": "節奏舒服",
    "節奏更穩": "節奏舒服",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--motion-spec", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=180)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def brand_clean(value: Any) -> Any:
    if isinstance(value, str):
        cleaned = value
        for bad, good in BRAND_REWRITE_MAP.items():
            cleaned = cleaned.replace(bad, good)
        return cleaned
    if isinstance(value, list):
        return [brand_clean(item) for item in value]
    if isinstance(value, dict):
        return {key: brand_clean(item) for key, item in value.items()}
    return value


def compact_manifest(manifest: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    images = [
        {"id": f"img{index}", "filename": Path(path).name}
        for index, path in enumerate(manifest.get("images", []), start=1)
    ]
    youtube = metadata.get("youtube_shorts", {})
    tiktok = metadata.get("tiktok", {})
    pinterest = metadata.get("pinterest", {})
    platform_seed = brand_clean({
        "youtube_title": youtube.get("title"),
        "youtube_description": youtube.get("description"),
        "tiktok_caption": tiktok.get("caption"),
        "pinterest_title": pinterest.get("pin_title"),
        "hashtags": youtube.get("hashtags") or tiktok.get("hashtags") or [],
    })
    return {
        "case_label": manifest.get("case_label"),
        "category": manifest.get("category"),
        "title": manifest.get("title"),
        "cta_line": manifest.get("cta_line"),
        "scene_lines": brand_clean(manifest.get("scene_lines", [])),
        "image_refs": images,
        "visual_template": manifest.get("visual_template"),
        "counter": manifest.get("counter"),
        "transition": manifest.get("transition"),
        "audio": manifest.get("audio"),
        "platform_seed": platform_seed,
    }


def build_prompt(case_packet: dict[str, Any], motion_spec_excerpt: str) -> str:
    scene_lines = case_packet.get("scene_lines") or []
    scene_packet = [
        {"scene": index, "source_ref": f"scene_line_{index}", "subtitle": line}
        for index, line in enumerate(scene_lines, start=1)
    ]
    return f"""你是 MAPLAB A8 地端備援模型。這是短 prompt 訓練，不是自由創作。

Stage 1 角色邊界：
- 你只根據 case_label / scene_lines / CTA 產 draft。
- 不要引用檔名，不要寫本機路徑。
- 不要宣稱看到了未提供的物件。
- 你不能說已上傳、已發布、已排程。
- 你只能協助 storyboard draft、platform copy draft、risk checklist。

Stage 2 MAPLAB 風格：
- 語氣自然、溫暖、具體、場景先行，不硬賣。
- 字幕要像 MAPLAB IG 文案，不要像內部流程檢查。
- 把「取餐要順」這類內部說法改成「茶點動線清楚」「交流節奏不被打斷」這類優雅說法。
- 可用語感：茶點動線清楚、交流節奏不被打斷、飲品甜點分區、桌面留白乾淨、短暫休息也有畫面。
- 本案 storyboard subtitle 優先沿用這五句：茶點動線清楚、交流節奏不被打斷、飲品甜點分區、桌面留白乾淨、台南企業茶會。
- 本案 visual_instruction 優先沿用這五句：桌面配置與留白、小份量甜點特寫、飲品甜點分區、乾淨桌面層次、茶會配置收束。
- 不要用確保、詳盡、分開、取餐、順暢、促進交流、動線穩、節奏更穩、節奏穩健；這些太像內部流程或硬銷。
- CTA 使用既定 line，不自行改寫：{case_packet.get("cta_line")}
- platform_copy 不可空白，必須包含 CTA 原文。
- 若 platform_copy 不知道怎麼寫，就複製 Case.platform_seed 的同名欄位；絕對不要留空字串。
- 若 Case.platform_seed 含禁用詞，必須依 JSON schema 範例改寫，不能照抄禁用詞。
- 每個字串都要短，不能在字串中換行。

Stage 3 輸出硬規則：
- 只輸出 JSON object。
- 不要 markdown。
- 不要換行塞進 JSON string。
- visual_instruction 最多 18 個中文字。
- source_status 只能是 scene_line 或 manifest。
- needs_cloud_tool 必須是 true。
- 不得使用這些未驗證詞：{", ".join(UNSUPPORTED_VISUAL_TERMS)}
- 不得使用這些不優雅或內部流程詞：{", ".join(AWKWARD_COPY_TERMS)}
- 為每個分鏡選擇合適的運鏡 (motion)：dolly_in（近景特寫放大）, dolly_out（近景特寫縮小）, pan_right（長桌左到右平移）, pan_left（長桌右到左平移）, static（無動態）。

JSON schema:
{{
  "fallback_verdict": "usable_draft | needs_review",
  "model_role": "A8_local_backup",
  "storyboard": [
    {{
      "scene": 1,
      "subtitle": "短字幕",
      "visual_instruction": "短畫面指示",
      "motion": "dolly_in | dolly_out | pan_right | pan_left | static",
      "source_status": "scene_line | manifest",
      "risk": "none | needs_review"
    }}
  ],
  "platform_copy": {{
    "youtube_title": "{case_packet.get("case_label")} | 台南企業外燴茶點 #Shorts",
    "youtube_description": "{case_packet.get("case_label")}。短暫休息也保留交流節奏。{case_packet.get("cta_line")}",
    "tiktok_caption": "{case_packet.get("case_label")}。茶點動線清楚，桌面留白乾淨。{case_packet.get("cta_line")}",
    "pinterest_title": "{case_packet.get("case_label")}｜台南企業外燴茶點",
    "hashtags": ["#台南外燴", "#企業外燴", "#會議茶點", "#MAPLAB", "#Shorts"]
  }},
  "risks": [],
  "needs_cloud_tool": true,
  "validator_notes": []
}}

Motion spec short:
{motion_spec_excerpt}

Case:
{json.dumps({"case_label": case_packet.get("case_label"), "category": case_packet.get("category"), "cta_line": case_packet.get("cta_line"), "scene_lines": scene_packet, "platform_seed": case_packet.get("platform_seed")}, ensure_ascii=False, indent=2)}
"""


def sanitize(raw: str) -> str:
    return ANSI_RE.sub("", raw).strip()


def extract_json(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[index:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    raise ValueError("no JSON object found")


def escape_newlines_inside_strings(text: str) -> str:
    chars: list[str] = []
    in_string = False
    escaped = False
    for char in text:
        if escaped:
            chars.append(char)
            escaped = False
            continue
        if char == "\\" and in_string:
            chars.append(char)
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            chars.append(char)
            continue
        if char in {"\n", "\r"} and in_string:
            chars.append("\\n")
            continue
        chars.append(char)
    return "".join(chars)


def collect_public_copy(obj: dict[str, Any]) -> str:
    platform_copy = obj.get("platform_copy", {})
    if not isinstance(platform_copy, dict):
        return ""
    parts: list[str] = []
    for value in platform_copy.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    return "\n".join(parts)


def validate(obj: dict[str, Any], expected_cta: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    missing = sorted(REQUIRED_KEYS - set(obj))
    if missing:
        errors.append(f"missing required keys: {', '.join(missing)}")

    if obj.get("model_role") != "A8_local_backup":
        warnings.append("model_role is not A8_local_backup")

    if obj.get("needs_cloud_tool") is not True:
        warnings.append("needs_cloud_tool should be true for final video polish / publishing")

    public_copy = collect_public_copy(obj)
    if expected_cta and expected_cta not in public_copy:
        errors.append("expected CTA not found in platform_copy")

    platform_copy = obj.get("platform_copy")
    if not isinstance(platform_copy, dict):
        errors.append("platform_copy must be an object")
    else:
        for key in ["youtube_title", "youtube_description", "tiktok_caption", "pinterest_title"]:
            if not str(platform_copy.get(key) or "").strip():
                errors.append(f"platform_copy.{key} is empty")
        hashtags = platform_copy.get("hashtags")
        if not isinstance(hashtags, list) or not hashtags:
            errors.append("platform_copy.hashtags is empty")

    for marker in PUBLIC_COPY_BLOCKLIST:
        if marker in public_copy:
            errors.append(f"public copy contains blocked marker: {marker}")
    for term in AWKWARD_COPY_TERMS:
        if term in public_copy:
            errors.append(f"public copy contains awkward or off-brand copy: {term}")

    storyboard = obj.get("storyboard")
    if not isinstance(storyboard, list) or not storyboard:
        errors.append("storyboard must be a non-empty list")
    else:
        for index, scene in enumerate(storyboard, start=1):
            if not isinstance(scene, dict):
                errors.append(f"storyboard scene {index} is not an object")
                continue
            if scene.get("source_status") not in {"scene_line", "filename_only", "manifest"}:
                warnings.append(f"scene {index} source_status is weak or missing")
            visual_instruction = str(scene.get("visual_instruction") or "")
            for term in UNSUPPORTED_VISUAL_TERMS:
                if term in visual_instruction:
                    errors.append(f"scene {index} unsupported visual claim: {term}")
            
            motion = scene.get("motion")
            valid_motions = {"dolly_in", "dolly_out", "pan_right", "pan_left", "static"}
            if motion not in valid_motions:
                errors.append(f"scene {index} motion '{motion}' is invalid")

            scene_public_text = "\n".join(
                str(scene.get(key) or "") for key in ["subtitle", "visual_instruction"]
            )
            for term in AWKWARD_COPY_TERMS:
                if term in scene_public_text:
                    errors.append(f"scene {index} awkward or off-brand copy: {term}")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def run_ollama(model: str, prompt: str, timeout: int) -> str:
    result = subprocess.run(
        ["ollama", "run", model, "--format", "json", "--nowordwrap", "--hidethinking"],
        input=prompt,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    metadata_path = Path(args.metadata)
    motion_spec_path = Path(args.motion_spec)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(manifest_path)
    metadata = load_json(metadata_path)
    motion_spec_excerpt = motion_spec_path.read_text(encoding="utf-8")[:3600]
    case_packet = compact_manifest(manifest, metadata)
    prompt = build_prompt(case_packet, motion_spec_excerpt)

    raw = run_ollama(args.model, prompt, args.timeout)
    cleaned = sanitize(raw)

    parsed: dict[str, Any] | None = None
    validation: dict[str, Any]
    try:
        parsed = extract_json(cleaned)
        validation = validate(parsed, str(case_packet.get("cta_line") or ""))
    except Exception as exc:  # noqa: BLE001 - validator report should preserve the failure text.
        try:
            repaired = escape_newlines_inside_strings(cleaned)
            parsed = extract_json(repaired)
            validation = validate(parsed, str(case_packet.get("cta_line") or ""))
            validation["warnings"].append("JSON repaired by escaping model newlines inside strings")
        except Exception:
            validation = {"valid": False, "errors": [str(exc)], "warnings": []}

    (out_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    (out_dir / "raw_output.txt").write_text(raw, encoding="utf-8")
    (out_dir / "clean_output.txt").write_text(cleaned + "\n", encoding="utf-8")
    if parsed is not None:
        (out_dir / "parsed_output.json").write_text(
            json.dumps(parsed, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    (out_dir / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report = [
        "# A8 Local Model Fallback Run",
        "",
        f"- Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"- Model: {args.model}",
        f"- Manifest: `{manifest_path}`",
        f"- Metadata: `{metadata_path}`",
        f"- CTA: {case_packet.get('cta_line')}",
        f"- Validator valid: {validation['valid']}",
        f"- Errors: {validation.get('errors', [])}",
        f"- Warnings: {validation.get('warnings', [])}",
        "",
        "## Local Model Output",
        "",
        "```json",
        json.dumps(parsed, ensure_ascii=False, indent=2) if parsed is not None else cleaned,
        "```",
    ]
    (out_dir / "run_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "model": args.model,
                "valid": validation["valid"],
                "errors": validation.get("errors", []),
                "warnings": validation.get("warnings", []),
                "parsed_output": str(out_dir / "parsed_output.json") if parsed is not None else None,
                "run_report": str(out_dir / "run_report.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
