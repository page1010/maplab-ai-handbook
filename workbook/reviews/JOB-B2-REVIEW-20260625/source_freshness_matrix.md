# Source Freshness Matrix — B2 2026-06-25

> 每個資料來源的新鮮度評估。B2 輸出，地端模型可用此格式自動更新。

| Source | 類型 | 門檻 | 上次已知更新 | 估計過期天數 | 狀態 | 負責 |
|--------|------|------|------------|-------------|------|------|
| Hermes 投資問題包 | 文件 | 200h | 2026-05-18 | ~900h / 37.5天 | 🔴 CRITICAL | B1 |
| convergence-engine launchd | job | 24h | 2026-06-02（exit=1）| 23天 | 🔴 CRITICAL | B1 diagnose |
| fb-shadow-refresh launchd | job | 24h | 2026-06-02（exit=126）| 23天 | 🔴 CRITICAL | B1 check auth |
| hermes-nightly-prep launchd | job | 48h | 2026-06-02（exit=2）| 23天 | 🔴 CRITICAL | B1 |
| left_side_narratives | 文件 | 72h | 2026-06-02 nightwatch 顯示 94h 過期 | 23天+ | 🔴 CRITICAL | B1 |
| influencer_insights DB | table | 48h | 最近有資料（687 rows，cross-checks 436）| 假設 <48h | 🟢 OK | 持續 |
| simulated_positions | table | 7天 | 2026-06-22 有 commit（B1 runner）| 3天 | 🟢 OK | 持續 |
| research_signals | table | 7天 | 不明，但 1793 rows 存在 | 未知 | 🟡 Needs verify | B2 next |
| nightwatch latest.md | 文件 | 24h | 2026-06-02 | 23天 | 🔴 CRITICAL（nightwatch 本身沒在跑）| B1 |
| shadow_findings.jsonl | 文件 | 7天 | 2026-05-28 | 28天 | 🔴 CRITICAL（最後一次 5月底）| B1/B4 |
| local_model_findings.jsonl | 文件 | 24h | 清空（2026-06-18 後被 rotate）| N/A | ⚪ Cleared | B3 archive |
| MAPLAB review bundles (B1-B4) | 文件 | 48h | B2: 2026-05-30, B3: 2026-05-30, B4: 2026-05-30 | ~26天 | 🔴 CRITICAL（本次解除）| B2-B4 本次 |
| T-IOS-KOL-001 task card | 文件 | 7天 | 2026-06-20 | 5天 | 🟢 OK | IOS-KOL |
| B4-RADAR-RECOVERY | 文件 | N/A | 2026-06-06 | — | 🟡 參考 | B4 |
| Investment OS DB (SQLite) | 資料庫 | 即時 | 2026-06-25（本次查證可讀）| 0 | 🟢 OK | — |

## 地端模型更新規則

此矩陣設計給地端模型定期更新（每日或每週一次）：
1. 讀 `reports/nightwatch/latest.md` → 更新所有 launchd job 欄
2. 查 SQLite DB → 更新 table 欄
3. `ls -la workbook/reviews/JOB-B2-*/` → 更新 B2 receipt 欄
4. 若有欄位超過門檻 → append 一行到 `workbook/hermes/patrol/latest.json` 的 `alerts` 陣列

地端模型**不需要讀懂 concern 語義**，只需要比較「上次更新時間」vs「門檻」，超過就標 🔴。
