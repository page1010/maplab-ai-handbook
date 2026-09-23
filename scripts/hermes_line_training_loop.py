#!/usr/bin/env python3
"""Run one private, local-only Hermes LINE reply evaluation round.

The corpus contains private business conversations with some direct identifiers
reduced. This
module rejects permissive corpus permissions, only talks to an Ollama endpoint
on the loopback interface, disables proxy/redirect handling, and writes all
derived artifacts with owner-only permissions.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import stat
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


DEFAULT_DATA_ROOT = Path("/Volumes/MacExternal/maplab-data/a6-hermes-training")
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "gemma4:latest"
EVALUATOR_VERSION = "maplab.hermes.line-evaluator.v1"
INFERENCE_PARAMETERS = {
    "temperature": 0,
    "seed_strategy": "round-seed-times-1000-plus-sample-index",
}
MAX_BATCH = 30
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600
SIGNALS = (
    "日期",
    "人數",
    "地點",
    "地址",
    "時間",
    "時段",
    "預算",
    "禁忌",
    "過敏",
    "素食",
    "菜單",
    "報價",
    "訂金",
    "匯款",
    "檔期",
    "服務費",
)


class TrainingConfigError(RuntimeError):
    """The requested run violates the local-only execution contract."""


class DatasetError(RuntimeError):
    """The private corpus is absent, malformed, or insufficiently protected."""


class LocalProviderError(RuntimeError):
    """The loopback-only model provider did not return a usable reply."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise urllib.error.HTTPError(req.full_url, code, "redirect blocked", headers, fp)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def resolve_data_root(cli_value: str | None = None) -> Path:
    raw = cli_value or os.environ.get("HERMES_LINE_DATA_ROOT") or str(DEFAULT_DATA_ROOT)
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        raise TrainingConfigError("data_root_must_be_absolute")
    return Path(os.path.abspath(candidate))


def validate_loopback_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    try:
        port = parsed.port
    except ValueError as exc:
        raise TrainingConfigError("ollama_url_invalid_port") from exc
    if parsed.scheme != "http":
        raise TrainingConfigError("ollama_url_requires_http_loopback")
    # Private LINE prompts may only reach the canonical local Ollama listener.
    # A broad "localhost" policy would also permit an unrelated local service
    # (or DNS/proxy behavior) to receive the corpus while still looking local.
    if parsed.hostname != "127.0.0.1":
        raise TrainingConfigError("ollama_url_not_numeric_loopback")
    if port != 11434:
        raise TrainingConfigError("ollama_url_port_not_allowed")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise TrainingConfigError("ollama_url_contains_disallowed_components")
    if parsed.path != "/api/generate":
        raise TrainingConfigError("ollama_url_path_not_allowed")
    return value


def resolve_local_provider(
    *,
    ollama_url: str | None = None,
    model: str | None = None,
) -> tuple[str, str]:
    provider = os.environ.get("HERMES_LINE_PROVIDER", "local-ollama").strip().lower()
    if provider not in {"local", "local-only", "ollama", "local-ollama"}:
        raise TrainingConfigError("external_provider_forbidden")
    resolved_url = validate_loopback_url(
        ollama_url or os.environ.get("HERMES_LINE_OLLAMA_URL") or DEFAULT_OLLAMA_URL
    )
    resolved_model = (
        model or os.environ.get("HERMES_LINE_LOCAL_MODEL") or DEFAULT_OLLAMA_MODEL
    ).strip()
    if not resolved_model or len(resolved_model) > 128 or re.search(r"[\s\x00-\x1f]", resolved_model):
        raise TrainingConfigError("invalid_local_model_name")
    return resolved_url, resolved_model


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _validate_private_path(path: Path, *, directory: bool) -> None:
    if path.is_symlink():
        raise DatasetError(f"symlink_forbidden:{path.name}")
    if not path.exists():
        raise DatasetError(f"missing:{path.name}")
    if directory and not path.is_dir():
        raise DatasetError(f"not_directory:{path.name}")
    if not directory and not path.is_file():
        raise DatasetError(f"not_file:{path.name}")
    info = path.stat()
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise DatasetError(f"wrong_owner:{path.name}")
    if _mode(path) & 0o077:
        raise DatasetError(f"permissions_not_private:{path.name}")


