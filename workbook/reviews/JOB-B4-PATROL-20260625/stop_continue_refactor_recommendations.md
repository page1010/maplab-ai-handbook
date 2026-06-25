# B4 Stop / Continue / Refactor 建議 — 2026-06-25

B4 RSI 判定：v0.1（degraded，~55 est）
前次判定：v0 baseline（broken，44）
趨勢：+11，但仍未過 70 門檻（working）

---

## Continue

| 項目 | 理由 |
|------|------|
| IOS-KOL 4 時段 digest | 核心 pipeline OK；gate 有效；Owner 在用 |
| Simulated positions tracker | B1 最近有 commit（2026-06-22）；不下單設計正確 |
| B1-B4 RSI loop 框架 | 架構正確，問題是執行頻率；框架本身不需改 |
| Investment OS SQLite（讀寫）| DB 健康，0 api_error_logs |
| A1 每日 patrol（改地端後）| 見 Part 2 SOP，MAPLAB patrol 繼續 |
| B-role 地端模型接手計畫 | 本次主要交付，往 Pro 化方向走 |

## Pause

| 項目 | 理由 | 恢復條件 |
|------|------|---------|
| Hermes cold-path 擴展 | 問題包 900h 過期，基礎失效 | B1 重建問題包 + 驗證 cold-path 可用 |
| IOS-KOL 英文源補充 | 非阻塞核心 digest；先穩定中文 KOL | 核心 digest 連續 7 天 gate 通過 |
| B-role RSI v1 升級（自動日報）| 分數 degraded 不宜加功能 | RSI 分數 > 70（working） |
| shadow review pipeline 重啟 | 不清楚 local_model_findings.jsonl 為何清空 | B1 確認清空原因 + pipeline 還在跑 |

## Refactor / Remove

| 項目 | 行動 | 負責 | 優先 |
|------|------|------|------|
| convergence-engine launchd（exit=1）| 診斷：exit code 意義、是否需要 | B1 | High |
| 15 個 dead code jobs | orphan-dispatcher shadow_findings 建議 refactor → 確認後清理 | B1 | Med |
| sentiment-arbitrage | shadow_findings 建議 delete → B4 確認後 B1 執行 | B4→B1 | Med |
| nightwatch 自動化 | latest.md 停 2026-06-02 → 若 job 失效就重啟或換 shell script | B1 | High |
| local_model_findings.jsonl rotate 機制 | 搞清楚誰在 rotate、rotate 前是否 B2 triage | B1 調查 → B2 gate 確立 | Med |

---

## RSI Continue / Pause / Refactor 正式判定

**B4 判定（2026-06-25）：**

| 層次 | 判定 | 理由 |
|------|------|------|
| B-role loop 本身 | **CONTINUE** | 結構正確，本次清算已恢復 receipt；地端模型接手後可維持頻率 |
| Investment OS 研究功能 | **CONTINUE（核心）+ PAUSE（擴展）** | KOL/模擬倉 continue；英文源/Hermes 擴展 pause |
| 問題修復 | **REFACTOR FIRST** | Hermes 問題包、convergence-engine、nightwatch 是前置修復；不修就不加功能 |
| 地端模型接手 | **START NOW** | RSI degraded 狀態下正是換地端接常規維護的好時機；省 Claude token 投入真正需要推理的問題 |

**下一個 B4 patrol 目標：** RSI 分數 > 70（working）
**達成條件（3 項中 2 項）：**
1. Hermes 問題包更新 < 200h
2. convergence-engine launchd 不再 exit=1
3. B-role receipt 間隔 < 7 天（地端模型接手後）

*B4 Receipt：JOB-B4-PATROL-20260625/stop_continue_refactor_recommendations.md*
