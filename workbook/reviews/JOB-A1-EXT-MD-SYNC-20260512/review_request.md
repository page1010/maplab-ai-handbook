# Review Request

status: waiting_for_owner_review

## What Changed

側邊欄現在不是只相信舊 role JSON。每個 role module 會記錄必讀 Markdown / JSON source 的 SHA-256，Chrome side panel 可按「檢查 MD 同步」比對 GitHub raw 最新內容。

## Evidence

- Chrome extension details page showed version `5.5.2`.
- A2 module showed `2026-05-12T07:21:23+08:00`.
- Sync check result: `Markdown 已同步｜27/27 sources match module hashes`.
- Screenshot: `screenshots/chrome_extension_md_sync_27_of_27.png`

## Owner Decision

- 可繼續沿用這個 side panel 作 Gemini / Codex / OpenClaw 的角色召喚入口。
- 若日後修改 source Markdown 後側邊欄顯示 stale，請讓 A1/Codex 跑 `python3 tools/ai_workbook/build_extension_task_modules.py` 並重新 reload extension。

