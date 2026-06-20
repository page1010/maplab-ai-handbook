# A8 Local Model End-to-End Video Run

- Run time: 2026-06-20T20:55:22
- Model: qwen2.5:14b
- Local model host: Ollama CLI on this Mac
- MCP: none attached to the local model in this runner
- Tool layer: Python runner -> Swift/AppKit frame renderer -> ffmpeg/ffprobe
- Fallback JSON: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/local_model/parsed_output.json`
- Render manifest: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/review_draft_manifest.json`
- Final video: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-video.mp4`
- Final cover: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/a8-short-local-model-cover.jpg`

## Scene Lines From Local Model
1. 茶點動線清楚
2. 交流節奏不被打斷
3. 飲品甜點分區
4. 桌面留白乾淨
5. 台南企業茶會

## Video Probe

```json
{
  "programs": [],
  "stream_groups": [],
  "streams": [
    {
      "codec_name": "h264",
      "width": 1080,
      "height": 1920,
      "r_frame_rate": "30/1",
      "duration": "13.166667"
    }
  ],
  "format": {
    "duration": "13.166667"
  }
}
```

## QA Frames
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/qa_frames/qa-intro.jpg`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/qa_frames/qa-middle.jpg`
- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/qa_frames/qa-outro.jpg`

## Platform Copy

```json
{
  "youtube_title": "大臺南會展中心企業會議茶點 | 台南企業外燴茶點 #Shorts",
  "youtube_description": "大臺南會展中心企業會議茶點紀錄。以好拿取、畫面乾淨、休息時間不打斷交流為主。\n\n台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab",
  "tiktok_caption": "大臺南會展中心企業會議茶點。會議休息時間的茶點配置，重點是好拿取、桌面留白乾淨。台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab",
  "pinterest_title": "大臺南會展中心企業會議茶點｜台南企業外燴茶點",
  "hashtags": [
    "#台南外燴",
    "#企業外燴",
    "#會議茶點",
    "#MAPLAB",
    "#Shorts"
  ]
}
```

## Render Summary

```json
{
  "asset_dir": "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001",
  "out_dir": "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video",
  "case_label": "大臺南會展中心企業會議茶點",
  "category": "corporate_tea",
  "cta_line": "台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab",
  "title": "台南企業茶點配置",
  "images": [
    "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-business-meeting-catering-14.webp",
    "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-catering-closeup-07.webp",
    "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-catering-table-overview-01.webp",
    "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-catering-table-overview-02.webp",
    "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001/maplab-icc-tainan-corporate-catering-display-11.webp"
  ],
  "scene_lines": [
    "茶點動線清楚",
    "交流節奏不被打斷",
    "飲品甜點分區",
    "桌面留白乾淨",
    "台南企業茶會"
  ],
  "scene_motions": [
    "pan_right",
    "dolly_in",
    "static",
    "dolly_out",
    "pan_left"
  ],
  "frame_modes": [
    "intro",
    "scene",
    "scene",
    "scene",
    "scene",
    "scene",
    "outro"
  ],
  "video": "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/a8-short-review-draft.mp4",
  "cover": "/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v6/rendered_video/a8-short-review-cover.jpg",
  "watermark": "MAPLAB Kitchen",
  "subtitle_overlay": "swift_appkit_rendered",
  "visual_template": "MAPLAB IG Soft v1",
  "visual_preset": "maplab_ig_soft",
  "counter": "hidden",
  "transition": "xfade",
  "transition_effect": "fade",
  "transition_seconds": 0.35,
  "audio": "none_local_draft_add_platform_licensed_music_before_publish",
  "status": "review_draft_rendered"
}
```
