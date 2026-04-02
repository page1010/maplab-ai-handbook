#!/usr/bin/env python3
"""
extract_slide_photos_to_items.py
用 Google Slides API 讀取 Menu Showcase 品項照片 URL，
比對 Items 工作表品項名稱，寫入 K 欄 image_url。

Slide ID: 16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo
Sheet ID: 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
"""

import json
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ── 常數 ────────────────────────────────────────────────
SLIDE_ID   = "16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo"
SHEET_ID   = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
ITEMS_TAB  = "Items"

TOKEN_PATH = Path.home() / ".claude/mcp-keys/google-token.json"
CREDS_PATH = Path.home() / ".claude/mcp-keys/google-credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── 認證 ────────────────────────────────────────────────
def get_credentials():
    """
    從 google-token.json 載入憑證。
    token.json 格式為 google.oauth2.credentials.Credentials 的 to_json() 輸出。
    """
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", SCOPES),
    )

    if creds.expired and creds.refresh_token:
        print("Token 過期，正在刷新...")
        creds.refresh(Request())
        # 把新 token 寫回
        token_data["token"] = creds.token
        with open(TOKEN_PATH, "w") as f:
            json.dump(token_data, f, indent=2)
        print("Token 已刷新並寫回。")

    return creds


# ── Slide 解析：提取每頁的圖片 URL 與文字 ────────────────
def extract_slide_items(slides_service):
    """
    遍歷 Slide 所有頁面，找出包含圖片的 slide。
    回傳 list of dict: [{slide_index, image_url, texts}]
    """
    preso = slides_service.presentations().get(
        presentationId=SLIDE_ID,
        fields="slides(objectId,pageElements(shape,image))"
    ).execute()

    results = []
    for slide_idx, slide in enumerate(preso.get("slides", []), start=1):
        images = []
        texts  = []

        for elem in slide.get("pageElements", []):
            # 圖片元素
            img = elem.get("image")
            if img:
                src = img.get("sourceUrl") or img.get("contentUrl")
                if src:
                    images.append(src)

            # 文字元素
            shape = elem.get("shape", {})
            text_content = shape.get("text", {})
            for te in text_content.get("textElements", []):
                run = te.get("textRun")
                if run:
                    t = run.get("content", "").strip()
                    if t:
                        texts.append(t)

        if images:
            results.append({
                "slide_index": slide_idx,
                "images": images,
                "texts": texts,
            })

    return results


# ── 從 Slide 建立「品項名稱 → image_url」映射 ────────────
def is_chinese(text):
    """是否含有中文字"""
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def is_placeholder(text):
    """是否是佔位符文字（[Photo], [COVER PHOTO] 等）"""
    t = text.strip()
    return t.startswith("[") and t.endswith("]")


def is_header(text):
    """是否是 slide 標題（Menu Showcase, MENU, PORTFOLIO 等）"""
    headers = {"Menu Showcase", "MENU", "PORTFOLIO", "WHAT WE DO", "ABOUT US",
               "WHY CHOOSE US", "OUR PARTNERS", "Selected Works", "Our Services",
               "Our Advantages", "Trusted By"}
    return text.strip() in headers


def build_name_url_map(slide_items):
    """
    從每張投影片提取品項名稱 → 圖片 URL 映射。

    策略：
    1. 過濾掉 header、[Photo] 佔位、英文+數量行
    2. 只保留中文品名
    3. 對每張 slide：中文品名按順序 1:1 對應圖片

    回傳 dict: {中文品名: url}
    """
    name_url = {}

    for s in slide_items:
        images = s["images"]
        if not images:
            continue

        # 僅保留中文品名（去掉 header、[Photo]、英文+qty 行）
        zh_names = []
        for t in s["texts"]:
            if is_placeholder(t) or is_header(t):
                continue
            if is_chinese(t):
                zh_names.append(t)
            # 跳過英文+qty 格式（如 "Basil Pesto Chicken Sandwich (20)"）

        print(f"\n  Slide {s['slide_index']}: {len(images)} 張圖, 中文品名 {len(zh_names)} 個")
        for n in zh_names:
            print(f"    名: {n}")

        # 1:1 配對（圖片數與品名數取最小值）
        pairs = min(len(images), len(zh_names))
        for i in range(pairs):
            name_url[zh_names[i]] = images[i]
            print(f"    → 配對: {zh_names[i][:20]} ← {images[i][:60]}...")

    return name_url


# ── Sheets：讀取 Items 工作表 ────────────────────────────
def read_items_sheet(sheets_service):
    """
    讀取 Items 工作表，回傳 (headers, rows)
    rows: list of list (每列的值)
    """
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{ITEMS_TAB}!A1:L500",
    ).execute()
    rows = result.get("values", [])
    headers = rows[0] if rows else []
    return headers, rows


# ── 比對並建立更新資料 ────────────────────────────────────
def longest_common_substring(s1, s2):
    """計算兩字串最長公共子串長度"""
    if not s1 or not s2:
        return 0
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                max_len = max(max_len, dp[i][j])
    return max_len


