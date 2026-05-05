import json
from datetime import date
from typing import Dict, List, Optional

from .paths import RELATION_GRAPH_PATH, WORKBOOK_DIR


def build_relation_graph(tasks: List[dict]) -> Dict[str, list]:
    nodes = []
    edges = []
    for task in tasks:
        task_node = _node("task", task["task_id"])
        nodes.append(task_node)
        owner = task.get("owner_agent", "UNKNOWN")
        nodes.append(_node("agent", owner))
        edges.append(_edge(task["task_id"], owner, "task->agent"))
        for blocker in task.get("blockers", []):
            bid = f"blocker:{blocker[:80]}"
            nodes.append(_node("blocker", bid, blocker))
            edges.append(_edge(task["task_id"], bid, "task->blocker"))
        cat = task.get("category", "OPS")
        pid = f"project:{cat}"
        nodes.append(_node("project", pid, cat))
        edges.append(_edge(task["task_id"], pid, "task->project"))
        oc = f"output_contract:{cat}"
        nodes.append(_node("output_contract", oc))
        edges.append(_edge(task["task_id"], oc, "task->output_contract"))

    graph = {
        "date": str(date.today()),
        "nodes": _uniq(nodes),
        "edges": _uniq(edges),
    }
    WORKBOOK_DIR.mkdir(parents=True, exist_ok=True)
    RELATION_GRAPH_PATH.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return graph


def _node(kind: str, node_id: str, label: Optional[str] = None) -> dict:
    return {"id": node_id, "type": kind, "label": label or node_id}


def _edge(src: str, dst: str, rel: str) -> dict:
    return {"from": src, "to": dst, "relation": rel}


def _uniq(items: List[dict]) -> List[dict]:
    seen = set()
    out = []
    for it in items:
        k = json.dumps(it, ensure_ascii=False, sort_keys=True)
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out