def validate_dataset_root(data_root: Path) -> dict:
    _validate_private_path(data_root, directory=True)
    required = [data_root / name for name in ("train.jsonl", "eval.jsonl", "manifest.json")]
    for path in required:
        _validate_private_path(path, directory=False)
    for name in ("loop_state.json", "current_lessons.md"):
        optional = data_root / name
        if optional.exists() or optional.is_symlink():
            _validate_private_path(optional, directory=False)
    for name in ("runs", "lesson_deltas", "supervisor_jobs"):
        derived_dir = data_root / name
        if derived_dir.exists() or derived_dir.is_symlink():
            _validate_private_path(derived_dir, directory=True)
    try:
        manifest = json.loads((data_root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DatasetError("manifest_unreadable") from exc
    if manifest.get("schema") != "maplab.hermes.line_pairs.v1":
        raise DatasetError("manifest_schema_unrecognized")
    anonymization = str(manifest.get("anonymization") or "").lower()
    split = str(manifest.get("split") or "").lower()
    if "sender" not in anonymization or "hash" not in split or "conversation" not in split:
        raise DatasetError("manifest_privacy_contract_missing")
    return manifest


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.chmod(PRIVATE_DIR_MODE)


def write_private_text(path: Path, text: str) -> None:
    ensure_private_dir(path.parent)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, PRIVATE_FILE_MODE)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        path.chmod(PRIVATE_FILE_MODE)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise


def write_private_json(path: Path, payload: dict) -> None:
    write_private_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise DatasetError(f"invalid_record:{path.name}:{line_number}")
                required = {"id", "stage", "conversation_id", "customer", "target"}
                if not required.issubset(item) or not isinstance(item.get("context", []), list):
                    raise DatasetError(f"invalid_record:{path.name}:{line_number}")
                records.append(item)
    except DatasetError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DatasetError(f"jsonl_unreadable:{path.name}") from exc
    if not records:
        raise DatasetError(f"jsonl_empty:{path.name}")
    return records


def generate_local(
    messages: list[dict],
    *,
    ollama_url: str,
    model: str,
    timeout: int,
    seed: int,
) -> tuple[str, str]:
    prompt = "\n\n".join(
        f"{item.get('role', 'user')}: {item.get('content', '')}" for item in messages
    )
    request = urllib.request.Request(
        ollama_url,
        data=json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0, "seed": seed},
            }
        ).encode(),
        headers={"Content-Type": "application/json"},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            data = json.loads(response.read().decode())
    except (OSError, UnicodeError, ValueError, urllib.error.URLError) as exc:
        raise LocalProviderError("local_ollama_unavailable") from exc
    content = data.get("response") if isinstance(data, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise LocalProviderError("local_ollama_empty_reply")
    return content.strip(), f"local/ollama/{model}"


def score_reply(generated: str, target: str) -> dict:
    required = [signal for signal in SIGNALS if signal in target]
    hits = [signal for signal in required if signal in generated]
    coverage = len(hits) / len(required) if required else 1.0
    target_money = set(re.findall(r"(?:NT\$|\$)?\s*\d[\d,]*(?:萬|元)?", target))
    generated_money = set(
        re.findall(r"(?:NT\$|\$)\s*\d[\d,]*|\d+(?:\.\d+)?萬|\d[\d,]+元", generated)
    )
    unsupported_money = sorted(generated_money - target_money)
    question_ok = not re.search(r"[？?]|請問|方便|麻煩", target) or bool(
        re.search(r"[？?]|請問|方便|麻煩", generated)
    )
    length_ratio = len(generated) / max(len(target), 1)
    length_ok = 0.25 <= length_ratio <= 2.5
    score = round(
        coverage * 55
        + (20 if question_ok else 0)
        + (15 if length_ok else 0)
        + (10 if not unsupported_money else 0)
    )
    passed = score >= 75 and coverage >= 0.75 and not unsupported_money and length_ok
    return {
        "score": score,
        "pass": passed,
        "required_signals": required,
        "hit_signals": hits,
        "missed_signals": sorted(set(required) - set(hits)),
        "unsupported_money": unsupported_money,
        "question_ok": question_ok,
        "length_ratio": round(length_ratio, 2),
    }


def build_prompt(sample: dict, examples: list[dict], lessons: str) -> list[dict]:
    example_text = "\n\n".join(
        f"客戶：{item['customer']}\nMina：{item['target']}" for item in examples
    )
    context = "\n".join(
        f"{item['role']}：{item['content']}" for item in sample.get("context", [])[-6:]
    )
    system = (
        "你是 MAPLAB Hermes 客服助理。請依 Mina 歷史回覆風格，只輸出下一則可直接使用的繁體中文回覆。"
        "優先回答客人當下問題，再補問下一個必要欄位；不要重問已知資料；不得杜撰價格、檔期或政策。"
        "保持手機可讀，不輸出程式碼、JSON、分析或格式規範。\n"
        + lessons[-2500:]
        + "\n\n參考案例：\n"
        + example_text
    )
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": f"對話：\n{context}\n\n客戶最新訊息：{sample['customer']}",
        },
    ]


