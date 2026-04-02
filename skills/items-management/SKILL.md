# Items 品項管理 Skill

> **版本**：v1.0 ｜ 建立：2026-04-02 ｜ 維護者：A0/A1
> **呼叫者**：A0 Cowork、A6 LINE 助手、A1 系統管理

---

## 觸發條件

Owner 說以下任何一句話時，啟動本 Skill：
- 「新增品項」、「加一個品項」、「加 XXX 到菜單」
- 「修正品項」、「更新品項分類」、「改成本」
- 「更新照片」、「換照片」、「補品項圖片」
- 「重新編號」、「品項排序」
- 「從 Slide 提取照片」、「同步菜單圖片」

---

## 前置條件

| 項目 | 說明 |
|------|------|
| Google API Token | `~/.claude/mcp-keys/google-token.json`（需要 drive + spreadsheets scope） |
| Sheet ID | `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` |
| Slide ID | `16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo`（Menu Showcase，照片提取用） |
| Items 工作表欄位 | A=item_id, B=category, C=name, D=default_price, E=default_cost, F=unit, G=min_qty, H=is_active, I=note, J=source_tag, K=image_url |

---

## Items 表結構速查

```
A: item_id     — APP/DST/MAIN/BEV 前綴 + 3位數序號（按 default_cost 排序，類似品項連號）
B: category    — 甜點 / 餐食小點 / 飲品 / 主食 / 招待
C: name        — 品項名稱（QUOTE_DRAFT / DropdownHelper 的 VLOOKUP/FILTER 鍵值）
D: default_price
E: default_cost
F: unit
G: min_qty
H: is_active   — TRUE/FALSE
I: note
J: source_tag  — APP / DST / MAIN（來源標籤）
K: image_url   — Google Drive 或 Slide 圖片 URL
```

---

## 標準操作流程（SOP）

### 操作 1：新增品項

1. **讀取 Items 現況**
   ```python
   # 用 Sheets API 讀取所有現有品項
   resp = sheets_svc.spreadsheets().values().get(
       spreadsheetId=SHEET_ID, range="Items!A2:K"
   ).execute()
   rows = resp.get("values", [])
   ```

2. **判斷品項分類（category）與前綴（source_tag）**
   - 甜點 / 餐食小點 / 主食 / 飲品 → 依 source_tag 決定 APP/DST/MAIN/BEV
   - 招待品項 → 詢問 Owner 確認

3. **暫時加入最後一行**（item_id 先設為 TMP），填寫所有欄位

4. **執行重新編號**（見操作 3）

5. **驗證並回報**

---

### 操作 2：修正品項分類 / 照片 URL

1. 讀取 Items 表，找到目標品項（用 C 欄 name 比對）
2. 直接用 Sheets API batchUpdate 修正對應欄位
3. 若分類（B 欄）或成本（E 欄）有變動 → 觸發重新編號

---

### 操作 3：重新編號（按 default_cost 排序）

**邏輯說明**：
- 相同 source_tag（APP/DST/MAIN/BEV）的品項，按 default_cost 升序排序後連號
- 格式：`{PREFIX}{3位數字}` 例如 APP001, APP002, DST001...
- 不同 source_tag 各自獨立編號（APP 從 001 開始，DST 從 001 開始）

**可直接使用腳本**：`scripts/fix_items_and_renumber.py`（如果存在）

**手動邏輯**（如腳本不存在時）：
```python
import re
from collections import defaultdict

# 按 source_tag 分群
groups = defaultdict(list)
for i, row in enumerate(rows):
    source_tag = row[9] if len(row) > 9 else ""  # J 欄
    default_cost = float(row[4]) if len(row) > 4 and row[4] else 0
    groups[source_tag].append((i, default_cost, row))

# 各群排序 + 連號
new_ids = {}
for tag, items in groups.items():
    items.sort(key=lambda x: x[1])  # 按 cost 升序
    for seq, (orig_idx, cost, row) in enumerate(items, start=1):
        new_id = f"{tag}{seq:03d}"
        new_ids[orig_idx] = new_id
```

