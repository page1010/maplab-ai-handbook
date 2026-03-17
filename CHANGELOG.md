# CHANGELOG.md — MAPLAB AI System 版本演進紀錄

本文件記錄 maplab-ai-handbook 的所有重大版本變更。
格式：版本號 | 日期 | 變更摘要 | 執行 Agent

---

## v2.8 — 2026-03-17（最新）

**troubleshooting-hub v1.0 + AGENT_STARTUP_PROTOCOL v1.1 + superpowers-guide v1.3**

執行 Agent：A1 Handbook Agent（Claude Opus 4.6）

更新：
- skills/troubleshooting-hub.md v1.0 — 新建：Agent 卡住急救手冊，13 個常見症狀診斷表 + 回報流程 + 使用規則
- - AGENT_STARTUP_PROTOCOL.md v1.1 — 新增「執行中卡住怎麼辦」區段，引導 Agent 查 troubleshooting-hub
  - - skills/superpowers-guide.md v1.3 — MAPLAB 自建技能包表格新增 troubleshooting-hub 行 + 詳細區段
   
    - 設計原則：
    - - troubleshooting-hub 只做路由（症狀 → 技能書），不重複寫解法
      - - 找不到解法 → 回報 A1 → A1 補充到 hub → 全員受益
        - - 解決核心問題：Agent 卡住時浪費 context 亂試，改為查表找解法
         
          - ---
## v2.7 — 2026-03-17

**seo-ads-agent.md v2.1 + gtm-conversion-setup.md v1.0**

執行 Agent：A3 Ads Monitor Agent（Claude Sonnet 4.6）

**更新：**
- `projects/seo-ads-agent.md` v2.1 — 素材要求區段新增 PMax 問句型標題建議（2 個，小幅測試用，追蹤 CTR 變化）
- - `projects/gtm-conversion-setup.md` v1.0 — 新建 GTM 轉換事件設定 SOP（LINE 點擊 / 表單送出 / 電話點擊）
  - - 版本紀錄表格修正（v1.1/v1.2 遺失修復 + v2.1 新增）
    - - 相關連結新增 GTM SOP 路徑
     
      - **調整 1 — PMax 問句型標題（小幅測試）：**
      - - 新增標題 1：辦週歲派對，餐點怎麼準備才不手忙腳亂？
        - - 新增標題 2：台南外燴推薦｜質感派對餐桌，不用自己張羅
          - - 追蹤方式：14 天後比較問句型 vs 原有標題 CTR 差異
            - - 目標：CTR 從 0.63% 提升至 1.0–1.5%
             
              - **調整 3 — GTM 轉換事件 SOP：**
              - - 三個事件完整設定步驟：GTM 觸發條件 + Meta Pixel 標籤 + Google Ads 轉換標籤
                - - 包含驗證方法（Meta Pixel Helper + Google Ads 轉換報表）
                  - - 包含重複 Pixel 處理步驟
                    - - 包含給 A2 SEO Agent / A4 Pipeline Agent / A5 Data Agent 的備註
                      - - 目標：PMax CPA 從 NT$322 降至 NT$200 以下
                       
                        - ---



## v2.6 — 2026-03-17

**seo-ads-agent.md v2.0 完整重寫 — 修正亂碼 + 廣告系統框架建立**

執行 Agent：A3 Ads Monitor Agent（Claude Sonnet 4.6）

**更新：**
- `projects/seo-ads-agent.md` v2.0 — 直接 commit 到 main，修正舊版 `> > - [ ]` 亂碼格式，完整重寫為 13 個章節的廣告系統技術文件
  - 一、核心目標（短期現金流 + 中長期品牌/SEO）
  - 二、整體漏斗設計（Top/Mid/Bottom Funnel）
  - 三、帳號資訊
  - 四、總預算配置（Google NT$300/天 + Meta NT$300/天 = NT$600/天）
  - 五、Google Ads 廣告系統（PMax 詳細設定 + 近期成效）
  - 六、Meta 廣告系統（目前 2 則進行中 + 1 則草稿）
  - 七、SEO 對接（給 SEO Agent 的關鍵字清單）
  - 八、素材對接（給素材 Agent 的規格 + 現況）
  - 九、待辦事項
  - 十、下次 Agent 接手必問清單
  - 十一、Pixel 串接確認
  - 十二、版本紀錄
  - 十三、相關連結

**廣告現況紀錄（截至 2026-03-17）：**
- Google PMax：NT$300/天，進行中，30天花費 NT$2,257，轉換 7 次，CPA NT$322
- Meta B組公關窗口：進行中，CPA NT$5/互動
- Meta B組企業窗口：進行中，CPA NT$13/互動
- Meta 策略一冷受眾：草稿，素材製作中，待上線

---

## v2.5 — 2026-03-15（最新）

**ai-model-guide v1.1 — GPT特殊地位補充 + 防prompt過長技能**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `skills/ai-model-guide.md` v1.1 — 補充 GPT 特殊地位：最早付費訂閱、長期記憶庫、幻覺校正 SOP、Step 0 背景確認協作流程
- `skills/context-compression-guide.md` v1.0 — 新建：防 prompt too long 技能書，包含 session 規劃、階段存檔、摘要格式、token 壓縮 SOP

**設計原則：** GPT 記憶需經使用者確認才可信；每個 session 應在 context 50% 時主動進行階段存檔

---

## v2.4 — 2026-03-15

**合併 A3+A6 為 Ads Team + 新增 AI 特性技能書**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `AGENT_RULES.md` v1.6 — 合併 A3+A6 為 Ads Team，新增 SECTION 1.1 任務分工表，新增 skills/ai-model-guide.md 引用，錯誤 004 記錄
- `skills/ai-model-guide.md` v1.0 — 新建：Claude / Gemini / GPT 特性說明 + 選 AI 速查表 + Ads Team 跨 AI 協作流程範例

**設計原則：** 以技能書取代固定角色召喚，任何 AI 接手時依任務性質查 ai-model-guide.md 選用最合適工具，不需重複說明背景

---

## v2.3 — 2026-03-15

**A1 系統巡查 + CURRENT_EXECUTION_BOARD 修正**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `CURRENT_EXECUTION_BOARD.md` v1.2 — 修正重複區塊（v1.0+v1.1 並存問題），新增「已知規則不明問題」SECTION，新增問題 004/005/006，同步 A4 路線等待狀態
- **發現問題（問題 004–006，詳見 CURRENT_EXECUTION_BOARD.md）：**
  - 問題 004：A3 與 A6 職責邊界不清（ads_agent.py 歸屬模糊）
  - 問題 005：maplab-master-data.md header v1.3 與實際內容 v1.4 版本矛盾
  - 問題 006：CURRENT_EXECUTION_BOARD.md 重複區塊（已本次修正）

---

## v2.2 — 2026-03-14

**初始版本歷史建立**

執行 Agent：A1 Handbook Agent

**更新：**
- 初始 CHANGELOG.md 建立
- 記錄 maplab-ai-handbook 早期版本歷史
