# Hidden-cost objective plateau review — 2026-08-28

## Identity and decision

- Role: MAPLAB durable-job continuation engineer
- Environment: `/Users/pagemacmini/maplab-ai-handbook`
- Job: `MAPJOB-20260828-HIDDEN-COST-001`
- Method: `margin-objective-plateau-review-v1`
- Fingerprint: `aac545d032f904a43bdb34b08f273c78d4a2ec0637c161a58074956bd0c7ae08`
- Decision: `OBJECTIVE_PLATEAU_CONFIRMED / REROUTE`
- Domain attempt consumed: `false`（維持 attempt 9/12）

廣版 G2 backup exclusion/index fixture 有工程價值，但不是目前隱藏成本
任務的阻塞點。它被延後為 future live-migration precondition；本 job 立即
回到 fixed-three 本機 four-pillar evidence packet。

## Last-three receipt plateau

| Method | Supporting delta | Owner-facing delta |
|---|---|---|
| `margin-deployed-source-inventory-v1` / `d282b0fe...` | deployed／local／historical truth與 modes盤點 | stable join 0；four-pillar verified 0；confirmed leakage 0；live capture false |
| `margin-private-root-deployed-readback-plan-v1` / `fa7086a1...` | static consumer/migration/readback gates | stable join 0；four-pillar verified 0；confirmed leakage 0；live capture false |
| `margin-private-root-resolver-prototype-v1` / `3dd861d0...` | synthetic resolver/copy-ledger runtime | stable join 0；four-pillar verified 0；confirmed leakage 0；live capture false |

Fingerprints不同，只證明方法不同。最近三輪完成的都是 supporting work；
Task Card 唯二未完成 acceptance 仍是 four-pillar evidence join與Owner核准
正式品項／價格。

## Runtime contradiction readback

主 agent與兩個獨立稽核重跑 G1 helper，確認：

1. `validate_backup_index()` 的 `classified_repo_paths=0` 是固定回傳，沒有從
   tree/index重算。
2. `case_store/not-a-generation`、`case_store/repository/private.db`、
   `backup_policy/arbitrary-new-class` 三個不完整／未知 logical source 都被接受，
   且仍回報 zero classified paths。
3. sealed generation加入一個未列帳 regular file後，既有 ledgered artifact仍
   可讀；因此 exact tree membership尚未驗證。

範圍修正：G1 對「ledger已列出的檔案」之 actual-byte hash/readback、generation
CAS及rollback證據仍成立；`backup logical allowlist`、`zero classified repo
paths`與`exact tree membership`不得視為已驗，live adoption仍為 `HOLD`。

## Live safety observation（read-only）

- `~/maplab_backup` 有 8 generations，root mode `0755`。
- current `state/dispatch_backup_index.json` 的 parent/file modes為
  `0755/0644`。
- 只按檔名／logical class計數，current index含 non-example env 7、Case Store
  2、dispatch 83、`.mcp.json` 1、`cookies.txt` 1、舊 backup index 1。
- live backup仍以整 repo `rsync -a --delete` 加 `os.walk` index運作；synthetic
  G2不會停止這個 propagation。

本輪沒有讀 secret/customer payload、沒有修改 backup script／plist／schedule／
權限／歷史副本。這是獨立安全問題，應另立修復任務；不可把它偷偷擴成
hidden-cost job 的無限安全工程。

## First-principles five questions

1. **真正目的**：從客戶要求、原報價、實際交付、增量成本與已收費證據，
   找到本來不在標準範圍但已代解且未收費的項目，產品化為合理加價服務。
2. **目前限制**：缺 `case_id → quote_id → OrderCharges → asset_id` 的可信
   evidence chain；不是缺 backup synthetic index。
3. **未證假設**：未證 G2 是分析真實案例前置條件、53 review artifacts與
   毛利證據直接相關、synthetic policy代表 live writers，或完成 G2後即獲准
   live migration。
4. **最小可否證實驗**：從18個既有 `true_candidate` hashes deterministic固定
   取3案，只在本機回讀原對話，對每案逐柱找原報價、實際交付、增量成本與
   `OrderCharges`；不做 bulk fuzzy backfill。
5. **停止條件**：三案完成後停止；沒有至少兩個獨立 exact anchors 的案保持
   `INSUFFICIENT_EVIDENCE`。若0/3達 four-pillar verified，下一步只提交
   prospective case-id live-capture Owner-review proposal，不再增加 synthetic
   infrastructure round。

## Next bounded action contract

- Method version: `margin-fixed-three-four-pillar-packet-v1`
- Selection: 對18個 calibration `true_candidate` 依
  `sha256(method_version|candidate_hash)`排序取前3，manifest固定後不得換案。
- Private route: 原文、姓名、電話、地址、報價與素材只在本機 domain worker；
  repo receipt僅留 hashes、pillar status、missing codes與aggregate。
- Per-case evidence: request row hash、baseline quote hash/readback、delivery／asset
  hash/readback、incremental cost basis、charged-fee／OrderCharges readback。
- Acceptance: 每柱只接受 exact source＋hash＋唯一 anchor；缺一不得算 confirmed
  leakage。可產 owner-only private packet與sanitized receipt，不改 live Sheet。
- Stop-loss: 不擴 fuzzy/name matcher、不改 backup／GAS／Sheets、不對客發送、不
  正式寫價格、不把私有資料送 DeerFlow/OpenRouter。
- Objective metrics: `four_pillar_verified_count`、
  `confirmed_leakage_amount`、`owner_reviewable_case_packet_count`。

## Safety counters

- network calls: 0
- model calls: 0
- private payload egress: 0
- credential/customer payload reads for this review: 0
- live path mutations: 0
- backup／launchd／permission writes: 0
- Google／price／customer writes: 0
- customer sends／publication／deployment: 0

Three independent read-only reviews agreed that broad G2 is objective drift and
should be deferred; the security audit additionally reproduced the G1 backup
validator's false-zero and exact-tree gaps.
