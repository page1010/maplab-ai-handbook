# 57 篇舊文批量分析 — 內鏈+語氣建議清單

> 來源：Codex sub-agent（gpt-5.5）呼叫 | 日期：2026-07-10
> 分析對象：WordPress 57 篇既有文章（唯讀，未修改任何文章）
> **所有建議需 A2/Owner 核准後才可實際修改 WordPress 文章**

---

## 一、內鏈機會 Top 10

| 優先順序 | 來源頁 | 目標頁 | 建議錨文字 | 理由 |
|---|---|---|---|---|
| 1 | `tainan-outdoor-wedding-catering` | `tainan-wedding-catering-cost` | 台南婚禮外燴費用怎麼抓 | 婚禮 pillar 已定案，但費用型子頁需從 pillar 明確承接高轉換搜尋意圖。 |
| 2 | `tainan-wedding-catering-cost` | `tainan-outdoor-wedding-catering` | 台南戶外婚禮外燴完整規劃 | 婚禮費用頁應回鏈 pillar，避免費用頁單獨吃掉婚禮主題權重。 |
| 3 | `tainan-outdoor-wedding-catering` | `wedding-catering-vs-banquet-tainan` | 婚宴外燴與傳統桌菜比較 | 決策比較型子頁是婚禮群組最接近詢問前的入口，應由 pillar 導流。 |
| 4 | `tainan-wedding-welcome-canapes` | `tainan-outdoor-wedding-catering` | 戶外婚禮外燴與迎賓茶點配置 | canapes 子頁要回到婚禮主頁，避免只停在菜單細節。 |
| 5 | `corporate-catering-tainan` | `icc-tainan-catering` | 大臺南會展中心外燴案例 | ICC 是高價值 B2B 場域案例，應由企業外燴主入口帶權重與信任證據。 |
| 6 | `corporate-tea-party-desserts` | `corporate-tea-party-catering-tips` | 企業茶會外燴操作技巧 | 會議茶點 pillar 應導向 tips 子意圖，補足「怎麼安排」搜尋需求。 |
| 7 | `corporate-tea-party-catering-tips` | `corporate-tea-party-desserts` | 企業茶會點心外燴完整方案 | tips 子頁應回鏈 924 pillar，避免企業茶點群組互搶。 |
| 8 | `catering-one-year-old-party-tainan` | `gender-reveal-party-tips` | 性別揭曉派對流程與甜點桌安排 | 週歲 pillar 已承接性別派對流量，需把獨立 gender reveal 子頁納入 cluster。 |
| 9 | `gender-reveal-party-tips` | `catering-one-year-old-party-tainan` | 週歲與性別揭曉派對外燴規劃 | gender reveal 子頁應回鏈週歲 pillar，讓生日/週歲受眾匯回主轉換頁。 |
| 10 | `tainan-catering-cost-guide` | `tainan-corporate-catering-cost` | 企業外燴費用估算 | 泛費用頁應導到企業分眾費用頁，降低 cost 群互搶並提高 B2B 轉換。 |

---

## 二、語氣複查優先順序（Top 10 篇）

| 優先順序 | 文章 slug / 主題 | 風險類型 | 建議行動 |
|---|---|---|---|
| 1 | `tainan-custom-catering-menu` / 台南外燴菜單推薦 | ⚠️ 食安紅線（無麩質）、FAQ schema 重複風險 | **最高優先**：人工改「無麩質」為「素食或其他飲食限制」等中性說法，正文與 JSON-LD 兩處都要查（post 698，已知問題）。 |
| 2 | `tainan-catering-sustainability-guide` / 永續外燴 | ESG/SDG 法規語感、空泛概念風險 | 避免認證式語氣，改成「減少一次性用品」「依活動需求調整」等具體做法。 |
| 3 | `tainan-catering-not-suitable-situations` / 不適合外燴情境 | 語氣過度否定、像在教育客人 | 改成溫和邊界說明，避免「不適合」「不能」堆疊造成拒客感。 |
| 4 | 婚禮群組：post 1213/1215/1217/1218/1220 | 浪漫過度、AI 形容詞、說服式句型 | 逐篇掃「一生一次、夢幻、最適合、不是而是、不僅更」；保留克制場景感。 |
| 5 | `tainan-wedding-welcome-canapes` | 已曾被標記 AI 說服式句型 | 人工重讀整篇，不只掃 regex；避免「驚艷、完美、最好」這類用力成交語。 |
| 6 | 費用群組：`tainan-catering-cost-guide`、`tainan-corporate-catering-cost`、`tainan-wedding-catering-cost` | 價格敏感、低價/CP 值風險 | 用「配置、服務範圍、人力、場地條件」說明價格，不走便宜或划算語氣。 |
| 7 | `tainan-catering-customer-reviews` | 見證文過度保證、空泛好評 | 只保留具體場景與可驗證描述，避免「保證滿意」「客戶一致推薦」類句型。 |
| 8 | 企業矩陣薄頁：post 1199/1201/1207/1209/1211 | 掛案例分類但缺真案例、AI 腔 | 若沒有真案例與圖，就改成指南頁語氣；不要用案例語氣包裝薄內容。 |
| 9 | `brand-esg-catering-service` / 品牌 ESG 活動外燴 | ESG 法規與品牌恭維過度 | 雖已修過崩壞尾巴，仍建議複查 ESG 用詞是否像認證或承諾。 |
| 10 | `tainan-catering-line-inquiry-guide` | CTA 過度推進、LINE 私訊硬賣 | CTA 改成「提供活動資訊後協助整理方向」，避免「趕快預約、名額有限」式語氣。 |

---

## 三、系統性觀察

1. **雙向內鏈閉環是當前最高優先**：婚禮、會議茶點、週歲三個 pillar/child 關係已定案，但最需要補的是雙向內鏈閉環，不是再新增文章。現有群組缺乏從子頁回鏈 pillar 的習慣，pillar 也未明確導流到所有子頁。

2. **2026-03 批量矩陣頁是最大語氣與分類風險**：很多頁是低圖、低內鏈、偏 AI 腔，卻掛在「案例」分類；應優先補真案例或改成指南分類，讓分類邏輯與內容深度一致。

3. **「無麩質」紅線尚未徹底清除**：舊文 post 698 已確認踩線，部分草稿 FAQ 也出現同類 wording，發布前應統一改成飲食限制的中性表述（「素食」「特殊飲食需求」），避免 seo_publish_gate.py F-1 gate 未來產生漏報。
