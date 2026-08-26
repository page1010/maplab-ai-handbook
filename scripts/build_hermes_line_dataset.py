#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


DEFAULT_SOURCE = Path("/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421")
DEFAULT_OUTPUT = Path("/Volumes/MacExternal/maplab-data/a6-hermes-training")


def conversation_id(path: Path) -> str:
    return hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:16]


def read_messages(path: Path) -> list[dict]:
    rows = list(csv.reader(path.open(encoding="utf-8-sig", errors="replace", newline="")))
    header_index = next((i for i, row in enumerate(rows) if row and row[0] == "傳送者類型"), None)
    if header_index is None:
        return []
    messages = []
    for row in rows[header_index + 1:]:
        if len(row) < 5 or row[0] not in {"User", "Account"}:
            continue
        messages.append({"side": row[0], "sender": row[1].strip(), "date": row[2], "time": row[3], "text": row[4].strip()})
    return messages


def anonymize(messages: list[dict]) -> list[dict]:
    customer_names = {
        item["sender"] for item in messages
        if item["side"] == "User" and item["sender"] and item["sender"].lower() != "unknown"
    }
    result = []
    for item in messages:
        text = item["text"]
        for name in sorted(customer_names, key=len, reverse=True):
            text = text.replace(name, "[CUSTOMER]")
        # The sender field is the primary source of the customer name.  Remove
        # it completely while retaining Mina/automatic-response distinction.
        sender = "[CUSTOMER]" if item["side"] == "User" else item["sender"]
        result.append({**item, "sender": sender, "text": text})
    return result


def classify_stage(text: str) -> str:
    if re.search(r"訂金|匯款|帳號|尾款", text): return "S4_PAYMENT"
    if re.search(r"照片已傳送|菜單這邊|報價明細|品項", text): return "S3_QUOTE_SEND"
    if re.search(r"禁忌|過敏|素食|不吃", text): return "S2_DIETARY"
    if re.search(r"日期|哪一天|人數|幾位|地點|地址|時段|預算", text): return "S2_DATA"
    if re.search(r"費用|低消|起皆可製作|服務範圍", text): return "S3_QUOTE_INTRO"
    if re.search(r"您好|你好|歡迎", text): return "S0_OPENING"
    return "S_PENDING"


def build_pairs(path: Path) -> list[dict]:
    messages = anonymize(read_messages(path))
    cid = conversation_id(path)
    split = "eval" if int(cid[:4], 16) % 10 < 2 else "train"
    pairs = []
    history: list[dict] = []
    i = 0
    turn = 0
    while i < len(messages):
        item = messages[i]
        if item["side"] != "User":
            history.append({"role": "business", "content": item["text"]})
            i += 1
            continue
        customer_block = []
        while i < len(messages) and messages[i]["side"] == "User":
            if messages[i]["text"]:
                customer_block.append(messages[i]["text"])
            i += 1
        business_block = []
        while i < len(messages) and messages[i]["side"] == "Account":
            sender = messages[i]["sender"]
            if sender not in {"自動回應訊息", "系統訊息"} and messages[i]["text"]:
                business_block.append(messages[i]["text"])
            i += 1
        if not customer_block:
            continue
        customer_text = "\n".join(customer_block)
        history.append({"role": "customer", "content": customer_text})
        if business_block:
            target = "\n\n".join(business_block)
            turn += 1
            pairs.append({
                "id": f"{cid}-{turn:03d}",
                "conversation_id": cid,
                "split": split,
                "stage": classify_stage(target),
                "context": history[-8:],
                "customer": customer_text,
                "target": target,
                "source": {"drive": "MacExternal", "filename_removed": True},
            })
            history.append({"role": "business", "content": target})
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    outputs = {"train": (args.output / "train.jsonl").open("w", encoding="utf-8"), "eval": (args.output / "eval.jsonl").open("w", encoding="utf-8")}
    counts = {"files": 0, "train": 0, "eval": 0, "pairs": 0}
    stages: dict[str, int] = {}
    try:
        for path in sorted(args.source.glob("*.csv")):
            counts["files"] += 1
            for pair in build_pairs(path):
                outputs[pair["split"]].write(json.dumps(pair, ensure_ascii=False) + "\n")
                counts[pair["split"]] += 1
                counts["pairs"] += 1
                stages[pair["stage"]] = stages.get(pair["stage"], 0) + 1
    finally:
        for handle in outputs.values(): handle.close()
    manifest = {"schema": "maplab.hermes.line_pairs.v1", "source": str(args.source), "output": str(args.output), "counts": counts, "stages": stages, "anonymization": "customer sender names removed/replaced; conversation IDs hashed", "split": "80/20 by conversation hash"}
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
