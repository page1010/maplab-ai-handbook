#!/usr/bin/env python3
"""
QUOTE_DRAFT 母版格式美化腳本
只改顏色/字體/邊框，不動 cell 位置和內容

Row 位置確認 (2026-04-15):
  Row 1:  MAP LAB KITCHEN Header
  Row 2-5: 客戶資訊 (客戶/地址/活動型態/活動名稱)
  Row 6:  菜單 menu header
  Row 7:  鹹食小點 分類標籤
  Row 12: 手作精緻甜點 Dessert 分類標籤
  Row 16: 8L 壺裝飲品 飲品分類標籤
  Row 21: 費用區 header (項目/金額/備註)
  Row 30: 總金額
  Row 34: 合約條款 header
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ─── Config ────────────────────────────────────────────────────────────────────
SHEET_ID    = "1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg"
SHEET_NAME  = "QUOTE_DRAFT"
TOKEN_PATH  = os.path.expanduser("~/.claude/mcp-keys/google-token.json")

# ─── Brand Colors (0~1 fractions for Sheets API) ───────────────────────────────
def rgb(r, g, b):
    return {"red": r / 255.0, "green": g / 255.0, "blue": b / 255.0}

C_CHARCOAL    = rgb(61,  43,  31)   # 炭棕    #3D2B1F
C_WARM_BROWN  = rgb(139, 94,  60)   # 暖棕    #8B5E3C
C_WARM_GOLD   = rgb(201, 169, 110)  # 溫暖金  #C9A96E (備用)
C_CREAM       = rgb(250, 249, 245)  # 奶油白  #FAF9F5
C_LIGHT_BEIGE = rgb(240, 235, 227)  # 淺米灰  #F0EBE3
C_TEXT        = rgb(51,  51,  51)   # 正文    #333333
C_WHITE       = rgb(255, 255, 255)  # 白色

# ─── Column indices (0-indexed) ────────────────────────────────────────────────
COL_C, COL_D, COL_E, COL_F = 2, 3, 4, 5


def load_creds():
    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def get_sheet_id(service, spreadsheet_id, sheet_name):
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in meta["sheets"]:
        if sheet["properties"]["title"] == sheet_name:
            return sheet["properties"]["sheetId"]
    raise ValueError(f"Sheet '{sheet_name}' not found")


def grid_range(sid, r0, r1, c0, c1):
    """All indices 0-based, end-exclusive."""
    return {
        "sheetId":          sid,
        "startRowIndex":    r0,
        "endRowIndex":      r1,
        "startColumnIndex": c0,
        "endColumnIndex":   c1,
    }


def repeat_cell(sid, r0, r1, c0, c1, *, bg=None, fg=None, bold=None, size=None):
    """
    repeatCell 格式化請求。
    只寫入明確指定的欄位，不覆蓋其他現有格式。
    """
    fmt    = {}
    fields = []

    if bg is not None:
        fmt["backgroundColor"] = bg
        fields.append("userEnteredFormat.backgroundColor")

    tf = {}
    if fg is not None:
        tf["foregroundColor"] = fg
        fields.append("userEnteredFormat.textFormat.foregroundColor")
    if bold is not None:
        tf["bold"] = bold
        fields.append("userEnteredFormat.textFormat.bold")
    if size is not None:
        tf["fontSize"] = size
        fields.append("userEnteredFormat.textFormat.fontSize")
    if tf:
        fmt["textFormat"] = tf

    return {
        "repeatCell": {
            "range":  grid_range(sid, r0, r1, c0, c1),
            "cell":   {"userEnteredFormat": fmt},
            "fields": ",".join(fields),
        }
    }


def border(style="SOLID", width=1, color=None):
    b = {"style": style, "width": width}
    if color:
        b["color"] = color
    return b


def main():
    print("🔑 載入憑證...")
    creds   = load_creds()
    service = build("sheets", "v4", credentials=creds)

    print("📋 取得 sheet ID...")
    sid = get_sheet_id(service, SHEET_ID, SHEET_NAME)
    print(f"   sheetId = {sid}")

    requests = []

    # ── 1. Row 1 Header C1:F1 ─────────────────────────────────────────────────
    #    背景炭棕, 文字奶油白, 加粗
    requests.append(repeat_cell(
        sid, 0, 1, COL_C, COL_F + 1,
        bg=C_CHARCOAL, fg=C_CREAM, bold=True
    ))

    # ── 2. Row 2-5 資訊區 ─────────────────────────────────────────────────────
    #    Label 欄 C2:C5 — 淺米灰底 + 暖棕字
    requests.append(repeat_cell(
        sid, 1, 5, COL_C, COL_C + 1,
        bg=C_LIGHT_BEIGE, fg=C_WARM_BROWN
    ))
    #    Label 欄 E2:E5 — 淺米灰底 + 暖棕字
    requests.append(repeat_cell(
        sid, 1, 5, COL_E, COL_E + 1,
        bg=C_LIGHT_BEIGE, fg=C_WARM_BROWN
    ))
    #    Value 欄 D2:D5 — 白底 + 正文色
    requests.append(repeat_cell(
        sid, 1, 5, COL_D, COL_D + 1,
        bg=C_WHITE, fg=C_TEXT
    ))
    #    Value 欄 F2:F5 — 白底 + 正文色
    requests.append(repeat_cell(
        sid, 1, 5, COL_F, COL_F + 1,
        bg=C_WHITE, fg=C_TEXT
    ))

    # ── 3. Row 6 菜單 header C6:F6 ───────────────────────────────────────────
    #    背景暖棕, 文字奶油白, 加粗
    requests.append(repeat_cell(
        sid, 5, 6, COL_C, COL_F + 1,
        bg=C_WARM_BROWN, fg=C_CREAM, bold=True
    ))

    # ── 4. Row 7 鹹食小點 分類標籤 C7 ────────────────────────────────────────
    #    文字暖棕, 字體縮小 (9pt)
    requests.append(repeat_cell(
        sid, 6, 7, COL_C, COL_C + 1,
        fg=C_WARM_BROWN, size=9
    ))

    # ── 5. Row 12 Dessert 分類標籤 C12 ───────────────────────────────────────
    requests.append(repeat_cell(
        sid, 11, 12, COL_C, COL_C + 1,
        fg=C_WARM_BROWN, size=9
    ))

    # ── 6. Row 16 飲品分類標籤 C16 ───────────────────────────────────────────
    requests.append(repeat_cell(
        sid, 15, 16, COL_C, COL_C + 1,
        fg=C_WARM_BROWN, size=9
    ))

    # ── 7. Row 21 費用區 header C21:F21 ──────────────────────────────────────
    #    背景淺米灰
    requests.append(repeat_cell(
        sid, 20, 21, COL_C, COL_F + 1,
        bg=C_LIGHT_BEIGE
    ))

    # ── 8. Row 30 總金額 C30:F30 ─────────────────────────────────────────────
    #    背景暖棕, 文字奶油白, 加粗加大
    requests.append(repeat_cell(
        sid, 29, 30, COL_C, COL_F + 1,
        bg=C_WARM_BROWN, fg=C_CREAM, bold=True, size=14
    ))

    # ── 9. Row 34 合約條款 header C34:F34 ────────────────────────────────────
    #    文字暖棕, 加粗
    requests.append(repeat_cell(
        sid, 33, 34, COL_C, COL_F + 1,
        fg=C_WARM_BROWN, bold=True
    ))

    # ── 10. 整體外框 C1:F55 ──────────────────────────────────────────────────
    #    暖棕色細線外框
    warm_border = border("SOLID", 1, C_WARM_BROWN)
    requests.append({
        "updateBorders": {
            "range":  grid_range(sid, 0, 55, COL_C, COL_F + 1),
            "top":    warm_border,
            "bottom": warm_border,
            "left":   warm_border,
            "right":  warm_border,
        }
    })

    # ── Execute ───────────────────────────────────────────────────────────────
    print(f"🎨 送出 {len(requests)} 個格式化請求...")
    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": requests}
    ).execute()

    replies = resp.get("replies", [])
    print(f"✅ 完成！共 {len(replies)} 個回應")
    print("   格式項目：")
    print("     [1] Row 1  Header — 炭棕底 + 奶油白字 + 粗體")
    print("     [2] Row 2-5 Label — 淺米灰底 + 暖棕字")
    print("     [3] Row 2-5 Value — 白底 + 正文色")
    print("     [4] Row 6  菜單 header — 暖棕底 + 奶油白字 + 粗體")
    print("     [5] Row 7  鹹食小點 — 暖棕字 + 9pt")
    print("     [6] Row 12 Dessert — 暖棕字 + 9pt")
    print("     [7] Row 16 飲品 — 暖棕字 + 9pt")
    print("     [8] Row 21 費用區 header — 淺米灰底")
    print("     [9] Row 30 總金額 — 暖棕底 + 奶油白字 + 粗體 + 14pt")
    print("    [10] Row 34 合約條款 — 暖棕字 + 粗體")
    print("    [11] C1:F55 外框 — 暖棕細線")


if __name__ == "__main__":
    main()
