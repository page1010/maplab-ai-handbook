# T-A6-HERMES-LINE-GYM-001

- Owner: A0 教學主責
- Executor: Hermes
- Status: OWNER_REVIEW / RUBRIC_V2_HUMAN_GOLD_REQUIRED
- Active loop: paused at 12 supervised rounds; daily 02:20 path is supervisor-only and live zero-call canary verified
- Truth source: `/Users/pagemacmini/.maplab/a6-hermes-training/`（private local, owner-only）
- Success: seven consecutive runs pass_rate >= 0.85 and unsupported price rate = 0
- Current evidence: 12 supervised rounds／60 calls，10/60 pass、best 40%、streak 0；v7 已凍結 20-case holdout 與 20 mappings／40-case two-shot manifest，但本機 exact reconstruction 證明來源只有20/20真人歷史回覆、0/20 structured human labels，且沒有rubric-v2 scorer。
- Safety finding: canonical／mirror／installed plist SHA `32803c23...` 且 live launchctl exact supervisor argv；plain kickstart 回 `canonical_execution_disabled`，job／receipt／round／call／attempt／run／lesson皆零 delta。`method-redesign-*` 缺 explicit true latch預設 fail closed。
- Next bounded action: Mina／Owner／明確真人reviewer完成owner-only 0600標註包的20個完整label vectors（七項criteria、unsafe、overall、reviewer provenance）；AI／deterministic prelabel不可冒充human gold。完成後才回RUNNING實作identity-blind scorer，要求至少18/20 exact agreement且commercial-safety mismatch=0。
- Evidence required: v7 method audit、schedule-gate v1 receipt SHA `0b704387...`、readiness receipt SHA `d8a8c573...`、private packet SHA `e48cb261...`、20/20真人labels與provenance、fixed scorer/rubric SHA、focused poisons。
- Stop condition: rubric v2 未達 18/20、paired runner SHA／rendered prompt manifest／immutable lesson snapshot尚未 pin、任何 unsupported commercial claim／private egress／customer send；寫 receipt 並停止，不得 promotion。

## Resume Prompt

我是 Hermes LINE 業務教練。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`docs/hermes-line-reply-training-plan.md`、canonical durable job、v7／schedule-gate／rubric-readiness receipts。Schedule gate不要重跑；frozen v7只有20個case identities，來源有20/20真人歷史回覆但0/20 structured human labels。Private 0600 annotation packet已備妥10個historical-reference＋10個controlled-negative specimens；job停在OWNER_REVIEW。只有Mina／Owner／明確真人reviewer填完七項criteria、unsafe、overall與provenance後，才可回RUNNING實作identity-blind scorer，校正至少18/20且commercial-safety mismatch=0。AI prelabel不可冒充human gold；保持execution disabled，不得render／跑E1／外送LINE／customer send。
