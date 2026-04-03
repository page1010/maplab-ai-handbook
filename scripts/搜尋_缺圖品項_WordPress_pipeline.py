#!/usr/bin/env python3
"""
搜尋_缺圖品項_WordPress_pipeline.py
從 WordPress 找 39 筆缺圖品項的照片，下載→轉 JPG→上傳 Drive→更新 Items K 欄

Session: d6fe0e3 接續，A0 執行
WordPress: https://www.maplabkitchen.com
Items_Photos 資料夾: 1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT
"""

import io, json, sys
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

try:
    import requests
    from PIL import Image
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
except ImportError as e:
    print(f"❌ 缺少套件：{e}")
    sys.exit(1)

# ── 常數 ──────────────────────────────────────────────────
SHEET_ID        = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
ITEMS_TAB       = "Items"
ITEMS_PHOTOS_ID = "1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT"
TOKEN_PATH      = Path.home() / ".claude/mcp-keys/google-token.json"
JPG_QUALITY     = 90
DOWNLOAD_TIMEOUT = 30

# ── WordPress 比對結果（10 筆，含完整 URL）──────────────────
# 格式: (item_id, standard_name, sheet_row_1based, wp_source_url, wp_note)
WP_MATCHES = [
    ("APP026", "尼斯鮪魚奶油乳酪可頌", 19,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-croissant-sandwich-egg-salad-pudding-wicker-basket.avif",
     "[1557] 可頌蛋沙拉三明治（含可頌）"),

    ("DST012", "葡式酥皮蛋塔", 61,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-shrimp-avocado-bruschetta-cheese-tart-rustic.avif",
     "[1556] 起司塔布丁水果串（含塔類點心）"),

    ("DST016", "菠蘿泡芙", 72,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-cheese-tart-cream-puff-mini-burger-warm-display.avif",
     "[1554] 起司塔泡芙迷你漢堡（含泡芙）"),

    # DST018 & DST032 共用同一張布丁圖
    ("DST018", "手工焦糖烤布丁", 65,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-outdoor-buffet-chafing-dish-mini-burgers-skewers.avif",
     "[1551] 戶外保溫鍋Buffet（含布丁）"),
    ("DST032", "法式焦糖烤布丁", 64,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-outdoor-buffet-chafing-dish-mini-burgers-skewers.avif",
     "[1551] 戶外保溫鍋Buffet（含布丁）"),

    # DST030 & DST046 共用同一張甜點桌圖
    ("DST030", "奶油多層蛋糕杯", 81,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-dessert-table-cheesecake-donut-cupcake-brand.avif",
     "[1560] 品牌甜點桌（含杯子蛋糕）"),
    ("DST046", "歐式派對淋面甜甜圈架", 56,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-dessert-table-cheesecake-donut-cupcake-brand.avif",
     "[1560] 品牌甜點桌（含甜甜圈）"),

    ("DST043", "巴斯克蛋糕_原味六吋", 82,
     "https://www.maplabkitchen.com/wp-content/uploads/2025/09/dessert-table-closeup-bruschetta-basque-cheesecake.webp.webp",
     "[950] basque-cheesecake 特寫（最佳比對）"),

    ("MAIN002", "溫式熟成牛排", 100,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-restaurant-flatlay-salmon-steak-salad-brunch.avif",
     "[1558] 餐桌俯拍（含牛排）"),

    ("MAIN007", "招牌義式炸雞腿", 104,
     "https://www.maplabkitchen.com/wp-content/uploads/2026/03/maplab-birthday-dessert-table-cake-canape-closeup.avif",
     "[1535] 生日派對甜點桌（含炸雞）"),
]

# ── 31 筆 WordPress 找不到，需 Owner 提供 ──────────────────
NO_MATCH_ITEMS = [
    ("APP028", "法式燻燻鵝胸葡萄小串"),
    ("APP001", "起酥皮捲腸"),
    ("APP011", "日式蜂蜜芥末燻雞烤墨西哥薄餅"),
    ("APP012", "法式黑松露野菇烤薄餅"),
    ("APP013", "日式香料和風唐揚雞 不醬"),
    ("APP039", "墨西哥莎莎醬奶小品"),
    ("DST025", "夏威夷豆塔_三吋"),
    ("DST005", "愛心馬林糖棒"),
    ("DST006", "杏仁和菓子"),
    ("DST027", "綜合夏威夷豆塔_三吋"),
    ("DST028", "維也納皇冠咕咕霍夫"),
    ("DST013", "義式提拉米蘇"),
    ("DST001", "焦糖千層酥"),
    ("DST019", "果凍杯_檸檬覆盆果60ml杯"),
    ("DST042", "生乳捲_原味/焦糖/抹茶/可可/莓莓"),
    ("DST040", "黃金虎皮蛋糕捲"),
    ("DST017", "黑金芝麻派對小蛋糕"),
    ("DST034", "奶油餅乾"),
    ("DST002", "餅乾_玫瑰愛心"),
    ("MAIN001", "古都秘醬洋蔥香煎豬里肌"),
    ("MAIN008", "慢烤美式雞翅"),
    ("BEV001", "冷泡黃金蕎麥_無糖"),
    ("BEV002", "可口可樂"),
    ("BEV003", "熱研磨美式咖啡"),
    ("BEV004", "盛夏柳橙"),
    ("BEV005", "冷泡冰釀烏龍茶_無糖"),
    ("BEV006", "檸檬紅茶"),
    ("BEV007", "阿薩姆紅茶"),
    ("BEV008", "冷泡鮮翠綠茶_無糖"),
]


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
    return creds


