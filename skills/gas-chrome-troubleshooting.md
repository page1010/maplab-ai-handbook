# Skill: gas-chrome-troubleshooting — GAS + Chrome 常見問題排除

## 觸發條件
在 Chrome 操作 GAS / Google Slides / Google Sheets 時遇到問題

## 常見問題 + 解法

### 1. GAS 需要授權
症狀：執行函數時跳出「需要授權」彈窗
解法：直接用 Chrome 點「審查權限」→ 選帳號 → 允許。不要來回問 Owner。

### 2. 頁面沒刷新 / 顯示舊資料
症狀：Chrome tab 顯示舊內容、檔案找不到
解法：F5 刷新頁面。如果還是不行，Cmd+Shift+R 強制刷新。

### 3. Drive 檔案打不開 / 顯示「檔案不存在」
症狀：GAS 產出的檔案 URL 打開後 404
解法：去 Drive 資料夾找檔案 → 雙擊打開（不要用 URL 直接開）

### 4. clasp push 後 GAS 編輯器看不到新程式碼
症狀：push 成功但編輯器還是舊版
解法：F5 刷新 GAS 編輯器頁面

### 5. GAS 執行記錄看不到
症狀：切到其他頁面後記錄消失
解法：不要切頁面，在執行記錄面板等待完成

### 6. GAS 部署版本沒更新
症狀：clasp push 了但 Web App 行為沒變
解法：管理部署 → 建立新版本 → 部署。clasp push 只更新程式碼，不更新部署。

### 原則
- 這些問題 A0 自己解決，不要問 Owner
- 如果 3 秒內可以用 F5/刷新解決，直接做
- 如果需要 Owner 點授權，用 Chrome 自己點按鈕
