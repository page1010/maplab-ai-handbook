#!/usr/bin/env python3
"""
fix_items_photos_and_renumber.py
1. 修正 Items 工作表照片 URL 配對（依 Owner 確認）
2. 按 category + default_cost 重新指派 item_id

照片修正說明：
- Row 73-75（法式小塔）有起司蛋糕照片 → 移到 Row 22（起司公爵可頸），清除 73-75
- Row 83-84（杯子蛋糕）有布朗尼照片 → 移到 Row 66-67，清除 83-85
- Row 87（磅蛋糕）有香腸照片 → Row 49 已有正確香腸照，清除 87
- Row 97（鬆餅）有蝦排照片 → Row 32 已有正確蝦排照，清除 97
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID   = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg'
ITEMS_TAB  = 'Items'
TOKEN_PATH = Path.home() / '.claude/mcp-keys/google-token.json'


def get_credentials():
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes'),
    )
    if creds.expired and creds.refresh_token:
        print("Token 過期，刷新中...")
        creds.refresh(Request())
        token_data['token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
        print("Token 已刷新。")
    return creds


def read_sheet(sheets, range_str):
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=range_str,
    ).execute()
    return result.get('values', [])


def batch_write(sheets, data):
    if not data:
        print("  (無需寫入)")
        return 0
    result = sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={'valueInputOption': 'RAW', 'data': data}
    ).execute()
    return result.get('totalUpdatedCells', 0)


def main():
    creds = get_credentials()
    sheets = build('sheets', 'v4', credentials=creds)

    # ── 讀取現有資料 ──────────────────────────────────────────
    rows = read_sheet(sheets, f'{ITEMS_TAB}!A1:K200')
    print(f"讀取 {len(rows)} 行（含 header）")
    print(f"欄位：{rows[0]}")

    COL_ITEM_ID  = 0
    COL_CATEGORY = 1
    COL_NAME     = 2
    COL_COST     = 4
    COL_IMG      = 10

    def get_row(row_num):
        """1-indexed"""
        return rows[row_num - 1] if row_num <= len(rows) else []

    def get_img(row_num):
        row = get_row(row_num)
        return row[COL_IMG] if len(row) > COL_IMG else ''

    # ── BACKUP 快照 ─────────────────────────────────────────
    print("\n=== BACKUP：修改前快照 ===")
    key_rows = [22, 32, 49, 66, 67, 73, 74, 75, 83, 84, 85, 87, 97]
    for r in key_rows:
        row = get_row(r)
        if row:
            item_id  = row[COL_ITEM_ID]  if len(row) > COL_ITEM_ID  else ''
            name     = row[COL_NAME]     if len(row) > COL_NAME     else ''
            img      = get_img(r)
            img_disp = img[:80] if img else '(空)'
            print(f"  R{r:3d}: [{item_id:12s}] {name[:28]:28s} | {img_disp}")

    # ── Step 3：修正照片 URL ──────────────────────────────────
    print("\n=== Step 3：修正照片 URL ===")
    photo_updates = []

    # 1. Row 73 URL → Row 22；清除 Rows 73, 74, 75
    url_73 = get_img(73)
    if url_73:
        print(f"  ✔ Row 73 起司蛋糕照片 → Row 22 ({get_row(22)[COL_NAME] if get_row(22) else '?'})")
        photo_updates.append({'range': f'{ITEMS_TAB}!K22', 'values': [[url_73]]})
    else:
        print("  ⚠ Row 73 無照片 URL，略過移動")
    for r in [73, 74, 75]:
        photo_updates.append({'range': f'{ITEMS_TAB}!K{r}', 'values': [['']]})
    print("  ✔ 清除 Rows 73, 74, 75 照片 URL")

    # 2. Row 83 URL → Row 66；Row 84 URL → Row 67；清除 Rows 83, 84, 85
    url_83 = get_img(83)
    url_84 = get_img(84)
    if url_83:
        print(f"  ✔ Row 83 布朗尼照片 → Row 66 ({get_row(66)[COL_NAME] if get_row(66) else '?'})")
        photo_updates.append({'range': f'{ITEMS_TAB}!K66', 'values': [[url_83]]})
    if url_84:
        print(f"  ✔ Row 84 布朗尼照片 → Row 67 ({get_row(67)[COL_NAME] if get_row(67) else '?'})")
        photo_updates.append({'range': f'{ITEMS_TAB}!K67', 'values': [[url_84]]})
    for r in [83, 84, 85]:
        photo_updates.append({'range': f'{ITEMS_TAB}!K{r}', 'values': [['']]})
    print("  ✔ 清除 Rows 83, 84, 85 照片 URL")

    # 3. 清除 Row 87（香腸照；Row 49 已有正確照片）
    print(f"  ✔ 清除 Row 87 照片 URL（Row 49 香腸已有正確照片）")
    photo_updates.append({'range': f'{ITEMS_TAB}!K87', 'values': [['']]})

    # 4. 清除 Row 97（蝦排照；Row 32 已有正確照片）
    print(f"  ✔ 清除 Row 97 照片 URL（Row 32 蝦排小漢堡已有正確照片）")
    photo_updates.append({'range': f'{ITEMS_TAB}!K97', 'values': [['']]})

    n = batch_write(sheets, photo_updates)
    print(f"\n  ✅ 照片修正：{n} 格寫入")

    # ── Step 4：重新編號 ─────────────────────────────────────
    print("\n=== Step 4：重新指派 item_id（按 default_cost 排序）===")

    # 重新讀取（照片修正後）
    rows = read_sheet(sheets, f'{ITEMS_TAB}!A1:K200')

    # 收集所有非空品項
    items = []
    for i, row in enumerate(rows[1:], start=2):  # skip header；1-indexed
        if not row or not row[0].strip():
            continue
        item_id  = row[0].strip()
        category = row[1].strip() if len(row) > 1 else ''
        name     = row[2].strip() if len(row) > 2 else ''
        cost_str = row[4].strip() if len(row) > 4 else ''
        try:
            cost = float(cost_str) if cost_str else 0
        except ValueError:
            cost = 0

        items.append({
            'row'     : i,
            'item_id' : item_id,
            'category': category,
            'name'    : name,
            'cost'    : cost,
        })

    # 按 item_id prefix 分組（APP, DST, MAIN, BEV, …）
    by_prefix = defaultdict(list)
    for item in items:
        match = re.match(r'^([A-Z]+)', item['item_id'])
        prefix = match.group(1) if match else 'UNK'
        item['prefix'] = prefix
        by_prefix[prefix].append(item)

    id_updates = []

    for prefix, prefix_items in sorted(by_prefix.items()):
        print(f"\n  {prefix} ({len(prefix_items)} 品項)：")

        # 以 item_id 數字部分為 series key（讓 DST034/DST034a 等變體維持相鄰）
        series = defaultdict(list)
        for item in prefix_items:
            m = re.match(r'^[A-Z]+(\d+)', item['item_id'])
            key = m.group(1) if m else item['item_id']
            series[key].append(item)

        # 按 series 最小 cost 排序
        def series_min_cost(group):
            costs = [it['cost'] for it in group if it['cost'] > 0]
            return min(costs) if costs else 999999

        sorted_series = sorted(series.values(), key=series_min_cost)

        # 指派新 ID
        counter = 1
        for group in sorted_series:
            group.sort(key=lambda x: x['cost'] if x['cost'] > 0 else 999999)
            for item in group:
                new_id = f"{prefix}{counter:03d}"
                counter += 1
                if new_id != item['item_id']:
                    print(f"    R{item['row']:3d}: {item['item_id']:12s} → {new_id}  "
                          f"({item['name'][:22]} cost={item['cost']})")
                    id_updates.append({
                        'range' : f"{ITEMS_TAB}!A{item['row']}",
                        'values': [[new_id]],
                    })

    if id_updates:
        n = batch_write(sheets, id_updates)
        print(f"\n  ✅ 重新編號：{n} 格寫入")
    else:
        print("\n  ✅ 所有 item_id 已是正確順序，無需修改")

    # ── Step 6：驗證 ────────────────────────────────────────
    print("\n=== Step 6：驗證 ===")
    rows_final = read_sheet(sheets, f'{ITEMS_TAB}!A1:K200')

    print("\n  關鍵行（照片修正前後對比）：")
    for r in key_rows:
        row = rows_final[r - 1] if r <= len(rows_final) else []
        if row:
            item_id = row[0] if len(row) > 0 else ''
            name    = row[2] if len(row) > 2 else ''
            img     = row[10] if len(row) > 10 else ''
            has_img = '✔ IMG' if img.startswith('http') else '  (空)'
            print(f"  R{r:3d}: [{item_id:12s}] {name[:28]:28s} {has_img}")

    print("\n=== 完成 ===")


if __name__ == '__main__':
    main()
