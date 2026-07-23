# local_model_evolution — STATE

> 全新 session 只讀本檔 + `RUN_PLAN.md` + `models/registry.json` 就要能接手。
> 最後更新：2026-07-19 ｜ 更新者：A1 / Local Model Evolution Orchestrator（第一輪）

## 這一輪做到哪

**第一輪範圍（LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md §十六）全部完成，
但兩個關鍵項目因執行環境限制而是「骨架 + 誠實標記為 blocked」，不是「已完成」：**

| 項目 | 狀態 | 備註 |
|---|---|---|
| 讀完整冷啟動資料 | ✅ 完成 | 見下方「已讀檔案」 |
| Runtime capability check | ✅ 完成（環境=沙盒，非 Mac mini） | 大部分能力 `unknown`/`not_detected`，誠實回報 |
| Quota Sentinel 設計 + dry-run | ✅ 完成，腳本可執行 | `bin/quota_sentinel.py` 已跑過，見 `state/provider_status.json` |
| `local_model_evolution/` 骨架 | ✅ 完成 | 見目錄樹 |
| P0 Curriculum × 2 | ✅ 完成 | 各 24 個去識別化 eval case（20–50 範圍內） |
| Eval harness | ✅ 完成，已自我測試 | `bin/eval_harness.py`，見 `evals/harness_selftest_*` |
| 真實地端模型 baseline | 🚫 **BLOCKED** | 這個沙盒沒有 Ollama，見 `evals/baseline_report.md` |
| 前三大錯誤類型 | ⚠️ 只有 harness 自我測試版本，非模型診斷 | 需 Mac mini 重跑才有效 |
| 第一版改善方案 | 🔲 待 Mac mini baseline 出來後才能定 | 見下方「下一步」 |
| 一週 MVP | ✅ 已規劃（見 RUN_PLAN.md） | 尚未開始執行，因為卡在 baseline |

## 已讀檔案（冷啟動資料）

MAPLAB：`SYSTEM_DIRECTORY_INDEX.md`、`workbook/system_index/system_relation_index.csv`（透過索引文件間接引用）、
`skills/system-directory-index/SKILL.md`（已 merge 進本分支，未逐字重讀全文，
已讀其索引與角色反向索引段落）、`docs/company-values.md`、
`skills/first-principles-check/SKILL.md`、`CURRENT_STATUS.md`（近期段落）、
`docs/governance/model-tier-policy.md`、`docs/governance/multi-model-orchestration-v0.1.md`、
`docs/governance/unattended-run-safety.md`、`workbook/learning_loop/README.md`、
`handoff/tasks/T-A1-LEARNING-LOOP-001.md`、`packages/local-model-teaching/2026-07/README.md`。

Investment OS（clone 於 `/workspace/investment-os`，未 push 回該 repo）：
`CURRENT_STATE.md`、`docs/SECURITY_BOUNDARIES.md`、`TASK_BOARD.md`、`HANDOFF.md`、
`docs/PROJECT_CONTEXT.md`（存在但本輪未逐字讀取全文，僅確認存在）。

**注意：`AGENT_RULES.md`、`AGENT_STARTUP_PROTOCOL.md`、`pitfalls.md`、
`dependency-map.md`、`investment-os/DECISION_LOG.md`、
`investment-os/schemas/README.md` 這幾份 Prompt 列為「依序讀」的檔案本輪
**未逐字讀取**（context 限制下優先讀了治理與 curriculum 直接相關的檔案）。
下一輪若要動 Level A 修正或建立 teacher jobs，必須先補讀。**

## 環境事實（重要，避免下一輪重踩）

這個 session 執行在 A1 remote cloud 沙盒，**不是 Owner 描述的 Mac mini Remote
Codex**。`command -v` 檢查結果：

- `python3` ✅（3.11.15，含 pyyaml）
- `claude` ✅（`/opt/node22/bin/claude`，Claude Code CLI 本身）
- `ollama` / `codex` / `agy` / `gemini` / `hermes` / `sqlite3` / `launchctl` / `crontab` ❌ 全部找不到

因此：Ollama 地端模型無法在此環境測試；launchd 排程無法在此環境設定或驗證；
LoRA/adapter training framework 無法盤點（沒有 torch/peft 可驗證，也沒有 GPU
runtime 可確認）。**這些都必須在 Mac mini 上重新盤點，本輪的 runtime capability
report 只證明「沙盒沒有」，不能推論「Mac mini 也沒有」。**

## 下一步（接續點）

1. 在 Mac mini 上重跑 `python3 local_model_evolution/bin/quota_sentinel.py`，
   取得真實 provider CLI health 訊號（claude/codex CLI 是否認證成功）。
2. 補讀 `AGENT_RULES.md`、`pitfalls.md`、`dependency-map.md`，確認沒有現成
   quota/multi-model 機制被重複建置（已核對 `multi-model-orchestration-v0.1.md`
   無衝突，但 `AGENT_RULES.md` 全文本輪未讀）。
3. 建立「eval_cases → 餵給地端模型 → outputs.jsonl」轉接腳本（目前不存在，
   `bin/` 底下只有 `quota_sentinel.py` 與 `eval_harness.py`，還缺
   `bin/run_local_baseline.py` 或等效腳本）。
4. 用轉接腳本對 T3 模型（見 model-tier-policy.md §1.1：gemma4/qwen2.5/llama3.1）
   跑兩個 curriculum，取得真正 baseline。
5. 找出前三大錯誤類型，先用 Level A（prompt/skill/metadata filter/deterministic
   validator/routing）修一輪，重新量測，才考慮 Level B。
6. **沒有真實 baseline、沒有固定 eval 跑過真模型、沒有資料權利與 rollback 前，
   不得建立任何 LoRA/adapter 候選**（`models/registry.json.candidates` 必須維持空）。

## 阻塞

- Mac mini / Ollama runtime 不可從此 session 存取 —— 結構性阻塞，需在正確環境
  重跑，非本輪能解決。
- 無其他 Owner 決策型阻塞；本輪未執行任何不可逆動作，無需 Owner 批准才能繼續。

## 相關但不重複的既有機制

- `workbook/learning_loop/`（T-A1-LEARNING-LOOP-001）：patrol reaction 分流，
  P2 token capital registry 待做。**本輪的 curricula/eval 是不同的資產類型
  （教學/評測用），不取代 token capital registry，未來 P2 執行時應該把
  `local_model_evolution/curricula/*` 登記進 token capital registry，而不是
  重建一份。**
- `packages/local-model-teaching/2026-07/`（B5 教材包骨架）：本輪的 eval cases
  未來可作為該教材包 `eval_cases/` 子目錄的候選來源，本輪未直接寫入該目錄，
  避免在 baseline 未完成前就把未驗證內容打包給地端模型。
- `docs/governance/multi-model-orchestration-v0.1.md`：既有的 Codex/Antigravity/
  地端三層省算力架構，本輪的教師分工（GPT/Claude/Gemini）與其一致，未新增
  平行角色定義。
