# AI Model Guide — MAPLAB 各 AI 使用建議與特性技能書
版本：v1.0 | 建立：2026-03-15 | 維護者：A1 Handbook Agent

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

### 核心強項
- **自然語言生成**：SEO 文章、廣告文案、回覆草稿，語氣流暢自然
- **快速問答**：低複雜度確認、即時回答，反應速度快
- **SEO 內容策略**：配合 Gemini 的關鍵字數據，生成符合 SEO 架構的文章
- **智慧體模式**：GPT 有長期記憶（My GPTs），適合需要持續上下文的工作流

### 使用時機
- SEO 文章草稿（A2 Detasys SEO Agent 的主要工具）
- 廣告文案變體生成
- AI 回覆草稿（A7 AI Reply System 的初稿生成）
- 快速確認、即時問答

### 使用限制
- 不直接串接 Google API（需要 Claude/Gemini 中介）
- 長程式碼 debug 穩定性不如 Claude

---

## 跨 AI 協作流程（Ads Team 範例）

```
任務：廣告成效分析 + 優化建議文件

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
