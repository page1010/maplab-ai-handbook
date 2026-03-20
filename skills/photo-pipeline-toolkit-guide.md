# 相簿整理 Pipeline 工具箱
版本：v1.0 | 建立：2026-03-18 | 適用 Agent：A4 Pipeline Agent
用途：Google Photos Takeout 解壓 → 分類 → 重命名 → 去重 → WebP 轉換 → 上傳的完整工具鏈

---

## SECTION 0 — 本技能書的目標讀者

你正在處理 MAPLAB Kitchen 的相簿整理自動化 Pipeline：
- 資料來源：Google Photos Takeout（mina 帳號 122,200 files + pagewu1010 帳號 ~187GB）
- 執行環境：Google Colab（lb99104@gmail.com, authuser=1）
- 目標：原始相片 → Gemini AI 分類 → SEO 重命名 → WebP 壓縮 → Drive/Notion 歸檔

**核心痛點（來自 A4 實戰經驗 Phase 0–3）：**
- Takeout 的 JSON metadata 與圖片檔分離，需要合併
- JSON 檔名有時被截斷，無法直接對應原始圖片
- 大量重複照片（同張相片出現在多個相簿資料夾）
- EXIF 資料不完整或遺失（尤其 HEIC 格式）
- Colab session 斷線後需要安全恢復機制
- 122,200 files 的規模需要批次處理 + 進度追蹤

---

## SECTION 1 — Takeout 解壓與 Metadata 合併

### 1.1 Takeout JSON 結構理解

Google Photos Takeout 對每張圖片產生一個同名 JSON 檔：
```
IMG_20250101_120000.jpg
IMG_20250101_120000.jpg.json
```

JSON 包含：
- `photoTakenTime`（拍攝時間，Unix timestamp）
- `geoData`（經緯度）
- `title`（原始檔名）
- `description`（使用者描述）
- `imageViews`（瀏覽次數）

**常見問題：** JSON 檔名有時被截斷（超過 46 字元的檔名會被截短加上括號序號）。

### 1.2 Metadata 合併工具（Python / Colab）

```python
import json
import os
from pathlib import Path

def merge_metadata(photo_dir):
    """
    掃描資料夾，為每張圖片找到對應的 JSON metadata
    回傳 dict: {filename: metadata}
    """
    photos = {}
    json_files = {}
    
    for f in Path(photo_dir).rglob('*'):
        if f.suffix == '.json' and f.stem != 'metadata':
            json_files[f.stem] = f
        elif f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.heic', '.mp4', '.gif', '.webp'):
            photos[f.name] = f
    
    merged = {}
    matched = 0
    unmatched = []
    
    for photo_name, photo_path in photos.items():
        # 嘗試精確匹配
        json_key = photo_name
        if json_key in json_files:
            with open(json_files[json_key]) as jf:
                merged[photo_name] = json.load(jf)
            matched += 1
        else:
            # 嘗試截斷匹配（前 46 字元）
            truncated = photo_name[:46]
            found = False
            for jk in json_files:
                if jk.startswith(truncated):
                    with open(json_files[jk]) as jf:
                        merged[photo_name] = json.load(jf)
                    matched += 1
                    found = True
                    break
            if not found:
                unmatched.append(photo_name)
    
    print(f"匹配成功: {matched}/{len(photos)}")
    print(f"未匹配: {len(unmatched)} 筆")
    return merged, unmatched
```

### 1.3 開源工具推薦

| 工具 | 用途 | GitHub |
|------|------|--------|
| GoogleTakeoutFixer | 修復 Takeout metadata，合併 JSON → EXIF | github.com/tazmancoder/GoogleTakeoutFixer |
| MetaSort | 依 metadata 分類整理 Google Photos | Reddit r/googlephotos |
| google-takeout-image-parser | Python 工具，排序整理 Takeout 匯出 | github.com/paulmrsn/google-takeout-image-parser |
| Google Photos Metadata Fixer | GUI 工具，合併 JSON metadata 回圖片 | 多平台 |

---

## SECTION 2 — EXIF 讀取與修復

### 2.1 Python EXIF 工具鏈

