#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from ai_workbook.build_context_pack import build_context_pack
from ai_workbook.create_microtask import create_microtask
from ai_workbook.ingest import ingest_repo
from ai_workbook.infer_need import infer_needs
from ai_workbook.parse_task_cards import parse_task_cards
from ai_workbook.photo_pipeline import build_photo_classification_plan
from ai_workbook.relation_graph import build_relation_graph
from ai_workbook.writeback import write_output


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Workbook CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("index")
    p_context = sub.add_parser("context")
    p_context.add_argument("task_id")
    p_micro = sub.add_parser("microtask")
    p_micro.add_argument("task_id")
    p_micro.add_argument("--goal", required=True)
    sub.add_parser("graph")
    sub.add_parser("infer")
    sub.add_parser("photo-plan")

    args = parser.parse_args()

    if args.cmd == "index":
        ingest = ingest_repo()
        tasks = parse_task_cards()
        print(f"indexed files={ingest['count']} tasks={tasks['count']}")
        return 0

    tasks = parse_task_cards()["tasks"]
    task = _find(tasks, getattr(args, "task_id", ""))

    if args.cmd == "context":
        if not task:
            return _not_found(args.task_id)
        p = build_context_pack(task)
        print(str(p))
        return 0

    if args.cmd == "microtask":
        if not task:
            return _not_found(args.task_id)
        p = create_microtask(task, args.goal)
        print(str(p))
        return 0

    if args.cmd == "graph":
        g = build_relation_graph(tasks)
        print(f"nodes={len(g['nodes'])} edges={len(g['edges'])}")
        return 0

    if args.cmd == "infer":
        payload = infer_needs(tasks)
        print(f"inferred={payload['count']}")
        return 0

    if args.cmd == "photo-plan":
        p = build_photo_classification_plan()
        write_output(
            "T-A4-photo-classification-restart",
            {"plan_path": str(p), "status": "proposed_only"},
            name="run_log",
        )
        print(str(p))
        return 0

    return 1


def _find(tasks: List[Dict], task_id: str) -> Optional[Dict]:
    for t in tasks:
        if t["task_id"] == task_id:
            return t
    return None


def _not_found(task_id: str) -> int:
    print(json.dumps({"error": "task_not_found", "task_id": task_id}, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())
