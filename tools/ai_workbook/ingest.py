import json
from pathlib import Path
from typing import Dict, List

from .paths import RAW_INDEX_PATH, ROOT, WORKBOOK_DIR


SOURCES = [
    "CURRENT_STATUS.md",
    "AGENT_RULES.md",
    "AGENT_RECALL_PROMPTS.md",
    "TASK_QUEUE.md",
]

GLOBS = [
    "handoff/tasks/*.md",
    "projects/*.md",
    "skills/*.md",
]


def ingest_repo() -> Dict[str, List[dict]]:
    files = []
    for rel in SOURCES:
        p = ROOT / rel
        if p.exists():
            files.append(_meta(p))

    for pattern in GLOBS:
        for p in sorted(ROOT.glob(pattern)):
            if p.is_file():
                files.append(_meta(p))

    result = {"root": str(ROOT), "count": len(files), "files": files}
    WORKBOOK_DIR.mkdir(parents=True, exist_ok=True)
    RAW_INDEX_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def _meta(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "lines": text.count("\n") + 1,
        "title": text.splitlines()[0].strip() if text else "",
    }

