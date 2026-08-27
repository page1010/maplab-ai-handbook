#!/usr/bin/env python3
"""Privacy-safe first-pass scan for potentially unbilled MAPLAB service work.

The scanner reads local/anonymized LINE JSONL and emits aggregate trigger counts
only.  It deliberately does not copy message text, names, phone numbers, raw
conversation IDs, or model output into the receipt.  Matches are candidates for
local human/rule review, not proof that a customer should be charged.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


CATEGORY_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "custom_scope": {
        "custom": (r"客製", r"特製", r"指定", r"專屬", r"主題"),
        "brand_assets": (r"logo", r"插旗", r"印刷", r"色系", r"品牌"),
        "styling": (r"花藝", r"鮮花", r"佈置", r"擺設", r"陳列"),
        "prototype": (r"試吃", r"試作", r"打樣", r"示意圖", r"樣品"),
    },
    "revision_change_order": {
        "change": (r"改成", r"換成", r"再改", r"變更", r"調整"),
        "add_remove": (r"再加", r"追加", r"加一個", r"去掉", r"取消"),
        "late_change": (r"臨時改", r"當天改", r"前一天改", r"已確認.*改"),
    },
    "onsite_service": {
        "staff": (r"服務人員", r"服務生", r"駐場", r"現場服務", r"工作人員"),
        "service": (r"補餐", r"巡場", r"遞送", r"倒酒", r"接待"),
    },
    "logistics_access": {
        "stairs": (r"[2-9二三四五六七八九十]+樓", r"樓梯", r"無電梯", r"搬運"),
        "unloading": (r"卸貨", r"停車", r"臨停", r"走很遠", r"狹窄"),
        "multi_stop": (r"多地點", r"兩個地點", r"第二個地點", r"分批送", r"多趟"),
        "remote": (r"跨縣市", r"偏遠", r"山區", r"外縣市"),
    },
    "time_rush": {
        "rush": (r"急件", r"臨時", r"明天", r"後天", r"這週要"),
        "wait": (r"等待", r"延後", r"延遲", r"超時", r"待命"),
        "off_hours": (r"清晨", r"半夜", r"夜間", r"國定假日", r"連假"),
    },
    "cleanup_waste": {
        "waste": (r"垃圾", r"廚餘", r"清運", r"載走"),
        "restore": (r"清潔", r"復原", r"收拾", r"打掃"),
        "packing": (r"剩食", r"分裝", r"打包盒", r"幫忙打包"),
    },
    "equipment_consumables": {
        "furniture": (r"長桌", r"桌巾", r"椅子", r"餐檯"),
        "tableware": (r"玻璃杯", r"酒杯", r"陶瓷", r"餐具", r"杯具"),
        "power_weather": (r"發電機", r"電源", r"帳棚", r"雨備", r"燈光", r"音響"),
        "temperature": (r"冰塊", r"保冷", r"保溫", r"冷藏"),
    },
    "third_party_turnkey": {
        "procurement": (r"代購", r"代訂", r"代墊", r"幫忙買", r"幫忙找"),
        "vendor": (r"攝影", r"主持", r"花藝", r"音響", r"清潔公司", r"場地"),
        "administration": (r"進場證", r"供應商登記", r"保險", r"核銷", r"請款流程"),
    },
    "dietary_separation": {
        "dietary": (r"素食", r"全素", r"蛋奶素", r"清真", r"宗教"),
        "allergen": (r"過敏", r"無麩質", r"不含堅果", r"獨立包裝", r"分開製作"),
    },
}


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compiled_rules() -> dict[str, dict[str, tuple[re.Pattern[str], ...]]]:
    return {
        category: {
            trigger: tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)
            for trigger, patterns in triggers.items()
        }
        for category, triggers in CATEGORY_RULES.items()
    }


def scan_jsonl(paths: list[Path]) -> dict:
    compiled = _compiled_rules()
    total_rows = 0
    conversations: set[str] = set()
    matched_conversations: dict[str, set[str]] = defaultdict(set)
    matched_rows: Counter[str] = Counter()
    trigger_counts: dict[str, Counter[str]] = defaultdict(Counter)
    stage_counts: dict[str, Counter[str]] = defaultdict(Counter)
    malformed_rows = 0

    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                total_rows += 1
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    malformed_rows += 1
                    continue
                if not isinstance(row, dict):
                    malformed_rows += 1
                    continue
                conversation_id = str(row.get("conversation_id") or "unknown")
                conversations.add(conversation_id)
                text = str(row.get("customer") or "")
                stage = str(row.get("stage") or "unknown")
                for category, triggers in compiled.items():
                    category_triggers = [
                        trigger
                        for trigger, patterns in triggers.items()
                        if any(pattern.search(text) for pattern in patterns)
                    ]
                    if not category_triggers:
                        continue
                    matched_rows[category] += 1
                    matched_conversations[category].add(conversation_id)
                    stage_counts[category][stage] += 1
                    trigger_counts[category].update(category_triggers)

    categories = []
    for category in CATEGORY_RULES:
        categories.append(
            {
                "category": category,
                "matched_rows": matched_rows[category],
                "unique_conversations": len(matched_conversations[category]),
                "trigger_counts": dict(trigger_counts[category].most_common()),
                "stage_counts": dict(stage_counts[category].most_common()),
                "review_status": "candidate_signal_not_confirmed_charge",
            }
        )
    categories.sort(key=lambda item: (-item["unique_conversations"], item["category"]))
    return {
        "schema_version": "maplab.margin-leak.aggregate.v1",
        "created_at": utc_iso(),
        "data_class": "private-local-aggregate",
        "contains_raw_text": False,
        "contains_customer_identifiers": False,
        "network_calls": 0,
        "total_rows": total_rows,
        "unique_conversations": len(conversations),
        "malformed_rows": malformed_rows,
        "categories": categories,
        "interpretation": (
            "Keyword matches are triage candidates only. Confirm baseline scope, actual work, "
            "incremental cost, existing charge, and whether MAPLAB caused the rework before pricing."
        ),
    }


def write_private_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    os.replace(temporary, path)
    path.chmod(0o600)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, help="Private JSONL input")
    parser.add_argument("--output", required=True, help="Private aggregate receipt JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = [Path(value).expanduser().resolve() for value in args.input]
    if any(not path.is_file() for path in paths):
        raise SystemExit("all --input paths must be files")
    payload = scan_jsonl(paths)
    write_private_json(Path(args.output).expanduser().resolve(), payload)
    print(
        json.dumps(
            {
                "status": "ok",
                "contains_raw_text": False,
                "total_rows": payload["total_rows"],
                "unique_conversations": payload["unique_conversations"],
                "category_count": len(payload["categories"]),
                "output": str(Path(args.output).expanduser().resolve()),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
