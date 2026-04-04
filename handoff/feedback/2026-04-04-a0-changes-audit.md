# A0 2026-04-04 改動審計

## 改動了什麼（全部推到 LINE 專案，報價系統沒動）

### LINE 專案（傳line對話到外燴系統sheet）被改的檔案：
1. Code.gs — 版本從 v3.1 改到 v3.8，多次修改 createQuote（客戶資訊位置、品項篩選、條款位置）
2. LineWebhook.gs — doPost 改成路由模式（LINE + createQuote + createSlides）
3. createSlides.gs — 新建，Slide 報價簡報生成
4. appsscript.json — 加入 presentations scope + oauthScopes

### 報價系統（MAPLAB_外燴系統_v0.1）：
⚠️ 完全沒被 A0 動過。所有 clasp push 都推到 LINE 專案。

### QUOTE_DRAFT 模板（Google Sheet）：
⚠️ 模板的 D9/D12 品項被 GAS 執行時改動（不確定哪次測試改的）
→ 已用版本紀錄還原到 4月3日下午5:00

### Drive 資料夾：
- MAPLAB_報價單/2026/ 裡多了好幾份測試報價單（檔名含「A0測試中」）
- MAPLAB_Proposals 裡可能有測試 Slide（如果 createSlides 成功執行過）

## 下一步（Owner 指示）
1. clasp pull 報價系統專案的現有程式碼，只看不動
2. 比對報價系統 vs LINE 專案的 createSlides.gs 哪個版本更好
3. 備份兩邊程式碼
4. 決定保留哪個版本後再做整合
