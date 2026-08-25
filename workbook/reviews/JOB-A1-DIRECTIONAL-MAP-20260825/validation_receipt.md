# JOB-A1-DIRECTIONAL-MAP-20260825 驗收收據

- 執行角色：A1 / Codex
- 執行環境：Mac mini / `/Users/pagemacmini/maplab-ai-handbook`
- 時間：2026-08-25 21:24 +0800
- 範圍：MAPLAB 非投資域
- 基底 commit：`4fa25ea3eb41`
- 任務狀態：實作完成；Chrome 已安裝擴充套件的 live reload/readback 待 Owner 手動一次

## VERIFIED

1. 單一真相源
   - `config/system-map/maplab-directional-map.json`
   - JSON Schema：`config/system-map/maplab-directional-map.schema.json`
   - manifest SHA-256：`c5297ddaf7b90c75a3ede164264c286b8756b4f64989de51480f2b5d03179b03`

2. 地圖交付
   - 7 個視角：系統總覽、Repo 地址、角色共治、A2–A8 工作流、產物互用、能力／硬體、治理／證據。
   - 角色：Owner + A0–A8，共 10。
   - 工作流：A2–A8，共 7 workflows／28 stages。
   - Canonical governance Graph JSON：263 nodes／302 edges。
   - docs map 與 Extension offline map 內容 byte-identical。

3. 資料庫／索引優先
   - 主 Sheet Dashboard、Asset Log、Ads Dashboard、A2 patrol evidence、本機素材索引、task indexes 已進 manifest。
   - 每個 workflow stage 明列 input／actions／outputs／acceptance／tools／approval gate／handoff／evidence。

4. NotebookLM safe pack
   - 上傳候選只有 `maplab-project-brain.md` 與 `source-manifest.json`。
   - 共 8 個允許來源，每個來源有 SHA-256、bytes、classification、redaction count。
   - 明確排除 `.env`、token、secret、credentials、cookie、session、broker、position、ledger、customer raw、runtime log、sqlite、private key 與 Investment OS。
   - `not_live_truth=true`：NotebookLM 只是查詢／綜合層，不取代 CURRENT_STATUS、Task Card、Git commit 或 receipt。

## 機器驗收

```text
python3 -m unittest tools.ai_workbook.test_build_directional_system_map -v
→ 6 tests / OK

python3 tools/ai_workbook/build_directional_system_map.py
→ ok=true / nodes=263 / edges=302 / sources=8

python3 tools/ai_workbook/build_directional_system_map.py --check
→ ok=true / generated_outputs=fresh / errors=[]

python3 -c <Draft202012Validator schema check>
→ schema validation PASS

node --check chrome-extension/popup.js
→ PASS

python3 -m json.tool chrome-extension/manifest.json
python3 -m json.tool config/system-map/maplab-directional-map.json
python3 -m json.tool config/system-map/maplab-directional-map.schema.json
→ PASS

cmp docs/system-map/index.html chrome-extension/system-map/index.html
→ PASS

rg <sensitive-patterns> workbook/notebooklm/... docs/system-map chrome-extension/system-map
→ 0 matches

git diff --check
→ PASS
```

## UI 讀回

- 本機 URL：`http://127.0.0.1:8766/docs/system-map/`
- Desktop：7 個 tab 皆能點選並顯示對應視圖。
- Workflow：點選 A8 後讀回「影音案例生產工作流」與 4 stages。
- Mobile 360×800：`clientWidth=345`、`scrollWidth=345`，無 body 橫向溢出。
- Browser console warnings/errors：0。
- Extension popup static readback：v5.7.0 與「🗺 指向性地圖｜角色・流程・產物・資料」按鈕可見，位於角色召喚區。

## DRIFT / 誠實邊界

- Chrome browser security policy 拒絕 agent 開啟 `chrome://extensions/`。沒有蹲過政策，也沒有宣稱已 reload 或已完成已安裝 extension 的 live readback。
- Windows 目前在 manifest 為 `declared`，未伯造 runtime 實測。
- Graphify 已全域安裝，但仍不取代 canonical manifest 或 live evidence；AST-only 圖無法單獨證明 Chrome runtime URL 會開啟哪份 generated HTML。
- NotebookLM 來源包未上傳 Google；本輪只生成可審查、可重建的安全包。

