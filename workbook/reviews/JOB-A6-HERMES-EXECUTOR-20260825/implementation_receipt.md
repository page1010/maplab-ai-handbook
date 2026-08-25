# A6 Hermes 治理式執行能力實作收據

## VERIFIED

- gateway 已接入 file-backed executor。
- accepted/rejected request 均建立 task 與 receipt。
- worker 使用固定 argv allowlist，沒有 `shell=True` 或 Telegram 任意命令插值。
- focused tests `4/4 PASS`；語法與 diff whitespace 檢查通過。
- 本機實際執行 `repo-status` 成功，task id `A6H-20260825-204904-bcf1c5`。

## DRIFT

- 舊 Hermes 對話宣稱完全沒有本機執行能力；新版啟用後應由 `/start` 說明三項有界能力。
- 2026-08-25 20:54 已取得 Telegram Web 新版 roundtrip，task id `A6H-20260825-205420-d79c9c` 與本機 receipt 一致；原 drift 已關閉。

## DISPATCH

- Owner 可用 `/do repo-status`、`/do recent-commits`、`/do a6-self-test`。
- 中文可用 `執行：最近提交` 或 `動手：測試 A6`。

## NEXT

- ROUNDTRIP_VERIFIED。後續新增能力時，維持固定 argv allowlist、focused tests 與 Telegram/receipt 同 id 驗證。
