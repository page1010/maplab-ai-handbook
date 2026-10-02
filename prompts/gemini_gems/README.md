# Google Gemini Gems 遷移與設定檔備份清單

因應 Google 官方公告（**2026年11月17日起，Gemini Gem 將全面轉為『技能 (Skills)』**），本目錄已將帳號中的全部 14 個客製化 Gems 完整匯出、結構化備份，並同步轉化為 Antigravity 與專案系統之標準 Skill 格式。

## 全球與本機 Skills 啟用狀態
- **Antigravity 全域 Skills 目錄**：`~/.gemini/config/skills/<slug>/SKILL.md`
- **對話中調用指令**：在對話框輸入 `/<slug>` 即可直接調用對應之 Gem 設定與提示詞！

## 14 個 Gems 清單與分類

| 編號 | Gem 名稱 | Slug (技能指令) | 領域 | 原始說明 / 定位 | 字數 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **看新聞找飆股** | `/gem-news-to-alpha` | `investment` | 跨市場「新聞找飆股」研究 SOP，Sell-side 研究員視野，將新聞延伸至上下游與族群。 | 1500 |
| 2 | **貼漲停 成交值 成交量名單** | `/gem-limit-up-turnover-screener` | `investment` | 市場敘事交易研究員，從今日漲停、成交值、成交量名單中篩出右側主線與可執行交易結論。 | 5716 |
| 3 | **私人教練** | `/gem-personal-trainer` | `personal` | 專屬私人教練與恢復顧問，涵蓋運動生理、三鐵耐力、物理治療與創業者時間管理。 | 1309 |
| 4 | **右側交易** | `/gem-right-side-trading` | `investment` | 右側主升段交易研究員，判斷市場 Regime 是否適合做右側並篩選最佳右側標的。 | 1294 |
| 5 | **動能選股與新聞助手-請貼動能向上名單截圖** | `/gem-momentum-stock-screener` | `investment` | 市場環境判斷與動能策略研究助手，依階段分析動能向上股票名單。 | 1622 |
| 6 | **搜票達人** | `/gem-flight-search-expert` | `personal` | 機票專家與搜尋顧問，提供多航點機票促銷比價與行程優化策略。 | 2405 |
| 7 | **大師多視角系統** | `/gem-multi-master-perspective` | `investment` | 專業投資顧問系統 ver2.2.0，融合大盤趨勢、總經研判與多角度論壇驗證。 | 991 |
| 8 | **總經研究員** | `/gem-macro-economic-researcher` | `investment` | 景氣循環週期總經研究員，在衰退前轉入保守資產、動態減碼再平衡與現金決策。 | 3186 |
| 9 | **跨市場財經新聞判讀** | `/gem-cross-market-news-intel` | `investment` | Sell-side 跨市場財經新聞判讀，對照公司 IR、財報、月營收與產業數據確認投資主線。 | 1470 |
| 10 | **sell side研究員-產業新聞** | `/gem-sell-side-industry-news` | `investment` | 嚴謹 sell-side 研究員，針對近90天產業新聞找出受惠於雲端/AI基礎設施重估之標的。 | 1297 |
| 11 | **敘事解析專家** | `/gem-narrative-analysis-expert` | `investment` | 市場敘事解析專家，解構新聞背後之資本敘事與預期差。 | 861 |
| 12 | **大師視角系統** | `/gem-master-view-20-investors` | `investment` | 20 位投資大師論壇系統，固定格式多視角反覆檢視標的與策略。 | 2391 |
| 13 | **seo 助手** | `/gem-maplab-seo-assistant` | `maplab` | MAPLAB Kitchen 品牌總策劃 × 整合行銷顧問 × SEO 寫手 × 廣告策略 × 品牌語氣守門人。 | 2680 |
| 14 | **體驗教育品牌** | `/gem-experiential-education-brand` | `maplab` | 資深體驗教育設計師，協助設計體驗教育課程、遊戲化專案與品牌企業提案。 | 905 |

---
## 檔案架構
1. `gemini_gems_raw_backup.json`：原始匯出 JSON（包含 ID、時間戳、完整提示詞）。
2. `<slug>.md`：獨立之標準 Markdown Prompt，可直接貼入任何 LLM 平台或於系統腳本中調用。
3. `~/.gemini/config/skills/<slug>/SKILL.md`：Antigravity 全域可識別之技能檔案。
