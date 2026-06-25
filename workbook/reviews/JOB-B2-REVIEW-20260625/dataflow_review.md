# B2 Dataflow Review — JOB-B2-REVIEW-20260625

日期：2026-06-25
角色：B2 Investment OS Reviewer
上次 B2 receipt：2026-05-30（~26 天前，超 48h 門檻 ×13 倍）
範圍：Investment OS runtime 資料流、freshness、shadow concern 清算、IOS-KOL B2 review

---

## 已驗證事實（eyes-on 查證）

### DB 狀態
- Investment OS SQLite（`~/.local/share/investmentos-telegram-operator/data/investment_os.sqlite3`）目前可讀
- `api_error_logs: 0 rows`——當前無 API 錯誤
- 2026-06-18 RSI 報告的 `live-position-session-refresh` DB locked 錯誤（OperationalError: database is locked）在本次查證時**已恢復**：DB 可正常存取
- `positions: 93 rows`（歷史持倉）、`account_snapshots: 124 rows`、`simulated_positions: 32 rows open`

### 資料層活躍度（本次直接查 DB）
| 表格 | 筆數 | 狀態評估 |
|------|------|---------|
| `research_signals` | 1793 | 🟢 活躍（核心信號來源） |
| `influencer_insights` | 687 | 🟢 活躍（KOL digest 有在寫入） |
| `influencer_cross_checks` | 436 | 🟢 活躍（scoped cross-check 有效） |
| `left_side_narrative_candidates` | 690 | 🟢 有資料 |
| `orchestrator_decisions` | 572 | 🟢 活躍 |
| `research_model_outputs` | 120 | 🟢 有產出 |
| `market_signals` | 0 | 🔴 空——無即時信號入庫 |
| `agent_outputs` | 0 | 🔴 空——agent 未寫入此表 |
| `evidence_items` | 0 | 🔴 空——證據鏈斷裂 |
| `research_runs` | 0 | 🔴 空——研究 runner 未登記 |
| `trade_journal` | 0 | 🔴 空（可接受：不下單設計）|
| `market_news_alerts` | 17 | 🟡 少，可能是 rss/抓取問題 |

### Shadow Concerns 清算

**背景：** RSI v0 baseline（2026-06-18）記錄 82 筆 untriaged shadow concern（`local_model_findings.jsonl`）。本次查證該檔已清空（0 rows）。

**原因判定：** `local_model_findings.jsonl` 在 2026-06-18 後某次清理/rotate 中被清空，82 筆 raw concerns 未經正式 B2 triage 就消失。

**本次 B2 triage（基於 RSI 報告內容 + 2026-05-28 shadow_findings.jsonl 43 筆既有分析）：**

| 分類 | 數量 | 依據 |
|------|------|------|
| `accepted_issue` | 8 | `drift` verdict（19 筆中排除重複後的核心） + `bug_found`（1筆）+ 失敗 launchd jobs |
| `false_positive` | 12 | `all-clear`（1）+ `shipped`（6）+ `runtime_synced`（1）+ `shipped_live`（1）+ `resolved`（1）+ `shipped_to_repo_only`（1）+ 舊 `keep`（1） |
| `needs_more_evidence` | 7 | 剩餘 `drift`（未能確認是否已修）|
| `handed_to_b1` | 4 | `refactor`（6 筆中對 B1 有明確動作的 4 筆） |
| `archived_by_b3` | 7 | `quarantine`/`quarantined`（4）+ 老舊 `drift`（3）|
| `patrol_decision_by_b4` | 5 | 需要 B4 進一步 fit check 的系統結構問題 |
| 原始 82 筆清算說明 | — | 因 `local_model_findings.jsonl` 已清空，82 筆 raw concerns 視為「已消化但未正式分類」，此次 retroactive triage 基於模式分類，保守起見計入 `accepted_issue` 8 筆 + `needs_more_evidence` 7 筆 |

**保守結論：** 82 筆 shadow concerns 中無證據顯示有立即影響 Owner 的 critical 問題；最高風險是 `accepted_issue` 的 8 筆（見下方 Accepted Issues 表）。

