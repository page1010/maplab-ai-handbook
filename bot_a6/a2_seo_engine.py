from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

try:
    from ai_workbook.openclaw_adapter import OpenClawAdapter
except Exception:
    OpenClawAdapter = None  # type: ignore[assignment]

DEFAULT_LOCAL_MODEL = os.getenv("A2_LOCAL_MODEL", os.getenv("OPENCLAW_MODEL", "qwen2.5:14b"))
DEFAULT_LOCAL_ENGINE = os.getenv("A2_LOCAL_ENGINE", "auto")
DEFAULT_THINKING = os.getenv("A2_LOCAL_THINKING", "off")

def run_a2_seo_task(
    user_message: str,
    user_name: str = "",
    job_id: Optional[str] = None,
    engine: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    透過 OpenClawAdapter 呼叫地端模型，並將 prompt 設定為 A2 角色。
    若無 OpenClawAdapter，將回傳錯誤訊息。
    """
    if OpenClawAdapter is None:
        return "⚠️ OpenClawAdapter 尚未準備好，無法喚醒地端 A2。"

    job = job_id or f"A2-SEO-{os.urandom(4).hex()}"
    requested_engine = engine or DEFAULT_LOCAL_ENGINE
    requested_model = model or DEFAULT_LOCAL_MODEL

    # Prompt based on A2 constraints
    prompt = (
        "你是 A2 Ads SEO WordPress Patrol (SEO 編輯與巡邏員)。\n"
        "請根據使用者的需求撰寫、優化或回答與 SEO、WordPress 或廣告相關的問題。\n"
        "你的回覆必須是一篇準備好可以發布或直接使用的 Markdown 文本，"
        "不要帶有過多的 AI 寒暄用語。\n\n"
        f"使用者（{user_name or '業務'}）的需求：\n"
        f"{user_message.strip()}\n"
    )

    try:
        adapter = OpenClawAdapter(default_model=requested_model)
        result = adapter.run_local_task(
            job_id=job,
            prompt=prompt,
            model=requested_model,
            engine=requested_engine,
            thinking=DEFAULT_THINKING,
        )
        
        draft_path = Path(str(result["draft_md"]))
        answer = draft_path.read_text(encoding="utf-8").strip()
        
        # Append runtime metadata
        footer = (
            f"\n\n---\n"
            f"📍 本地 A2 引擎: engine={result.get('engine_used')} model={result.get('model_used')} fallback={result.get('fallback_used')}\n"
            f"review bundle: `{result.get('bundle_dir')}`"
        )
        return answer + footer
    except Exception as exc:
        return f"⚠️ A2 地端引擎發生錯誤: {exc}"
