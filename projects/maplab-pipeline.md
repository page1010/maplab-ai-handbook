# Pipeline Agent — 角色定位與技術文件
  版本：v1.8 | 建立：2026-03-12 | 更新：2026-03-24

---

## SECTION 0 — 重要：執行環境說明

**本專案全部在雲端執行，不在本機跑任何東西。**

- 本機的 git clone 只用來讀程式碼，不執行任何 Phython
- 所有 Python 執行環境 = Google Colab（帳號：lb99104@gmail.com，authuser=1）
- 程式碼管理 = GitHub API（純雲端，不需要 push / pull / clone）
- 如果本機 git pull 出現 IndentationError，忽略它，GitHub 上的版本是乾淨的

---

## 你是誰（接手前先讀這段）

- 角色：A4 Pipeline Agent
- 任務：相簿整理自動化（Google Photos Takeout → Drive → Gemini 分類 → WebP → Notion）
- GitHub：https://github.com/page1010/maplab-pipeline
- 進度：project_state.md（maplab-pipeline repo）
- 不在範圍：SEO、廣告、ERP — 那是 A2/A3/A5 的事

---

## 技能清單（開工前翻一下）

完整技能庫：skills/superpowers-guide.md

| 情境 | 用哪個 Skill |
|------|----------|
| 需求模糊 | brainstorming |
| 要寫計畫 | writing-plans |
| 要寫程式 | test-driven-development |
| 遇到 Bug | systematic-debugging |
| 說完成前 | verification-before-completion |
| 任務收尾 | finishing-a-development-branch |
| Pipeline 相簿整理 | photo-pipeline-toolkit-guide + colab-resilience-guide + media-limit-workaround |

---

## Phase 進度（截至 2026-03-19）

