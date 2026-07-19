# Baseline Report — Cycle 1（2026-07-19）

## 誠實狀態：真實地端模型 baseline = BLOCKED

這次啟動是在 A1 的 remote cloud 沙盒（`claude/local-model-evolution-orchestrator-puvj7d`
分支的執行環境）跑的，**不是 Mac mini**。Runtime capability check（見
`../../local_model_evolution/reports/latest.md` 或
`../../workbook/reviews/JOB-LOCAL-MODEL-EVOLUTION-20260719/runtime_capability_check.md`）
證實這個環境沒有 `ollama`、`codex`、`agy`、`gemini`、`hermes`、`sqlite3`、
`launchctl`／`crontab`。**無法對任何真實地端模型跑 baseline，這是環境限制，
不是選擇不做。**

根據企業文化「不做白工」與安全紅線「不得虛構」，本輪不假裝有 baseline 數字，
改做兩件可驗證、可交接的事：

## 1. 驗證 eval harness 本身邏輯正確（harness self-test，非模型 baseline）

用手寫、明確標記為 synthetic fixture 的 model-output JSONL（不是任何真實模型的輸出）
去跑 `bin/eval_harness.py`，證明每一類 validator 真的會抓到對應的錯誤，而不是
形式上寫了程式碼但沒驗證過。

### Investment curriculum self-test

```
python3 local_model_evolution/bin/eval_harness.py \
  --curriculum investment-report-current-state \
  --outputs local_model_evolution/evals/harness_selftest_investment_outputs.jsonl
```

結果（`harness_selftest_investment_report.json`）：24 題全部評分，8/24 pass
（pass_rate 僅供 harness 驗證用，不代表任何模型品質——fixture 刻意讓多個類別
預設值會觸發驗證器，用意是確認驗證器會響）。前五大錯誤類型：

| 錯誤類型 | 次數 |
|---|---|
| `stale_source_treated_as_fresh` | 4 |
| `guessed_instead_of_declining` | 4 |
| `ticker_contamination` | 2 |
| `period_contamination` | 2 |
| `unsupported_number_claim` | 2 |

### SEO curriculum self-test

```
python3 local_model_evolution/bin/eval_harness.py \
  --curriculum seo-ranking-keyword \
  --outputs local_model_evolution/evals/harness_selftest_seo_outputs.jsonl
```

結果（`harness_selftest_seo_report.json`）：24 題全部評分，12/24 pass。前五大錯誤類型：

| 錯誤類型 | 次數 |
|---|---|
| `action_card_incomplete` | 4 |
| `historical_rank_treated_as_today` | 4 |
| `keyword_page_mapping_error` | 2 |
| `ranking_timestamp_missing` | 2 |
| `destructive_action_without_approval` | 2 |

### 缺資料時的行為驗證

```
python3 local_model_evolution/bin/eval_harness.py \
  --curriculum investment-report-current-state \
  --outputs local_model_evolution/evals/does_not_exist.jsonl
```

回傳 `"status": "baseline_unavailable"`，exit code 1，**不產生假分數**。這是
安全紅線「讀不到可靠數值時必須標記 unknown，不得虛構」在 eval 層的對應實作。

## 2. 「前三大錯誤類型」— 這是 harness 自我測試結果，不是模型缺陷診斷

**必須明確區分**：上面兩張表列的是「我刻意寫壞的 fixture 觸發了哪些 validator」，
不是「Mac mini 上的 T3 模型（gemma4/qwen2.5/llama3.1）實際會犯哪些錯」。
在 Mac mini 上重跑本節第一段的指令、換成真實模型輸出後，才會得到真正的
baseline 與有意義的前三大錯誤類型。

## 3. 給 Mac mini 上下一輪的具體指令

```bash
cd /Users/pagemacmini/maplab-ai-handbook
git fetch origin
git checkout claude/local-model-evolution-orchestrator-puvj7d   # 或已 merge 後的 main

# 1) 重跑 Quota Sentinel（在真實 runtime 上才有意義）
python3 local_model_evolution/bin/quota_sentinel.py

# 2) 對每個 curriculum，用 T3 模型產生輸出並存成 outputs jsonl
#    （格式：{"sample_id": "...", "output": {...}}，每題一列）
#    範例路由：ollama run qwen2.5:14b < curricula/investment-report-current-state/evals/eval_cases.jsonl
#    需要一支轉接腳本把 eval_cases.jsonl 的 input 餵給模型、把模型回覆轉成 output schema，
#    這支腳本尚未建立（下一輪待辦，見 STATE.md）。

# 3) 跑真正的 baseline
python3 local_model_evolution/bin/eval_harness.py \
  --curriculum investment-report-current-state --outputs <真實輸出.jsonl>
python3 local_model_evolution/bin/eval_harness.py \
  --curriculum seo-ranking-keyword --outputs <真實輸出.jsonl>
```

## Baseline 完成門檻（沒完成前不得動 LoRA）

- [ ] 兩個 curriculum 都有 Mac mini 上跑出的真實 `outputs.jsonl`
- [ ] `eval_harness.py` 回傳 `status: scored`（非 `baseline_unavailable`）
- [ ] 前三大錯誤類型已從真實輸出算出，非本輪的 fixture 自我測試
- [ ] Level A 修正（prompt/skill/routing/validator）已嘗試至少一輪並重新量測
