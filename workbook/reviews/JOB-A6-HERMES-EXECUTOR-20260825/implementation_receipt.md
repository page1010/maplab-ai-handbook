# A6 Hermes 治理式執行能力實作收據

## VERIFIED

- gateway 已接入 file-backed executor。
- accepted/rejected request 均建立 task 與 receipt。
- worker 使用固定 argv allowlist，沒有 `shell=True` 或 Telegram 任意命令插值。
- focused tests `4/4 PASS`；語法與 diff whitespace 檢查通過。
- 本機實際執行 `repo-status` 成功，task id `A6H-20260825-204904-bcf1c5`。

## DRIFT

- 舊 Hermes 對話宣稱完全沒有本機執行能力；新版啟用後應由 `/start` 說明三項有界能力。
- 尚未在本工作 session 取得 Telegram Web 新版 roundtrip，因此不標 LIVE_VERIFIED。

## DISPATCH

- Owner 可用 `/do repo-status`、`/do recent-commits`、`/do a6-self-test`。
- 中文可用 `執行：最近提交` 或 `動手：測試 A6`。

## NEXT

- 重載 `com.maplab.a6bot` 後以 Telegram Web 發 `/do recent-commits`；比對回覆 task id 與本機 receipt。
