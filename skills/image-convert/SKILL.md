# image-convert — 圖片格式轉換技能書

## 觸發條件
- Owner 上傳 HEIC / HEIF 照片（iPhone 直拍格式）
- 任何格式轉換需求：webp → jpg、avif → jpg、png → jpg、heic → jpg
- 需要批次轉換並上傳 Drive Items_Photos

---

## 安裝依賴

```bash
pip install pillow-heif Pillow
```

> `pillow-heif` 讓 Pillow 支援 HEIC/HEIF 格式

---

## 單檔轉換 SOP

```python
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()  # 必須在 open 之前執行

img = Image.open("input.heic")
img = img.convert("RGB")  # HEIC 可能是 RGBA，需轉 RGB 才能存 jpg
img.save("output.jpg", "JPEG", quality=90)
```

---

## 批次轉換腳本（HEIC 資料夾 → JPG）

```python
from pathlib import Path
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

def convert_to_jpg(src_path: Path, dst_path: Path, quality=90):
    img = Image.open(src_path).convert("RGB")
    img.save(dst_path, "JPEG", quality=quality)
    print(f"  ✅ {src_path.name} → {dst_path.name}")

# 使用範例
src_dir = Path("heic_input/")
dst_dir = Path("jpg_output/")
dst_dir.mkdir(exist_ok=True)

for f in src_dir.glob("*.heic"):
    dst = dst_dir / f.with_suffix(".jpg").name
    convert_to_jpg(f, dst)
```

---

## 命名規範

輸出檔名格式：`{item_id}_{中文品名}.jpg`

範例：
```
APP002_義大利嫩煎香料豚肉球.jpg
DST026_綜合堅果小塔_三吋.jpg
```

**Owner 提供圖片時詢問對應 item_id**，才能正確命名。

---

## 上傳到 Drive Items_Photos

```python
import requests, json

with open('/Users/pagemacmini/.claude/mcp-keys/google-token.json') as f:
    creds = json.load(f)
token = creds['token']
FOLDER_ID = '1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT'  # MAPLAB_Items_Photos

def upload_jpg(file_path: str, file_name: str) -> str:
    """上傳 jpg 到 Drive，回傳 file_id"""
    with open(file_path, 'rb') as f:
        data = f.read()

    metadata = json.dumps({'name': file_name, 'parents': [FOLDER_ID]})
    resp = requests.post(
        'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart',
        headers={'Authorization': f'Bearer {token}'},
        files={
            'metadata': ('metadata', metadata, 'application/json'),
            'file': (file_name, data, 'image/jpeg')
        }
    )
    file_id = resp.json()['id']
    return file_id

# 上傳後更新 K 欄
def update_sheet_k(row: int, file_id: str):
    url = f"https://drive.google.com/uc?id={file_id}&export=view"
    SHEET_ID = '1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg'
    requests.put(
        f'https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Items!K{row}',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'range': f'Items!K{row}', 'majorDimension': 'ROWS', 'values': [[url]]},
        params={'valueInputOption': 'RAW'}
    )
```

---

## 支援格式對照

| 輸入格式 | 說明 | Pillow 處理 |
|----------|------|------------|
| HEIC / HEIF | iPhone 直拍，需 `pillow-heif` | `pillow_heif.register_heif_opener()` |
| WEBP | Google 格式，Pillow 原生支援 | 直接 `Image.open()` |
| AVIF | 新格式，需 `pillow-avif-plugin` | `pip install pillow-avif-plugin` |
| PNG | 透明底需轉 RGB | `.convert("RGB")` 再存 jpg |

---

## 完整流程（Owner 提供 HEIC → Drive → Sheet）

1. Owner 上傳 HEIC 到指定位置（或 `/tmp/heic_input/`）
2. 確認 item_id 對應
3. 執行轉換腳本 → 生成 `{item_id}_{品名}.jpg`
4. Refresh token（如過期）：
   ```python
   # 見 skills/credentials/ 下的 Google OAuth 說明
   ```
5. 上傳到 Drive FOLDER_ID
6. 更新 Items Sheet K 欄
7. `bash scripts/checkpoint.sh "A0" "HEIC轉換上傳 N筆"`

---

## Token 過期處理

```python
import requests, json

def refresh_token():
    with open('/Users/pagemacmini/.claude/mcp-keys/google-token.json') as f:
        creds = json.load(f)
    resp = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'refresh_token': creds['refresh_token'],
        'grant_type': 'refresh_token'
    })
    creds['token'] = resp.json()['access_token']
    with open('/Users/pagemacmini/.claude/mcp-keys/google-token.json', 'w') as f:
        json.dump(creds, f, indent=2)
    return creds['token']
```
