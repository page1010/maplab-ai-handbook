# Google Sheets Tracking Guide

Version: 1.0
Created: 2026-03-17
Purpose: Unified progress tracking via Google Sheets (replaces Notion DB for pipeline logging)

## Why Sheets Instead of Notion

- Unified interface: all MAPLAB agents use Google Workspace
- Shared access: anyone with the Sheet link can view progress
- API simplicity: Sheets API is simpler than Notion API
- Cost: free with existing Google Workspace
- Real-time: changes visible instantly
- Integration: works natively with Colab (same Google auth)

## ASSET_LOG Schema (15 columns)

| Col | Field | Type | Description |
|-----|-------|------|-------------|
| A | file_id | UUID | Unique identifier |
| B | original_name | text | Original filename |
| C | seo_name | text | SEO-optimized name |
| D | category | enum | food/store/event/landscape/screenshot/other |
| E | keywords | text | Comma-separated keywords |
| F | alt_text | text | Image alt text for web |
| G | drive_url | URL | Google Drive link |
| H | source_folder | text | Original Takeout folder |
| I | year | number | Photo year |
| J | file_type | text | jpg/heic/png/mp4 |
| K | is_screenshot | bool | TRUE/FALSE |
| L | status | enum | pending/processing/done/error |
| M | processed_at | ISO date | Processing timestamp |
| N | gemini_tokens_used | number | API usage tracking |
| O | error_message | text | Error details if failed |

## Setup Checklist

1. Create Google Sheet named "MAPLAB_ASSET_LOG"
2. Share with service account or authenticated user
3. Copy spreadsheet ID from URL
4. Set spreadsheet_id in pipeline config
5. Run sheets_logger.ensure_header() to create columns

## Progress Monitoring

Link this Sheet in the team dashboard or skill reference.
Use get_progress() method to get summary:

```python
logger = SheetsLogger(spreadsheet_id, creds)
progress = logger.get_progress()
# Returns: {total: 122200, done: 50000, error: 12, progress_pct: 40.9}
```

## Best Practices

- Always use batch_log() for bulk operations (not single log_asset)
- Flush buffer before Colab disconnect
- Check progress before resuming after reconnect
- Use status column to find where to resume
- Filter by error status to find and retry failures