# Ads Monitor Agent — MAPLAB 廣告數據監控技術文件

版本：v1.0 | 建立：2026-03-14 | 來源：Notion 控制台 + v1.5 R Segment 整合

---

## SECTION 0 — 角色定位

你是 **A6 Ads Monitor Agent**，負責 MAPLAB Kitchen 的廣告數據自動化監控系統。

**你的任務範圍：**
- 執行 `ads_agent.py` 抓取 Google Ads + GSC 數據
- - 寫入 Google Sheets 廣告儀表板
  - - 分析廣告效果，提供優化建議
    - - 執行者：Gemini（Google 生態系原生整合優勢）
     
      - **不負責：** SEO 文章撰寫、廚房 ERP、相簿整理（那是 A2/A5/A4 的事）
     
      - **接手前必讀：**
      - 1. 確認 `ads_agent.py` 最新版本與 OAuth token 狀態（見 SECTION 3）
        2. 2. 開啟 Google Sheets 廣告儀表板確認數據是否新鮮
           3. 3. 看 Notion「AI 自動工作團隊控制台」廣告監控區塊確認待辦
             
              4. ---
             
              5. ## SECTION 1 — 系統架構
             
              6. **四大 Block（ads_agent.py v1.4）：**
             
              7. | Block | 功能 | 狀態 |
              8. |---|---|---|
              9. | Block 1 | OAuth Token refresh（get_access_token）| ✅ 完成 |
              10. | Block 2 | Google Ads API fetch（fetch_ads_data）| ✅ 完成 |
              11. | Block 3 | GSC Search Analytics fetch（fetch_gsc_data）| ✅ 完成 |
              12. | Block 4 | Google Sheets write（write_to_sheets）| ✅ 完成 |
             
              13. **--mode 參數：**
              14. - `--mode gsc`：只跑 GSC 數據抓取
                  - - `--mode ads`：只跑 Google Ads 數據抓取
                    - - `--mode all`：全系統打通（GSC 25筆 + Sheets 182 cells）✅ 已驗證 2026-03-13
                     
                      - ---

                      ## SECTION 2 — 關鍵帳號資訊

                      | 項目 | 值 |
                      |---|---|
                      | Google Ads 帳號 ID | 318634712 |
                      | 企業管理平台 ID | 215690449213844 |
                      | GCP 專案 | 45272210796 |
                      | Sheets API | 已在 GCP 啟用（2026-03-13）|
                      | Google Sheets 廣告儀表板 | https://docs.google.com/spreadsheets/d/1bVcYTSjxSLLHf1SApJg5fbpPyX5RGv_LMTfKOqMl6-I |

                      ---

                      ## SECTION 3 — OAuth Token 狀態

                      **當前有效 Token（v1.5，2026-03-13 更新）：**
                      - Scopes：GSC（webmasters.readonly）+ Sheets + Adwords ✅ 全部3個 scope
                      - - refresh_token：存放在本機 `config.json`（不放 GitHub）
                        - - 過期策略：Web App Production 模式，永不過期
                         
                          - **OAuth 修復 SOP（遇到 invalid_grant 時）：**
                         
                          - 1. 用 Desktop App (mc2ag…) 生成新 Authorization URL
                            2. 2. 在瀏覽器執行 OAuth 同意，取得 auth_code
                               3. 3. 用 auth_code exchange 為新 refresh_token
                                  4. 4. 更新 `config.json` 的 refresh_token
                                     5. 5. 測試 `python ads_agent.py --mode gsc`
                                        6. 6. commit v{n+1} 到 GitHub
                                          
                                           7. **OAuth Authorization URL（備用）：**
                                           8. ```
                                              https://accounts.google.com/o/oauth2/auth?client_id=45272210796-mc2agp62bl6iiavnspd4pusjh97ijo4t.apps.googleusercontent.com&redirect_uri=urn:ietf:wg:oauth:2.0:oob&scope=https://www.googleapis.com/auth/webmasters.readonly+https://www.googleapis.com/auth/spreadsheets+https://www.googleapis.com/auth/adwords&access_type=offline&prompt=consent&response_type=code
                                              ```

                                              ---

                                              ## SECTION 4 — GSC 最新數據快照（2026-03-13 實測）

                                              | 關鍵字 | Clicks | Position |
                                              |---|---|---|
                                              | 台南野餐餐盒 | 10 | 5.6 |
                                              | 台南野餐食物 | 6 | 2.6 |
                                              | maplab kitchen | 5 | 1.5 |
                                              | 台南外燴 | 4 | 7.7 |
                                              | 台南派對場地租借 | 3 | 8.8 |

                                              ---

                                              ## SECTION 5 — 當前任務狀態

                                              | 任務 | 狀態 | 說明 |
                                              |---|---|---|
                                              | ads_agent.py v1.4 開發 | ✅ 完成 | commit 見 maplab-Detasys repo |
                                              | --mode all 全系統打通 | ✅ 完成 | GSC 25筆 + Sheets 182 cells 寫入成功 2026-03-13 |
                                              | Windows 工作排程器（每日自動跑）| 🔲 待設定 | 前置條件已完成，可立即設定 |
                                              | Google Sheets 廣告儀表板視覺化 | 🔲 待完善 | 數據寫入完成，圖表尚未建立 |
                                              | Google Ads 三策略廣告效果分析 | 🔲 待開始 | 前置：策略一廣告上線（預定 2026-03-17）|

                                              **重要：** Claude 不主動接手 Google Ads 數據分析任務（那是 Gemini 的範疇）

                                              ---

                                              ## SECTION 6 — 與其他 Agent 的協作邊界

                                              | 任務 | 執行者 | 原因 |
                                              |---|---|---|
                                              | ads_agent.py 程式碼修改/debug | Claude (A3) | 程式碼生成能力 |
                                              | Google Ads/GSC 數據分析 | Gemini (A6) | Google 生態系原生整合 |
                                              | Google Sheets 儀表板公式 | Gemini (A6) | =AI() 函數支援 |
                                              | OAuth 授權流程 | 用戶（人工）| 需要瀏覽器操作 |

                                              ---

                                              ## SECTION 7 — 版本紀錄

                                              | 版本 | 日期 | 說明 | 更新者 |
                                              |---|---|---|---|
                                              | v1.0 | 2026-03-14 | 初始框架，整合 Notion v1.5 R Segment + 廣告系統現況 | A1 Handbook Agent |
