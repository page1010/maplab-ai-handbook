from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from ai_workbook.openclaw_adapter import OpenClawAdapter
except Exception:  # pragma: no cover - fallback path is tested from runtime.
    OpenClawAdapter = None  # type: ignore[assignment]


DEFAULT_LOCAL_MODEL = os.getenv("A5_LOCAL_MODEL", os.getenv("OPENCLAW_MODEL", "qwen2.5:14b"))
DEFAULT_LOCAL_ENGINE = os.getenv("A5_LOCAL_ENGINE", "auto")
DEFAULT_THINKING = os.getenv("A5_LOCAL_THINKING", "off")
DEFAULT_PROMPT_PROFILE = os.getenv("A5_QUOTE_PROMPT_PROFILE", "telegram")


@dataclass(frozen=True)
class A5QuoteResult:
    answer: str
    engine_used: str
    model_used: str
    fallback_used: bool
    bundle_dir: Optional[str] = None
    error: str = ""


def build_a5_quote_prompt(
    user_message: str,
    user_name: str = "",
    history: Optional[Iterable[dict]] = None,
    runtime: str = "local",
    profile: Optional[str] = None,
) -> str:
    prompt_profile = profile or DEFAULT_PROMPT_PROFILE
    docs = _load_support_docs(prompt_profile)
    parsed_facts = _extract_normalized_facts(user_message)
    sections = [
        "# MAPLAB A5 Quote Runtime",
        "",
        f"- runtime: {runtime}",
        f"- requester: {user_name or 'Owner'}",
        f"- generated_at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Identity",
        "你是 MAPLAB A5 報價與提案引擎部。你負責菜單品項資料庫、成本/毛利邏輯、報價公式、活動模板、報價草稿生成。",
        "你正在協助 Owner 或業務整理內部報價草稿，不是直接對客戶發送正式報價。",
        "",
        "## Operating rules",
        "- 先產出可用草稿，不因為缺少日期、地點或預算而卡住；缺資料時列為待確認。",
        "- 不得自行改 Google Sheets、Items 主表、GAS、Drive、WordPress 或正式 truth source。",
        "- 不得揭露內部成本給客戶；但可以在內部草稿中標示估算成本與毛利風險。",
        "- 報價判斷必須分開寫：餐點毛利 / 食材成本佔比，以及整體毛利；餐點安全線以食材成本不超過餐點收入 20% 為優先。",
        "- 客戶指定的價格級距只是詢價條件，不等於 A5 已核准承接價；若指定價格低於毛利安全線，必須先說明限制，提供「升價保留內容」或「精簡菜單守毛利」兩條路，不得默默犧牲毛利。",
        "- 如果使用者只是說「第一版 / 毛利太低 / 調高一點」但近期上下文沒有明確案件或報價連結，不要沿用舊測試案，請先要求指定案件或報價單。",
        "- 不猜不存在的報價單 URL；如果沒有外部寫入，就明確說這是本地草稿。",
        "- 如果本地模型信心不足，最後輸出一段可交給其他模型或 A5 雲端引擎的 handoff prompt。",
        "",
        "## Response contract",
        "請用繁體中文 Markdown，控制在手機可讀長度。輸出固定包含：",
        "1. `A5 報價草稿`：案件摘要、缺漏資訊、建議方案。",
        "2. `建議菜單`：依類別列出品項與數量，優先用已知 MAPLAB 品項。",
        "3. `金額判斷`：建議報價、車馬/服務/搬運假設、餐點毛利/食材成本佔比、整體毛利，不要偽造正式報價單連結。",
        "4. `業務下一步`：要問客戶或 Owner 的 3-5 件事。",
        "5. `備援 handoff prompt`：一段可直接交給其他模型續做的短 prompt。",
        "",
        "## Deterministic parsing hints",
        "以下是進模型前的硬解析提示。若與模型自行推測衝突，優先採用本段，尤其是中文金額單位。",
        parsed_facts,
        "",
        "## Support docs",
        f"(profile: {prompt_profile})",
    ]
    for path, content in docs.items():
        sections.extend([f"### {path}", content, ""])

    if history:
        sections.append("## Recent conversation")
        history_limit = 8 if prompt_profile == "full" else 3
        content_limit = 900 if prompt_profile == "full" else 300
        for msg in list(history)[-history_limit:]:
            role = "使用者" if msg.get("role") == "user" else "助理"
            content = str(msg.get("content", "")).strip()
            if content:
                sections.append(f"{role}: {content[:content_limit]}")
        sections.append("")

    sections.extend(
        [
            "## User request",
            "```text",
            user_message.strip(),
            "```",
            "",
            "請直接產出草稿。若需求已足夠，可給一組推薦方案；若資訊不足，也要先給可用估算與補問清單。",
        ]
    )
    return "\n".join(sections)


