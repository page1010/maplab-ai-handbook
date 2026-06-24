# Skill: IOS-SELL 持倉賣出訊號監控員

**觸發條件**：需要計算 RSI / MACD / MA 技術指標，或實作 IOS-SELL 賣出訊號邏輯時。

## 指標計算參考實作

### RSI(14)

```python
import pandas as pd

def calc_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def rsi_reversal(rsi: pd.Series, threshold: float = 70) -> pd.Series:
    """True on the bar where RSI crosses from >=threshold back below threshold."""
    return (rsi.shift(1) >= threshold) & (rsi < threshold)
```

### MACD(12,26,9)

```python
def calc_macd(prices: pd.Series,
              fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def macd_death_cross(macd: pd.Series, signal: pd.Series) -> pd.Series:
    """True on the bar where MACD crosses below signal line."""
    return (macd.shift(1) > signal.shift(1)) & (macd < signal)
```

### MA 死亡交叉(50/200)

```python
def calc_ma(prices: pd.Series, window: int) -> pd.Series:
    return prices.rolling(window=window).mean()

def ma_death_cross(prices: pd.Series,
                   short: int = 50, long: int = 200) -> pd.Series:
    """True on the bar where short MA crosses below long MA."""
    ma_short = calc_ma(prices, short)
    ma_long = calc_ma(prices, long)
    return (ma_short.shift(1) > ma_long.shift(1)) & (ma_short < ma_long)
```

### 組合觸發判斷

```python
def check_sell_alert(ticker: str, ohlcv_df: pd.DataFrame) -> dict | None:
    """
    Returns sell alert dict if all three signals trigger simultaneously,
    else returns None.
    ohlcv_df: columns = ['open','high','low','close','volume'], DatetimeIndex
    """
    close = ohlcv_df['close']

    rsi = calc_rsi(close)
    macd_line, signal_line, _ = calc_macd(close)

    last = ohlcv_df.index[-1]

    reversal = rsi_reversal(rsi).iloc[-1]
    death_cross_macd = macd_death_cross(macd_line, signal_line).iloc[-1]
    death_cross_ma = ma_death_cross(close).iloc[-1]

    if reversal and death_cross_macd and death_cross_ma:
        ma50 = calc_ma(close, 50).iloc[-1]
        ma200 = calc_ma(close, 200).iloc[-1]
        return {
            "ticker": ticker,
            "date": str(last.date()),
            "price": close.iloc[-1],
            "rsi": rsi.iloc[-1],
            "rsi_prev": rsi.iloc[-2],
            "macd": macd_line.iloc[-1],
            "signal": signal_line.iloc[-1],
            "ma50": ma50,
            "ma200": ma200,
        }
    return None
```

## 常見踩坑

| 問題 | 原因 | 解法 |
|------|------|------|
| MA200 全是 NaN | 資料少於 200 根 K 棒 | 確保至少取 250+ 根歷史資料 |
| RSI 觸發太頻繁 | 用 rsi < 70 而非穿越判斷 | 用 shift(1) 判斷穿越，不是當根值 |
| MACD 假訊號多 | 震盪行情 histogram 反覆正負 | 加上 histogram 斜率確認或等收盤確認 |
| 資料時區錯誤 | 台股 / 美股時區不同 | 統一轉成 UTC，顯示時再轉本地時間 |

## 邊界提醒

- 這些計算**不構成買賣建議**
- 三指標同時觸發是告警條件，不是「必須賣出」指令
- Owner 自行判斷是否採取行動
- B1 負責實作程式碼，IOS-SELL 負責執行與告警

## 相關文件

- `projects/ios-sell-signal-monitor.md` — 角色規格與參數設定
- `recalls/IOS-SELL_recall.md` — 角色 recall prompt