def fuzzy_match(item_name, name_url_map, min_match_len=4):
    """
    對 item_name 進行模糊比對：
    1. 完全包含（一方包含另一方）
    2. 最長公共子串 ≥ min_match_len
    回傳 (url, match_key, score) 或 None
    """
    best_url, best_key, best_score = None, None, 0

    for key, url in name_url_map.items():
        if not is_chinese(key):
            continue
        # 精確包含
        if item_name in key or key in item_name:
            score = len(min(item_name, key, key=len))
            if score > best_score:
                best_url, best_key, best_score = url, key, score + 100  # 精確加權

        # 最長公共子串
        lcs = longest_common_substring(item_name, key)
        if lcs >= min_match_len and lcs > best_score:
            best_url, best_key, best_score = url, key, lcs

    if best_score > 0:
        return best_url, best_key, best_score
    return None


def match_and_prepare_updates(headers, rows, name_url_map):
    """
    比對 Items 表的 standard_name 欄與 name_url_map，找出 K 欄應填入的值。
    回傳 list of (row_index_1based, url)
    """
    # 找欄位 index（支援多種欄名）
    col_name = None
    col_k    = 10  # K = index 10（0-based）

    for i, h in enumerate(headers):
        h_lower = h.lower().strip()
        if h_lower in ("standard_name", "name_zh", "item_name", "品名", "name", "中文名", "name_tw"):
            col_name = i
            break

    if col_name is None:
        print("⚠️  找不到品名欄，嘗試第三欄（index=2）")
        col_name = 2

    print(f"\n欄位：standard_name 欄={col_name} ('{headers[col_name]}'), K 欄={col_k}")
    print(f"name_url_map 共 {len(name_url_map)} 筆（中文品名）")

    updates = []
    matched_log = []
    unmatched_log = []

    for row_i, row in enumerate(rows[1:], start=2):  # skip header, 1-based
        if not row:  # 跳過空列
            continue
        name = row[col_name].strip() if len(row) > col_name else ""
        if not name:
            continue

        # K 欄現有值
        k_val = row[col_k].strip() if len(row) > col_k else ""

        # 跳過已有 URL 的列
        if k_val.startswith("http"):
            continue

        # 模糊比對
        result = fuzzy_match(name, name_url_map)
        if result:
            url, matched_key, score = result
            updates.append((row_i, url))
            matched_log.append(f"  row {row_i}: [{name}] ← [{matched_key}] (score={score})")
        else:
            unmatched_log.append(f"  row {row_i}: {name} (K={k_val or '空白'})")

    print(f"\n✅ 比對成功：{len(updates)} 筆")
    for m in matched_log:
        print(m)
    print(f"\n⚠️  未比對：{len(unmatched_log)} 筆")
    for u in unmatched_log[:30]:
        print(u)

    return updates


# ── Sheets：批次寫入 K 欄 ────────────────────────────────
def write_k_column(sheets_service, updates):
    """
    updates: list of (row_index_1based, url)
    批次 batchUpdate 寫入 K 欄
    """
    if not updates:
        print("\n沒有需要寫入的資料。")
        return

    data = []
    for row_i, url in updates:
        data.append({
            "range": f"{ITEMS_TAB}!K{row_i}",
            "values": [[url]],
        })

    body = {"valueInputOption": "RAW", "data": data}
    result = sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID, body=body
    ).execute()

    print(f"\n✅ 寫入完成：{result.get('totalUpdatedCells', 0)} 格")


# ── 主程式 ────────────────────────────────────────────────
def main():
    print("=== extract_slide_photos_to_items.py ===")
    print(f"Slide: {SLIDE_ID}")
    print(f"Sheet: {SHEET_ID}")

    # 1. 取得認證
    creds = get_credentials()

    # 2. 建立 API 服務
    slides_service = build("slides", "v1", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)

    # 3. 從 Slide 提取圖片 + 文字
    print("\n--- 讀取 Slide ---")
    slide_items = extract_slide_items(slides_service)
    print(f"找到 {len(slide_items)} 張含圖片的投影片")

    # 4. 建立名稱→URL 映射
    print("\n--- 建立品項映射 ---")
    name_url_map = build_name_url_map(slide_items)
    print(f"\n品項名稱→URL 映射：{len(name_url_map)} 筆")

    if not name_url_map:
        print("⚠️  未從 Slide 提取到任何品項，請檢查 Slide 結構。")
        print("\n=== Slide 原始資料摘要 ===")
        for s in slide_items[:5]:
            print(f"  Slide {s['slide_index']}: images={len(s['images'])}, texts={s['texts'][:5]}")
        sys.exit(1)

    # 5. 讀取 Items 工作表
    print("\n--- 讀取 Items 工作表 ---")
    headers, rows = read_items_sheet(sheets_service)
    print(f"欄位：{headers}")
    print(f"共 {len(rows)-1} 筆品項")

    # 6. 比對 + 準備更新
    print("\n--- 比對品項 ---")
    updates = match_and_prepare_updates(headers, rows, name_url_map)

    # 7. 確認後寫入
    if updates:
        print(f"\n準備寫入 {len(updates)} 筆到 Items K 欄...")
        write_k_column(sheets_service, updates)
    else:
        print("\n沒有新的比對結果可寫入（可能全部已有 URL，或無比對成功）。")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
