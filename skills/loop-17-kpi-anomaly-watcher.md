---
# Skill: Loop-17 KPI 異常監看（A6 報價轉換率版）

> 來源：Fable5 Loop 工作流 #17，2026-07-07 Owner 指示接入 MAPLAB
> 用途：每日自動讀 Sheets 報價數據，偵測異常，主動推送 Telegram 警報

---

## Goal（停止條件）

```
GOAL: A6 報價轉換率持續 7 天在基線 ±20% 內，且無超時未跟進的報價單
STOP: 連續 7 天 0 異常，或業務已進入淡季（Owner 手動暫停）
```

## 監看指標

| 指標 | 基線 | 警報閾值 | 說明 |
|------|------|---------|------|
| 報價單轉換率 | 待觀察期建立 | 基線 ±20% | 成交 / 報價總數 |
| 報價回應時間 | < 2h | > 4h | 超時未回客戶 |
| 報價單量 | 7天滾動均值 | 均值 -40% | 需求急降警報 |
| 高價方案佔比 | 待觀察期建立 | < 10% 連續 3 天 | 客單價下滑 |

## Loop 迭代邏輯

每日 08:00 執行：
1. 用 Sheets MCP 讀報價 Sheets（A6 業務數據頁）
   ```
   Sheets ID: 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
   分頁：A6 報價數據 / Task Board
   ```
2. 計算當日指標（轉換率、回應時間、單量）
3. 與 7 天滾動基線比較
4. 偵測異常 → 分級：
   - 🟡 WARNING：單一指標超閾值
   - 🔴 ALERT：多指標同時異常
   - ⛔ CRITICAL：轉換率腰斬 (>50% 下滑)
5. 正常 → 靜默（不推送）
6. 異常 → Telegram 推送警報

## 執行指令

```bash
# 手動觸發
bash scripts/loop_17_kpi_anomaly.sh

# launchd 每日 08:00 自動執行
# plist: launchd/com.maplab.loop-17-kpi-anomaly.plist
```

## 警報格式

```
【Loop-17 KPI 警報】🔴 ALERT 2026-07-07 08:05
---
異常指標（2個）：
- 報價轉換率：今日 18% vs 基線 32%（↓44%）
- 報價單量：今日 3 筆 vs 7日均值 8 筆（↓62%）
---
可能原因（自動推斷）：
- 週末效應（今日星期日）
- 旺季結束（6月婚宴高峰後）
---
建議行動：
→ A6：確認未回覆報價單是否有堆積
→ A3：廣告轉換率是否同步下滑？
---
GOAL 進度：連續達標 0 天（目標 7 天）
```

## 觀察期設置（首次啟動）

首次啟動需要 14 天觀察期建立基線：
```bash
# 初始化基線（讀歷史 Sheets 數據）
bash scripts/loop_17_kpi_anomaly.sh --init-baseline
```

輸出：`state/loop_17_kpi_baseline.json`

## 路由策略

- Sheets 數據讀取 → Sheets MCP
- 指標計算 → bash + python（不用 Claude）
- 異常原因推斷 → Hermes/gemma4（pattern-match 季節/週期）
- 🔴 CRITICAL 異常 → 升級 Claude Sonnet 做深度分析

## 整合點

- 輸出：`state/loop_17_kpi_daily.json`（每日覆蓋）
- 歷史：`state/loop_17_kpi_history.jsonl`（追加）
- 基線：`state/loop_17_kpi_baseline.json`（14天更新一次）
- 觸發 A6：發現超時未跟進報價單 → 自動推送提醒

## Sheets MCP 呼叫範例

```python
# 讀 A6 報價數據
data = mcp__google-sheets__get_sheet_data(
    spreadsheetId="1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg",
    range="A6報價數據!A:Z"
)
```
