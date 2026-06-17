# Local Model Fallback Smoke

Date: 2026-06-17
Purpose: answer whether A8 folder-to-video workflow can use local models as backup.

## Availability

`ollama list` returned:

| Model | Use |
|---|---|
| `qwen2.5:14b` | Best local fallback for Chinese storyboard / platform copy / risk checklist |
| `gemma4:latest` | Secondary review / checklist |
| `qwen2.5-coder:7b` | Script / JSON / schema helper, not brand copy lead |

## Smoke Prompt

Asked `qwen2.5:14b` to produce JSON fields:

- `fallback_verdict`
- `storyboard`
- `platform_copy`
- `risks`
- `needs_cloud_tool`

Input described the ICC Tainan dry-run case, brand voice, and restrictions.

## Result

Verdict: usable as L1 fallback only when paired with deterministic local tooling.

Important correction:

- JSON-only output is not a complete A8 video fallback.
- Complete A8 local fallback means: local model JSON valid → local renderer produces MP4 → ffprobe validates 1080x1920 H.264 → QA frames checked.

What worked:

- Produced a storyboard structure.
- Produced platform copy ideas.
- Included privacy / copyright risk items.
- Understood this was a draft workflow, not a direct upload.

What failed or needs guardrails:

- CLI output included terminal control codes, so raw output is not directly usable as JSON.
- The model inferred visual details not guaranteed by the manifest, such as coffee / steam. This is unacceptable for final public copy unless verified by image QA.
- It returned `needs_cloud_tool=false`, but the actual production workflow still needs Google Vids / Canva / CapCut or similar for final subtitle / cover assembly.
- It reused off-brand/internal phrases such as `取餐要順`, `分開`, and `動線穩` until the prompt seed and validator were tightened.

## Runner Integration

Added:

- `tools/ai_workbook/a8_local_model_fallback.py`

Command used for the accepted run:

```bash
python3 tools/ai_workbook/a8_local_model_fallback.py \
  --manifest workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_manifest.json \
  --metadata workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_platform_metadata.json \
  --motion-spec workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6 \
  --model qwen2.5:14b \
  --timeout 240
```

Accepted output:

- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6/parsed_output.json`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6/validation.json`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6/run_report.md`

Validator result:

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

Training sequence:

| Run | Result | Lesson |
|---|---|---|
| v2 | invalid | JSON-like output contained invalid strings. |
| v3 | invalid | Schema shape drifted into nested / wrong fields. |
| v4 | invalid | Unsupported visual claim appeared. |
| v5 | invalid | Platform copy did not fully satisfy CTA / non-empty copy rule. |
| v6 | valid | Short prompt contract + JSON mode + stricter validator produced usable draft. |

## End-to-End Local Video Integration

Added:

- `tools/ai_workbook/a8_local_model_video_pipeline.py`

Accepted command:

```bash
python3 tools/ai_workbook/a8_local_model_video_pipeline.py \
  --manifest workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_manifest.json \
  --metadata workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_platform_metadata.json \
  --motion-spec workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5 \
  --model qwen2.5:14b \
  --timeout 300
```

Accepted output:

- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/a8-short-local-model-video.mp4`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/a8-short-local-model-cover.jpg`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/pipeline_report.md`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/local_model/validation.json`

Accepted scene lines:

1. 茶點動線清楚
2. 交流節奏不被打斷
3. 飲品甜點分區
4. 桌面留白乾淨
5. 台南企業茶會

Video validation:

```json
{
  "codec_name": "h264",
  "width": 1080,
  "height": 1920,
  "r_frame_rate": "30/1",
  "duration": "13.200000"
}
```

Video training sequence:

| Run | Result | Lesson |
|---|---|---|
| v1 | rendered MP4 | MP4 alone is insufficient if copy sounds like internal ops. |
| v2 | blocked | Missing platform titles must block rendering. |
| v3 | blocked | `分開` still leaked through visual instructions. |
| v4 | blocked | Input seed contained `動線穩`; bad seed copy must be brand-cleaned before model use. |
| v5 | passed | Brand-cleaned seed + stricter validator + local renderer produced complete MP4. |

## Hermes / OpenClaw Route Check

2026-06-17 check:

- Hermes CLI exists, but gateway is stopped, sessions are 0, messaging is not configured. Do not use Hermes as A8 hot-path renderer.
- OpenClaw gateway/browser is healthy; `openclaw browser doctor` passed and tabs are visible. Use OpenClaw for browser/operator readback.
- OpenClaw agent QA for A8 v5 returned `NO_REPLY`; do not rely on it for A8 video/copy QA until it returns useful structured output.

## Policy

Use local model for:

- draft storyboard
- platform metadata
- privacy / brand checklist
- approval card draft
- missing-field detection
- local MP4 proof only through `a8_local_model_video_pipeline.py`

Do not use local model for:

- final visual truth
- final upload decision
- publishing to external platforms
- sending private client material to third-party AI tools

Required validator:

1. Strip ANSI/control codes.
2. Validate JSON if JSON was requested.
3. Reject claims about visible objects unless sourced from manifest, image QA, or human/vision readback.
4. Keep output as draft until Owner/A1 approval.
