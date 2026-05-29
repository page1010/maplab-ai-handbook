# Review Request — B1-B4 Investment OS Roles + A2 Patrol Extension Wiring

日期：2026-05-29
負責：A1 / Codex
狀態：ready for Owner/A1 review

## Summary

本次把原 B1 投資邏輯橋接任務拆成固定 B1-B4 role family，並讓 Chrome Extension 可透過 dynamic role modules 召喚：

- B1 Investment OS Builder：寫功能。
- B2 Investment OS Reviewer：檢查資料流與錯誤。
- B3 Investment OS Archivist：寫版本紀錄與交接紀錄。
- B4 Investment OS System Patrol：定期問「這套東西還適合嗎？」

同時新增 A2 Ads / SEO / WordPress Patrol，召喚後先確認品牌價值、品牌語氣、品牌顏色/視覺來源、live web 狀態，以及 MAPLAB + Investment OS 共用的證據分層與風險邊界。

## Key Outputs

- `projects/invest-os-b-role-system.md`
- `projects/b1-invest-os-builder.md`
- `projects/b2-invest-os-reviewer.md`
- `projects/b3-invest-os-archivist.md`
- `projects/b4-invest-os-system-patrol.md`
- `skills/invest-os-b-role-system.md`
- `recalls/B1_recall.md` to `recalls/B4_recall.md`
- `projects/a2-ads-seo-wordpress-patrol.md`
- `handoff/tasks/T-B1-B4-investment-os-role-split.md`
- `handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`
- `chrome-extension/task-modules/B1.json` to `B4.json`
- `chrome-extension/task-modules/A2.json`
- `chrome-extension/task-modules/index.json`

## Chrome Extension Change

`chrome-extension/popup.js` now populates the role selector from `chrome-extension/task-modules/index.json`, grouped into MAPLAB A roles and Investment OS / Cross-Project B roles. This prevents future module additions from being hidden by stale hardcoded dropdown options.

## Automation

Created Codex automation:

- id: `a2-ads-seo-wordpress-patrol`
- kind: cron
- status: ACTIVE
- schedule: `FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0;BYSECOND=0`
- cwd: `/Users/pagemacmini/maplab-ai-handbook`

## High-Risk Actions Not Performed

- No WordPress publish.
- No Google Ads / Meta Ads settings changed.
- No Rank Math paid/settings state changed.
- No secrets / `.env` / API keys / cookies read.
- No Investment OS order, simulation ledger, broker, or trading action.

## Review Focus

1. Confirm B1-B4 naming and boundaries match Owner intent.
2. Confirm A2 patrol startup memory is strict enough for brand voice and live web checks.
3. Confirm weekly Monday 09:00 is acceptable for the A2 patrol cadence.
4. Confirm whether B4 should also get a separate Codex automation later.