⚠️ **重新編號後必須掃描其他 Sheet**：
- QUOTE_DRAFT、DropdownHelper 使用 **品項名稱（C欄）** 做 VLOOKUP/FILTER，**不受 item_id 重新編號影響**
- 若有其他 Sheet 寫死了舊 item_id 值，需手動更新

---

### 操作 4：從 Slide 提取照片 URL 配對到品項

使用腳本：`scripts/extract_slide_photos_to_items.py`

```bash
cd /path/to/maplab-ai-handbook
python3 scripts/extract_slide_photos_to_items.py
```

**腳本做什麼**：
1. 用 Google Drive API 讀取 Slide（16R9Ivi...）的 JSON 結構
2. 提取 Menu Showcase 頁面的品項名稱 + 圖片 URL
3. 用模糊比對（fuzz.ratio）將 Slide 品項名稱 → Items 表品項
4. Score ≥ 60 才寫入，避免誤配
5. 寫入 Items K 欄 image_url

**已知陷阱**：
- Slide API 需要 `drive` scope（不是 `presentations` scope）
- 模糊比對 threshold 建議 ≥ 60（過低會誤配）
- 提取前先備份 K 欄現有值

---

### 操作 5：驗證結果

```python
# 驗證重新編號後的完整性
resp = sheets_svc.spreadsheets().values().get(
    spreadsheetId=SHEET_ID, range="Items!A2:K"
).execute()
rows = resp.get("values", [])

# 檢查：item_id 格式是否正確
import re
pattern = re.compile(r'^(APP|DST|MAIN|BEV)\d{3}$')
bad = [row[0] for row in rows if row and not pattern.match(row[0])]
print(f"格式錯誤的 item_id: {bad}")

# 統計各前綴數量
from collections import Counter
counts = Counter(re.match(r'^([A-Z]+)', row[0]).group(1) for row in rows if row)
print(f"品項統計: {dict(counts)}")
```

---

## 腳本清單

| 腳本 | 用途 |
|------|------|
| `scripts/extract_slide_photos_to_items.py` | 從 Google Slide 提取品項照片 URL，比對後寫入 Items K 欄 |
| `scripts/fix_items_and_renumber.py` | 修正品項分類/照片 + 按 default_cost 重新編號（若存在） |

---

## Input / Output 格式（供 A6 LINE 助手呼叫）

### Input（A6 呼叫時傳入）

```json
{
  "action": "add_item" | "fix_item" | "renumber" | "sync_photos",
  "data": {
    "name": "品項名稱",
    "category": "甜點 | 餐食小點 | 飲品 | 主食 | 招待",
    "source_tag": "APP | DST | MAIN | BEV",
    "default_cost": 150,
    "default_price": 200,
    "note": "備註（可選）"
  }
}
```

### Output

```json
{
  "status": "success" | "error",
  "message": "操作摘要",
  "changes": [
    {"item_id": "APP042", "action": "added", "name": "品項名稱"},
    {"item_id": "APP001~APP050", "action": "renumbered", "count": 50}
  ],
  "warnings": ["需要注意的事項"]
}
```

---

## 注意事項與已知陷阱

1. **重新編號前必須備份**：先讀取現有 Items 完整資料存到變數，出錯才能還原
2. **DropdownHelper 不受影響**：使用 `FILTER(Items!C:C, Items!B:B="分類")` → 按名稱讀，不受 item_id 影響
3. **QUOTE_DRAFT 不受影響**：使用 `VLOOKUP(品名, Items!C:E, ...)` → 按名稱 VLOOKUP，不受 item_id 影響
4. **source_tag 空白問題**：部分品項的 J 欄可能為空，需先問 Owner 確認前綴
5. **Slide scope**：提取 Slide 照片用 `drive` scope，不是 `presentations` scope
6. **模糊比對最低分數**：threshold 設 60，避免 score=4 這種明顯誤配

---

## 執行歷史（供未來參考）

| 日期 | 操作 | 結果 |
|------|------|------|
| 2026-04-02 | 從 Slide 提取照片（T-A5-004 Phase 1） | 16 筆有效 URL 寫入 K 欄 |
| 2026-04-02 | Items 照片 URL 修正 | 5 筆移轉 + 7 筆清除 |
| 2026-04-02 | Items 重新編號 | 91 格，按 default_cost 排序，APP/DST/MAIN 各自連號 |
