# Skill:指向性地圖(系統全貌導覽視覺化)

- 建立:2026-08-25|更新:2026-08-25(單一 manifest + 七視角)|作者:A0/Fable5+A1/Codex|狀態:**已建 v2**
- Owner 澄清(msg 3999 前後):指向性地圖=**幫助了解系統全貌的導覽圖**,不是地理地圖。

## 成品位置

- Canonical manifest：`config/system-map/maplab-directional-map.json`。
- Schema：`config/system-map/maplab-directional-map.schema.json`。
- Owner 網頁：`docs/system-map/index.html`。
- Extension 離線網頁：`chrome-extension/system-map/index.html`。
- Graph JSON：`docs/system-map/maplab-directional-map.graph.json`。
- 生成器：`python3 tools/ai_workbook/build_directional_system_map.py`。
- 七視角：系統總圖、Repo／地址、角色與派工、A2–A8 工作流、產物血緣、能力／工具／硬體、治理／記憶／證據。

## 維護規則(所有 agent 共用)

1. 禁止直接修改兩份 generated HTML；只改 manifest 或 generator，再重建。
2. 每個 workflow stage 必須有輸入、執行、輸出、驗收、交接、工具、approval gate、evidence。
3. 每個 path 必須是真實來源或明確標示 generated／external ID；路徑錯誤會讓生成器失敗。
4. 狀態只用 verified／declared／missing／excluded；模型建議不得標 verified。
5. Graphify 只讀 graph JSON 管檔案與依賴；`CURRENT_STATUS.md` 管現況、Task Card 管邊界、receipt 管完成。
6. 不放金鑰、token value、客戶原始個資、持股、runtime dump 或 chat_id。

## 驗證

```bash
python3 -m unittest tools.ai_workbook.test_build_directional_system_map -v
python3 tools/ai_workbook/build_directional_system_map.py
python3 tools/ai_workbook/build_directional_system_map.py --check
```

## Graphify 已上線（2026-08-25）

- 版本：`0.9.49`；全域 Codex 規則：`/Users/pagemacmini/AGENTS.md`。
- repo 排除規則：`.graphifyignore`，排除投資域、secrets、runtime logs、客戶原始資料、歷史／生成器雜訊。
- 程式圖：`graphify-out/graph.json`（1817 nodes／3252 edges／148 communities）。
- 互動圖：`graphify-out/graph.html`；目錄樹：`graphify-out/GRAPH_TREE.html`。
- 診斷：0 dangling、0 missing endpoints、0 self-loops、0 collapsed edges；AST 抽取曾警告 `AppKit` 與 `Foundation` 各有一個重複 node id 被去重。
- 效率基準：約 121,133 naive tokens 對 3,404 average query tokens，約 `35.6x` 縮減。

維護指令：

```bash
graphify update .
graphify query "<question>"
graphify path "<A>" "<B>" --undirected
graphify explain "<concept>"
graphify tree --graph graphify-out/graph.json --output graphify-out/GRAPH_TREE.html --root .
```

Graphify 只用於程式結構與影響面；治理真相仍來自 canonical manifest、`CURRENT_STATUS.md`、Task Card、live readback 與 receipt。
