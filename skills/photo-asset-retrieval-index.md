# skills/photo-asset-retrieval-index.md — 相片索引「指向路徑」自取技能

> 狀態：DRAFT（2026-08-02）。給任何專案/agent **自取**：相片在哪、怎麼撈、方向正不正、能不能用。
> 搭配讀：`skills/photo-asset-retrieval-guide.md`（撈取流程）、`skills/case-study-production-sop.md` §4（命名/alt）、`docs/seo-keyword-map.md`。

## 1. 索引在哪（真相檔）

- **`MAPLAB_WORKSPACE/index/photo_alt_index.csv`**（UTF-8-SIG，可直接 Excel/Sheet 開）。
- 一列＝一張相片。目前涵蓋 **2026 母夾 21 個具名個案夾、348 張**。
- 母夾（原始檔）：Google Drive `2026maplab外燴紀錄`（本機串流掛載）＝`~/Library/CloudStorage/GoogleDrive-<owner>/我的雲端硬碟/2026maplab外燴紀錄/`。

## 2. 欄位怎麼看

| 欄位 | 意義 |
|---|---|
| `file_path` | 相片本機絕對路徑 |
| `case_folder` | 屬哪個案（＝Drive 子夾原名） |
| `scene` | 場景代碼：opening-tea / first-birthday / preschool-grad / wedding / corporate-meeting / forum / seminar / party / vip / corporate-event / event |
| `orientation_disp` | 顯示方向 L橫/P直/no-tag/?（EXIF 由 macOS mdls 讀出） |
| `needs_rotate` | **正不正**：`NO`=正、`YES`=側躺需轉、`NO(no-tag)`=無EXIF旗標(預設正)、`?`=雲端未索引(見§4) |
| `proposed_filename` | `maplab-tainan-{scene}-NN.webp` |
| `proposed_alt` | `台南{場景}外燴—{描述}`（描述為場景模板，挑進個案時細化） |
| `needs_face_crop` | 人臉合規：見 §3 |
| `needs_logo_crop` | 他牌 logo：CHECK=先確認可否公開；NO=無 |
| `ad_ok` | 是否可進廣告素材（預設 NO 待審） |
| `pointer_指向` | `case_folder | 場景`（撈圖錨點） |

## 3. 合規：人臉處理（Owner 定案 2026-08-02）

- **`CHILD-blur或貼兔子貼圖(不排除)`**：偵測到**幼童臉** → **預設 blur（霧化）或蓋可愛貼圖（如邦尼兔主題貼兔子）遮臉**，**不整張排除**——讓更多相片可用。只有整張無法處理才棄用。
- `ADULT-查`：成人臉 → 選圖優先無正臉；必要時 blur。
- `NO`：以食物/佈置為主、無臉，直接可用。
- `needs_logo_crop=CHECK`：他牌招牌/logo → 裁切或確認可公開（客戶本身品牌 OK）。

## 4. 方向的權威來源 & 待辦

- `NO`/`YES`/`no-tag` 由 **mdls 讀 EXIF Orientation**（macOS Spotlight 解析，已與 PIL JPG EXIF 交叉驗證＝權威）。
- `?`＝Google Drive 串流檔尚未 materialize / Spotlight 未索引 → 兩種補法：
  1. Drive 那幾夾設「可離線」或 `cat 檔 >/dev/null` 觸發下載後重掃。
  2. 上稿時本就會過 `tools/ai_workbook/a8_auto_orient.py`（依 EXIF 自動轉正，非盲轉）→ **側躺會在轉 webp 時自動修正**，故 `?` 不阻塞使用。
- 權威覆核（可選）：`brew install exiftool` → `exiftool -Orientation -n` 直讀 HEIC，回填 `?`/覆核全部。

## 5. 怎麼撈（自取範例）

```bash
CSV=~/investment-os/MAPLAB_WORKSPACE/index/photo_alt_index.csv
# 撈某案所有圖：
awk -F, '$2 ~ /邦尼兔/' "$CSV"
# 撈某場景（如開幕）可用、無臉、方向正：
awk -F, '$3=="opening-tea" && $9=="NO" && $6=="NO"' "$CSV"
# 撈某場景（含幼童臉但可 blur 保留）：
awk -F, '$3=="first-birthday"' "$CSV"   # child 走 blur/貼圖，不排除
```

## 6. 新相片進來怎麼自動歸位

落進 `{日期}{客戶}-{活動}` Drive 子夾 → 跑索引器（本 skill 附的掃描邏輯：mdls 方向 + 場景對映 + 命名/alt + 合規旗標）→ 追加進 `photo_alt_index.csv`。命名/alt 規則見 `case-study-production-sop.md` §4。
> 未命名的純日期夾（`2026-05-30` 等原始傾印）先整理成具名個案夾才索引。
