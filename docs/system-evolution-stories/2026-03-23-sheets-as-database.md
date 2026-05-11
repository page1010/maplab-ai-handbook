# 2026-03-23 — Google Sheets 模擬 RDB 的架構決策

> 記錄者：A1 系統總管（從 experience-log EXP-S002 整理）
> 日期：2026-03-13 ~ 2026-03-23
> 背景：MAPLAB Kitchen 需要 ERP 資料庫，選擇用 Google Sheets 而非傳統 DB

---

## Owner 原始需求

外燴工作室需要管理品項、報價、客戶資料，但不想維護資料庫伺服器。

## 過程

考慮過的方案：
1. **PostgreSQL/MySQL** — 功能完整但需要伺服器、維護成本高
2. **Airtable** — 好用但有 row 限制、付費門檻
3. **Google Sheets** — 免費、Owner 直接能看能改、Gemini 輔助驗證

**決定用 Sheets**：外燴業務 <10,000 筆資料，Sheets 完全夠用。

## 架構設計

- 6 張表 + item_id FK 關聯（模擬 RDB）
- 命名規則：`{TYPE}-{SUBTYPE}-{SEQ3}`（如 APP-002）
- Gemini 輔助格式驗證
- GAS（Google Apps Script）處理複雜邏輯

## 學到的事

1. **不要用大砲打蚊子** — 小規模業務用 Sheets 比 DB 進入成本低 10 倍
2. **Owner 能直接操作的工具才有生命力** — Sheets 人人會用，DB 需要寫查詢
3. **先清洗品項再建結構** — 資料品質比架構更重要

## 相關文件
- experience-log: EXP-S002
- T-A1-V6-P2 Task Card
