#!/usr/bin/env python3
"""
A0 Phase 3f: 下載「未分割」照片 → 用 Pillow 裁切 → 重新上傳 → 更新 K 欄
裁切規則（依檔名關鍵字）：
  中上 → top 50%, x center (25-75%)
  左下 → bottom 50%, left 50%
  右下 / 下右 → bottom 50%, right 50%
  右  → right 50% (full height)
"""

import sys, os, io, json, requests, tempfile
from PIL import Image

ACCESS_TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
SHEET_ID = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
FOLDER_ID = "1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT"

HEADERS_JSON = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
HEADERS_AUTH = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

def img_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}&export=view"

# Files to process: (item_id, drive_file_id, crop_position)
# Crop positions: 中上, 左下, 右下, 右
UNCUT_FILES = [
    ("APP001", "1GltTejEqHy9Kua8Ie2Ufnt16Xdr5s6Qe", "中上"),
    ("DST012", "1iKRQ0Hv4E1qUi1xFN5RLRlOFJxB0WUNu", "左下"),
    ("DST017", "1AG9_5fQzBiyJGX4OU2paNNJVFeBqMETf", "左下"),
    ("DST034", "1a0327CqcCuCc0YhwZl4PimBNwtqsSf_d", "右下"),
    ("DST040", "1KzGlAz8cLfC4CORtvZVO0ZzQXRuYMDrj", "右下"),
    ("MAIN008", "1OULf-Shus_ptXtFmUQxzcLU45--QyIa7", "右"),
]

def crop_image(img: Image.Image, position: str) -> Image.Image:
    w, h = img.size
    if position == "中上":
        box = (int(w*0.25), 0, int(w*0.75), int(h*0.5))
    elif position == "左下":
        box = (0, int(h*0.45), int(w*0.55), h)
    elif position in ("右下", "下右"):
        box = (int(w*0.45), int(h*0.45), w, h)
    elif position == "右":
        box = (int(w*0.45), 0, w, h)
    else:
        print(f"  Unknown position '{position}', skipping crop")
        return img
    print(f"  Crop box: {box} (from {w}x{h})")
    return img.crop(box)

def download_drive_file(file_id: str) -> bytes:
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    resp = requests.get(url, headers=HEADERS_AUTH)
    if resp.status_code != 200:
        raise Exception(f"Download failed {resp.status_code}: {resp.text[:100]}")
    return resp.content

def upload_to_drive(image_bytes: bytes, filename: str) -> str:
    """Upload image to Items_Photos folder, return new file_id"""
    metadata = {
        "name": filename,
        "parents": [FOLDER_ID],
        "mimeType": "image/jpeg"
    }
    boundary = "boundary_maplab_upload"
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + image_bytes + f"\r\n--{boundary}--".encode("utf-8")

    upload_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": f"multipart/related; boundary={boundary}",
        "Content-Length": str(len(body))
    }
    resp = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=upload_headers,
        data=body
    )
    if resp.status_code not in (200, 201):
        raise Exception(f"Upload failed {resp.status_code}: {resp.text[:200]}")
    result = resp.json()
    return result["id"]

def set_drive_file_public(file_id: str):
    """Make file readable by anyone with link"""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
    resp = requests.post(url, headers=HEADERS_JSON, json={"role": "reader", "type": "anyone"})
    if resp.status_code not in (200, 201):
        print(f"  WARN: set_public failed {resp.status_code}")

def find_item_row(item_id: str, rows: list) -> int:
    """Find 1-indexed sheet row for item_id"""
    for i, row in enumerate(rows, 1):
        if row and row[0] == item_id:
            return i
    return -1

def update_k_column(sheet_row: int, new_url: str):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Items!K{sheet_row}"
    params = {"valueInputOption": "USER_ENTERED"}
    resp = requests.put(url, headers=HEADERS_JSON, params=params, json={"values": [[new_url]]})
    if resp.status_code != 200:
        print(f"  ERROR update K{sheet_row}: {resp.status_code}")
        return False
    return True

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
print("Phase 3f: Download → Crop → Upload → Update K")
print("=" * 55)

# 1. Load current sheet to find row positions
print("Loading current sheet data...")
resp = requests.get(
    f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Items!A1:A200",
    headers=HEADERS_AUTH
)
rows = resp.json().get("values", [])
print(f"  Sheet has {len(rows)} rows (including header)")

results = []

for item_id, file_id, position in UNCUT_FILES:
    print(f"\n[{item_id}] Crop position: {position}")
    try:
        # Find row
        sheet_row = find_item_row(item_id, rows)
        if sheet_row == -1:
            print(f"  ERROR: {item_id} not found in sheet!")
            results.append((item_id, "NOT FOUND", None))
            continue
        print(f"  Sheet row: {sheet_row}")

        # Download
        print(f"  Downloading file {file_id}...")
        raw_bytes = download_drive_file(file_id)
        print(f"  Downloaded {len(raw_bytes)} bytes")

        # Crop
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        print(f"  Original size: {img.size}")
        cropped = crop_image(img, position)
        print(f"  Cropped size: {cropped.size}")

        # Convert to JPEG bytes
        buf = io.BytesIO()
        cropped.save(buf, format="JPEG", quality=90)
        jpeg_bytes = buf.getvalue()

        # Upload cropped version
        new_filename = f"{item_id}_cropped.jpg"
        print(f"  Uploading as {new_filename}...")
        new_file_id = upload_to_drive(jpeg_bytes, new_filename)
        set_drive_file_public(new_file_id)
        print(f"  Uploaded → new file_id: {new_file_id}")

        # Update K column
        new_url = img_url(new_file_id)
        ok = update_k_column(sheet_row, new_url)
        print(f"  Updated K{sheet_row}: {'OK' if ok else 'FAILED'}")

        results.append((item_id, "OK", new_file_id))

    except Exception as e:
        print(f"  ERROR: {e}")
        results.append((item_id, f"ERROR: {e}", None))

# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("Phase 3f Summary:")
for item_id, status, fid in results:
    mark = "✅" if status == "OK" else "❌"
    print(f"  {mark} {item_id}: {status}" + (f" → {fid}" if fid else ""))
