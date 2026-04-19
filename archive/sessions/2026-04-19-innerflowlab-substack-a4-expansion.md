# Session 存檔：InnerFlowLab + Substack + A4 擴充規劃

**日期**：2026-04-19
**參與者**：Owner ↔ A1（via Telegram Bot）
**狀態**：決策已定，任務交給 A0 執行

---

## 決策摘要

### 1. Substack 協作模式
- **不開新角色**，掛在 A2 底下用技能書區分
- 已建技能書：`skills/a2-substack-collab.md`
- 未來量大再拆（A2S 或 A9）

### 2. InnerFlowLab 網站定位
- **網域**：innerflowlab.com（Owner 已有，原為心靈網站）
- **決定**：直接轉型為英文 AI 故事系列主站，不用子網域
- **舊內容**：不刪，讓新文章自然蓋過
- **雙線結構**：
  - **Building（Lab 線）**：跟 AI 建系統的真實故事
  - **Reflecting（Inner 線）**：AI 對話 × 榮格 / 心理學 / 自我覺察
- Substack 用 Sections 分流，不開兩個帳號
- 域名不賣，自用價值 > 賣價（估值 $100-500 USD）

### 3. Substack 帳號設定
- 用 Google 帳號登入，在 Substack 設定裡改 profile
- Publication name: InnerFlowLab
- Bio（Owner 選定 250 字元版）：
  > Business owner, not an engineer. I built a system of 8 AI agents to run my catering company. Here I document the messy process — building, breaking things, and the quiet moments when AI conversations lead to Jung, self-reflection, and unexpected clarity.

### 4. A4 照片分類 — Gemini Flash 擴充規劃
- **現狀確認**：Gemini 2.5 Flash 免費 tier，跑在 Colab，已處理 ~35,000 張
- **免費額度**：照片分類幾乎吃不完，不花錢
- **擴充方向**（不開新 Agent，掛在 A4）：

| 優先順序 | 功能 | 用途 |
|---------|------|------|
| 1 | alt text / caption 生成 | SEO（WordPress 圖片 alt 欄位） |
| 2 | 品質評分（構圖/光線 1-5 分） | Slide 母版自動選圖（A5 報價） |
| 3 | 旅遊照片分組 + story caption | InnerFlowLab 文章配圖 |

- **排除項目**：競品菜單分析、名片 OCR（Owner 明確不需要）
- **技術做法**：同一張照片一次 API call，用不同 prompt 段落拿多個輸出

---

## Owner 待辦（A1 幫不了的）
- [ ] 註冊 Substack（InnerFlowLab）
- [ ] 確認 innerflowlab.com DNS 管理位置
- [ ] 開始寫第一篇故事

## 交給 A0 執行的任務
- Owner 表示已把任務交給 A0
- 具體範圍：A4 Gemini Flash 擴充 + Substack 技術串接

---

## 技能書更新紀錄
- `skills/a2-substack-collab.md` — 已建立 + 已更新（加入雙線結構、innerflowlab.com、Sections 分流）
