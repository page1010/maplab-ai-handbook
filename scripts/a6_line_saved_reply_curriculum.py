#!/usr/bin/env python3
"""Materialize LINE OA saved replies as private Hermes development fixtures.

This is a zero-network curriculum step, not weight training. Historical reply
bodies are inspected locally for safety signals, represented only by hashes in
the derived fixtures, and never copied into tracked files or provider prompts.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sqlite3
import stat
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "data" / "case-store" / "a6_case_store.sqlite3"
DEFAULT_OUTPUT_ROOT = (
    Path.home() / ".maplab" / "a6-hermes-training" / "line_oa_saved_replies"
)
CONTRACT_PATH = REPO_ROOT / "config" / "hermes-line-sheets-assistant-v1.json"
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600

import sys

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ASSISTANT_SPEC = importlib.util.spec_from_file_location(
    "a6_curriculum_hermes_sheets_assistant",
    REPO_ROOT / "bot_a6" / "hermes_sheets_assistant.py",
)
if ASSISTANT_SPEC is None or ASSISTANT_SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("hermes_sheets_assistant_import_failed")
ASSISTANT_MODULE = importlib.util.module_from_spec(ASSISTANT_SPEC)
sys.modules[ASSISTANT_SPEC.name] = ASSISTANT_MODULE
ASSISTANT_SPEC.loader.exec_module(ASSISTANT_MODULE)
customer_reply_violations = ASSISTANT_MODULE.customer_reply_violations


# Owner-authored LINE titles are the explicit scenario labels. Mapping them to
# the current neutral contract is deterministic and reviewable; no model guesses.
ROUTE_BY_TITLE: dict[str, tuple[str, str | None]] = {
    "只提供人數要報價": ("Q2", "business_category"),
    "有炒飯的菜單說明": ("MENU_PREF", None),
    "公司菜單做好回覆": ("MENU_PREF", None),
    "直接給的菜單最後說明": ("MENU_PREF", None),
    "菜單直接給的": ("MENU_PREF", None),
    "收據回覆": ("PAYMENT_CHECK", None),
    "檔期滿了公版回覆": ("Q6", "event_time"),
    "確認預訂與否 公版回覆": ("Q6", "event_time"),
    "什麼類型活動": ("Q1", "business_category"),
    "報價後問有菜單嗎？": ("MENU_PREF", None),
    "參考餐檯擺設的精選限動": ("REF_IMAGE", None),
    "一來就問菜單": ("MENU_PREF", None),
    "洽詢入厝": ("Q1", "event_date"),
    "餐點照片": ("REF_IMAGE", None),
    "洽詢開幕": ("Q1", "event_date"),
    "外燴預算不夠推外帶": ("Q9", "service_format"),
    "洽詢婚禮Candy Bar": ("Q1", "event_date"),
    "預算不高推外帶": ("Q9", "service_format"),
    "外燴匯款前": ("PAYMENT_CHECK", None),
    "外燴服務範圍介紹": ("SERVICE_SCOPE", None),
    "洽詢外燴表單": ("Q1", "event_date"),
    "洽詢週歲抓周性別收涎慶生": ("Q1", "event_date"),
    "菜單回傳2": ("PAYMENT_CHECK", None),
    "外燴服務範圍": ("SERVICE_SCOPE", None),
    "詢問外帶菜單介紹1-1": ("Q3", "event_date"),
    "詢問外帶菜單介紹1-2": ("Q3", "event_date"),
    "高雄嘉義問外燴": ("Q5", "venue"),
    "匯款資訊": ("PAYMENT_CHECK", None),
}


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _require_private_file(path: Path) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"private_file_missing:{path.name}")
    if hasattr(os, "getuid") and path.stat().st_uid != os.getuid():
        raise ValueError(f"private_file_wrong_owner:{path.name}")
    if _mode(path) & 0o077:
        raise ValueError(f"private_file_permissions:{path.name}")


def _ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.chmod(PRIVATE_DIR_MODE)


def _write_private(path: Path, text: str) -> None:
    _ensure_private_dir(path.parent)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        os.fchmod(fd, PRIVATE_FILE_MODE)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        path.chmod(PRIVATE_FILE_MODE)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        temp_path.unlink(missing_ok=True)
        raise


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_latest_snapshot(db_path: Path) -> tuple[dict, list[dict]]:
    _require_private_file(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        snapshot = conn.execute(
            """
            SELECT snapshot_id, account_ref, source, observed_at, payload_digest,
                   tag_count, saved_reply_count, imported_at
            FROM line_oa_settings_snapshots
            ORDER BY snapshot_id DESC
            LIMIT 1
            """
        ).fetchone()
        if snapshot is None:
            raise ValueError("line_oa_snapshot_missing")
        replies = conn.execute(
            """
            SELECT ordinal, title, message, usage_scenario, sensitivity,
                   policy_status, allowed_for_auto_send, requires_human_review
            FROM line_oa_saved_replies
            WHERE snapshot_id = ?
            ORDER BY ordinal
            """,
            (snapshot["snapshot_id"],),
        ).fetchall()
    return dict(snapshot), [dict(row) for row in replies]


def load_contract(path: Path = CONTRACT_PATH) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "hermes-line-sheets-assistant-v1":
        raise ValueError("unexpected_hermes_contract")
    return payload


def _approved_pattern(contract: dict, route_id: str, next_field: str | None) -> str:
    templates = {item["id"]: item for item in contract["templates"]}
    if route_id not in templates:
        raise ValueError(f"route_template_missing:{route_id}")
    text = str(templates[route_id]["customer_facing"])
    if "{next_missing_question}" in text:
        if not next_field or next_field not in contract["field_questions"]:
            raise ValueError(f"next_field_missing:{route_id}")
        text = text.replace(
            "{next_missing_question}",
            str(contract["field_questions"][next_field]),
        )
    return text


def build_curriculum(snapshot: dict, replies: list[dict], contract: dict) -> tuple[list[dict], dict]:
    titles = [str(item["title"]) for item in replies]
    missing = sorted(set(ROUTE_BY_TITLE) - set(titles))
    unexpected = sorted(set(titles) - set(ROUTE_BY_TITLE))
    if missing or unexpected or len(titles) != len(set(titles)):
        raise ValueError(
            f"scenario_inventory_drift:missing={missing}:unexpected={unexpected}"
        )
    if int(snapshot["saved_reply_count"]) != len(replies):
        raise ValueError("snapshot_saved_reply_count_mismatch")

    fixtures: list[dict] = []
    raw_violation_counts: Counter[str] = Counter()
    specimen_roles: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    target_violation_count = 0

    for item in replies:
        title = str(item["title"])
        message = str(item["message"])
        route_id, next_field = ROUTE_BY_TITLE[title]
        raw_violations = customer_reply_violations(message)
        raw_violation_counts.update(raw_violations)
        specimen_role = (
            "PROHIBITED_NEGATIVE"
            if raw_violations or item["sensitivity"] in {"commercial", "financial"}
            else "HISTORICAL_REFERENCE"
        )
        specimen_roles[specimen_role] += 1
        route_counts[route_id] += 1
        target = _approved_pattern(contract, route_id, next_field)
        target_violations = customer_reply_violations(target)
        target_violation_count += len(target_violations)
        if target_violations:
            raise ValueError(f"approved_pattern_unsafe:{title}:{target_violations}")
        fixtures.append(
            {
                "id": f"line-oa-saved-reply-{int(item['ordinal']):02d}",
                "training_role": "DEVELOPMENT_FIXTURE_NOT_HUMAN_GOLD",
                "source_scenario": title,
                "scenario_input": f"情境：客戶詢問「{title}」",
                "source_message_sha256": _sha256_text(message),
                "source_message_length": len(message),
                "source_sensitivity": item["sensitivity"],
                "source_policy_status": item["policy_status"],
                "source_specimen_role": specimen_role,
                "source_violation_codes": raw_violations,
                "approved_route": route_id,
                "next_field": next_field,
                "approved_pattern": target,
                "approved_pattern_sha256": _sha256_text(target),
                "eligible_for_sft": False,
                "eligible_for_auto_send": False,
                "requires_mina_review": True,
            }
        )

    receipt = {
        "schema_version": "maplab.hermes.line-oa-curriculum.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_snapshot_id": snapshot["snapshot_id"],
        "source_payload_digest": snapshot["payload_digest"],
        "source_saved_reply_count": len(replies),
        "fixture_count": len(fixtures),
        "specimen_role_counts": dict(sorted(specimen_roles.items())),
        "route_counts": dict(sorted(route_counts.items())),
        "source_violation_counts": dict(sorted(raw_violation_counts.items())),
        "approved_pattern_violation_count": target_violation_count,
        "raw_message_embedded_in_fixture": False,
        "provider_attempts": 0,
        "optimizer_steps": 0,
        "weight_delta_created": False,
        "customer_send_count": 0,
        "external_egress_count": 0,
        "verdict": {
            "weight_learning": "NOT_PROVEN",
            "system_quality": "IMPROVED_DEVELOPMENT_FIXTURES_ONLY",
            "organizational_learning": "INSTITUTIONALIZED",
            "safety": "PASS",
            "promotion": "BLOCKED",
        },
    }
    return fixtures, receipt


def materialize(db_path: Path, output_root: Path) -> dict:
    snapshot, replies = load_latest_snapshot(db_path)
    fixtures, receipt = build_curriculum(snapshot, replies, load_contract())
    _ensure_private_dir(output_root)
    fixture_path = output_root / "development_fixtures.jsonl"
    lesson_path = output_root / "current_lessons.md"
    receipt_path = output_root / "receipt.json"
    _write_private(
        fixture_path,
        "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in fixtures),
    )
    lesson_lines = [
        "# LINE OA saved-reply curriculum",
        "",
        "- Historical reply bodies are local-only and are not copied here.",
        "- Every item is a development fixture, not human gold.",
        "- Only the approved current-contract pattern may be proposed.",
        "- Price, menu, availability, payment, booking and dietary authority remain with Mina.",
        "",
        "## Scenario routes",
        "",
    ]
    lesson_lines.extend(
        f"- {item['source_scenario']} -> {item['approved_route']} -> {item['approved_pattern']}"
        for item in fixtures
    )
    _write_private(lesson_path, "\n".join(lesson_lines) + "\n")
    receipt.update(
        {
            "fixture_path": str(fixture_path),
            "fixture_sha256": _sha256_text(fixture_path.read_text(encoding="utf-8")),
            "lesson_path": str(lesson_path),
            "lesson_sha256": _sha256_text(lesson_path.read_text(encoding="utf-8")),
        }
    )
    _write_private(receipt_path, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    receipt = materialize(args.db.expanduser(), args.output_root.expanduser())
    print(
        json.dumps(
            {
                "fixture_count": receipt["fixture_count"],
                "approved_pattern_violation_count": receipt[
                    "approved_pattern_violation_count"
                ],
                "provider_attempts": receipt["provider_attempts"],
                "optimizer_steps": receipt["optimizer_steps"],
                "weight_delta_created": receipt["weight_delta_created"],
                "customer_send_count": receipt["customer_send_count"],
                "external_egress_count": receipt["external_egress_count"],
                "receipt_path": str(args.output_root.expanduser() / "receipt.json"),
                "verdict": receipt["verdict"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
