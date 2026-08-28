# LINE 12 輪 plateau 第一性原理檢討

日期：2026-08-28
角色：A1/A6 系統升級工程師
結論：前 12 輪不是有效訓練實驗；立即停止同方法續跑，改為固定 canary、failure taxonomy 與單一變因比較。

## 五題回推

1. **真正目的**：不是讓 Ollama 一直回覆，而是讓 Hermes 在不外送私密對話、不亂報價格、不重問已知資訊的前提下，穩定產出可直接草擬的 MAPLAB LINE 回覆。
2. **現況與目的差距**：12 rounds／60 calls 只有 10 pass（16.7%），單輪最高 40%，success streak 0。60 題全部不同，沒有固定 canary；因此無法判斷 lesson、prompt 或模型是否真的改善。
3. **假限制**：不是「再多跑才會學會」。現行 worker 沒有 fine-tune、權重更新或穩定 retrieval；只有 random two-shot 與最新 lesson prompt。多跑不同樣本只會累積不可比較結果。
4. **從零設計**：先人工讀失敗，建立 taxonomy；用 20 個固定分層 canary 校正 grader；同案例跑 baseline A 與單一變因 candidate B；安全 gate 與能力分數分離；達不到預先寫下的 delta 就停損。
5. **最小可證明下一步**：先用零模型證據封住 scheduled side door；其後仍須校正 rubric、materialize immutable lesson snapshot、pin paired runner 與 rendered prompt manifest，才可用最多 40 次本機 inference 跑 paired block。任何 unsupported price／private egress／customer send 立即停止。

## 失敗結構

- 50/60 failed；39 次被 length gate 擋下，38 次實際過長，32 次只有長度問題。
- 35 個 score >= 75 的回答仍 fail，說明 aggregate score 與硬門檻混在一起。
- 生成文字中位數約 126 字，Mina gold 中位數約 26.5 字；真正主因之一是回覆設計過長，不是樣本跑不夠。
- `S_PENDING` 佔 35/60；`S2_DIETARY` 與 `S3_QUOTE_INTRO` 為 0，抽樣不均。
- evaluator 主要做 lexical／長度檢查，沒有可靠驗證「回答了問題、下一問正確、沒有重問已知資訊、最多三問、事實與價格有根據」。
- current lesson 會被覆寫，前輪教訓不保證在下一批適用。
- Canonical 與 installed launchd plist（SHA `0f93b994...`）都直接呼叫 raw training loop，沒有進 supervisor plateau guard。Supervisor 於 17:38Z 暫停後，02:20 path 又產生 5 calls、0/5 pass、1 個 unsupported price；這是 schedule side door，不是「持續訓練」。
- Physical store 有 17 份 run receipts；15 份有 explicit counter，至少 71 calls，其中至少 11 calls 不在 supervisor 計數內。兩份 legacy receipts 缺 counter，所以 71 是下限，不是精確總數。
- 最近三輪缺 prompt、lesson、sampling、acceptance、model digest 的完整 fingerprint；不同 seed／sample 不能當 paired improvement evidence。

## E1 實驗契約（已凍結，尚不可執行模型）

```yaml
method_version: line-reply-e1-prompt-only-v1
hypothesis: 結構化 known/missing/forbidden 短回覆 prompt 能在不增加 unsupported claims 下，顯著優於 legacy prompt。
target_failure_bucket: answer_relevance, reask_known, excessive_length, unsupported_policy_or_price
changed_variable: prompt_builder_contract_sha256 only
fixed_holdout: 20 unique conversations; data 4, dietary 4, quote-intro 2, quote-send 2, payment 4, followup 4
fixed_few_shot: 20 mappings / 40 globally unique train cases; two per holdout
prior_exposure: exclude all 77 unique eval IDs and their 68 conversations seen in physical run receipts; legacy few-shot IDs are unrecorded, so that exposure remains unconstructable
baseline: source-bound legacy build_prompt plan; full per-case messages NOT_RENDERED
candidate: structured known/missing/forbidden prompt plan; full per-case messages NOT_RENDERED
shared_inputs: NOT_PINNED
lesson_snapshot: NOT_MATERIALIZED
fixed_now: model digest, holdout, two-shot mappings, per-case seed, rubric v2 spec, acceptance spec
preconditions: scheduled path guard; rubric v2 >=18/20; paired runner SHA; immutable lesson snapshot; shared-input rendered prompt manifest
expected_delta: candidate at least +4/20 pass over baseline
stop_loss: max 40 local inferences; stop on any unsafe claim or grader calibration below 18/20
safety_gates: price/policy/known-fact violations 0; private egress 0; customer send false
qualification: correct answer plus next question >=18/20; reask_known <=1/20; at_most_3_questions >=19/20; no stage regresses >1 case
promotion_boundary: this dev holdout cannot count toward the seven-run promotion streak
```

執行順序是「先封 scheduler side door → 零模型校正 rubric → materialize lesson snapshot → render並pin兩側共用輸入 → 再做 prompt-builder-only paired E1」。v7只凍結source-bound計畫與資料manifest，不宣稱prompt已render或E1已ready；把 prompt 與 grader 同時改掉不是單一變因，因此舊契約作廢。

2026-08-28 10:05 readback：scheduler side door已由schedule-gate v1關閉；plain kickstart只增加launchd runs 0→1，job／12 rounds／60 calls／attempt 6／17 run receipts／15 lesson deltas全零delta。這只解除第一項前置，不改E1 eligibility；下一個最小可否證動作是20-case rubric v2零模型校正到至少18/20。

## 本輪零模型收據

- Sanitized：`hermes_line_method_redesign_receipt_v7.json`，SHA-256 `83725f64524fbf8776e19b09fcbe3c6c653acfcac46dfa1447f8b5abad03590c`，body `f0cac0218e5833e1560fef0bdd5bef8f6fcb5b589a36dadec7285d6a405c384b`。
- Private audit：owner-only mode 0600，SHA-256 `b604e7fa4e59d1986a45fdea4f6a6107408284a92dd676dbf762324ae8e6e891`。
- Source／tests：`730cff691743fe02ee556da5a304173fee02cd3d4379d3b9c4dc50c69f803f2d`／`7037e1925a3f3572ea9aadc3d4dc273ad30389eaf04e05ffb89d1456211d522c`；7/7 PASS，11組pair-forgery／nested payload／type／timestamp poisons全REJECT。
- 本 action：model calls 0、external calls 0、customer send false、attempt 6 → 6。
- 決策：`AUDIT_COMPLETE__SCHEDULE_GATE_REQUIRED_BEFORE_E1`。

## 方法來源

- OpenAI failure taxonomy：<https://openai.com/index/evals-drive-next-chapter-of-ai/>
- Anthropic held-out evaluation guide：<https://www-cdn.anthropic.com/38a1fb9db81446402a70bc45d104327aab12f3fe.pdf>
- Anthropic agent evals：<https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- Adaptive data analysis：<https://arxiv.org/abs/1506.02629>
- OpenAI noisy evals：<https://openai.com/index/separating-signal-from-noise-coding-evaluations/>
- Anthropic infrastructure noise：<https://www.anthropic.com/engineering/infrastructure-noise>
