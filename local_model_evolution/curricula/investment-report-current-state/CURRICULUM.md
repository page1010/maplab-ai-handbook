# P0-1 Curriculum — Investment Report / Current-State

> 狀態：dataset_ready（eval only）｜ 版本 v0.1 ｜ 建立：2026-07-19
> 對應：LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md §八 P0-1

## 目標輸出

固定十欄現況卡：資料時間與來源／今日狀態／部位與風控閘門／Thesis 狀態／
市場確認／規則觸發／缺資料或 stale 或 conflict／Owner 選項／失效條件／下次檢查。

## 地端模型必須學會（G1→G2 邊界）

- ticker／公司／市場／日期／quarter 硬性隔離，不跨 ticker 或跨季度混用資料。
- 數字問題只引用有 `source_ref` 的輸入；沒有來源的數字必須拒絕或標記 unverified。
- 資料時間戳超過新鮮度門檻時必須明確標記 stale，不得當成今日現況。
- 缺資料時拒絕補猜，明確標記 `missing_or_stale_or_conflict`。
- 全程 simulation only（呼應 investment-os/docs/SECURITY_BOUNDARIES.md）。

## Eval Cases

- 位置：`evals/eval_cases.jsonl`
- 數量：24（20–50 範圍內，第一輪不擴大）
- 資料來源：**全部為去識別化合成資料**（`TICKER_ALPHA/BETA/GAMMA/DELTA` 等佔位代碼）。
  這個 remote 沙盒沒有 Investment OS SQLite 存取權，也不應該把真實部位／持股資料
  送進教師模型評測集；用合成資料完全對齊「去識別化」與「資料權利已核准」兩條紅線。
- 六類，各 4 題：
  1. `INV-TICKER-*` — ticker isolation（防跨 ticker 污染）
  2. `INV-PERIOD-*` — period isolation（防跨季度污染）
  3. `INV-STALE-*` — stale source handling（防把舊資料當今日現況）
  4. `INV-NUMCLAIM-*` — unsupported number claims（防止無來源數字）
  5. `INV-CARD-*` — decision card completeness（十欄齊全）
  6. `INV-DECLINE-*` — missing data → 拒絕補猜

## 核心 Eval 指標（對應 eval_harness.py）

| 指標 | harness 錯誤代碼 | 目標 |
|---|---|---|
| ticker contamination rate | `ticker_contamination` | = 0 |
| period contamination rate | `period_contamination` | = 0 |
| stale source critical failure | `stale_source_treated_as_fresh` | = 0 |
| unsupported number claims | `unsupported_number_claim` | = 0 |
| decision card completeness | `decision_card_incomplete` | = 0 |
| 拒絕補猜正確率 | `guessed_instead_of_declining` | = 0 |

## Baseline 狀態

**Blocked in this remote sandbox** — 沒有 Ollama / Mac mini runtime 可存取，無法對
真實地端模型跑 baseline。已改用手寫 fixture 自我測試 `eval_harness.py` 本身能否
正確抓出每一類錯誤（見 `../../evals/harness_selftest_investment_report.json`），
證明 harness 邏輯可信，等 Mac mini runtime 執行時才是真正 baseline。

## 下一步（不得跳過 baseline 直接進 LoRA）

1. 在 Mac mini 上對 T3 模型（gemma4 / qwen2.5 / llama3.1，見 model-tier-policy.md §1.1）
   跑本 curriculum，用 `bin/eval_harness.py --curriculum investment-report-current-state
   --outputs <真實模型輸出.jsonl>` 產生真正 baseline。
2. 找出前三大錯誤類型，優先用 Level A（prompt/skill/metadata filter/deterministic
   validator）修正，Level B（教師示範/preference pairs）其次，Level C（LoRA）最後。
3. Eval case 數量視 baseline 結果決定是否擴充到 50 題上限，不預先擴大。
