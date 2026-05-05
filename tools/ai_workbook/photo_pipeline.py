import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

from .paths import OUTPUTS_DIR, ROOT


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def build_photo_classification_plan(scan_dir: str = "data/telegram-photos") -> Path:
    base = ROOT / scan_dir
    files = []
    if base.exists():
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                files.append(p)

    plan = []
    for p in files:
        target_cluster = _infer_cluster(p.name)
        suggested_path = f"assets/{target_cluster}/{p.name}"
        plan.append(
            {
                "source": str(p.relative_to(ROOT)),
                "target_cluster": target_cluster,
                "suggested_target": suggested_path,
                "confidence": 0.55,
                "status": "proposed_only",
            }
        )

    counter = Counter([x["target_cluster"] for x in plan])
    payload = {
        "date": str(date.today()),
        "scan_dir": scan_dir,
        "total_images": len(plan),
        "cluster_counts": dict(counter),
        "rules": [
            "先產生分類計畫，不直接搬檔",
            "低信心項目交給 ollama/gemini 補分類",
            "人工核准後才 move",
        ],
        "items": plan,
    }
    out_dir = OUTPUTS_DIR / str(date.today()) / "T-A4-photo-classification-restart"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "classification_plan.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _infer_cluster(name: str) -> str:
    n = name.lower()
    if re.search(r"wedding|婚|宴|迎賓", n):
        return "wedding"
    if re.search(r"birthday|抓周|週歲|party", n):
        return "birthday"
    if re.search(r"corp|企業|會議|品牌|開幕", n):
        return "corporate"
    return "uncategorized"

