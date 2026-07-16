<!-- receipt: TG-DISPATCH-20260714-CODEX-AGY-R04R05R10 / JOB-R10 / completed -->
# R10 — Investment OS 角色整合全貌（B1）

> 執行者：A1（Codex null，A1 直接執行）  
> 完成日期：2026-07-16  
> 資料來源：T-B1-B4-investment-os-role-split.md, T-B1-001.md, projects/b5-shadow-capability-distillation.md, projects/invest-os-strategy-role-system.md

---

## 1. IOS 目前有幾個角色？各角色主責一句話

### MAPLAB B 系列（執行層）— 5 個

| 角色 | 主責（一句話） |
|------|--------------|
| **B1** Investment OS Builder | 實作 IOS 功能、驗證資料流、輸出 implementation 交付物 |
| **B2** Investment OS Reviewer | 審核 B1 輸出的資料流正確性、錯誤分類、新鮮度評估 |
| **B3** Investment OS Archivist | 撰寫版本紀錄與交接文件、保存 RSI 趨勢歷史 |
| **B4** Investment OS System Patrol | 定期問「這套系統還適合嗎？」判讀 continue/pause/refactor |
| **B5** Shadow Capability Distillation | 把所有角色的複利產出蒸餾成地端模型可理解的教材 |

### IOS 策略層（跨 MAPLAB 獨立系統）— 8 個

| 角色 | 主責（一句話） |
|------|--------------|
| **IOS-KOL** | KOL 輸出品質管理與策略修正 |
| **IOS-MOMENTUM** | 動能訊號新鮮度維護 |
| **IOS-INVENTORY** | 實倉位風險清晰化 |
| **IOS-MACRO** | 宏觀牌卡正確性 |
| **IOS-ALPHA** | Polymarket 與跨來源 alpha 雜訊過濾 |
| **IOS-BLACKSWAN** | 黑天鵝訊號偵測 |
| **IOS-SURFACE** | Markdown/卡片版型跨策略一致性 |
| **IOS-HYGIENE** | Dirty worktree 清理與 keep/drop 決策 |

**總計：13 個活躍角色**（B1-B5 × 5 + IOS 策略層 × 8）

---

## 2. B1-B4 分工盲點（最多 3 個）

### 盲點 1：B2/B3 召喚頻率不足，RSI 閉環實際未運行

B1 已落地 RSI-like 成長機制（`tools/invest_os/b_role_recursive_self_improvement.py`），但驗收標準要求「用 scorer 證明紅燈變少、分數變高」——目前 B2 的 `raw finding 分類` 和 B3 的 `趨勢保存` 從未被觸發（只有 B1 在產出，沒有 B2/B3 消費）。

**後果**：RSI 形同虛設，沒有人在問「這輪比上輪更好嗎？」

### 盲點 2：B4 Patrol 沒有明確觸發條件

B4 定義為「定期問系統是否適合」，但「定期」沒有具體排程（沒有 cron，沒有 Hermes 觸發）。B4 只在 Owner 手動召喚時才執行，等同於沒有 patrol 機制。

**後果**：系統健康問題（如 Hermes null、OAuth 過期）只靠 A1 巡查，B4 角色冗余。

### 盲點 3：MAPLAB B 系列與 IOS 策略層之間缺乏路由協議

`projects/invest-os-strategy-role-system.md` 定義了 IOS 策略角色，但沒有說明「B1 發現問題後，如何知道要去找 IOS-KOL 還是 IOS-SURFACE？」——路由邏輯只寫在文件裡，沒有程式化的觸發機制。

---

## 3. B5 能力蒸餾進展與對其他角色的影響

**進展**：
- ✅ Owner 核准：2026-07-10
- ✅ 配套建立完成：2026-07-11（A1 執行）
  - `projects/b5-shadow-capability-distillation.md`（定義文件）
  - `AGENT_RULES.md` Section 1 加入 B5
  - `AGENT_RECALL_PROMPTS.md` 加入 B5 段落
  - `chrome-extension/task-modules/` 加入 B5 模組

**尚未啟動**：
- 首次能力盤點（`reports/capability-inventory/inventory_2026-07.md`）尚未執行
- 地端模型教材包（`packages/local-model-teaching/2026-07/`）尚未產出
- 召回品質審查（`reports/recall-quality/recall_quality_2026-Q3.md`）尚未排程

**對其他角色的影響**：
- B1-B4：B5 若啟動蒸餾，RSI 迴圈的輸出會有人評分，盲點 1 的問題可被發現
- A1：B5 的召回品質審查可接替 A1 部分文件稽核工作，減輕 A1 巡查負擔
- IOS 策略層：B5 可把 IOS 的踩坑與策略模式打包成 Ollama 可讀格式，是地端化的最大受益者

---

## 4. 整合優先序建議（3 條）

### ① 可自主執行 — 執行 B5 首次能力盤點

掃描 `skills/auto/`、`pitfalls.md`、`workbook/reviews/` 三個複利產出目錄，為每個新增能力打蒸餾評分（1-5），輸出 `reports/capability-inventory/inventory_2026-07.md`。

不需 Owner 授權，A1 或 B5 角色召喚即可執行。

### ② 可自主執行 — 給 B4 建立最小可用觸發條件

在 `scripts/` 中建立 `b4_patrol_trigger.sh`，每週執行一次系統適合性問卷（5 題），輸出結果 append 到 `state/b4_patrol_log.jsonl`。

沒有 Hermes/cron 也可以用 A1 週巡查時手動觸發。

### ③ 需 Owner 確認 — 決定 InnerFlowLab R06 停止後的 B 系列範圍

Owner 已確認 R06 InnerFlowLab 停止，但 `T-B1-001.md` 和 `T-B1-DASH-001.md` 裡有部分 InnerFlowLab 相關內容。

建議 A1 下次巡查時把 IFL 相關任務標記為 `❌ CANCELLED`，避免 B1-B4 未來召喚時產生混淆。

---

## 附：IOS 角色全景圖（簡版）

```
MAPLAB 系統
├── A 系列（業務執行）: A0~A8
└── B 系列（IOS + 系統成長）
    ├── B1 Builder        → 實作
    ├── B2 Reviewer       → 審查
    ├── B3 Archivist      → 存檔
    ├── B4 Patrol         → 系統健康
    └── B5 Distillation   → 能力固態化 → 地端模型

Investment OS（跨系統獨立）
├── IOS-KOL / MOMENTUM / INVENTORY / MACRO
└── IOS-ALPHA / BLACKSWAN / SURFACE / HYGIENE

跨系統路由：B1 發現問題 → invest-os-strategy-role-system.md 路由表 → 對應 IOS 角色
```
