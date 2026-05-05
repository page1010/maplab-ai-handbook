import json
from datetime import date
from typing import Dict, List

from .paths import INFERRED_NEEDS_PATH, WORKBOOK_DIR
from .runtime_adapter import get_adapter, select_runtime


def infer_needs(tasks: List[dict]) -> Dict[str, List[dict]]:
    results = []
    for t in tasks:
        heuristic = _heuristic_infer(t)
        runtime = select_runtime(
            confidence=heuristic["confidence"],
            cross_file_reasoning=bool(t.get("related_files")),
        )
        llm = get_adapter(runtime).complete_json(_llm_prompt(t, heuristic))
        merged = {
            "task_id": t["task_id"],
            "surface_task": t.get("current_step") or t.get("task_id"),
            "inferred_real_need": heuristic["inferred_real_need"],
            "actual_output": heuristic["actual_output"],
            "real_next_action": t.get("next_action") or heuristic["real_next_action"],
            "owner_blocker": ", ".join(t.get("blockers", [])),
            "confidence": heuristic["confidence"],
            "runtime_used": runtime,
            "llm_second_opinion": llm,
            "date": str(date.today()),
        }
        results.append(merged)

    payload = {"count": len(results), "items": results}
    WORKBOOK_DIR.mkdir(parents=True, exist_ok=True)
    INFERRED_NEEDS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return payload


def _heuristic_infer(task: dict) -> dict:
    text = "\n".join(
        [
            task.get("task_id", ""),
            task.get("current_step", ""),
            " ".join(task.get("blockers", [])),
            task.get("next_action", ""),
        ]
    ).lower()
    if "seo" in text:
        inferred = "穩定產出高意圖內容並可追蹤回寫"
    elif "photo" in text or "相片" in text or "素材" in text:
        inferred = "把素材轉成可檢索且可重用的分類資產庫"
    elif "quote" in text or "報價" in text:
        inferred = "快速產生可修改的報價草稿並沉澱規則"
    else:
        inferred = "縮短交接成本，確保任務閉環與可追溯"
    return {
        "inferred_real_need": inferred,
        "actual_output": [task.get("current_step", ""), task.get("status", "")],
        "real_next_action": task.get("next_action", ""),
        "confidence": 0.7 if task.get("blockers") else 0.86,
    }


def _llm_prompt(task: dict, heuristic: dict) -> str:
    return (
        "你是任務治理助手。輸出 JSON，欄位: inferred_real_need, "
        "actual_output(array), real_next_action, owner_blocker, confidence(0-1)。\n"
        f"task={json.dumps(task, ensure_ascii=False)}\n"
        f"heuristic={json.dumps(heuristic, ensure_ascii=False)}\n"
    )

