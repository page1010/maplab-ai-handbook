# T-A6-HERMES-LINE-GYM-001

- Owner: A0 教學主責
- Executor: Hermes
- Status: IN_PROGRESS / METHOD_REDESIGN_RUBRIC_CALIBRATION
- Active loop: paused at 12 supervised rounds; daily 02:20 path is supervisor-only and live zero-call canary verified
- Truth source: `/Users/pagemacmini/.maplab/a6-hermes-training/`（private local, owner-only）
- Success: seven consecutive runs pass_rate >= 0.85 and unsupported price rate = 0
- Current evidence: 12 supervised rounds／60 calls，10/60 pass、best 40%、streak 0；v7 已凍結 20-case holdout 與 20 mappings／40-case two-shot manifest，排除過往曝露的 77 eval IDs／68 conversations；method audit 不耗 model call／attempt。
- Safety finding: canonical／mirror／installed plist SHA `32803c23...` 且 live launchctl exact supervisor argv；plain kickstart 回 `canonical_execution_disabled`，job／receipt／round／call／attempt／run／lesson皆零 delta。`method-redesign-*` 缺 explicit true latch預設 fail closed。
- Next bounded action: 只用 frozen 20 個 structured labels 零模型校正 rubric v2；至少 18/20 exact agreement，逐筆記 disagreement 與 rubric change。保持 `execution_eligible=false`，不得 render／跑 E1。
- Evidence required: v7 method audit、schedule-gate v1 receipt SHA `0b704387...`、20-case calibration manifest、逐案 labels／agreement、fixed rubric SHA、focused tests。
- Stop condition: rubric v2 未達 18/20、paired runner SHA／rendered prompt manifest／immutable lesson snapshot尚未 pin、任何 unsupported commercial claim／private egress／customer send；寫 receipt 並停止，不得 promotion。

## Resume Prompt

我是 Hermes LINE 業務教練。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`docs/hermes-line-reply-training-plan.md`、canonical durable job、`hermes_line_method_redesign_receipt_v7.json` 與 `hermes_line_schedule_gate_receipt_v1.json`。Schedule side door 已封，live kickstart 已證明 round=12、calls=60、attempt=6、model calls delta=0；不要再重載或重跑 gate。下一步只對 frozen 20 個 structured labels 做 rubric v2 零模型校正，要求至少18/20 exact agreement並逐筆記錄 disagreement／rule change／fixed rubric SHA。保持 `execution_eligible=false`；rubric、paired runner SHA、immutable lesson snapshot及共用輸入 rendered prompt manifest四項未全關閉前不得 render／跑 E1。此 dev holdout不得算七連勝；不得外送LINE對話、不得對客發訊、不得杜撰價格。
