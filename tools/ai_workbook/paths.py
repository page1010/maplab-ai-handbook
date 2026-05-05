from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKBOOK_DIR = ROOT / "workbook"
CONTEXT_PACKS_DIR = WORKBOOK_DIR / "context_packs"
MICROTASKS_DIR = WORKBOOK_DIR / "microtasks"
OUTPUTS_DIR = WORKBOOK_DIR / "outputs"
RAW_INDEX_PATH = WORKBOOK_DIR / "raw_index.json"
TASK_INDEX_PATH = WORKBOOK_DIR / "task_index.json"
RELATION_GRAPH_PATH = WORKBOOK_DIR / "relation_graph.json"
INFERRED_NEEDS_PATH = WORKBOOK_DIR / "inferred_needs.json"

