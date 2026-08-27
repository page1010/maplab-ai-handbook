# LINE 12 輪 plateau 第一性原理檢討

日期：2026-08-28
角色：A1/A6 系統升級工程師
結論：前 12 輪不是有效訓練實驗；立即停止同方法續跑，改為固定 canary、failure taxonomy 與單一變因比較。

## 五題回推

1. **真正目的**：不是讓 Ollama 一直回覆，而是讓 Hermes 在不外送私密對話、不亂報價格、不重問已知資訊的前提下，穩定產出可直接草擬的 MAPLAB LINE 回覆。
2. **現況與目的差距**：12 rounds／60 calls 只有 10 pass（16.7%），單輪最高 40%，success streak 0。60 題全部不同，沒有固定 canary；因此無法判斷 lesson、prompt 或模型是否真的改善。
3. **假限制**：不是「再多跑才會學會」。現行 worker 沒有 fine-tune、權重更新或穩定 retrieval；只有 random two-shot 與最新 lesson prompt。多跑不同樣本只會累積不可比較結果。
4. **從零設計**：先人工讀失敗，建立 taxonomy；用 20 個固定分層 canary 校正 grader；同案例跑 baseline A 與單一變因 candidate B；安全 gate 與能力分數分離；達不到預先寫下的 delta 就停損。
5. **最小可證明下一步**：零模型呼叫完成 method contract；再以最多 40 次本機 inference 跑一個 paired block。任何 unsupported price／private egress／customer send 立即停止。

## 失敗結構

- 50/60 failed；39 次被 length gate 擋下，38 次實際過長，32 次只有長度問題。
- 35 個 score >= 75 的回答仍 fail，說明 aggregate score 與硬門檻混在一起。
- 生成文字中位數約 126 字，Mina gold 中位數約 26.5 字；真正主因之一是回覆設計過長，不是樣本跑不夠。
- `S_PENDING` 佔 35/60；`S2_DIETARY` 與 `S3_QUOTE_INTRO` 為 0，抽樣不均。
- evaluator 主要做 lexical／長度檢查，沒有可靠驗證「回答了問題、下一問正確、沒有重問已知資訊、最多三問、事實與價格有根據」。
- current lesson 會被覆寫，前輪教訓不保證在下一批適用。

## E1 實驗契約（尚未執行模型）

```yaml
method_version: line-reply-e1-structured-rubric
hypothesis: 結構化 known/missing/forbidden rubric 加上短回覆模板，能在不增加 unsupported claims 下，顯著優於現行 random two-shot prompt。
target_failure_bucket: answer_relevance, reask_known, excessive_length, unsupported_policy_or_price
changed_variable: prompt and grader contract only
fixed_holdout: 20 cases, 4 each for data/dietary/quote/payment/followup
baseline: current prompt, same model digest, same 20 cases, same seed schedule
candidate: structured known/missing/forbidden prompt, same everything else
expected_delta: candidate at least +4/20 pass over baseline
stop_loss: max 40 local inferences; stop on any unsafe claim or grader calibration below 18/20
safety_gates: price/policy/known-fact violations 0; private egress 0; customer send false
qualification: correct answer plus next question >=18/20; reask_known <=1/20; at_most_3_questions >=19/20; no stage regresses >1 case
```

## 方法來源

- OpenAI failure taxonomy：<https://openai.com/index/evals-drive-next-chapter-of-ai/>
- Anthropic held-out evaluation guide：<https://www-cdn.anthropic.com/38a1fb9db81446402a70bc45d104327aab12f3fe.pdf>
- Anthropic agent evals：<https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
- Adaptive data analysis：<https://arxiv.org/abs/1506.02629>
- OpenAI noisy evals：<https://openai.com/index/separating-signal-from-noise-coding-evaluations/>
- Anthropic infrastructure noise：<https://www.anthropic.com/engineering/infrastructure-noise>
