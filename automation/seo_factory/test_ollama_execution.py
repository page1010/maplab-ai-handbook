#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime

import requests

from seo_factory import load_factory_config, run_factory


def check_ollama_health(base_url: str) -> dict:
    out = {"ok": False, "base_url": base_url}
    try:
        tags = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=10)
        out["tags_status"] = tags.status_code
        out["models"] = [m.get("name") for m in tags.json().get("models", [])] if tags.ok else []
    except Exception as e:
        out["error"] = f"tags_error:{e}"
        return out

    model = os.getenv("OLLAMA_MODEL_MEDIUM") or os.getenv("OLLAMA_MODEL_SMALL") or "llama3.1:latest"
    try:
        payload = {"model": model, "prompt": "請回傳一行文字：本地模型測試成功。", "stream": False}
        gen = requests.post(f"{base_url.rstrip('/')}/api/generate", json=payload, timeout=30)
        out["generate_status"] = gen.status_code
        resp = gen.json().get("response", "").strip() if gen.ok else ""
        out["sample_response"] = resp[:200]
        out["ok"] = bool(gen.ok and resp)
    except Exception as e:
        out["error"] = f"generate_error:{e}"
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Test local Ollama execution for SEO factory.")
    parser.add_argument("--pillar", default="corporate", help="Run one pillar only. Default: corporate")
    parser.add_argument("--publish", action="store_true", help="Also publish WordPress draft")
    args = parser.parse_args()

    cfg = load_factory_config(publish_enabled=args.publish)
    health = check_ollama_health(cfg.ollama_base_url)
    if not health.get("ok"):
        print(json.dumps({"stage": "ollama-health", "result": health}, ensure_ascii=False, indent=2))
        return

    result = run_factory(publish=args.publish, pillars_filter=[args.pillar])
    output = {
        "stage": "pipeline-run",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ollama_health": health,
        "result": result,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
