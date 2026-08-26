# T-A6-HERMES-LINE-GYM-001

- Owner: A0 教學主責
- Executor: Hermes
- Status: IN_PROGRESS
- Active loop: daily 02:20 LINE reply evaluation
- Truth source: `/Volumes/MacExternal/maplab-data/a6-hermes-training/`
- Success: seven consecutive runs pass_rate >= 0.85 and unsupported price rate = 0
- Next bounded action: inspect the first real-data run, identify the lowest-scoring stage, and run a five-case repair batch.
- Evidence required: run JSON, loop_state, lessons delta, provider used, score delta.
- Stop condition: external drive missing, no provider succeeds, or unsupported commercial claims appear; write receipt and do not promote.

## Resume Prompt

我是 Hermes LINE 業務教練。先讀 `docs/hermes-line-reply-training-plan.md`、外接硬碟 manifest、loop_state、current_lessons 與最新 run。找最低分 stage，跑下一個 bounded repair batch；比較 Mina gold answer，不要用字面相似度冒充正確。每輪留下 run receipt、分數 delta、錯誤類型與下一輪 prompt。達到連續七輪門檻前，不接正式客戶自動發送。
