# Sol 5.6 訓練 Hermes 經驗談 Skill 收據

- Status: `FINAL_PASS`
- Date: `2026-09-01`
- Scope: `repo`
- Canonical location: `.agents/skills/sol56-hermes-training-retrospective/`
- Explicit invocation: `$sol56-hermes-training-retrospective`
- Runtime／model calls／customer sends: `0 / 0 / 0`

## Why this scope and name

這套方法是 MAPLAB／Hermes 專屬的訓練治理與組織學習方式，因此跟專案版本放在 repo 的 `.agents/skills/`，不複製到 user skill root。Skill 系統要求入口檔固定名為 `SKILL.md`，所以可搜尋名稱放在 folder、frontmatter 與 UI metadata；顯示名稱保留 Owner 要的「Sol 5.6 訓練 Hermes 經驗談」。

## What was institutionalized

```text
事實 → 偏差 → 根因 → 方法 → 實驗 → 結果 → 防復發規則 → 測試／收據 → Task／Resume
```

- What：分開 provider attempt、response、example、evaluation round、optimizer step、training run、qualification 與 shadow；禁止用活動量冒充學習。
- So What：先定位因果斷點，再在 authority／state／prompt／retrieval／SFT／DPO／system control 間選方法。
- Now What：建立 Detect／Contain／Correct／Institutionalize，讓同類觸發條件再次出現時能自動發現與停止。
- Success：分開 `WEIGHT_LEARNING`、`SYSTEM_QUALITY`、`ORGANIZATIONAL_LEARNING`，並另列 safety 與 promotion；成果和過程必須同時過關。

## Discovery and cold-start wiring

- Repo skill audit：`skills=18 duplicates=0`，canonical skill 已被掃描。
- Explicit search：`$sol56-hermes-training-retrospective`。
- Implicit triggers：`Sol 5.6 訓練 Hermes 經驗談`、`Hermes 訓練檢討`、`企業學習蛛網`、`經驗學習圈`、`misleading round counts`、`plan-versus-actual drift`。
- Cold-start entries updated：`CURRENT_STATUS.md`、`handoff/tasks/T-A6-HERMES-LINE-GYM-001.md`、`docs/hermes-line-reply-training-plan.md` 與兩處 Resume Prompt。

## Files and immutable hashes

- `SKILL.md`: `8266ba967dc2bdb3bc9ac7ce33e43a80d97e5d3fb86abd8458f7dbbc852c4fc8`
- `agents/openai.yaml`: `2071a83e1f895e448075aa8324a5cc5791f0fdaf5c05da0cacfb00627dddbb6e`
- `references/hermes-case-study.md`: `1bbeaabfef944542f00bd01d768f538d060e7689bd2aad37e157eab55d907161`
- `references/training-retrospective-report.schema.json`: `9155cf3a3af8cfac32e4930a821941df29ec4eb09938085f0f38838e87fce3a3`
- `scripts/validate_report.py`: `1f2f5767e8e473f4d069a91e7dcdde3149e1168f6fedc028eaab02609372e8a8`
- `scripts/self_test.py`: `8101eed9ebec392784f04d75dad4949a78a5ee9188e9244c615897ed24c2ccd6`
- `forward-test-report.json`: `c03011addd556e0e7e37a6dc12585cb5d7b369c203b890853672d2623f0c6ed5`

## Validation evidence

- Skill Creator `quick_validate.py`: `PASS`.
- JSON Schema draft 2020-12 meta-validation: `PASS`.
- Synthetic 200-attempt forward report validated against schema and cross-field rules: `PASS`.
- Positive／negative self-test: `8/8 PASS`:
  - valid report accepted;
  - read-only report claiming applied writeback rejected;
  - zero-proof success verdict rejected;
  - missing activity-mapping evidence code rejected;
  - inconsistent safety total rejected;
  - inconsistent adoption denominator rejected;
  - system improvement with missing adoption contract rejected;
  - complete mapping without per-attempt links rejected.
- Independent agent forward-test cycle:
  1. first result `PASS_WITH_GAPS` and identified eight content omissions;
  2. second review identified `2 P1 + 2 P2` machine-enforcement gaps;
  3. third review identified `1 P1 + 1 P2` contradiction paths;
  4. final re-test: `FINAL_PASS`, no remaining P1/P2.
- `git diff --check`: `PASS`.

## First bounded use

Before the next Hermes experiment, invoke the Skill and emit its machine-readable report. The current Hermes route remains `QUALITY_NOT_PROVEN / PROMOTION_BLOCKED`; the next authorized work is still 20/20 named-human rubric labels, not more blind provider calls.
