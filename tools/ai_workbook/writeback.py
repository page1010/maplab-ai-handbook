import json
from datetime import date
from pathlib import Path
from typing import Any, Dict

from .paths import OUTPUTS_DIR


def write_output(task_id: str, payload: Dict[str, Any], name: str = "summary") -> Path:
    base = OUTPUTS_DIR / str(date.today()) / task_id
    base.mkdir(parents=True, exist_ok=True)
    out = base / f"{name}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