```python
# 安裝（Colab）
# !pip install Pillow piexif exifread

from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import json

def read_exif(image_path):
    """讀取圖片 EXIF 資料"""
    img = Image.open(image_path)
    exif_data = img._getexif()
    if exif_data is None:
        return {}
    return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}

def write_exif_from_json(image_path, json_metadata, output_path):
    """
    從 Takeout JSON 回寫 EXIF 到圖片
    適用場景：Takeout 圖片遺失 EXIF 時，從 JSON 恢復
    """
    img = Image.open(image_path)
    
    try:
        exif_dict = piexif.load(img.info.get('exif', b''))
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
    
    # 寫入拍攝時間
    if 'photoTakenTime' in json_metadata:
        from datetime import datetime
        ts = int(json_metadata['photoTakenTime']['timestamp'])
        dt = datetime.fromtimestamp(ts)
        date_str = dt.strftime('%Y:%m:%d %H:%M:%S')
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str.encode()
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str.encode()
    
    # 寫入 GPS
    if 'geoData' in json_metadata:
        geo = json_metadata['geoData']
        if geo.get('latitude', 0) != 0:
            # GPS 座標轉換為 EXIF 格式
            lat = abs(geo['latitude'])
            lng = abs(geo['longitude'])
            exif_dict['GPS'] = {
                piexif.GPSIFD.GPSLatitudeRef: b'N' if geo['latitude'] >= 0 else b'S',
                piexif.GPSIFD.GPSLatitude: _decimal_to_dms(lat),
                piexif.GPSIFD.GPSLongitudeRef: b'E' if geo['longitude'] >= 0 else b'W',
                piexif.GPSIFD.GPSLongitude: _decimal_to_dms(lng),
            }
    
    exif_bytes = piexif.dump(exif_dict)
    img.save(output_path, exif=exif_bytes)

def _decimal_to_dms(decimal):
    """十進位度數轉為 EXIF DMS 格式"""
    d = int(decimal)
    m = int((decimal - d) * 60)
    s = int(((decimal - d) * 60 - m) * 60 * 100)
    return ((d, 1), (m, 1), (s, 100))
```

### 2.2 HEIC 格式處理

HEIC（Apple 裝置預設格式）在 Python 中需要額外支援：

```python
# Colab 安裝
# !pip install pillow-heif

from pillow_heif import register_heif_opener
register_heif_opener()

# 之後 Pillow 就能直接開啟 HEIC
img = Image.open('photo.heic')
```

---

## SECTION 3 — 重複照片偵測

### 3.1 Hash-Based 去重（精確匹配）

```python
import hashlib
from collections import defaultdict

def find_exact_duplicates(photo_dir):
    """
    使用 MD5 hash 找出完全相同的檔案
    適用：同一張照片出現在多個 Takeout 相簿資料夾
    """
    hash_map = defaultdict(list)
    
    for f in Path(photo_dir).rglob('*'):
        if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.heic', '.mp4'):
            file_hash = hashlib.md5(f.read_bytes()).hexdigest()
            hash_map[file_hash].append(str(f))
    
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    
    total_dup = sum(len(v) - 1 for v in duplicates.values())
    print(f"找到 {len(duplicates)} 組重複，共 {total_dup} 個可刪除")
    return duplicates
```

### 3.2 Perceptual Hash 去重（相似圖片）

```python
# !pip install imagehash

import imagehash

def find_similar_photos(photo_dir, threshold=5):
    """
    使用感知雜湊找出視覺相似的照片
    threshold: 容差值，越小越嚴格（0=完全相同）
    適用：同一場景不同角度、連拍、編輯版本
    """
    hashes = {}
    similar_groups = []
    
    for f in sorted(Path(photo_dir).rglob('*.jpg')):
        try:
            h = imagehash.phash(Image.open(f))
            matched = False
            for existing_hash, existing_path in hashes.items():
                if abs(h - existing_hash) <= threshold:
                    similar_groups.append((existing_path, str(f), abs(h - existing_hash)))
                    matched = True
                    break
            if not matched:
                hashes[h] = str(f)
        except Exception as e:
            print(f"跳過 {f.name}: {e}")
    
    print(f"找到 {len(similar_groups)} 組相似照片")
    return similar_groups
```

### 3.3 去重安全原則

1. **永遠不刪除原始檔** — 只標記、移動到 _duplicates 資料夾
2. **保留策略：優先保留有 EXIF 的版本**
3. **保留策略：同組重複中保留最大檔案（通常品質最好）**
4. **Log 記錄** — 每次去重操作記錄到 ASSET_LOG sheet

---

## SECTION 4 — AI 分類（Gemini Vision）

### 4.1 Gemini 分類 Prompt 設計

