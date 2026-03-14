# Pipeline Agent — 角色定位與技術文件

版本：v1.1 | 建立：2026-03-12 | 更新：2026-03-14

---

## 你是誰（接手前先讀這段）

- **角色：** A4 Pipeline Agent
- - **任務：** 相簿整理自動化（Google Photos → WebP → Drive → Notion）
  - - **GitHub：** https://github.com/page1010/maplab-pipeline
    - - **進度：** Notion「相簿整理專案 — maplab-pipeline」
      - - **不在範圍：** SEO、廣告、ERP — 那是 A2/A3/A5 的事
       
        - ---

        ## Phase 進度（截至 2026-03-13 Notion v2.2）

        | Phase | 說明 | 狀態 |
        |---|---|---|
        | Phase 0 | 環境設定、OAuth、GCP 設定 | ✅ 完成 |
        | Phase 1 | Google Photos 讀取 + EXIF + collector.py | 🔄 OAuth 重授權成功，待執行 collector test |
        | Phase 2 | Gemini Vision 分類 + Alt Text（vision.py）| 🔲 未開始 |
        | Phase 3 | Sheets × Calendar 日期比對（crossref.py）| 🔲 未開始 |
        | Phase 4 | WebP 轉換 + SEO 命名（transformer.py）| 🔲 未開始 |
        | Phase 5 | Google Drive 備份 + Notion 記錄（archiver.py）| 🔲 未開始 |

        **重要：禁止刪除 Google Photos 原始相片（只讀取）**

        ---

        ## 當前卡點與解法（Notion v2.2，2026-03-13）

        **問題 1 — collector.py 靜默回傳 0 photos**
        - 根因：`accounts` 預設包含 'spouse'，token_spouse.json 不存在時 exception 被靜默吞掉
        - - 解法：`collector.py` 改為 `accounts = ['owner']` 預設（已 commit）
          - - 需本機：`git pull` 才能更新
           
            - **問題 2 — Photos API 403 Forbidden**
            - - 根因：舊 token 無 photoslibrary.readonly scope
              - - 解法：✅ 已解決 — 刪除舊 token → 重新授權 → Token valid: True（2026-03-12）
               
                - **問題 3 — git pull 失敗（README.md conflict）**
                - - 根因：本機與 GitHub 版本都有修改（both added）
                  - - 解法：`git checkout --theirs README.md` → `git add README.md` → `git commit` → `git pull`
                   
                    - **下一步（需人工執行）：**
                    - ```bash
                      # 1. 確認最新版本
                      git pull --no-edit

                      # 2. 設定 credentials
                      python auth/setup_credentials.py

                      # 3. 重新授權（點選瀏覽器授權頁）
                      python -m src.auth.google_auth --account owner

                      # 4. 測試 Phase 1
                      python -m src.collector --test --account owner
                      ```

                      ---

                      ## OAuth / GCP 設定狀態

                      | 項目 | 狀態 |
                      |---|---|
                      | GCP 專案 | maplab-pipeline（建立完成）|
                      | 啟用的 API | Google Photos Library / Drive / Sheets / Calendar / Gmail ✅ |
                      | OAuth 用戶端 | maplab-pipeline-desktop（重新建立，credentials.json 已下載）|
                      | token_owner.json | ✅ 重新授權成功（2026-03-12）|
                      | Sheets API | 已在 GCP 啟用 |
                      | ASSET_LOG Notion DB | ✅ 建立完成（ID: 320ab0806d5c801b9063d444cd7fbd1c）|

                      ---

                      ## 最小阻力方案（卡住時優先試這個）

                      自動化卡住時：先手動標記 AI Keywords + Alt Text 填入 ASSET_LOG，驗證流程可行後再決定是否自動化。**禁止一開始就寫完整 parser，先產出再優化。**

                      ---

                      ## 版本紀錄

                      | 版本 | 日期 | 說明 | 更新者 |
                      |---|---|---|---|
                      | v1.0 | 2026-03-12 | 初始版本，Handbook Agent 整理 | Handbook Agent |
                      | v1.1 | 2026-03-14 | 更新至 Notion v2.2 狀態：OAuth 重授權成功記錄、Phase 進度表、卡點與解法 | A1 Handbook Agent |
