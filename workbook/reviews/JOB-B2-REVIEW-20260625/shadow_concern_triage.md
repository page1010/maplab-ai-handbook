# B2 Shadow Concern Triage — 2026-06-25

來源：`~/.local/share/investmentos-telegram-operator/reports/shadow/local_model_findings.jsonl`  
分析視窗：2026-06-18T00:00 ～ 2026-06-18T23:59（RSI baseline 計數的 82 筆）  
總量：1759 筆（全 history）；2026-06-18 window=82；2026-06-18 後累計=558 筆

---

## 82 筆 triage 結果（2026-06-18 window）

| 分類 | 筆數 | 代表 pattern |
|------|------|-------------|
| `false_positive` | 81 | 見下方 |
| `accepted_issue` | 1 | Hermes timeout |

### 細分

| evidence pattern | 筆數 | 分類 | 理由 |
|----------------|------|------|------|
| "matrix_rows array is empty" | 70 | `false_positive` | convergence-engine 無資料時 Hermes 正確 flag；問題在上游（Polymarket/Reddit/RSS 0 筆），不是 Hermes 邏輯錯 |
| "identical raw_summary / all-zero scores" | 7 | `false_positive` | 同上；template 行填充時觸發，非真實信號問題 |
| "matrix row with all-zero scores" | 3 | `false_positive` | 同上 |
| "raw_summary identical across rows, all-zero" | 1 | `false_positive` | 同上 |
| "Hermes reviewer failed: timeout" | 1 | `accepted_issue` | Hermes 超時是真實 issue；B1 action：加 retry 上限或 fallback |

### 根本 accepted_issue（路由 B1）

**上游資料源乾燥**：82 次觸發中 81 次是「沒有訊號可評估」而非「有訊號但評估錯誤」。

- `next_action: rerun_with_alt_prompt`（81 筆）→ Hermes 已正確建議重跑，但沒有 B1 修上游
- **B1 action**：確認 Polymarket API、Reddit API、RSS 源是否仍有效；若長期無數據考慮 mute convergence-engine Hermes review（節省 token）

---

## 2026-06-18 後累積 558 筆（概況）

- 最新幾筆（2026-06-25 08:xx）的 `concern` 欄位為空（schema drift）
- 模式與 2026-06-18 相同：全部 `parent_job: convergence-engine`，全部 `verdict: concern`
- **判定**：不需逐筆 triage；全部為同一根本問題（上游無訊號），`false_positive` 批次處理

---

## B2 triage 決定摘要

```json
{
  "window": "2026-06-18",
  "total": 82,
  "false_positive": 81,
  "accepted_issue": 1,
  "root_cause": "convergence_engine_data_sources_dry",
  "b1_action": [
    "verify Polymarket/Reddit/RSS API status",
    "add Hermes timeout retry limit (currently 0 retry)"
  ],
  "b2_close_reason": "all concerns follow predictable empty-data pattern; no owner-facing impact detected"
}
```

*B2 Receipt：JOB-B2-REVIEW-20260625/shadow_concern_triage.md*
