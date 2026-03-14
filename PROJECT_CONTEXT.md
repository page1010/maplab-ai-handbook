# PROJECT_CONTEXT.md — MAPLAB AI 專案地圖

**閱讀順序：README.md → 你在這裡 → AI_WORKFLOW_MAP.md → AGENT_RULES.md**

本文件是第二層文件，提供每個專案的詳細脈絡、現況、依賴關係與負責 Agent。

---

## Project 1: maplab-ai-handbook（系統治理）

**目的：** 作為整個多 Agent 系統的公開治理層與知識中樞

**主要 Agent：** A1 Handbook Agent

**主要 Repo：** maplab-ai-handbook（本 repo，公開）

**當前狀態：** 持續維護中，v2.0 文件改造進行中

**依賴項：** 無（本 repo 是其他所有 repo 的知識基礎）

---

## Project 2: maplab-pipeline（相簿自動化）

**目的：** 建立從 Google Photos 到 WebP 格式、上傳 Drive、記錄至 Notion 的完整自動化流程

**主要 Agent：** A4 Pipeline Agent

**主要 Repo：** maplab-pipeline（私有）

**當前狀態：** Phase 1 進行中 — 相簿整理自動化（v2.2）

**流程說明：** Google Photos 原始照片（唯讀）→ WebP 轉檔 → Google Drive 歸檔 → Notion 事件頁面更新

**關鍵約束：** 絕對不得刪除 Google Photos 原始照片（只讀取）

**依賴項：** Google API 授權、Notion 事件頁面結構、命名規則標準

**詳細文件：** [projects/maplab-pipeline.md](./projects/maplab-pipeline.md)

---

## Project 3: maplab-Detasys（SEO & 廣告監控）

**目的：** 提供 SEO 內容生成腳本與 Meta 廣告監控自動化工具

**主要 Agent：** A2 SEO Content Agent / A3 Ads Monitor Agent / A6 Ads Tech Agent

**主要 Repo：** maplab-Detasys（私有）

**當前狀態：** SEO Python v1.4 可用；Meta 廣告 OAuth 修復中

**工具清單：** ads_agent.py v1.4（廣告監控腳本）、SEO 文章生成模組、OAuth 授權流程

**依賴項：** Meta API Token、Google Search Console API、WordPress 存取權限

**詳細文件：** [projects/seo-ads-agent.md](./projects/seo-ads-agent.md) / [projects/maplab-ads-monitor.md](./projects/maplab-ads-monitor.md)

---

## Project 4: maplab-master-data（廚房 ERP 主資料）

**目的：** 建立 MAPLAB Kitchen 的主資料結構，成為後續分析與自動化的資料底座

**主要 Agent：** A5 Master Data Agent

**主要 Repo：** maplab-master-data（私有，待建立）

**當前狀態：** v0.7 架構設計中，Sheets 結構規劃階段

**資料範圍：** 客戶資料、活動訂單、食材品項、報價單、活動紀錄

**依賴項：** 欄位標準定義、Google Sheets 結構、後續 pipeline 串接規格

**詳細文件：** [projects/maplab-master-data.md](./projects/maplab-master-data.md)

---

## Project 5: AI Reply System（自動回覆系統）

**目的：** 整理對話紀錄、建立回覆規則模組、支援客服與 Line OA 自動回覆

**主要 Agent：** A7 AI Reply System Agent

**主要 Repo：** maplab-ai-handbook（整合於本 repo）

**當前狀態：** 規則建立中，回覆模組草稿階段

**依賴項：** 對話紀錄來源、Line OA API、回覆規則分類標準

**詳細文件：** [projects/ai-reply-system.md](./projects/ai-reply-system.md)

---

## Relationship Map（系統依賴關係）

Handbook（治理層）連結所有專案。執行鏈由下往上：Master Data（資料底座）→ Pipeline（資料流動層）→ Detasys SEO/Ads（分析監控層）→ AI Reply System（知識應用層）。

---

## Current Priority（當前優先順序）

**Step 1.** 補齊 handbook 總控文件（README v2.0 完成、PROJECT_CONTEXT v1.0 完成、AI_WORKFLOW_MAP 待建）

**Step 2.** 對齊 Agent 啟動流程（AGENT_STARTUP_PROTOCOL 待建）

**Step 3.** 建立 Master Data 基礎結構

**Step 4.** 讓 Pipeline 與 Detasys 對齊命名規範與版本規則

---

*版本：v1.0 | 建立：2026-03-14 | 維護者：A1 Handbook Agent*