def _stage_metrics(results: list[dict]) -> tuple[dict[str, dict], str | None]:
    grouped: dict[str, list[dict]] = {}
    for item in results:
        grouped.setdefault(item["stage"], []).append(item)
    metrics: dict[str, dict] = {}
    for stage, items in sorted(grouped.items()):
        metrics[stage] = {
            "count": len(items),
            "pass_rate": round(
                sum(bool(item["evaluation"]["pass"]) for item in items) / len(items), 4
            ),
            "mean_score": round(
                sum(float(item["evaluation"]["score"]) for item in items) / len(items), 1
            ),
        }
    lowest = min(metrics, key=lambda stage: (metrics[stage]["mean_score"], stage)) if metrics else None
    return metrics, lowest


def _read_prior_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run_training_round(
    *,
    data_root: Path,
    batch: int,
    seed: int,
    stage: str,
    ollama_url: str,
    model: str,
    timeout: int,
    generate_fn: Callable[..., tuple[str, str]] = generate_local,
) -> dict:
    if not 1 <= batch <= MAX_BATCH:
        raise TrainingConfigError(f"batch_must_be_1_to_{MAX_BATCH}")
    if not 1 <= timeout <= 600:
        raise TrainingConfigError("timeout_must_be_1_to_600")
    validate_dataset_root(data_root)
    train = load_jsonl(data_root / "train.jsonl")
    evaluation = load_jsonl(data_root / "eval.jsonl")
    evaluation_pool = [item for item in evaluation if item["stage"] == stage] if stage else evaluation
    if not evaluation_pool:
        raise DatasetError("evaluation_stage_empty")

    rng = random.Random(seed)
    samples = rng.sample(evaluation_pool, min(batch, len(evaluation_pool)))
    by_stage: dict[str, list[dict]] = {}
    for item in train:
        by_stage.setdefault(item["stage"], []).append(item)

    lessons_path = data_root / "current_lessons.md"
    lessons = lessons_path.read_text(encoding="utf-8") if lessons_path.exists() else ""
    results: list[dict] = []
    for sample_index, sample in enumerate(samples):
        pool = [
            item
            for item in by_stage.get(sample["stage"], [])
            if item["conversation_id"] != sample["conversation_id"]
        ]
        examples = rng.sample(pool, min(2, len(pool)))
        inference_seed = seed * 1000 + sample_index
        generated, provider = generate_fn(
            build_prompt(sample, examples, lessons),
            ollama_url=ollama_url,
            model=model,
            timeout=timeout,
            seed=inference_seed,
        )
        if not provider.startswith("local/ollama/"):
            raise TrainingConfigError("provider_policy_violation")
        results.append(
            {
                "id": sample["id"],
                "stage": sample["stage"],
                "provider": provider,
                "inference_seed": inference_seed,
                "customer": sample["customer"],
                "generated": generated,
                "target": sample["target"],
                "evaluation": score_reply(generated, sample["target"]),
            }
        )

    passed = sum(bool(item["evaluation"]["pass"]) for item in results)
    unsupported_count = sum(bool(item["evaluation"]["unsupported_money"]) for item in results)
    missed: dict[str, int] = {}
    for item in results:
        for signal in item["evaluation"]["missed_signals"]:
            missed[signal] = missed.get(signal, 0) + 1
    stage_metrics, lowest_stage = _stage_metrics(results)
    created_at = utc_now()
    run_id = f"HERMES-LINE-{created_at.strftime('%Y%m%d-%H%M%S-%f')}"
    summary = {
        "schema_version": "maplab.hermes.line-run.v2",
        "evaluator_version": EVALUATOR_VERSION,
        "run_id": run_id,
        "created_at": created_at.isoformat(),
        "local_only": True,
        "provider_policy": "loopback-ollama-only",
        "ollama_endpoint": ollama_url,
        "model": model,
        "inference_parameters": INFERENCE_PARAMETERS,
        "external_network_calls": 0,
        "loopback_ollama_calls": len(results),
        "seed": seed,
        "requested_stage": stage or None,
        "batch": len(results),
        "passed": passed,
        "pass_rate": round(passed / max(len(results), 1), 4),
        "mean_score": round(
            sum(float(item["evaluation"]["score"]) for item in results)
            / max(len(results), 1),
            1,
        ),
        "unsupported_price_count": unsupported_count,
        "unsupported_price_rate": round(unsupported_count / max(len(results), 1), 4),
        "providers": sorted({item["provider"] for item in results}),
        "lowest_stage": lowest_stage,
        "stage_metrics": stage_metrics,
        "missed_signals": dict(sorted(missed.items(), key=lambda pair: (-pair[1], pair[0]))),
        "results": results,
    }

    result_root = data_root / "runs"
    lesson_delta_root = data_root / "lesson_deltas"
    ensure_private_dir(result_root)
    ensure_private_dir(lesson_delta_root)
    run_path = result_root / f"{run_id}.json"
    lesson_delta_path = lesson_delta_root / f"{run_id}.md"
    if lesson_delta_path.exists() or lesson_delta_path.is_symlink():
        raise DatasetError("lesson_delta_collision")
    summary["lesson_delta"] = str(lesson_delta_path)
    lesson_signals = "、".join(list(summary["missed_signals"])[:8]) or "無新增缺漏"
    lesson_stage = lowest_stage or "未辨識"
    lesson_delta = (
        f"# {run_id} lesson delta\n\n"
        f"- created_at: `{summary['created_at']}`\n"
        f"- lowest_stage: `{lesson_stage}`\n"
        f"- pass_rate: `{summary['pass_rate']}`\n"
        f"- unsupported_price_rate: `{summary['unsupported_price_rate']}`\n"
        f"- next_focus: {lesson_signals}\n"
        "- invariant: 不得發明真實回覆未出現的價格。\n"
    )
    write_private_text(lesson_delta_path, lesson_delta)
    write_private_json(run_path, summary)
    write_private_text(
        lessons_path,
        "# Hermes rolling lessons\n\n"
        f"Latest immutable delta: `{lesson_delta_path}`\n\n"
        f"下一輪優先 stage：{lesson_stage}。\n"
        f"下一輪優先補齊：{lesson_signals}。不得發明真實回覆未出現的價格。\n",
    )

    state_path = data_root / "loop_state.json"
    prior = _read_prior_state(state_path)
    previous_pass_rate = prior.get("pass_rate")
    successful_round = summary["pass_rate"] >= 0.85 and summary["unsupported_price_rate"] == 0
    success_streak = int(prior.get("success_streak") or 0) + 1 if successful_round else 0
    regression_streak = 0
    if isinstance(previous_pass_rate, (int, float)) and summary["pass_rate"] < previous_pass_rate:
        regression_streak = int(prior.get("regression_streak") or 0) + 1
    state = {
        "schema_version": "maplab.hermes.line-loop-state.v2",
        "evaluator_version": EVALUATOR_VERSION,
        "updated_at": utc_now().isoformat(),
        "local_only": True,
        "provider_policy": "loopback-ollama-only",
        "ollama_endpoint": ollama_url,
        "model": model,
        "inference_parameters": INFERENCE_PARAMETERS,
        "external_network_calls": 0,
        "loopback_ollama_calls": summary["loopback_ollama_calls"],
        "latest_run": str(run_path),
        "providers": summary["providers"],
        "pass_rate": summary["pass_rate"],
        "mean_score": summary["mean_score"],
        "unsupported_price_rate": summary["unsupported_price_rate"],
        "lowest_stage": lowest_stage,
        "successful_round": successful_round,
        "success_streak": success_streak,
        "regression_streak": regression_streak,
        "next_prompt": (
            "讀 manifest、current_lessons 與 latest run；針對最低分 stage 再跑一輪，"
            "確認 pass_rate 改善且 unsupported_price_rate 維持 0。"
        ),
    }
    write_private_json(state_path, state)
    return summary | {"receipt": str(run_path)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one owner-only LINE reply evaluation round using local Ollama only."
    )
    parser.add_argument("--batch", type=int, default=12)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--stage", default="")
    parser.add_argument("--data-root")
    parser.add_argument("--ollama-url")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=180)
    return parser


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    args = build_parser().parse_args(argv)
    try:
        data_root = resolve_data_root(args.data_root)
        ollama_url, model = resolve_local_provider(
            ollama_url=args.ollama_url,
            model=args.model,
        )
        seed = args.seed if args.seed is not None else int(utc_now().strftime("%Y%m%d"))
        summary = run_training_round(
            data_root=data_root,
            batch=args.batch,
            seed=seed,
            stage=args.stage.strip(),
            ollama_url=ollama_url,
            model=model,
            timeout=args.timeout,
        )
    except TrainingConfigError as exc:
        print(f"config_error:{exc}", file=os.sys.stderr)
        return 2
    except DatasetError as exc:
        print(f"dataset_error:{exc}", file=os.sys.stderr)
        return 3
    except LocalProviderError as exc:
        print(f"provider_error:{exc}", file=os.sys.stderr)
        return 4
    public_summary = {key: value for key, value in summary.items() if key != "results"}
    print(json.dumps(public_summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