```python
CLASSIFICATION_PROMPT = """
你是 MAPLAB Kitchen 的相片分類助手。
請分析這張圖片並回傳 JSON 格式：

{
  "category": "food|store|event|landscape|screenshot|other",
  "keywords": ["關鍵字1", "關鍵字2"],
  "alt_text": "適合 SEO 的中文圖片描述",
  "is_food_photo": true/false,
  "food_items": ["可辨識的餐點名稱"],
  "event_type": "wedding|birthday|corporate|opening|null",
  "quality_score": 1-5
}

分類規則：
- food: 餐點特寫、擺盤、食材
- store: 店面、廚房、工作區
- event: 外燴現場、活動佈置、客人互動
- landscape: 場地環境、交通、風景
- screenshot: 螢幕截圖、對話紀錄
- other: 以上皆非
"""
```

### 4.2 批次分類（含速率限制）

```python
import time
import google.generativeai as genai

def batch_classify(photo_list, batch_size=10, delay=2):
    """
    批次呼叫 Gemini Vision API 分類照片
    
    Args:
        photo_list: 圖片路徑清單
        batch_size: 每批處理數量
        delay: 每批間隔秒數（API 速率限制）
    """
    results = []
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    for i in range(0, len(photo_list), batch_size):
        batch = photo_list[i:i+batch_size]
        
        for photo_path in batch:
            try:
                img = Image.open(photo_path)
                response = model.generate_content([CLASSIFICATION_PROMPT, img])
                result = json.loads(response.text)
                result['file_path'] = str(photo_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'file_path': str(photo_path),
                    'error': str(e),
                    'category': 'error'
                })
        
        # Checkpoint：每批存一次進度
        print(f"進度: {min(i+batch_size, len(photo_list))}/{len(photo_list)}")
        time.sleep(delay)
    
    return results
```

### 4.3 Token 用量追蹤

```python
def track_tokens(response, photo_name, log_sheet):
    """
    追蹤 Gemini API token 使用量
    寫入 ASSET_LOG 的 N 欄 (gemini_tokens_used)
    """
    tokens = response.usage_metadata.total_token_count
    # 寫入 Google Sheets...
    return tokens
```

---

## SECTION 5 — WebP 轉換與 SEO 重命名

### 5.1 WebP 批次轉換

```python
def convert_to_webp(input_path, output_dir, quality=80):
    """
    將 JPG/PNG/HEIC 轉為 WebP
    WebP 通常比 JPG 小 25-35%，網頁載入更快
    """
    img = Image.open(input_path)
    
    # 保持 EXIF
    exif = img.info.get('exif', b'')
    
    output_name = Path(input_path).stem + '.webp'
    output_path = Path(output_dir) / output_name
    
    img.save(output_path, 'WebP', quality=quality, exif=exif)
    
    original_size = os.path.getsize(input_path)
    new_size = os.path.getsize(output_path)
    savings = (1 - new_size / original_size) * 100
    
    return {
        'output': str(output_path),
        'original_size': original_size,
        'new_size': new_size,
        'savings_pct': round(savings, 1)
    }
```

### 5.2 SEO 重命名規則

```python
def generate_seo_filename(classification, original_name):
    """
    根據 AI 分類結果產生 SEO 友善檔名
    
    命名格式：{category}-{keywords}-{date}.webp
    範例：food-rose-macaron-wedding-catering-20250315.webp
    """
    import re
    from datetime import datetime
    
    cat = classification.get('category', 'other')
    keywords = classification.get('keywords', [])[:3]
    
    # 清洗關鍵字：移除特殊字元、轉小寫
    clean_kw = [re.sub(r'[^a-z0-9\u4e00-\u9fff]', '', k.lower()) for k in keywords]
    clean_kw = [k for k in clean_kw if k]
    
    # 嘗試從 EXIF 或 filename 提取日期
    date_match = re.search(r'(20\d{6})', original_name)
    date_str = date_match.group(1) if date_match else datetime.now().strftime('%Y%m%d')
    
    parts = [cat] + clean_kw + [date_str]
    seo_name = '-'.join(parts) + '.webp'
    
    return seo_name
```

---

## SECTION 6 — Colab 防斷線與進度恢復

### 6.1 Checkpoint 機制

```python
import pickle

CHECKPOINT_PATH = '/content/drive/MyDrive/MAPLAB/pipeline_checkpoint.pkl'

def save_checkpoint(state):
    """每批處理後存檔"""
    with open(CHECKPOINT_PATH, 'wb') as f:
        pickle.dump(state, f)
    print(f"Checkpoint saved: {state.get('processed', 0)} files done")

def load_checkpoint():
    """Colab 重連後恢復進度"""
    try:
        with open(CHECKPOINT_PATH, 'rb') as f:
            state = pickle.load(f)
        print(f"Checkpoint loaded: resuming from {state.get('processed', 0)}")
        return state
    except FileNotFoundError:
        return {'processed': 0, 'results': [], 'errors': []}
```