| Phase | 說明 | 狀態 |
|-------|------|------|
| Phase 0 | 環境設定、GCP、OAuth | DONE |
| Phase 1 | collector_picker.py + collector_local.py | DONE (PR #3 #4) |
| Phase 1.5 | 兩個帳號 Takeout 確認在 Drive | DONE |
| Phase 2 | mina Takeout 解壓 122,200 files → MAPLAB/photos | DONE (Colab) |
| Phase 3 | collector_drive.py | DONE (PR #5) |
| Phase 3.5 | Drive API Overlap Check（OLD vs Takeout） | **DONE** (2026-03-19) |
| Phase 4 | vision.py — Gemini 分析 + EXIF（僅 2022 年起） | **NEXT** |
| Phase 5 | transformer.py + archiver.py | TODO |
| Phase 6 | Notion logging | TODO |
| Phase 7 | pipeline.py 串接 | TODO |

> ⚠️ 禁止刪除 Google Photos 原始相片（只讀取）

---

## Phase 3.5 結果：Drive API Overlap Check（2026-03-19）

### 執行方式
- 工具：`google.colab.auth` + Drive API v3（drive.mount 失敗，改用 API）
- 帳號：lb99104@gmail.com (authuser=1)
- Notebook：MAPLAB_takeout_unzip (Colab)

### OLD Google Photos 資料夾
- Folder ID: `1jRyrjW9JlhKPTWLRsoV_9plThOynBwD15r2TYhnkCPo`
- 子資料夾：2012, 2014, 2015, 2016, 2017, 2018, MAPLAB_ASSET_LOG
- **結果：所有子資料夾都是空的（0 files）**

### Takeout 資料夾
- Folder ID: `1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz`
- 26 個子資料夾（完整數據）
- 總檔案數：122,200 files

### Overlap 比對結論

| 年份 | OLD (files) | Takeout (files) | 狀態 |
|------|------------|----------------|------|
| 2012 | 0 | 無對應 | 可能在 pagewu1010 帳號 |
| 2014 | 0 | 3,862 | Takeout 有完整數據 |
| 2015 | 0 | 640 | Takeout 有完整數據 |
| 2016 | 0 | 6,043 | Takeout 有完整數據 |
| 2017 | 0 | 2,574 | Takeout 有完整數據 |
| 2018 | 0 | 6,618 | Takeout 有完整數據 |
| 2019–2026 | 無 | 有 | Takeout only |

**結論：Takeout 是唯一完整數據來源，OLD Google Photos 全空可忽略。**

---

## 相片分類規則（Phase 4 執行依據）

### 分類範圍
- **起始年份：2022 年**（之前的照片不需要分類）
- 目標資料夾：Takeout 中 2022年的相片 ~ 2026年的相片

### 三大分類

| 分類 | 說明 | 判斷依據 |
|------|------|----------|
| **外燴** | 外燴現場、擺盤、活動佈置、客人互動 | TimeTree 「飛寶一家」行事曆外燴事件 + Gemini Vision |
| **旅遊** | 旅行/出遊照片、飯店、風景 | TimeTree 行事曆旅遊事件（agoda 訂房等）+ Gemini Vision |
| **日常** | 不屬於外燴或旅遊的所有照片（分 home/shop 子類） | 預設分類 + GPS/地址判斷：home=安中路、shop=和緯路450號 |

### 日期驗證來源
- **TimeTree 行事曆：「飛寶一家」**
- URL: https://timetreeapp.com/calendars/m3h1hJs1Ki6N/
- 日期大概都是對的，可用於交叉比對照片日期與事件
- 外燴事件範例：「外燴 請上桌開幕」、3/12、「外燴 請上桌」
- 旅遊事件範例：agoda 訂房、住宿紀錄

### 分類流程（Phase 4 執行計畫）
1. 從 Takeout 讀取 2022–2026 的照片清單（Drive API）
2. 提取每張照片的拍攝日期（JSON metadata / EXIF）
3. 比對 TimeTree 行事曆事件，標記符合外燴/旅遊的日期範圍
4. 用 Gemini Vision 分析照片內容，確認/修正分類
5. 結果寫入 ASSET_LOG sheet + Drive 資料夾標記

---

## 資料來源

### mina (lb99104@gmail.com) — PRIMARY
- 122,200 files 在 MAPLAB/photos/Takeout/Google相簿/YYYY年的相片/
- Google相簿 folder ID: `1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz`
- OLD Google Photos folder ID: `1jRyrjW9JlhKPTWLRsoV_9plThOynBwD15r2TYhnkCPo`（全空，可忽略）
- 8 個 Takeout ZIP 已移到垃圾桶（等使用者清空）

### pagewu1010 (main account) — PENDING
- 5 個 ZIP (~187 GB) 仍在 Drive，等 mina pipeline 跑通後再處理
- Takeout folder ID: `13IoJpnuDCYQUIQImaUaTSZc6qKqGnLZC3NDQH8NpXgIPubMlK40LoZ_rsGGGPlnuabbpE4pO`

---

## Colab 操作說明

- Notebook: MAPLAB_takeout_unzip (ID: `16Ff4LF9zchNJQZ7nT28EWBDiEChoJfjo`)
- 帳號: lb99104@gmail.com (authuser=1)
- **drive.mount 已知失敗**：改用 `google.colab.auth` + Drive API v3（不需要 mount）
- 重連後: 先跑 auth cell，再繼續執行
- 永遠用 `%%bash`，不用 Python with indentation（防止 IndentationError）
- 用 JavaScript Monaco API `setValue()` 輸入程式碼（避免 Colab autocomplete 干擾）

---

## 已知阻塞

| 問題 | 狀態 | 解決方向 |
|------|------|----------|
| Vertex AI API 403/404 | ✅ 已解決 | 改用 Gemini API key (google.genai + gemini-2.5-flash) |
| drive.mount ValueError | 已繞過 | 改用 google.colab.auth + Drive API v3 |
| pagewu1010 187GB 待處理 | 待排程 | 等 mina pipeline 跑通後再處理 |

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-12 | 初始版本 | Handbook Agent |
| v1.1 | 2026-03-14 | 更新 OAuth 狀態 | A1 Handbook Agent |
| v1.2 | 2026-03-15 | 戰略重定義 | A5 |
| v1.3 | 2026-03-17 | 全雲端執行聲明 + Phase 2/3 完成 + 不走本機說明 | A4 |
| v1.4 | 2026-03-19 | Phase 3.5 Overlap Check 完成 + 相片分類規則（2022+，外燴/旅遊/日常）+ Colab 指令更新 | A4 |

| v1.5 | 2026-03-20 | Photo scan 60K done + Gemini API OK + Slides SECTION 11 整合 + Phase 4 v3.0 計畫 | A4 |
| v1.6 | 2026-03-20 | 使用者決策：日常分 home/shop + 旅遊用目的地命名 + A5 去重晚點 | A4 |
| v1.7 | 2026-03-23 | Phase 4 v4.0：S1-S4 完成 + S5 進行中 + 新增 S5.5 GPS 日常細分 + REST API 遷移 + 技術筆記 + ASSET_LOG 欄位說明 | A4 |

---

## Phase 4 v4.0 執行計畫（2026-03-23 更新）

整合來源：使用者（SEO + TimeTree 事件名分類）+ Slides Agent SECTION 11（MAPLAB_ASSETS 結構 + items/{item_id} + 4 新欄位）
v4.0 更新：補充實際執行進度 + 新增 S5.5 GPS 日常細分 + 錯誤紀錄 + Gemini REST API 遷移

### Photo Scan 結果

60,584 files（C=4,593 T=254 D=55,737），TimeTree lookup 361 dates（C=322 T=39）

### Gemini Prompt（定版 S3）

```
你是MAPLAB Kitchen的照片分類助手。請分析這張照片並回傳JSON格式：
{"category":"外燴|旅遊|日常","keywords":["3-5個中文關鍵詞"],
 "alt_text":"SEO中文描述30字內","seo_name":"english-lowercase-hyphenated"}
分類規則：外燴=餐點/擺盤/食材/外燴現場/廚房/單據；旅遊=風景/觀光/家庭出遊；日常=家庭/自拍/寵物/小孩/其他
seo_name格式：{category}-{description}-{detail}，例：catering-birthday-buffet-setup
僅回傳JSON，不要其他文字。
```

⚠️ 此 prompt 只做三大分類 + SEO 命名建議。日常 home/shop 細分由 S5.5 GPS 步驟處理（Gemini 無法判斷地點）。

### 第一波（不依賴 A5）— 執行進度

| Step | 名稱 | 狀態 | 完成日期 | 備註 |
|------|------|------|---------|------|
| S1 | enriched_lookup（TimeTree + photo scan 交叉比對） | ✅ DONE | 2026-03-20 | 361 dates enriched |
| S2 | 先鋒 10 張（驗證 prompt + API 流程） | ✅ DONE | 2026-03-23 | ASSET_LOG rows 2-11 |
| S3 | 定版 Gemini prompt | ✅ DONE | 2026-03-23 | 見上方 prompt |
| S4 | 建 MAPLAB_ASSETS 資料夾結構 | ✅ DONE | 2026-03-23 | 2022-2026 × catering/travel/daily |
| S5 | 2022 全年 batch（8,559 images） | 🔄 進行中 | — | REST API ~310/h，預估 ~28h |
| S5.5 | 日常 home/shop GPS 細分 | 🔲 待 S5 完成 | — | 新增步驟，見下方說明 |
| S6 | 2023 batch | 🔲 待開始 | — | 19,459 files |
| S6.5 | 2023 日常 GPS 細分 | 🔲 待 S6 完成 | — | 同 S5.5 邏輯 |

### S5.5 / S6.5 — 日常 home/shop GPS 細分（新增）

**背景**：Gemini Vision 無法從照片內容判斷拍攝地點（除非有店招/地標），因此日常照片的 home/shop 細分需要另外處理。

**方法**：從 Takeout JSON metadata 提取 GPS 座標，用距離計算分類

**執行步驟**：
1. 掃描 ASSET_LOG 中 category=日常 的所有 rows
2. 2. 用 file_id 找到對應 Takeout 資料夾中的 `.json` metadata 檔
   3. 3. 提取 `geoData.latitude` / `geoData.longitude`
      4. 4. 計算距離：
         5.    - home（台南市安中路2段336巷11號）：lat=23.0xxx, lng=120.2xxx（需確認精確座標）
               -    - shop（台南市北區和緯路2段450號）：lat=23.0xxx, lng=120.2xxx（需確認精確座標）
                    - 5. 分類規則：距離 home < 500m → `home`，距離 shop < 500m → `shop`，其他 → `other`
                      6. 6. 寫入 ASSET_LOG 新欄位 `daily_sub`（home / shop / other / no_gps）
                         7. 7. 無 GPS 資料的照片標記為 `no_gps`，後續可人工檢查
                           
                            8. **優點**：
                            9. - 不需要 Gemini API → 零成本、極快速（純座標計算，~5000 張/分鐘）
                               - - 準確度高（GPS 座標比視覺判斷更可靠）
                                 - - 可獨立於 S5 之後執行，不阻塞其他步驟
                                  
                                   - **注意**：需要使用者提供 home 和 shop 的精確 GPS 座標（或由 Google Maps 查詢）
                                  
                                   - ### 第二波（等 A5 ITEM_MASTER）
                                  
                                   - | Step | 名稱 | 狀態 | 備註 |
                                   - |------|------|------|------|
                                   - | S7 | 拿 A5 品項清單 | 🔲 等 A5 去重完成 | |
                                   - | S8 | matched_item_id 比對 | 🔲 | |
                                   - | S9 | items/primary + WebP 轉檔 + SEO 重命名 | 🔲 | 實際檔名變更在此步驟 |
                                   - | S10 | ASSET_MASTER 建立 + 通知 Slides | 🔲 | |
                                  
                                   - ### 第三波（全年份完成後）
                                  
                                   - | Step | 名稱 | 狀態 | 備註 |
                                   - |------|------|------|------|
                                   - | S11 | 2024 batch + GPS 細分 | 🔲 | 17,834 files |
                                   - | S12 | 2025 batch + GPS 細分 | 🔲 | 9,883 files |
                                   - | S13 | 2026 batch + GPS 細分 | 🔲 | 4,424 files |
                                   - | S14 | ASSET_LOG 欄位統一 + 清洗 | 🔲 | S2 pioneer vs S5 batch 格式不同 |
                                   - | S15 | 旅遊目的地命名（travel/{destination}） | 🔲 | 需 TimeTree 交叉比對 |
                                  
                                   - ### 跨 Agent 溝通
                                  
                                   - - 2026-03-20：收到 Slides Agent SECTION 11（commit f8c4bb2），已整合進 v3.0 計畫
                                     -   - 第二波依賴 A5 甜點去重完成 → ⚠️ 提醒使用者確認進度
                                         -   - 旅遊/日常照：Slides 不需要，但保持 SEO 命名供網站使用
                                          
                                             - ### 使用者決策
                                          
                                             - | 日期 | 問題 | 決策 |
                                             - |------|------|------|
                                             - | 2026-03-20 | A5 甜點去重 | 晚點處理（Wave 2 繼續等） |
                                             - | 2026-03-20 | 旅遊資料夾命名 | 用目的地（小琉球/東京/薄荷島） ✅ |
                                             - | 2026-03-20 | 日常照分類 | 分 home/shop：home=台南安中路、shop=台南和緯路450號 |
                                             - | 2026-03-23 | 日常 home/shop 如何實現 | GPS 座標判斷（非 Gemini Vision），新增 S5.5 步驟 |
                                          
                                             - ### MAPLAB_ASSETS 資料夾結構（S4 已建立 ✅）
                                          
                                             - ```
                                               MAPLAB_ASSETS/                          # root: 1yVggYKiTkBJe4kd8CPoM3U75kmOnVuNy
                                                 2022/                                 # 1wp6SXhVTHTEvj1_THT_IXZXpm6L48T4O
                                                   catering/
                                                   travel/
                                                   daily/
                                                 2023/                                 # 1i4d0BtnGidpNBEUgTGdgh_W_vH81o-iE
                                                   catering/ | travel/ | daily/
                                                 2024/                                 # 1ZrJdCp_oM6m-H6eB89mUSoAsOin2wbYX
                                                 2025/                                 # 1nIG-CTQNIrCiBWLzKUuakTLX-8SmHy-C
                                                 2026/                                 # 1pJVuRlpDULsxuXR7rN8KpgJ1kvO3lWYV
                                               ```

                                               最終歸檔結構（S9+ 建立）：
                                               ```
                                               MAPLAB_ASSETS/
                                                 catering/
                                                   hero/
                                                   team/
                                                   events/{type}/
                                                   items/{item_id}/
                                                 travel/{destination}/
                                                 daily/
                                                   home/
                                                   shop/
                                               ```

                                               ### 技術筆記（2026-03-23 實戰經驗）

                                               **Gemini API 選擇**：
                                               - ❌ `google.generativeai` library — 使用 localhost proxy，Colab 斷線後 proxy 死亡，無法恢復
                                               - - ✅ Gemini REST API（`requests.post`）— 直接呼叫，更快（~310/h vs ~160/h）、更穩定
                                                 - - Model：`gemini-2.5-flash`（2.0-flash 已 retired）
                                                   - - API URL：`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`
                                                    
                                                     - **Colab 防斷線**：
                                                     - - 每 50 張寫入 Sheet（`BATCH_SIZE = 50`）
                                                       - - 每 200 張寫入 Drive checkpoint（`CHECKPOINT_EVERY = 200`）
                                                         - - 重連後：Auth cell → S5-RESUME cell（自動從 Sheet 讀取已完成 filenames 跳過）
                                                           - - REST API timeout：120 秒 + MAX_RETRIES = 3
                                                            
                                                             - **已知 Warning**（不影響運行）：
                                                             - - `google_auth_httplib2:httplib2 transport does not support per-request timeout` — Sheets API 的 httplib2 限制，不影響功能
                                                              
                                                               - ### ASSET_LOG 欄位說明
                                                              
                                                               - | 欄 | Pioneer (S2) | Batch (S5+) | 說明 |
                                                               - |----|-------------|-------------|------|
                                                               - | A | file_id | year | ⚠️ 格式不同，S14 統一 |
                                                               - | B | original_name | filename | |
                                                               - | C | seo_name | file_id | |
                                                               - | D | category | category | ✅ 一致 |
                                                               - | E | keywords | keywords | ✅ 一致 |
                                                               - | F | alt_text | alt_text | ✅ 一致 |
                                                               - | G | drive_url | seo_name | |
                                                               - | H | source_folder | tokens | |
                                                               - | I | year | status | |
                                                               - | J | file_type | timestamp | |
                                                              
                                                               - S14 步驟將統一為：`year | filename | file_id | category | daily_sub | keywords | alt_text | seo_name | tokens | status | timestamp`
