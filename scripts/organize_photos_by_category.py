# organize_photos_by_category.py
# 用途：按 ASSET_LOG category 建 Drive 資料夾結構，複製照片並重命名為 seo_name
# 執行環境：Google Colab（需要 Drive access）
# API：Google Sheets API + Drive API（免費，無 Gemini）
# 規則：只複製，不移動，不刪除原始照片

# ── 安裝 ──────────────────────────────────────────────────────────────────────
# !pip install --quiet google-api-python-client google-auth-httplib2 google-auth-oauthlib

# ── 1. Colab 認證 ─────────────────────────────────────────────────────────────
from google.colab import auth
auth.authenticate_user()

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth import default
import time

creds, _ = default()
sheets = build("sheets", "v4", credentials=creds)
drive  = build("drive",  "v3", credentials=creds)

# ── 2. 設定 ───────────────────────────────────────────────────────────────────
ASSET_LOG_SHEET_ID = "1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI"
ASSET_LOG_TAB      = "ASSET_LOG"          # 讀取的分頁名稱
ROOT_FOLDER_NAME   = "MAPLAB_Assets"      # Drive 根資料夾（若不存在會自動建立）
DRY_RUN            = False                # True = 只列出計畫，不實際複製

# 外燴子資料夾關鍵字對照（按順序比對，第一個命中為準）
CATERING_SUB = [
    ("生日派對", ["生日", "birthday", "生日派對"]),
    ("婚禮",   ["婚禮", "婚", "wedding"]),
    ("企業活動", ["企業", "開幕", "尾牙", "corporate", "年終"]),
]
CATERING_DEFAULT = "其他"

# ── 3. 讀取 ASSET_LOG ─────────────────────────────────────────────────────────
def read_asset_log():
    result = sheets.spreadsheets().values().get(
        spreadsheetId=ASSET_LOG_SHEET_ID,
        range=f"{ASSET_LOG_TAB}!A1:Z",
    ).execute()
    rows = result.get("values", [])
    if not rows:
        raise RuntimeError("ASSET_LOG 是空的，請確認 Sheet ID 和分頁名稱")

    header = [h.strip() for h in rows[0]]
    col = {name: idx for idx, name in enumerate(header)}
    required = {"file_id", "seo_name", "category", "keywords"}
    missing = required - set(col.keys())
    if missing:
        raise RuntimeError(f"ASSET_LOG 缺少欄位：{missing}（現有：{list(col.keys())}）")

    records = []
    for row in rows[1:]:
        def get(name):
            idx = col[name]
            return row[idx].strip() if idx < len(row) else ""

        file_id  = get("file_id")
        seo_name = get("seo_name")
        category = get("category")
        keywords = get("keywords")

        if not file_id or not category:
            continue  # 跳過不完整的列
        records.append({
            "file_id":  file_id,
            "seo_name": seo_name or file_id,
            "category": category,
            "keywords": keywords,
        })
    print(f"✅ 讀取 ASSET_LOG：{len(records)} 筆有效記錄")
    return records

# ── 4. Drive 資料夾工具 ────────────────────────────────────────────────────────
_folder_cache: dict[str, str] = {}  # (parent_id, name) → folder_id

def find_or_create_folder(name: str, parent_id: str) -> str:
    key = f"{parent_id}:{name}"
    if key in _folder_cache:
        return _folder_cache[key]

    q = (
        f"mimeType='application/vnd.google-apps.folder'"
        f" and name='{name}'"
        f" and '{parent_id}' in parents"
        f" and trashed=false"
    )
    resp = drive.files().list(q=q, fields="files(id,name)").execute()
    files = resp.get("files", [])
    if files:
        folder_id = files[0]["id"]
    else:
        if DRY_RUN:
            print(f"  [DRY_RUN] 建資料夾：{name} (parent={parent_id})")
            _folder_cache[key] = f"dry_{name}"
            return _folder_cache[key]
        meta = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = drive.files().create(body=meta, fields="id").execute()
        folder_id = folder["id"]
        print(f"  📁 建立資料夾：{name}")

    _folder_cache[key] = folder_id
    return folder_id

def get_my_drive_root() -> str:
    return "root"

# ── 5. 分類邏輯 ───────────────────────────────────────────────────────────────
def resolve_folder_path(category: str, keywords: str) -> list[str]:
    """回傳資料夾層級列表，例如 ['外燴', '生日派對']"""
    cat = category.strip()
    kw  = keywords.lower()

    if cat == "外燴":
        for sub_name, triggers in CATERING_SUB:
            if any(t in kw for t in triggers):
                return ["外燴", sub_name]
        return ["外燴", CATERING_DEFAULT]

    if cat in ("日常", "旅遊"):
        return [cat]

    return ["其他"]

# ── 6. 複製照片並重命名 ────────────────────────────────────────────────────────
def copy_file(file_id: str, seo_name: str, dest_folder_id: str) -> str | None:
    # 取得原始副檔名
    try:
        meta = drive.files().get(fileId=file_id, fields="name,mimeType").execute()
    except HttpError as e:
        print(f"  ⚠️ 無法取得 {file_id} 的資訊：{e}")
        return None

    orig_name = meta.get("name", "")
    ext = ""
    if "." in orig_name:
        ext = "." + orig_name.rsplit(".", 1)[-1].lower()

    new_name = seo_name if seo_name.endswith(ext) else seo_name + ext

    if DRY_RUN:
        print(f"  [DRY_RUN] 複製 {orig_name} → {new_name}")
        return "dry_copy"

    try:
        copy_meta = {"name": new_name, "parents": [dest_folder_id]}
        result = drive.files().copy(fileId=file_id, body=copy_meta, fields="id").execute()
        return result["id"]
    except HttpError as e:
        print(f"  ⚠️ 複製失敗 {file_id} ({orig_name})：{e}")
        return None

# ── 7. 主流程 ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("organize_photos_by_category.py 啟動")
    print(f"DRY_RUN = {DRY_RUN}")
    print("=" * 60)

    records = read_asset_log()

    # 建立根資料夾
    root_id = find_or_create_folder(ROOT_FOLDER_NAME, get_my_drive_root())
    print(f"📂 根資料夾 {ROOT_FOLDER_NAME}：{root_id}")

    ok, skip, fail = 0, 0, 0

    for i, rec in enumerate(records, 1):
        path = resolve_folder_path(rec["category"], rec["keywords"])

        # 逐層建立 / 取得資料夾
        current_parent = root_id
        for folder_name in path:
            current_parent = find_or_create_folder(folder_name, current_parent)

        # 複製檔案
        new_id = copy_file(rec["file_id"], rec["seo_name"], current_parent)
        if new_id:
            ok += 1
        else:
            fail += 1

        # 每 50 筆顯示進度，避免刷太快
        if i % 50 == 0:
            print(f"  進度：{i}/{len(records)}（✅{ok} ⚠️{fail}）")
            time.sleep(0.5)  # 避免 API rate limit

    print("=" * 60)
    print(f"完成！✅ 成功：{ok}  ⚠️ 失敗：{fail}  跳過：{skip}")
    print(f"根資料夾：https://drive.google.com/drive/folders/{root_id}")
    print("=" * 60)

main()
