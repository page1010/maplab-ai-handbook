#!/usr/bin/env python3
"""
整理_品項圖片_pipeline.py
下載所有品項圖片（Slides googleusercontent + WordPress avif/webp）
轉成 jpg，上傳到 Drive 品項照片資料夾，更新 Items K 欄。

常數：
  Slide ID:           16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo
  Sheet ID:           1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
  Items_Photos 資料夾: 1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT
  Token:              ~/.claude/mcp-keys/google-token.json

用途：一次工整理所有品項圖片 → 確保每筆品項都有穩定的 Drive jpg URL
"""

import io
import json
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ── 套件 ──────────────────────────────────────────────────
try:
    import requests
    from PIL import Image
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
except ImportError as e:
    print(f"❌ 缺少套件：{e}")
    print("執行：python3 -m pip install Pillow google-auth google-auth-oauthlib google-api-python-client requests --user")
    sys.exit(1)

# ── 常數 ──────────────────────────────────────────────────
SLIDE_ID        = "16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo"
SHEET_ID        = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
ITEMS_TAB       = "Items"
ITEMS_PHOTOS_ID = "1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT"   # Drive 品項照片資料夾
TOKEN_PATH      = Path.home() / ".claude/mcp-keys/google-token.json"
JPG_QUALITY     = 90
DOWNLOAD_TIMEOUT = 30


# ════════════════════════════════════════════════════════════
# 1. OAuth 認證
# ════════════════════════════════════════════════════════════
def get_credentials():
    with open(TOKEN_PATH) as f:
        td = json.load(f)

    creds = Credentials(
        token=td.get("token"),
        refresh_token=td.get("refresh_token"),
        token_uri=td.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=td.get("client_id"),
        client_secret=td.get("client_secret"),
        scopes=td.get("scopes"),
    )
    if creds.expired and creds.refresh_token:
        print("  Token 過期，正在刷新...")
        creds.refresh(Request())
        td["token"] = creds.token
        with open(TOKEN_PATH, "w") as f:
            json.dump(td, f, indent=2)
        print("  Token 已刷新。")
    return creds


# ════════════════════════════════════════════════════════════
# 2. 讀取 Items 工作表
# ════════════════════════════════════════════════════════════
def read_items(sheets_svc):
    """回傳 list of dict，含 row_index(1-based), item_id, standard_name, image_url"""
    result = sheets_svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{ITEMS_TAB}!A1:L300",
    ).execute()
    rows = result.get("values", [])
    if not rows:
        return []
    headers = rows[0]

    # 找欄位 index
    h = [x.lower().strip() for x in headers]
    idx_id   = h.index("item_id")      if "item_id"      in h else 0
    idx_name = h.index("standard_name") if "standard_name" in h else 2
    idx_k    = 10  # K 欄 = index 10（image_url）

    items = []
    for row_i, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        item_id = row[idx_id].strip()  if len(row) > idx_id   else ""
        name    = row[idx_name].strip() if len(row) > idx_name else ""
        url     = row[idx_k].strip()    if len(row) > idx_k    else ""
        if not item_id and not name:
            continue
        items.append({
            "row": row_i,
            "item_id": item_id,
            "name": name,
            "old_url": url,
        })
    return items


# ════════════════════════════════════════════════════════════
# 3. 從 Slides 抽取「品名 → contentUrl」映射（給空白 K 欄用）
# ════════════════════════════════════════════════════════════
def extract_slide_name_url_map(slides_svc):
    """遍歷 Slide，回傳 {中文品名: contentUrl}"""
    preso = slides_svc.presentations().get(
        presentationId=SLIDE_ID,
        fields="slides(objectId,pageElements(shape,image))",
    ).execute()

    name_url = {}
    for slide_idx, slide in enumerate(preso.get("slides", []), start=1):
        images, texts = [], []
        for elem in slide.get("pageElements", []):
            img = elem.get("image")
            if img:
                src = img.get("sourceUrl") or img.get("contentUrl")
                if src:
                    images.append(src)
            shape = elem.get("shape", {})
            for te in shape.get("text", {}).get("textElements", []):
                run = te.get("textRun")
                if run:
                    t = run.get("content", "").strip()
                    if t:
                        texts.append(t)

        if not images:
            continue

        # 過濾：只保留中文品名
        skip_headers = {"Menu Showcase", "MENU", "PORTFOLIO", "WHAT WE DO",
                        "ABOUT US", "WHY CHOOSE US", "OUR PARTNERS",
                        "Selected Works", "Our Services", "Our Advantages",
                        "Trusted By"}
        zh_names = []
        for t in texts:
            if t in skip_headers:
                continue
            if t.startswith("[") and t.endswith("]"):
                continue
            if any("\u4e00" <= c <= "\u9fff" for c in t):
                zh_names.append(t)

        pairs = min(len(images), len(zh_names))
        for i in range(pairs):
            name_url[zh_names[i]] = images[i]

    print(f"  Slides 品名→URL 映射：{len(name_url)} 筆")
    return name_url


