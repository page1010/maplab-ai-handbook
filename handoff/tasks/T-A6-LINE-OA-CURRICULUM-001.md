# T-A6-LINE-OA-CURRICULUM-001

- Owner: Mina / MAPLAB
- Role: Codex A0/A1 system administrator and Hermes training supervisor
- Status: `COMPLETE_DEVELOPMENT_FIXTURES_READY / SAFETY_PASS / WEIGHT_LEARNING_NOT_PROVEN / PROMOTION_BLOCKED`
- Started: 2026-10-02
- Completed: 2026-10-02

## Goal / Outcome

把已存入 A6 本機資料庫的 28 組 LINE OA 預設訊息轉成 Hermes 可重複驗收的離線 development fixtures，以現行「一輪一題、不報價、不承諾檔期、不自動對客」contract 當答案，舊範本只當歷史正反例。

## Definition of Done

- [x] 28 組 Owner 命名情境全數對應現行 Hermes route，未知或缺少 title 會 fail closed。
- [x] 原訊息只在本機記憶體內檢查，衍生 fixture 僅保留 hash、長度、sensitivity 與 violation code。
- [x] 20 組標為 `PROHIBITED_NEGATIVE`，8 組標為 `HISTORICAL_REFERENCE`；全部標為非 human gold、不可 SFT、不可 auto-send、需 Mina review。
- [x] 現行 approved patterns deterministic guard 違規數 0。
- [x] 私密輸出目錄 0700、檔案 0600；原訊息未進 Git。
- [x] 相關測試 19/19 PASS，compileall PASS。
- [x] provider attempts、optimizer steps、weight delta、customer send、external egress 全部為 0。

## Implementation

- Materializer: `scripts/a6_line_saved_reply_curriculum.py`
- Regression tests: `tests/test_a6_line_saved_reply_curriculum.py`
- Source snapshot: gitignored `data/case-store/a6_case_store.sqlite3`
- Private output: `/Users/pagemacmini/.maplab/a6-hermes-training/line_oa_saved_replies/`
- Continuous heartbeat: `hermes-a6-shadow-training` (`ACTIVE`, daily 02:20 Asia/Taipei, notify only on material change or failure)
- Validation receipt: `workbook/reviews/A6-LINE-OA-CURRICULUM-20261002/validation_receipt.md`

## Verified Result

- Fixtures: 28.
- Route distribution: `Q1=6, Q2=1, Q3=2, Q5=1, Q6=2, Q9=2, MENU_PREF=6, PAYMENT_CHECK=4, REF_IMAGE=2, SERVICE_SCOPE=2`.
- Historical roles: `PROHIBITED_NEGATIVE=20, HISTORICAL_REFERENCE=8`.
- Source violation signals: `availability_commitment=1, money_or_terms_commitment=8, more_than_one_question=3`.
- Approved-pattern violations: 0.
- Verdict: `SAFETY_PASS / IMPROVED_DEVELOPMENT_FIXTURES_ONLY / WEIGHT_LEARNING_NOT_PROVEN / PROMOTION_BLOCKED`.

## Boundary

這次完成的是教材整理、路由答案與回歸驗收，不是模型權重已學會。未產生 adapter，未使用 OpenRouter，未修改 LINE，未發送客戶訊息。

## Next Bounded Action

自動產生需求變體，用 28 組 route 做零發送 shadow simulation 與 deterministic grading，只將異常列為待處理。Owner 已提供的回饋直接進 regression；不要求 Owner 另填 20 案或重寫 28 案。具名 human-gold 由日常使用中的真實修正漸進累積，未過 gate 前不進 SFT 或 Telegram／LINE live 影子發送。

## Resume Prompt

我是接手 A6 LINE OA curriculum 的 Codex。先讀 `AGENT_CORE.md`、`CURRENT_STATUS.md`、`pitfalls.md`、本 Task Card、`.agents/skills/sol56-hermes-training-retrospective/SKILL.md`、`docs/hermes-line-reply-training-plan.md` 與 `config/hermes-line-sheets-assistant-v1.json`。先重跑 `scripts/a6_line_saved_reply_curriculum.py` 與 19 項關聯測試，再核對 private receipt。下一步做零發送 shadow simulation 與異常清單，不要求 Owner 填 20 或 28 案答案。未累積足夠具名 human-gold correction 與新收據前，不得宣告權重學習、不得自動對客、不得把原訊息送往 OpenRouter 或其他第三方。
