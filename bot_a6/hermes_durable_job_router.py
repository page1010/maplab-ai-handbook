#!/usr/bin/env python3
"""Deterministic natural-language router for MAPLAB durable jobs.

The router decides locally and stores the full Owner request only in a private
job packet.  DeerFlow receives the sanitized ``deerflow_view`` field, never the
raw request for private-domain work.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
import uuid
from dataclasses import dataclass
from pathlib import Path

try:
    from .hermes_deerflow_bridge import parse_public_query
except ImportError:  # Direct script/gateway execution.
    from hermes_deerflow_bridge import parse_public_query


REPO_ROOT = Path(__file__).resolve().parent.parent
JOB_ROOT = REPO_ROOT / "workbook" / "reviews" / "MAPLAB-DURABLE-JOBS"
LINKED_RECEIPT_ROOT = REPO_ROOT / "workbook" / "reviews" / "A6-HERMES-TASKS"
LONG_RUN_RE = re.compile(
    r"(持續|繼續跑|多跑|多輪|幾輪|直到|跑完|全流程|端到端|交付成果|給我看成果|不要停|別停|"
    r"長時間|深入研究|深度研究|至少\s*\d+\s*個?來源|完成後通知|背景跑|自動接續|反覆優化|"
    r"keep\s+going|until\s+(?:done|complete)|end[- ]to[- ]end)",
    re.IGNORECASE,
)
A8_RE = re.compile(
    r"(\bA8\b|生歌|作歌|歌曲|主題曲|音樂生成|影片|短影音|剪片|成片|YouTube|Shorts|Reels|TikTok|Pinterest)",
    re.IGNORECASE,
)
A8_ACTION_RE = re.compile(r"(做|生|生成|產出|製作|剪|上傳|發布|公開|upload|publish|render)", re.IGNORECASE)
LINE_TRAINING_RE = re.compile(
    r"((LINE|Hermes).{0,24}(訓練|回訓|評估|對話|回覆).{0,24}(輪|持續|繼續|跑|改善|門檻))|"
    r"((多輪|幾輪|持續|繼續|跑).{0,24}(LINE|Hermes).{0,24}(訓練|回訓|評估))",
    re.IGNORECASE,
)
RESEARCH_RE = re.compile(r"(深度研究|多來源|比較研究|工具研究|GitHub|競品研究|查證|研究)", re.IGNORECASE)
SEO_PATROL_RE = re.compile(
    r"(\bSEO\b|搜尋引擎|sitemap|canonical|結構化資料|schema|"
    r"(?:網站|WordPress).{0,18}(?:巡查|巡檢|索引|技術檢查))",
    re.IGNORECASE,
)
SEO_PATROL_ACTION_RE = re.compile(
    r"(巡查|巡檢|檢查|基線|差異|delta|每週|每日|有變化|派工|優化)",
    re.IGNORECASE,
)
SEO_EXTERNAL_MUTATION_RE = re.compile(
    r"((?:改|修改|更新|發布|上線|寫入|刪除|調整|出價|啟用|停用|切換|儲存|部署).{0,32}"
    r"(?:WordPress|\bWP\b|Rank\s*Math|Google\s*Ads|Meta\s*Ads|廣告後台|廣告預算|廣告受眾))|"
    r"((?:WordPress|\bWP\b|Rank\s*Math|Google\s*Ads|Meta\s*Ads|廣告後台|廣告預算|廣告受眾).{0,32}"
    r"(?:改|修改|更新|發布|上線|寫入|刪除|調整|出價|啟用|停用|切換|儲存|部署))",
    re.IGNORECASE,
)
SEO_PRIVATE_SOURCE_RE = re.compile(
    r"(客訊|客資|客戶資料|客戶對話|客戶訊息|客戶紀錄|LINE.{0,12}(?:對話|訊息|紀錄)|瀏覽器登入態|私密資料|私人檔案)",
    re.IGNORECASE,
)
SEO_PRIVATE_USE_RE = re.compile(r"(使用|讀取|分析|匯入|上傳|外送|傳給|交給|提供|同步)", re.IGNORECASE)
SEO_CUSTOMER_SEND_RE = re.compile(
    r"((?:傳送|發送|通知|回覆).{0,20}(?:客戶|客人|LINE))|"
    r"((?:客戶|客人|LINE).{0,20}(?:傳送|發送|通知|回覆))|"
    r"((?:^|[\s，,；;並])(?:傳|發)\s*(?:給)?\s*(?:客戶|客人|LINE))|"
    r"((?:客戶|客人|LINE)\s*(?:傳|發)(?:送)?)|"
    r"(上傳.{0,20}(?:給|到)\s*(?:客戶|客人|LINE))",
    re.IGNORECASE,
)
PRIVATE_THIRD_PARTY_EGRESS_RE = re.compile(
    r"(OpenRouter|DeerFlow|第三方|外部模型|雲端模型|public\s+research\s+provider)",
    re.IGNORECASE,
)
SMALL_TALK_RE = re.compile(r"^\s*(你好|哈囉|hello|hi|謝謝|thanks|在嗎)[！!。.]?\s*$", re.IGNORECASE)
FORBIDDEN_DURABLE_RE = re.compile(
    r"(下單|買入|賣出|轉帳|匯款|券商|broker|刪除|rm\s|sudo|"
    r"token|secret|\.env|密鑰|金鑰|密碼|cookie|"
    r"(?:自動|直接).{0,12}(?:傳送|發送).{0,12}(?:客戶|LINE)|"
    r"(?:傳送|發送).{0,12}(?:客戶|LINE).{0,12}(?:不用|不需).{0,8}(?:確認|審核))",
    re.IGNORECASE,
)
MEDIA_PLATFORM_RE = re.compile(r"(YouTube|Shorts|TikTok|Instagram|\bIG\b|Pinterest|Facebook|\bFB\b)", re.IGNORECASE)
PUBLICATION_RE = re.compile(r"(發布|公開|publish)", re.IGNORECASE)
TERMINAL_STATES = {"OWNER_REVIEW", "BLOCKED", "FAILED", "COMPLETED"}


@dataclass(frozen=True)
class DurableIntent:
    job_type: str
    data_class: str
    adapter: str
    reason: str


def classify_durable_intent(text: str) -> DurableIntent | None:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized or SMALL_TALK_RE.match(normalized):
        return None
    if LINE_TRAINING_RE.search(normalized):
        return DurableIntent(
            job_type="hermes-line-training",
            data_class="private-local-only",
            adapter="hermes-line-training-supervisor",
            reason="LINE/Hermes multi-round training goal",
        )
    if A8_RE.search(normalized) and (A8_ACTION_RE.search(normalized) or LONG_RUN_RE.search(normalized)):
        return DurableIntent(
            job_type="a8-production",
            data_class="private-local-only",
            adapter="codex-heartbeat+a8-domain-worker",
            reason="A8 media workflow spans generation, QA and delivery",
        )
    if SEO_PATROL_RE.search(normalized) and (
        SEO_PATROL_ACTION_RE.search(normalized) or LONG_RUN_RE.search(normalized)
    ):
        return DurableIntent(
            job_type="seo-patrol",
            data_class="public",
            adapter="codex-heartbeat+maplab-seo-coach-patrol",
            reason="SEO patrol requires a material-delta gate and bounded local follow-up",
        )
    if RESEARCH_RE.search(normalized) and (LONG_RUN_RE.search(normalized) or len(RESEARCH_RE.findall(normalized)) > 1):
        _query, rejection = parse_public_query(f"/research-public {normalized}")
        if not rejection:
            return DurableIntent(
                job_type="public-research",
                data_class="public",
                adapter="deerflow-public-research",
                reason="multi-source public research benefits from DeerFlow",
            )
    if LONG_RUN_RE.search(normalized):
        return DurableIntent(
            job_type="general-agent",
            data_class="private-local-only",
            adapter="codex-heartbeat",
            reason="Owner explicitly requested sustained or multi-round completion",
        )
    return None


def validate_durable_request(text: str, intent: DurableIntent) -> str | None:
    """Reject dangerous scope expansion before a durable job is created."""

    if FORBIDDEN_DURABLE_RE.search(text or ""):
        return "持久任務含交易、刪除、憑證或未核准對客發送要求，已 fail closed"
    if intent.job_type in {"seo-patrol", "general-agent"} and SEO_EXTERNAL_MUTATION_RE.search(text or ""):
        return "SEO 持久任務含未核准外部寫入；只允許公開讀取、repo receipt 與 approval-ready proposal"
    if SEO_CUSTOMER_SEND_RE.search(text or ""):
        return "持久任務不得對客或 LINE 發訊，已 fail closed"
    if SEO_PRIVATE_SOURCE_RE.search(text or "") and PRIVATE_THIRD_PARTY_EGRESS_RE.search(text or ""):
        return "持久任務不得把客訊或私密資料交給第三方模型，已 fail closed"
    if (
        intent.job_type == "seo-patrol"
        and SEO_PRIVATE_SOURCE_RE.search(text or "")
        and SEO_PRIVATE_USE_RE.search(text or "")
    ):
        return "SEO patrol 只接受公開資料；客訊或私密資料使用或外送已 fail closed"
    if intent.job_type == "a8-production" and PUBLICATION_RE.search(text or "") and not MEDIA_PLATFORM_RE.search(text or ""):
        return "公開發布未指定受控影音平台；先只允許生成、QA 與審核包"
    return None


def infer_authorization(text: str, intent: DurableIntent) -> dict:
    authorization = {
        "research": intent.job_type == "public-research" or bool(RESEARCH_RE.search(text)),
        "local_generation": bool(re.search(r"(生歌|作歌|生成|製作|成片|render)", text, re.IGNORECASE)),
        "third_party_generation": bool(re.search(r"(生歌|音樂生成|Suno|Canva|Google\s*Vids)", text, re.IGNORECASE)),
        "draft_upload": bool(re.search(r"(上傳|upload).{0,20}(YouTube|TikTok|Instagram|Pinterest)|(?:YouTube|TikTok|Instagram|Pinterest).{0,20}(上傳|upload)", text, re.IGNORECASE)),
        "publication": bool(re.search(r"(發布|公開|publish).{0,20}(YouTube|TikTok|Instagram|Pinterest)|(?:YouTube|TikTok|Instagram|Pinterest).{0,20}(發布|公開|publish)", text, re.IGNORECASE)),
        "offline_training": intent.job_type == "hermes-line-training",
        "public_site_read": intent.job_type == "seo-patrol",
        "repo_report_write": intent.job_type == "seo-patrol",
        "external_system_write": False,
        "private_third_party_egress": False,
        "wordpress_write": False,
        "ads_write": False,
        "rank_math_write": False,
        "private_data_egress": False,
        "customer_send": False,
    }
    return authorization


def acceptance_for(intent: DurableIntent, authorization: dict) -> list[str]:
    if intent.job_type == "a8-production":
        requirements = [
            "owner-viewable song/video artifact with hash",
            "full playback and visual QA receipt",
            "resume prompt and state history",
        ]
        if authorization.get("draft_upload") or authorization.get("publication"):
            requirements.append("YouTube/platform URL plus visibility readback")
        return requirements
    if intent.job_type == "hermes-line-training":
        return [
            "round receipts and lesson delta",
            "pass rate and unsupported-price count",
            "continue toward seven consecutive runs >= 0.85 with zero unsupported prices",
        ]
    if intent.job_type == "public-research":
        return ["research artifact", "source URLs", "DeerFlow/config/provider receipt"]
    if intent.job_type == "seo-patrol":
        return [
            "public baseline plus previous material-delta comparison",
            "one bounded SEO artifact tied to the active Task Card",
            "external_writes=0, customer_send=0, private_third_party_egress=0",
            "durable receipt and resume prompt",
        ]
    return ["artifact or live readback matching the Owner goal", "durable receipt", "resume prompt"]


def _private_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.chmod(0o600)
    os.replace(temporary, path)
    path.chmod(0o600)


def write_job(job_dir: Path, job: dict) -> None:
    job["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    _private_write(job_dir / "job.json", json.dumps(job, ensure_ascii=False, indent=2) + "\n")
    lines = [
        f"# {job['job_id']}",
        "",
        f"- Type: `{job['job_type']}`",
        f"- State: `{job['state']}`",
        f"- Adapter: `{job['adapter']}`",
        f"- Current phase: `{job['current_phase']}`",
        f"- Next: {job['next_bounded_action']}",
        f"- Receipt: `{job_dir / 'job.json'}`",
        "",
        "## Resume Prompt",
        "",
        job["resume_prompt"],
    ]
    _private_write(job_dir / "job.md", "\n".join(lines) + "\n")


def read_job(job_path: str | Path) -> tuple[Path, dict]:
    path = Path(job_path).resolve()
    root = JOB_ROOT.resolve()
    if path.name != "job.json" or path.parent.parent != root or not path.parent.name.startswith("MAPJOB-"):
        raise ValueError("invalid durable job path")
    return path, json.loads(path.read_text(encoding="utf-8"))


def transition_job(job_path: str | Path, state: str, *, result: dict | None = None, next_action: str | None = None) -> dict:
    path, job = read_job(job_path)
    previous = job.get("state")
    job["state"] = state
    job["last_result"] = result
    if next_action is not None:
        job["next_bounded_action"] = next_action
    job.setdefault("history", []).append(
        {
            "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "from": previous,
            "to": state,
            "reason": (result or {}).get("reason") or (result or {}).get("status") or "bounded action update",
        }
    )
    write_job(path.parent, job)
    job["job_path"] = str(path)
    return job


def create_durable_job(
    request: str,
    intent: DurableIntent,
    owner_user_id: int,
    *,
    chat_id: int | None = None,
    chat_type: str | None = None,
) -> dict:
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    job_id = f"MAPJOB-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    job_dir = JOB_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    job_dir.chmod(0o700)
    authorization = infer_authorization(request, intent)
    sanitized_view = {
        "job_type": intent.job_type,
        "state": "ACCEPTED",
        "goal_class": intent.reason,
        "acceptance_count": len(acceptance_for(intent, authorization)),
        "data_class": intent.data_class,
    }
    next_action = {
        "a8-production": "Codex heartbeat reads the A8 SOP and active Task Card, then executes the first safe unfinished phase.",
        "hermes-line-training": "Start the fixed local multi-round training supervisor against the protected local cache.",
        "public-research": "Start the hardened DeerFlow public-research worker with the current request only.",
        "seo-patrol": "Read the active A2 SEO Task Card and maplab-seo-coach-patrol Skill, then execute exactly one public-safe bounded action; no material delta means NO_DELTA_NO_DISPATCH.",
        "general-agent": "Codex heartbeat selects and executes the first bounded action from the Owner goal.",
    }[intent.job_type]
    requester_channel = "telegram" if chat_id is not None else "local-heartbeat"
    notification_policy = "telegram-terminal" if chat_id is not None else "none"
    job = {
        "schema_version": "maplab.durable-job.v1",
        "job_id": job_id,
        "created_at": now,
        "updated_at": now,
        "requester": {"channel": requester_channel, "owner_user_id": owner_user_id, "chat_id": chat_id, "chat_type": chat_type},
        "notification_policy": notification_policy,
        "request": request[:4000],
        "request_sha256": hashlib.sha256(request.encode("utf-8")).hexdigest(),
        "job_type": intent.job_type,
        "adapter": intent.adapter,
        "route_reason": intent.reason,
        "state": "ACCEPTED",
        "data_class": intent.data_class,
        "deerflow_view": sanitized_view,
        "authorization": authorization,
        "acceptance": acceptance_for(intent, authorization),
        "attempt": 0,
        "max_attempts": 3 if intent.job_type == "seo-patrol" else 12,
        "wall_deadline": None,
        "current_phase": "sensor-delta-intake" if intent.job_type == "seo-patrol" else "intake",
        "last_result": None,
        "next_bounded_action": next_action,
        "objective_metrics_before": {},
        "objective_metrics_after": {},
        "owner_acceptance_delta": 0,
        "unlocked_next_action": next_action,
        "attempt_consumed": False,
        "artifacts": [],
        "history": [{"at": now, "from": None, "to": "ACCEPTED", "reason": intent.reason}],
        "resume_prompt": (
            "我是 MAPLAB durable-job executor。先讀 CURRENT_STATUS.md、pitfalls.md、"
            f".agents/skills/maplab-durable-job-orchestrator/SKILL.md 與 {job_dir / 'job.json'}。"
            + (
                "SEO任務另讀handoff/tasks/T-A2-HERMES-SEO-COACH-001.md與"
                ".agents/skills/maplab-seo-coach-patrol/SKILL.md。"
                if intent.job_type == "seo-patrol"
                else ""
            )
            + "只執行 next_bounded_action；驗證 artifact/live surface 後更新 state、history、next action。"
            "已有 authorization 不要重問；新 spend、私密資料新第三方、公開發布或不可逆動作才進 OWNER_REVIEW。"
        ),
    }
    job["job_path"] = str(job_dir / "job.json")
    write_job(job_dir, job)
    return job


def telegram_job_summary(job: dict) -> str:
    authorization = job.get("authorization") or {}
    authorized = [name for name, enabled in authorization.items() if enabled]
    return "\n".join(
        [
            "【hermes】已自動建立 durable job，不用輸入任何研究指令。",
            f"任務：{job['job_id']}",
            f"路由：{job['job_type']} → {job['adapter']}",
            f"狀態：{job['state']}",
            f"已承接授權：{'、'.join(authorized) if authorized else '本機可逆步驟'}",
            f"下一步：{job['next_bounded_action']}",
            f"receipt：{job['job_path']}",
        ]
    )


def _reconcile_linked_receipt(job_path: Path, job: dict) -> dict:
    """Project a worker receipt into the canonical job without exposing payload."""

    linked = job.get("linked_receipt")
    if not linked or job.get("state") not in {"ACCEPTED", "RUNNING", "WAITING_EXTERNAL"}:
        return job
    receipt_path = Path(str(linked)).resolve()
    linked_root = LINKED_RECEIPT_ROOT.resolve()
    if (
        receipt_path.name != "receipt.json"
        or receipt_path.parent.parent != linked_root
        or not receipt_path.parent.name.startswith("DFR-")
    ):
        return job
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return job
    if (
        receipt.get("action") != "deerflow-public-research"
        or receipt.get("parent_job_id") != job.get("job_id")
        or receipt.get("request_sha256") != job.get("request_sha256")
    ):
        return job
    status = receipt.get("status")
    if status not in {"completed", "failed"}:
        return job
    artifact_path: Path | None = None
    if status == "completed":
        artifact_value = receipt.get("artifact_path")
        artifact_sha256 = receipt.get("artifact_sha256")
        if not isinstance(artifact_value, str) or not isinstance(artifact_sha256, str):
            return job
        artifact_path = Path(artifact_value).resolve()
        if artifact_path.parent != receipt_path.parent or not artifact_path.is_file():
            return job
        if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != artifact_sha256:
            return job
    artifacts = list(job.get("artifacts") or [])
    if artifact_path is not None:
        artifacts.append(
            {
                "path": str(artifact_path),
                "sha256": receipt.get("artifact_sha256"),
                "readback": "hash-verified-pending-owner-notification",
            }
        )
    job["artifacts"] = artifacts
    job["state"] = "COMPLETED" if status == "completed" else "FAILED"
    job["current_phase"] = "terminal"
    job["last_result"] = {
        "status": status,
        "reason": receipt.get("reason"),
        "answer_preview": receipt.get("answer_preview") if job.get("data_class") == "public" else None,
        "linked_receipt": str(receipt_path),
    }
    job["next_bounded_action"] = "Notify the Owner with the verified artifact and receipt."
    job.setdefault("history", []).append(
        {
            "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "from": "WAITING_EXTERNAL",
            "to": job["state"],
            "reason": f"linked worker {status}",
        }
    )
    write_job(job_path.parent, job)
    return job


def pending_durable_notifications() -> list[dict]:
    notifications: list[dict] = []
    if not JOB_ROOT.is_dir():
        return notifications
    for job_path in sorted(JOB_ROOT.glob("MAPJOB-*/job.json")):
        try:
            job = json.loads(job_path.read_text(encoding="utf-8"))
            job = _reconcile_linked_receipt(job_path, job)
        except (OSError, ValueError, TypeError):
            continue
        if job.get("state") not in TERMINAL_STATES:
            continue
        if job.get("notification_policy") == "none":
            continue
        marker_path = job_path.parent / "notification.json"
        try:
            marker = json.loads(marker_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            marker = {}
        if marker.get("state") == job.get("state") and marker.get("job_updated_at") == job.get("updated_at"):
            continue
        chat_id = (job.get("requester") or {}).get("chat_id")
        if chat_id is None:
            continue
        job["job_path"] = str(job_path)
        notifications.append({"job": job, "job_path": str(job_path), "chat_id": chat_id})
    return notifications


def durable_completion_summary(job: dict) -> str:
    lines = [
        f"【hermes】持久任務 {job.get('state')}",
        f"任務：{job.get('job_id')}",
        f"類型：{job.get('job_type')}",
    ]
    result = job.get("last_result") or {}
    if result.get("reason"):
        lines.append(f"原因：{result['reason']}")
    if result.get("answer_preview"):
        lines.extend(["成果摘要：", str(result["answer_preview"])[:2200]])
    artifacts = job.get("artifacts") or []
    if artifacts:
        lines.append(f"成果：{artifacts[-1].get('path') or artifacts[-1].get('url')}")
    if job.get("state") == "OWNER_REVIEW":
        lines.append("已到真正需要你判斷的 Owner gate；不是因 session 結束而停。")
    lines.append(f"receipt：{job.get('job_path')}")
    return "\n".join(lines)


def mark_durable_notified(job_path: str | Path, message_id: int | None = None) -> None:
    path, job = read_job(job_path)
    _private_write(
        path.parent / "notification.json",
        json.dumps(
            {
                "status": "sent",
                "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "job_id": job.get("job_id"),
                "state": job.get("state"),
                "job_updated_at": job.get("updated_at"),
                "job_path": str(path),
                "telegram_message_id": message_id,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )


if __name__ == "__main__":
    raise SystemExit("This module is called by the Hermes executor; it has no free-form CLI.")
