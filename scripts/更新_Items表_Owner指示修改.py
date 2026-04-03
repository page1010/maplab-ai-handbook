#!/usr/bin/env python3
"""
A0 執行 Owner 指示的 Items 表批量修改
Phase 3a: APP011 用 APP012 圖
Phase 3b: APP024 拆 5 個變體
Phase 3c: 新增 APP040 canape
Phase 3d: APP024-5 野菇普切塔 (含在 3b)
Phase 3e: 隱藏 D 欄
Phase 4:  更新 DropdownHelper
"""

import json, requests, sys

ACCESS_TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
SHEET_ID = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
ITEMS_SHEET_ID = 2137253687
DROPDOWN_SHEET_ID = 524757605

HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

def img_url(file_id):
    return f"https://drive.google.com/uc?id={file_id}&export=view"

# Drive file IDs
APP012_IMG  = "1I2LV03x2aiJcO_6Z2kXcHz04V6yrGFLa"
APP024_1    = "1pup0oUcpMSR5jQ-mSd-PZlfE4H20ihZy"   # 鮮蝦普切塔
APP024_2    = "15qtcDQVHhkZg_fPpkwF5sQH46PbIodPS"   # 煙燻鮭魚普切塔
APP024_3    = "1G2KbEToPkJ2tYojQCmLshf1nuh68SRmb"   # 番茄普切塔
APP024_4    = "1Z2QccnxNe-ynpmHNUWkuxfJBtRFxTo6h"   # 綜合普切塔
APP024_5    = "13LxNKoS3d1mkGtTavnfTXbBeTc8WpzeE"   # 野菇普切塔 (APP姑姑普切塔.jpg)
CANAPE_IMG  = "1_sDyXvjLDcWTvZeKiawR6uWNQWivgLJV"  # 火腿起司canape

# Row positions (1-indexed, before any insertion)
ROW_APP024 = 15   # APP024 current row
ROW_APP011 = 23   # APP011 current row
ROW_APP012 = 27   # APP012 current row
ROW_LAST   = 115  # APP039 (last item)

def run_batch_update(requests_list):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}:batchUpdate"
    resp = requests.post(url, headers=HEADERS, json={"requests": requests_list})
    if resp.status_code != 200:
        print(f"ERROR batchUpdate: {resp.status_code} {resp.text[:300]}")
        return False
    print(f"  batchUpdate OK ({len(requests_list)} requests)")
    return True

def update_cell_range(range_notation, values):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_notation}"
    params = {"valueInputOption": "USER_ENTERED"}
    resp = requests.put(url, headers=HEADERS, params=params, json={"values": values})
    if resp.status_code != 200:
        print(f"ERROR update {range_notation}: {resp.status_code} {resp.text[:200]}")
        return False
    info = resp.json()
    print(f"  Updated {range_notation}: {info.get('updatedCells',0)} cells")
    return True

def append_rows(sheet_range, values):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_range}:append"
    params = {"valueInputOption": "USER_ENTERED", "insertDataOption": "INSERT_ROWS"}
    resp = requests.post(url, headers=HEADERS, params=params, json={"values": values})
    if resp.status_code != 200:
        print(f"ERROR append: {resp.status_code} {resp.text[:200]}")
        return False
    info = resp.json()
    print(f"  Appended to {sheet_range}: {info.get('updates',{}).get('updatedCells',0)} cells")
    return True

def make_string_cell(value):
    return {"userEnteredValue": {"stringValue": str(value)}}

def make_number_cell(value):
    return {"userEnteredValue": {"numberValue": float(value)}}

# ─────────────────────────────────────────────
# STEP 1: Insert 5 rows after APP024 (row 15)
# ─────────────────────────────────────────────
print("\n[STEP 1] Insert 5 rows after APP024 (row 15)...")
insert_req = {
    "insertDimension": {
        "range": {
            "sheetId": ITEMS_SHEET_ID,
            "dimension": "ROWS",
            "startIndex": ROW_APP024,   # 0-based → inserts BEFORE row 16 (after row 15)
            "endIndex": ROW_APP024 + 5  # insert 5 rows
        },
        "inheritFromBefore": True
    }
}
ok = run_batch_update([insert_req])
if not ok:
    print("ABORT: row insertion failed")
    sys.exit(1)

# After insertion, shift positions
SHIFT = 5
ROW_APP011_NEW = ROW_APP011 + SHIFT   # 28
ROW_APP012_NEW = ROW_APP012 + SHIFT   # 32
ROW_LAST_NEW   = ROW_LAST   + SHIFT   # 120

print(f"  APP011 now at row {ROW_APP011_NEW}, APP012 at {ROW_APP012_NEW}")

