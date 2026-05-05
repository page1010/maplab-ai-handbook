import json
import os
import subprocess
from typing import Any, Dict, Optional


class OllamaAdapter:
    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:latest")

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        cmd = ["ollama", "run", self.model, prompt]
        try:
            out = subprocess.check_output(cmd, text=True, timeout=90)
            return _safe_json(out)
        except Exception as exc:
            return {"ok": False, "error": f"ollama_failed: {exc}"}


def _safe_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        return {"ok": False, "error": "empty_response"}
    try:
        return json.loads(text)
    except Exception:
        return {"ok": True, "raw_text": text}
