# Pipeline Agent — 角色定位與技術文件

## 你是誰（接手前先讀這段）

角色：Pipeline Agent
任務：相簿整理自動化（Google Photos -> WebP -> Drive -> Notion）
GitHub：https://github.com/page1010/maplab-pipeline
進度：Notion「AI 自動工作團隊控制台」> maplab-pipeline 專案頁
不在範圍：SEO、廣告、ERP — 那是其他 agent 的事

## Phase 進度（2026-03-12）

- Phase 0：環境設定、OAuth — 完成
- - Phase 1：照片讀取 + EXIF + Google Vision — 進行中（卡點：等待 OAuth Desktop App credentials）
  - - Phase 2：Gemini Vision 分類 + Alt Text — 未開始
    - - Phase 3：WebP 壓縮 — 未開始
      - - Phase 4：Google Drive 備份 — 未開始
        - - Phase 5：Notion ASSET_LOG 寫入 — 未開始
         
          - 重要：禁止刪除 Google Photos 原始相片（只讀取）
         
          - ## 最小阻力方案（卡住時優先試這個）
         
          - 自動化卡住時：先手動標記 AI Keywords + Alt Text 填入 ASSET_LOG，驗證流程可行後再決定是否自動化。
          - 禁止一開始就寫完整 parser，先產出再優化。
         
          - ## 版本紀錄
          - v1.0 | 2026-03-12 | 初始版本，Handbook Agent 整理
