# Telegram Multi-Agent Router (A6 Proxy)

本文件描述了 Telegram 機器人（A6 介面）如何將任務動態分派給不同地端 Agent，並統一將結果回傳給使用者的路由架構。

## 架構概念

A6 不再只是單一的對話機器人，而是成為使用者手機端操作地端多智能體（Multi-Agent）的「單一通訊總機」。

使用者藉由切換「操作模式（Mode）」或下達特定前綴指令，A6 會將請求分配給對應專長的 Agent，並透過 `OpenClawAdapter` 喚醒地端的無限算力池執行任務。

## Mermaid 流程圖

```mermaid
flowchart TD
    User([Owner / Sales]) -- 透過 Telegram 傳訊 --> A6[A6 Bot \n (通訊總機)]

    subgraph A6 Router [A6 Router Logic]
        A6 -->|Mode == Quote| A5(A5 報價與提案引擎)
        A6 -->|Mode == SEO| A2(A2 Ads SEO Patrol)
        A6 -->|指令 == /a1| A1(A1 System Orchestrator)
        A6 -->|Mode == Chat| Base(OpenClaw / Hermes 一般對話)
    end

    A5 -->|觸發| GAS[Google Apps Script \n (Sheet / Slide)]
    A2 -->|撰寫 / 審查| WP[WordPress / SEO 庫]
    A1 -->|遠端控制| OS[Mac OS / 其他 Agent]

    GAS -- 報價單網址 --> A6
    WP -- SEO 草稿內容 --> A6
    OS -- 執行結果 / 截圖 --> A6

    A6 -- 回傳結果 --> User
```

## Agent 角色與職責對應

| Agent | 角色全稱 | Telegram 進入點 | 核心能力 / 輸出 |
|---|---|---|---|
| **A6** | Line Quote Assistant (Telegram 版) | 預設對話介面 | 作為通訊中樞、分配流量與處理無狀態日常對答。 |
| **A5** | Quote Engine | 點擊 `🧾 報價模式` <br> 或輸入 `報價...` | 提供報價建議，並呼叫 GAS 自動產生 Google Sheet 與 Slide 報價單。 |
| **A2** | Ads SEO WordPress Patrol | 點擊 `📝 召喚a2seo文章編輯` | 提供符合 MAPLAB Brand Voice 與 SEO 指南的專文撰寫與 WordPress 檢查。 |
| **A1** | System Orchestrator | （已實作）輸入 `/a1 run ...` 或 `/a1 paste ...` | 遠端控制本機電腦、跨 Agent 對話貼文、執行 Terminal 指令或修正 Bug。 |
| **Base** | OpenClaw / Hermes | 點擊 `💬 聊天模式` | 一般對話與系統備援。支援利用 Browser Bridge 進行跨視窗對話與貼文工具呼叫。 |

## 資料流與持久化

所有透過 A6 分派給 A5, A2, A1 的任務，底層都會透過 `OpenClawAdapter` 執行。這意味著：
1. 每個獨立任務都會在 `workbook/reviews/JOB-xxx` 產生完整的 `TaskExecution` 紀錄（包含 `output.json`, `execution_log.json`）。
2. 在地端執行的軌跡，能完整受到系統架構的保存與監控，達成 100% 觀測性。
