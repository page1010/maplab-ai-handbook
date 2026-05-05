import json
import os
import urllib.request
from typing import Any, Dict


class GeminiAdapter:
    def __init__(self, model: str = "gemini-2.5-flash-lite") -> None:
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY", "")

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"ok": False, "error": "missing_GEMINI_API_KEY"}
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            text = (
                payload.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            return _safe_json(text)
        except Exception as exc:
            return {"ok": False, "error": f"gemini_failed: {exc}"}


def _safe_json(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "empty_response"}
    try:
        return json.loads(text)
    except Exception:
        return {"ok": True, "raw_text": text}

