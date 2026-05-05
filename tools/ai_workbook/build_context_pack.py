from datetime import date
from pathlib import Path
from typing import Dict, List

from .paths import CONTEXT_PACKS_DIR, ROOT


def build_context_pack(task: dict) -> Path:
    CONTEXT_PACKS_DIR.mkdir(parents=True, exist_ok=True)
    task_id = task["task_id"]
    path = CONTEXT_PACKS_DIR / f"{task_id}.md"
    rel_rules = _pick_rules(task)
    rel_projects = _pick_projects(task)
    rel_skills = _pick_skills(task)
    md = f"""# Context Pack — {task_id}

Date: {date.today()}
Owner: {task.get("owner_agent", "UNKNOWN")}
Status: {task.get("status", "")}
Current Step: {task.get("current_step", "")}
Blockers: {", ".join(task.get("blockers", [])) or "none"}
Next Action: {task.get("next_action", "")}

## Role Summary
- This pack is trimmed for one task only.
- Goal: reduce context size and keep execution deterministic.

## Relevant Rules
{_as_bullets(rel_rules)}

## Relevant Projects
{_as_bullets(rel_projects)}

## Relevant Skills
{_as_bullets(rel_skills)}

## Output Contract
- Must include: input -> action -> output -> check -> relation -> next.
- Writeback targets:
  - workbook/outputs/YYYY-MM-DD/{task_id}/
  - workbook/relation_graph.json
- Do not modify CURRENT_STATUS.md automatically.
"""
    path.write_text(md, encoding="utf-8")
    return path


def _pick_rules(task: dict) -> List[str]:
    out = []
    for rel in ["AGENT_RULES.md", "AGENT_STARTUP_PROTOCOL.md", "CURRENT_STATUS.md"]:
        if (ROOT / rel).exists():
            out.append(rel)
    if task.get("category") == "SEO":
        out.append("skills/page-checker.md")
    return out


def _pick_projects(task: dict) -> List[str]:
    candidates = []
    task_id = task.get("task_id", "")
    for p in (ROOT / "projects").glob("*.md"):
        name = p.name.lower()
        if "seo" in task_id.lower() and "seo" in name:
            candidates.append(str(p.relative_to(ROOT)))
        elif "a6" in task_id.lower() and ("quote" in name or "architecture" in name):
            candidates.append(str(p.relative_to(ROOT)))
    if not candidates:
        candidates = ["projects/v6-architecture.md"]
    return sorted(set(candidates))[:6]


def _pick_skills(task: dict) -> List[str]:
    cat = task.get("category")
    if cat == "SEO":
        return [
            "skills/seo-session-checklist.md",
            "skills/page-checker.md",
            "skills/task-progress-guide.md",
        ]
    if cat == "PHOTO":
        return [
            "skills/photo-pipeline-toolkit-guide.md",
            "skills/a4-photo-asset-skills.md",
            "skills/task-progress-guide.md",
        ]
    if cat == "QUOTE":
        return ["skills/a6-sales-rapid-response-skills.md", "skills/task-progress-guide.md"]
    return ["skills/task-progress-guide.md"]


def _as_bullets(items: List[str]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- {i}" for i in items)

