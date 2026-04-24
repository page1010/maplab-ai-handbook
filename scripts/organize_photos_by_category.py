"""
整理照片到分類資料夾 — 按 category + keywords + 日期分類
讀取 ASSET_LOG，在 lb99104 Drive 建立 MAPLAB_Assets 結構並複製照片（重命名為 seo_name）。

DRY_RUN=True  → 列出前 20 筆分類結果，不操作 Drive
DRY_RUN=False → 正式用 Drive API files.copy() 複製
"""

import re
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ── 設定 ─────────────────────────────────────────────────────────────
ASSET_LOG_SHEET_ID = "YOUR_ASSET_LOG_SHEET_ID"   # 替換成實際 Spreadsheet ID
ASSET_LOG_SHEET    = "ASSET_LOG"
ROOT_FOLDER_NAME   = "MAPLAB_Assets"
DRY_RUN            = True   # 改 False 才實際操作

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive",
]

# ── 地名清單 ──────────────────────────────────────────────────────────
FOREIGN_PLACES = [
    "日本", "泰國", "韓國", "越南", "澳門", "香港",
    "馬來西亞", "巴黎", "法國", "義大利", "英國", "美國",
    "德國", "西班牙", "新加坡", "印尼", "菲律賓", "印度",
    "土耳其", "希臘", "荷蘭", "瑞士", "奧地利", "捷克",
    "匈牙利", "波蘭", "葡萄牙", "北歐", "冰島", "加拿大",
    "澳洲", "紐西蘭", "埃及", "摩洛哥", "南非", "阿聯酋",
    "杜拜", "峇里島", "沖繩", "北海道", "東京", "大阪",
    "京都", "首爾", "釜山", "曼谷", "清邁",
]
TAIWAN_PLACES = [
    "台北", "台中", "台南", "高雄", "花蓮", "台東",
    "宜蘭", "苗栗", "彰化", "南投", "嘉義", "屏東",
    "澎湖", "金門", "馬祖", "基隆", "新竹", "桃園",
    "新北", "阿里山", "墾丁", "日月潭", "太魯閣",
]


# ── 日期提取 ──────────────────────────────────────────────────────────
def extract_date(original_name: str):
    """
    從檔名提取日期，支援：
      IMG_20221224_xxx  → 2022-12-24
      20221224          → 2022-12-24
      2022-12-24        → 2022-12-24
      2022_12_24        → 2022-12-24
    找不到回傳 (None, None, None)
    """
    patterns = [
        r"20(\d{2})[-_](\d{2})[-_](\d{2})",   # 2022-12-24 / 2022_12_24
        r"20(\d{2})(\d{2})(\d{2})",             # 20221224
    ]
    for pat in patterns:
        m = re.search(pat, original_name)
        if m:
            yy, mm, dd = m.group(1), m.group(2), m.group(3)
            # 簡單驗證
            if 1 <= int(mm) <= 12 and 1 <= int(dd) <= 31:
                return f"20{yy}", mm, dd
    return None, None, None


def date_label(original_name: str, ym_only=False):
    """回傳 YYYY-MM-DD 或 YYYY-MM，找不到就回傳「日期不明」"""
    y, m, d = extract_date(original_name)
    if y is None:
        return "日期不明"
    return f"{y}-{m}" if ym_only else f"{y}-{m}-{d}"


# ── 分類邏輯 ──────────────────────────────────────────────────────────
def classify(row: dict):
    """
    根據 category + keywords 決定目標資料夾路徑（相對於根資料夾）。
    回傳 list[str]，例如 ["外燴", "生日派對", "2022-12-24"]
    """
    category = (row.get("category") or "").strip()
    keywords = (row.get("keywords") or "").strip()
    original = (row.get("original_name") or "").strip()

    kw = keywords  # 方便後面 in 判斷

    if "外燴" in category:
        date_str = date_label(original, ym_only=False)
        if "生日" in kw:
            return ["外燴", "生日派對", date_str]
        if any(w in kw for w in ["婚", "婚禮", "婚宴"]):
            return ["外燴", "婚禮", date_str]
        if any(w in kw for w in ["企業", "開幕", "尾牙", "春酒"]):
            return ["外燴", "企業活動", date_str]
        return ["外燴", "其他", date_str]

    if "旅遊" in category:
        date_ym = date_label(original, ym_only=True)
        for place in FOREIGN_PLACES:
            if place in kw:
                return ["旅遊", "國外", f"{date_ym} {place}"]
        for place in TAIWAN_PLACES:
            if place in kw:
                return ["旅遊", "台灣", f"{date_ym} {place}"]
        if any(w in kw for w in ["海", "玩水", "沙灘", "潮間帶"]):
            return ["旅遊", "海邊玩水", date_ym]
        if "露營" in kw:
            return ["旅遊", "露營", date_ym]
        return ["旅遊", "其他", date_ym]

    if "日常" in category:
        date_ym = date_label(original, ym_only=True)
        return ["日常", date_ym]

    return ["error"]


