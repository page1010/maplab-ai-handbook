#!/usr/bin/env python3
"""
相似品項共用_第二輪.py
更寬鬆策略：八成像就好
- 讀 Items Sheet + Drive Items_Photos 清單
- 對缺圖品項找外觀相似的已有圖品項
- Drive files.copy() → 重命名 → 更新 K 欄
"""

import json
import re
import sys
from pathlib import Path

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError as e:
    print(f"❌ 缺套件：{e}")
    print("pip install google-auth google-auth-oauthlib google-api-python-client --user")
    sys.exit(1)

# ── 常數 ─────────────────────────────────────────────────────
SHEET_ID        = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
ITEMS_TAB       = "Items"
ITEMS_PHOTOS_ID = "1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT"
TOKEN_PATH      = Path.home() / ".claude/mcp-keys/google-token.json"

# ── 明確相似映射（target_id → source_id 候選清單，依優先順序）──
EXPLICIT_MAP = {
    "DST003": ["DST022", "DST023"],          # 迷你瑪德蓮 → 瑪德蓮
    "DST007": ["DST023", "DST022"],          # 迷你瑪德蓮淋面 → 瑪德蓮淋面
    "APP011": ["APP012"],                    # 日式薄餅 → 法式薄餅（互補）
    "APP012": ["APP011"],                    # 法式薄餅 → 日式薄餅（互補）
    "DST034": ["DST002"],                    # 奶油餅乾 → 玫瑰餅乾
    "DST002": ["DST034"],                    # 玫瑰愛心 → 奶油餅乾
    "DST013": ["DST020", "DST019"],          # 提拉米蘇 → 鮮奶酪派對杯
    "DST028": ["DST017", "DST040"],          # 咕咕霍夫 → 任何蛋糕類
    "APP028": ["APP016", "APP013"],          # 鵝胸葡萄小串 → 魚腸小串
    "APP001": ["APP016", "APP013"],          # 捲腸 → 小串類
    "APP039": ["APP013", "APP016"],          # 莎莎醬奶小品 → appetizer 類
    "DST001": ["DST019", "DST017"],          # 焦糖千層酥 → 千層/塔類
    "DST005": ["DST025", "DST027"],          # 愛心馬林糖棒 → 馬林糖/糖類
    "DST006": ["DST040", "DST042"],          # 杏仁和菓子 → 甜點類
    "MAIN001": ["MAIN002", "MAIN003", "MAIN004", "MAIN005",
                "MAIN006", "MAIN007", "MAIN008", "MAIN009"],  # 豬里肌 → 任何主食
}

# BEV 飲品：先嘗試同類別互補，再用任何有圖的 BEV
BEV_IDS = [f"BEV{str(i).zfill(3)}" for i in range(1, 9)]  # BEV001–BEV008


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


def read_items(sheets_svc):
    """回傳 list of dict：row, item_id, name, image_url"""
    result = sheets_svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{ITEMS_TAB}!A1:L300",
    ).execute()
    rows = result.get("values", [])
    if not rows:
        return []
    headers = rows[0]
    h = [x.lower().strip() for x in headers]
    idx_id   = h.index("item_id")       if "item_id"       in h else 0
    idx_name = h.index("standard_name") if "standard_name" in h else 2
    idx_k    = 10  # K 欄 image_url

    items = []
    for row_i, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        item_id = row[idx_id].strip()   if len(row) > idx_id   else ""
        name    = row[idx_name].strip() if len(row) > idx_name else ""
        url     = row[idx_k].strip()    if len(row) > idx_k    else ""
        if not item_id and not name:
            continue
        items.append({"row": row_i, "item_id": item_id, "name": name, "url": url})
    return items


def list_drive_files(drive_svc):
    """列出 Items_Photos 所有檔案，回傳 {item_id: {id, name, webViewLink}}"""
    files = {}
    page_token = None
    while True:
        resp = drive_svc.files().list(
            q=f"'{ITEMS_PHOTOS_ID}' in parents and trashed=false",
            fields="nextPageToken,files(id,name,webViewLink,mimeType)",
            pageSize=200,
            pageToken=page_token,
        ).execute()
        for f in resp.get("files", []):
            fname = f["name"]
            # 從檔名萃取 item_id（格式 APP001_xxx.jpg）
            m = re.match(r'^([A-Z]+\d+)_', fname)
            if m:
                fid = m.group(1)
                files[fid] = {
                    "drive_id": f["id"],
                    "name": fname,
                    "url": f.get("webViewLink", ""),
                }
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


def drive_copy(drive_svc, source_file_id, new_name, parent_id):
    """複製 Drive 檔案，回傳新檔案 dict"""
    body = {"name": new_name, "parents": [parent_id]}
    return drive_svc.files().copy(
        fileId=source_file_id,
        body=body,
        fields="id,name,webViewLink",
    ).execute()


