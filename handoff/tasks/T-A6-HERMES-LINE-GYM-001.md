# T-A6-HERMES-LINE-GYM-001

- Owner: A0 教學主責
- Executor: Hermes
- Status: OWNER_REVIEW / RUBRIC_V2_HUMAN_ANNOTATION
- Active loop: paused at 12 supervised rounds; daily 02:20 path is supervisor-only and live zero-call canary verified
- Truth source: `/Users/pagemacmini/.maplab/a6-hermes-training/`（private local, owner-only）
- Success: seven consecutive runs pass_rate >= 0.85 and unsupported price rate = 0
- Current evidence: 12 supervised rounds／60 calls，10/60 pass、best 40%、streak 0；v7 已凍結20-case holdout。Source-bound rubric guide SHA `d62cf9bf...` 已固定七項規則、exact overall、fail-closed commercial authority SHA `84d9733b...`、14個各項正反fixtures與具名真人attestation/adjudication；structured human labels仍為0/20。
- Safety finding: canonical／mirror／installed plist SHA `32803c23...` 且 live launchctl exact supervisor argv；plain kickstart 回 `canonical_execution_disabled`，job／receipt／round／call／attempt／run／lesson皆零 delta。`method-redesign-*` 缺 explicit true latch預設 fail closed。
- Next bounded action: 一位具名真人依 `docs/hermes-line-rubric-v2-annotation-guide.json` 在本機逐案判讀20案，寫入新的owner-only 0600 annotation檔，並綁private preflight SHA `10e41cf2...`、guide SHA `d62cf9bf...`、authority SHA `84d9733b...`。Private blank preflight不可原地修改，AI／synthetic labels不可當human gold。
- Evidence required: v7 method audit、schedule-gate v1 receipt SHA `0b704387...`、readiness receipt SHA `e001166c...`、guide receipt SHA `f809f5ae...`；接著需要20/20具名真人labels、必要時第二真人與adjudication、identity-blind scorer與agreement receipt。
- Stop condition: rubric v2 未達 18/20、paired runner SHA／rendered prompt manifest／immutable lesson snapshot尚未 pin、任何 unsupported commercial claim／private egress／customer send；寫 receipt 並停止，不得 promotion。

## Resume Prompt

我是 Hermes LINE 業務教練。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`docs/hermes-line-reply-training-plan.md`、`docs/hermes-line-rubric-v2-annotation-guide.json`、canonical durable job與guide receipt。Schedule gate與guide freeze不要重跑；七項decision rules、overall公式、commercial authority fail-closed snapshot、14個正反fixtures、具名真人attestation/adjudication均已驗證。下一步只由具名真人在本機逐案標註20個private cases，另建0600檔並綁preflight／guide／authority三個SHA；blank preflight不可原地改，AI／synthetic labels不可當human gold。保持execution disabled，不得pin scorer、render／跑E1／外送LINE／customer send。
