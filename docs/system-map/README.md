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

The same build writes the Extension offline copy and the NotebookLM sanitized source pack. Graphify is optional; use the generated nodes/edges JSON when it becomes available.
