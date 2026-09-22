#!/usr/bin/env python3
"""Governed local task executor for the Owner-only A6 Hermes gateway.

This module deliberately exposes a small capability allowlist.  It never accepts
shell text from Telegram, never reads secret files, and writes a durable task and
receipt for every accepted or rejected request.
"""
from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

try:
    from .hermes_deerflow_bridge import (
        DEERFLOW_PYTHON,
        is_public_research_command,
        parse_public_query,
    )
    from .hermes_durable_job_router import (
        classify_durable_intent,
        create_durable_job,
        telegram_job_summary,
        transition_job,
        validate_durable_request,
        write_job,
    )
    from . import quote_calc
except ImportError:  # Direct launchd/script execution.
    from hermes_deerflow_bridge import (
        DEERFLOW_PYTHON,
        is_public_research_command,
        parse_public_query,
    )
    from hermes_durable_job_router import (
        classify_durable_intent,
        create_durable_job,
        telegram_job_summary,
        transition_job,
        validate_durable_request,
        write_job,
    )
    import quote_calc


REPO_ROOT = Path(__file__).resolve().parent.parent
TASK_ROOT = REPO_ROOT / "workbook" / "reviews" / "A6-HERMES-TASKS"
MAX_OUTPUT_CHARS = 12_000
DENY_PATTERN = re.compile(
    r"(下單|買入|賣出|轉帳|匯款|發布|publish|wordpress|"
    r"token|密鑰|secret|\.env|刪除|rm\s|sudo|券商|broker)",
    re.IGNORECASE,
)
SCHEDULE_MUTATION_PATTERN = re.compile(
    r"((修改|改動|重啟|重跑|啟動|停用|關閉|載入|卸載|刪除|modify|restart|rerun|start|stop|load|unload).{0,20}"
    r"(launchd|launchctl|排程|schedule|cron))|"
    r"(launchctl.{0,20}(bootstrap|bootout|kickstart|enable|disable))",
    re.IGNORECASE,
)
PYTHON = str(Path(sys.executable).resolve())
DEERFLOW_BRIDGE = REPO_ROOT / "bot_a6" / "hermes_deerflow_bridge.py"
RESEARCH_STATUS_RE = re.compile(
    r"^\s*(?:/research-status|research-status|研究狀態\s*[：:]?)\s+"
    r"(DFR-\d{8}-\d{6}-[0-9a-f]{6})\s*$",
    re.IGNORECASE,
)
LINE_TRAINING_SUPERVISOR = REPO_ROOT / "scripts" / "hermes_line_training_supervisor.py"
LINE_SUPERVISOR_CHUNK = ("--max-rounds", "2", "--max-seconds", "900", "--batch", "5")


@dataclass(frozen=True)
class Action:
    name: str
    argv: tuple[str, ...]
    timeout: int
    description: str


