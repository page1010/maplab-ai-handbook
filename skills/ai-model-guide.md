# AI Model Guide — MAPLAB 各 AI 使用建議與特性技能書
版本：v1.1 | 建立：2026-03-15 | 維護者：A1 Handbook Agent

本文件是 MAPLAB AI 系統的「選 AI 指南」。
目的：不依賴固定角色召喚，而是依任務性質選用最合適的 AI，減少每次需要重新說明背景的開銷。

完整角色分工規則見：AGENT_RULES.md

---

## 快速選 AI 對照表

| 任務類型 | 推薦 AI | 次選 | 理由 |
|---------|---------|------|------|
| 程式碼撰寫 / debug | Claude | GPT | 推理鏈長、不易幻覺、可處理大型程式碼檔案 |
| 長文件生成 / 技術文件 | Claude | — | 長 context 處理穩定，格式精確 |
| 規則 / 準則 / Prompt 設計 | Claude | — | 邏輯結構強、可自我檢查矛盾 |
| OAuth / API 技術問題排查 | Claude | — | 程式碼推理 + 錯誤訊息解讀 |
| Google API 串接（Ads/GSC/Sheets） | Gemini | — | Google 生態系原生整合，API quota 共享不消耗 |
| Google Sheets =AI() 公式 | Gemini | — | Sheets 側邊欄原生支援，零部署成本 |
| 廣告數據分析 / ROAS / CPM | Gemini | GPT | 數字處理 + 圖表生成強項 |
| SEO 關鍵字分析 / GSC 數據 | Gemini → GPT | Claude | Gemini 接 GSC API，GPT 做內容策略 |
| SEO 文章草稿生成 | GPT | Claude | 流暢自然語言生成，符合人類閱讀習慣 |
| 廣告文案撰寫 | Claude | GPT | 精準控制語氣、符合品牌規範 |
| 圖片分類 / Vision 任務 | Gemini | Claude | Gemini Vision 對 Google Photos 整合友好 |
| 多工並行執行 | Gemini CLI | — | gemini extensions 支援批次並行任務 |
| 快速問答 / 即時確認 | GPT | Claude | 反應速度快、適合低複雜度確認 |
| Master Data ERP 資料結構設計 | Gemini | Claude | Sheets 整合 + 格式驗證即時反饋 |
| 回覆草稿 / 客服文案 | GPT | Claude | 自然語氣生成、符合品牌溫度 |
| 查詢用戶背景 / 創業現況 / 歷史決策 | GPT | — | 最早付費，記憶最完整，是 MAPLAB 的「長期記憶庫」 |
| 校正 GPT 幻覺 / 更新 GPT 記憶 | Claude + 用戶確認 | — | Claude 提出疑問，用戶確認後協助更新 GPT 記憶 |

---

## Claude — 強項與使用建議

### 核心強項
- **長 context 推理**：可一次處理 200k tokens 的程式碼或文件，不丟失脈絡
- **程式碼品質**：TDD、debug、OAuth 修復、架構設計，錯誤率低
- **邏輯一致性**：規則、準則、Prompt 設計時自動檢查矛盾
- **格式控制**：Markdown 表格、技術文件、交接文件輸出乾淨精確
- **瀏覽器操作**：Superpowers Skills 完整支援，可直接操作瀏覽器執行自動化

### 使用時機
- 任何需要寫程式或 debug 的任務
- GitHub 文件撰寫與維護（本 Handbook 由 Claude 維護）
- 架構設計、流程規劃、錯誤排查
- 需要長時間保持角色一致的任務

### 使用限制
- 不主動執行 Google Ads / GSC 數據抓取（那是 Gemini 的強項）
- 不適合需要即時 Google API quota 共享的任務

### 安裝 Superpowers Skills
```
# Claude Code（官方 Marketplace）
/plugin install superpowers@claude-plugins-official
```
技能書詳細說明見：skills/superpowers-guide.md

---

## Gemini — 強項與使用建議

### 核心強項
- **Google 生態系原生整合**：Ads API、GSC API、Sheets、Drive、Gmail — 零授權衝突
- **Sheets =AI() 函數**：直接在 Google Sheets 側邊欄執行，無需部署，即時驗證格式
- **圖片分析 (Vision)**：對 Google Photos 和 Drive 圖片原生友好
- **數據分析**：圖表生成、ROAS/CPM 分析、廣告成效報告
- **Gemini CLI 批次執行**：gemini extensions 支援並行 Subagent 任務

### 使用時機
- Google Ads API 數據抓取與儀表板更新
- GSC 關鍵字數據拉取與分析
- Google Sheets 公式驗證（使用 =AI() 函數即時執行）
- 圖片分類與 Alt Text 批次生成（Pipeline 的 Vision 模組）
- Master Data 格式驗證（寫入 Sheets 前即時檢查）

