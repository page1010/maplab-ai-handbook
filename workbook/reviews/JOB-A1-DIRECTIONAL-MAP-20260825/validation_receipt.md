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
   - manifest SHA-256：`75a93d5bb747e9eb8e649876c1f1c48e9a233845fd3894429e2737391d1236ce`

2. 地圖交付
   - 7 個視角：系統總覽、Repo 地址、角色共治、A2–A8 工作流、產物互用、能力／硬體、治理／證據。
   - 角色：Owner + A0–A8，共 10。
   - 工作流：A2–A8，共 7 workflows／28 stages。
   - Graph JSON：262 nodes／302 edges。
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
→ ok=true / nodes=262 / edges=302 / sources=8

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
- Graphify 未安裝；先交付通用 nodes/edges JSON，避免將外部工具變成單點依賴。
- NotebookLM 來源包未上傳 Google；本輪只生成可審查、可重建的安全包。

## NEXT

Owner 在 Chrome 開啟 `chrome://extensions` → MAPLAB Agent Commander → 點「重新載入」一次。之後點擴充套件內「系統地圖」，應開啟 7 視角 offline map。

## Resume Prompt

我是 A1 指向性治理地圖接手者。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A1-DIRECTIONAL-MAP-001.md` 與本 receipt。重跑 generator／unittest／`--check`，不直接手改 generated HTML。若 Owner 已 reload Extension，做 popup／side panel live readback；成功後將 Task Card 由 OWNER_RELOAD 改為 DONE。NotebookLM 若要上傳，只傳 `workbook/notebooklm/maplab-project-brain/` 明列的兩個 upload files，不傳整個 repo。