def _extract_normalized_facts(user_message: str) -> str:
    lines: list[str] = [
        "- 中文金額單位：1萬 = 10,000；5萬 = 50,000；不要把 5萬 展成 500,000。"
    ]
    budget = _find_budget(user_message)
    if budget:
        lines.append(f"- 偵測預算：NT${budget[0]:,}（來源：{budget[1]}）")
    people = re.findall(r"(\d{1,4})\s*(?:人|位)", user_message)
    if people:
        lines.append(f"- 偵測人數：{people[-1]} 人")
    restrictions = _find_restrictions(user_message)
    if restrictions:
        lines.append(f"- 偵測飲食禁忌：{'; '.join(restrictions)}")
    return "\n".join(lines)


def _find_restrictions(user_message: str) -> list[str]:
    patterns = [
        (r"(?:不吃|不要|無|不能有)\s*牛", "不可含牛肉"),
        (r"(?:不吃|不要|無|不能有)\s*海鮮", "不可含海鮮"),
        (r"(?:不吃|不要|無|不能有)\s*酒", "不可含酒精"),
        (r"素食|吃素|蔬食", "需要素食或蔬食選項"),
    ]
    return [label for pattern, label in patterns if re.search(pattern, user_message)]


def _find_budget(user_message: str) -> Optional[tuple[int, str]]:
    budget_patterns = [
        r"(?:預算|budget|費用|金額)\s*(?:約|大約|around)?\s*(\d+(?:\.\d+)?)\s*([萬万kK]?)",
        r"(\d+(?:\.\d+)?)\s*([萬万kK])\s*(?:預算|budget|費用|金額)?",
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, user_message, flags=re.IGNORECASE)
        if not match:
            continue
        raw_number = match.group(1)
        unit = match.group(2) or ""
        amount = float(raw_number)
        if unit in {"萬", "万"}:
            amount *= 10000
        elif unit in {"k", "K"}:
            amount *= 1000
        return int(amount), match.group(0).strip()
    return None


def _apply_deterministic_corrections(answer: str, user_message: str) -> str:
    answer = _sanitize_model_output(answer)
    budget = _find_budget(user_message)
    if not budget:
        return answer
    amount, source = budget
    normalized = f"NT${amount:,}"
    corrected_lines: list[str] = []
    changed = False
    for line in answer.splitlines():
        if "預算" in line and "NT$" in line:
            new_line = re.sub(r"NT\$[\d,]+", normalized, line, count=1)
            changed = changed or new_line != line
            corrected_lines.append(new_line)
        else:
            corrected_lines.append(line)
    note = f"> 金額校正：使用者預算解析為 {normalized}（來源：{source}；萬=10,000）。"
    corrected = "\n".join(corrected_lines).strip()
    if changed or note not in corrected:
        return note + "\n\n" + corrected
    return corrected


def _sanitize_model_output(answer: str) -> str:
    answer = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", answer)
    return answer.replace("\r", "").strip()


