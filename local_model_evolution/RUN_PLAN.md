# RUN_PLAN — Local Model Evolution Orchestrator

> 版本 v0.1 ｜ 建立 2026-07-19 ｜ 依據 `LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md`
> （page1010/maplab-ai-handbook Draft PR #20 內容，已 merge 進本分支）
> 全新 session 只讀本檔 + `state/STATE.md` + `models/registry.json` 即可接手。

## 北極星（不重寫，指回原始 prompt）

G1（照規則完成）→ G2（路由與防錯）→ G3（自我檢查修復）→ G4（邊界內自主跑 loop）。
只服務 MAPLAB 與 Investment OS，不追求通用 GPT-4。優先部門：
①股票報表與投資現況分析 ②SEO 排名與關鍵字追蹤 ③MAPLAB 客服/報價/現金流（P1，本輪未動）。

## 治理前提（本輪新確認，寫入是因為原始 prompt 沒完全對齊既有政策）

`docs/governance/model-tier-policy.md` §0 明文禁止開任何按量 API key
（OpenAI/Anthropic/Gemini 皆同）。原始 prompt §六描述的「official usage/cost API」
資料層，在 MAPLAB 現行政策下**預設 blocked_by_policy**，不是單純排在優先順序最後——
除非 Owner 針對特定任務書面核准 + 預算上限 + 用量回報義務。`config/providers.yml`
已把這條規則寫死在 schema 裡（`status_override: blocked_by_policy`），避免任何一輪
不小心開了按量 key。

## 這一輪（Cycle 1）實際完成範圍

見 `state/STATE.md` 表格。摘要：骨架、curricula、eval harness、Quota Sentinel
腳本全部完成且可執行；**真實地端模型 baseline 因為這個 session 跑在沒有 Ollama
的 remote 沙盒而 blocked**，harness 本身已用 hand-authored fixture 自我測試過
（不是拿模型輸出冒充 baseline）。

## 目錄結構

```
local_model_evolution/
├── RUN_PLAN.md                      本檔
├── state/
│   ├── STATE.md                     接續狀態（唯一真相源）
│   └── provider_status.json         quota_sentinel.py 產出
├── config/
│   ├── providers.yml                provider registry + 政策紅線
│   └── reset_calendar.yml           reset 時區與信心標記
├── bin/
│   ├── quota_sentinel.py            可執行，已跑過
│   └── eval_harness.py              可執行，已自我測試
├── curricula/
│   ├── investment-report-current-state/
│   │   ├── CURRICULUM.md
│   │   └── evals/eval_cases.jsonl   24 題
│   └── seo-ranking-keyword/
│       ├── CURRICULUM.md
│       └── evals/eval_cases.jsonl   24 題
├── datasets/README.md               空骨架 + 進場門檻與紅線
├── evals/
│   ├── baseline_report.md           誠實記錄 blocked 狀態 + harness 自我測試結果
│   ├── harness_selftest_investment_outputs.jsonl / _report.json
│   └── harness_selftest_seo_outputs.jsonl / _report.json
├── models/registry.json             schema only，candidates 為空
└── reports/latest.md                本輪總報告（Runtime/Quota/Curriculum/Baseline/MVP）
```

`jobs/` 目錄本輪未建立——沒有真實 teacher job 被派出（baseline 未完成前，
教師任務只會產生無法驗證品質的資料，違反「不做白工」原則），等 Mac mini
baseline 完成、Level A 修正試過一輪後才會開始建 job cards。

## Provider adapter（已建立，dry-run 通過）

`config/providers.yml` + `bin/quota_sentinel.py`，資料來源優先序：

```
official usage/quota API（MAPLAB 政策下 blocked_by_policy，需 Owner 例外核准）
→ official CLI / console export
→ local request ledger（尚未建立，見「已知缺口」）
→ authenticated CLI health / 429 分類
→ manual override
→ unknown
```

## 一週 MVP（下一輪執行順序，需在 Mac mini 上跑）

**Day 1** — 在 Mac mini 重跑 `quota_sentinel.py`，補讀 `AGENT_RULES.md` /
`pitfalls.md` / `dependency-map.md`，確認無重複建置。

**Day 2-3** — 建立 `bin/run_local_baseline.py`（把 `curricula/*/evals/eval_cases.jsonl`
的 `input` 餵給 T3 模型、把回覆轉成 harness 要的 output schema），對兩個
curriculum 各跑一次，產出真實 `outputs.jsonl`，跑 `eval_harness.py` 得到真正
baseline，寫回 `evals/baseline_report.md`。

**Day 4** — 找出前三大錯誤類型，設計 Level A 修正（prompt template / skill /
metadata hard filter / deterministic validator / tool routing 擇一或組合），
不碰模型權重。

**Day 5** — 重新跑 eval，比較 baseline vs candidate，套用 §十二 升格門檻
（關鍵安全錯誤不得增加、contamination 必須為 0、格式完整度不得退步、總分
提升 ≥5% 或同品質下成本/時間降低 ≥20%、任一核心 eval regression 超過 2% 不得升格）。

**Day 6** — 若通過，寫入 `models/registry.json` 一筆 `state: eval_passed`，
進入 shadow（investment 不產生真實委託；SEO 不直接發布或改 Ads/正式頁面）。

**Day 7** — 週報：`evals/baseline_report.md` 更新、`state/STATE.md` 接續點更新、
checkpoint.sh 存檔、回報 Owner What/So What/Now What/Loop Back。

## 已知缺口（不掩蓋）

1. `bin/run_local_baseline.py`（eval case → 模型輸出 → outputs.jsonl 轉接腳本）
   **尚未建立**——這是本輪最大的實際缺口，因為沒有可呼叫的地端模型可以測試它。
2. Local request ledger（quota 追蹤的「local_ledger」層）**尚未建立**，
   `quota_sentinel.py` 目前只做得到 CLI health 檢查，做不到用量估算。
3. Training framework（LoRA/adapter，如 peft/LoRA on Ollama-compatible base）
   **未盤點**——這個沙盒沒有 GPU、沒有 torch/peft 可驗證，Mac mini 上的實際
   能力（硬體、已裝套件）本輪完全未知，`STATE.md` 已誠實標記。

## Validation Receipt

- `python3 local_model_evolution/bin/quota_sentinel.py` — 執行成功，輸出見
  `state/provider_status.json`（7 行 provider/surface 組合，全部誠實回報
  `unknown`/`blocked_by_policy`/`available`，無捏造數字）。
- `python3 -c "import json; [json.loads(l) for l in open(p)]"` 對兩份
  `curricula/*/evals/eval_cases.jsonl` — 24+24 行全部為合法 JSON。
- `python3 local_model_evolution/bin/eval_harness.py --curriculum
  investment-report-current-state --outputs
  evals/harness_selftest_investment_outputs.jsonl` — exit 0，24/24 scored，
  正確抓出 5 類刻意植入的錯誤。
- 同上對 `seo-ranking-keyword` — exit 0，24/24 scored，正確抓出 6 類刻意植入的錯誤。
- `python3 local_model_evolution/bin/eval_harness.py --curriculum
  investment-report-current-state --outputs evals/does_not_exist.jsonl` —
  exit 1，回傳 `status: baseline_unavailable`，證明「讀不到資料就標 unknown，
  不虛構」的紅線在程式層真的生效，不只是文件宣稱。
- `python3 -c "import json; json.load(open('local_model_evolution/models/registry.json'))"` — 合法 JSON。

完整 receipt 路徑：`workbook/reviews/JOB-LOCAL-MODEL-EVOLUTION-20260719/`。
