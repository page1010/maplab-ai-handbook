# T-A6-HERMES-LINE-GYM-001

- Owner: A0 教學主責
- Executor: Hermes
- Status: IN_PROGRESS / METHOD_REDESIGN_SCHEDULE_GATE
- Active loop: paused at 12 supervised rounds; daily 02:20 path is unsafe until it routes through the supervisor plateau guard
- Truth source: `/Users/pagemacmini/.maplab/a6-hermes-training/`（private local, owner-only）
- Success: seven consecutive runs pass_rate >= 0.85 and unsupported price rate = 0
- Current evidence: 12 supervised rounds／60 calls，10/60 pass、best 40%、streak 0；v7 已凍結 20-case holdout 與 20 mappings／40-case two-shot manifest，排除過往曝露的 77 eval IDs／68 conversations；method audit 不耗 model call／attempt。
- Safety finding: canonical＋installed launchd 仍直接呼叫 raw training loop；supervisor pause 後又多跑 5 calls、0/5 pass，且出現 1 個 unsupported price。
- Next bounded action: 把 02:20 canonical＋installed launchd 改由 supervisor 進入 fail-closed plateau gate，加入 plist contract test；reload／kickstart 必須維持 round=12、calls=60、attempt=6，且新增 model calls=0。不得先跑 E1。
- Evidence required: v7 method audit、source-preimage job SHA chain、plist source/runtime hashes、launchctl live readback、zero-call kickstart receipt、focused tests。
- Stop condition: schedule path 未受 guard、rubric v2 未先達 18/20 calibration、paired runner SHA／rendered prompt manifest／immutable lesson snapshot 尚未 pin、任何 unsupported commercial claim／private egress／customer send；寫 receipt 並停止，不得 promotion。

## Resume Prompt

我是 Hermes LINE 業務教練。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`docs/hermes-line-reply-training-plan.md`、canonical durable job 與 `hermes_line_method_redesign_receipt_v7.json`。目前不是繼續跑題；先封住 launchd 直通 raw loop 的 side door，讓 scheduled path 經 supervisor fail closed。以 reload／kickstart 證明 round=12、calls=60、attempt=6、model calls delta=0，再更新 job receipt。E1 前還要校正 rubric v2 到至少 18/20、pin paired runner SHA、materialize immutable lesson snapshot，並讓 baseline/candidate 共用相同 user/context/examples/lesson 的 rendered prompt manifest；v7 明列 NOT_RENDERED／NOT_PINNED，因此現在不得執行。此 dev holdout 不得算入七連勝。不得外送 LINE 對話、不得對客發訊、不得杜撰價格。
