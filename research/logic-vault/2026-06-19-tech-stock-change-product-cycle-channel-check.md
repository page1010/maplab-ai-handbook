# LV-20260619-001 — 科技股研究：理解變化、產品週期與 channel check 權重

## Intake

- 收錄日期：2026-06-19
- 來源：Owner 貼入文章全文。
- 外部 URL：未提供。
- 來源狀態：`owner_provided_text`，可作研究框架收納；若要對外引用或作事實主張，仍需補原始 URL / 作者 / 發文時間。
- 主題標籤：`TMT`、`台股供應鏈`、`product cycle`、`channel check`、`long short equity`、`source weighting`

## 對應角色

主責是 `IOS-MOMENTUM` + `IOS-EVIDENCE`，B1 負責把它變成系統。

| 角色 | 任務 |
| --- | --- |
| `B1 Builder` | 把文章邏輯轉成資料表、scorecard、prompt contract 與後續功能需求。 |
| `IOS-MOMENTUM` | 拆產品週期、供應鏈重排序、瓶頸、share shift、右側題材擴散。 |
| `IOS-EVIDENCE` | 建 channel check 權重、來源可信度、誘因結構、track record 與反證。 |
| `IOS-ALPHA` | 把「變化」轉成可測的 alpha hypothesis，而不是心得。 |
| `IOS-CHIP` | 用法人、借券、融資融券、成交值與資金流確認市場是否正在定價。 |
| `IOS-RIGHT` | 用產品週期 + 題材確認 + 位階，設計右側候選與 long/short pair。 |
| `IOS-KOL` | 若文章來自社群/KOL，保存原文語境、來源與後續準確度。 |
| `B2 Reviewer` | 檢查資料 freshness、來源混用、權重設定與假訊號。 |
| `B3 Archivist` | 保存文章卡、版本與後續 post-mortem。 |
| `B4 System Patrol` | 巡查這套邏輯是否真的有被排程、更新與驗證。 |

## 核心價值

這篇文章最有用的不是「科技股很重要」，而是把科技股研究的核心從找護城河，改成追蹤變化鏈。

1. 科技股研究的核心是理解 `變`：科技是提高生產力、打破既有成本與利潤分配的工具。
2. 產品週期不是只有需求變好，而是會連動供應鏈排序、零組件價值、產能瓶頸、庫存拉貨、客戶份額與市場預期重估。
3. 台股多數公司是供應鏈角色，所以要問公司位置是否變好，而不是只問終端需求是否變好。
4. 同一個技術變化會同時創造贏家和輸家，因此特別適合做 long/short equity 的 pair 思考。
5. Channel check 的價值不在於聽到消息，而在於能不能給每個消息正確權重。
6. Expert network 越普及，越像防守資訊；真正進階的研究，是讓自己變成產業資訊節點。

## 量化與拆解路徑

### 1. 變化鏈 Change Chain Map

每個科技題材先拆成一條變化鏈：

| 問題 | 欄位 |
| --- | --- |
| 變化從哪裡開始？ | technology_trigger、product_trigger、customer_trigger |
| 誰的成本被降低？ | cost_down_actor、cost_down_amount、evidence |
| 誰的利潤被壓縮？ | margin_pressure_actor、price_change、substitution_risk |
| 誰的位置被重估？ | rerated_node、old_role、new_role、why_now |
| 誰拿走增量利潤？ | profit_capture_actor、take_rate、duration、risk |

輸出不是「題材看好」，而是：

- `winner_nodes`
- `loser_nodes`
- `bottleneck_nodes`
- `commoditized_nodes`
- `uncertain_nodes`

### 2. 產品週期 Product Cycle Map

產品週期要拆成六段，避免把短期拉貨誤認成結構成長。

| 段落 | 需要回答 | 量化線索 |
| --- | --- | --- |
| 終端需求 | 是真需求、替換需求，還是庫存拉貨？ | sell-through、出貨、客戶 capex、終端價格 |
| 規格變化 | 新規格是否改變 BOM 與供應商價值？ | BOM share、ASP、認證、design win |
| 供應鏈重排 | 哪些公司拿 share，哪些掉 share？ | 客戶占比、月營收差異、同業相對成長 |
| 產能瓶頸 | 哪個環節限制供給並有定價權？ | lead time、稼動率、報價、交期 |
| 財務穿透 | 營收是否能穿到毛利、EPS、現金流？ | GM、OPM、inventory、AR、FCF |
| 市場重估 | 市場是否已經定價？ | 估值、EPS revision、成交值、法人、券資 |

建議 score：

`product_cycle_score = end_demand 15 + spec_adoption 15 + supply_chain_reorder 15 + bottleneck_pricing 15 + share_shift 20 + financial_translation 20`

### 3. Channel Source Weighting

Channel check 不直接產生結論，只產生加權後的 evidence。

