# Troubleshooting Hub — Agent 卡住時先看這裡

版本：v1.0 | 建立：2026-03-17 | 維護者：A1 Handbook Agent

---

## 使用時機

執行任務時遇到問題 → 嘗試 1-2 次修不好 → **來這裡查**。

不要浪費 context 亂試。查表 → 找到技能書 → 照著做。

---

## 快速診斷表

| 症狀 | 可能原因 | 解法摘要 | 參考文件 |
|------|--------|---------|--------|
| Colab session 斷線 / 超時 | 長任務未設 checkpoint | checkpoint + timeout + retry | `colab-resilience-guide.md` |
| Prompt too long | context 爆炸 | 階段存檔 + 壓縮 + 換 session | `context-compression-guide.md` |
| GitHub API 403 / 409 / 422 | token 權限 / SHA 過期 | 重新 GET SHA，檢查 branch | `github-api-workflow-guide.md` |
| 不確定該用哪個 AI | 任務特性不同 | 查 Claude/GPT/Gemini 對照表 | `ai-model-guide.md` |
| Bug 修 3 次修不好 | 根因判斷錯誤 | 停下來，走四階段除錯法 | `systematic-debugging-cloud-guide.md` |
| 說「完成」但沒證據 | 缺驗證步驟 | 5 步驗證關卡 | `verification-checklist-guide.md` |
| Google Sheets 追蹤混亂 | 缺乏欄位結構 | 標準追蹤表範本 | `sheets-tracking-guide.md` |
| 不可逆操作導致資料遺失 | 未確認依賴鏈 | 刪除前列依賴 → 驗證 → 才刪 | `lessons-learned.md` INCIDENT-001 |
| 不知道上次做到哪 | 沒讀交接文件 | 讀 handoff + BOARD | `HANDOFF_TEMPLATE.md` + `CURRENT_EXECUTION_BOARD.md` |
| 不知道自己該做什麼 | 沒走啟動協議 | 重走 8 步驟 | `AGENT_STARTUP_PROTOCOL.md` |
| Colab 長任務輸出灌爆 context | 沒用 quiet mode | `-q` 靜音 + 只印摘要 | `context-compression-guide.md` 規則 5 |
| btoa 中文亂碼 | 編碼問題 | `btoa(unescape(encodeURIComponent(text)))` | `github-api-workflow-guide.md` 踩坑表 |
| 任務做到一半要如何做大局分析 | 缺策略思維 | 商業指標 → 差距 → 優先排序 | `strategic-review-guide.md` |

---

## 找不到解法？

**不要自己亂試。** 按以下步驟回報：

### 回報格式

```
## 新問題回報
- 症狀：（一句話描述你卡在什麼）
- 嘗試過：（試了什麼、結果如何）
- 結果：（錯誤訊息 / 非預期行為）
- 建議分類：Colab / API / 資料 / 流程 / 權限 / 其他
```

### 回報流程

1. 用上述格式記錄問題
2. 回報給 A1 或 owner
3. A1 將解法補充到本文件的診斷表
4. 下次所有 Agent 都能查到 → 系統持續進化

---

## 使用規則

1. **先查再問** — 執行中卡住，先 Ctrl+F 搜這份文件
2. **不重複踩坑** — 每次新問題解決後，A1 必須更新本表
3. **只做路由** — 本文件不重複寫解法，解法在各 skills/*.md 裡
4. **低門檻** — 搜關鍵字就能找到對應技能書

---

## 版本紀錄

| 版本 | 日期 | 變更摘要 | 更新者 |
|------|------|---------|--------|
| v1.0 | 2026-03-17 | 初始建立：13 個常見症狀診斷表 + 回報流程 + 使用規則 | A1 Handbook Agent |
