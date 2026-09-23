#!/usr/bin/env python3
"""Build a privacy-safe, stratified calibration packet for margin-leak signals.

Raw customer text is read only in-process.  The output contains re-hashed
candidate keys, category labels, reason codes, and local evidence locators; it
never copies message text, customer identifiers, or source conversation IDs.
The labels are review triage, not proof of leakage or permission to charge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from maplab_margin_leak_scan import CATEGORY_RULES  # noqa: E402


METHOD_VERSION = "margin-calibration-v1"
DEFAULT_QUOTAS = {
    "custom_scope": 6,
    "third_party_turnkey": 6,
    "logistics_access": 6,
    "revision_change_order": 6,
    "equipment_consumables": 6,
    "time_rush": 5,
    "dietary_separation": 5,
    "onsite_service": 5,
    "cleanup_waste": 5,
}
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600

REQUEST_RE = re.compile(
    r"幫我|幫忙|麻煩|請問|可以.{0,8}嗎|能不能|需要|希望|想要|我要|我們要|"
    r"再加|追加|改成|換成|安排|提供",
    re.IGNORECASE,
)
INCLUDED_RE = re.compile(
    r"有含|包含|已含|含在|本來就有|原本就有|不用加價|不另外收|方案.{0,8}(?:含|有)",
    re.IGNORECASE,
)
OUR_REWORK_RE = re.compile(
    r"你們.{0,10}(?:做錯|弄錯|漏|少|忘)|做錯|弄錯|重做|補送|不對|不是我.{0,8}要|"
    r"跟.{0,12}不一樣",
    re.IGNORECASE,
)
STRONG_CATEGORY_RE = {
    "custom_scope": re.compile(r"logo|插旗|印刷|花藝|鮮花|打樣|試吃|試作|專屬", re.I),
    "third_party_turnkey": re.compile(
        r"代購|代訂|代墊|幫忙買|幫忙找|進場證|供應商登記|保險|核銷|請款流程",
        re.I,
    ),
    "logistics_access": re.compile(
        r"無電梯|樓梯|搬運|卸貨|停車|臨停|跨縣市|偏遠|山區|多地點|分批送|多趟",
        re.I,
    ),
    "revision_change_order": re.compile(
        r"再改|變更|調整|追加|再加|加一個|去掉|取消|臨時改|當天改|前一天改",
        re.I,
    ),
    "equipment_consumables": re.compile(
        r"長桌|桌巾|椅子|玻璃杯|酒杯|陶瓷|發電機|帳棚|雨備|燈光|音響|保冷|保溫|冷藏",
        re.I,
    ),
    "time_rush": re.compile(r"急件|等待|延後|延遲|超時|待命|清晨|半夜|夜間|國定假日|連假", re.I),
    "dietary_separation": re.compile(
        r"清真|無麩質|不含堅果|獨立包裝|分開製作|全素|蛋奶素",
        re.I,
    ),
    "onsite_service": re.compile(r"服務人員|服務生|駐場|現場服務|補餐|巡場|遞送|倒酒|接待", re.I),
    "cleanup_waste": re.compile(r"垃圾|廚餘|清運|載走|清潔|復原|打掃|剩食|分裝|打包盒", re.I),
}


class CalibrationError(RuntimeError):
    """The calibration request violates the privacy or sampling contract."""


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_private_input(path: Path) -> None:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise CalibrationError("input_must_be_absolute_private_file")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
        raise CalibrationError(f"input_permissions_not_private:{path.name}")
    if hasattr(os, "getuid") and info.st_uid != os.getuid():
        raise CalibrationError(f"input_wrong_owner:{path.name}")


def _compiled_rules() -> dict[str, dict[str, tuple[re.Pattern[str], ...]]]:
    return {
        category: {
            trigger: tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)
            for trigger, patterns in triggers.items()
        }
        for category, triggers in CATEGORY_RULES.items()
    }


def _label(text: str, category: str) -> tuple[str, list[str]]:
    if OUR_REWORK_RE.search(text):
        return "our_rework", ["customer_reports_our_error_or_rework"]
    if INCLUDED_RE.search(text):
        return "included", ["scope_language_says_included"]
    request = bool(REQUEST_RE.search(text))
    strong = bool(STRONG_CATEGORY_RE[category].search(text))
    if request and strong:
        return "true_candidate", ["direct_request_cue", "category_specific_cost_cue"]
    if not request and not strong:
        return "false_positive", ["weak_keyword_without_request_or_cost_cue"]
    return "insufficient_evidence", [
        "category_cue_without_complete_scope_and_delivery_evidence"
    ]


def calibrate(paths: list[Path], *, quotas: dict[str, int] | None = None) -> dict:
    quotas = dict(quotas or DEFAULT_QUOTAS)
    if not quotas or any(category not in CATEGORY_RULES for category in quotas):
        raise CalibrationError("quota_category_invalid")
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 1 for value in quotas.values()):
        raise CalibrationError("quota_value_invalid")
    if sum(quotas.values()) > 200:
        raise CalibrationError("sample_limit_exceeded")

    compiled = _compiled_rules()
    candidates: dict[str, dict[str, dict]] = {category: {} for category in quotas}
    source_hashes = []
    for path in paths:
        validate_private_input(path)
        source_hashes.append(
            {
                "path": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "mode": "0600",
            }
        )
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                conversation_id = row.get("conversation_id")
                text = row.get("customer")
                if not isinstance(conversation_id, str) or not conversation_id:
                    continue
                if not isinstance(text, str) or not text:
                    continue
                for category in quotas:
                    trigger_codes = [
                        trigger
                        for trigger, patterns in compiled[category].items()
                        if any(pattern.search(text) for pattern in patterns)
                    ]
                    if not trigger_codes:
                        continue
                    record = candidates[category].setdefault(
                        conversation_id,
                        {
                            "texts": [],
                            "trigger_codes": set(),
                            "evidence_path": f"{path}#L{line_number}",
                            "evidence_sha256": hashlib.sha256(line.rstrip("\n").encode("utf-8")).hexdigest(),
                            "source_split": path.stem,
                        },
                    )
                    record["texts"].append(text)
                    record["trigger_codes"].update(trigger_codes)

    samples = []
    used_conversations: set[str] = set()
    for category, quota in quotas.items():
        ordered = sorted(
            candidates[category].items(),
            key=lambda item: sha256_text(f"{METHOD_VERSION}|{category}|{item[0]}"),
        )
        selected = [(cid, record) for cid, record in ordered if cid not in used_conversations][
            :quota
        ]
        if len(selected) != quota:
            raise CalibrationError(f"insufficient_unique_candidates:{category}")
        for conversation_id, record in selected:
            used_conversations.add(conversation_id)
            text = "\n".join(record["texts"])
            label, reason_codes = _label(text, category)
            samples.append(
                {
                    "candidate_hash": sha256_text(f"{conversation_id}|{category}"),
                    "category": category,
                    "label": label,
                    "reason_codes": reason_codes,
                    "trigger_codes": sorted(record["trigger_codes"]),
                    "source_split": record["source_split"],
                    "evidence_path": record["evidence_path"],
                    "evidence_sha256": record["evidence_sha256"],
                }
            )

    method_contract = {
        "method_version": METHOD_VERSION,
        "hypothesis": (
            "Direct-request plus category-specific cost cues will separate stronger review "
            "candidates from generic keyword mentions without model calls."
        ),
        "changed_variable": "stratified fixed sample plus deterministic request/cost/rework rules",
        "fixed_holdout": {"total": sum(quotas.values()), "quotas": quotas},
        "expected_delta": "manual precision review can now be measured per category instead of aggregate keyword counts",
        "stop_loss": "stop at the fixed sample; no model, cloud, customer send, live price write, or raw-text output",
        "adapter": "maplab-margin-leak-auditor",
        "sampling": "sha256(method_version|category|conversation_id), unique conversation across categories",
        "evaluator": "deterministic label precedence: our_rework, included, true_candidate, false_positive, insufficient_evidence",
        "acceptance": "exact quota, unique candidate hashes, evidence hashes, privacy contract, owner-only output",
    }
    method_contract["fingerprint"] = sha256_text(
        json.dumps(method_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    label_counts = Counter(sample["label"] for sample in samples)
    category_counts = Counter(sample["category"] for sample in samples)
    return {
        "schema_version": "maplab.margin-leak.calibration.v1",
        "created_at": utc_iso(),
        "data_class": "private-local-calibration",
        "plateau_review": {
            "receipts_compared": 1,
            "consecutive_no_improvement": 0,
            "decision": "new_method_allowed_no_repeated_calibration_receipt",
        },
        "method_contract": method_contract,
        "privacy": {
            "contains_raw_text": False,
            "contains_customer_identifiers": False,
            "contains_source_conversation_ids": False,
            "network_calls": 0,
            "model_calls": 0,
            "customer_send": False,
            "live_price_write": False,
        },
        "source_receipts": source_hashes,
        "sample_count": len(samples),
        "unique_candidate_hashes": len({sample["candidate_hash"] for sample in samples}),
        "category_counts": dict(category_counts),
        "label_counts": dict(label_counts),
        "interpretation": (
            "Deterministic triage labels only. true_candidate is not confirmed leakage; quote, "
            "delivery, incremental-cost, and charged-fee evidence are still required."
        ),
        "samples": samples,
    }


def write_private_json(path: Path, payload: dict) -> None:
    if not path.is_absolute():
        raise CalibrationError("output_path_must_be_absolute")
    path.parent.mkdir(parents=True, exist_ok=True, mode=PRIVATE_DIR_MODE)
    path.parent.chmod(PRIVATE_DIR_MODE)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.chmod(PRIVATE_FILE_MODE)
    os.replace(temporary, path)
    path.chmod(PRIVATE_FILE_MODE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = [Path(value).expanduser().resolve() for value in args.input]
    output = Path(args.output).expanduser().resolve()
    payload = calibrate(paths)
    write_private_json(output, payload)
    print(
        json.dumps(
            {
                "status": "ok",
                "method_version": METHOD_VERSION,
                "sample_count": payload["sample_count"],
                "label_counts": payload["label_counts"],
                "contains_raw_text": False,
                "network_calls": 0,
                "model_calls": 0,
                "output": str(output),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
