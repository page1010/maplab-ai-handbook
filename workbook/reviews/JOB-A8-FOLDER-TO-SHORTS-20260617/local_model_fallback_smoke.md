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

Verdict: usable as L1 fallback with validation.

What worked:

- Produced a storyboard structure.
- Produced platform copy ideas.
- Included privacy / copyright risk items.
- Understood this was a draft workflow, not a direct upload.

What failed or needs guardrails:

- CLI output included terminal control codes, so raw output is not directly usable as JSON.
- The model inferred visual details not guaranteed by the manifest, such as coffee / steam. This is unacceptable for final public copy unless verified by image QA.
- It returned `needs_cloud_tool=false`, but the actual production workflow still needs Google Vids / Canva / CapCut or similar for final subtitle / cover assembly.

## Policy

Use local model for:

- draft storyboard
- platform metadata
- privacy / brand checklist
- approval card draft
- missing-field detection

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