## Graphify 0.9.49 實際上線驗收（2026-08-25 21:43 +0800）

- 執行檔：`/Users/pagemacmini/.local/bin/graphify`；版本：`0.9.49`。
- 全域 Codex 規則：`/Users/pagemacmini/AGENTS.md`；全域 PreToolUse hook：`/Users/pagemacmini/.codex/hooks.json`。
- CLI `graphify hook status` 顯示 git post-commit/post-checkout hook 未安裝；本輪不额外改 repo git hook。
- 原始 corpus 盤點：631 supported files／445,560 words，含 221 code／410 docs，超過 500-file 警戒線。
- 最終邊界：`.graphifyignore` 排除 docs／history／generated copies／secrets／runtime／customer raw／Investment OS，使首建與 `graphify update .` 都維持同一 AST-only corpus。
- 最終 graph：1817 nodes／3252 edges／148 communities，0 LLM input/output tokens。
- 交付：`graphify-out/graph.html`、`GRAPH_TREE.html`、`GRAPH_REPORT.md`、`graph.json`、`manifest.json`、`memory/`、`reflections/LESSONS.md`。
- 完整性診斷：0 missing endpoints／0 dangling endpoints／0 self-loops／0 collapsed edges／0 duplicates。
- 抽取警告：`AppKit` 與 `Foundation` 分別在兩個 Swift 檔案產生同 id，Graphify 各去重一個；圖可用，但這兩個 framework 節點不能當完整檔案雙向證據。
- 查詢驗收：`explain build_notebooklm_pack` 讀回 redaction／hash／write_outputs 關係；`path build_notebooklm_pack check_generated_outputs --undirected` 讀回 2 hops；`explain openDirectionalSystemMap` 只有 popup.js containment，已存為 dead-end lesson。
- Investment 邊界複驗：共用 `bot/bot.py` 仍會帶出 4 個 investment discussion 節點；因 Graphify 只能以檔案排除，本版將整個混合 dispatcher 移出 corpus，角色／Telegram 路由改由 canonical manifest 保留。最終圖不含 investment／stock 專項節點；`reaction_ledger`、slide 文案 `PORTFOLIO` 與 schema `position_hint` 是非投資同名詞，保留。
- Token benchmark：121,133 naive tokens 對平均 3,404 query tokens，約 `35.6x` 縮減。
- Drift 修復：第一次 incremental update 因把 Markdown 當 code-like 節點，圖膨脹為 7,332 nodes；補 `.graphifyignore` 後 force rebuild，再排除混合 investment dispatcher 與記錄 Graphify 統計的 canonical manifest/schema，避免 self-reference，最終穩定為 1,817 nodes；第二次 update 顯示 `No code-graph topology changes detected`。
- In-app Browser 實際讀回：`graph.html` 顯示 1,817 nodes／3,252 edges／148 communities，搜尋 `build_directional_system_map` 可回傳 generator 與 test 節點；網路圖可視、community filter 可見。`GRAPH_TREE.html` 顯示專案標題與 Expand All／Collapse All／Reset View，console error 為 0。
- `vis-network` 留下一則 info 級 layout 建議，但實際圖已正常定位並可操作；不把它誤記成零訊息，也不視為功能失敗。

## NEXT

Owner 在 Chrome 開啟 `chrome://extensions` → MAPLAB Agent Commander → 點「重新載入」一次。之後點擴充套件內「系統地圖」，應開啟 7 視角 offline map。

## Resume Prompt

我是 A1 指向性治理地圖接手者。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A1-DIRECTIONAL-MAP-001.md` 與本 receipt。重跑 generator／unittest／`--check`，不直接手改 generated HTML。若 Owner 已 reload Extension，做 popup／side panel live readback；成功後將 Task Card 由 OWNER_RELOAD 改為 DONE。NotebookLM 若要上傳，只傳 `workbook/notebooklm/maplab-project-brain/` 明列的兩個 upload files，不傳整個 repo。
