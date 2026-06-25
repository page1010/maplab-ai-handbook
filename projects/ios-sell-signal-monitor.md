# IOS-SELL：Position Sentinel（實單哨兵）

## 角色定位

**角色 ID**：IOS-SELL  
**角色名稱**：Position Sentinel（實單哨兵）  
**系列**：IOS-* 觀測/告警角色（非 builder 系列）  
**建造者**：B1 Investment OS Builder  
**版本**：v1.0，建立於 2026-06-24

## 核心職責

監控 Owner 實際持倉，計算技術指標（RSI / MACD / MA），當三個指標**同時出現賣出訊號**時，透過 Telegram 通知 Owner。

**不做的事**：下單、模擬單、主觀買賣建議、操作券商 API。

## 邊界說明（與 B1-B4 的區別）

| 角色 | 性質 | 職責 |
|------|------|------|
| B1 Builder | 建造者 | 建立 / 維護 IOS-SELL 的程式碼與規格 |
| B2 Reviewer | 審查者 | 審查輸出品質與訊號準確性 |
| B3 Archivist | 存檔者 | 儲存歷史告警紀錄 |
| B4 Patrol | 巡邏者 | 系統健康巡檢，包含此角色是否正常運行 |
| **IOS-SELL** | **觀測/告警** | **計算指標、判斷觸發、送 Telegram 通知** |

IOS-SELL 是「觀測+通知」角色，不是 builder。它讀取資料、運算、推播，不修改系統也不下決策。

## 技術指標規格

### RSI(14) 超買反轉

- 週期：14 根 K 棒（可由 Owner 調整）
- 觸發條件：前一根 RSI >= 70 且本根 RSI < 70（確認穿越，避免假訊號）
- 公式：RSI = 100 - 100/(1 + RS)，RS = avg_gain/avg_loss over N periods

### MACD 死叉 (12,26,9)

- 快線 EMA：12 期
- 慢線 EMA：26 期
- Signal line：MACD 的 9 期 EMA
- 觸發條件：前一根 MACD > Signal 且本根 MACD < Signal（death cross）

### MA 死亡交叉 (50/200)

- 短均線：MA50（50 日均線）
- 長均線：MA200（200 日均線）
- 觸發條件：前一根 MA50 > MA200 且本根 MA50 < MA200

### 組合觸發邏輯

```python
SELL_ALERT = (
    rsi_reversal        # RSI 從 >=70 跌回 <70
    and macd_death_cross  # MACD 線穿越 Signal 線向下
    and ma_death_cross    # MA50 穿越 MA200 向下
)
# 三者必須在同一根 K 棒（或同一個掃描週期）同時成立
```

## 資料來源

- 持倉清單：由 IOS-INVENTORY 角色或 Owner 手動提供（CSV / JSON）
- 歷史 OHLCV：優先使用 Investment OS 已建立的資料管線
  (`/Users/pagemacmini/Documents/New project`)
- 計算由 B1 在 Investment OS session 實作，IOS-SELL 讀取計算結果

## 輸出規格

### Telegram 告警訊息

```
[SELL ALERT] IOS-SELL 賣出訊號告警
股票：{ticker} | 現價：NT${price}（{pnl_pct:+.1f}%）

三指標同時觸發：
RSI(14) = {rsi:.1f}（從 {rsi_prev:.1f} 穿越回 <70）
MACD 死叉（MACD={macd:.4f}, Signal={signal:.4f}）
死亡交叉（MA50={ma50:.1f} 跌破 MA200={ma200:.1f}）

此為技術面訊號，由 Owner 自行判斷是否賣出。
時間：{datetime} | IOS-SELL v1.0
```

### 工作目錄輸出

```
workbook/reviews/JOB-IOS-SELL-YYYYMMDD/
  signal_report.md        # 本次掃描結果與觸發詳情
  position_scan_summary.md  # 所有持倉的指標狀態快照
  review_request.md       # B2 審查請求（若需要）
```

## 參數設定（Owner 可調整）

| 參數 | 預設值 | 說明 |
|------|--------|------|
| RSI 週期 | 14 | 可調整為 9/21 |
| RSI 超買門檻 | 70 | 可調整為 65/75 |
| MACD 快線 | 12 | 標準設定 |
| MACD 慢線 | 26 | 標準設定 |
| MACD Signal | 9 | 標準設定 |
| MA 短線 | 50 | 可調整為 20/100 |
| MA 長線 | 200 | 可調整為 100 |
| 掃描頻率 | 每日收盤後 | 可調整為盤中定時 |

## 實作狀態

- [x] 角色定義文件（本文件）
- [x] Recall prompt (`recalls/IOS-SELL_recall.md`)
- [x] Skill book (`skills/ios-sell-signal-monitor.md`)
- [x] Chrome Extension task module (`chrome-extension/task-modules/IOS-SELL.json`)
- [ ] 指標計算實作（由 B1 在 Investment OS session 建立）
- [ ] Telegram 推播整合（依賴 Investment OS 資料管線）

## 相關文件

- `recalls/IOS_strategy_role_recall.md` — 通用 IOS 角色 recall
- `recalls/IOS-SELL_recall.md` — IOS-SELL 專屬 recall
- `skills/ios-sell-signal-monitor.md` — 技術指標計算指引
- `projects/invest-os-strategy-role-system.md` — IOS 角色系統總覽