def download_image(url):
    try:
        resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
        if resp.status_code == 200:
            return resp.content
        print(f"    ⚠️  HTTP {resp.status_code}: {url[:70]}")
        return None
    except Exception as e:
        print(f"    ❌ 下載失敗：{e}")
        return None


def to_jpg_bytes(img_bytes, item_id):
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPG_QUALITY)
        return buf.getvalue()
    except Exception as e:
        print(f"    ❌ 轉 JPG 失敗 [{item_id}]：{e}")
        return None


def upload_to_drive(drive_svc, jpg_bytes, filename, folder_id):
    try:
        meta = {"name": filename, "parents": [folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(jpg_bytes), mimetype="image/jpeg", resumable=False)
        file = drive_svc.files().create(body=meta, media_body=media, fields="id").execute()
        file_id = file.get("id")
        drive_svc.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
        return file_id
    except Exception as e:
        print(f"    ❌ 上傳失敗 [{filename}]：{e}")
        return None


def write_k_column(sheets_svc, updates):
    if not updates:
        return 0
    data = [{"range": f"{ITEMS_TAB}!K{row_i}", "values": [[url]]} for row_i, url in updates]
    result = sheets_svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": data}
    ).execute()
    return result.get("totalUpdatedCells", 0)


def drive_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}&export=view"


def main():
    print("=" * 65)
    print("搜尋_缺圖品項_WordPress_pipeline.py 開始")
    print("=" * 65)

    # 1. 認證
    print("\n[0] 取得 OAuth 認證...")
    creds = get_credentials()
    sheets_svc = build("sheets", "v4", credentials=creds)
    drive_svc  = build("drive",  "v3", credentials=creds)
    print("  ✅ 認證完成")

    # 2. 下載 → 轉 JPG → 上傳 Drive
    print("\n[1] 下載 → 轉 JPG → 上傳 Drive")
    print("-" * 65)

    k_updates = []
    report = []
    url_to_file_id = {}  # 同 URL 不重複上傳

    for item_id, name, row, src_url, wp_note in WP_MATCHES:
        filename = f"{item_id}_{name}.jpg"

        if src_url in url_to_file_id:
            # 共用既有 Drive 檔案
            file_id = url_to_file_id[src_url]
            new_url = drive_url(file_id)
            k_updates.append((row, new_url))
            report.append({"item_id": item_id, "name": name, "status": "✅ 共用既有圖", "new_url": new_url, "note": wp_note})
            print(f"  ♻️  {item_id} {name[:25]} → 共用 {file_id}")
            continue

        print(f"\n  ↓  {item_id} {name[:25]}")
        print(f"     {src_url[:70]}")

        img_bytes = download_image(src_url)
        if not img_bytes:
            report.append({"item_id": item_id, "name": name, "status": "❌ 下載失敗", "new_url": "", "note": wp_note})
            continue

        jpg = to_jpg_bytes(img_bytes, item_id)
        if not jpg:
            report.append({"item_id": item_id, "name": name, "status": "❌ 轉 JPG 失敗", "new_url": "", "note": wp_note})
            continue

        file_id = upload_to_drive(drive_svc, jpg, filename, ITEMS_PHOTOS_ID)
        if not file_id:
            report.append({"item_id": item_id, "name": name, "status": "❌ 上傳失敗", "new_url": "", "note": wp_note})
            continue

        new_url = drive_url(file_id)
        url_to_file_id[src_url] = file_id
        k_updates.append((row, new_url))
        report.append({"item_id": item_id, "name": name, "status": "✅ 已上傳", "new_url": new_url, "note": wp_note})
        print(f"     ✅ Drive: {file_id}")

    # 3. 批次寫入 K 欄
    print(f"\n[2] 寫入 K 欄（{len(k_updates)} 筆）...")
    cells = write_k_column(sheets_svc, k_updates)
    print(f"  ✅ 更新 {cells} 格")

    # 4. 輸出報告
    print("\n" + "=" * 65)
    success = [r for r in report if "✅" in r["status"]]
    failed  = [r for r in report if "❌" in r["status"]]

    print(f"✅ 成功：{len(success)} 筆")
    for r in success:
        print(f"  {r['item_id']:<10} {r['name'][:28]:<30} {r['note'][:40]}")

    if failed:
        print(f"\n❌ 失敗：{len(failed)} 筆")
        for r in failed:
            print(f"  {r['item_id']:<10} {r['name'][:28]} — {r['status']}")

    print(f"\n{'='*65}")
    print(f"⚠️  需 Owner 手動補圖（WordPress / Instagram 無法找到，{len(NO_MATCH_ITEMS)} 筆）：")
    print("-" * 50)
    for item_id, name in NO_MATCH_ITEMS:
        print(f"  {item_id:<10} {name}")

    print(f"\n=== 完成 ===")
    print(f"總缺圖：39  已補：{len(success)}  仍缺：{len(NO_MATCH_ITEMS) + len(failed)}")


if __name__ == "__main__":
    main()