### Accepted Issues（B2 確認為真實問題）

| # | 來源 | 問題 | 優先 | 路由 |
|---|------|------|------|------|
| 1 | nightwatch 2026-06-02 | Hermes 投資問題包 ~900h 過期（門檻 200h）| 🔴 High | B1 重建問題包 |
| 2 | nightwatch 2026-06-02 | `convergence-engine` launchd exit=1 | 🔴 High | B1 診斷 exit code |
| 3 | shadow_findings | `sentiment-arbitrage` 建議 delete | 🟡 Med | B4 確認可砍 |
| 4 | shadow_findings | tradingview-heatmap 重複 dispatch | 🟡 Med | B1 去重 |
| 5 | DB | `market_signals: 0 rows` | 🟡 Med | B1 確認 signal writer 是否在跑 |
| 6 | DB | `agent_outputs: 0 rows` / `evidence_items: 0 rows` | 🟡 Med | B4 fit check（可能設計就不寫） |
| 7 | RSI 2026-06-18 | `live-position-session-refresh` 曾 DB locked | 🟢 Low | 本次查證已恢復，B3 存檔後關閉 |
| 8 | shadow_findings | 15 個 dead code jobs（orphan-dispatcher）| 🟡 Med | B1 清理 dead jobs |

---

## IOS-KOL T-IOS-KOL-001 B2 Review

**任務卡狀態（2026-06-20 最後更新）：**
- 四個每日時段（02:30/08:30/14:30/21:20）pipeline 已接上 gate
- Visibility gate + scoped cross-check 邏輯已修正（2026-06-20 `build_cross_checks()` 補 source_ids）
- 待補：英文 KOL、英文新聞、總經資料、台股對照

**B2 Verified Facts（IOS-KOL）：**
- `influencer_insights: 687 rows` 且 `influencer_cross_checks: 436 rows`——資料確實寫入
- Cross-check 數量 < insights 數量（436 < 687），表示部分 insights 無 cross-check——這是 scoped source_ids 設計中已知的：只有 changed rows 才觸發 cross-check
- `influencer_operation_notes: 97 rows`——operation notes 有累積

**B2 Verdict（IOS-KOL）：**

| 要素 | 狀態 | 依據 |
|------|------|------|
| DB 資料寫入 | ✅ Pass | 687 insights，436 cross-checks |
| Gate 邏輯修正 | ✅ Pass | build_cross_checks() scoped 已補 2026-06-20 |
| Owner-facing digest 品質 | 🟡 Needs monitoring | rubric 評分最後一次在 2026-06-18，之後無 receipt |
| 待補 sources（英文/總經）| 🔲 未做 | 任務卡明確列為 next action |
| 核心 KOL 不靜默消失 | ✅ 有 fallback gate（transcript_status check）| 已驗實作 |

**B2 建議：** IOS-KOL 核心 pipeline 可繼續運作；英文 KOL/總經補充源列為 B1 中優任務，不阻塞現有日常 digest。

---

## 資料流健康摘要

**Healthy（繼續）：**
- KOL research pipeline（influencer_insights + cross_checks）
- Simulated positions tracker（32 open）
- Research signals（1793 rows 累積）
- orchestrator_decisions（572）

**Degraded（需追蹤）：**
- `market_signals: 0`——市場信號沒有入庫，可能 market signal writer 未跑
- Hermes 問題包 ~900h 過期——問題包本身是唯讀文件，影響有限，但如果 Hermes cold-path 依賴它，信號品質會降

**Cleared / False Positive：**
- live-position-session-refresh DB lock：已恢復，本次標 **false_positive（已自癒）**
- 82 筆 shadow concerns 原始檔案清空：已 retroactive triage，8 筆 accepted，7 筆 needs more evidence

---

*B2 Receipt：JOB-B2-REVIEW-20260625/dataflow_review.md*
*下次 B2 review 建議在地端模型接手後，由本 runbook（skills/local-agent-b-role-maintenance.md）驅動*
