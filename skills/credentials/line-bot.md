# LINE Bot / Webhook 技能書

版本：v1.0 | 建立：2026-04-01 | 維護者：A1

---

## 鑰匙位置

| 變數 | 位置 | 說明 |
|------|------|------|
| `LINE_CHANNEL_SECRET` | Notion「MAPLAB API Keys」頁 或 `bot/.env`（本機） | LINE Developers → Messaging API → Channel Secret |
| `LINE_CHANNEL_ACCESS_TOKEN` | Notion「MAPLAB API Keys」頁 或 `bot/.env`（本機） | LINE Developers → Messaging API → Channel access token (long-lived) |
| Channel ID | `1654658337` | LINE Developers Console 可見，非機密 |

> ⚠️ 金鑰不進 git。若懷疑洩漏，立即到 LINE Developers 重新 Issue 新的 token。

---

## Webhook 設定步驟

### 方法 A：LINE OA Manager（manager.line.biz）
1. 左側選單 → **「設定」**（齒輪圖示）
2. → **「回應設定」**
3. 找到 **「Webhook」** 區塊 → 開關切換為**開啟**
4. 若需填 Webhook URL → 回到 **LINE Developers Console**（developers.line.biz）

### 方法 B：LINE Developers Console（developers.line.biz）
1. 進入 Console → 選 Channel `1654658337`
2. → **「Messaging API」** 分頁
3. **「Webhook URL」** 欄位貼入 Apps Script URL：
   ```
   https://script.google.com/macros/s/AKfycbz_zA_tG2fxNRlvrRMsJyMAzbnpNC-IL8oKqc5h94kyhExsIOuuo7LujbrSuZGK_eap/exec
   ```
4. 點**「Update」** 儲存
5. 點**「Verify」** 驗證（回傳 `200 OK` = 成功）
6. 確認「**Use webhook**」開關是藍色/開啟

> ⚠️ LINE OA Manager 的 Webhook 開關 和 Developers Console 的 Use webhook 是同一個設定，兩邊會同步。

---

## Apps Script Webhook 程式碼位置

- Google Drive → Apps Script 專案（與 Sheets 同帳號）
- Spreadsheet ID：存於 Script 內 `SHEET_ID` 變數
- 寫入目標分頁：`CONVERSATION_LOG`
- 部署 ID：`AKfycbz_zA_tG2fxNRlvrRMsJyMAzbnpNC-IL8oKqc5h94kyhExsIOuuo7LujbrSuZGK_eap`

---

## 驗證流程

1. 用個人 LINE 帳號傳訊息給 MAPLAB LINE OA
2. 開 Google Sheets → `CONVERSATION_LOG` 分頁
3. 有新增一筆 = Webhook 正常

---

## 金鑰被洩漏時的處理

1. LINE Developers Console → Messaging API → Channel access token → **Issue**（舊的立即失效）
2. Channel Secret → **Regenerate**
3. 更新 `bot/.env`（本機）和 Notion
4. 不需要重新設定 Webhook URL
