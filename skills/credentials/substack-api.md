# Substack 發文技能書
版本：v1.0 | 建立：2026-04-24 | B1 InnerFlowLab

## 帳號資訊
- Profile: https://substack.com/@pagewu
- - Publication: InnerFlowLab
  - - Subdomain: pagewu（不是 innerflowlab）
   
    - ## 三層備援
   
    - 層1 Chrome tab：進 substack.com/@pagewu → Create → New Post → 貼標題正文 → Publish or Save draft
   
    - 層2 curl + cookie：
    - POST https://substack.com/api/v1/drafts
    - Header: Cookie: connect.sid=YOUR_COOKIE
    - Body: type=newsletter, draft_title, draft_body(HTML), audience=everyone
    - Cookie 取法：DevTools > Application > Cookies > substack.com > connect.sid
    - 注意：非官方API，cookie每次登入更新
   
    - 層3 MCP：Substack 無官方 MCP，不可用。
   
    - ## B1 發文 SOP
    - 1. Owner 給中文稿/筆記
      2. 2. B1 輸出英文稿存 sessions/B1/
         3. 3. Owner 確認
            4. 4. B1 Chrome tab 貼入發布
               5. 5. Commit: publish(b1): [title]
                 
                  6. ## Codex 接替 SOP
                  7. 1. 讀 sessions/B1/ 最新 log
                     2. 2. 取 EN Article Draft 內容
                        3. 3. Owner 提供 connect.sid
                           4. 4. curl POST 建 draft
                              5. 5. Owner 手動 Publish
                                 6. 6. Commit: publish(codex-failover): [title]
                                   
                                    7. ## 圖片規格
                                    8. 尺寸：1600x900px | 工具：Canva免費版
                                    9. Building線：深色+白字+技術感
                                    10. Reflecting線：暖色+旅遊照片
                                    11. 命名：IFL-P01-cover.png
                                   
                                    12. ## 文章記錄
                                    13. P01-CN 偷懶是靈感來源 Building 2026-04-23 已發布
                                    14. P02-CN Claude應該要給我分潤 Reflecting 2026-04-23 已發布
                                    15. P01-EN draft ready Building — 待發布
