# Skill:NotebookLM 專案大腦(專案管理/把專案狀態餵給他)

- 建立:2026-08-25|作者:A0/Fable5|狀態:**可用(方法已驗證)**|Owner 指示:msg 3992
- 用途:把專案狀態文件(CURRENT_STATUS、handoff、派工卡)餵進 NotebookLM 建成可問答的專案知識庫;也用於 KOL 逐字稿研究。

## 已驗證的操作方法(2026-06-05 三集 KOL 實測 PASS)

1. 前提:機器上有已登入 Google 的 Chrome(A6 慣例);agent 用 Chrome MCP 工具(list_connected_browsers → select_browser)直接當 operator,不需 OpenClaw、不需手動觸發。
2. 建 notebook → 加來源:文件貼上或「網站與 YouTube 網址」→ 等 ingest 完成。
3. 用建議問題/自訂問題取得帶引用答案;取長文時注意單次回傳約 2000 字會截斷,分段抽取。
4. NotebookLM 會自動把 notebook 命名成英文——整合層必須自己綁回專案/episode id。
5. 誠實鐵則:拿不到內容就標 FAIL,不准用標題或摘要假裝是原文重點。

## 餵專案狀態的標準做法

- 來源選擇:只餵 L1 內部文件中「不含金鑰/客戶個資/持股明細」的部分;L0(持股、券商、金鑰、Owner 個資)絕不進 NotebookLM。
- 建議一專案一 notebook:maplab-ai-handbook 用 CURRENT_STATUS.md + docs/ 重點;investment-os 只餵已發布的 reports(不餵 ledger/DB)。
- 更新方式:狀態檔改版後重新上傳來源(NotebookLM 不會自己同步 git)。

## MAPLAB 可重建安全包（2026-08-25）

不要把整個 repo 直接拖進 NotebookLM。repo 內含 runtime log、credential 路由、歷史生成物、可能的客戶資料與跨專案內容；wholesale dump 會同時造成資料外洩風險、過期文件干擾與引用品質下降。

標準入口：

```bash
python3 tools/ai_workbook/build_directional_system_map.py
```

只上傳：

- `workbook/notebooklm/maplab-project-brain/maplab-project-brain.md`
- `workbook/notebooklm/maplab-project-brain/source-manifest.json`

`source-manifest.json` 會列出來源路徑、SHA-256、分類、redaction 數量與 build base commit。NotebookLM 回答現況問題時必引用來源；來源 hash 過期或涉及外部 live 狀態時，回答 `needs live refresh`，再由 A0/A1 走 API/UI/runtime readback。

禁止上傳：`.env`、token／secret value、cookie/session、credential files、客戶 raw conversations、持股／券商／ledger、SQLite/DB、runtime logs、媒體 binary、未審核 generated dump。

## 既有管線(KOL 線)

RSS→逐字稿→packet(scripts/kol_shadow_workflow.py)→ NotebookLM → Codex 整合;歷史斷點在 OpenClaw 那步,用上面的 Chrome operator 法即可繞過。產出範例:investment-os reviews/JOB-KOL-NOTEBOOKLM-OPERATOR-20260605/smoke/。