def update_sheet_k(sheets_svc, row_index, url):
    """更新 Items K 欄（col 11，1-based）"""
    range_str = f"{ITEMS_TAB}!K{row_index}"
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="RAW",
        body={"values": [[url]]},
    ).execute()


# ════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("🔄 第二輪相似品項共用 — 寬鬆策略")
    print("=" * 60)

    creds = get_credentials()
    sheets_svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
    drive_svc  = build("drive",  "v3", credentials=creds, cache_discovery=False)

    # Step 1: 讀取資料
    print("\n📋 Step 1：讀取 Items 表 + Drive 清單")
    items = read_items(sheets_svc)
    drive_files = list_drive_files(drive_svc)

    print(f"  Items 共 {len(items)} 筆")
    print(f"  Drive Items_Photos 共 {len(drive_files)} 個檔案")

    # 建立 item_id → row 映射
    item_map = {it["item_id"]: it for it in items}

    # 找出缺圖品項（K 欄空白且 Drive 也沒有）
    missing = []
    for it in items:
        iid = it["item_id"]
        has_sheet_url = bool(it["url"])
        has_drive_file = iid in drive_files
        if not has_sheet_url and not has_drive_file:
            missing.append(it)

    print(f"\n  缺圖品項（K 欄空 + Drive 無檔）：{len(missing)} 筆")
    for m in missing:
        print(f"    {m['item_id']} {m['name']}")

    # Step 2: 相似配對
    print("\n🔗 Step 2：相似配對")
    pairs = []   # (target_item, source_drive_file, source_item_id)

    for target in missing:
        tid = target["item_id"]
        matched_src = None
        matched_sid = None

        # 先查 explicit map
        candidates = EXPLICIT_MAP.get(tid, [])

        # BEV 類：若沒有 explicit，嘗試任何已有圖的 BEV
        if not candidates and tid.startswith("BEV"):
            candidates = [s for s in BEV_IDS if s != tid]
            # 再加任何有圖的 BEV（Drive 裡）
            bev_in_drive = [k for k in drive_files if k.startswith("BEV")]
            candidates = list(dict.fromkeys(candidates + bev_in_drive))

        for sid in candidates:
            if sid in drive_files:
                matched_src = drive_files[sid]
                matched_sid = sid
                break

        if matched_src:
            pairs.append((target, matched_src, matched_sid))
            print(f"  ✅ {tid} {target['name'][:20]}")
            print(f"       → 共用 {matched_sid} ({matched_src['name']})")
        else:
            print(f"  ❌ {tid} {target['name'][:20]} — 找不到合適的來源")

    print(f"\n  可共用：{len(pairs)} 筆，真正無法補：{len(missing) - len(pairs)} 筆")

    # Step 3: 執行共用
    print("\n📁 Step 3：Drive copy + 更新 K 欄")
    success, fail = 0, 0

    for target, src_file, src_id in pairs:
        tid = target["item_id"]
        tname = target["name"].replace("/", "、").replace(" ", "_")
        new_filename = f"{tid}_{tname}.jpg"

        try:
            # Drive copy
            new_file = drive_copy(drive_svc, src_file["drive_id"], new_filename, ITEMS_PHOTOS_ID)
            new_url = new_file.get("webViewLink", "")
            print(f"  ✅ {tid}: 已複製 → {new_filename}")

            # 更新 K 欄
            update_sheet_k(sheets_svc, target["row"], new_url)
            print(f"     K{target['row']} 已更新：{new_url[:60]}...")
            success += 1

        except Exception as e:
            print(f"  ❌ {tid} 失敗：{e}")
            fail += 1

    # Step 4: 最終統計
    print("\n" + "=" * 60)
    print("📊 Step 4：最終報告")
    print("=" * 60)

    # 重新讀取 Drive（含剛複製的新檔）
    drive_files_after = list_drive_files(drive_svc)
    # 重新讀取 Sheet
    items_after = read_items(sheets_svc)
    item_map_after = {it["item_id"]: it for it in items_after}

    has_img, no_img = [], []
    for it in items_after:
        iid = it["item_id"]
        if it["url"] or iid in drive_files_after:
            has_img.append(iid)
        else:
            no_img.append(f"{iid} {it['name']}")

    print(f"\n  ✅ 本輪成功共用：{success} 筆")
    if fail:
        print(f"  ❌ 本輪失敗：{fail} 筆")
    print(f"\n  📸 有圖品項：{len(has_img)} 筆")
    print(f"  🕳️  無圖品項：{len(no_img)} 筆")
    if no_img:
        print("\n  真正無法補的品項：")
        for n in no_img:
            print(f"    {n}")

    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
