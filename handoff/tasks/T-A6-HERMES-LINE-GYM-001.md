# T-A6-HERMES-LINE-GYM-001

- Owner: A0 教學主責
- Executor: Codex / A1（教練與整合）；Hermes（受限草稿 worker）
- Status: OWNER_REVIEW / RUBRIC_V2_HUMAN_ANNOTATION / MLX_LAB_READY_QUALITY_UNPROVEN
- Active loop: paused at 12 supervised local rounds; daily 02:20 path is supervisor-only and live zero-call canary verified. OpenRouter cloud lane is also execution-gated; its 2026-08-31 preflight made zero calls.
- Truth source: `/Users/pagemacmini/.maplab/a6-hermes-training/`（private local, owner-only）
- Success: seven consecutive runs pass_rate >= 0.85 and unsupported price rate = 0
- Current evidence: 12 supervised local rounds／60 calls，10/60 pass、best 40%、streak 0；另一次受控OpenRouter探索為25 examples／49 provider requests（25 HTTP errors、24 answers），只有1個lexical heuristic pass，不能算新訓練輪或品質進步。v7 已凍結20-case holdout。Source-bound rubric guide SHA `d62cf9bf...` 已固定七項規則、exact overall、fail-closed commercial authority SHA `84d9733b...`、14個各項正反fixtures與具名真人attestation/adjudication；structured human labels仍為0/20。
- Quota contract: Owner 的 USD 10 credit purchase 對應每日1,000個`:free` request attempts；訓練硬上限950、Owner日常保留50。2026-08-31已用49，私有共用0600 ledger剩901；fallback與失敗都先記一次，paid model本機拒絕，paid key limit維持0。950是上限，不是每日目標。
- 2026-08-30 quote lesson: Claude分析經Owner點名後只升為`OWNER_NOMINATED_CURRICULUM_CANDIDATE`。可採用的是單一窗口先講統籌價值、參考圖與預算互補、核心資料後才整理A/B/C範圍、醫療／兒童／樓層只問不斷言、勘場不承諾。Claude生成的價位、比例、競品斷言全部拒絕；不是pricing authority、Owner policy或human gold。Synthetic curriculum SHA（canonical JSON）=`098f8fa0...`。
- 2026-09-01 method correction: 前5輪確認為random two-shot inference、沒有權重更新，僅4/25 pass且2個未授權價格；不再稱為持續訓練。已隔離安裝Apple MLX-LM＋Qwen3-4B-Instruct-2507，並以8筆純合成資料在deny-network sandbox完成3-step QLoRA：adapter可保存／reload、base與adapter輸出不同、peak memory 2.697GB。Adapter只把回覆縮短，仍漏「單一窗口價值」，故只證明training stack，品質仍未過關；live route維持disabled。
- Safety finding: canonical／mirror／installed plist SHA `32803c23...` 且 live launchctl exact supervisor argv；plain kickstart 回 `canonical_execution_disabled`，job／receipt／round／call／attempt／run／lesson皆零 delta。`method-redesign-*` 缺 explicit true latch預設 fail closed。
- Next bounded action: 一位具名真人依 `docs/hermes-line-rubric-v2-annotation-guide.json` 在本機逐案判讀20案，寫入新的owner-only 0600 annotation檔，並綁private preflight SHA `10e41cf2...`、guide SHA `d62cf9bf...`、authority SHA `84d9733b...`。Private blank preflight不可原地修改，AI／synthetic labels不可當human gold。
- Evidence required: v7 method audit、schedule-gate v1 receipt SHA `0b704387...`、readiness receipt SHA `e001166c...`、guide receipt SHA `f809f5ae...`、`reviews/HERMES-MLX-DISTILLATION-20260901/install-smoke-receipt.json`；接著需要20/20具名真人labels、必要時第二真人與adjudication、identity-blind scorer與agreement receipt。
- Stop condition: 20/20具名真人labels未完成、rubric v2 未達 18/20、paired runner SHA／rendered prompt manifest／immutable lesson snapshot尚未 pin、ledger/rate/cap/free-only gate失敗、任何 unsupported commercial claim／未核准private egress／customer send；寫 receipt 並停止，不得 provider execution或promotion。

## Resume Prompt

我是接手 Hermes LINE 訓練的 Codex / A1。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`docs/hermes-line-reply-training-plan.md`、`docs/hermes-distillation-method-v1.md`、rubric guide、OpenRouter task與MLX install receipt。舊12輪是random two-shot evaluation，不是權重訓練；MLX lab雖已完成真正3-step QLoRA smoke，但只證明底座，不代表品質。每日1,000的單位是provider request attempts；950是ceiling、Owner保留50，不得為吃額度盲跑。下一步只由具名真人在本機逐案標註20個private cases，另建0600檔並綁三個SHA；完成scorer >=18/20且安全0 mismatch後，才做DLP與30–50組Owner-corrected gold。外接碟只放公開基模，私有dataset／adapter／logs留owner-only root；保持live route disabled，不得外送原始LINE或customer send。
