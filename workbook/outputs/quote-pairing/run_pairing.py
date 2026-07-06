#!/usr/bin/env python3
"""
Offline LINE conversation to quote-sheet pairing pipeline.

Safety contract:
- Reads historical LINE CSV, quote filename, and photo-folder metadata only.
- Writes only candidates.json and report.md inside workbook/outputs/quote-pairing.
- Does not import or touch bot_a6, runtime code, .env files, secrets, or APIs.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path("/Users/pagemacmini/maplab-ai-handbook")
OUTPUT_DIR = BASE_DIR / "workbook" / "outputs" / "quote-pairing"

LINE_DIR = Path("/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421")
QUOTE_2025_DIR = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com/"
    "其他電腦/我的電腦/Desktop/外燴 訂單EXCEL待清洗/2025外燴訂單"
)
QUOTE_2024_DIR = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com/"
    "其他電腦/我的電腦/Desktop/外燴 訂單EXCEL待清洗/2024外燴訂單"
)
QUOTE_2026_DIR = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com/"
    "我的雲端硬碟/MAPLAB_DATA/MAPLAB_報價單/2026"
)
PHOTO_2026_DIR = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com/"
    "我的雲端硬碟/2026maplab外燴紀錄"
)

DATE_COMPACT_RE = re.compile(r"^(20\d{2})(\d{2})(\d{2})")
DATE_IN_TEXT_RE = re.compile(r"(20\d{2})[\s_\-./年]*(\d{1,2})[\s_\-./月]*(\d{1,2})日?")
HEADCOUNT_RANGE_RE = re.compile(r"(?<!\d)(\d{1,4})\s*(?:[-~～到至])\s*(\d{1,4})\s*(?:人|位|pax|PAX)")
HEADCOUNT_SINGLE_RE = re.compile(r"(?<!\d)(\d{1,4})\s*(?:人|位|pax|PAX)")
QUOTE_HEADCOUNT_RE = re.compile(r"(?<!\d)(\d{1,4})\s*人")
PRICE_HINT_RE = re.compile(r"(?<!\d)(\d{3,5})(?:\s*/?\s*人)?")
DEAL_TERMS = (
    "匯款",
    "汇款",
    "轉帳",
    "转账",
    "已收到",
    "付款",
    "付清",
    "訂金",
    "订金",
    "尾款",
    "收款",
    "入帳",
    "入账",
    "款項",
    "款项",
)
TAKEOUT_TERMS = (
    "lalamove",
    "Lalamove",
    "客人自己叫",
    "自己會叫",
    "自己会叫",
    "自己叫",
)


@dataclass(frozen=True)
class LineRecord:
    conv_id: str
    start_date: date
    end_date: date
    contact_name: str
    filepath: str
    line_headcount: int | None
    is_deal_signal: bool
    is_takeout_flow: bool
    head_lines_read: int
    parse_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class QuoteRecord:
    internal_id: str
    quote_id: str
    date: date | None
    headcount_hint: int | None
    event_hint: str | None
    price_hint: int | None
    filepath: str
    format: str
    parse_warnings: tuple[str, ...] = ()


def ensure_safe_output_dir() -> None:
    output_resolved = OUTPUT_DIR.resolve()
    allowed_resolved = (BASE_DIR / "workbook" / "outputs" / "quote-pairing").resolve()
    if output_resolved != allowed_resolved:
        raise RuntimeError(f"unsafe output dir: {output_resolved}")
    output_resolved.mkdir(parents=True, exist_ok=True)


def iso_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def parse_yyyymmdd(raw: str) -> date | None:
    match = DATE_COMPACT_RE.search(raw)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def parse_date_in_text(raw: str) -> date | None:
    match = DATE_IN_TEXT_RE.search(raw)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def parse_line_filename(path: Path) -> tuple[str, date | None, date | None, str, list[str]]:
    stem = path.stem
    parts = stem.split("_", 3)
    warnings: list[str] = []
    if len(parts) < 4:
        warnings.append("filename_does_not_match_expected_4_part_pattern")
        return stem, None, None, stem, warnings
    conv_id, start_raw, end_raw, contact_name = parts
    start_dt = parse_yyyymmdd(start_raw)
    end_dt = parse_yyyymmdd(end_raw)
    if start_dt is None:
        warnings.append("start_date_parse_failed")
    if end_dt is None:
        warnings.append("end_date_parse_failed")
    return conv_id, start_dt, end_dt, contact_name, warnings


def read_head_lines(path: Path, max_lines: int = 200) -> tuple[str, int, str | None]:
    encodings = ("utf-8-sig", "utf-8", "cp950", "big5", "gb18030")
    last_error: str | None = None
    for encoding in encodings:
        try:
            chunks: list[str] = []
            with path.open("r", encoding=encoding, newline="") as handle:
                for index, line in enumerate(handle):
                    if index >= max_lines:
                        break
                    chunks.append(line)
            return "".join(chunks), len(chunks), None
        except UnicodeDecodeError as exc:
            last_error = f"{encoding}:{exc.__class__.__name__}"
        except OSError as exc:
            return "", 0, f"{exc.__class__.__name__}:{exc}"
    return "", 0, f"decode_failed:{last_error}"


def extract_headcount(text: str) -> int | None:
    candidates: list[int] = []
    for match in HEADCOUNT_RANGE_RE.finditer(text):
        low = int(match.group(1))
        high = int(match.group(2))
        if 1 <= low <= 500 and 1 <= high <= 500:
            candidates.append(round((low + high) / 2))
    for match in HEADCOUNT_SINGLE_RE.finditer(text):
        value = int(match.group(1))
        if 1 <= value <= 500:
            candidates.append(value)
    if not candidates:
        return None
    counts = Counter(candidates)
    return counts.most_common(1)[0][0]


def has_deal_signal(text: str) -> bool:
    return any(term in text for term in DEAL_TERMS)


def has_takeout_signal(contact_name: str, text: str) -> bool:
    if any(term in contact_name for term in ("外帶", "外带", "自取")):
        return True
    return any(term in text for term in TAKEOUT_TERMS)


def parse_quote_headcount(stem: str) -> int | None:
    matches = [int(match.group(1)) for match in QUOTE_HEADCOUNT_RE.finditer(stem)]
    valid = [value for value in matches if 1 <= value <= 1000]
    return valid[-1] if valid else None


def parse_price_hint(stem: str) -> int | None:
    cleaned = QUOTE_HEADCOUNT_RE.sub(" ", stem)
    values = [int(match.group(1)) for match in PRICE_HINT_RE.finditer(cleaned)]
    likely_prices = [value for value in values if 300 <= value <= 100000]
    return likely_prices[0] if likely_prices else None


def parse_event_hint(stem: str) -> str | None:
    value = DATE_IN_TEXT_RE.sub(" ", stem)
    value = QUOTE_HEADCOUNT_RE.sub(" ", value)
    value = re.sub(r"\b\d{3,6}\b", " ", value)
    value = re.sub(r"[_\-.()\[\]（）]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def list_files(path: Path, suffix: str) -> tuple[list[Path], str | None]:
    try:
        files = [
            child
            for child in path.iterdir()
            if child.is_file()
            and child.suffix.lower() == suffix.lower()
            and not child.name.startswith("~$")
            and not child.name.startswith(".")
        ]
        return sorted(files, key=lambda item: item.name), None
    except OSError as exc:
        return [], f"{path}: {exc.__class__.__name__}: {exc}"


def list_dirs(path: Path) -> tuple[list[Path], str | None]:
    try:
        folders = [
            child
            for child in path.iterdir()
            if child.is_dir() and not child.name.startswith(".")
        ]
        return sorted(folders, key=lambda item: item.name), None
    except OSError as exc:
        return [], f"{path}: {exc.__class__.__name__}: {exc}"


def build_line_records(paths: list[Path]) -> tuple[list[LineRecord], list[str]]:
    records: list[LineRecord] = []
    errors: list[str] = []
    for path in paths:
        conv_id, start_dt, end_dt, contact_name, warnings = parse_line_filename(path)
        text, lines_read, read_error = read_head_lines(path)
        local_warnings = list(warnings)
        if read_error:
            local_warnings.append(read_error)
        if start_dt is None or end_dt is None:
            errors.append(f"{path.name}: missing_start_or_end_date")
            continue
        records.append(
            LineRecord(
                conv_id=conv_id,
                start_date=start_dt,
                end_date=end_dt,
                contact_name=contact_name,
                filepath=str(path),
                line_headcount=extract_headcount(text),
                is_deal_signal=has_deal_signal(text),
                is_takeout_flow=has_takeout_signal(contact_name, text),
                head_lines_read=lines_read,
                parse_warnings=tuple(local_warnings),
            )
        )
    return records, errors


def unique_internal_id(base: str, seen: Counter[str]) -> str:
    seen[base] += 1
    if seen[base] == 1:
        return base
    return f"{base}__dup{seen[base]}"


def build_quote_records(
    quote_2024_paths: list[Path],
    quote_2025_paths: list[Path],
    quote_2026_paths: list[Path],
) -> list[QuoteRecord]:
    records: list[QuoteRecord] = []
    seen: Counter[str] = Counter()

    for path, fmt in [(item, "xlsx_2024") for item in quote_2024_paths] + [
        (item, "xlsx_2025") for item in quote_2025_paths
    ]:
        stem = path.stem
        quote_dt = parse_date_in_text(stem)
        warnings: list[str] = []
        if quote_dt is None:
            warnings.append("date_parse_failed")
        internal_id = unique_internal_id(f"{fmt}:{stem}", seen)
        records.append(
            QuoteRecord(
                internal_id=internal_id,
                quote_id=stem,
                date=quote_dt,
                headcount_hint=parse_quote_headcount(stem),
                event_hint=parse_event_hint(stem),
                price_hint=parse_price_hint(stem),
                filepath=str(path),
                format=fmt,
                parse_warnings=tuple(warnings),
            )
        )

    for path in quote_2026_paths:
        stem = path.stem
        quote_dt = parse_yyyymmdd(stem[:8])
        warnings = [] if quote_dt else ["date_parse_failed"]
        internal_id = unique_internal_id(f"gsheet_2026:{stem}", seen)
        records.append(
            QuoteRecord(
                internal_id=internal_id,
                quote_id=stem,
                date=quote_dt,
                headcount_hint=parse_quote_headcount(stem),
                event_hint=parse_event_hint(stem),
                price_hint=parse_price_hint(stem),
                filepath=str(path),
                format="gsheet_2026",
                parse_warnings=tuple(warnings),
            )
        )
    return records


def parse_photo_date(folder_name: str) -> date | None:
    compact = re.search(r"(20\d{6})", folder_name)
    if compact:
        parsed = parse_yyyymmdd(compact.group(1))
        if parsed:
            return parsed
    short = re.match(r"^(\d{2})(\d{2})", folder_name)
    if short:
        try:
            return date(2026, int(short.group(1)), int(short.group(2)))
        except ValueError:
            return None
    return None


def build_photo_lookup(paths: list[Path]) -> dict[date, str]:
    lookup: dict[date, str] = {}
    for path in paths:
        parsed = parse_photo_date(path.name)
        if parsed and parsed not in lookup:
            lookup[parsed] = path.name
    return lookup


def headcount_matches(line_headcount: int | None, quote_headcount: int | None) -> bool:
    if line_headcount is None or quote_headcount is None or quote_headcount <= 0:
        return False
    return abs(line_headcount - quote_headcount) / quote_headcount <= 0.20


def score_pair(line: LineRecord, quote: QuoteRecord, photo_lookup: dict[date, str]) -> dict[str, Any]:
    if quote.date is None:
        return {
            "confidence": 0,
            "date_delta_days": None,
            "headcount_match": False,
            "photo_folder": None,
            "score_reasons": [],
            "passes_anchor_gate": False,
        }

    delta_days = (quote.date - line.end_date).days
    abs_delta = abs(delta_days)
    score = 0
    reasons: list[str] = []

    if abs_delta == 0:
        score += 40
        reasons.append("date_match_exact")
    elif abs_delta <= 3:
        score += 25
        reasons.append("date_match_close")
    elif abs_delta <= 14:
        score += 15
        reasons.append("date_match_window_4_14")

    matched_headcount = headcount_matches(line.line_headcount, quote.headcount_hint)
    if matched_headcount:
        score += 25
        reasons.append("headcount_match")

    photo_folder = photo_lookup.get(quote.date)
    if photo_folder:
        score += 20
        reasons.append("photo_folder_exists")

    if line.is_deal_signal:
        score += 15
        reasons.append("line_deal_signal")

    # Date-only matches create false positives because LINE display names do not equal quote clients.
    # Require one LINE-side anchor beyond date: either a matching headcount or a deal/payment signal.
    passes_anchor_gate = matched_headcount or line.is_deal_signal

    return {
        "confidence": min(100, score),
        "date_delta_days": delta_days,
        "headcount_match": matched_headcount,
        "photo_folder": photo_folder,
        "score_reasons": reasons,
        "passes_anchor_gate": passes_anchor_gate,
    }


def mask_contact_name(name: str) -> str:
    compact = re.sub(r"\s+", "", name or "")
    if not compact:
        return ""
    if len(compact) == 1:
        return "*"
    if all(ord(char) < 128 for char in compact):
        return compact[:2] + "***"
    return compact[0] + "**"


def build_candidates(
    line_records: list[LineRecord],
    quote_records: list[QuoteRecord],
    photo_lookup: dict[date, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    quotes_with_dates = [quote for quote in quote_records if quote.date]
    candidates: list[dict[str, Any]] = []
    discarded_by_anchor_gate = 0
    below_threshold = 0
    scored_pairs = 0
    skipped_takeout_pairs = 0

    for line in line_records:
        if line.is_takeout_flow:
            skipped_takeout_pairs += len(quotes_with_dates)
            continue
        window_start = line.end_date - timedelta(days=3)
        window_end = line.end_date + timedelta(days=45)
        for quote in quotes_with_dates:
            assert quote.date is not None
            if not (window_start <= quote.date <= window_end):
                continue
            scored_pairs += 1
            score = score_pair(line, quote, photo_lookup)
            if score["confidence"] < 30:
                below_threshold += 1
                continue
            if not score["passes_anchor_gate"]:
                discarded_by_anchor_gate += 1
                continue
            candidates.append(
                {
                    "conv_id": line.conv_id,
                    "contact_name_masked": mask_contact_name(line.contact_name),
                    "line_start_date": line.start_date.isoformat(),
                    "line_end_date": line.end_date.isoformat(),
                    "line_headcount": line.line_headcount,
                    "quote_sheet_id": quote.quote_id,
                    "quote_format": quote.format,
                    "quote_date": quote.date.isoformat(),
                    "headcount": quote.headcount_hint,
                    "photo_folder": score["photo_folder"],
                    "is_deal_signal": line.is_deal_signal,
                    "confidence": score["confidence"],
                    "score_reasons": score["score_reasons"],
                    "date_delta_days": score["date_delta_days"],
                }
            )

    candidates.sort(
        key=lambda item: (
            -int(item["confidence"]),
            item["quote_date"],
            item["conv_id"],
            item["quote_sheet_id"],
        )
    )
    stats = {
        "scored_pairs_in_date_window": scored_pairs,
        "discarded_below_threshold": below_threshold,
        "discarded_by_anchor_gate": discarded_by_anchor_gate,
        "excluded_takeout_conversations": len([line for line in line_records if line.is_takeout_flow]),
        "skipped_takeout_pairs": skipped_takeout_pairs,
    }
    return candidates, stats


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", value or "").lower()


GROUND_TRUTH = {
    "QA-1": {
        "contact_terms": ["李晴宜"],
        "quote_date": "2025-12-21",
        "headcount": 20,
        "expect_quote": True,
        "note": "confirmed_pair",
    },
    "QA-2": {
        "contact_terms": ["洪炳輝"],
        "quote_date": "2025-10-25",
        "headcount": 30,
        "expect_quote": True,
        "note": "confirmed_pair",
    },
    "QA-3": {
        "contact_terms": ["Gina浥慧", "Gina", "浥慧"],
        "quote_date": "2025-11-09",
        "headcount_range": [30, 40],
        "expect_quote": True,
        "note": "type_match_may_not_exist_locally",
    },
    "QA-4": {
        "contact_terms": ["范純禎"],
        "expect_quote": False,
        "note": "takeout_flow_no_quote_sheet",
    },
    "QA-5": {
        "contact_terms": ["林韋如"],
        "quote_date": "2025-03-09",
        "headcount": 50,
        "expect_quote": True,
        "note": "type_match",
    },
    "QA-6": {
        "contact_terms": ["張雅淳"],
        "quote_date": "2025-03-22",
        "headcount_range": [70, 80],
        "expect_quote": True,
        "note": "type_match",
    },
    "QA-7": {
        "contact_terms": ["立碩車業"],
        "quote_date": "2025-10-30",
        "expect_quote": False,
        "note": "no_deal_first_inquiry",
    },
}


def find_line_matches(line_records: list[LineRecord], contact_terms: list[str]) -> list[LineRecord]:
    normalized_terms = [normalize_text(term) for term in contact_terms]
    matches: list[LineRecord] = []
    for line in line_records:
        normalized_name = normalize_text(line.contact_name)
        if any(term and term in normalized_name for term in normalized_terms):
            matches.append(line)
    return matches


def expected_headcount_matches(quote_headcount: int | None, spec: dict[str, Any]) -> bool:
    if quote_headcount is None:
        return False
    if "headcount" in spec:
        expected = int(spec["headcount"])
        return abs(quote_headcount - expected) / expected <= 0.20
    if "headcount_range" in spec:
        low, high = spec["headcount_range"]
        midpoint = (low + high) / 2
        return low <= quote_headcount <= high or abs(quote_headcount - midpoint) / midpoint <= 0.20
    return True


def quote_matches_ground_truth(quote: QuoteRecord, spec: dict[str, Any]) -> bool:
    if "quote_date" in spec:
        expected_date = date.fromisoformat(spec["quote_date"])
        if quote.date != expected_date:
            return False
    if "headcount" in spec or "headcount_range" in spec:
        return expected_headcount_matches(quote.headcount_hint, spec)
    return True


def validate_ground_truth(
    line_records: list[LineRecord],
    quote_records: list[QuoteRecord],
    candidates: list[dict[str, Any]],
    photo_lookup: dict[date, str],
) -> dict[str, dict[str, Any]]:
    candidates_by_conv: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        candidates_by_conv[str(candidate["conv_id"])].append(candidate)

    validation: dict[str, dict[str, Any]] = {}
    for qa_id, spec in GROUND_TRUTH.items():
        line_matches = find_line_matches(line_records, spec["contact_terms"])
        conv_ids = {line.conv_id for line in line_matches}

        if not spec["expect_quote"]:
            matched = [
                candidate
                for conv_id in conv_ids
                for candidate in candidates_by_conv.get(conv_id, [])
            ]
            if matched:
                best = max(matched, key=lambda item: int(item["confidence"]))
                validation[qa_id] = {
                    "status": "incorrectly_matched",
                    "matched_quote": best["quote_sheet_id"],
                    "confidence": best["confidence"],
                    "reason": f"no-quote case produced {len(matched)} kept candidates",
                    "line_matches_found": len(line_matches),
                    "note": spec["note"],
                }
            else:
                reason = "no kept candidates for matched LINE contact"
                if not line_matches:
                    reason = "no LINE filename contact match found; no candidates produced"
                validation[qa_id] = {
                    "status": "correctly_excluded",
                    "matched_quote": None,
                    "confidence": None,
                    "reason": reason,
                    "line_matches_found": len(line_matches),
                    "note": spec["note"],
                }
            continue

        kept_matches = [
            candidate
            for conv_id in conv_ids
            for candidate in candidates_by_conv.get(conv_id, [])
            if candidate["quote_date"] == spec.get("quote_date")
            and (
                "headcount" not in spec
                and "headcount_range" not in spec
                or expected_headcount_matches(candidate.get("headcount"), spec)
            )
        ]
        if kept_matches:
            best = max(kept_matches, key=lambda item: int(item["confidence"]))
            validation[qa_id] = {
                "status": "found",
                "matched_quote": best["quote_sheet_id"],
                "confidence": best["confidence"],
                "reason": "candidate matched expected LINE contact/date/headcount",
                "line_matches_found": len(line_matches),
                "note": spec["note"],
            }
            continue

        matching_quotes = [quote for quote in quote_records if quote_matches_ground_truth(quote, spec)]
        best_debug: dict[str, Any] | None = None
        for line in line_matches:
            for quote in matching_quotes:
                scored = score_pair(line, quote, photo_lookup)
                debug = {
                    "line_conv_id": line.conv_id,
                    "quote_sheet_id": quote.quote_id,
                    "confidence": scored["confidence"],
                    "passes_anchor_gate": scored["passes_anchor_gate"],
                    "score_reasons": scored["score_reasons"],
                    "line_headcount": line.line_headcount,
                    "quote_headcount": quote.headcount_hint,
                    "line_is_deal_signal": line.is_deal_signal,
                }
                if best_debug is None or debug["confidence"] > best_debug["confidence"]:
                    best_debug = debug

        if not line_matches:
            reason = "LINE contact not found by filename contact_name"
        elif not matching_quotes:
            reason = "quote file not found for expected date/headcount"
        elif best_debug and best_debug["confidence"] < 30:
            reason = "best scored pair below confidence threshold"
        elif best_debug and not best_debug["passes_anchor_gate"]:
            reason = "best scored pair filtered by conservative anchor gate"
        else:
            reason = "expected line and quote existed but no kept candidate matched"

        validation[qa_id] = {
            "status": "not_found",
            "matched_quote": None,
            "confidence": best_debug["confidence"] if best_debug else None,
            "reason": reason,
            "line_matches_found": len(line_matches),
            "quote_matches_found": len(matching_quotes),
            "best_debug": best_debug,
            "note": spec["note"],
        }
    return validation


def build_inventory(
    line_paths: list[Path],
    quote_2024_paths: list[Path],
    quote_2025_paths: list[Path],
    quote_2026_paths: list[Path],
    photo_paths: list[Path],
    path_errors: list[str],
) -> dict[str, Any]:
    return {
        "line_csvs_found": len(line_paths),
        "quote_xlsx_2024": len(quote_2024_paths),
        "quote_xlsx_2025": len(quote_2025_paths),
        "quote_gsheet_2026": len(quote_2026_paths),
        "photo_folders_2026": len(photo_paths),
        "path_errors": path_errors,
    }


def write_report(payload: dict[str, Any], stats: dict[str, Any]) -> None:
    validation = payload["ground_truth_validation"]
    inventory = payload["inventory"]
    summary = payload["summary"]
    top_candidates = payload["candidates"][:30]
    lines = [
        "# Quote Pairing Report",
        "",
        f"- Run timestamp: `{payload['run_ts']}`",
        f"- Total candidates: `{summary['total_candidates']}`",
        f"- High confidence 70+: `{summary['high_confidence_70plus']}`",
        f"- Medium confidence 30-70: `{summary['medium_confidence_30_70']}`",
        f"- Quote coverage: `{summary['coverage_pct_of_quotes_matched']}`",
        "",
        "## Inventory",
        "",
        "| Source | Count |",
        "|---|---:|",
        f"| LINE CSVs | {inventory['line_csvs_found']} |",
        f"| 2024 quote xlsx | {inventory['quote_xlsx_2024']} |",
        f"| 2025 quote xlsx | {inventory['quote_xlsx_2025']} |",
        f"| 2026 quote gsheet | {inventory['quote_gsheet_2026']} |",
        f"| 2026 photo folders | {inventory['photo_folders_2026']} |",
        "",
        "## Candidate Policy",
        "",
        "- Confidence scoring follows the requested point system.",
        "- Kept candidates must also have at least one LINE-side anchor beyond date: matching headcount or payment/deal signal.",
        "- This conservative anchor gate prevents date-only false positives because LINE display names do not equal quote-sheet client names.",
        "- LINE conversations with takeout/self-pickup signals are excluded from catering quote pairing.",
        f"- Scored pairs in date window: `{stats['scored_pairs_in_date_window']}`",
        f"- Discarded below threshold: `{stats['discarded_below_threshold']}`",
        f"- Discarded by anchor gate: `{stats['discarded_by_anchor_gate']}`",
        f"- Excluded takeout conversations: `{stats['excluded_takeout_conversations']}`",
        "",
        "## Ground Truth Validation",
        "",
        "| ID | Status | Matched quote | Confidence | Reason |",
        "|---|---|---|---:|---|",
    ]
    for qa_id in sorted(validation):
        item = validation[qa_id]
        quote = item.get("matched_quote") or ""
        confidence = item.get("confidence")
        confidence_text = "" if confidence is None else str(confidence)
        reason = str(item.get("reason", "")).replace("|", "/")
        lines.append(f"| {qa_id} | {item['status']} | {quote} | {confidence_text} | {reason} |")

    lines.extend(
        [
            "",
            "## Top Candidates",
            "",
            "| Confidence | Contact | LINE end | Quote date | Headcount | Quote | Reasons |",
            "|---:|---|---|---|---:|---|---|",
        ]
    )
    for candidate in top_candidates:
        reasons = ",".join(candidate.get("score_reasons", []))
        headcount = "" if candidate.get("headcount") is None else str(candidate["headcount"])
        quote = str(candidate["quote_sheet_id"]).replace("|", "/")
        lines.append(
            f"| {candidate['confidence']} | {candidate['contact_name_masked']} | "
            f"{candidate['line_end_date']} | {candidate['quote_date']} | {headcount} | "
            f"{quote} | {reasons} |"
        )

    lines.extend(
        [
            "",
            "## Blocker",
            "",
            summary["blocker"],
            "",
        ]
    )
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_safe_output_dir()

    path_errors: list[str] = []
    line_paths, error = list_files(LINE_DIR, ".csv")
    if error:
        path_errors.append(error)
    quote_2024_paths, error = list_files(QUOTE_2024_DIR, ".xlsx")
    if error:
        path_errors.append(error)
    quote_2025_paths, error = list_files(QUOTE_2025_DIR, ".xlsx")
    if error:
        path_errors.append(error)
    quote_2026_paths, error = list_files(QUOTE_2026_DIR, ".gsheet")
    if error:
        path_errors.append(error)
    photo_paths, error = list_dirs(PHOTO_2026_DIR)
    if error:
        path_errors.append(error)

    line_records, line_parse_errors = build_line_records(line_paths)
    quote_records = build_quote_records(quote_2024_paths, quote_2025_paths, quote_2026_paths)
    photo_lookup = build_photo_lookup(photo_paths)
    candidates, candidate_stats = build_candidates(line_records, quote_records, photo_lookup)
    validation = validate_ground_truth(line_records, quote_records, candidates, photo_lookup)

    dated_quote_ids = {quote.internal_id for quote in quote_records if quote.date is not None}
    matched_quote_ids = {
        candidate["quote_format"] + ":" + candidate["quote_sheet_id"] for candidate in candidates
    }
    if dated_quote_ids:
        coverage = len(matched_quote_ids) / len(dated_quote_ids) * 100
    else:
        coverage = 0.0

    blocker_parts: list[str] = []
    if path_errors:
        blocker_parts.append("one_or_more_source_paths_unreadable")
    confirmed_misses = [
        f"{qa_id}={item.get('reason', 'not_found')}"
        for qa_id, item in validation.items()
        if item.get("note") == "confirmed_pair" and item.get("status") == "not_found"
    ]
    if confirmed_misses:
        blocker_parts.append("confirmed_pair_missed: " + "; ".join(confirmed_misses))
    if not blocker_parts:
        blocker_parts.append(
            "main gap: 2026 .gsheet filenames usually lack headcount, and date-only matches are intentionally filtered to avoid no-deal false positives"
        )

    payload: dict[str, Any] = {
        "run_ts": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "inventory": build_inventory(
            line_paths,
            quote_2024_paths,
            quote_2025_paths,
            quote_2026_paths,
            photo_paths,
            path_errors,
        ),
        "parse_stats": {
            "line_records_parsed": len(line_records),
            "line_parse_errors": len(line_parse_errors),
            "quote_records_parsed": len(quote_records),
            "quote_records_with_dates": len(dated_quote_ids),
            "quote_records_without_dates": len([quote for quote in quote_records if quote.date is None]),
            "photo_dates_parsed": len(photo_lookup),
        },
        "ground_truth_validation": validation,
        "candidates": candidates,
        "summary": {
            "total_candidates": len(candidates),
            "high_confidence_70plus": len([item for item in candidates if item["confidence"] >= 70]),
            "medium_confidence_30_70": len([item for item in candidates if 30 <= item["confidence"] < 70]),
            "coverage_pct_of_quotes_matched": f"{coverage:.1f}%",
            "blocker": "; ".join(blocker_parts),
        },
    }

    (OUTPUT_DIR / "candidates.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    write_report(payload, candidate_stats)

    print(
        json.dumps(
            {
                "status": "ok",
                "candidates_json": str(OUTPUT_DIR / "candidates.json"),
                "report_md": str(OUTPUT_DIR / "report.md"),
                "inventory": payload["inventory"],
                "parse_stats": payload["parse_stats"],
                "summary": payload["summary"],
                "ground_truth_status": {
                    key: value["status"] for key, value in payload["ground_truth_validation"].items()
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
