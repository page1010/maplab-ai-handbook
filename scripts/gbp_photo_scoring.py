#!/usr/bin/env python3
"""GBP photo scoring: local Ollama vision scan over 2026maplab外燴紀錄 subfolders.

Usage: bot/venv/bin/python3 scripts/gbp_photo_scoring.py
Output: state/gbp_photo_scoring_report.json + state/gbp_photo_scoring_report.md
"""
import base64
import io
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

BASE = Path(
    "/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com"
    "/我的雲端硬碟/2026maplab外燴紀錄"
)
TARGET_FOLDERS = [
    "0702中興工程",
    "20260627東門教會證婚",
    "0621歡樂時光-性別派對",
    "20260621說事實木地板開幕",
    "20260614富信飯店-社工公會會議",
    "20260613遊艇氣泡水",
]
IMG_EXTS = {".jpg", ".jpeg", ".heic", ".png"}
MODEL = "gemma4:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"
STATE_DIR = Path(__file__).resolve().parent.parent / "state"
SAMPLE_CAP_PER_FOLDER = 100

PROMPT = """你是MAPLAB Kitchen的照片分類助手。請分析這張照片並回傳JSON格式：
{"評分":"高|中|低","標籤":["3-5個中文關鍵詞"],
 "說明":"適用性描述30字內","類型":"english-lowercase-hyphenated"}
評分規則：擺盤精緻=高；普通=中；模糊雜亂或有清楚正臉入鏡=低
類型格式：{評分}-{subject}-{detail}，subject從 food/plating/venue/group/other 選一個，例：high-plating-dessert-buffet
僅回傳JSON，不要其他文字。"""

SCORE_MAP = {"高": 3, "中": 2, "低": 1}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def get_drive_id(path: Path) -> str:
    try:
        out = subprocess.run(
            ["xattr", "-p", "com.google.drivefs.item-id", str(path)],
            capture_output=True, text=True, timeout=5,
        )
        fid = out.stdout.strip()
        return fid if fid else ""
    except Exception:
        return ""


def drive_link(path: Path) -> str:
    fid = get_drive_id(path)
    return f"https://drive.google.com/file/d/{fid}/view" if fid else f"(no drive id: {path.name})"


def load_thumbnail_b64(path: Path) -> str:
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((768, 768))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def _call_ollama_once(img_b64: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "images": [img_b64],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 400},
    }
    req = urllib.request.Request(
        OLLAMA_URL, json.dumps(payload).encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())["response"]


def score_with_ollama(img_b64: str, retries: int = 6) -> dict:
    """llama-server 在連續多模態呼叫後會偶發性退化成空輸出（done_reason=length 但 response=''），
    與 prompt 內容/圖片內容無關（同一組合重測會從成功變失敗）。用 ollama stop 重啟模型 process 後重試可恢復。"""
    last_err = None
    for attempt in range(retries):
        try:
            out = _call_ollama_once(img_b64)
            m = re.search(r"\{.*\}", out, re.S)
            if m:
                return json.loads(m.group(0))
            last_err = f"no JSON in output (empty/degenerate response, len={len(out)})"
        except Exception as e:
            last_err = str(e)
        log(f"  retry {attempt + 1}/{retries} after: {last_err} — restarting model")
        subprocess.run(["ollama", "stop", MODEL], capture_output=True, timeout=30)
        time.sleep(6)
    raise ValueError(f"failed after {retries} retries: {last_err}")


def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    folder_summary = {}

    for folder_name in TARGET_FOLDERS:
        folder_path = BASE / folder_name
        if not folder_path.exists():
            log(f"MISSING folder: {folder_name}")
            folder_summary[folder_name] = {"status": "folder_not_found", "count": 0}
            continue
        images = sorted(
            f for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in IMG_EXTS
        )
        if not images:
            log(f"EMPTY folder (0 photos): {folder_name}")
            folder_summary[folder_name] = {"status": "empty", "count": 0}
            continue
        if len(images) > SAMPLE_CAP_PER_FOLDER:
            step = len(images) / SAMPLE_CAP_PER_FOLDER
            images = [images[int(i * step)] for i in range(SAMPLE_CAP_PER_FOLDER)]
            log(f"{folder_name}: sampled {len(images)} of larger set")

        log(f"{folder_name}: scoring {len(images)} photos")
        folder_summary[folder_name] = {"status": "scored", "count": len(images)}
        for img_path in images:
            try:
                b64 = load_thumbnail_b64(img_path)
                parsed = score_with_ollama(b64)
                label = parsed.get("評分", "")
                subject_type = str(parsed.get("類型", "")).split("-")[1] if "-" in str(parsed.get("類型", "")) else ""
                results.append({
                    "folder": folder_name,
                    "filename": img_path.name,
                    "path": str(img_path),
                    "drive_link": drive_link(img_path),
                    "score_label": label,
                    "score": SCORE_MAP.get(label, 0),
                    "tags": parsed.get("標籤"),
                    "subject_type": subject_type,
                    "reason": parsed.get("說明"),
                    "seo_type": parsed.get("類型"),
                })
                log(f"  {img_path.name}: {label} / {subject_type}")
            except Exception as e:
                log(f"FAIL {img_path.name}: {e}")
                results.append({
                    "folder": folder_name,
                    "filename": img_path.name,
                    "path": str(img_path),
                    "drive_link": drive_link(img_path),
                    "score": None,
                    "error": str(e),
                })

    (STATE_DIR / "gbp_photo_scoring_report.json").write_text(
        json.dumps({"folder_summary": folder_summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log(f"done: {len(results)} photos scored, report written")


if __name__ == "__main__":
    main()