def slide_match(item_name, name_url_map, min_len=3):
    """LCS 模糊比對，回傳 (url, matched_key) 或 None"""
    best_url, best_key, best_score = None, None, 0
    for key, url in name_url_map.items():
        if item_name in key or key in item_name:
            score = len(min(item_name, key, key=len)) + 100
        else:
            # LCS
            m, n = len(item_name), len(key)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            lcs = 0
            for ii in range(1, m + 1):
                for jj in range(1, n + 1):
                    if item_name[ii-1] == key[jj-1]:
                        dp[ii][jj] = dp[ii-1][jj-1] + 1
                        lcs = max(lcs, dp[ii][jj])
            score = lcs if lcs >= min_len else 0

        if score > best_score:
            best_url, best_key, best_score = url, key, score

    if best_score > 0:
        return best_url, best_key
    return None


# ════════════════════════════════════════════════════════════
# 4. 下載圖片 → bytes
# ════════════════════════════════════════════════════════════
def download_image(url, bearer_token=None):
    """下載圖片，回傳 bytes 或 None"""
    headers = {}
    if bearer_token and "googleusercontent" in url:
        headers["Authorization"] = f"Bearer {bearer_token}"

    try:
        resp = requests.get(url, headers=headers, timeout=DOWNLOAD_TIMEOUT)
        if resp.status_code == 200:
            return resp.content
        else:
            print(f"    ⚠️  HTTP {resp.status_code}: {url[:80]}")
            return None
    except Exception as e:
        print(f"    ❌ 下載失敗：{e} | {url[:80]}")
        return None


# ════════════════════════════════════════════════════════════
# 5. 轉成 JPG bytes
# ════════════════════════════════════════════════════════════
def to_jpg_bytes(img_bytes, item_id, name):
    """用 Pillow 轉成 JPG，回傳 bytes 或 None"""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPG_QUALITY)
        return buf.getvalue()
    except Exception as e:
        print(f"    ❌ 轉 JPG 失敗 [{item_id}]：{e}")
        return None


# ════════════════════════════════════════════════════════════
# 6. 上傳到 Drive + 設公開可讀
# ════════════════════════════════════════════════════════════
def upload_to_drive(drive_svc, jpg_bytes, filename, folder_id):
    """上傳 jpg bytes 到 Drive，設任何人可讀，回傳 file_id 或 None"""
    try:
        meta = {
            "name": filename,
            "parents": [folder_id],
        }
        media = MediaIoBaseUpload(
            io.BytesIO(jpg_bytes),
            mimetype="image/jpeg",
            resumable=False,
        )
        file = drive_svc.files().create(
            body=meta,
            media_body=media,
            fields="id",
        ).execute()
        file_id = file.get("id")

        # 設為任何人知道連結都能查看
        drive_svc.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        return file_id
    except Exception as e:
        print(f"    ❌ 上傳失敗 [{filename}]：{e}")
        return None


def drive_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}&export=view"


# ════════════════════════════════════════════════════════════
# 7. 寫回 Items K 欄
# ════════════════════════════════════════════════════════════
def write_k_column(sheets_svc, updates):
    """updates: list of (row_index_1based, url)"""
    if not updates:
        print("  沒有需要寫入的資料。")
        return 0

    data = [
        {"range": f"{ITEMS_TAB}!K{row_i}", "values": [[url]]}
        for row_i, url in updates
    ]
    body = {"valueInputOption": "RAW", "data": data}
    result = sheets_svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID, body=body
    ).execute()
    return result.get("totalUpdatedCells", 0)


