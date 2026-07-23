# Runtime Capability Check — JOB-LOCAL-MODEL-EVOLUTION-20260719

見 `local_model_evolution/reports/latest.md` §Runtime Capability Report 為完整版本
（本檔不重複維護，避免平行真相源）。

## 摘要

執行環境 = A1 remote cloud 沙盒，非 Mac mini。已確認缺席：`ollama`、`codex`、
`agy`、`gemini`、`hermes`、`sqlite3`、`launchctl`／`crontab`。已確認存在：
`python3`（含 pyyaml）、`claude` CLI（Claude Code 本身）。Investment OS repo
已 shallow clone 至 `/workspace/investment-os` 供本輪讀取（未寫入該 repo）。

## 為何這樣記錄不算做白工

雖然不能對真實地端模型跑 baseline，這次盤點本身是可重用資產：下一輪
（無論在此沙盒或 Mac mini）都不用重跑 `command -v` 逐項確認，直接讀本檔
與 `local_model_evolution/state/STATE.md` 就知道哪些能力需要在 Mac mini
上重新驗證。
