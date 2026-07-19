# Local Model Evolution — Cycle 1 Report

> 日期：2026-07-19 ｜ 執行者：A1 / Local Model Evolution Orchestrator
> 分支：`claude/local-model-evolution-orchestrator-puvj7d` ｜ 依據：Draft PR #20
> `LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md`（已 merge 進本分支）

## Runtime Capability Report

執行環境是 A1 remote cloud 沙盒，**不是 Owner 訊息中提到的 Mac mini Remote Codex**。
`command -v` 逐項檢查結果：

| 能力 | 結果 |
|---|---|
| MAPLAB repo | ✅ `/home/user/maplab-ai-handbook`，branch `claude/local-model-evolution-orchestrator-puvj7d` |
| Investment OS repo | ✅ clone 於 `/workspace/investment-os`（shallow, 未 push 回該 repo） |
| python3 | ✅ 3.11.15，含 pyyaml |
| Ollama | ❌ 未偵測到，本沙盒無法驗證 Mac mini 上實際的地端模型清單 |
| Codex CLI | ❌ 未偵測到 |
| Claude CLI | ✅ `/opt/node22/bin/claude`（Claude Code CLI 本身，非額外訂閱端點） |
| Gemini / Antigravity | ❌ 未偵測到 |
| Hermes | ❌ 未偵測到 |
| Google Drive/Sheets | ⚠️ 未測試（本輪未呼叫 MCP，因為不需要即時營運資料） |
| SQLite | ❌ 未偵測到 `sqlite3` 指令 |
| launchd / scheduler | ❌ 不適用（Linux 沙盒，非 macOS） |
| Training framework (LoRA/peft) | ❓ 未盤點，無法在此環境驗證，Mac mini 實際狀況未知 |
| Missing capabilities | Ollama、Codex CLI、Antigravity、Hermes、SQLite、launchd 全部需要在 Mac mini 上重新盤點 |
| Safety boundaries confirmed | ✅ 已讀 `docs/company-values.md`、`docs/governance/unattended-run-safety.md`、
  investment-os `docs/SECURITY_BOUNDARIES.md`，本輪未觸碰任何 secrets、未下真實委託、
  未發布 SEO/改 Ads、未自動回覆客戶、未 merge main |

## Quota Sentinel Dry-Run

`local_model_evolution/bin/quota_sentinel.py` 已建立並執行成功，輸出見
`../state/provider_status.json`。摘要：

| provider | surface | status | confidence |
|---|---|---|---|
| claude | subscription_cli | available（此沙盒內，非 Mac mini 訊號） | estimated |
| claude | api | blocked_by_policy | unknown |
| openai_codex | subscription_cli | unknown（沙盒無 CLI） | unknown |
| openai_codex | api | blocked_by_policy | unknown |
| gemini | app_ui | unknown（無機器可讀來源） | unknown |
| gemini | api | blocked_by_policy | unknown |
| ollama_local | local_process | unknown（沙盒無 ollama） | unknown |

**治理發現**：`docs/governance/model-tier-policy.md` §0 禁止任何按量 API key，
所以三個高成本 provider 的「official_api」層在 MAPLAB 現行政策下預設
`blocked_by_policy`，已寫入 `config/providers.yml`。這比原始 prompt §六 描述的
「排序最後」更嚴格——不是「盡量避免」，是「預設關閉，需要 Owner 書面例外」。

Safe reserve：15%（`config/providers.yml` 全域設定）。

## 兩個 P0 Curriculum

| Curriculum | Eval cases | 狀態 |
|---|---|---|
| Investment report/current-state | 24 | dataset_ready（eval only），去識別化合成 ticker |
| SEO ranking/keyword | 24 | dataset_ready（eval only），去識別化合成關鍵字/頁面 |

詳見 `../curricula/*/CURRICULUM.md`。

## Baseline Eval

**真實地端模型 baseline：BLOCKED**（此沙盒無 Ollama）。已完成的是
**eval harness 自我測試**：用手寫、明確標記為 fixture（非真實模型輸出）的
outputs.jsonl 驗證 `bin/eval_harness.py` 的每一類 validator 真的會抓到對應錯誤。

## 前三大錯誤類型（harness 自我測試結果，非模型診斷 — 見下方警語）

Investment（自我測試）：`stale_source_treated_as_fresh`(4)、
`guessed_instead_of_declining`(4)、`ticker_contamination`(2)。

SEO（自我測試）：`action_card_incomplete`(4)、
`historical_rank_treated_as_today`(4)、`keyword_page_mapping_error`(2)。

> ⚠️ 這些數字證明 harness 邏輯正確，**不代表** Mac mini 上任何真實 T3 模型
> 會犯這些錯誤。真正的前三大錯誤類型必須等 Mac mini 上跑出真實 `outputs.jsonl`
> 後才能算出，見 `../evals/baseline_report.md` 的下一步指令。

## 第一版改善方案（待真實 baseline 後才能定案，本輪只給方法論）

依 §十一 Level A 優先：先查是否能用 prompt template（把十欄格式與拒絕補猜規則
寫進系統提示）、skill/SOP（把 ticker/period 隔離規則寫成強制檢查清單）、
metadata hard filter（在轉接腳本裡強制 sample 的 ticker/period 與輸出比對，
不通過就攔截重試）解決，再考慮教師蒸餾樣本，最後才考慮 LoRA。

## 一週 MVP

見 `../RUN_PLAN.md` 「一週 MVP」章節：Day1 Mac mini quota 重跑 + 補讀治理文件
→ Day2-3 建轉接腳本+跑真實 baseline → Day4 Level A 修正 → Day5 重新 eval 比較
→ Day6 若通過寫入 registry 並進 shadow → Day7 週報+存檔。

## Validation Receipt

見 `../RUN_PLAN.md` 「Validation Receipt」章節逐條列出的可重現指令與結果；
完整 job bundle：`workbook/reviews/JOB-LOCAL-MODEL-EVOLUTION-20260719/`。
