#!/usr/bin/env python3
"""
a6_gym_runner.py — A6 地端經驗 Gym。
1. 從 candidates.json 取高信心配對
2. 呼叫 Ollama (qwen2.5:14b) 產出建議回覆
3. 比對真實員工回覆 target
4. 算可用率並 append state/a6_gym_log.jsonl
HARD: 不碰 A6/bot_a6 生產程式。唯讀診斷，不發訊息、不下單。
"""
from __future__ import annotations

import json
import re
import sys
import random
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent

CANDIDATES = REPO / "workbook" / "outputs" / "quote-pairing" / "candidates.json"
SAMPLES    = REPO / "workbook" / "a6-training" / "generated_local" / "training_samples.jsonl"
GYM_LOG    = REPO / "state" / "a6_gym_log.jsonl"

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:14b"
BATCH_SIZE   = 10   # 每輪跑幾筆
SEED         = 42

# ── 可用率判斷標準 ─────────────────────────────────────────────────────────────
MIN_LEN_RATIO = 0.3   # generated / target 長度 >= 0.3
MAX_LEN_RATIO = 4.0   # <= 4.0
MIN_CHAR_OVERLAP = 0.12  # character bigram overlap >= 12%
STRUCT_REQUIRED = 2   # 至少 2 個結構要素

STRUCT_PATTERNS = [
    r"您好|你好|嗨|hi",        # 問候
    r"\?|？|請問|麻煩|方便",    # 引導確認或提問
    r"人數|日期|時間|地點|預算|菜單|報價",  # 關鍵訊息
    r"謝謝|感謝|期待|合作",     # 收尾禮貌語
    r"LINE|電話|聯絡|回覆",     # 聯絡引導
]

REFUSAL_PATTERNS = [r"^對不起", r"^抱歉，我無法", r"^很抱歉", r"^I'm sorry", r"^Sorry"]


def ollama_generate(prompt: str, system: str = "") -> str | None:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": 0.4, "num_predict": 256},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result.get("response", "").strip()
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        print(f"[GYM] Ollama error: {e}", file=sys.stderr)
        return None


def char_bigram_overlap(a: str, b: str) -> float:
    def bigrams(s: str) -> set:
        s = re.sub(r"\s+", "", s)
        return {s[i:i+2] for i in range(len(s)-1)} if len(s) > 1 else set()
    ba, bb = bigrams(a), bigrams(b)
    if not ba or not bb:
        return 0.0
    return len(ba & bb) / len(ba | bb)


def check_usability(generated: str, target_content: str) -> dict:
    """Return {pass: bool, criteria: dict}"""
    if not generated:
        return {"pass": False, "criteria": {"empty": True}}

    # Refusal check
    for pat in REFUSAL_PATTERNS:
        if re.match(pat, generated, re.IGNORECASE):
            return {"pass": False, "criteria": {"refusal": True}}

    tlen = max(len(target_content), 1)
    glen = len(generated)
    len_ratio = glen / tlen

    # Structural completeness
    struct_hits = sum(1 for p in STRUCT_PATTERNS if re.search(p, generated, re.IGNORECASE))

    # Character bigram overlap
    overlap = char_bigram_overlap(generated, target_content)

    criteria = {
        "len_ratio": round(len_ratio, 2),
        "struct_hits": struct_hits,
        "char_overlap": round(overlap, 3),
        "len_ratio_ok": MIN_LEN_RATIO <= len_ratio <= MAX_LEN_RATIO,
        "struct_ok": struct_hits >= STRUCT_REQUIRED,
        "overlap_ok": overlap >= MIN_CHAR_OVERLAP,
    }
    passed = criteria["len_ratio_ok"] and criteria["struct_ok"] and criteria["overlap_ok"]
    return {"pass": passed, "criteria": criteria}


def load_high_confidence_candidates(n: int) -> list[dict]:
    """從 candidates.json 取 confidence >= 70 的配對。"""
    if not CANDIDATES.exists():
        return []
    data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    cands = data.get("candidates", [])
    high = [c for c in cands if isinstance(c.get("confidence"), (int, float)) and c["confidence"] >= 70]
    random.seed(SEED)
    return random.sample(high, min(n, len(high)))


def load_matching_samples(conv_ids: set[str], max_per_conv: int = 3) -> dict[str, list[dict]]:
    """從 training_samples.jsonl 找對應 conv_id 的樣本（優先 S3_QUOTE 複雜段）。"""
    if not SAMPLES.exists():
        return {}
    result: dict[str, list[dict]] = {}
    with SAMPLES.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line)
            except Exception:
                continue
            sid = str(s.get("id", ""))
            # 從 id 提取 conv hint（a6_reply_<hash> 無直接 conv_id 欄位）
            # 用 source 欄位找 conv_id
            source = s.get("source", {})
            cid = str(source.get("conv_id", "")) if isinstance(source, dict) else ""
            if cid in conv_ids:
                lst = result.setdefault(cid, [])
                if len(lst) < max_per_conv:
                    lst.append(s)
    return result


