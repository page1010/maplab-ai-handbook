import json
import re
from pathlib import Path
from typing import Dict, List

from .paths import ROOT, TASK_INDEX_PATH, WORKBOOK_DIR


STATUS_PATTERNS = [
    re.compile(r"-\s*\*\*狀態\*\*:\s*(.+)"),
    re.compile(r"-\s*狀態:\s*(.+)"),
]
LAST_ACTIVITY_PATTERNS = [
    re.compile(r"-\s*\*\*最後活動\*\*:\s*(.+)"),
    re.compile(r"-\s*最後活動:\s*(.+)"),
]
CURRENT_STEP_PATTERNS = [
    re.compile(r"-\s*\*\*接續點\*\*:\s*(.+)"),
    re.compile(r"-\s*接續點:\s*(.+)"),
]
BLOCKER_PATTERNS = [
    re.compile(r"-\s*\*\*阻塞\*\*:\s*(.+)"),
    re.compile(r"-\s*阻塞:\s*(.+)"),
]


def parse_task_cards() -> Dict[str, List[dict]]:
    cards = []
    for p in sorted((ROOT / "handoff" / "tasks").glob("*.md")):
        cards.append(parse_single_card(p))

    result = {"count": len(cards), "tasks": cards}
    WORKBOOK_DIR.mkdir(parents=True, exist_ok=True)
    TASK_INDEX_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def parse_single_card(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    title = lines[0].strip() if lines else path.stem
    task_id = _extract_task_id(title, path.stem)
    owner = _extract_owner(text, task_id)
    status = _extract_by_patterns(text, STATUS_PATTERNS)
    last_activity = _extract_by_patterns(text, LAST_ACTIVITY_PATTERNS)
    current_step = _extract_by_patterns(text, CURRENT_STEP_PATTERNS)
    blocker = _extract_by_patterns(text, BLOCKER_PATTERNS)
    next_action = _extract_next_action(text)
    done = _extract_checked_items(text)
    continuation_prompt = _extract_continuation_prompt(text)
    related_files = _extract_related_files(text)
    category = _infer_category(text, task_id)
    return {
        "task_id": task_id,
        "owner_agent": owner,
        "status": status,
        "last_activity": last_activity,
        "current_step": current_step,
        "blockers": [blocker] if blocker else [],
        "done": done,
        "next_action": next_action,
        "continuation_prompt": continuation_prompt,
        "related_files": related_files,
        "task_card_path": str(path.relative_to(ROOT)),
        "category": category,
    }


def _extract_task_id(title: str, fallback: str) -> str:
    m = re.search(r"(T-[A-Z0-9-]+)", title)
    return m.group(1) if m else fallback


def _extract_owner(text: str, task_id: str) -> str:
    m = re.search(r"\*\*負責\*\*[:：]\s*([A-Za-z0-9]+)", text)
    if m:
        return m.group(1)
    m = re.search(r"(A[0-9])", task_id)
    return m.group(1) if m else "UNKNOWN"


def _extract_by_patterns(text: str, patterns: List[re.Pattern]) -> str:
    for p in patterns:
        m = p.search(text)
        if m:
            return m.group(1).strip()
    return ""


def _extract_next_action(text: str) -> str:
    m = re.search(r"下一步[:：]\s*(.+)", text)
    if m:
        return m.group(1).strip()
    lines = [ln.strip("- ").strip() for ln in text.splitlines() if "待做" in ln or "next" in ln.lower()]
    return lines[0] if lines else ""


def _extract_checked_items(text: str) -> List[str]:
    done = []
    for ln in text.splitlines():
        if ln.strip().startswith("- [x]") or ln.strip().startswith("- [X]"):
            done.append(ln.strip()[5:].strip())
    return done[:20]


def _extract_continuation_prompt(text: str) -> str:
    anchor = "接續 Prompt"
    idx = text.find(anchor)
    if idx < 0:
        return ""
    chunk = text[idx : idx + 900]
    return "\n".join(chunk.splitlines()[:12]).strip()


def _extract_related_files(text: str) -> List[str]:
    out = []
    for m in re.finditer(r"`([^`]+\.md)`", text):
        out.append(m.group(1))
    return sorted(set(out))[:30]


def _infer_category(text: str, task_id: str) -> str:
    bag = f"{task_id}\n{text}".lower()
    if "seo" in bag:
        return "SEO"
    if "quote" in bag or "報價" in bag:
        return "QUOTE"
    if "photo" in bag or "相片" in bag or "素材" in bag:
        return "PHOTO"
    return "OPS"