ACTIONS = {
    "runtime-status": Action(
        "runtime-status",
        (PYTHON, str(REPO_ROOT / "bot_a6" / "hermes_capability_runtime.py"), "capabilities"),
        20,
        "讀取 A6 Hermes 當前能力、provider、記憶與 launchd 狀態",
    ),
    "signal-status": Action(
        "signal-status",
        (PYTHON, str(REPO_ROOT / "bot_a6" / "hermes_capability_runtime.py"), "signal-status"),
        20,
        "讀取 16:20 動能名單的 launchd 與最新報告實況",
    ),
    "repo-status": Action(
        "repo-status",
        ("git", "status", "--short"),
        20,
        "讀取 MAPLAB repo 的未提交變更摘要",
    ),
    "recent-commits": Action(
        "recent-commits",
        ("git", "log", "-8", "--oneline", "--decorate"),
        20,
        "讀取最近八筆 commit",
    ),
    "a6-self-test": Action(
        "a6-self-test",
        (
            str(REPO_ROOT / "bot" / "venv" / "bin" / "python3"),
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_hermes*.py",
            "-v",
        ),
        90,
        "執行 A6 Hermes 治理式 executor 自我測試",
    ),
    "deerflow-status": Action(
        "deerflow-status",
        (PYTHON, str(DEERFLOW_BRIDGE), "status"),
        20,
        "讀取 embedded DeerFlow pin、隔離設定與 provider gate，不執行研究",
    ),
    "deerflow-public-research": Action(
        "deerflow-public-research",
        (str(DEERFLOW_PYTHON), str(DEERFLOW_BRIDGE), "supervise"),
        600,
        "以隔離 one-shot worker 研究單一公開／合成問題",
    ),
    "deerflow-job-status": Action(
        "deerflow-job-status",
        (PYTHON, str(DEERFLOW_BRIDGE), "status"),
        20,
        "讀取指定 DeerFlow job 的 owner-only receipt",
    ),

    "general-chat": Action(
        "general-chat",
        (PYTHON, str(REPO_ROOT / "bot_a6" / "hermes_telegram_gateway.py"), "chat-fallback"),
        30,
        "透過模型進行自由形式的文字回覆（僅限 Owner 私聊，仍會產生 receipt）",
    ),
    "quote-intake": Action(
        "quote-intake",
        ("/usr/bin/true",),
        10,
        "受理報價需求：原文建案卷、轉交 A0 代產，本動作不產生任何價格",
    ),
    "quote-estimate": Action(
        "quote-estimate",
        ("/usr/bin/true",),
        20,
        "報價試算：以有 source 的價目表做零 LLM 算術，產出毛利率與件數（內部試算，不對客）",
    ),
}

# hermes 的 fail-closed 紅線第一條就是不報價。但「不報價」不等於「不回話」——
# 2026-08-27 與 09-21 兩次 Owner 在這個對話框要報價,都只換到一句拒絕。
# 這個動作只做三件事:把需求原文建成案卷、記下時間、回一句「已受理,交 A0 代產」。
# 用 2026-08-27 與 09-21 兩則真實被拒的 Owner 原話當回歸素材:8/27 那則只寫
# 「預算20000」,第一版正則抓不到它,所以「預算+金額」和「報 N 人」要獨立成條。
QUOTE_INTENT_RE = re.compile(
    # 「報個價」「報一下價」中間會夾字,只寫「報價」會漏掉(2026-09-22 實測)。
    r"(報.{0,3}價|估價|開價|多少錢|抓預算|毛利|"
    r"預算\s*\d{3,}|預算.{0,12}(反推|抓|做|配|內)|"
    r"\d{3,}\s*(塊|元)|每人\s*\d+|人數\s*\d+|報\s*\d+\s*人)",
)
QUOTE_INTAKE_ROOT = Path.home() / ".maplab" / "quote_intake"

ALIASES = {
    "runtime-status": (
        "runtime-status",
        "hermesruntime狀態",
        "hermes狀態",
        "gateway狀態",
        "a6狀態",
        "執行環境狀態",
    ),
    "signal-status": (
        "signal-status",
        "動能名單",
        "強股故事",
        "strong-stock-story",
        "16:20名單",
        "訊號狀態",
    ),
    "repo-status": ("repo-status", "git status", "repo狀態", "專案狀態", "未提交變更"),
    "recent-commits": ("recent-commits", "最近commit", "最近提交", "版本紀錄"),
    "a6-self-test": ("a6-self-test", "測試a6", "a6測試", "測試hermes", "自我測試"),
    "deerflow-status": ("deerflow-status", "deerflow狀態", "研究引擎狀態"),
    "general-chat": (
        "一般聊天",
        "自由對話",
        "聊天",
        "chat",
        "general-chat",
        "閒聊",
    ),
}