# ════════════════════════════════════════════════════════════
# 主程式
# ════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("整理_品項圖片_pipeline.py 開始")
    print("=" * 60)

    # 1. 認證
    print("\n[1] 取得 OAuth 認證...")
    creds = get_credentials()
    bearer = creds.token
    slides_svc = build("slides",  "v1",  credentials=creds)
    sheets_svc = build("sheets",  "v4",  credentials=creds)
    drive_svc  = build("drive",   "v3",  credentials=creds)
    print("  ✅ 認證完成")

    # 2. 讀取 Items 表
    print("\n[2] 讀取 Items 工作表...")
    items = read_items(sheets_svc)
    print(f"  共 {len(items)} 筆品項")

    # 3. 抽 Slides 映射（備用：給空 K 欄的品項補圖）
    print("\n[3] 從 Slides 抽取品名→圖片映射...")
    slide_map = extract_slide_name_url_map(slides_svc)

    # 4. 逐筆處理
    print("\n[4] 下載 → 轉 JPG → 上傳 Drive → 準備更新 K 欄")
    print("-" * 60)

    k_updates   = []   # (row, new_drive_url)
    report      = []   # 最終報告行

    done_urls = {}     # 原始 URL → Drive file_id（去重，同 URL 不重複上傳）

    for item in items:
        row      = item["row"]
        item_id  = item["item_id"]
        name     = item["name"]
        old_url  = item["old_url"]
        filename = f"{item_id}_{name}.jpg"

        # 已有 Drive URL → 跳過（已處理完成）
        if "drive.google.com" in old_url:
            report.append({
                "item_id": item_id, "name": name,
                "old_url": old_url, "new_url": old_url,
                "status": "⏭ 已有 Drive URL"
            })
            continue

        # 決定來源 URL
        # googleusercontent 的舊 URL 已過期（HTTP 403），重新從 Slides 抓新鮮 URL
        src_url  = old_url
        src_type = "existing"

        if not src_url or "googleusercontent" in src_url:
            # 嘗試 Slide 映射（取得新鮮 URL）
            match = slide_match(name, slide_map)
            if match:
                src_url, matched_key = match
                src_type = f"slide_fresh({matched_key[:20]})"
            elif not old_url:
                # 無任何圖片來源
                report.append({
                    "item_id": item_id, "name": name,
                    "old_url": "", "new_url": "",
                    "status": "❌ 無圖"
                })
                print(f"  ❌ 無圖：{item_id} {name}")
                continue
            else:
                # 有 googleusercontent 但 Slides 比對不到，跳過（無法下載）
                report.append({
                    "item_id": item_id, "name": name,
                    "old_url": old_url, "new_url": "",
                    "status": "❌ Slides 無對應（舊URL過期）"
                })
                print(f"  ❌ Slides 無對應：{item_id} {name}")
                continue

        # 已處理過相同 URL 的品項（如 APP020/APP021 共用同一張圖）
        if src_url in done_urls:
            existing_id = done_urls[src_url]
            new_url = drive_url(existing_id)
            k_updates.append((row, new_url))
            report.append({
                "item_id": item_id, "name": name,
                "old_url": old_url, "new_url": new_url,
                "status": "✅ 共用既有圖"
            })
            print(f"  ♻️  {item_id} {name[:20]} → 共用 {existing_id}")
            continue

        # 判斷是否需要 bearer（googleusercontent）
        needs_auth = "googleusercontent" in src_url

        print(f"  ↓  {item_id} {name[:20]} ({src_type}{'  [auth]' if needs_auth else ''})")

        # 下載
        img_bytes = download_image(src_url, bearer if needs_auth else None)
        if not img_bytes:
            report.append({
                "item_id": item_id, "name": name,
                "old_url": old_url, "new_url": "",
                "status": "❌ 下載失敗"
            })
            continue

        # 轉 JPG
        jpg = to_jpg_bytes(img_bytes, item_id, name)
        if not jpg:
            report.append({
                "item_id": item_id, "name": name,
                "old_url": old_url, "new_url": "",
                "status": "❌ 轉 JPG 失敗"
            })
            continue

        # 上傳到 Drive
        file_id = upload_to_drive(drive_svc, jpg, filename, ITEMS_PHOTOS_ID)
        if not file_id:
            report.append({
                "item_id": item_id, "name": name,
                "old_url": old_url, "new_url": "",
                "status": "❌ 上傳失敗"
            })
            continue

        new_url = drive_url(file_id)
        done_urls[src_url] = file_id
        k_updates.append((row, new_url))
        report.append({
            "item_id": item_id, "name": name,
            "old_url": old_url, "new_url": new_url,
            "status": "✅ 已上傳"
        })
        print(f"     ✅ → Drive: {file_id}")

    # 5. 批次寫回 K 欄
    print(f"\n[5] 寫入 K 欄（{len(k_updates)} 筆）...")
    cells_updated = write_k_column(sheets_svc, k_updates)
    print(f"  ✅ 更新 {cells_updated} 格")

    # 6. 輸出完整對照報告
    print("\n" + "=" * 60)
    print("完整對照報告")
    print("=" * 60)
    print(f"{'item_id':<10} {'品名':<30} {'狀態':<12} {'舊 URL 類型':<15} 新 Drive URL")
    print("-" * 100)
    for r in report:
        old_type = (
            "googleusercontent" if "googleusercontent" in r["old_url"]
            else "avif"  if "avif"  in r["old_url"]
            else "webp"  if "webp"  in r["old_url"]
            else "drive" if "drive" in r["old_url"]
            else "(空白)" if not r["old_url"]
            else "other"
        )
        print(f"{r['item_id']:<10} {r['name'][:28]:<30} {r['status']:<12} {old_type:<15} {r['new_url'][:60]}")

    # 統計
    success = [r for r in report if "✅" in r["status"]]
    no_img  = [r for r in report if "無圖" in r["status"]]
    failed  = [r for r in report if "❌" in r["status"] and "無圖" not in r["status"]]

    print("\n" + "=" * 60)
    print("統計摘要")
    print("=" * 60)
    print(f"  總品項：{len(items)}")
    print(f"  ✅ 成功（含共用）：{len(success)}")
    print(f"  ❌ 無圖（給 Owner 補齊）：{len(no_img)}")
    print(f"  ❌ 失敗（下載/轉換/上傳）：{len(failed)}")

    if no_img:
        print("\n無圖品項清單（需 Owner 提供照片）：")
        for r in no_img:
            print(f"  {r['item_id']:<10} {r['name']}")

    if failed:
        print("\n失敗品項：")
        for r in failed:
            print(f"  {r['item_id']:<10} {r['name']} — {r['status']}")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
