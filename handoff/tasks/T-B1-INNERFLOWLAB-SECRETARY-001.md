# T-B1-INNERFLOWLAB-SECRETARY-001 — WordPress 個人秘書入口 v0

## 接續狀態

- **狀態**: COMPLETE（v0.7 live；18501 比較型資料中心已上線；hourly sync 待 Owner 一次性 Keychain 授權）
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

## 2026-07-23 v0.5 接續完成

- B5 已正式接入動態角色模組生成器；生成器目前 32 模組（31 portal 角色 + WIN），popup consistency PASS。
- 乾淨 truth source 下，31 portal 角色為 `1 running / 30 standby / 0 warning`，source-hash alert 已清除。
- IOS-ALPHA 前次 `36d stale` 是 exporter 讀到 repo 範例副本；真 runtime 手機卡、長報告、shadow training 與 local-model findings 均於 13:03 更新，runner SHA-256 與 repo 一致。
- IOS 功能目前 `3 running / 5 ready / 4 standby / 4 warning`；IOS-ALPHA 為 `READY / 0h`。
- Live WordPress 已同步 v0.5；登入後眼見 IOS-ALPHA READY，匿名頁仍 302，匿名 REST 仍 401。
- 已新增 Keychain-only hourly wrapper、LaunchAgent、fail-closed installer 與一次性 Owner 設定文件；未建立、讀取或保存 Application Password。

## 2026-07-23 v0.6 — 18501 成果中心

- 已實際讀取 `http://127.0.0.1:18501/`，確認它是完整 Investment OS Streamlit，涵蓋風控、總經、研究、交易、16 個 Strategy Guild 角色工作區與運維，不是單一 IOS-ALPHA 頁。
- WordPress 新增「18501 成果中心」，首屏直接顯示：現在可不可信、行情日、正式工作完成率、四條核心成果線、Broker 只讀 freshness 與自動下單開關。
- 目前 live 判讀：`14/18` 條正式工作完成、`4` 條未通過、`2/4` 條核心成果線有當日完成品；實單只讀快照需刷新，因此整體是「部分可用」，不是整套不能用。
- 18 條工作逐條顯示名稱、責任角色、最近結果與 freshness；`timeout-smoke` 測試工作不列入正式分母。
- 網站不接觸原始 SQLite、持倉、帳戶、股票清單、raw log、local URL 或任意命令。失敗原因只保留去敏判讀。
- Live WordPress：管理員登入可見 `18501 成果中心`、31 角色、16 功能；匿名頁 HTTP 302、匿名 REST HTTP 401。
- Code Snippets 更新時曾因 CodeMirror 未先清空全文而疊入新舊程式碼，安全機制自動停用 shortcode；已以 `Meta+A → Backspace → 一次 fill → save+activate` 修復並完成 UI readback。
- 新外掛包：`dist/innerflowlab-personal-secretary-0.2.0.zip`。Live 目前仍由等價的 Code Snippets 版本運作，正式 merge 後可改由外掛安裝取代。

## 2026-07-23 v0.7 — MacroMicro 式比較型資料中心

- 已用登入中的實頁比對本機 18501、InnerFlowLab 私人入口與 MacroMicro 國家數據中心；採用「全寬主題頁首 → sticky 分類導覽 → 同尺寸指標卡 → 分類細節」的判讀結構，未複製品牌素材。
- 首屏刪除 WordPress 頁名與多餘留白，改為 `Investment OS 資料中心`、更新時間、31 角色、18 正式工作、4 項需處理與只讀安全標示。
- Exporter 新增公開市場指標 allowlist：10Y、DXY、USD/TWD、Gold、Oil、Copper、Nasdaq、SOX；不接受個股、帳戶值或任意原始欄位。
- 18 條正式工作分為總經風控、阿爾法雷達、研究證據、交易劇本、系統運維五區，支援關鍵字搜尋與正常/警告/失敗篩選；live eye proof 的警告篩選恰顯示 4 條。
- 31 個角色與 16 個功能保留完整成果，但預設收進兩個可展開檔案庫，避免長列表遮蔽真正判讀。
- Live 快照時間 `2026-07-23T14:28:36+08:00`；行情日 2026-07-22、14/18 工作完成、2/4 核心成果線有當日產物、Broker 只讀快照 8 天需刷新、IOS-ALPHA 0h ready。
- 管理員 live render 已驗證；匿名頁 302、匿名 REST 401。測試 7/7 通過，`git diff --check` 通過。
- 外掛版本 0.3.0；安裝包 `dist/innerflowlab-personal-secretary-0.3.0.zip`；review bundle：`workbook/reviews/JOB-B1-INNERFLOWLAB-SECRETARY-20260723/`。

## Resume Prompt

我是接手 InnerFlowLab Personal Secretary v0.7 後續同步的 B1/Codex。先讀
`CURRENT_STATUS.md`、`pitfalls.md` 與本 Task Card。外掛在
`wordpress/innerflowlab-personal-secretary/`，exporter 在
`tools/innerflowlab_personal_secretary_snapshot.py`，live URL 是
`https://innerflowlab.com/personal-secretary/`。v0.7 已完成 18501 比較型資料中心、
8 個公開市場指標卡、五類工作分組、搜尋/狀態篩選與角色/功能收合；目前 live
判讀是 14/18 工作完成、4 條未通過、2/4 核心成果線有產物，不能把 warning
解讀成整套不能用。live 仍由 Code Snippets id=6 運作；修改 CodeMirror 必須
`Meta+A → Backspace → fill → save`，並確認片段仍為 active。
下一步由 Owner 依 `docs/innerflowlab-personal-secretary-sync.md` 建立 WordPress
Application Password，直接存入 macOS Keychain，不貼到聊天或 repo。分支 merge
到 canonical checkout 後，執行 `tools/innerflowlab_personal_secretary_sync.sh` 與
`tools/install_innerflowlab_personal_secretary_sync.sh`，再驗 launchctl、登入後時間戳、
匿名 302 與 REST 401。四個 warning 工作是實單快照、實單研究、watchdog、
強勢股故事驗證；另建 B1/B2 修復任務，不阻塞入口與其他 14 條成果。
不可把 `.env`、broker state、持倉明細、raw logs 或任意命令送到 WordPress；
每次同步後重驗匿名 302、REST 401 與管理員畫面。
