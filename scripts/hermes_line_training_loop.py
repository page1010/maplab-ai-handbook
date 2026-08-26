#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bot_a6"))
from hermes_telegram_gateway import load_chain, load_free_env_key, local_ollama_chat, openrouter_chat


DATA_ROOT = Path("/Volumes/MacExternal/maplab-data/a6-hermes-training")
RESULT_ROOT = DATA_ROOT / "runs"
STATE_PATH = DATA_ROOT / "loop_state.json"
LESSONS_PATH = DATA_ROOT / "current_lessons.md"
SIGNALS = ("日期", "人數", "地點", "地址", "時間", "時段", "預算", "禁忌", "過敏", "素食", "菜單", "報價", "訂金", "匯款", "檔期", "服務費")


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def generate(messages: list[dict]) -> tuple[str, str]:
    key = load_free_env_key()
    if key:
        for model in load_chain()[:2]:
            try:
                reply = openrouter_chat(key, model, messages, timeout=45)
            except Exception:
                continue
            if reply:
                return reply, model
    reply = local_ollama_chat(messages)
    return (reply or ""), "local-fallback"


def score_reply(generated: str, target: str) -> dict:
    required = [signal for signal in SIGNALS if signal in target]
    hits = [signal for signal in required if signal in generated]
    coverage = len(hits) / len(required) if required else 1.0
    target_money = set(re.findall(r"(?:NT\$|\$)?\s*\d[\d,]*(?:萬|元)?", target))
    generated_money = set(re.findall(r"(?:NT\$|\$)\s*\d[\d,]*|\d+(?:\.\d+)?萬|\d[\d,]+元", generated))
    unsupported_money = sorted(generated_money - target_money)
    question_ok = not re.search(r"[？?]|請問|方便|麻煩", target) or bool(re.search(r"[？?]|請問|方便|麻煩", generated))
    length_ratio = len(generated) / max(len(target), 1)
    length_ok = 0.25 <= length_ratio <= 2.5
    score = round(coverage * 55 + (20 if question_ok else 0) + (15 if length_ok else 0) + (10 if not unsupported_money else 0))
    passed = score >= 75 and coverage >= 0.75 and not unsupported_money and length_ok
    return {"score": score, "pass": passed, "required_signals": required, "hit_signals": hits, "missed_signals": sorted(set(required) - set(hits)), "unsupported_money": unsupported_money, "question_ok": question_ok, "length_ratio": round(length_ratio, 2)}


def build_prompt(sample: dict, examples: list[dict], lessons: str) -> list[dict]:
    example_text = "\n\n".join(f"客戶：{x['customer']}\nMina：{x['target']}" for x in examples)
    context = "\n".join(f"{x['role']}：{x['content']}" for x in sample.get("context", [])[-6:])
    system = (
        "你是 MAPLAB Hermes 客服助理。請依 Mina 歷史回覆風格，只輸出下一則可直接使用的繁體中文回覆。"
        "優先回答客人當下問題，再補問下一個必要欄位；不要重問已知資料；不得杜撰價格、檔期或政策。"
        "保持手機可讀，不輸出程式碼、JSON、分析或格式規範。\n"
        + lessons[-2500:]
        + "\n\n參考案例：\n" + example_text
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": f"對話：\n{context}\n\n客戶最新訊息：{sample['customer']}"}]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=12)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--stage", default="")
    args = parser.parse_args()
    if not (DATA_ROOT / "train.jsonl").exists() or not (DATA_ROOT / "eval.jsonl").exists():
        print("dataset_missing", file=sys.stderr)
        return 2
    train, evaluation = load_jsonl(DATA_ROOT / "train.jsonl"), load_jsonl(DATA_ROOT / "eval.jsonl")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    seed = args.seed if args.seed is not None else int(datetime.now().strftime("%Y%m%d"))
    rng = random.Random(seed)
    evaluation_pool = [item for item in evaluation if item["stage"] == args.stage] if args.stage else evaluation
    samples = rng.sample(evaluation_pool, min(args.batch, len(evaluation_pool)))
    by_stage: dict[str, list[dict]] = {}
    for item in train:
        by_stage.setdefault(item["stage"], []).append(item)
    lessons = LESSONS_PATH.read_text(encoding="utf-8") if LESSONS_PATH.exists() else ""
    results = []
    for sample in samples:
        pool = [x for x in by_stage.get(sample["stage"], []) if x["conversation_id"] != sample["conversation_id"]]
        examples = rng.sample(pool, min(2, len(pool)))
        generated, provider = generate(build_prompt(sample, examples, lessons))
        results.append({"id": sample["id"], "stage": sample["stage"], "provider": provider, "customer": sample["customer"], "generated": generated, "target": sample["target"], "evaluation": score_reply(generated, sample["target"])})
    passed = sum(item["evaluation"]["pass"] for item in results)
    missed: dict[str, int] = {}
    for item in results:
        for signal in item["evaluation"]["missed_signals"]:
            missed[signal] = missed.get(signal, 0) + 1
    summary = {"run_id": f"HERMES-LINE-{stamp}", "created_at": datetime.now(timezone.utc).isoformat(), "batch": len(results), "passed": passed, "pass_rate": round(passed / max(len(results), 1), 4), "mean_score": round(sum(x["evaluation"]["score"] for x in results) / max(len(results), 1), 1), "missed_signals": dict(sorted(missed.items(), key=lambda x: -x[1])), "results": results}
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)
    run_path = RESULT_ROOT / f"{summary['run_id']}.json"
    run_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LESSONS_PATH.write_text("# Hermes rolling lessons\n\n下一輪優先補齊：" + "、".join(list(summary["missed_signals"])[:8]) + "。不得發明真實回覆未出現的價格。\n", encoding="utf-8")
    STATE_PATH.write_text(json.dumps({"latest_run": str(run_path), "pass_rate": summary["pass_rate"], "mean_score": summary["mean_score"], "next_prompt": "讀 manifest、current_lessons 與 latest run；針對最低分 stage 再跑一輪，確認 pass_rate 是否改善。"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"} | {"receipt": str(run_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