### 使用限制
- 不主動修改 GitHub 文件（那是 Claude 的範疇）
- 長程式碼推理和複雜 debug 建議轉交 Claude

### 安裝 Superpowers Skills
```
# Gemini CLI
gemini extensions install https://github.com/obra/superpowers
```

---

## GPT — 強項與使用建議

### ⭐ 特殊地位：MAPLAB 長期記憶庫

GPT 是 MAPLAB 團隊**最早付費使用的 AI**，累積了最完整的用戶背景記憶，包含：
- **創業現況**：MAPLAB Kitchen 的品牌定位、發展脈絡、過去的決策歷程
- **用戶習慣**：Owner 的工作方式、偏好、曾遇到的問題與解法
- **跨專案脈絡**：各專案的來龍去脈，包含很多沒有寫進 GitHub 的背景知識

當任何 Agent 需要了解「為什麼當時這樣決定」「用戶的背景是什麼」「這個需求的前因後果」，**優先去問 GPT**，而不是靠猜測或要求用戶重新解釋。

### ⚠️ 幻覺風險：使用 GPT 記憶時的必要步驟

GPT 的長期記憶雖然豐富，但**可能存在過時資訊或記憶偏差**。每次從 GPT 取得背景資訊時，必須：

1. **取得資訊後，向用戶重複確認**：「GPT 記憶顯示 [X]，這目前還正確嗎？」
2. **發現出入時，協助用戶校正 GPT**：引導用戶更新 GPT 的記憶（告訴 GPT 哪裡錯了、現在的實際狀況）
3. **不要直接把 GPT 說的當作事實**：特別是數字（預算、訂單量）、人名、日期、決策結果

### GPT 幻覺校正 SOP

```
當你從 GPT 取得背景資訊後：

Step 1. 向用戶說明：
        「我從 GPT 記憶中查到 [具體資訊]，請確認這是否正確？」

Step 2. 用戶確認 or 更正：
        - 確認正確 → 繼續使用
        - 有出入 → 請用戶更正 GPT

Step 3. 協助用戶更新 GPT 記憶：
        建議用戶在 GPT 對話中說：
        「請更新你的記憶：[正確資訊]，之前的 [錯誤資訊] 已過時。」

Step 4. 記錄在 GitHub（如果是重要決策變更）：
        更新對應的 projects/*.md，確保 GitHub 版本也同步
```

### 核心強項
- **長期記憶（My GPTs）**：唯一能跨對話保留用戶背景的 AI，是整個系統的「創業記憶庫」
- **自然語言生成**：SEO 文章、廣告文案、回覆草稿，語氣流暢自然
- **快速問答**：低複雜度確認、即時回答，反應速度快
- **SEO 內容策略**：配合 Gemini 的關鍵字數據，生成符合 SEO 架構的文章
- **AI Reply 系統**：A7 的主要工具，對話紀錄整理 + 回覆草稿生成

### 使用時機
- **查詢用戶背景、創業決策歷史**（最重要用途，其他 AI 不具備此能力）
- SEO 文章草稿（A2 Detasys SEO Agent 的主要工具）
- 廣告文案變體生成
- AI 回覆草稿（A7 AI Reply System 的初稿生成）
- 快速確認、即時問答

### 使用限制
- 不直接串接 Google API（需要 Claude/Gemini 中介）
- 長程式碼 debug 穩定性不如 Claude
- **記憶需要定期校正**：有疑問一定問用戶確認，不要盲目相信

---

## 跨 AI 協作流程（Ads Team 範例）

```
任務：廣告成效分析 + 優化建議文件

Step 0. GPT 提供背景（可選）：
        查詢 GPT 記憶 → 確認廣告策略背景 + 歷史決策
        → 向用戶確認 GPT 說的是否還正確
        → 如有出入，協助用戶校正 GPT

Step 1. Gemini 執行：
        python ads_agent.py --mode all
        → 抓取 Google Ads + GSC 數據 → 寫入 Sheets

Step 2. Gemini 分析：
        Sheets 側邊欄 =AI() 函數
        → 自動生成 CPM / ROAS 趨勢分析

Step 3. Claude 輸出：
        讀取 Sheets 分析結果
        → 生成廣告優化建議文件 + 下一步行動清單
        → 更新 projects/maplab-ads-monitor.md

不需要「召喚 A3」或「召喚 A6」。
只需要依步驟選對 AI，任務自然推進。
```

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-15 | 初始版本：各 AI 特性說明 + 選 AI 速查表 + 跨 AI 協作流程範例 | A1 Handbook Agent |
| v1.1 | 2026-03-15 | 補充 GPT 特殊地位：最早付費/長期記憶庫/幻覺校正 SOP/Step 0 協作流程 | A1 Handbook Agent |