# ── Drive 輔助 ────────────────────────────────────────────────────────
_folder_cache: dict[str, str] = {}


def get_or_create_folder(service, name: str, parent_id: str) -> str:
    cache_key = f"{parent_id}/{name}"
    if cache_key in _folder_cache:
        return _folder_cache[cache_key]

    query = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        f" and '{parent_id}' in parents and trashed=false"
    )
    resp = service.files().list(q=query, fields="files(id)").execute()
    files = resp.get("files", [])
    if files:
        fid = files[0]["id"]
    else:
        meta = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        fid = service.files().create(body=meta, fields="id").execute()["id"]

    _folder_cache[cache_key] = fid
    return fid


def ensure_folder_path(service, root_id: str, path_parts: list[str]) -> str:
    current = root_id
    for part in path_parts:
        current = get_or_create_folder(service, part, current)
    return current


def copy_file(service, file_id: str, dest_folder_id: str, new_name: str) -> str:
    body = {"name": new_name, "parents": [dest_folder_id]}
    result = service.files().copy(fileId=file_id, body=body, fields="id").execute()
    return result["id"]


# ── 主流程 ────────────────────────────────────────────────────────────
def main():
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES
    )
    sheets_svc = build("sheets", "v4", credentials=creds)
    drive_svc  = build("drive",  "v3", credentials=creds)

    # 1. 讀 ASSET_LOG
    result = (
        sheets_svc.spreadsheets()
        .values()
        .get(spreadsheetId=ASSET_LOG_SHEET_ID, range=f"{ASSET_LOG_SHEET}!A1:Z")
        .execute()
    )
    rows = result.get("values", [])
    if not rows:
        print("ASSET_LOG 是空的，結束。")
        return

    headers = [h.strip() for h in rows[0]]
    records = [dict(zip(headers, r)) for r in rows[1:]]
    print(f"共讀到 {len(records)} 筆")

    # 2. DRY_RUN：印前 20 筆分類結果
    if DRY_RUN:
        print("\n[DRY_RUN] 前 20 筆分類預覽：")
        print(f"{'original_name':<30} {'seo_name':<40} {'目標路徑'}")
        print("-" * 100)
        for rec in records[:20]:
            path = classify(rec)
            seo  = rec.get("seo_name", "(無 seo_name)")
            orig = rec.get("original_name", "")
            print(f"{orig:<30} {seo:<40} {'/'.join(path)}")
        print("\nDRY_RUN 完成。設 DRY_RUN=False 後重執行才實際複製。")
        return

    # 3. 正式模式
    # 在 lb99104 Drive 建根資料夾
    root_id = get_or_create_folder(drive_svc, ROOT_FOLDER_NAME, "root")
    print(f"根資料夾 {ROOT_FOLDER_NAME} id={root_id}")

    ok, fail = 0, 0
    for i, rec in enumerate(records):
        file_id  = rec.get("file_id", "").strip()
        seo_name = rec.get("seo_name", "").strip()
        orig     = rec.get("original_name", "").strip()

        if not file_id or not seo_name:
            print(f"[SKIP] 第 {i+2} 行缺 file_id 或 seo_name，跳過")
            continue

        path_parts = classify(rec)
        try:
            dest_folder = ensure_folder_path(drive_svc, root_id, path_parts)
            copy_file(drive_svc, file_id, dest_folder, seo_name)
            ok += 1
        except Exception as e:
            print(f"[FAIL] {orig} → {'/'.join(path_parts)}: {e}")
            fail += 1

        if (i + 1) % 100 == 0:
            print(f"進度：{i+1}/{len(records)}（成功 {ok} / 失敗 {fail}）")

    print(f"\n完成！成功 {ok}，失敗 {fail}，共 {len(records)} 筆")


if __name__ == "__main__":
    main()
