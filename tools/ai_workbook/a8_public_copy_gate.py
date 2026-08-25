#!/usr/bin/env python3
"""Reject internal production language before A8 copy reaches a public surface."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BLOCKED_PUBLIC_TERMS = (
    "快速導覽",
    "WordPress 審稿草稿",
    "公開草稿",
    "內部用",
    "不上稿",
    "未發布",
    "待補",
    "待查證",
    "精選圖",
    "含幼兒人像",
    "先排除",
    "不使用該畫面",
    "原始素材",
    "查證紀錄",
    "Suno",
    "Owner",
    "repo",
)

INTERNAL_PATTERNS = (
    ("local_path", re.compile(r"(?:/Users/|workbook/|\b[A-Za-z]:\\)")),
    ("file_label", re.compile(r"\bc\d{2}\.(?:mov|mp4|jpe?g|png|webp)\b", re.IGNORECASE)),
    ("placeholder", re.compile(r"(?:\[INTERNAL_[^]]+\]|\[[^]]*待[^]]*\])")),
)

DATE_PATTERNS = (
    re.compile(r"\b20\d{2}[-/.年]\d{1,2}(?:[-/.月]\d{1,2}日?)?"),
    re.compile(r"(?<!\d)\d{1,2}\s*月\s*\d{1,2}\s*日"),
)


def validate_public_copy(text: str, *, forbid_dates: bool = False) -> list[str]:
    errors: list[str] = []
    for term in BLOCKED_PUBLIC_TERMS:
        if term in text:
            errors.append(f"internal_term:{term}")
    for label, pattern in INTERNAL_PATTERNS:
        if pattern.search(text):
            errors.append(label)
    if forbid_dates:
        for pattern in DATE_PATTERNS:
            if pattern.search(text):
                errors.append("date_exposed")
                break
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--forbid-dates", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = args.path.read_text(encoding="utf-8")
    errors = validate_public_copy(text, forbid_dates=args.forbid_dates)
    result = {"ok": not errors, "path": str(args.path), "errors": errors}
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if not errors else 2)


if __name__ == "__main__":
    main()
