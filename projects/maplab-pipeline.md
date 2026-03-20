# Pipeline Agent — 角色定位與技術文件
版本：v1.5 | 建立：2026-03-12 | 更新：2026-03-20

---

## SECTION 0 — 重要：執行環境說明

**本專案全部在雲端執行，不在本機跑任何東西。**

- 本機的 git clone 只用來讀程式碼，不執行任何 Python
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
| **日常** | 不屬於外燴或旅遊的所有照片 | 預設分類，排除以上兩類後的剩餘 |

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

---

## Phase 4 v3.0 執行計畫（2026-03-20）

整合來源：使用者（SEO + TimeTree 事件名分類）+ Slides Agent SECTION 11（MAPLAB_ASSETS 結構 + items/{item_id} + 4 新欄位）

### Photo Scan 結果

60,584 files（C=4,593 T=254 D=55,737），TimeTree lookup 361 dates（C=322 T=39）

### Gemini Prompt 擴充

原有：category / keywords / alt_text / is_food_photo / food_items / event_type / quality_score
新增：matched_item_id / photo_orientation / is_catering_usable / suggested_slide_usage

### 第一波（不依賴 A5）

S1 enriched_lookup → S2 先鋒10張 → S3 定版prompt → S4 建MAPLAB_ASSETS資料夾 → S5 2022外燴batch → S6 2023外燴+旅遊batch

### 第二波（等 A5 ITEM_MASTER）

S7 拿品項清單 → S8 matched_item_id比對 → S9 items/primary+WebP → S10 ASSET_MASTER+通知Slides

### 跨 Agent 溝通

- 2026-03-20：收到 Slides Agent SECTION 11（commit f8c4bb2），已整合進 v3.0 計畫
- - 第二波依賴 A5 甜點去重完成 → ⚠️ 提醒使用者確認進度
  - - 旅遊/日常照：Slides 不需要，但保持 SEO 命名供網站使用
