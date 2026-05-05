from datetime import date
from pathlib import Path

from .paths import MICROTASKS_DIR


def create_microtask(task: dict, goal: str) -> Path:
    MICROTASKS_DIR.mkdir(parents=True, exist_ok=True)
    task_id = task["task_id"]
    microtask_id = f"MT-{task_id}-001"
    out = MICROTASKS_DIR / f"{microtask_id}.md"
    md = f"""microtask_id: {microtask_id}
parent_task: {task_id}
owner_agent: {task.get("owner_agent", "A1")}
request_from_owner: {goal}
inferred_real_need: 將大任務拆成可驗收短任務閉環
input_sources:
  - file: {task.get("task_card_path", "")}
  - file: AGENT_RULES.md
  - file: CURRENT_STATUS.md
action:
  1. 讀取必要輸入，不擴張範圍
  2. 產出可驗證檔案
  3. 執行最小檢查並回寫 relation
expected_output:
  - summary.md
  - run_log.json
output_path: workbook/outputs/{date.today()}/{task_id}/
consumer:
  - owner
related_tasks:
  - {task_id}
check_rule:
  - output exists
  - fields complete
write_back:
  - workbook/outputs/{date.today()}/{task_id}/
  - workbook/relation_graph.json
next_action: 交給下一個執行角色或人工審核
owner_decision_required: false
risk_level: low
"""
    out.write_text(md, encoding="utf-8")
    return out