def run_a5_local_quote(
    user_message: str,
    user_name: str = "",
    history: Optional[Iterable[dict]] = None,
    job_id: Optional[str] = None,
    engine: Optional[str] = None,
    model: Optional[str] = None,
) -> A5QuoteResult:
    job = job_id or _new_job_id("A5-QUOTE")
    prompt = build_a5_quote_prompt(
        user_message=user_message,
        user_name=user_name,
        history=history,
        runtime="openclaw/ollama-fallback",
    )
    requested_engine = engine or DEFAULT_LOCAL_ENGINE
    requested_model = model or DEFAULT_LOCAL_MODEL

    if OpenClawAdapter is not None:
        try:
            adapter = OpenClawAdapter(default_model=requested_model)
            result = adapter.run_local_task(
                job_id=job,
                prompt=prompt,
                model=requested_model,
                engine=requested_engine,
                thinking=DEFAULT_THINKING,
            )
            draft_path = Path(str(result["draft_md"]))
            raw_answer = draft_path.read_text(encoding="utf-8").strip()
            answer = _apply_deterministic_corrections(
                raw_answer,
                user_message,
            )
            if answer != raw_answer:
                draft_path.write_text(answer + "\n", encoding="utf-8")
            return A5QuoteResult(
                answer=_append_local_footer(answer, result),
                engine_used=str(result.get("engine_used", requested_engine)),
                model_used=str(result.get("model_used", requested_model)),
                fallback_used=bool(result.get("fallback_used", False)),
                bundle_dir=str(result.get("bundle_dir", "")) or None,
            )
        except Exception as exc:
            direct = _run_direct_ollama(prompt, requested_model)
            direct = _apply_deterministic_corrections(direct, user_message)
            return A5QuoteResult(
                answer=_append_direct_footer(direct, job, str(exc)),
                engine_used="ollama-direct",
                model_used=requested_model,
                fallback_used=True,
                bundle_dir=None,
                error=str(exc),
            )

    direct = _run_direct_ollama(prompt, requested_model)
    direct = _apply_deterministic_corrections(direct, user_message)
    return A5QuoteResult(
        answer=_append_direct_footer(direct, job, "OpenClawAdapter unavailable"),
        engine_used="ollama-direct",
        model_used=requested_model,
        fallback_used=True,
        bundle_dir=None,
        error="OpenClawAdapter unavailable",
    )


def _run_direct_ollama(prompt: str, model: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": int(os.getenv("A5_LOCAL_NUM_CTX", "4096")),
                "num_predict": int(os.getenv("A5_LOCAL_NUM_PREDICT", "900")),
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=int(os.getenv("A5_LOCAL_TIMEOUT_SECONDS", "90"))) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    return (data.get("response") or "").strip() or "⚠️ 本地模型沒有產出內容。"


def _load_support_docs(profile: str = "telegram") -> dict[str, str]:
    if profile == "full":
        files = {
            "recalls/A5_recall.md": 120,
            "handoff/tasks/T-A5-002.md": 180,
            "handoff/tasks/T-A5-004.md": 120,
            "handoff/tasks/T-A5-005.md": 90,
            "skills/a6-rapid-quote-sop.md": 230,
            "data/quote-terms-reference.md": 120,
            "archive/data/item-frequency-top50.md": 120,
            "archive/data/item-master-cross-reference.md": 160,
        }
    else:
        files = {
            "recalls/A5_recall.md": 25,
            "handoff/tasks/T-A5-002.md": 25,
            "handoff/tasks/T-A5-004.md": 8,
            "handoff/tasks/T-A5-005.md": 8,
            "skills/a6-rapid-quote-sop.md": 35,
            "data/quote-terms-reference.md": 25,
            "archive/data/item-frequency-top50.md": 35,
            "archive/data/item-master-cross-reference.md": 35,
        }
    return {path: _read_doc(ROOT / path, max_lines) for path, max_lines in files.items()}


def _read_doc(path: Path, max_lines: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
    except Exception:
        return f"(missing: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path})"
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["", f"... ({len(lines) - max_lines} more lines omitted)"]
    return "\n".join(lines)


def _new_job_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _append_local_footer(answer: str, result: dict) -> str:
    bundle_dir = result.get("bundle_dir", "")
    footer = [
        "",
        "---",
        f"本地備援：engine={result.get('engine_used')} model={result.get('model_used')} fallback={result.get('fallback_used')}",
    ]
    if bundle_dir:
        footer.append(f"review bundle: `{bundle_dir}`")
    return answer.rstrip() + "\n" + "\n".join(footer)


def _append_direct_footer(answer: str, job_id: str, reason: str) -> str:
    return (
        answer.rstrip()
        + "\n\n---\n"
        + f"本地備援：engine=ollama-direct job_id={job_id}\n"
        + f"fallback reason: {reason}"
    )
