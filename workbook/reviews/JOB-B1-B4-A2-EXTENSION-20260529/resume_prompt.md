# Resume Prompt

我是 A1/Codex，接手 B1-B4 Investment OS role split + A2 Ads/SEO/WordPress patrol extension wiring。

先讀：

1. `CURRENT_STATUS.md`
2. `pitfalls.md`
3. `handoff/tasks/T-B1-B4-investment-os-role-split.md`
4. `handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`
5. `projects/invest-os-b-role-system.md`
6. `projects/a2-ads-seo-wordpress-patrol.md`
7. `workbook/reviews/JOB-B1-B4-A2-EXTENSION-20260529/review_request.md`
8. `workbook/reviews/JOB-B1-B4-A2-EXTENSION-20260529/validation_record.md`

目前狀態：

- B1-B4 docs / recalls / module generator 已建立。
- Chrome Extension role selector 已改為從 module index 動態產生。
- Chrome Extension v5.6.0 已新增 `召喚任務` 欄位與 `自動選角`，handoff prompt 會帶入 `本次召喚任務`。
- task modules 與 role recall fallback 先讀 local packaged extension data，GitHub raw 只作 fallback。
- Chrome live profile 已啟用 MAPLAB Agent Commander v5.6.0（id `ifpmihhbfhpbcippnhdnjdecbgkmbgmf`）；舊 v4.7.0 entry 保留但關閉。
- `/Users/pagemacmini/Desktop/chrome-extension` 現在是 symlink，指向 `/Users/pagemacmini/maplab-ai-handbook/chrome-extension`；舊 Desktop folder 備份為 `/Users/pagemacmini/Desktop/chrome-extension.stale-v4.7-20260529-212125`。
- `python3 tools/ai_workbook/build_extension_task_modules.py` 已重建 13 modules。
- A2 weekly automation `a2-ads-seo-wordpress-patrol` 已 ACTIVE。
- 外部發布、Ads 設定、投資/交易動作都沒有執行。

下一步：

1. 若 Owner 要巡查 Investment OS，從 Chrome Extension 的 `召喚任務` 欄位輸入任務，按 `自動選角`，再複製 handoff。
2. 若 Owner 要 A2 跑品牌/SEO/WP 巡查，輸入任務並讓 Extension 切 A2，或等待週一 09:00 automation。
3. 若要清理 Chrome Extensions 頁，舊 v4.7.0 entry 可由 Owner/A1 另案確認後移除；本次未移除，避免破壞性操作。
