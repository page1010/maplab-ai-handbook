# Pipeline Agent — 角色定位與技術文件
版本：v1.3 | 建立：2026-03-12 | 更新：2026-03-17

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
|------|-------------|
| 需求模糊 | brainstorming |
| 要寫計畫 | writing-plans |
| 要寫程式 | test-driven-development |
| 遇到 Bug | systematic-debugging |
| 說完成前 | verification-before-completion |
| 任務收尾 | finishing-a-development-branch |

---

## Phase 進度（截至 2026-03-17）

| Phase | 說明 | 狀態 |
|-------|------|------|
| Phase 0 | 環境設定、GCP、OAuth | DONE |
| Phase 1 | collector_picker.py + collector_local.py | DONE (PR #3 #4) |
| Phase 1.5 | 兩個帳號 Takeout 確認在 Drive | DONE |
| Phase 2 | mina Takeout 解壓 122,200 files → MAPLAB/photos | DONE (Colab) |
| Phase 3 | collector_drive.py | DONE (PR #5) |
| Phase 4 | vision.py — Gemini 分析 + EXIF | NEXT |
| Phase 5 | transformer.py + archiver.py | TODO |
| Phase 6 | Notion logging | TODO |
| Phase 7 | pipeline.py 串接 | TODO |

禁止刪除 Google Photos 原始相片（只讀取）

---

## 資料來源

### mina (lb99104@gmail.com) — PRIMARY
- 122,200 files 在 MAPLAB/photos/Takeout/Google相簿/YYYY年的相片/
- Google相簿 folder ID: 1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz
- 8 個 Takeout ZIP 已移到垃圾桶（等使用者清空）

### pagewu1010 (main account) — PENDING
- 5 個 ZIP (~187 GB) 仍在 Drive，等 mina pipeline 跑通後再處理
- Takeout folder ID: 13IoJpnuDCYQUIQImaUaTSZc6qKqGnLZC3NDQH8NpXgIPubMlK40LoZ_rsGGGPlnuabbpE4pO

---

## Colab 操作說明

- Notebook: MAPLAB_takeout_unzip (ID: 16Ff4LF9zchNJQZ7nT28EWBDiEChoJfjo)
- 帳號: lb99104@gmail.com (authuser=1)
- 重連後: 先跑 Cell 1 (drive.mount)，ValueError: mount failed = 正常，繼續跑
- 永遠用 %%bash，不用 Python with indentation（防止 IndentationError）

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-12 | 初始版本 | Handbook Agent |
| v1.1 | 2026-03-14 | 更新 OAuth 狀態 | A1 Handbook Agent |
| v1.2 | 2026-03-15 | 戰略重定義 | A5 |
| v1.3 | 2026-03-17 | 全雲端執行聲明 + Phase 2/3 完成 + 不走本機說明 | A4 |