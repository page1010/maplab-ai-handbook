#!/usr/bin/env python3
"""Quota Sentinel — provider-neutral usage/availability dry-run.

讀 config/providers.yml，對每個 provider 依「資料來源優先順序」偵測，
寫出 state/provider_status.json。不讀取、不印出任何 secret value。

資料來源優先順序（見 LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md §六）：
  official usage/quota API（MAPLAB 政策下預設 blocked_by_policy）
  → provider console export / official CLI
  → local request ledger
  → authenticated CLI health / 429 分類
  → manual override
  → unknown

執行：
  python3 local_model_evolution/bin/quota_sentinel.py

此腳本設計為在真正的 runtime 機器（例如 Mac mini）上執行才有意義；
在沒有 Ollama / Codex CLI / claude CLI 訂閱環境的沙盒中執行時，
所有 CLI health 檢查會誠實回報 not_detected，不會假造訊號。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("需要 pyyaml：pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS_YML = ROOT / "config" / "providers.yml"
STATE_JSON = ROOT / "state" / "provider_status.json"


def cli_health(detect_command: list[str] | None) -> tuple[str, list[str]]:
    """回傳 (status, evidence)。不讀取任何 secret，只看指令是否存在並可執行。"""
    if not detect_command:
        return "unknown", ["no detect_command configured"]
    binary = detect_command[0]
    if shutil.which(binary) is None:
        return "unknown", [f"binary '{binary}' not found on PATH in this runtime — not installed here, not necessarily auth_missing on the real runtime host"]
    try:
        proc = subprocess.run(
            detect_command, capture_output=True, text=True, timeout=15
        )
        if proc.returncode == 0:
            return "available", [f"`{' '.join(detect_command)}` exit=0"]
        return "unknown", [f"`{' '.join(detect_command)}` exit={proc.returncode}"]
    except Exception as exc:  # noqa: BLE001 — dry-run must never crash the sentinel
        return "unknown", [f"detect_command raised {type(exc).__name__}: {exc}"]


def build_status_row(provider: dict, surface: dict, safe_reserve_ratio: float) -> dict:
    source = surface.get("source", "unknown")
    status_override = surface.get("status_override")

    if status_override == "blocked_by_policy":
        return {
            "provider": provider["provider"],
            "surface": surface["surface"],
            "source": "official_api",
            "confidence": "unknown",
            "window_start": None,
            "window_end": None,
            "reset_timezone": "unknown",
            "limit_unit": "unknown",
            "limit": None,
            "used": None,
            "remaining": None,
            "remaining_ratio": None,
            "last_success": None,
            "status": "blocked_by_policy",
            "evidence": [surface.get("notes", "")],
            "safe_reserve_ratio": safe_reserve_ratio,
        }

    if source == "authenticated_cli_health":
        status, evidence = cli_health(surface.get("detect_command"))
        confidence = "estimated" if status == "available" else "unknown"
        return {
            "provider": provider["provider"],
            "surface": surface["surface"],
            "source": source,
            "confidence": confidence,
            "window_start": None,
            "window_end": None,
            "reset_timezone": "unknown",
            "limit_unit": "unknown",
            "limit": None,
            "used": None,
            "remaining": None,
            "remaining_ratio": None,
            "last_success": None,
            "status": status,
            "evidence": evidence,
            "safe_reserve_ratio": safe_reserve_ratio,
        }

    # manual / unknown / not_applicable
    return {
        "provider": provider["provider"],
        "surface": surface["surface"],
        "source": source,
        "confidence": "unknown" if source != "not_applicable" else "verified",
        "window_start": None,
        "window_end": None,
        "reset_timezone": "unknown",
        "limit_unit": "unknown" if source != "not_applicable" else "not_applicable",
        "limit": None,
        "used": None,
        "remaining": None,
        "remaining_ratio": None,
        "last_success": None,
        "status": "unknown" if source != "not_applicable" else "available",
        "evidence": [surface.get("notes", "")],
        "safe_reserve_ratio": safe_reserve_ratio,
    }


def main() -> None:
    config = yaml.safe_load(PROVIDERS_YML.read_text(encoding="utf-8"))
    safe_reserve_ratio = config.get("safe_reserve_ratio", 0.15)

    rows = []
    for provider in config.get("providers", []):
        for surface in provider.get("surfaces", []):
            rows.append(build_status_row(provider, surface, safe_reserve_ratio))

    output = {
        "generated_by": "quota_sentinel.py dry-run",
        "generated_note": (
            "此輪在 A1 remote 沙盒（非 Mac mini runtime）執行，"
            "CLI health 結果反映沙盒環境，不代表 Mac mini 實際訂閱狀態。"
            "正式訊號需在 Mac mini 上重跑本腳本。"
        ),
        "safe_reserve_ratio": safe_reserve_ratio,
        "providers": rows,
    }

    STATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {STATE_JSON}")
    for row in rows:
        print(f"  {row['provider']:15s} {row['surface']:18s} status={row['status']:16s} confidence={row['confidence']}")


if __name__ == "__main__":
    main()
