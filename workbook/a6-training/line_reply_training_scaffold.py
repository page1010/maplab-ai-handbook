#!/usr/bin/env python3
"""Build local, de-identified A6 LINE reply training scaffold data.

This script is intentionally conservative:
- no model calls
- no network
- no message sending
- no secrets
- no raw filename/contact_name export

Default mode is dry-run. Use --write to write generated JSONL/manifest files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BOOKING_PAIRS = REPO_ROOT / "data" / "line_booking_pairs.csv"
DEFAULT_QA_JSON = Path(__file__).with_name("qa_examples_deidentified.json")
DEFAULT_RAW_PAIRS_JSON = Path(__file__).with_name("training_pairs_raw.json")
DEFAULT_OUTPUT_DIR = Path(__file__).with_name("generated_local")

KNOWN_STAGES = {
    "S0_OPENING",
    "S1_INQUIRY",
    "S1_QUALIFY",
    "S2_DATA",
    "S2_DIETARY_ASK",
    "S3_QUOTE_INTRO",
    "S3_QUOTE_SEND",
    "S3_QUOTE_ACK",
    "S3_MENU_ADJUST",
    "S3_BUDGET_CONFIRM",
    "S4_BOOKING_ASK",
    "S4_PAYMENT_INFO",
    "S5_PAYMENT",
    "S5_PAYMENT_ACK",
    "S6_PREDAY",
    "S_PENDING",
}

USER_ROLES = {"user", "customer", "客戶"}
ACCOUNT_ROLES = {"account", "business", "maplab", "mina", "業務", "店家"}


@dataclass(frozen=True)
class BookingIndex:
    stats: dict[str, Any]
    mask_tokens: tuple[str, ...]


def stable_id(*parts: object, prefix: str = "a6") -> str:
    raw = "\u241f".join("" if p is None else str(p) for p in parts)
    digest = hashlib.sha256(("a6-line-reply-v0:" + raw).encode("utf-8")).hexdigest()
    return f"{prefix}_{digest[:16]}"


def normalize_role(role: Any) -> str:
    return str(role or "").strip().lower()


def split_for_id(sample_id: str) -> str:
    bucket = int(hashlib.sha256(sample_id.encode("utf-8")).hexdigest()[:8], 16) % 10
    if bucket == 0:
        return "test"
    if bucket == 1:
        return "validation"
    return "train"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError(f"{path} must contain a top-level object")
    return obj


def read_booking_index(path: Path) -> BookingIndex:
    rows: list[dict[str, str]] = []
    mask_tokens: set[str] = set()
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            name = (row.get("contact_name") or "").strip()
            if name:
                mask_tokens.add(name)
    stats = {
        "path": str(path),
        "rows": len(rows),
        "confirmed": Counter(row.get("confirmed", "") for row in rows),
        "likely_true_positive": Counter(row.get("likely_true_positive", "") for row in rows),
        "matched_timetree_rows": sum(
            1 for row in rows if row.get("match_timetree_date") or row.get("match_timetree_events")
        ),
        "start_months": Counter((row.get("start_date") or "")[:7] or "<missing>" for row in rows),
        "privacy": {
            "filename_exported": False,
            "contact_name_exported": False,
            "raw_message_exported": False,
        },
    }
    # Convert Counters to normal dicts for stable JSON output.
    stats["confirmed"] = dict(stats["confirmed"])
    stats["likely_true_positive"] = dict(stats["likely_true_positive"])
    stats["start_months"] = dict(stats["start_months"])
    return BookingIndex(stats=stats, mask_tokens=tuple(sorted(mask_tokens, key=len, reverse=True)))


def mask_pii(text: Any, mask_tokens: Iterable[str] = ()) -> str:
    value = str(text or "")
    for token in mask_tokens:
        token = token.strip()
        if len(token) >= 2:
            value = value.replace(token, "[姓名]")
    value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[email]", value)
    value = re.sub(r"https?://\S+|www\.\S+", "[url]", value)
    value = re.sub(r"(?:\+?886[-\s]?)?0?9\d{2}[-\s]?\d{3}[-\s]?\d{3}", "[電話]", value)
    value = re.sub(r"(?:\+?886[-\s]?)?0\d{1,2}[-\s]?\d{3,4}[-\s]?\d{3,4}", "[電話]", value)
    value = re.sub(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", "[日期]", value)
    value = re.sub(r"\b\d{1,2}[-/]\d{1,2}\b", "[日期]", value)
    value = re.sub(r"\d{1,2}\s*月\s*\d{1,2}\s*日?", "[日期]", value)
    value = re.sub(r"[^\s，。！？,!?]{2,20}(?:路|街|巷|弄)[^\s，。！？,!?]{0,20}(?:號|樓)?", "[地址]", value)
    # P15: mask "姓名：XXX" inline patterns (customer fills own name in reply)
    value = re.sub(r"姓名[：:]\s*[^\n\[（(\s，。]{2,10}", "姓名：[姓名]", value)
    # Also mask bare digit sequences that look like account numbers (≥8 digits)
    value = re.sub(r"\b\d{8,20}\b", "[帳號]", value)
    return value.strip()


def build_sample(
    *,
    source_kind: str,
    source_ref: str,
    stage: str,
    customer_text: str,
    business_text: str,
    mask_tokens: Iterable[str],
) -> dict[str, Any] | None:
    customer = mask_pii(customer_text, mask_tokens)
    business = mask_pii(business_text, mask_tokens)
    if not customer or not business:
        return None
    sample_id = stable_id(source_kind, source_ref, stage, customer, business, prefix="a6_reply")
    needs_stage_review = stage not in KNOWN_STAGES
    return {
        "id": sample_id,
        "task": "line_quote_reply_draft",
        "stage": stage or "S_PENDING",
        "split": split_for_id(sample_id),
        "source": {
            "kind": source_kind,
            "privacy": "masked_local",
            "conversation_id_hash": stable_id(source_kind, source_ref, prefix="conv"),
        },
        "instruction": "根據 MAPLAB LINE 銷售 SOP，為 Mina 起草下一則業務回覆。只輸出草稿，不送訊息。",
        "input": {
            "messages": [{"role": "customer", "content": customer}],
            "known_fields": {},
        },
        "target": {
            "role": "business",
            "content": business,
        },
        "safety": {
            "send_allowed": False,
            "requires_human_review": True,
            "price_truth_source": "A5/GAS/Sheet only",
            "needs_stage_review": needs_stage_review,
        },
    }


def samples_from_raw_pairs(obj: dict[str, Any], mask_tokens: Iterable[str]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    pairs = obj.get("pairs") or []
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            continue
        role = normalize_role(pair.get("role"))
        response_role = normalize_role(pair.get("response_role"))
        if role not in USER_ROLES or response_role not in ACCOUNT_ROLES:
            continue
        sample = build_sample(
            source_kind="training_pairs_raw",
            source_ref=str(pair.get("conv_id") or index),
            stage=str(pair.get("stage") or "S_PENDING"),
            customer_text=str(pair.get("msg") or ""),
            business_text=str(pair.get("response") or ""),
            mask_tokens=mask_tokens,
        )
        if sample:
            samples.append(sample)
    return samples


def samples_from_qa_examples(obj: dict[str, Any], mask_tokens: Iterable[str]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    examples = obj.get("examples") or []
    for index, example in enumerate(examples):
        if not isinstance(example, dict):
            continue
        sample = build_sample(
            source_kind="qa_examples_deidentified",
            source_ref=str(example.get("conv_id") or example.get("id") or index),
            stage=str(example.get("stage") or "S_PENDING"),
            customer_text=str(example.get("customer") or ""),
            business_text=str(example.get("business") or ""),
            mask_tokens=mask_tokens,
        )
        if sample:
            samples.append(sample)
    return samples


def make_manifest(samples: list[dict[str, Any]], booking: BookingIndex) -> dict[str, Any]:
    stage_counts = Counter(sample["stage"] for sample in samples)
    split_counts = Counter(sample["split"] for sample in samples)
    source_counts = Counter(sample["source"]["kind"] for sample in samples)
    account_target_count = len(samples)
    sparse_stages = sorted(stage for stage, count in stage_counts.items() if count < 5)
    return {
        "version": "a6-line-reply-training-scaffold-v0.1",
        "privacy": {
            "raw_pii_exported": False,
            "filename_exported": False,
            "contact_name_exported": False,
            "send_allowed": False,
        },
        "booking_index": booking.stats,
        "sample_counts": {
            "total_supervised": len(samples),
            "with_account_target": account_target_count,
            "by_stage": dict(stage_counts),
            "by_split": dict(split_counts),
            "by_source": dict(source_counts),
        },
        "answer_side_gap": {
            "current_booking_pairs_have_answer_text": False,
            "line_webhook_has_business_replies": False,
            "status": "needs_LINE_OA_Manager_export_or_human_labels",
            "sparse_stages": sparse_stages,
            "recommended_sources": [
                "LINE OA Manager full conversation CSV export with speaker=Account rows",
                "Mina/Owner human labels for missing target replies",
                "A5/GAS/Sheet quote facts joined as context, not gold reply wording",
            ],
        },
    }


def assert_no_forbidden_tokens(paths: Iterable[Path], tokens: Iterable[str]) -> None:
    needles = [token for token in tokens if token and len(token) >= 2]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for token in needles:
            if token in text:
                raise ValueError(f"forbidden token leaked into {path}: {token[:1]}***")


def write_outputs(output_dir: Path, samples: list[dict[str, Any]], manifest: dict[str, Any], mask_tokens: Iterable[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    samples_path = output_dir / "training_samples.jsonl"
    manifest_path = output_dir / "manifest.json"
    with samples_path.open("w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False, sort_keys=True) + "\n")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert_no_forbidden_tokens([samples_path, manifest_path], mask_tokens)


def build_dataset(
    *,
    booking_pairs: Path,
    qa_json: Path,
    raw_pairs_json: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], tuple[str, ...]]:
    booking = read_booking_index(booking_pairs)
    mask_tokens = booking.mask_tokens
    qa = read_json(qa_json)
    raw_pairs = read_json(raw_pairs_json)
    samples = samples_from_raw_pairs(raw_pairs, mask_tokens)
    samples.extend(samples_from_qa_examples(qa, mask_tokens))
    manifest = make_manifest(samples, booking)
    return samples, manifest, mask_tokens


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--booking-pairs", type=Path, default=DEFAULT_BOOKING_PAIRS)
    parser.add_argument("--qa-json", type=Path, default=DEFAULT_QA_JSON)
    parser.add_argument("--raw-pairs-json", type=Path, default=DEFAULT_RAW_PAIRS_JSON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write", action="store_true", help="write generated JSONL/manifest; default is dry-run")
    parser.add_argument(
        "--strict-answer-side",
        action="store_true",
        help="exit nonzero if no supervised Account/business targets are available",
    )
    args = parser.parse_args(argv)

    samples, manifest, mask_tokens = build_dataset(
        booking_pairs=args.booking_pairs,
        qa_json=args.qa_json,
        raw_pairs_json=args.raw_pairs_json,
    )
    if args.strict_answer_side and not samples:
        print("answer-side target count is zero; refusing to produce train data", file=sys.stderr)
        return 2
    if args.write:
        write_outputs(args.output_dir, samples, manifest, mask_tokens)
        print(json.dumps({"written": str(args.output_dir), "manifest": manifest["sample_counts"]}, ensure_ascii=False))
    else:
        print(json.dumps({"dry_run": True, "output_dir": str(args.output_dir), "manifest": manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
