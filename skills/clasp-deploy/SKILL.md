# clasp 部署防呆指南（Apps Script 部署技能）

> 每次 AI 協作者需要部署 Apps Script 時，先讀這份文件。
> 最後更新：2026-04-01 | 教訓來源：.clasp.json 在 worktree 遺失導致反覆排查

## 觸發條件

Owner 說以下任何一句話時，啟動本 Skill：
- 「clasp 部署」「clasp push」「部署 Apps Script」
- 「更新 Google Apps Script」「把程式碼推上 Google」
- 「LINE webhook 部署」「報價系統部署」

---

## 快速部署（30 秒版本）

```bash
cd scripts/apps-script
clasp push
```

就這樣。.clasp.json 已經在 repo 裡了。

## 環境資訊

| 項目 | 值 |
|------|-----|
| clasp 版本 | 3.3.0 |
| clasp 路徑 | /opt/homebrew/bin/clasp |
| 認證檔 | ~/.clasprc.json（OAuth tokens，不要 commit） |
| Script ID | 1Fkl34P7p395k0YzwY8hyhz7DAAsgA3CBgyumx9ImSOFoXu771lFABSi7 |
| .clasp.json | scripts/apps-script/.clasp.json（已 commit 到 repo） |
| 綁定 Spreadsheet | 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg |
| 專案名稱 | 傳line對話到外燴系統（含 LINE webhook + 報價系統） |

## 部署目錄結構

```
scripts/apps-script/
├── .clasp.json          ← 已 commit，不用重建
├── appsscript.json      ← GAS manifest
├── Code.gs              ← 報價系統主程式
├── line-webhook.gs      ← LINE Webhook
├── QuoteForm.html       ← 報價表單 UI
└── setup-template.gs    ← 一次性模板設定（可刪）
```

## 部署步驟

1. `cd scripts/apps-script/`
2. `clasp pull` — 先拉線上版，確認沒人改過（比對 diff）
3. 修改 .gs 或 .html 檔案
4. `clasp push` — 部署到 Google
5. 回到 Google Sheet 重新整理，測試功能

## 踩坑紀錄

### .clasp.json 遺失問題（已解決）
- **問題**：.clasp.json 之前沒有 commit，每個 worktree 都找不到，每次都要重新找 Script ID
- **解法**：把 .clasp.json commit 到 repo。scriptId 不是 secret，可以公開
- **教訓**：工具配置檔（.clasp.json 等）如果不是 secret，就該 commit。「以後會用到的東西」不 commit = 每次重做

### clasp push 會覆蓋所有檔案
- **問題**：push 會用本地目錄完全取代線上版。如果本地缺少某個 .gs 檔，線上版該檔案會被刪除
- **解法**：push 前一定先 `clasp pull`，把線上版拉下來比對，確保沒有遺漏
- **教訓**：線上有 `程式碼.js`（LINE webhook），repo 有 `Code.gs`（報價系統），兩邊檔名不同。合併後才能一起 push

### Code.gs cell references 必須對齊 Sheet 版面
- **問題**：Code.gs 寫入 B2-B9 但實際版面的值在 C2、C3、E3、E4 等位置
- **解法**：修改前一定要先截圖確認 Sheet 實際版面，不要假設 cell 位置
- **教訓**：Sheet 版面會隨人工編輯改變，Code.gs 不會自動跟上。每次改 Code.gs 都要重新確認版面對照

### 認證問題
- `~/.clasprc.json` 是 OAuth token，絕對不能 commit
- 如果 `clasp push` 失敗說未認證：`clasp login` 重新認證
- 認證綁定的是 Google 帳號，不是專案

## 注意事項

- 這個 Script 專案同時包含報價系統和 LINE Webhook，push 時不能漏檔
- `QuoteForm.html` 是報價表單 UI，Code.gs 的 `showQuoteForm()` 會載入它
- 線上版檔名可能是中文（如 `程式碼.js`），pull 下來要注意命名
- push 後選單可能不會立刻出現，需要重新整理 Sheet