def classify(request: str) -> tuple[str | None, str | None]:
    if is_public_research_command(request):
        _query, rejection = parse_public_query(request)
        if rejection:
            return None, rejection
        return "deerflow-public-research", None
    if RESEARCH_STATUS_RE.match(request or ""):
        return "deerflow-job-status", None
    durable_intent = classify_durable_intent(request)
    if durable_intent is not None:
        durable_rejection = validate_durable_request(request, durable_intent)
        if durable_rejection:
            return None, durable_rejection
        return "durable-job", None
    normalized = re.sub(r"\s+", "", request).lower()
    if DENY_PATTERN.search(request) or SCHEDULE_MUTATION_PATTERN.search(request):
        return None, "涉及禁止或高風險能力，已 fail closed"
    for action_name, aliases in ALIASES.items():
        if any(re.sub(r"\s+", "", alias).lower() in normalized for alias in aliases):
            return action_name, None
    if QUOTE_INTENT_RE.search(request or ""):
        # 人數與預算都問到了就直接試算（Owner msg 5774：沒人有額度時 a6 要能幫 Owner 算）；
        # 缺任一項就退回受理，由 hermes 照經驗庫把缺的那幾題問回來，不猜。
        facts = quote_calc.parse_brief(request or "")["facts"]
        if facts.get("pax") and facts.get("budget"):
            return "quote-estimate", None
        return "quote-intake", None
    return None, "不在目前的安全動作白名單"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    path.chmod(0o600)


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload)
    path.chmod(0o600)


def _write_receipt_markdown(task_dir: Path, receipt: dict) -> None:
    summary = [
        f"# {receipt['task_id']}",
        "",
        f"- 狀態：`{receipt['status']}`",
        f"- 動作：`{receipt.get('action') or 'none'}`",
        f"- 建立：`{receipt['created_at']}`",
        f"- 收據：`{task_dir / 'receipt.json'}`",
    ]
    if receipt.get("reason"):
        summary.append(f"- 原因：{receipt['reason']}")
    _write_text(task_dir / "receipt.md", "\n".join(summary) + "\n")


def _deerflow_provider(openrouter_key: str | None) -> tuple[str | None, str | None, dict[str, str]]:
    # 2026-09-21 Owner「hermes 就是 ollama 的接班」：本機 Ollama 已於 9/4 卸載，
    # 預設引擎改為 Hermes 免費鏈（公開資料研究；Owner 9/12 msg 5228 已接受雲端隱私取捨）。
    provider = os.environ.get("HERMES_DEERFLOW_PROVIDER", "hermes").strip().lower()
    child_env: dict[str, str] = {}
    if provider == "hermes":
        # bridge 會自行從 Hermes maplabcloud 設定載入金鑰；若呼叫端已有則沿用
        if openrouter_key:
            child_env["OPENROUTER_API_KEY"] = openrouter_key
        return provider, None, child_env
    if provider == "local":
        return provider, None, child_env
    if provider != "openrouter":
        return None, "未知的 HERMES_DEERFLOW_PROVIDER，已 fail closed", child_env
    if os.environ.get("HERMES_DEERFLOW_OPENROUTER_POLICY_VERIFIED") != "1":
        return None, "OpenRouter ZDR/data-collection 帳戶政策尚未 authenticated readback", child_env
    if os.environ.get("HERMES_DEERFLOW_ALLOW_PAID") != "1":
        return None, "ZDR 相容 route 為付費路由，尚無 Owner spend approval", child_env
    if not openrouter_key:
        return None, "OpenRouter key unavailable", child_env
    child_env = {
        "OPENROUTER_API_KEY": openrouter_key,
        "HERMES_DEERFLOW_OPENROUTER_POLICY_VERIFIED": "1",
        "HERMES_DEERFLOW_ALLOW_PAID": "1",
    }
    return provider, None, child_env


