# MAPLAB Directional System Map

`index.html` and `maplab-directional-map.graph.json` are generated outputs. Do not edit them directly.

Canonical source:

- `config/system-map/maplab-directional-map.json`
- `config/system-map/maplab-directional-map.schema.json`

Build and verify:

```bash
python3 tools/ai_workbook/build_directional_system_map.py
python3 -m unittest tools.ai_workbook.test_build_directional_system_map -v
python3 tools/ai_workbook/build_directional_system_map.py --check
```

The same build writes the Extension offline copy and the NotebookLM sanitized source pack.

Graphify 0.9.49 另有一張 AST-only 程式依賴圖：

- `graphify-out/graph.html`：程式節點／community 互動圖。
- `graphify-out/GRAPH_TREE.html`：目錄樹與檔案內符號。
- `graphify-out/GRAPH_REPORT.md`：god nodes、surprising connections、cohesion 與 freshness。
- `graphify-out/graph.json`：`query` / `path` / `explain` / `affected` 的正式圖資料。

兩層不能互相取代：canonical map 回答角色、SOP、Sheet、gate 與治理；Graphify 回答程式函式、檔案、call/import 與影響面。
