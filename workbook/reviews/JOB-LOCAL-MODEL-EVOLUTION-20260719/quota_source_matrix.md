# Quota Source Matrix — JOB-LOCAL-MODEL-EVOLUTION-20260719

canonical 版本：`local_model_evolution/config/providers.yml` +
`local_model_evolution/config/reset_calendar.yml`（設計）與
`local_model_evolution/state/provider_status.json`（dry-run 執行結果，本目錄的
`provider_status.json` 是同一次執行的 receipt 快照）。

## 資料來源優先序（已寫入 providers.yml，非本檔重複定義）

```
official usage/quota API（MAPLAB model-tier-policy.md §0 下預設 blocked_by_policy）
→ official CLI / console export
→ local request ledger（尚未建立）
→ authenticated CLI health / 429 分類
→ manual override
→ unknown
```

## 治理衝突發現（本輪新確認，需 A1/Owner 知悉）

原始 `LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md` §六 假設可能讀取
OpenAI Usage/Costs API、Anthropic organization usage report、Gemini/Google
Cloud quota 工具。但 `docs/governance/model-tier-policy.md` §0（2026-07-06
生效，「本檔是 A0/A1 派工前的強制查表」）明文禁止開任何按量計費 API key，
理由是 2026-04-18 GCP Gemini 事件燒掉約 NT$3,000 的教訓。

**處置**：`providers.yml` 把三個 provider 的 `api` surface 都標
`status_override: blocked_by_policy`，Quota Sentinel 預設不會嘗試使用這條
資料來源，除非 Owner 針對特定任務書面核准 + 預算上限 + 用量回報義務
（見 `providers.yml` 的 `override` 區塊）。這不是本輪自行決定放寬或忽略，
是把既有更高位階的治理規則（model-tier-policy.md）套用到新設計上。
