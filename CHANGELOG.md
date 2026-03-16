# CHANGELOG.md — MAPLAB AI System 版本演進紀錄

本文件記錄 maplab-ai-handbook 的所有重大版本變更。
格式：版本號 | 日期 | 變更摘要 | 執行 Agent

---

## v2.5 — 2026-03-15（最新）

**ai-model-guide v1.1 — GPT特殊地位補充 + 防prompt過長技能**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `skills/ai-model-guide.md` v1.1 — 補充 GPT 特殊地位：最早付費訂閱、長期記憶庫、幻覺校正 SOP、Step 0 背景確認協作流程
- `skills/context-compression-guide.md` v1.0 — 新建：防 prompt too long 技能書，包含 session 規劃、階段存檔、摘要格式、token 壓縮 SOP

**設計原則：** GPT 記憶需經使用者確認才可信；每個 session 應在 context 50% 時主動進行階段存檔

---

## v2.4 — 2026-03-15

**合併 A3+A6 為 Ads Team + 新增 AI 特性技能書**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `AGENT_RULES.md` v1.6 — 合併 A3+A6 為 Ads Team，新增 SECTION 1.1 任務分工表，新增 skills/ai-model-guide.md 引用，錯誤 004 記錄
- `skills/ai-model-guide.md` v1.0 — 新建：Claude / Gemini / GPT 特性說明 + 選 AI 速查表 + Ads Team 跨 AI 協作流程範例

**設計原則：** 以技能書取代固定角色召喚，任何 AI 接手時依任務性質查 ai-model-guide.md 選用最合適工具，不需重複說明背景

---

## v2.3 — 2026-03-15

**A1 系統巡查 + CURRENT_EXECUTION_BOARD 修正**

執行 Agent：A1 Handbook Agent（Claude Sonnet 4.6）

**更新：**
- `CURRENT_EXECUTION_BOARD.md` v1.2 — 修正重複區塊（v1.0+v1.1 並存問題），新增「已知規則不明問題」SECTION，新增問題 004/005/006，同步 A4 路線等待狀態
- **發現問題（問題 004–006，詳見 CURRENT_EXECUTION_BOARD.md）：**
  - 問題 004：A3 與 A6 職責邊界不清（ads_agent.py 歸屬模糊）
  - 問題 005：maplab-master-data.md header v1.3 與實際內容 v1.4 版本矛盾
  - 問題 006：CURRENT_EXECUTION_BOARD.md 重複區塊（已本次修正）

---

## v2.2 — 2026-03-14

**初始版本歷史建立**

執行 Agent：A1 Handbook Agent

**更新：**
- 初始 CHANGELOG.md 建立
- 記錄 maplab-ai-handbook 早期版本歷史