# ─────────────────────────────────────────────
# STEP 2: Fill new rows 16-20 (APP024-1 to APP024-5)
# ─────────────────────────────────────────────
print("\n[STEP 2] Fill APP024-1 to APP024-5 (rows 16-20)...")

APP024_COST = 35  # from original APP024

new_variants = [
    # [item_id, category, standard_name, price, cost, unit, batch, cpu, active, note, image_url]
    ["APP024-1", "餐食小點", "鮮蝦普切塔",   "", str(APP024_COST+5),  "份", "", "", "Y", "APP024 系列", img_url(APP024_1)],
    ["APP024-2", "餐食小點", "煙燻鮭魚普切塔","", str(APP024_COST+10), "份", "", "", "Y", "APP024 系列", img_url(APP024_2)],
    ["APP024-3", "餐食小點", "番茄普切塔",   "", str(APP024_COST),    "份", "", "", "Y", "APP024 系列", img_url(APP024_3)],
    ["APP024-4", "餐食小點", "綜合普切塔",   "", str(APP024_COST),    "份", "", "", "Y", "APP024 系列", img_url(APP024_4)],
    ["APP024-5", "餐食小點", "野菇普切塔",   "", str(APP024_COST),    "份", "", "", "Y", "APP024 系列", img_url(APP024_5)],
]

# Write rows 16-20
for i, row_data in enumerate(new_variants):
    sheet_row = ROW_APP024 + 1 + i  # rows 16,17,18,19,20
    ok = update_cell_range(f"Items!A{sheet_row}:K{sheet_row}", [row_data])
    if not ok:
        print(f"  WARN: row {sheet_row} write failed")

# ─────────────────────────────────────────────
# STEP 3a: Update APP011 K column (use APP012 image)
# ─────────────────────────────────────────────
print(f"\n[STEP 3a] Update APP011 K{ROW_APP011_NEW} with APP012 image...")
update_cell_range(f"Items!K{ROW_APP011_NEW}", [[img_url(APP012_IMG)]])

# ─────────────────────────────────────────────
# STEP 3a': Update APP012 K column (was also missing image)
# ─────────────────────────────────────────────
print(f"\n[STEP 3a'] Update APP012 K{ROW_APP012_NEW} with its own image...")
update_cell_range(f"Items!K{ROW_APP012_NEW}", [[img_url(APP012_IMG)]])

# ─────────────────────────────────────────────
# STEP 3c: Append APP040 (canape)
# ─────────────────────────────────────────────
print("\n[STEP 3c] Append APP040 法式開胃小點 canape...")
canape_row = ["APP040", "餐食小點", "法式開胃小點 canape", "", "25", "份", "", "", "Y", "", img_url(CANAPE_IMG)]
append_rows("Items!A:K", [canape_row])

# ─────────────────────────────────────────────
# STEP 3e: Hide column D (default_price)
# ─────────────────────────────────────────────
print("\n[STEP 3e] Hide column D (default_price)...")
hide_req = {
    "updateDimensionProperties": {
        "range": {
            "sheetId": ITEMS_SHEET_ID,
            "dimension": "COLUMNS",
            "startIndex": 3,   # 0-based: D=3
            "endIndex": 4
        },
        "properties": {
            "hiddenByUser": True
        },
        "fields": "hiddenByUser"
    }
}
run_batch_update([hide_req])

# ─────────────────────────────────────────────
# STEP 4: Update DropdownHelper
# ─────────────────────────────────────────────
print("\n[STEP 4] Update DropdownHelper B column with new APP items...")
# Last known APP entry is at row 40 (澳式雞球迷你鬆餅)
# Adding: APP039 (墨西哥莎莎醬奶小品, was missing), APP024-1 to APP024-5, APP040
new_dropdown_items = [
    ["墨西哥莎莎醬奶小品"],    # APP039 (was missing)
    ["鮮蝦普切塔"],            # APP024-1
    ["煙燻鮭魚普切塔"],        # APP024-2
    ["番茄普切塔"],            # APP024-3
    ["綜合普切塔"],            # APP024-4
    ["野菇普切塔"],            # APP024-5
    ["法式開胃小點 canape"],   # APP040
]
append_rows("DropdownHelper!B:B", new_dropdown_items)

print("\n✅ ALL STEPS COMPLETE")
print(f"   APP024-1~5 inserted at rows 16-20")
print(f"   APP011 K at row {ROW_APP011_NEW}: {img_url(APP012_IMG)[:60]}...")
print(f"   APP012 K at row {ROW_APP012_NEW}: {img_url(APP012_IMG)[:60]}...")
print(f"   APP040 appended at end")
print(f"   Column D hidden")
print(f"   DropdownHelper updated with 7 new items")
