# JOB-A1-EXT-MD-SYNC-20260512

## Owner Request

「她本來有設定動態連結你改動 md 他應該會跟上吧，協助改一下」

## A1 Interpretation

Chrome side panel 的角色召喚模組不能只顯示舊 JSON。Markdown / JSON source 改動後，側邊欄需要能判斷 role module 是否過期，handoff prompt 也要要求 Gemini / Codex / OpenClaw 讀最新 GitHub raw source。

## Scope

- 修正 role module generator，把 source hash 寫進 role module。
- 修正 Chrome extension，顯示 module source freshness 並可執行 Markdown 同步檢查。
- 修正 GitHub fetch cache，避免側邊欄拿到舊 module。
- 用 Chrome / Computer Use 實際驗證 v5.5.2 與 A2 模組同步結果。

