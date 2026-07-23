# T-B1-INNERFLOWLAB-SECRETARY-001 — WordPress 個人秘書入口 v0

## 接續狀態

- **狀態**: COMPLETE（v0 live；持續自動同步另列後續）
- **負責**: A1 管理整合 + B1 Builder + B2/B3/B4 review
- **目標**: 把 MAPLAB 角色與 Investment OS 已驗證成果整理成 InnerFlowLab 的管理員專用只讀入口。
- **邊界**: 不下單、不建立模擬單、不公開 broker/持倉/secrets/raw logs、不提供任意 shell/command 執行。
- **完成證據**: exporter tests、外掛安裝與啟用、未登入導向 Google 登入、管理員登入可見角色/功能/警示、WordPress REST 更新需 `manage_options`。

## v0 變更

1. `wordpress/innerflowlab-personal-secretary/`：WordPress 外掛、登入門檻、私人頁面、只讀 dashboard、受權限保護的 snapshot endpoint。
2. `tools/innerflowlab_personal_secretary_snapshot.py`：在 Mac 蒐集非秘密健康資料，dry-run 預設，明確 `--push` 才送 WordPress。
3. `tests/test_innerflowlab_personal_secretary_snapshot.py`：launchctl 語意、merge conflict、secret 不外洩與 schema 測試。

## Success definition

- WordPress 只保存去識別化摘要。
- 管理員以既有 Google Apps Login 登入。
- 登出狀態看不到資料。
- 角色燈號分清「召喚模組存在」與「常駐 runtime 正在跑」。
- IOS 功能分清 PID、最近退出碼、檔案 freshness 與 owner-facing 讀回。
- 任何錯誤不得因為 launchd exit 0 就自動判綠。

## 2026-07-23 完成紀錄

- Live URL：`https://innerflowlab.com/personal-secretary/`
- 已登入管理員：可見 31 個角色、16 個功能、來源雜湊過期與 runtime 警示。
- 角色狀態已拆層：`1 running / 29 standby / 1 warning`；source hash 過期只列為上下文維護警示，不再冒充 runtime 故障。
- IOS 功能狀態：`3 running / 4 ready / 4 standby / 5 warning`。
- IOS-ALPHA 已列入私人入口；程式與排程可用，但 `convergence_phone.md` 為 `36d stale`，因此資料層維持 warning，不把舊訊號當目前結果。
- 未登入：HTTP 302 至 WordPress / Google Apps Login；看不到私人快照。
- 私人頁：`Cache-Control: private, no-store`、`X-Robots-Tag: noindex, nofollow, noarchive`。
- REST：匿名讀取 `/wp-json/innerflowlab-secretary/v1/snapshot` 回 HTTP 401。
- Chrome 檔案上傳權限未開，live 端改用 Code Snippets 啟用同一份 PHP；正式外掛 zip 已保存在 `dist/`。
- 本輪是去敏的一次性快照。持續同步要另設 WordPress Application Password 與低頻排程，不得把憑證寫入 repo。

## Resume Prompt

我是接手 InnerFlowLab Personal Secretary v0.1 後續同步的 B1/Codex。先讀
`CURRENT_STATUS.md`、`pitfalls.md` 與本 Task Card。外掛在
`wordpress/innerflowlab-personal-secretary/`，exporter 在
`tools/innerflowlab_personal_secretary_snapshot.py`，live URL 是
`https://innerflowlab.com/personal-secretary/`。v0 已完成登入/登出 eye proof。
下一步先收斂 MAPLAB `CURRENT_STATUS.md` merge conflict 並重建 task modules，
再更新 IOS-ALPHA 跨源資料並補齊 shadow training artifact；之後以環境變數設定
WordPress Application Password，為 exporter 建立低頻排程。
不可把 `.env`、broker state、持倉明細、raw logs 或任意命令送到 WordPress；
每次同步後重驗匿名 302、REST 401 與管理員畫面。