| 權重項 | 分數 | 判斷 |
| --- | ---: | --- |
| 資訊手數 | 20 | 第一手最高；第二、第三、第四手逐步折價。 |
| 位置可見度 | 20 | 來源職能是否真的看得到這件事。 |
| 誘因清楚度 | 15 | 他為什麼要告訴我們，是否想影響預期。 |
| 歷史準確率 | 20 | 過去說法是否可被事後驗證。 |
| 交叉驗證 | 15 | 是否有獨立來源或硬資料支持。 |
| 具體度與時間戳 | 10 | 是否有具體數字、時間、客戶、規格，而不是空泛形容。 |

`channel_source_score` 滿分 100。低於 50 只能進 `rumour / watch`，不能支撐 thesis；50-70 可作輔助線索；70 以上才可進入主要 evidence，但仍要有反證條件。

### 4. 結構成長 vs 庫存幻覺

判斷表：

| 類型 | 支持條件 | 風險訊號 |
| --- | --- | --- |
| 結構成長 | 多客戶 adoption、design win、規格升級、share gain、毛利率同步改善、估值仍未完全反映。 | 單一客戶過度集中、產能快速開出、同業同時暴增。 |
| 庫存週期 | 短期拉貨、渠道補庫、單月營收暴衝、無終端 sell-through 支持。 | inventory / AR 上升、毛利不升、下一季指引保守。 |
| 小作文交易 | 社群擴散快、證據薄、股價先行、來源無 track record。 | 來源誘因不明、沒有硬資料、題材只剩轉述。 |

### 5. Long/Short Pair 設計

同一個變化要同時找贏家與輸家：

| 欄位 | 說明 |
| --- | --- |
| change_event | 哪個產品、規格、客戶或產能變化。 |
| long_candidate | 拿 share / 有瓶頸 / 有毛利穿透的公司。 |
| short_candidate | 掉 share / 舊規格 / 被 commoditize 的公司。 |
| common_factor | 同一產業 beta，避免只是市場方向。 |
| catalyst | 月營收、法說、客戶 launch、報價、庫存數字。 |
| fail_condition | 哪個資料出現就代表 thesis 錯。 |

## 需要拿什麼資料訓練與思考

| 資料 | 用途 | 可能來源 |
| --- | --- | --- |
| 月營收、財報、毛利率、庫存、應收帳款 | 判斷產品週期是否穿透財務。 | MOPS、公司財報、法說資料。 |
| 價格、成交值、族群廣度、法人、借券、融資融券 | 判斷市場是否正在定價與是否過熱。 | TWSE、TPEx、TAIFEX、broker snapshot。 |
| BOM、規格、design win、客戶供應鏈 | 判斷誰在新產品週期中拿到增量價值。 | 公司 IR、拆解報告、產業報告、供應鏈訪談。 |
| Channel check ledger | 訓練來源權重與 post-mortem。 | Expert network、公司拜訪、供應商、客戶、業內人士。 |
| 報價、lead time、稼動率、產能擴張 | 找瓶頸與定價權。 | 供應鏈調研、法說、產業資料。 |
| 市場預期與修正 | 找 expectation gap。 | Consensus、法說 Q&A、新聞、研究報告摘要。 |
| 歷史案例標籤 | 訓練結構成長 / 庫存幻覺 / 小作文分類。 | 既有投資紀錄、watchlist、post-mortem、歷史月營收與股價。 |

訓練資料不能只存結果，必須存當時的 `claim`、`source_score`、`timestamp`、`decision`、`ex_post_outcome`，否則無法讓 B2/B3/B4 回頭校正。

## 思考提示

- 這個變化到底從產品、規格、客戶、產能、成本，還是政策開始？
- 如果某家公司是贏家，輸家是誰？
- 股價反應的是真需求、庫存拉貨，還是市場小作文？
- 目前證據是硬資料、第一手 channel、第二手 channel，還是社群轉述？
- 來源看得到這件事嗎？他說這件事的誘因是什麼？
- 如果 thesis 錯，最早會在哪個資料上露出？
- 這個題材適合 long-only、右側觀察，還是 long/short pair？

## 系統落地

下一步 B1 可以把這張邏輯卡變成兩個小模組：

1. `product_cycle_map`：每個科技題材都要填變化鏈、供應鏈節點、瓶頸、share shift、財務穿透、market pricing。
2. `channel_check_ledger`：每個 channel claim 都要填來源手數、位置、誘因、track record、交叉驗證、事後結果。

B2 的檢查重點：

- 是否把低分 channel claim 寫成事實。
- 是否混淆終端需求、庫存拉貨與供應鏈 share gain。
- 是否有明確反證條件。

B3 的保存重點：

- 每篇文章卡與後續案例 post-mortem 要能互相連回。
- 同一個邏輯若多次被證偽，要標記為需要降權。

B4 的巡查重點：

- `product_cycle_map` 與 `channel_check_ledger` 是否有定期更新。
- 來源分數是否隨 post-mortem 自動調整。
- 邏輯庫是否只收文，卻沒有被接到每日動能、新聞、右側與 evidence 報告。
