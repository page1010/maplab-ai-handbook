#!/usr/bin/env python3
"""
MAPLAB DASHBOARD 自動更新腳本
用途：讀 CURRENT_STATUS.md + git log，用 Sheets API 更新 DASHBOARD 分頁

使用方式：
  python3 scripts/update-dashboard.py

排程（crontab）：
  */30 * * * * cd /Users/pagemacmini/maplab-ai-handbook && python3 scripts/update-dashboard.py >> /tmp/maplab-dashboard.log 2>&1

需求：
  pip install google-auth google-auth-httplib2 requests
"""

import json
import subprocess
import warnings
from datetime import datetime
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

warnings.filterwarnings("ignore")

# ── 設定 ──────────────────────────────────────────────────────────────────────
TOKEN_PATH = Path.home() / ".claude/mcp-keys/google-token.json"
SHEET_ID = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
REPO_ROOT = Path(__file__).parent.parent
STATUS_FILE = REPO_ROOT / "CURRENT_STATUS.md"

# ── Token 工具 ────────────────────────────────────────────────────────────────

def get_token() -> str:
    with open(TOKEN_PATH) as f:
        t = json.load(f)
    creds = Credentials(
        token=t.get("token"),
        refresh_token=t.get("refresh_token"),
        token_uri=t.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=t.get("client_id"),
        client_secret=t.get("client_secret"),
        scopes=t.get("scopes"),
    )
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        t["token"] = creds.token
        with open(TOKEN_PATH, "w") as f:
            json.dump(t, f)
    return creds.token


# ── Git log ───────────────────────────────────────────────────────────────────

def get_recent_commits(n: int = 10) -> list[dict]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "log", f"-{n}", "--pretty=format:%h|%s|%ad", "--date=short"],
        capture_output=True, text=True
    )
    commits = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({"sha": parts[0], "message": parts[1], "date": parts[2]})
    return commits


# ── CURRENT_STATUS.md 解析 ────────────────────────────────────────────────────

def parse_tasks(status_path: Path) -> list[dict]:
    """從 CURRENT_STATUS.md 解析 ## 當前進行中任務 表格"""
    tasks = []
    in_table = False
    for line in status_path.read_text().splitlines():
        if "## 當前進行中任務" in line:
            in_table = True
            continue
        if in_table:
            if line.startswith("##"):
                break  # 下一個 section
            if line.startswith("| T-") or line.startswith("| t-"):
                cols = [c.strip() for c in line.split("|")]
                # cols[0]=空, 1=TaskID, 2=任務, 3=負責, 4=狀態, 5=Task Card
                if len(cols) >= 5:
                    tasks.append({
                        "id": cols[1],
                        "name": cols[2],
                        "agent": cols[3],
                        "status": cols[4],
                        "card": cols[5] if len(cols) > 5 else "",
                    })
    return tasks


# ── Sheets 寫入 ───────────────────────────────────────────────────────────────

def batch_update(token: str, data: list[dict]) -> None:
    """data = [{"range": "DASHBOARD!A1", "values": [[v1, v2, ...]]}]"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values:batchUpdate"
    body = {"valueInputOption": "RAW", "data": data}
    r = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=body)
    r.raise_for_status()
    resp = r.json()
    print(f"  ✅ 更新 {resp.get('totalUpdatedCells', 0)} 個儲存格")


def update_dashboard_header(token: str, now: str) -> None:
    batch_update(token, [
        {"range": "DASHBOARD!B2", "values": [[now]]},
    ])


def update_task_board_section(token: str, tasks: list[dict]) -> None:
    """覆寫 DASHBOARD Task Board 區塊（Row 4 開始的任務列）"""
    if not tasks:
        return
    # 找出 DASHBOARD 中任務列開始的位置（Row 5 = index 4，Row 4 是標題）
    rows = []
    for task in tasks:
        rows.append([
            task["id"],
            task["name"],
            task["agent"],
            task["status"],
            datetime.now().strftime("%Y-%m-%d"),
            "",
            task["card"],
        ])
    data = [{"range": f"DASHBOARD!A5:G{4 + len(rows)}", "values": rows}]
    batch_update(token, data)


def update_commit_section(token: str, commits: list[dict]) -> None:
    """覆寫 DASHBOARD Commit 區塊（Row 22 開始）"""
    rows = [[c["sha"], c["message"], c["date"]] for c in commits]
    data = [{"range": f"DASHBOARD!A22:C{21 + len(rows)}", "values": rows}]
    batch_update(token, data)


# ── 主程式 ────────────────────────────────────────────────────────────────────

def main() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] MAPLAB Dashboard 更新開始")

    token = get_token()

    # 1. 更新時間
    print("  → 更新時間戳記…")
    update_dashboard_header(token, now)

    # 2. 任務表
    print("  → 讀取 CURRENT_STATUS.md 任務…")
    tasks = parse_tasks(STATUS_FILE)
    print(f"     找到 {len(tasks)} 筆任務")
    if tasks:
        update_task_board_section(token, tasks)

    # 3. 最新 Commit
    print("  → 讀取 git log…")
    commits = get_recent_commits(10)
    update_commit_section(token, commits)

    print(f"[{now}] ✅ Dashboard 更新完成")


if __name__ == "__main__":
    main()