### 6.2 Colab 重連 SOP

1. 重新掛載 Drive: `from google.colab import drive; drive.mount('/content/drive')`
2. 載入 checkpoint: `state = load_checkpoint()`
3. 從上次中斷點繼續: `remaining = all_photos[state['processed']:]`
4. 繼續處理，每批存 checkpoint

### 6.3 大量檔案處理策略

122,200 files 不可能一次處理完。建議分批策略：

| 階段 | 處理範圍 | 目標 |
|------|---------|------|
| 先鋒批 | 前 100 張 | 驗證 pipeline 全流程 |
| 食物批 | 所有 food 類（估 ~30%）| 優先產出 SEO 素材 |
| 活動批 | event 類（估 ~20%）| 外燴作品集 |
| 掃尾批 | 剩餘 screenshot/other | 低優先，可延後 |

---

## SECTION 7 — Google Sheets 進度追蹤整合

### 7.1 ASSET_LOG 寫入

參照 skills/sheets-tracking-guide.md 的 ASSET_LOG schema，使用 Sheets API 記錄每張照片的處理狀態：

```python
from googleapiclient.discovery import build

def log_to_sheets(creds, spreadsheet_id, records):
    """
    批次寫入處理結果到 ASSET_LOG sheet
    使用 batch update 減少 API 呼叫次數
    """
    service = build('sheets', 'v4', credentials=creds)
    
    values = [[
        r.get('file_id', ''),
        r.get('original_name', ''),
        r.get('seo_name', ''),
        r.get('category', ''),
        ','.join(r.get('keywords', [])),
        r.get('alt_text', ''),
        r.get('drive_url', ''),
        r.get('source_folder', ''),
        r.get('year', ''),
        r.get('file_type', ''),
        str(r.get('is_screenshot', False)),
        r.get('status', 'done'),
        r.get('processed_at', ''),
        r.get('gemini_tokens', 0),
        r.get('error', '')
    ] for r in records]
    
    body = {'values': values}
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='ASSET_LOG!A:O',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
```

### 7.2 進度查詢

```python
def get_pipeline_progress(creds, spreadsheet_id):
    """查詢 pipeline 總體進度"""
    service = build('sheets', 'v4', credentials=creds)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='ASSET_LOG!L:L'
    ).execute()
    
    values = result.get('values', [])
    statuses = [v[0] for v in values[1:] if v]  # 跳過 header
    
    return {
        'total': len(statuses),
        'done': statuses.count('done'),
        'error': statuses.count('error'),
        'pending': statuses.count('pending'),
        'progress_pct': round(statuses.count('done') / max(len(statuses), 1) * 100, 1)
    }
```

---

## SECTION 8 — 安全規則（MAPLAB 特有）

1. **禁止刪除 Google Photos 原始相片** — 只讀取，不刪除
2. **Drive 操作只在 MAPLAB/ 資料夾內** — 不碰其他資料夾
3. **OAuth token 不上傳 GitHub** — .env 或 Colab Secrets 管理
4. **大量 API 呼叫前先小批測試** — 防止 quota 爆掉
5. **所有操作寫 log** — ASSET_LOG sheet 是唯一事實來源
6. **Colab 超時預警** — 25 秒安全邊界，超時存 checkpoint

---

## SECTION 9 — 工具版本與參考

| 工具 | 版本 / 來源 | 用途 |
|------|------------|------|
| Pillow (PIL) | pip install Pillow | 圖片讀寫、格式轉換、EXIF 讀取 |
| piexif | pip install piexif | EXIF 寫入與修改 |
| pillow-heif | pip install pillow-heif | HEIC 格式支援 |
| imagehash | pip install imagehash | 感知雜湊去重 |
| google-generativeai | pip install google-generativeai | Gemini Vision API |
| google-api-python-client | pip install google-api-python-client | Sheets API / Drive API |
| exiftool (CLI) | apt-get install libimage-exiftool-perl | 命令列 EXIF 工具（Colab 可用） |

**外部工具參考：**
- Google Photos Library API: https://developers.google.com/photos/library/guides/overview
- Gemini API: https://ai.google.dev/docs
- piexif 文件: https://piexif.readthedocs.io

---

*版本：v1.0 | 維護者：A1 Handbook Agent | 適用 Agent：A4 Pipeline*
