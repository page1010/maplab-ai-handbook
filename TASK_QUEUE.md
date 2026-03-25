# TASK_QUEUE.md — 任務池
> Agent 從這裡認領任務。認領前必須先讀 CURRENT_STATUS.md。

最後更新：2026-03-25 | 維護者：A1 / Owner / A2

---

## 認領規則

1. 先讀 CURRENT_STATUS.md 確認系統狀態
2. 從下方任務池選一個你角色範圍內的任務
3. 確認前置條件已滿足（未滿足 = 不能認領）
4. 輸出認領格式後，等 owner 確認才開始
5. 開始後建立對應的 Task Card（handoff/tasks/T-xxx.md）
6. 完成後更新本文件狀態 + 寫 handoff checkpoint

### 認領格式（開始前必須輸出）
```
Task Claim
- Task ID: T-xxx-xxx
- Agent: A?
- Files I will read: [清單]
- Files I will modify: [清單]
- Files I will NOT touch: [清單]
- Estimated scope: [簡述]
- Preconditions met: Yes/No
```

---

## 🔴 高優先

| Task ID | 任務 | 適合 Agent | 前置條件 | 狀態 |
|---------|------|-----------|---------|------|
| T-A2-001 | 文章精選圖片補齊（57篇→每篇獨立配圖） | A2 | 無 | 🔄 進行中（Phase 2: 22/57） |
| T-A1-002 | Phase 4.1 系統治理升級 — 全部完成 | A1 | 無 | ✅ 完成 |
| T-A5-001 | Items 甜點(DST)去重 + 全品項重新編碼 | A5 | 使用者手動完成甜點去重 | ⏸️ 等使用者 |
| T-A5-002 | QUOTE_DRAFT 報價單增強（飲料容量/保冰桶/招待欄位）| A5 | T-A5-001 完成 | 🔲 待開始 |
| T-A5-004 | 使用者填 Items.D 欄 default_price | Owner | — | ⏸️ 等使用者 |

## 🟡 中優先

| Task ID | 任務 | 適合 Agent | 前置條件 | 狀態 |
|---------|------|-----------|---------|------|
| T-A5-003 | 熱客招待品項定義（小西點+隨機禮品）| A5 | 無 | 🔲 可認領 |
| T-A5-005 | 2025 訂單品項抽樣（TimeTree 密集週 → Sheet 本週訂單）| A5 | 無 | 🔲 可認領 |
| T-A2A3-001 | SEO 關鍵字頁面補足（台南外燴總頁等 5 頁）| A2/A3 | 無 | 🔲 可認領 |
| T-A4-001 | vision.py Phase 4 — Gemini 分析 + EXIF | A4 | 用戶確認相片來源（Mina 照片清洗中，不急） | ⏸️ 等使用者 |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 + 優化 | A3 | ✅ 使用者已用現有貼文上線 | 🔄 確認中 |
| T-GBP-001 | Google 商家檔案「一歲生日客製化週歲派對外燴」產品圖片更換 | Owner | 需準備新圖片 | 🔲 待開始 |

> **T-GBP-001 備註**：位置 = Google 商家檔案 > MAPLAB Kitchen (maplab-tainan) > 編輯產品 > 「一歲生日客製化週歲派對外燴」（週歲派對/家庭聚餐類別，$12,000）。刪除現有圖片後上傳新圖。

## 🟢 低優先

| Task ID | 任務 | 適合 Agent | 前置條件 | 狀態 |
|---------|------|-----------|---------|------|
| T-A5-006 | OrderLines 2025 手動重建（R6 任務）| A5 | T-A5-005 完成 | 🔲 待開始 |
| T-A7-001 | AI 回覆系統對話紀錄整理 + 規則建立 | A7 | 無 | 🔲 可認領 |
| T-A4-002 | pagewu1010 帳號 187GB Takeout 處理 | A4 | T-A4-001 完成 | 🔲 待開始 |

---

## ✅ 已完成（歸檔區）

> 完成的任務從上方移到這裡。只保留最近 10 筆。

| Task ID | 任務 | 完成者 | 完成日期 |
|---------|------|-------|---------| 
| — | A1 系統治理升級 v3.9（PROTOCOL v1.5 + AGENT_RULES v2.2 + task-progress-guide + TimeTree v2.0 + handoff-to-A5） | A1 | 2026-03-23 |
| T-A3-001 | GTM LINE 按鈕追蹤修復（方案 B regex + Pixel Helper 驗證） | A2/A3 | 2026-03-24 |
| T-A1-001 | Phase 4.2 全系統文件對齊（README/SYSTEM_MAP/WORKFLOW_MAP/BOARD） | A1 | 2026-03-19 |
| — | Phase 3 全部 4 項任務 | A1 | 2026-03-18 |
| — | A2+A3 合併為 SEO & Ads Team | A1 | 2026-03-18 |
| — | A5 Items 清洗 v1.5（BEV容量/去重/後綴） | A5 | 2026-03-18 |
| — | A5 QUOTE_DRAFT 極簡版 MVP | A5 | 2026-03-17 |
| — | A5 TimeTree 密集日掃描 | A5 | 2026-03-17 |

維護者：A1 Handbook Agent + Owner。Agent 只能更新自己認領的任務狀態。
