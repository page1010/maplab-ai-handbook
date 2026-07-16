# Investment OS 異常積壓處理報告
**派工**: A0 緊急派工 2026-07-16　**執行**: A1 系統總管　**完成**: 2026-07-16 19:55 TW

---

## 1. 最新曝險摘要（2026-07-16 19:42 TW，yfinance live）

### 帳戶總覽
| 帳戶 | Gross | Equity | Debt | 斷頭風險 |
|------|-------|--------|------|---------|
| 🛟 外幣帳（公司股票） | $131,444 | $131,444 | $0 | NONE（純現金） |
| ⚡ 主帳 (Firstrade) | $154,164 | $77,513 | $76,652 | BP $24,112 (31.11%) |
| 🛟 文心直接戶（台股現股） | $67,842 | $67,842 | $0 | NONE（純現金） |
| **合計** | **$353,450** | **$276,799** | **$76,652** | 家庭槓桿 1.28x |

**最差情境回撤**: -$170,524 (-46.1%)

### 跨帳戶集中度
| 指標 | 2026-06-29 (CRITICAL) | 2026-07-16 現況 | 趨勢 |
|------|----------------------|-----------------|------|
| 🇺🇸 US 科技/半導體 | 82.3% | **82.9%** | 🔴 略微惡化 (+0.6%) |
| Firstrade BP | $371.94 (0.54% equity) | **$24,112 (31.11%)** | 🟢 大幅緩解 |
| MC 距離（斷頭） | 8.1% | **23.5%** | 🟢 大幅緩解 |
| SOP4 黑天鵝閘門 | 🔴 觸發 | ✅ 未觸發 | 🟢 緩解 |

### 主要持倉價格變動（07-01 → 07-16）
| 股票 | 07-01 | 07-16 | 變動 |
|------|-------|-------|------|
| TSLA | $420.60 | $394.46 | -6.2% |
| ONTO | $378.45 | $304.73 | -19.5% |
| NVDA | $200.09 | $212.50 | +6.2% |
| AMD | $580.91 | $529.14 | -8.9% |
| AMAT | $723.00 | $579.43 | -19.9% |
| MKSI | $444.80 | $353.80 | -20.5% |
| VSH | $53.78 | $40.45 | -24.8% |
| MU | $1,154.29 | $904.28 | -21.7% |

> ⚠️ 半導體設備 / Analog 類股顯著回調，US半導體集中度結構性偏高仍待Owner決策。

---

## 2. 06-29 CRITICAL 比對結論

### ✅ 已緩解（條件不再成立）
1. **Firstrade 保證金近零** (239b270a)：$371.94 → $24,112 (+6,382%)，斷頭距離 8.1% → 23.5%。Owner 可能已減碼或注資。
2. **SOP4 黑天鵝閘門觸發** (22888832)：因 BP 恢復，SOP4 閘門已關閉（目前 SPY day_chg +0.4%）。

### 🔴 持續 CRITICAL（結構性）
- **US 科技/半導體跨帳集中度 82.9%** — 未解，Owner 需決策是否調整。

### 🟡 持續 WARNING（結構性，Owner 已知）
- SOP1 主題超限（Speculation/Narrative 25.9%、EV/Auto 25.8%、SemiEquip 17.7%等）
- SOP2 TSLA 25.8% > 25% 核心上限（需減 $3,535）
- SOP2 3296 17.2% > 15% 非核心上限（需減 $9,438）
- 文心帳 3296 勝德 99.4% 單名集中

---

## 3. 佇列衛生處理結果

**處理前**: 41 筆 open（含 3 筆已 resolved）  
**處理後**: 13 筆真實 open，28 筆新標 resolved，3 筆維持 resolved

| 類別 | 數量 | 說明 |
|------|------|------|
| 條件已清 → resolved | 2 | margin_near_call(239b270a), SOP4(22888832) |
| 重複開單 → resolved | 26 | 同一 23 秒內重複觸發（07-01 16:09:36 vs 16:09:59） |
| 真實 open（結構性） | 13 | 集中度/SOP breach，待Owner決策 |

**dispatch_draft e8837ba2.md** (台股日線落後 2026-06-27)：queue 內已 resolved (afc04d96/e8837ba2/5bfdf658)，三筆日線問題均已在 06-27 當天標 resolved。

---

## 4. 呈報管線修復

### 根因
`calc_exposure_ledger.py` → `maybe_escalate()` 只寫 JSONL，依賴 19:30 launchd 鬧鈴 → 鬧鈴因 Claude Code session tool gap 空跑 → CRITICAL 異常悶 2.5 週無人知曉。

### 修復
- **source**: `/Users/pagemacmini/Documents/New project/scripts/calc_exposure_ledger.py`
- **deployed**: `/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/calc_exposure_ledger.py`
- 兩個版本均已加入 `_notify_owner_critical()` 函數
- CRITICAL anomaly 產生時立即呼叫 Telegram API（不等鬧鈴）
- Credentials: 讀 `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` env var，fallback 讀 `ROOT/.env`

### 實測驗收
```
Testing _notify_owner_critical with 1 fake CRITICAL...
  [notify] Telegram push OK (1 CRITICAL)
Done.
```
✅ 假 CRITICAL `test_critical_notify_pipe` 推播成功，測試 entry 已移除（僅測試，未寫入 queue）。

---

## 5. pitfalls 記錄

已 append `/Users/pagemacmini/Documents/New project/pitfalls.md` **錯誤 185 — 監控管道失效 = 盲區，異常悶 2.5 週無人呈報（2026-07-16）**。

Fallback 建議（尚未實作，供 Owner 決策）：
- launchd plist 加 `TELEGRAM_BOT_TOKEN` env var → 鬧鈴也能直接推播
- `maybe_escalate()` 加去重邏輯（open queue 已有相同 routing_key 則跳過）

---

## 6. Owner 決策清單（按優先序）

1. 🔴 **CRITICAL: US 半導體 82.9% 集中度** — 結構性，07-01→07-16 略微惡化；是否啟動再平衡計畫？
2. 🟡 TSLA 兩帳合計 25.8% > 25% 上限，需減碼 ~$3,500（TSLA 07-16 已回落至 $394.46）
3. 🟡 3296 勝德 17.2% > 15% 上限，需減碼 ~$9,438 TWD 等值
4. ℹ️ HPE/SRFM qty 未填，建議 Owner 補 `real_holdings.yaml`
5. ℹ️ market_regime=UNKNOWN（DB 無 external_market_snapshots 表），考慮補 VIX/QQQ 源

---

_A1 系統總管 2026-07-16 19:55 TW_