def _start_deerflow_job(task_dir: Path, task: dict, query: str, openrouter_key: str | None) -> dict:
    provider, rejection, provider_env = _deerflow_provider(openrouter_key)
    if rejection or provider is None:
        receipt = {
            **task,
            "status": "rejected",
            "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "reason": rejection,
            "network_calls": 0,
        }
        _write_json(task_dir / "receipt.json", receipt)
        _write_receipt_markdown(task_dir, receipt)
        return receipt

    _write_text(task_dir / "question.txt", query + "\n")
    receipt = {
        **task,
        "status": "accepted",
        "provider": provider,
        "input_classification": "public",
        "network_calls": 0,
        "next": "background one-shot worker will update this receipt",
    }
    # The supervisor reads this before starting its isolated model subprocess.
    _write_json(task_dir / "receipt.json", receipt)
    _write_receipt_markdown(task_dir, receipt)
    supervisor_env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
        "LANG": "zh_TW.UTF-8",
        "PYTHONUNBUFFERED": "1",
        **provider_env,
    }
    log_fd = os.open(task_dir / "supervisor.log", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        subprocess.Popen(
            (
                str(DEERFLOW_PYTHON),
                str(DEERFLOW_BRIDGE),
                "supervise",
                "--task-dir",
                str(task_dir),
                "--provider",
                provider,
            ),
            cwd=REPO_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=log_fd,
            stderr=log_fd,
            env=supervisor_env,
            start_new_session=True,
            close_fds=True,
        )
    except OSError as exc:
        receipt.update(
            {
                "status": "failed",
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "reason": f"worker start failed: {type(exc).__name__}",
            }
        )
        _write_json(task_dir / "receipt.json", receipt)
        _write_receipt_markdown(task_dir, receipt)
    finally:
        os.close(log_fd)
    return receipt


def _start_durable_public_research(job: dict, request: str, openrouter_key: str | None) -> tuple[dict, dict]:
    query, rejection = parse_public_query(f"/research-public {request}")
    if rejection or query is None:
        job = transition_job(
            job["job_path"],
            "FAILED",
            result={"status": "failed", "reason": rejection or "public research classifier rejected request"},
            next_action="Review the local classifier receipt; no network call was made.",
        )
        return job, {"status": "failed", "reason": rejection, "network_calls": 0}

    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    task_id = f"DFR-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    task_dir = TASK_ROOT / task_id
    task_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    task_dir.chmod(0o700)
    task = {
        "schema_version": 4,
        "task_id": task_id,
        "created_at": now,
        "request": "[redacted-auto-routed-public-research]",
        "request_sha256": hashlib.sha256(request.encode("utf-8")).hexdigest(),
        "request_chars": len(request),
        "requester": job["requester"],
        "action": "deerflow-public-research",
        "policy": "public-research-auto-route-v2",
        "parent_job_id": job["job_id"],
    }
    _write_json(task_dir / "task.json", task)
    research_receipt = _start_deerflow_job(task_dir, task, query, openrouter_key)
    job_path = job["job_path"]
    job = transition_job(
        job_path,
        "WAITING_EXTERNAL" if research_receipt.get("status") == "accepted" else "FAILED",
        result={
            "status": research_receipt.get("status"),
            "reason": research_receipt.get("reason"),
            "worker_task_id": task_id,
        },
        next_action=(
            "Poll the linked DeerFlow receipt and deliver its verified artifact."
            if research_receipt.get("status") == "accepted"
            else "Review the DeerFlow launch receipt; no retry until its gate is corrected."
        ),
    )
    job["linked_receipt"] = str(task_dir / "receipt.json")
    # Persist the link after the state transition; the worker owns only its DFR receipt.
    write_job(Path(job_path).parent, job)
    return job, research_receipt


def _start_durable_job(
    request: str,
    owner_user_id: int,
    *,
    chat_id: int | None,
    chat_type: str | None,
    openrouter_key: str | None,
) -> dict:
    intent = classify_durable_intent(request)
    if intent is None:
        raise ValueError("durable job requested without a durable intent")
    rejection = validate_durable_request(request, intent)
    if rejection:
        raise ValueError(rejection)
    job = create_durable_job(request, intent, owner_user_id, chat_id=chat_id, chat_type=chat_type)
    worker_receipt: dict | None = None
    if intent.job_type == "public-research":
        job, worker_receipt = _start_durable_public_research(job, request, openrouter_key)
    elif intent.job_type == "hermes-line-training" and LINE_TRAINING_SUPERVISOR.is_file():
        log_path = Path(job["job_path"]).parent / "supervisor.log"
        log_fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            process = subprocess.Popen(
                (
                    PYTHON,
                    str(LINE_TRAINING_SUPERVISOR),
                    "--job-path",
                    job["job_path"],
                    *LINE_SUPERVISOR_CHUNK,
                ),
                cwd=REPO_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=log_fd,
                stderr=log_fd,
                env={
                    "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
                    "LANG": "zh_TW.UTF-8",
                    "PYTHONUNBUFFERED": "1",
                    "HERMES_LINE_PROVIDER": "local-only",
                    **(
                        {"HERMES_LINE_DATA_ROOT": os.environ["HERMES_LINE_DATA_ROOT"]}
                        if os.environ.get("HERMES_LINE_DATA_ROOT")
                        else {}
                    ),
                },
                start_new_session=True,
                close_fds=True,
            )
            worker_receipt = {"status": "running", "pid": process.pid, "network_calls": 0}
            job = transition_job(
                job["job_path"],
                "RUNNING",
                result=worker_receipt,
                next_action="The local-only bounded LINE supervisor is running; poll its job receipt.",
            )
        except OSError as exc:
            worker_receipt = {"status": "failed", "reason": f"supervisor start failed: {type(exc).__name__}", "network_calls": 0}
            job = transition_job(job["job_path"], "FAILED", result=worker_receipt, next_action="Inspect supervisor.log and retry a bounded local round.")
        finally:
            os.close(log_fd)
    else:
        queued_result = {"status": "queued-for-heartbeat", "network_calls": 0}
        if intent.job_type == "seo-patrol":
            queued_result.update(
                {
                    "external_writes": 0,
                    "customer_send": 0,
                    "private_third_party_egress": 0,
                    "attempt_consumed": False,
                    "owner_acceptance_delta": 0,
                }
            )
        job = transition_job(
            job["job_path"],
            "RUNNING",
            result=queued_result,
            next_action=job["next_bounded_action"],
        )
    return {
        "schema_version": 1,
        "task_id": job["job_id"],
        "status": "accepted" if job["state"] in {"RUNNING", "WAITING_EXTERNAL"} else "failed",
        "action": "durable-job",
        "policy": "natural-language-durable-route-v2",
        "job_type": job["job_type"],
        "job_state": job["state"],
        "receipt_path": job["job_path"],
        "summary": telegram_job_summary(job) if chat_id is not None else None,
        "notification_policy": job.get("notification_policy"),
        "worker": worker_receipt,
    }


def _deerflow_job_readback(task_id: str) -> dict:
    path = TASK_ROOT / task_id / "receipt.json"
    if not path.is_file() or path.parent.parent.resolve() != TASK_ROOT.resolve():
        return {"status": "missing", "task_id": task_id, "reason": "DeerFlow job receipt not found"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "failed", "task_id": task_id, "reason": "DeerFlow job receipt unreadable"}
    if payload.get("action") != "deerflow-public-research":
        return {"status": "rejected", "task_id": task_id, "reason": "receipt is not a DeerFlow research job"}
    return payload


def _quote_estimate_output(request: str, task_id: str, now: str) -> str:
    """報價試算的文字輸出。每個數字都出自 quote_calc(有 source 的價目表),模型不參與算術。"""
    brief = quote_calc.parse_brief(request)
    facts = brief["facts"]
    pax = int(facts["pax"])
    budget = float(facts["budget"])
    target = facts.get("target_margin")
    book = quote_calc.load_price_book()
    ceiling = quote_calc.menu_sum_ceiling(book)

    lines = [
        "【hermes 報價試算・內部用,不得直接發給客人】",
        f"讀到的需求:{pax} 人／預算 {budget:.0f} 元"
        + (f"／目標毛利 {target:.0%}" if target else "")
        + (f"／日期 {facts['event_date']}" if facts.get("event_date") else ""),
        "",
        f"逐項加總的毛利率天花板:{ceiling['ceiling_rate']:.1%}(最高毛利品項={ceiling['ceiling_item']})。"
        "砍件數不會改變毛利率。",
    ]
    if target and target > ceiling["ceiling_rate"]:
        cost_cap = quote_calc.cost_budget_for_margin(budget, float(target))
        lines += [
            f"→ 目標 {target:.0%} 高於天花板,逐項加總做不到。唯一路徑=整案價收滿 {budget:.0f},"
            f"食材成本壓在 {cost_cap:.0f} 元以內。",
            "→ 換報價法屬對外定價決定,要 Owner 拍板,我不自裁。",
        ]

    matched = [
        plan
        for plan in quote_calc.reference_plans(book)
        if plan.get("pax") == pax and plan.get("package_price") in (None, budget)
    ]
    if matched:
        lines += ["", f"同規模算過的配置({len(matched)} 組),以下為程式重算結果:"]
        for plan in matched:
            result = quote_calc.run_reference_plan(plan["name"], book)
            lines += [
                "",
                f"[{plan['name']}] {plan['label']}(來源 {plan['source']})",
                quote_calc.render(result),
            ]
    else:
        lines += [
            "",
            "這個規模我沒有算過的既有配置。菜色要你或 Owner 先定(選菜不是我的權責),"
            "定好我就用 scale 指令放大到剛好達標,連風險一起報。",
        ]

    if brief["missing"]:
        lines += ["", "還沒問到的必要事實:" + "、".join(brief["missing"])]
    lines += [
        "",
        f"案卷:{QUOTE_INTAKE_ROOT / (task_id + '.md')}",
        f"受理時間:{now}",
        "對客發送、選菜、定價方法三件仍由人決定。",
    ]
    output = "\n".join(lines)
    _write_text(
        QUOTE_INTAKE_ROOT / f"{task_id}.md",
        "\n".join(
            [
                f"# 報價試算 {task_id}",
                "",
                f"- 受理時間:{now}",
                "- 狀態:hermes 已用價目表試算(內部),待 A0 覆核與 Owner 定案",
                "",
                "## Owner 需求原文",
                "",
                request,
                "",
                "## hermes 試算輸出",
                "",
                output,
                "",
            ]
        ),
    )
    return output


def execute(
    request: str,
    owner_user_id: int,
    *,
    chat_id: int | None = None,
    chat_type: str | None = None,
    openrouter_key: str | None = None,
    forced_rejection: str | None = None,
) -> dict:
    action_name, early_rejection = classify(request)
    # 呼叫端(gateway)已經有更精確的拒絕理由時,一律沿用它,不得被這裡的
    # 二次分類覆寫成「不在目前的安全動作白名單」——覆寫會讓收據上的原因是假的,
    # 每次故障排查都被導向錯的方向(2026-09-22 誤診兩次的根因)。
    if forced_rejection:
        action_name, early_rejection = None, forced_rejection
    if action_name == "durable-job" and early_rejection is None:
        return _start_durable_job(
            request,
            owner_user_id,
            chat_id=chat_id,
            chat_type=chat_type,
            openrouter_key=openrouter_key,
        )
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    research_request = is_public_research_command(request)
    prefix = "DFR" if research_request else "A6H"
    task_id = f"{prefix}-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    task_dir = TASK_ROOT / task_id
    task_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    task_dir.chmod(0o700)
    action_name, rejection = action_name, early_rejection
    stored_request = "[redacted-public-research-command]" if research_request else request[:2000]
    task = {
        "schema_version": 3 if research_request else 2,
        "task_id": task_id,
        "created_at": now,
        "request": stored_request,
        "request_sha256": hashlib.sha256(request.encode("utf-8")).hexdigest(),
        "request_chars": len(request),
        "requester": {
            "channel": "telegram" if chat_id is not None else "local-heartbeat",
            "owner_user_id": owner_user_id,
            "chat_id": chat_id,
            "chat_type": chat_type,
        },
        "action": action_name,
        "policy": "public-research-cold-route-v1" if research_request else "fixed-argv-allowlist-v2",
    }
    _write_json(task_dir / "task.json", task)

    if rejection:
        receipt = {**task, "status": "rejected", "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "reason": rejection}
    elif action_name == "deerflow-public-research":
        query, query_rejection = parse_public_query(request)
        if query_rejection or query is None:
            receipt = {**task, "status": "rejected", "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "reason": query_rejection or "invalid public query", "network_calls": 0}
        else:
            receipt = _start_deerflow_job(task_dir, task, query, openrouter_key)
        receipt["receipt_path"] = str(task_dir / "receipt.json")
        return receipt
    elif action_name == "deerflow-job-status":
        match = RESEARCH_STATUS_RE.match(request)
        target = _deerflow_job_readback(match.group(1)) if match else {"status": "rejected", "reason": "invalid research job id"}
        receipt = {
            **task,
            "status": "completed" if target.get("status") not in {"missing", "rejected"} else "failed",
            "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "description": ACTIONS[action_name].description,
            "output": json.dumps(
                {
                    key: target.get(key)
                    for key in ("task_id", "status", "provider", "model", "reason", "artifact_path", "answer_preview")
                    if target.get(key) is not None
                },
                ensure_ascii=False,
                indent=2,
            ),
        }
    elif action_name == "quote-intake":
        intake_path = QUOTE_INTAKE_ROOT / f"{task_id}.md"
        _write_text(
            intake_path,
            "\n".join(
                [
                    f"# 報價需求受理 {task_id}",
                    "",
                    f"- 受理時間:{now}",
                    "- 狀態:待 A0 代產(hermes 不報價,紅線不動)",
                    "",
                    "## Owner 需求原文",
                    "",
                    request,
                    "",
                ]
            ),
        )
        receipt = {
            **task,
            "status": "completed",
            "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "description": ACTIONS[action_name].description,
            "output": (
                "【hermes】已收到報價需求並建成案卷,原文完整留存。\n"
                "我不報價(這是固定紅線),已標記為待 A0 代產,A0 下一輪續接時會看到這筆。\n"
                f"案卷:{intake_path}"
            ),
        }
    elif action_name == "quote-estimate":
        receipt = {
            **task,
            "status": "completed",
            "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "description": ACTIONS[action_name].description,
            "output": _quote_estimate_output(request, task_id, now),
        }
    else:
        action = ACTIONS[action_name]
        if action_name == "general-chat":
            # Free-form chat via the gateway's chat-fallback mode
            # Extract the actual user message from "general-chat: <message>"
            user_message = request
            if request.startswith("general-chat: "):
                user_message = request[len("general-chat: "):]
            # Call the gateway's chat fallback directly via subprocess
            # to avoid circular import between executor and gateway
            from subprocess import run
            result = run(
                (PYTHON, str(REPO_ROOT / "bot_a6" / "hermes_telegram_gateway.py"), "chat-fallback", user_message),
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=action.timeout,
                check=False,
                env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin", "LANG": "zh_TW.UTF-8"},
            )
            output = result.stdout.strip() or result.stderr.strip()
            receipt = {
                **task,
                "status": "completed" if result.returncode == 0 else "failed",
                "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "description": action.description,
                "returncode": result.returncode,
                "output": output[:MAX_OUTPUT_CHARS],
                "output_truncated": len(output) > MAX_OUTPUT_CHARS,
            }
        else:
            try:
                proc = subprocess.run(
                    action.argv,
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=action.timeout,
                    check=False,
                    env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin", "LANG": "zh_TW.UTF-8"},
                )
                output = ((proc.stdout or "") + (proc.stderr or ""))[:MAX_OUTPUT_CHARS]
                receipt = {
                    **task,
                    "status": "completed" if proc.returncode == 0 else "failed",
                    "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "description": action.description,
                    "returncode": proc.returncode,
                    "output": output,
                    "output_truncated": len((proc.stdout or "") + (proc.stderr or "")) > MAX_OUTPUT_CHARS,
                }
            except subprocess.TimeoutExpired:
                receipt = {**task, "status": "failed", "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "reason": f"worker timeout after {action.timeout}s"}
    _write_json(task_dir / "receipt.json", receipt)
    _write_receipt_markdown(task_dir, receipt)
    receipt["receipt_path"] = str(task_dir / "receipt.json")
    return receipt


def telegram_summary(receipt: dict) -> str:
    if receipt.get("action") == "durable-job":
        return str(receipt.get("summary") or "【hermes】持久任務已建立。")
    status = receipt["status"]
    lines = [f"【hermes executor】{status}", f"任務：{receipt['task_id']}", f"動作：{receipt.get('action') or 'none'}"]
    if receipt.get("reason"):
        lines.append(f"原因：{receipt['reason']}")
    output = receipt.get("output", "").strip()
    if output:
        lines.extend(["結果：", output[:1800]])
    if status == "accepted" and receipt.get("action") == "deerflow-public-research":
        lines.append("已交給隔離 DeerFlow one-shot worker；完成後 Hermes 會主動回報，也可用 /research-status <job-id> 查詢。")
    lines.append(f"receipt：{receipt['receipt_path']}")
    if status == "rejected":
        lines.append("可用：runtime-status／signal-status／repo-status／recent-commits／a6-self-test／deerflow-status／/research-public")
    return "\n".join(lines)


def completed_deerflow_notifications() -> list[dict]:
    notifications: list[dict] = []
    if not TASK_ROOT.is_dir():
        return notifications
    for task_dir in sorted(TASK_ROOT.glob("DFR-*")):
        if (task_dir / "notification.json").exists():
            continue
        receipt_path = task_dir / "receipt.json"
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if receipt.get("action") != "deerflow-public-research" or receipt.get("status") not in {"completed", "failed"}:
            continue
        if receipt.get("parent_job_id"):
            continue
        chat_id = (receipt.get("requester") or {}).get("chat_id")
        if chat_id is None:
            continue
        notifications.append({"receipt": receipt, "receipt_path": str(receipt_path), "chat_id": chat_id})
    return notifications


def deerflow_completion_summary(receipt: dict) -> str:
    lines = [
        f"【hermes】DeerFlow 研究 {receipt.get('status')}",
        f"任務：{receipt.get('task_id')}",
        f"provider：{receipt.get('provider', 'unknown')}",
    ]
    if receipt.get("reason"):
        lines.append(f"原因：{receipt['reason']}")
    if receipt.get("answer_preview"):
        lines.extend(["摘要：", str(receipt["answer_preview"])[:2200]])
    if receipt.get("artifact_path"):
        lines.append(f"artifact：{receipt['artifact_path']}")
    lines.append(f"receipt：{receipt.get('receipt_path') or TASK_ROOT / str(receipt.get('task_id')) / 'receipt.json'}")
    return "\n".join(lines)


def mark_deerflow_notified(receipt_path: str, message_id: int | None = None) -> None:
    path = Path(receipt_path).resolve()
    if path.name != "receipt.json" or path.parent.parent != TASK_ROOT.resolve():
        raise ValueError("invalid DeerFlow receipt path")
    _write_json(
        path.parent / "notification.json",
        {
            "status": "sent",
            "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "receipt_path": str(path),
            "telegram_message_id": message_id,
        },
    )
