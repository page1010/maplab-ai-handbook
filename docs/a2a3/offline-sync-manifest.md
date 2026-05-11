# A2/A3 Selective Sync Manifest

這份清單是給 Google Drive for Desktop 的 selective sync 用的。

**原則**

- 只同步今天會用到的資料夾
- 不要把整個 Drive 都鏡像到本機
- 圖片 / 草稿 / 追蹤素材分開
- 高風險原檔只讀，不覆蓋

## 建議同步的工作區

### 1) A2/A3 主工作區

同步：

- `MAPLAB_DATA`
- `MAPLAB_DATA/MAPLAB_Items_Photos`
- `MAPLAB_DATA/MAPLAB_Proposals`
- `MAPLAB_DATA/MAPLAB_報價單`
- `MAPLAB_DATA/ai_reply_system`
- `MAPLAB_DATA/Colab Notebooks`
- `MAPLAB_DATA/line_oa_chat_csv`

### 2) 廣告與 SEO 工作檔

同步：

- `2026廣告meta 策略.gsheet`
- `MAPLAB Google Ads Dashboard.gsheet`
- `maplabkitchen.com-Performance-on-Search-2026-04-28.gsheet`
- `MAPLAB_外燴系統_v0.1.gsheet`
- `MAPLAB_ASSET_LOG - 副本.gsheet`

參考但不當作唯一真相：

- `網頁SEO時程.gsheet`

> 這份時程檔目前視為候選參考，不覆蓋你自己提供的版本。
> 之後若你指定了正式版本，我會把它升回主入口。

### 3) 今日素材區

同步：

- `2026maplab外燴紀錄`
- `食物介紹素材`
- `食物介紹素材/webp`
- `_MAPLAB_TEMP_IMAGES`

### 4) 需要離線可開的工作內容

同步：

- `MAPLAB_DATA/📋 進行中_Active Orders`
- `MAPLAB_DATA/✅ 已結案_Completed Orders`
- `MAPLAB_DATA/❌ 未成交_Lost Quotes`

## A4 / 照片工作線

若你要做 A4 素材整理，另外保留：

- `MAPLAB_ASSET_LOG`
- `MAPLAB_ASSETS`
- `Takeout`
- `2026maplab外燴紀錄`

## 不要同步

- 整個 Google Drive 根目錄
- 歷史冗餘的大型 meta 匯出資料夾，除非今天要用
- 不確定是否屬於本次任務的舊備份

## 驗收標準

- 本機 Finder 打開時，A2/A3 工作檔案能離線讀取
- WordPress 草稿與 SEO sheet 能立即開啟
- OpenClaw 任務不需要掃整個 Drive 才開始
