from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from typing import Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
OPENCLAW_WORKSPACE_DIR = Path(
    os.getenv("OPENCLAW_WORKSPACE_DIR", str(Path.home() / ".openclaw" / "workspace"))
)
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from ai_workbook.openclaw_adapter import OpenClawAdapter


ADS_KEYWORDS = {
    "廣告", "meta", "meta廣告", "meta ads", "facebook", "ig", "instagram",
    "wordpress", "wp", "seo", "slug", "alt", "meta description",
    "素材", "照片", "圖片", "圖文", "文案", "草稿", "活動照片", "外燴",
    "landing", "blog", "文章", "內連", "內部連結", "發文", "內容",
}
STOCK_KEYWORDS = {
    "股票", "台股", "財報", "回測", "估值", "風險", "產業", "etf", "美債",
    "台積", "台泥", "研究", "新聞", "籌碼", "技術分析", "基本面",
}
REVIEW_KEYWORDS = {
    "程式", "代碼", "code", "debug", "修正", "review", "審稿", "架構",
    "文件", "規格", "workflow", "系統", "設定", "驗證", "測試",
}


@dataclass(frozen=True)
class DispatchDecision:
    task_type: str
    reason: str
    worker: str
    review_required: bool = True


class OpenClawDispatchRouter:
    def __init__(
        self,
        repo_root: Optional[Path] = None,
        model: Optional[str] = None,
        thinking: Optional[str] = None,
    ) -> None:
        self.repo_root = repo_root or ROOT
        self.model = model or os.getenv("OPENCLAW_MODEL", "qwen2.5:14b")
        self.thinking = thinking or os.getenv("OPENCLAW_THINKING", "off")
        self.task_models = {
            "dispatch": os.getenv("OPENCLAW_MODEL_DISPATCH", "qwen2.5-coder:7b"),
            "ads": os.getenv("OPENCLAW_MODEL_ADS", "qwen2.5-coder:7b"),
            "stock": os.getenv("OPENCLAW_MODEL_STOCK", "qwen3.5:latest"),
            "review": os.getenv("OPENCLAW_MODEL_REVIEW", "llama3.1:latest"),
        }
        self.adapter = OpenClawAdapter(default_model=self.model)

    def classify(self, text: str, mode: str = "dispatch", has_photo: bool = False) -> DispatchDecision:
        lowered = text.lower()
        if mode == "ads":
            return DispatchDecision("ads", "使用者手動指定廣告/內容工作流", "A6 Ads worker")
        if mode == "stock":
            return DispatchDecision("stock", "使用者手動指定股票/研究工作流", "A6 Stock worker")
        if mode == "review":
            return DispatchDecision("review", "使用者手動指定審稿/工程工作流", "A6 Review worker")

        if has_photo:
            return DispatchDecision("ads", "含照片輸入，預設走素材整理與內容路由", "A6 Ads worker")
        if _matches(lowered, STOCK_KEYWORDS):
            return DispatchDecision("stock", "命中股票/研究相關關鍵字", "A6 Stock worker")
        if _matches(lowered, ADS_KEYWORDS):
            return DispatchDecision("ads", "命中廣告、WordPress、SEO、素材關鍵字", "A6 Ads worker")
        if _matches(lowered, REVIEW_KEYWORDS):
            return DispatchDecision("review", "命中程式、架構、驗證、審稿關鍵字", "A6 Review worker")
        return DispatchDecision("review", "未命中明確商業詞彙，預設走審稿/工程工作流", "A6 Review worker")

    def run(
        self,
        job_id: str,
        user_message: str,
        mode: str = "dispatch",
        user_name: str = "",
        has_photo: bool = False,
        photo_path: Optional[str] = None,
        caption: str = "",
    ) -> Dict[str, object]:
        decision = self.classify(user_message, mode=mode, has_photo=has_photo)
        task_model = self._model_for_task(decision.task_type)
        prompt = self._build_prompt(
            job_id=job_id,
            user_message=user_message,
            user_name=user_name,
            decision=decision,
            task_model=task_model,
            has_photo=has_photo,
            photo_path=photo_path,
            caption=caption,
        )
        result = self.adapter.run_local_task(
            job_id=job_id,
            prompt=prompt,
            model=task_model,
            engine="auto",
            thinking=self.thinking,
        )
        bundle_dir = Path(result["bundle_dir"])
        routing_path = bundle_dir / "routing.json"
        routing_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "task_type": decision.task_type,
                    "reason": decision.reason,
                    "worker": decision.worker,
                    "review_required": decision.review_required,
                    "mode": mode,
                    "requested_model": self.model,
                    "task_model": task_model,
                    "thinking": self.thinking,
                    "has_photo": has_photo,
                    "photo_path": photo_path,
                    "caption": caption,
                    "documents_loaded": self._documents_loaded(decision.task_type),
                    "workspace_root": str(self.repo_root),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        result["routing_json"] = str(routing_path)
        result["task_type"] = decision.task_type
        result["decision_reason"] = decision.reason
        result["worker"] = decision.worker
        return result

    def _build_prompt(
        self,
        job_id: str,
        user_message: str,
        user_name: str,
        decision: DispatchDecision,
        task_model: str,
        has_photo: bool,
        photo_path: Optional[str],
        caption: str,
    ) -> str:
        docs = self._documents_loaded(decision.task_type)
        sections = [
            "# MAPLAB A6 OpenClaw Dispatch",
            "",
            f"- job_id: {job_id}",
            f"- task_type: {decision.task_type}",
            f"- worker: {decision.worker}",
            f"- reason: {decision.reason}",
            f"- review_required: {str(decision.review_required).lower()}",
            f"- requested_model: {self.model}",
            f"- task_model: {task_model}",
            f"- thinking: {self.thinking}",
            "",
            "## Role",
            "你是 MAPLAB A6 的 dispatch secretary。你不是最終決策者，只做分類、轉派、整理與回報。",
            "你必須輸出可審查成果，不可直接發布到 WordPress、不可推送 main、不可刪除原始素材。",
            "",
            "## Safety boundaries",
            "請遵守 review bundle first、只做 draft / research / verification，不做正式發布或高風險寫入。",
            "",
            "## Dispatch role",
            "根據任務類型把工作轉給正確 worker；廣告任務走 ads、股票任務走 stock、其餘走 review。",
            "廣告任務優先產出草稿與素材包，股票任務只產研究與風險筆記，審稿任務只做驗證與修正建議。",
            "",
            "## Worker profile",
            f"worker_doc: {self._worker_doc_path(decision.task_type).name}",
            "",
            "## Loaded support docs",
        ]
        for rel_path, content in docs.items():
            sections.extend([f"### {rel_path}", content, ""])
        sections.extend(
            [
                "## User request",
                f"Requester: {user_name or 'Owner'}",
                "",
                "```text",
                user_message,
                "```",
                "",
            "## Response contract",
            "請用繁體中文，先給 5 行內的 dispatch summary，再給可審查產出清單。",
            "整體請保持精簡，優先列點，不要長篇敘事；總長度盡量控制在 500 字以內。",
            "如果是廣告/內容任務，請包含：WordPress 草稿、SEO title、meta description、slug、圖片建議、alt text、Meta 廣告標題、Meta 廣告文案、素材使用說明。",
            "如果是股票任務，請包含：研究摘要、風險清單、觀察重點、下一步待核實問題。",
            "如果是審稿/工程任務，請包含：問題診斷、修正建議、驗證清單、風險提示。",
                "最後請附上一段「給 Owner 的回報」與「下一步建議」。",
            ]
        )
        if has_photo:
            sections.extend(
                [
                    "",
                    "## Attached photo context",
                    f"- photo_path: {photo_path or ''}",
                    f"- caption: {caption or ''}",
                    "若無法直接讀圖，請根據路徑與說明產出可執行的素材整理建議，並清楚標註需要人工確認的地方。",
                ]
            )
        return "\n".join(sections)

    def _model_for_task(self, task_type: str) -> str:
        return self.task_models.get(task_type, self.model)

    def _documents_loaded(self, task_type: str) -> Dict[str, str]:
        docs = {
            "docs/openclaw/README.md": _read_doc(self.repo_root / "docs" / "openclaw" / "README.md", max_lines=20),
            "docs/openclaw/memory-governance.md": _read_doc(self.repo_root / "docs" / "openclaw" / "memory-governance.md", max_lines=36),
            "docs/openclaw/output-contract.md": _read_doc(self.repo_root / "docs" / "openclaw" / "output-contract.md", max_lines=36),
            "docs/openclaw/relation-graph.md": _read_doc(self.repo_root / "docs" / "openclaw" / "relation-graph.md", max_lines=36),
            "docs/openclaw/closed-loop-playbook.md": _read_doc(self.repo_root / "docs" / "openclaw" / "closed-loop-playbook.md", max_lines=32),
            "docs/openclaw/dispatch-role.md": _read_doc(self.repo_root / "docs" / "openclaw" / "dispatch-role.md", max_lines=24),
            "docs/openclaw/security-boundaries.md": _read_doc(self.repo_root / "docs" / "openclaw" / "security-boundaries.md", max_lines=24),
            "workbook/reviews/README.md": _read_doc(self.repo_root / "workbook" / "reviews" / "README.md", max_lines=24),
            "docs/governance/verification-bundles.md": _read_doc(self.repo_root / "docs" / "governance" / "verification-bundles.md", max_lines=32),
            "workspace/AGENTS.md": _read_doc(OPENCLAW_WORKSPACE_DIR / "AGENTS.md", max_lines=24),
            "workspace/MEMORY_FRAMEWORK.md": _read_doc(OPENCLAW_WORKSPACE_DIR / "MEMORY_FRAMEWORK.md", max_lines=40),
            "workspace/BOOTSTRAP.md": _read_doc(OPENCLAW_WORKSPACE_DIR / "BOOTSTRAP.md", max_lines=24),
            "workspace/IDENTITY.md": _read_doc(OPENCLAW_WORKSPACE_DIR / "IDENTITY.md", max_lines=24),
            "workspace/SOUL.md": _read_doc(OPENCLAW_WORKSPACE_DIR / "SOUL.md", max_lines=24),
        }
        if task_type == "ads":
            docs.update(
                {
                    "docs/openclaw/ads-assistant.md": _read_doc(self.repo_root / "docs" / "openclaw" / "ads-assistant.md", max_lines=24),
                    "skills/maplab-visual-spec.md": _read_doc(self.repo_root / "skills" / "maplab-visual-spec.md", max_lines=32),
                    "skills/a4-photo-asset-skills.md": _read_doc(self.repo_root / "skills" / "a4-photo-asset-skills.md", max_lines=32),
                    "docs/business-requirements/a6-usage-scenarios.md": _read_doc(self.repo_root / "docs" / "business-requirements" / "a6-usage-scenarios.md", max_lines=40),
                }
            )
        elif task_type == "stock":
            docs.update(
                {
                    "docs/openclaw/stock-assistant.md": _read_doc(self.repo_root / "docs" / "openclaw" / "stock-assistant.md", max_lines=24),
                    "skills/first-principles-check/SKILL.md": _read_doc(self.repo_root / "skills" / "first-principles-check" / "SKILL.md", max_lines=32),
                    "skills/system-audit/SKILL.md": _read_doc(self.repo_root / "skills" / "system-audit" / "SKILL.md", max_lines=32),
                }
            )
        else:
            docs.update(
                {
                    "projects/dual-bot-architecture.md": _read_doc(self.repo_root / "projects" / "dual-bot-architecture.md", max_lines=32),
                    "CLAUDE.md": _read_doc(self.repo_root / "CLAUDE.md", max_lines=32),
                }
            )
        return docs

    def _worker_doc_path(self, task_type: str) -> Path:
        if task_type == "ads":
            return self.repo_root / "docs" / "openclaw" / "ads-assistant.md"
        if task_type == "stock":
            return self.repo_root / "docs" / "openclaw" / "stock-assistant.md"
        return self.repo_root / "docs" / "openclaw" / "dispatch-role.md"


def _matches(text: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _read_doc(path: Path, max_lines: int = 80) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
        lines = text.splitlines()
        if len(lines) > max_lines:
            return "\n".join(lines[:max_lines] + ["", f"... ({len(lines) - max_lines} more lines omitted)"])
        return text
    except Exception:
        return f"(missing: {path})"
