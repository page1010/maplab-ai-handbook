# 邏輯庫 (Logic Vault)

建立：2026-06-19
狀態：B1 Investment OS research logic intake v0

## 名字

對話簡稱：`邏輯庫`

Owner 之後可以直接說：

- `這篇丟邏輯庫`
- `幫我把這篇進邏輯庫`
- `用邏輯庫格式拆這篇`

## 用途

`邏輯庫` 是投資邏輯好文的收納區。它不是新聞摘要庫，也不是買賣建議庫，而是把外部好文章拆成 Investment OS 可重複使用的研究框架。

每篇文章都要回答六件事：

1. 文章主題與來源狀態。
2. 對應角色：哪個 agent 主責，哪些 agent 複核、落地、存檔、巡查。
3. 核心價值：這篇文章提供的可重複判斷方法。
4. 量化與拆解路徑：要變成表格、分數、分類器或檢查清單時怎麼拆。
5. 資料與訓練需求：要餵哪些資料，才不會只停在文字心得。
6. 系統落地建議：下一步應該接到哪個 Investment OS 模組。

## 角色路由

- `B1 Builder`：把文章邏輯轉成規格、資料表、scorecard、prompt contract。
- `B2 Reviewer`：檢查資料流、freshness、來源品質與錯誤模式。
- `B3 Archivist`：保存文章卡、版本、引用與後續 post-mortem。
- `B4 System Patrol`：巡查這套邏輯是否真的被排程、被更新、被驗證。
- `IOS-EVIDENCE`：來源分級、channel check 權重、反證與引用。
- `IOS-MOMENTUM`：產品週期、產業鏈擴散、右側題材與動能整理。
- `IOS-ALPHA`：把文章邏輯轉成可驗證的 alpha hypothesis。
- `IOS-CHIP`：籌碼、法人、借券、融資融券與資金流交叉驗證。
- `IOS-RIGHT`：把產品週期與題材確認轉成右側候選與 long/short pair。
- `IOS-KOL`：當文章來自社群/KOL 時，負責來源留痕與社群語境。

## 檔案規格

- `article_index.json`：文章索引與狀態。
- `YYYY-MM-DD-*.md`：單篇文章邏輯卡。
- `templates/article_template.md`：後續文章的固定輸出格式。

## 邊界

- 不因文章好就直接升格成投資結論。
- 不把未提供 URL 的貼文當成已驗證公開來源。
- 不把 channel check、expert network、小作文直接當正向 thesis。
- 每個可交易推論都必須拆成資料、權重、反證條件與下一步驗證。
