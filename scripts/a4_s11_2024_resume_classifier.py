#!/usr/bin/env python3
"""A4 S11(2024) 補跑 — 地端 Ollama vision 分類，取代 Colab + Gemini API（T-A4-001）。

背景（2026-07-06 Owner 授權修好重啟）：
  S11(2024) 原本靠 Colab + Gemini 2.5 Flash API 跑，Colab 免費層 session 逾時
  兩次斷線後 ~80 天無人接手；同一組 GCP project 的 Gemini API 又是 04-18
  $3,000+/月帳單事件的根因，Owner 稱已關額度。因此本次補跑改用本機 Ollama
  vision（比照 T-A4-004 `a4_photo_classifier.py` 已驗證的做法），完全不碰
  GCP/Gemini，零成本、可斷點續跑。

範圍：
  只處理 MAPLAB_ASSET_LOG 尚未涵蓋的 2024 Drive 資料夾（folder id
  1jiuc_WuHObiWUGvDTH1Hafe_jcexusNy）圖片檔（排除影片）。

  2026-07-06 完整核對（比原本任務卡記錄的更複雜，記錄在這裡避免下次又搞混）：
  - Drive 2024 資料夾目前圖片 13,980 張（比 04 月估計的 12,213 多，
    這幾個月資料夾又進了新照片）。
  - ASSET_LOG 主區塊（rows 17066-27116）已有 10,051 筆 2024 有效分類。
  - ASSET_LOG 尾端還藏了一段 2,163 列的「補跑殘留」（約 row 34761-36923，
    2025 資料之後、本次新資料之前）——這應該是先前某次 Colab/Gemini
    重啟嘗試的結果，從未同步回任務卡，其中只有 541 筆是有效分類
    （外燴/日常/旅遊），其餘 1,622 筆是 category="error" 的失敗佔位列。
  - 真正還沒有效分類過的張數 = 13,980 − 10,051 − 541 = 3,388，
    其中 ~1,622 張是重新分類舊 error、~1,766 張是資料夾裡從未出現過的新照片
    （`sheet_processed_names()` 每次執行都會重新掃描全表算出精確數字，
    不要沿用這裡寫死的數字）。
  - 舊的 1,622 筆 error 列不會被刪除，只是不會再被當「已完成」；
    本次補跑完成後 Sheet 會同時存在舊 error 列與新的正確分類列，
    是已知的歷史髒資料，建議另開一次性清理任務刪掉 error 列。

分類 prompt 沿用 projects/maplab-pipeline.md「Gemini Prompt（定版 S3）」，
只是把執行模型從 Gemini 2.5 Flash 換成本機 gemma4:latest vision。

安全設計：
  - 只下載到暫存檔，分類完即刪，不落地大量原始照片到本機硬碟。
  - 每張處理完就寫 SQLite checkpoint（data/s11_2024_resume.db），
    斷線/中斷重跑會自動跳過已完成的 file_id，不重複分類。
  - 每 20 張 batch append 一次到 MAPLAB_ASSET_LOG（Sheets API v4
    values:append），避免每張都打一次 Sheets API。
  - Google OAuth token 用完自動用 refresh_token 換新，不需要人在場。

用法（需用 bot/venv 的 python，系統 python3 的 Pillow/pyexpat 環境壞掉）：
  bot/venv/bin/python3 scripts/a4_s11_2024_resume_classifier.py --status
  bot/venv/bin/python3 scripts/a4_s11_2024_resume_classifier.py --all
  bot/venv/bin/python3 scripts/a4_s11_2024_resume_classifier.py --limit 20   # 小批試跑

依賴：bot/venv 已裝 pillow + pillow-heif（2026-07-06 補裝，讀 HEIC 用）。
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import re
import sqlite3
import time
import urllib.error
import urllib.parse

import pillow_heif

pillow_heif.register_heif_opener()
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOKEN_PATH = Path.home() / ".claude/mcp-keys/google-token.json"
FOLDER_2024 = "1jiuc_WuHObiWUGvDTH1Hafe_jcexusNy"
SHEET_ID = "1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI"
SHEET_TAB = "工作表1"
DB_PATH = REPO_ROOT / "data" / "s11_2024_resume.db"
LOG_PATH = REPO_ROOT / "state" / "a4_s11_resume.log"
MISSING_CACHE = REPO_ROOT / "state" / "s11_2024_missing_cache.json"

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "gemma4:latest"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif"}
BATCH_APPEND_SIZE = 20

PROMPT = """你是MAPLAB Kitchen的照片分類助手。請分析這張照片並回傳JSON格式：
{"category":"外燴|旅遊|日常","keywords":["3-5個中文關鍵詞"],
 "alt_text":"SEO中文描述30字內","seo_name":"english-lowercase-hyphenated"}
