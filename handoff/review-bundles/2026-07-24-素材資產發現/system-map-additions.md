# system_map 增補草稿 — 素材資產 / 存檔架構 / 本輪發現（2026-07-24）

> **狀態：DRAFT — 待 Owner review。未 push main。**
> 用途：把 2026-07-24 素材歸檔任務「走過的痕跡」留檔。
> **插入建議**：本 repo 無 `system_map.md`、無 `gen_system_truth.py`（＝無自動覆寫風險）。
> 建議把本段以「## 素材資產 / 本輪發現（2026-07-24）」新標題插入人工維護的
> `SYSTEM_DIRECTORY_INDEX.md`（全局目錄索引大全）末段，或 `CURRENT_STATUS.md`。
> 未直接寫入正式檔，等 Owner 定奪插入點。

## 1. 素材真相（單一來源）

- **A4 素材索引 = `MAPLAB_ASSET_LOG`**（Google Sheet，**mina / lb99104@gmail.com 擁有**，
  2026-03-19 共享給 Owner）。ID `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`。
  欄位：file_id / original_name / seo_name / category / keywords / alt_text / drive_url / year。
- **`photo_alt_index.csv`**（29,258 列，mina 擁有）
  路徑：`GoogleDrive-lb99104…(2026-6-13)/我的雲端硬碟/MAPLAB/MAPLAB_ASSETS/_alt_index/photo_alt_index.csv`
  欄位：相對路徑 / ALT文字 / 場景 / 標籤 / 可上網 / 處理時間。
- **⚠️ 關鍵陷阱**：ASSET_LOG 的 `category` 欄只有粗分「外燴 / 日常 / 旅遊」，
  會把婚禮/HR **壓平成外燴**。A4 真正的細分類在 **CSV 的路徑子類別**：
  `年份/catering/{子類別}/`。子類別分佈：
  - `catering/wedding` **333 張** → TA-2 婚禮
  - `catering/corporate` **472 張** → TA-3 HR
  - `catering/birthday` 3,347 → TA-1 週歲/生日
  - `catering/dessert` 4,283 → 甜點桌（跨 TA）
  - `catering/other` 9,013
  **分類真相以路徑子類別為準，別信 category 欄。**
- 實體檔在 Owner 自己建的 Drive 夾：`年份/catering/{wedding,corporate,dessert,birthday,other}/`
  （5 個年度 catering 夾；wedding 夾樣本 id `1X2QOeEf3L0P09ecq0ly4PmYV3G10u4-0`）。

## 2. 關鍵字主軸（TA = 視圖）

- **`docs/seo-keyword-map.md`**（A2 canonical 單一真相，2026-07-07 更新）＝素材分類**主軸**。
  三個 TA 只是「關鍵字→TA」的視圖，非主分類。對應 pillar：
  婚禮 `tainan-outdoor-wedding-catering`(1215)；週歲 `catering-one-year-old-party-tainan`(498)；
  企業茶會 `corporate-tea-party-desserts`(924)。
- **`docs/real-cases-to-seo-matrix.md`**＝2026 活動事件夾 → cluster → 關鍵字 完整對照
  （東門教會證婚→wedding、富信/工研院→meeting_refreshment…）。

## 3. 成果位置

- **已分類素材（190 張）**：`/Volumes/MacExternal/MAPLAB_素材_依TA_20260724/`
  - `TA1_週歲/`（抓周甜點桌 17 + 托嬰畢業 22 = 39）
  - `TA2_婚禮/`（證婚 27 + 婚禮風候選未確認 7 + 缺口 txt）
  - `TA3_HR/`（研發日26/論壇26/會議23/說明會23/開幕茶會19 = 117）
- **可用清單（含 drive_url）**：`/Volumes/MacExternal/MAPLAB_WORKSPACE/index/`
  - `A4_婚禮照_可用清單_含連結.csv`（231/333 有連結）
  - `A4_企業照_可用清單_含連結.csv`（183/472 有連結，資料夾 400 上限截斷，補分頁可再高）
  - `A4_婚禮照清單_wedding333.csv`、`A4_企業照清單_corporate472.csv`（A4 原描述）
  - `素材索引_關鍵字主軸_schema草稿_2026-07-24.md`

## 4. 新存檔架構（治理）

- **agent 固定存檔根**：`/Volumes/MacExternal/MAPLAB_WORKSPACE/{outputs,state,tools,index}`
  - `outputs/<YYYY-MM-DD>_<任務短名>/`、`state/`、`tools/`、`index/`（素材真相索引）
- 治理草稿：`skills/agent-output-convention.md`（DRAFT）
  + review bundle `handoff/review-bundles/2026-07-24-agent-output-convention/`。

## 5. 已知卡點 / 陷阱（走過的坑）

1. **實體素材未同步本機** → 只有 `_alt_index` CSV 有同步，實體照片夾沒同步。
2. **Drive API 下載會 base64 爆 context** → `download_file_content` 回 base64 進 context，
   單張全解析度 ≈ 數十萬 token；**大量下載不能在主 context 做**。落地策略：
   優先「設資料夾離線 / 鏡像後 cp」，次選 subagent 批次消化，別在主 context 硬下。
3. **Google Drive 桌面版只能整碟鏡像、不能挑單夾**（鏡像模式）→ 要嘛整碟、要嘛用 offline。
4. **實體檔名 seo/原始混用** → CSV 用 seo 名、實體夾部分還是 IMG_/UUID 名，
   join 命中率被壓（婚 231/333、企 183/472）；A4 完成 seo-rename 回寫可拉高。
5. **資料夾列檔 400 筆分頁上限** → 大夾要 nextPageToken 補齊。
6. **婚禮無拍攝日期** → A4 CSV 只有年份+處理時間，`MAPLAB_ASSET_LOG` 只有 year；
   **date-join 走不通**，改靠「路徑子類別」桶分類。
7. **Chrome 開 Drive 資料夾縮圖會 render 凍結**（截圖逾時）→ 視覺驗證改「落地後本機 sips+montage」。

## 6. 其他本輪跑過的事實（痕跡）

- **Ollama 排程**：`com.maplab.a6-gym`（LaunchAgent）每天 **15:00** 跑 `a6_gym_runner.py`
  用 Ollama `qwen2.5:14b`（~9GB）。`ollama-keep-alive` 只設環境變數非排程。**工作時段勿 stop**。
- **TimeTree**：Chrome 已預設登入（行事曆「飛寶一家」），但婚禮場次用**客戶/場地名**命名
  （如東門教會），關鍵字搜「婚禮」無果；婚禮日期更可靠來源＝**mina 訂單 Sheet 標題**
  （2026/6/27、2026/3/6、2025/11/23、2025/9/27、2024/11/2…）。
- **mina 舊照片共享**：`外燴照片（擺設）`140（人工命名事件庫，含 `戶外婚禮證婚場地.jpg` +
  ~20 HR 具名照）、`餐點照片`103（純食物照，0 婚禮）。
- **外接硬碟**：`/Volumes/MacExternal`（1.8T，可寫）；另有 Steam、Macintosh HD。
- **廣告線**：meta-ads MCP 已接、token 為無期限系統使用者；Meta 帳號 `act_318634712`。
- **素材分類方法定論**：以「事件脈絡 / A4 路徑桶」為主、單張影像辨識為輔（甜點桌跨 TA 撞臉，
  單圖不可靠）；分類主軸跟 `seo-keyword-map` 關鍵字，TA 為視圖，一份素材跨 audience/channel 共用。
