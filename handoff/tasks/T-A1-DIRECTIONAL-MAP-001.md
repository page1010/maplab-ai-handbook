# Task Card: T-A1-DIRECTIONAL-MAP-001 — MAPLAB 指向性治理地圖

- **狀態**: 🟠 OWNER_RELOAD（實作與靜態／本機 UI 驗收完成）
- **Owner**: A1 / Codex
- **建立**: 2026-08-25
- **範圍**: MAPLAB 非投資域；A0–A8、Mac mini／Windows、共治代理、A2–A8 工作流、產物互用、Sheets／索引、治理／記憶／receipt、NotebookLM safe pack

## Owner 原始需求

「看一下關聯圖，不要只畫 A2 A8，把可以畫的都畫完；確認現有角色定位與系統全貌。投資系統的關聯先不用，但地端模型、Windows + Mac mini、共治方案、A2–A8 任務流程、產出物互用、已建立的 Sheet 資料庫索引優先。」

後續核准：「對我們系統有幫助嗎？有的話跑起來吧；另外把整個專案塞給 NotebookLM 是否有幫助？」

## 成功標準

1. 單一 canonical manifest，而非多份人工地圖。
2. 七個視角：系統、Repo、角色、A2–A8 工作流、產物、能力／硬體、治理／證據。
3. 每個 workflow stage 有輸入、執行、輸出、驗收、交接、工具、gate、evidence。
4. 同一 manifest 產 docs map、Extension offline map、graph JSON 與 NotebookLM safe pack。
5. Extension 角色召喚旁有可用地圖入口。
6. NotebookLM 不接受 wholesale repo dump；使用可重建、帶 hash、去敏的 source pack。
7. 通過 schema/path/sensitive scan/unit/UI/readback/git checks，留下 receipt 與 scoped commit。

## 交付狀態（2026-08-25）

- ✅ canonical manifest：`config/system-map/maplab-directional-map.json`
- ✅ 7 視角 HTML：`docs/system-map/index.html`
- ✅ Extension offline copy 與「系統地圖」按鈕
- ✅ canonical Graphify-compatible governance graph：263 nodes／302 edges
- ✅ Graphify 0.9.49 AST code graph：1817 nodes／3252 edges／148 communities，含 interactive graph、tree、report 與 query memory
- ✅ A2–A8：7 workflows／28 stages，含交接合約與產物血緣
- ✅ NotebookLM safe pack：8 份去敏內部來源，帶 SHA-256 與排除規則
- ✅ unit、schema、path、sensitive scan、desktop／mobile UI readback、console scan、`git diff --check`
- ⚠️ 未能自動開啟 `chrome://extensions`：Chrome 安全邊界明確拒絕。Owner 手動按一次「重新載入」後，再做 live Extension UI readback 即可收尾。

驗收收據：`workbook/reviews/JOB-A1-DIRECTIONAL-MAP-20260825/validation_receipt.md`

## 邊界

- 不展開 Investment OS 角色、研究、部位、資料庫或 runtime。
- Graphify 已全域安裝；repo 只用 AST-only 程式圖，不開付費 LLM 語意抽取，不索引投資域、secrets、runtime logs 或客戶 raw data。
- 不發布、不傳送、不上傳 NotebookLM、不改外部平台。
- 不碰本任務以外既有 dirty files。

## Resume Prompt

我是 A1 指向性治理地圖接手者。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`config/system-map/maplab-directional-map.json`、`.graphifyignore` 與 `tools/ai_workbook/build_directional_system_map.py`。重新執行 generator／unittest／`--check`；若有 code-like 變更再跑 `graphify update .`，確認 topology 不會由 2k 節點漂到全文件圖。確認 docs／Extension map、Graphify graph／Tree／Report、NotebookLM source pack 和 Extension 入口一致。完成前讀 `workbook/reviews/JOB-A1-DIRECTIONAL-MAP-20260825/validation_receipt.md`，只 stage 本任務明列檔案。
