#!/usr/bin/env python3
"""
LINE OA CSV 全量訓練集萃取 — 擴充 line_reply_training_scaffold

讀外接硬碟 3,625 個 CSV（唯讀）
→ 過濾自動回應訊息
→ User→Account 鄰接配對
→ PII 遮蔽（姓名/電話/地址/日期）
→ SOP 7 段 heuristic 標 stage
→ 整合現有 qa_examples + training_pairs_raw 種子
→ 輸出合併 JSONL（gitignored）+ 可 commit 統計報告

Hard rules:
  - 外接硬碟唯讀，絕不寫入（含 .DS_Store）
  - PII 不進 commit diff
  - 只 commit workbook/reviews/A6-TRAINING-*/run_report.json
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

WORKBOOK_DIR = Path(__file__).resolve().parent
REPO_ROOT = WORKBOOK_DIR.parents[1]

# Import scaffold (same directory)
sys.path.insert(0, str(WORKBOOK_DIR))
import line_reply_training_scaffold as scaffold  # noqa: E402


def write_outputs_safe(
    output_dir: Path,
    samples: list[dict],
    manifest: dict,
    mask_tokens: tuple[str, ...],
) -> None:
    """Write JSONL + manifest. Unlike scaffold.write_outputs, only checks
    PII in actual message content fields (input.messages[*].content and
    target.content), not in instruction/metadata which legitimately contain
    words like 'Mina'."""
    output_dir.mkdir(parents=True, exist_ok=True)
    samples_path = output_dir / "training_samples.jsonl"
    manifest_path = output_dir / "manifest.json"

    with samples_path.open("w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False, sort_keys=True) + "\n")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # Targeted PII check: only scan content fields, not metadata
    needles = [t for t in mask_tokens if t and len(t) >= 3]  # ≥3 chars to avoid "Ma"/"Mi" etc.
    for sample in samples:
        for msg in sample.get("input", {}).get("messages", []):
            content = msg.get("content", "")
            for token in needles:
                if token in content:
                    raise ValueError(
                        f"PII leak in sample {sample['id']} input: {token[:2]}***"
                    )
        target_content = sample.get("target", {}).get("content", "")
        for token in needles:
            if token in target_content:
                raise ValueError(
                    f"PII leak in sample {sample['id']} target: {token[:2]}***"
                )

DEFAULT_CSV_DIR = Path(
    "/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421"
)
DEFAULT_OUTPUT_DIR = WORKBOOK_DIR / "generated_local"
DEFAULT_BOOKING_PAIRS = REPO_ROOT / "data" / "line_booking_pairs.csv"
DEFAULT_QA_JSON = WORKBOOK_DIR / "qa_examples_deidentified.json"
DEFAULT_RAW_PAIRS_JSON = WORKBOOK_DIR / "training_pairs_raw.json"

AUTO_REPLY_NAME = "自動回應訊息"
META_LINES = 3  # 帳號名稱 / 時區 / 下載時間


# ---------------------------------------------------------------------------
# Filename → display name
# ---------------------------------------------------------------------------

def _name_from_filename(filename: str) -> str | None:
    """'1002_20250617_20250725_林育慈.csv' → '林育慈'"""
    stem = filename.rsplit(".csv", 1)[0]
    parts = stem.split("_", 3)
    if len(parts) == 4:
        name = parts[3].strip()
        return name if len(name) >= 2 else None
    return None


# ---------------------------------------------------------------------------
# Stage heuristic (SOP keyword matching)
# ---------------------------------------------------------------------------

def classify_stage(customer_text: str, business_text: str) -> str:
    import re as _re  # local import to avoid top-level dependency duplication
    bt = business_text
    ct = customer_text
    both = ct + " " + bt

    # ── S6: pre-event logistics ───────────────────────────────────────────────
    # Business reply is primary signal; timing keywords can appear in either side
    _S6_KEYWORDS = [
        "明天見", "幾點到", "活動當天", "到了唷", "我們到了",
        "隔天過去", "當日看一下狀況",
        "陳列", "撤場", "撤收", "規劃師", "車號", "服務人員",
        "帶你們進來", "帶進來", "測量", "長寬", "桌子", "發票",
        "統編", "請購", "承辦人", "委托書",
        # Expanded from batch review (GAP-3)
        "走廊", "擺椅子", "鑰匙", "示意圖",
        "幾張桌", "停車", "進場時間", "抵達時間",
        # Round 2: S_PENDING recovery — venue/logistics bt signals
        "擺設", "哨點", "一起進", "帶你們", "可以租借",
    ]
    if any(k in bt for k in _S6_KEYWORDS):
        return "S6_PREDAY"
    # Timing keywords + S6-specific phrases may appear in either side
    if any(k in both for k in ["幾點到", "明天見", "到了唷", "我們到了", "車號", "帶你們進來"]):
        return "S6_PREDAY"
    # Customer gives venue/logistics info
    if any(k in ct for k in [
        "桌子", "走廊", "擺椅子", "椅子", "鑰匙", "示意圖",
        # Round 2: ct S6 signals (customer provides entry/setup info)
        "帶你們進來", "測量", "提前擺設", "去帶你們",
    ]):
        return "S6_PREDAY"
    # Pickup time coordination — only when customer is NOT still asking (GAP-5)
    _customer_still_asking = any(k in ct for k in ["請問", "有嗎", "可以嗎", "詢問", "有提供", "請問一下"])
    if "取餐" in both and any(k in both for k in ["幾點", "點半", "左右", "時候"]) \
            and not _customer_still_asking:
        return "S6_PREDAY"

    # ── S5 ───────────────────────────────────────────────────────────────────
    if any(k in ct for k in ["已轉帳", "已匯款", "已付款", "轉帳成功"]):
        return "S5_PAYMENT"
    if any(k in bt for k in ["已查收", "收到款"]) and (
        any(k in both for k in ["訂金", "匯款", "轉帳"])
        # Row 40: masked text loses "匯款" but retains "新臺幣" + amount pattern
        or "新臺幣" in ct
        or _re.search(r"\d[,，]\d+元", ct)
    ):
        return "S5_PAYMENT_ACK"

    # ── S4 ───────────────────────────────────────────────────────────────────
    if any(k in bt for k in ["匯款", "帳號", "訂金", "金融", "匯入", "尾款"]):
        return "S4_PAYMENT_INFO"
    if any(k in bt for k in ["姓名", "電話", "建檔", "為您登記", "留一下", "先為您登記"]):
        return "S4_BOOKING_ASK"
    if any(k in both for k in ["保留檔期", "先為您登記", "先登記"]):
        return "S4_BOOKING_ASK"
    # Post-booking follow-through: customer says "後續麻煩您規劃" = S4 wrap-up (GAP-3)
    if any(k in ct for k in ["後續麻煩", "麻煩規劃"]) and any(
        k in bt for k in ["下週", "主廚", "確認", "好的", "沒問題"]
    ):
        return "S4_BOOKING_ASK"

    # ── S3_QUOTE_INTRO: service framework introduction ────────────────────────
    # Must come BEFORE S3_QUOTE_SEND to prevent misclassification (GAP-1)
    if any(k in bt for k in [
        "服務範圍", "★", "低消", "外燴整體", "出車", "整體規劃", "低消是",
        "整體規劃的費用", "費用約", "費用大約", "方案介紹", "外帶菜單",
    ]):
        return "S3_QUOTE_INTRO"

    # ── S3_QUOTE_SEND: actual menu/photo delivery (narrowed — GAP-1) ─────────
    if "照片已傳送" in bt or "貼圖已傳送" in bt:
        return "S3_QUOTE_SEND"
    # Only when actual specific menu items/formal quote are listed
    if any(k in both for k in ["鹹點", "甜點", "飲品", "報價單", "估價單", "提供報價"]):
        return "S3_QUOTE_SEND"

    # ── S3_MENU_ADJUST: item-level adjustments (new — GAP-6) ─────────────────
    if any(k in both for k in [
        "換品項", "換成", "改成", "替換", "換掉", "調整品項",
        "幾隻", "一組幾", "可以加", "寶寶水", "飲料選項",
        # Round 2: S_PENDING recovery — portion/addon/flavor patterns
        "多加", "餐具", "口味", "返潮", "品項直接打",
        "幾道菜", "幾個點心", "個點心", "一人幾道",
    ]):
        return "S3_MENU_ADJUST"

    # ── S3_BUDGET_CONFIRM: price discussion with gate (GAP-4) ────────────────
    # Gate: business must NOT still be asking for date/headcount/venue
    _biz_still_collecting = any(
        k in bt for k in ["日期", "哪一天", "幾位", "地點", "場地", "什麼時候"]
    )
    if (any(k in both for k in ["預算", "價位", "幾萬", "幾千", "提案", "評估"])
            and not _biz_still_collecting):
        return "S3_BUDGET_CONFIRM"

    # ── S2 ───────────────────────────────────────────────────────────────────
    if any(k in both for k in [
        "禁忌食材", "食物過敏", "蔥蒜", "素食", "豬肉",
    ]) or ("禁忌" in both and "食材" in both):
        return "S2_DIETARY_ASK"
    if any(k in both for k in [
        "日期", "人數", "幾位", "幾人", "人份", "場地", "室內", "室外",
        "地點", "活動類型", "場合", "幾位賓客", "活動日期", "活動時間",
    ]) or _re.search(r"\d+\s*人", ct):  # Row 24: "大概150人" as headcount signal
        return "S2_DATA"

    # ── S1: inquiry intent ───────────────────────────────────────────────────
    if any(k in both for k in [
        "外燴", "詢問外燴", "請問外燴", "茶點", "茶會", "開幕",
        "週歲", "派對", "到府", "性別派對", "尾牙", "歡送", "迎新",
        "外帶",
    ]):
        return "S1_INQUIRY"

    # ── S0: opening greeting — ONLY when customer has no substantive intent ──
    # Negative condition: if customer message already has real inquiry → NOT S0 (GAP-2)
    _customer_has_intent = any(k in ct for k in [
        "外燴", "茶點", "外帶", "日期", "人數", "場地", "檔期",
        "報價", "詢問", "想請問", "多少", "可以", "有嗎", "有沒有",
    ])
    if not _customer_has_intent:
        if any(k in bt for k in ["您好", "旅圖", "我們是", "Map Lab", "歡迎", "外燴品牌"]):
            return "S0_OPENING"

    return "S_PENDING"


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def _parse_rows(path: Path) -> list[dict]:
    try:
        with path.open(encoding="utf-8-sig", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return []
    if len(lines) < META_LINES + 2:
        return []
    try:
        return list(csv.DictReader(io.StringIO("".join(lines[META_LINES:]))))
    except Exception:
        return []


def classify_stage_with_context(
    customer_text: str,
    business_text: str,
    prev_turns: list[tuple[str, str]] | None = None,
) -> str:
    """
    Context-aware stage classification using sliding window.
    If current pair classifies as S_PENDING, walk backward through prev_turns
    (up to 3) looking for an inheritable specific late-stage.
    """
    result = classify_stage(customer_text, business_text)
    if result != "S_PENDING" or not prev_turns:
        return result

    # Only inherit stages that naturally span multiple short acks.
    # Exclude S1/S2 — an ack after an inquiry is still ambiguous.
    INHERITABLE = {
        "S6_PREDAY",
        "S4_PAYMENT_INFO",
        "S4_BOOKING_ASK",
        "S5_PAYMENT",
        "S5_PAYMENT_ACK",
        "S3_MENU_ADJUST",
        "S3_QUOTE_SEND",
        "S3_BUDGET_CONFIRM",
    }

    for prev_ct, prev_bt in reversed(prev_turns[-3:]):
        prev_stage = classify_stage(prev_ct, prev_bt)
        if prev_stage in INHERITABLE:
            return prev_stage

    return "S_PENDING"


def extract_pairs(
    path: Path,
    window: int = 3,
) -> list[tuple[str, str, str, list[str], list[tuple[str, str]]]]:
    """
    Returns list of (customer_text, business_text, conv_hash, extra_mask_names, prev_turns).
    prev_turns: last `window` (ct, bt) raw pairs from this conversation (for context-aware
    classify_stage_with_context).
    """
    rows = _parse_rows(path)
    if not rows:
        return []

    conv_hash = scaffold.stable_id("line_oa_csv", path.name, prefix="conv")
    file_name = _name_from_filename(path.name)

    user_buffer: list[str] = []
    user_names: set[str] = set()
    pair_history: list[tuple[str, str]] = []
    pairs: list[tuple[str, str, str, list[str], list[tuple[str, str]]]] = []

    for row in rows:
        s_type = (row.get("傳送者類型") or "").strip()
        s_name = (row.get("傳送者名稱") or "").strip()
        content = (row.get("內容") or "").strip()

        if not content:
            continue

        if s_type == "User":
            user_buffer.append(content)
            if s_name and len(s_name) >= 2:
                user_names.add(s_name)

        elif s_type == "Account" and s_name == AUTO_REPLY_NAME:
            # Automated system reply — discard pending user buffer
            user_buffer = []
            user_names = set()

        elif s_type == "Account":
            # Real Mina / Account reply
            if user_buffer:
                customer_text = "\n".join(user_buffer)
                extra: list[str] = list(user_names)
                if file_name:
                    extra.append(file_name)
                prev_turns_snapshot = list(pair_history[-window:])
                pairs.append((customer_text, content, conv_hash, extra, prev_turns_snapshot))
                pair_history.append((customer_text, content))
                user_buffer = []
                user_names = set()
            # Account→Account sequence (Mina sends multiple msgs): skip

    return pairs


# ---------------------------------------------------------------------------
# Full CSV pipeline
# ---------------------------------------------------------------------------

def _llm_classify(ct_masked: str, bt_masked: str, prev_turns_masked: list[tuple[str, str]]) -> str:
    """Call local Ollama qwen2.5:14b for stage when keyword fails (S_PENDING fallback)."""
    try:
        from llm_stage_classifier import classify_with_llm
        return classify_with_llm({"ct": ct_masked, "bt": bt_masked, "prev_turns": prev_turns_masked})
    except Exception:
        return "S_PENDING"


def run_csv_pipeline(
    csv_dir: Path,
    base_mask_tokens: tuple[str, ...],
    limit: int | None = None,
    verbose: bool = False,
    use_llm: bool = False,
) -> tuple[list[dict], dict]:
    """Process all CSV files. Returns (samples, stats).
    use_llm=True: call Ollama qwen2.5:14b for residual S_PENDING after sliding window.
    Adds ~2.5s per S_PENDING sample; only enable when LLM throughput is acceptable.
    """
    csv_files = sorted(csv_dir.glob("*.csv"))
    if limit is not None:
        csv_files = csv_files[:limit]

    total = len(csv_files)
    empty_files = 0
    pairs_extracted = 0
    pairs_kept = 0
    stage_counter: Counter = Counter()
    samples: list[dict] = []

    for i, path in enumerate(csv_files):
        if verbose and i % 500 == 0:
            print(f"  [{i}/{total}] {path.name[:40]}...", file=sys.stderr)

        pairs = extract_pairs(path)
        if not pairs:
            empty_files += 1
            continue

        pairs_extracted += len(pairs)

        for customer_text, business_text, conv_hash, extra_names, prev_turns in pairs:
            # File-specific masks: per-file customer names + shared base tokens
            file_masks = tuple(
                list(base_mask_tokens) + [n for n in extra_names if len(n) >= 2]
            )
            stage = classify_stage_with_context(customer_text, business_text, prev_turns)
            # LLM fallback for residual S_PENDING (opt-in via use_llm flag)
            if stage == "S_PENDING" and use_llm:
                ct_m = scaffold.mask_pii(customer_text, file_masks)
                bt_m = scaffold.mask_pii(business_text, file_masks)
                ctx_m = [
                    (scaffold.mask_pii(pc, file_masks), scaffold.mask_pii(pb, file_masks))
                    for pc, pb in prev_turns[-2:]
                ]
                stage = _llm_classify(ct_m, bt_m, ctx_m)
            sample = scaffold.build_sample(
                source_kind="line_oa_csv",
                source_ref=conv_hash,
                stage=stage,
                customer_text=customer_text,
                business_text=business_text,
                mask_tokens=file_masks,
            )
            if sample:
                samples.append(sample)
                pairs_kept += 1
                stage_counter[stage] += 1

    stats = {
        "csv_dir": str(csv_dir),
        "total_csv_files": total,
        "empty_or_failed": empty_files,
        "pairs_extracted": pairs_extracted,
        "pairs_kept": pairs_kept,
        "stage_distribution": dict(stage_counter.most_common()),
    }
    return samples, stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, default=DEFAULT_CSV_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--booking-pairs", type=Path, default=DEFAULT_BOOKING_PAIRS)
    parser.add_argument("--qa-json", type=Path, default=DEFAULT_QA_JSON)
    parser.add_argument("--raw-pairs-json", type=Path, default=DEFAULT_RAW_PAIRS_JSON)
    parser.add_argument(
        "--write", action="store_true",
        help="write JSONL + manifest to --output-dir (gitignored path)"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="process only first N CSV files (smoke test)"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--report-dir", type=Path, default=None,
        help="write non-PII stats JSON here (committable path)"
    )
    parser.add_argument(
        "--llm-fallback", action="store_true",
        help="call local Ollama qwen2.5:14b for residual S_PENDING after sliding window (adds ~2.5s/sample)"
    )
    args = parser.parse_args(argv)

    # 1. Booking index (provides mask_tokens from contact_name column)
    print("Loading booking index...", file=sys.stderr)
    booking = scaffold.read_booking_index(args.booking_pairs)
    mask_tokens = booking.mask_tokens

    # 2. Seed samples from existing JSON files
    qa = scaffold.read_json(args.qa_json)
    raw_pairs = scaffold.read_json(args.raw_pairs_json)
    seed_samples = scaffold.samples_from_raw_pairs(raw_pairs, mask_tokens)
    seed_samples += scaffold.samples_from_qa_examples(qa, mask_tokens)
    print(f"Seed samples loaded: {len(seed_samples)}", file=sys.stderr)

    # 3. Full CSV pipeline
    print(f"Processing CSVs in {args.csv_dir} ...", file=sys.stderr)
    csv_samples, csv_stats = run_csv_pipeline(
        csv_dir=args.csv_dir,
        base_mask_tokens=mask_tokens,
        limit=args.limit,
        verbose=args.verbose,
        use_llm=args.llm_fallback,
    )
    print(
        f"CSV pipeline done: {csv_stats['pairs_kept']} pairs kept "
        f"from {csv_stats['total_csv_files']} files",
        file=sys.stderr,
    )

    # 4. Combine all samples
    all_samples = seed_samples + csv_samples
    manifest = scaffold.make_manifest(all_samples, booking)
    manifest["csv_pipeline"] = csv_stats
    manifest["seed_samples"] = len(seed_samples)
    manifest["csv_samples"] = len(csv_samples)
    manifest["run_ts"] = datetime.now(timezone.utc).isoformat()

    # 5. Write JSONL + manifest (gitignored)
    if args.write:
        write_outputs_safe(args.output_dir, all_samples, manifest, mask_tokens)

    # 6. Write committable stats report (no PII)
    if args.report_dir:
        args.report_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "run_date": manifest["run_ts"][:10],
            "source_script": "line_oa_csv_parser.py",
            "csv_dir_label": "line_oa_chat_csv_260622_213421 (external drive, read-only)",
            "total_csv_files": csv_stats["total_csv_files"],
            "empty_or_failed_files": csv_stats["empty_or_failed"],
            "pairs_extracted": csv_stats["pairs_extracted"],
            "pairs_kept": csv_stats["pairs_kept"],
            "auto_reply_filter": "excluded 自動回應訊息 rows",
            "seed_samples": len(seed_samples),
            "total_training_samples": len(all_samples),
            "stage_distribution": csv_stats["stage_distribution"],
            "split_distribution": manifest["sample_counts"]["by_split"],
            "source_distribution": manifest["sample_counts"]["by_source"],
            "answer_side_gap": manifest["answer_side_gap"],
            "pii_policy": {
                "raw_pii_in_commit": False,
                "training_jsonl_gitignored": True,
                "masking_applied": ["姓名", "電話", "email", "url", "日期", "地址"],
            },
        }
        report_path = args.report_dir / "run_report.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Stats report → {report_path}", file=sys.stderr)

    # 7. Print summary
    result = {
        "total_samples": len(all_samples),
        "csv_samples": len(csv_samples),
        "seed_samples": len(seed_samples),
        "stage_distribution": csv_stats["stage_distribution"],
        "split_distribution": manifest["sample_counts"]["by_split"],
        "written": args.write,
        "output_dir": str(args.output_dir) if args.write else None,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