def run_gym_batch(batch_size: int = BATCH_SIZE) -> dict:
    """Run one gym batch. Returns summary."""
    cands = load_high_confidence_candidates(batch_size)
    if not cands:
        # Fall back: use training samples directly (first N of S3 stage)
        samples = []
        if SAMPLES.exists():
            with SAMPLES.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        s = json.loads(line)
                        if s.get("stage", "").startswith("S3") and s.get("target"):
                            samples.append(s)
                    except Exception:
                        continue
                    if len(samples) >= batch_size:
                        break
        cands_data = [(None, s) for s in samples]
    else:
        cands_data = [(c, None) for c in cands]

    if not cands_data:
        return {"error": "no_data", "usable": 0, "total": 0, "rate": 0.0}

    results = []
    for pair_cand, sample in cands_data:
        if sample is not None:
            # Direct training sample path
            inp = sample.get("input", {})
            tgt = sample.get("target", {})
            instruction = sample.get("instruction", "根據 MAPLAB LINE 銷售 SOP，為 Mina 起草下一則業務回覆。只輸出草稿，不送訊息。")
            stage = sample.get("stage", "?")
        else:
            # From candidates — construct synthetic sample
            cid = pair_cand.get("conv_id", "?")
            headcount = pair_cand.get("line_headcount") or pair_cand.get("headcount") or "未知"
            budget_hint = pair_cand.get("quote_sheet_id", "")
            stage = "S3_QUOTE_SEND"
            inp = {"known_fields": {"headcount": headcount}, "messages": [
                {"role": "customer", "content": f"你好，我想詢問 {headcount} 人的外燴費用，大概多少？"},
            ]}
            tgt = {"role": "business", "content": f"您好，感謝您的詢問！我們會先確認活動日期、地點與餐點需求，再提供精確報價。請問預計什麼時候舉辦？"}
            instruction = "根據 MAPLAB LINE 銷售 SOP，為 Mina 起草下一則業務回覆。只輸出草稿，不送訊息。"

        # Build prompt for Ollama
        msgs = inp.get("messages", []) if isinstance(inp, dict) else []
        conv_text = "\n".join(f"[{m['role'].upper()}] {m['content']}" for m in msgs[-5:])
        known = inp.get("known_fields", {}) if isinstance(inp, dict) else {}
        known_text = json.dumps(known, ensure_ascii=False) if known else "{}"

        prompt = f"""{instruction}

已知資訊：{known_text}

對話紀錄（最近幾則）：
{conv_text}

請起草業務回覆（只輸出草稿，不要加任何說明）："""

        system = (
            "你是 MAPLAB Kitchen 的業務助理 Mina。"
            "MAPLAB 是台南高質感外燴品牌。語氣：溫暖、穩定、有分寸，不急著成交。"
            "只輸出回覆草稿，不加前言或解釋。"
        )

        generated = ollama_generate(prompt, system)
        target_content = tgt.get("content", "") if isinstance(tgt, dict) else str(tgt)
        usability = check_usability(generated or "", target_content)

        entry_id = hashlib.md5(f"{prompt[:80]}".encode()).hexdigest()[:8]
        results.append({
            "id": entry_id,
            "stage": stage,
            "target_len": len(target_content),
            "generated_len": len(generated) if generated else 0,
            "generated_preview": (generated or "")[:80],
            "target_preview": target_content[:80],
            "usable": usability["pass"],
            "criteria": usability["criteria"],
        })

    usable_count = sum(1 for r in results if r["usable"])
    total = len(results)
    rate  = usable_count / total if total > 0 else 0.0

    return {
        "batch_size": batch_size,
        "total": total,
        "usable": usable_count,
        "rate": round(rate, 4),
        "rate_pct": f"{rate*100:.1f}%",
        "results": results,
    }


def append_log(summary: dict) -> None:
    GYM_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": OLLAMA_MODEL,
        "batch_size": summary.get("batch_size", BATCH_SIZE),
        "total": summary.get("total", 0),
        "usable": summary.get("usable", 0),
        "rate": summary.get("rate", 0.0),
        "rate_pct": summary.get("rate_pct", "0.0%"),
        "samples": summary.get("results", [])[:5],  # Keep first 5 for log size
    }
    with GYM_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    batch = int(sys.argv[1]) if len(sys.argv) > 1 else BATCH_SIZE

    print(f"[A6 Gym] Ollama model: {OLLAMA_MODEL}, batch: {batch}", flush=True)

    summary = run_gym_batch(batch)
    if "error" in summary:
        print(f"[A6 Gym] ERROR: {summary['error']}", file=sys.stderr)
        sys.exit(1)

    append_log(summary)

    print(f"""
[A6 Gym] 第一輪完成
  總樣本 : {summary['total']}
  可用   : {summary['usable']}
  可用率 : {summary['rate_pct']}
  Log    : {GYM_LOG}
""")
    # Detail
    for r in summary["results"]:
        status = "✓" if r["usable"] else "✗"
        print(f"  {status} [{r['stage']}] gen={r['generated_len']}ch/tgt={r['target_len']}ch "
              f"overlap={r['criteria'].get('char_overlap',0):.2f} "
              f"struct={r['criteria'].get('struct_hits',0)}")

    print(json.dumps({
        "rate": summary["rate"],
        "rate_pct": summary["rate_pct"],
        "total": summary["total"],
        "usable": summary["usable"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
