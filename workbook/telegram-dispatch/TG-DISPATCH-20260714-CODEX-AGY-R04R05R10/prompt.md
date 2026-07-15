# MAPLAB Dispatch — TG-DISPATCH-20260714-CODEX-AGY-R04R05R10

你是 MAPLAB 系統的 Codex/agy worker。Dispatch ID：`TG-DISPATCH-20260714-CODEX-AGY-R04R05R10`

## 執行前必讀
1. `CURRENT_STATUS.md`
2. `handoff/tasks/` — 對應任務卡（見下方各 JOB）

## 守則
- 唯讀分析，不發布 WordPress 文章，不改廣告設定
- 每個 JOB 完成後，把輸出落地到指定 output 路徑
- 最後在 `CURRENT_STATUS.md` 最新事實欄位 **不要改**（由 A1 checkpoint.sh 負責）
- 完成後回報 receipt：`dispatch_id + job_id + output_path`

---

## JOB R04 — SEO中斷診斷+重啟策略（A2）

讀：
- `handoff/tasks/T-A2-005-local-seo-factory.md`
- `handoff/tasks/T-A2-SEO-CATERING-MATRIX-001.md`
- `projects/seo-ads-agent.md`
- `state/seo_loop_run.jsonl`（最後 20 筆）

回答：
1. Local SEO Factory 目前卡在哪？最後成功步驟是？
2. SEO Catering Matrix 文章撰寫未開始的根因？
3. `seo_loop_run.jsonl` 最後一筆是什麼時候？有無錯誤？
4. 給出 3 步重啟計畫（優先排不需 Owner 授權的步驟）

輸出路徑：`workbook/outputs/R04-seo-diagnosis-2026-07-14.md`

---

## JOB R05 — 品牌語氣vs現有文章掃描（A2）

讀：
- `skills/brand-voice-guide.md`
- `skills/maplab-visual-spec.md`

任務：
1. 列出品牌語氣核心準則（5 條以內）
2. 掃描 `docs/` 目錄，找出明顯偏離準則的段落（最多 5 例）
3. 輸出格式：準則/偏差段落/建議改法

輸出路徑：`workbook/outputs/R05-brand-voice-audit-2026-07-14.md`

---

## JOB R10 — Investment OS 角色整合全貌（B1）

讀：
- `handoff/tasks/T-B1-B4-investment-os-role-split.md`
- `handoff/tasks/T-B1-001.md`
- `projects/b5-shadow-capability-distillation.md`（若存在）

回答：
1. IOS 目前有幾個角色？各角色主責一句話
2. B1-B4 分工盲點（最多 3 個）
3. B5 能力蒸餾進展與對其他角色的影響
4. 整合優先序建議（3 條，可自主執行的放前）

輸出路徑：`workbook/outputs/R10-ios-role-integration-2026-07-14.md`

---

## 完成後 Receipt

在每個 output 檔案頂部加入：

```
<!-- receipt: TG-DISPATCH-20260714-CODEX-AGY-R04R05R10 / JOB-Rxx / completed -->
```
