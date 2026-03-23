# handoff-to-A5.md — A1 → A5 跨部門通知

建立日期：2026-03-23 | 發送者：A1 Handbook Agent

---

## 通知：TimeTree 事件資料已增強至 v2.0

A5，你負責的 Master Data 系統現在有一份增強過的 TimeTree 事件資料可以用。

### 檔案位置
`data/timetree_events_2022_2026.json`（commit bdab84c）

### 跟 v1.0 有什麼不同

| | v1.0（舊） | v2.0（新） |
|--|-----------|-----------|
| 內容 | 只有日期 + 類型（catering/travel） | 日期 + 類型 + **客戶/公司名稱** |
| 資料來源 | 手動整理 | TimeTree IndexedDB 程式提取 |
| 範圍 | 2022-2025，361 筆日期 | 2022-03 ~ 2025-06，**392 筆日期、746 筆事件** |
| 抓週 | 包含 | **已排除** |

### JSON 結構
```json
{
  "2024-11-16": {
    "type": "catering",
    "events": ["外燴 陳小姐", "外燴 台南市政府"]
  }
}
```

每個日期下的 `events` 陣列包含該日所有外燴事件標題，可直接用來比對客戶名。

### A5 可以怎麼用
- 比對 Google Drive `外燴訂單` 資料夾中的日期與客戶名，建立完整外燴歷史
- 為 T-A5-005（訂單品項抽樣）提供 TimeTree 密集週的客戶名對照
- 未來如果要做 logo 牆或客戶清單，事件名稱裡有公司/客戶名可直接提取

### 權限狀態
GitHub repo `maplab-ai-handbook` 為 private，所有 Agent 透過同一帳號（page1010）存取，無額外權限設定需求。

---

*此通知由 A1 根據 AGENT_RULES SECTION 1 跨部門溝通職責建立。A5 下次啟動時請確認已讀。*
