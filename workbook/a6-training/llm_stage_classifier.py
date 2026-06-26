#!/usr/bin/env python3
"""
A6 Stage LLM Classifier — Ollama 地端驗證
對 sliding window 後仍是 S_PENDING 的殘餘樣本，用 qwen2.5:14b + rubric 重新判 stage。
只跑本地 Ollama，不送外部 API。
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

OLLAMA_BASE = "http://localhost:11434"
MODEL = "qwen2.5:14b"

RUBRIC_COMPACT = """
## 7段 SOP stage 判斷（精簡版）

優先順序（高→低）：S6 > S5 > S4 > S3_QUOTE_INTRO > S3_QUOTE_SEND > S3_MENU_ADJUST > S3_BUDGET_CONFIRM > S2_DIETARY_ASK > S2_DATA > S1_INQUIRY > S0_OPENING > S_PENDING

- **S6_PREDAY**：活動前場地/後勤協調（桌子/鑰匙/到達時間/車號/擺設/服務人員/哨點/進場時間）
- **S5_PAYMENT_ACK**：業務確認收到款項（含 已查收/訂金/匯款 訊號）
- **S5_PAYMENT**：客人通知已付款（已轉帳/已匯款）
- **S4_PAYMENT_INFO**：業務提供匯款帳號/訂金金額
- **S4_BOOKING_ASK**：業務請客人留姓名電話/建檔；或客人說「後續麻煩您規劃」
- **S3_BUDGET_CONFIRM**：客人明確提出預算金額，業務確認（且業務不再問基本資料）
- **S3_MENU_ADJUST**：具體品項替換/份數確認/口味/多加（換成/改成/幾隻/餐具/口味/多加）
- **S3_QUOTE_SEND**：業務傳送具體菜單/照片/報價單（鹹點/甜點/飲品/報價單/照片已傳送）
- **S3_QUOTE_INTRO**：業務介紹服務框架/費用區間（低消/方案介紹/費用大約/整體規劃）
- **S2_DIETARY_ASK**：詢問禁忌食材/過敏/素食
- **S2_DATA**：收集日期/人數/地點/場合基本資訊
- **S1_INQUIRY**：外燴/外帶/茶點等服務詢問意圖
- **S0_OPENING**：純問候，客人無實質詢問
- **S_PENDING**：以上皆不符合（注意：短確認語如「好的」如有業務 S6/S4 回覆訊號，仍可歸類）

## 關鍵規則
1. **業務回覆 > 客人說什麼**：業務說「桌子幾張？」→ S6，不管客人說了什麼
2. 客人說「好的」但業務回 S4/S6/S3 訊號 → 歸那個 stage，不是 S_PENDING
3. 上下文(前幾輪)若業務在討論 S6 後勤，當前純 ack → 仍是 S6
"""


def _call_ollama(prompt: str) -> str:
    import urllib.request
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 32},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())["response"].strip()


VALID_STAGES = {
    "S0_OPENING", "S1_INQUIRY",
    "S2_DATA", "S2_DIETARY_ASK",
    "S3_BUDGET_CONFIRM", "S3_MENU_ADJUST", "S3_QUOTE_INTRO", "S3_QUOTE_SEND",
    "S4_BOOKING_ASK", "S4_PAYMENT_INFO",
    "S5_PAYMENT", "S5_PAYMENT_ACK",
    "S6_PREDAY", "S_PENDING",
}


def classify_with_llm(sample: dict) -> str:
    prev_str = ""
    if sample.get("prev_turns"):
        prev_str = "\n## 對話上下文（前幾輪）\n"
        for i, (pc, pb) in enumerate(sample["prev_turns"], 1):
            prev_str += f"[前{len(sample['prev_turns'])-i+1}輪] 客人：{pc[:120]}\n[前{len(sample['prev_turns'])-i+1}輪] 業務：{pb[:120]}\n"

    prompt = f"""你是 MAPLAB LINE OA 對話 stage 分類器。
{RUBRIC_COMPACT}
{prev_str}
## 當前交換（待分類）
客人：{sample['ct'][:200]}
業務：{sample['bt'][:200]}

## 任務
請只輸出 stage 代碼（如 S6_PREDAY），不要說明，不要換行。
"""

    raw = _call_ollama(prompt)
    # Extract first valid stage code from response
    for candidate in re.findall(r"S\w+", raw):
        if candidate in VALID_STAGES:
            return candidate
    return "S_PENDING"


def run_validation(sample_path: Path, output_path: Path) -> dict:
    samples = json.loads(sample_path.read_text())
    results = []
    t0 = time.time()

    for i, s in enumerate(samples):
        stage = classify_with_llm(s)
        results.append({
            "idx": i,
            "ct": s["ct"][:80],
            "bt": s["bt"][:80],
            "llm_stage": stage,
            "has_ctx": bool(s.get("prev_turns")),
        })
        elapsed = time.time() - t0
        avg = elapsed / (i + 1)
        remaining = avg * (len(samples) - i - 1)
        print(f"[{i+1:02d}/{len(samples)}] {stage:<22} | avg {avg:.1f}s | ETA {remaining:.0f}s", flush=True)

    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    stage_dist = {}
    for r in results:
        stage_dist[r["llm_stage"]] = stage_dist.get(r["llm_stage"], 0) + 1

    still_pending = stage_dist.get("S_PENDING", 0)
    rescued = len(results) - still_pending

    print(f"\n=== LLM 驗證結果 ===")
    print(f"總樣本: {len(results)}")
    print(f"LLM 救出（非 S_PENDING）: {rescued}/{len(results)} = {rescued/len(results)*100:.1f}%")
    print(f"仍是 S_PENDING: {still_pending} = {still_pending/len(results)*100:.1f}%")
    print(f"\nLLM 分類分佈:")
    for stage, cnt in sorted(stage_dist.items(), key=lambda x: -x[1]):
        print(f"  {stage:<22} {cnt:>3} ({cnt/len(results)*100:.1f}%)")

    return {"stage_dist": stage_dist, "total": len(results), "rescued": rescued}


if __name__ == "__main__":
    base = Path(__file__).parent
    sample_path = base / "generated_local" / "llm_pending_sample.json"
    output_path = base / "generated_local" / "llm_validation_results.json"

    if not sample_path.exists():
        print(f"ERROR: {sample_path} not found — run extract step first")
        raise SystemExit(1)

    run_validation(sample_path, output_path)
