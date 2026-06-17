# A8 Superseded Local Runs

Date: 2026-06-17

Canonical usable output:

- `local_model_video_v5/a8-short-local-model-video.mp4`
- `local_model_video_v5/a8-short-local-model-cover.jpg`
- `local_model_video_v5/pipeline_report.md`

Superseded local-only runs:

- `local_model_fallback_v2/` through `local_model_fallback_v5/`
- `local_model_video_v1/` through `local_model_video_v4/`

Disposition:

- Keep local files temporarily as failure evidence.
- Do not commit these directories.
- Use `local_model_video_v5/` as the current verified A8 local fallback artifact.

Reason:

The earlier fallback runs either produced JSON/storyboard only, failed the visual/copy standard, or were replaced by the verified MP4 pipeline. The committed v5 output has the required rendered MP4, cover, QA frames, and report.