分類規則：外燴=餐點/擺盤/食材/外燴現場/廚房/單據；旅遊=風景/觀光/家庭出遊；日常=家庭/自拍/寵物/小孩/其他
seo_name格式：{category}-{description}-{detail}，例：catering-birthday-buffet-setup
僅回傳JSON，不要其他文字。"""

CATEGORY_MAP = {"外燴": "外燴", "旅遊": "旅遊", "日常": "日常"}


def log(msg: str) -> None:
    line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def db_init() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS classified (
            file_id TEXT PRIMARY KEY, name TEXT, category TEXT,
            keywords TEXT, alt_text TEXT, seo_name TEXT,
            appended INTEGER DEFAULT 0, error TEXT, ts TEXT)"""
    )
    conn.commit()
    return conn


def load_token() -> dict:
    return json.load(open(TOKEN_PATH, encoding="utf-8"))


def get_access_token() -> str:
    tok = load_token()
    expiry = tok.get("expiry")
    if expiry:
        exp_dt = dt.datetime.fromisoformat(expiry.replace("Z", "+00:00"))
        now = dt.datetime.now(dt.timezone.utc)
        if now < exp_dt - dt.timedelta(minutes=2):
            return tok["token"]
    data = urllib.parse.urlencode(
        {
            "client_id": tok["client_id"],
            "client_secret": tok["client_secret"],
            "refresh_token": tok["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode()
    req = urllib.request.Request(tok["token_uri"], data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        new_tok = json.loads(resp.read())
    tok["token"] = new_tok["access_token"]
    tok["expiry"] = (
        dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=new_tok.get("expires_in", 3600))
    ).isoformat().replace("+00:00", "Z")
    json.dump(tok, open(TOKEN_PATH, "w", encoding="utf-8"))
    log("Google OAuth token refreshed")
    return tok["token"]


def drive_list_all_files(folder_id: str, access_token: str) -> list[dict]:
    files: list[dict] = []
    page_token = None
    while True:
        params = {
            "q": f'"{folder_id}" in parents and trashed=false',
            "fields": "files(id,name),nextPageToken",
            "pageSize": "1000",
        }
        if page_token:
            params["pageToken"] = page_token
        req = urllib.request.Request(
            f"https://www.googleapis.com/drive/v3/files?{urllib.parse.urlencode(params)}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        files.extend(data.get("files", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return files


def sheet_processed_names() -> set[str]:
    """已驗證分類過的 2024 檔名（跨整張 Sheet 掃描，用 A欄=='2024' + D欄
    有效分類值配對，不能只看檔名 —— 不同年份的照片檔名會撞號，例如手機
    IMG_XXXX 序號每年會重來）。

    2026-07-06 發現：2024 資料不是只有 rows 17066-27116 這個主區塊，
    2025 區塊之後（約 row 34761-36923）還有一段 2,163 列的「尾端補跑」
    紀錄 —— 應該是先前某次 Colab/Gemini 重啟嘗試的殘留，從未同步回
    task card，其中 541 筆有效分類、1,622 筆是 category=="error" 的
    失敗佔位列。只有前者算「已處理」，後者要重新分類。"""
    access_token = get_access_token()
    rng = urllib.parse.quote(f"{SHEET_TAB}!A2:D")
    req = urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{rng}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    processed = set()
    for row in data.get("values", []):
        if len(row) < 4:
            continue
        year, name, _file_id, category = row[0], row[1], row[2], row[3]
        if year == "2024" and category and category != "error":
            processed.add(name)
    return processed


def compute_missing(force_refresh: bool = False) -> list[dict]:
    if MISSING_CACHE.exists() and not force_refresh:
        return json.loads(MISSING_CACHE.read_text(encoding="utf-8"))
    access_token = get_access_token()
    files = drive_list_all_files(FOLDER_2024, access_token)
    images = [f for f in files if Path(f["name"]).suffix.lower() in IMG_EXTS]
    processed = sheet_processed_names()
    missing = [f for f in images if f["name"] not in processed]
    MISSING_CACHE.parent.mkdir(parents=True, exist_ok=True)
    MISSING_CACHE.write_text(json.dumps(missing, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"drive folder images={len(images)} already_valid_in_sheet={len(processed)} missing={len(missing)}")
    return missing


def drive_download_bytes(file_id: str, access_token: str) -> bytes:
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def classify_with_ollama(image_bytes: bytes) -> dict:
    from PIL import Image
    import io

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((768, 768))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "images": [base64.b64encode(buf.getvalue()).decode()],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 800},
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        json.dumps(payload).encode(),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        out = json.loads(resp.read())["response"]
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        raise ValueError(f"no JSON in model output: {out[:200]}")
    parsed = json.loads(m.group(0))
    category = parsed.get("category", "").strip()
    if category not in CATEGORY_MAP:
        category = "日常"  # 模糊時保守分類，同 T-A4-004 邏輯
    keywords = parsed.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in re.split(r"[,|、]", keywords) if k.strip()]
    return {
        "category": category,
        "keywords": "|".join(keywords[:5]),
        "alt_text": str(parsed.get("alt_text", ""))[:120],
        "seo_name": str(parsed.get("seo_name", ""))[:100],
    }


def sheet_append_rows(rows: list[list[str]]) -> None:
    if not rows:
        return
    access_token = get_access_token()
    rng = urllib.parse.quote(f"{SHEET_TAB}!A:G")
    body = json.dumps({"values": rows}).encode()
    req = urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{rng}:append"
        f"?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS",
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()


def run(limit: int) -> None:
    conn = db_init()
    missing = compute_missing()
    done_ids = {r[0] for r in conn.execute("SELECT file_id FROM classified WHERE error IS NULL")}
    todo = [f for f in missing if f["id"] not in done_ids]
    log(f"resume run start: missing_total={len(missing)} already_done_this_run={len(done_ids)} todo={len(todo)} limit={limit}")

    pending_rows: list[list[str]] = []
    processed_count = 0
    for f in todo[:limit]:
        file_id, name = f["id"], f["name"]
        try:
            access_token = get_access_token()
            img_bytes = drive_download_bytes(file_id, access_token)
            result = classify_with_ollama(img_bytes)
            conn.execute(
                "INSERT OR REPLACE INTO classified VALUES (?,?,?,?,?,?,0,NULL,datetime('now'))",
                (file_id, name, result["category"], result["keywords"], result["alt_text"], result["seo_name"]),
            )
            conn.commit()
            pending_rows.append(
                ["2024", name, file_id, result["category"], result["keywords"], result["alt_text"], result["seo_name"]]
            )
        except Exception as e:  # noqa: BLE001 - log and keep going, don't kill the whole batch
            conn.execute(
                "INSERT OR REPLACE INTO classified VALUES (?,?,NULL,NULL,NULL,NULL,0,?,datetime('now'))",
                (file_id, name, str(e)[:300]),
            )
            conn.commit()
            log(f"FAIL {name} ({file_id}): {e}")

        processed_count += 1
        if len(pending_rows) >= BATCH_APPEND_SIZE:
            sheet_append_rows(pending_rows)
            ids = [r[2] for r in pending_rows]
            conn.execute(
                f"UPDATE classified SET appended=1 WHERE file_id IN ({','.join('?' * len(ids))})",
                ids,
            )
            conn.commit()
            log(f"appended batch of {len(pending_rows)} rows to Sheet")
            pending_rows = []

        if processed_count % 100 == 0:
            log(f"progress: {processed_count}/{min(limit, len(todo))}")

    if pending_rows:
        sheet_append_rows(pending_rows)
        ids = [r[2] for r in pending_rows]
        conn.execute(
            f"UPDATE classified SET appended=1 WHERE file_id IN ({','.join('?' * len(ids))})",
            ids,
        )
        conn.commit()
        log(f"appended final batch of {len(pending_rows)} rows to Sheet")

    log(f"run done: processed {processed_count} this invocation")


def status() -> None:
    conn = db_init()
    total_missing = len(compute_missing())
    ok = conn.execute("SELECT COUNT(*) FROM classified WHERE error IS NULL").fetchone()[0]
    appended = conn.execute("SELECT COUNT(*) FROM classified WHERE appended=1").fetchone()[0]
    errs = conn.execute("SELECT COUNT(*) FROM classified WHERE error IS NOT NULL").fetchone()[0]
    print(f"目標補跑張數（2026-07-06 實測缺口）: {total_missing}")
    print(f"已分類（含待 append）: {ok}")
    print(f"已寫回 Sheet: {appended}")
    print(f"失敗: {errs}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--refresh-missing", action="store_true", help="強制重新枚舉 Drive + Sheet 算缺口")
    args = ap.parse_args()

    if args.status:
        status()
        return
    if args.refresh_missing:
        compute_missing(force_refresh=True)
        return

    limit = 10**9 if args.all else args.limit
    run(limit)


if __name__ == "__main__":
    main()
