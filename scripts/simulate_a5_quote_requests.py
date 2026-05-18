#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "bot_a6") not in sys.path:
    sys.path.insert(0, str(ROOT / "bot_a6"))

from a5_quote_engine import run_a5_local_quote


SIMULATED_REQUESTS = [
    "報價 陳小姐 週歲派對 30人 預算2萬 台南東區 室內 甜點多一點 不吃牛",
    "報價 台南科技公司 開幕茶會 80人 預算5萬 需統編 台南永康 需要飲品和質感鹹食",
    "報價 林先生 婚禮 after party 60人 預算4萬 嘉義市區 鹹食多一點 不要海鮮",
    "報價 王小姐 性別揭曉派對 24人 預算15000 台南安平 希望粉藍色甜點 不要酒",
    "報價 品牌發表會 120人 預算6萬 高雄展覽館 企業版 需要茶點 不確定樓層搬運",
]


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"JOB-A5-SIM-{stamp}"
    review_dir = ROOT / "workbook" / "reviews" / run_id
    review_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for index, request in enumerate(SIMULATED_REQUESTS, start=1):
        job_id = f"{run_id}-{index:02d}"
        result = run_a5_local_quote(
            request,
            user_name="simulation",
            history=[],
            job_id=job_id,
            engine="ollama",
        )
        results.append(
            {
                "index": index,
                "request": request,
                "engine_used": result.engine_used,
                "model_used": result.model_used,
                "fallback_used": result.fallback_used,
                "bundle_dir": result.bundle_dir,
                "answer": result.answer,
                "error": result.error,
            }
        )
        print(f"[{index}/5] {result.engine_used} {result.model_used} -> {result.bundle_dir or 'no bundle'}")

    (review_dir / "simulation_results.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "count": len(results),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (review_dir / "simulation_report.md").write_text(_render_report(run_id, results), encoding="utf-8")
    print(f"report={review_dir / 'simulation_report.md'}")
    return 0


def _render_report(run_id: str, results: list[dict]) -> str:
    lines = [
        f"# A5 Quote Simulation Report — {run_id}",
        "",
        f"created_at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Summary",
        "",
        f"- total_requests: {len(results)}",
        f"- successful_outputs: {sum(1 for item in results if item.get('answer'))}",
        "- mode: local Ollama quote simulation, no Google Sheets / GAS / Telegram send",
        "",
    ]
    for item in results:
        lines.extend(
            [
                f"## Case {item['index']}",
                "",
                f"request: {item['request']}",
                f"engine_used: {item['engine_used']}",
                f"model_used: {item['model_used']}",
                f"bundle_dir: `{item.get('bundle_dir') or ''}`",
                "",
                "### Output",
                "",
                item["answer"].strip(),
                "",
            ]
        )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
