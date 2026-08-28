# T-A5-A6-HIDDEN-COST-RECOVERY-001 — 隱藏成本與可加價服務回收

```yaml
status: OWNER_REVIEW_PROSPECTIVE_CASE_ID_CAPTURE
assigned_session: 2026-08-28 / A1-A5-A6 Codex
last_committed_by: Codex / 2f5d5b3 (G1 governance handoff); c44e8bc (synthetic private-root resolver/copy-ledger runtime); 5535e89 (private-root/deployed-readback static hardening gates); b7ccd3e (read-only deployed-source/header inventory); 1b2a2af (no-write case-id integration gates); 4ecda3f (synthetic intake case-id contract); 444c73a (fixed-five join-first shadow); 0ed12cb (live Google join bridge); bfb6854 (10-case evidence join); 70077c0 (50-case calibration); 665eb23 (workflow/workbook); 86c1cf1 (supervisor guard)
owner_goal: 從真實對話與交付證據找出本來不在標準範圍、MAPLAB 實際代解且未收費的工作，產品化為合理加價服務，提升專案毛利。
data_class: private-local-only
```

## 已確認的系統事實

- 主報價 Sheet 已有 `SALES_INTAKE`、`REVISION_LOG`、`CONVERSATION_LOG`、`OrderCharges` 與 `Items`，但沒有額外要求、實際工時、增量成本、是否已收費、豁免原因與漏收金額的完整閉環。
- `Items.default_price` 仍有空值，而成本欄存在；現有成本觀念偏餐點成本，尚未穩定納入行政、設計、搬運、停車、設備、垃圾、第三方協調與場地復原。
- MAPLAB 公開 IG 已證實做過 Logo 食物插旗、鮮花加購、Tray-passed 駐場服務、依品牌調性重做菜單／器皿／陳列等可獨立交付。
- 本機初篩 20,256 rows／2,491 conversations；輸出只有 aggregate。命中是 review queue，不是可向客戶追收的證明。

## 交付物

- `outputs/01a03eed-f050-7e80-bb78-f2f05fd02f8b/maplab_hidden_cost_pricing_matrix_20260828.xlsx`
- `scripts/maplab_margin_leak_scan.py`
- `scripts/maplab_margin_leak_evidence_join.py`
- `scripts/maplab_margin_google_join_bridge.py`
- `scripts/maplab_margin_join_first_shadow.py`
- `scripts/maplab_case_id_capture_contract.py`
- `scripts/build_hidden_cost_pricing_workbook.mjs`
- `docs/margin-leak-evidence-join-schema-proposal.md`
- `docs/margin-leak-case-id-capture-contract.md`
- `docs/margin-leak-case-id-integration-plan.md`
- `scripts/maplab_case_id_integration_plan.py`
- `tests/test_maplab_case_id_integration_plan.py`
- `scripts/maplab_deployed_source_inventory.py`
- `tests/test_maplab_deployed_source_inventory.py`
- `docs/margin-leak-deployed-source-inventory.md`
- `scripts/maplab_private_root_hardening_plan.py`
- `tests/test_maplab_private_root_hardening_plan.py`
- `docs/margin-private-root-deployed-readback-hardening-plan.md`
- `scripts/maplab_private_root_resolver_prototype.py`
- `tests/test_maplab_private_root_resolver_prototype.py`
- `docs/margin-private-root-resolver-prototype.md`
- `scripts/maplab_margin_fixed_three_packet.py`
- `tests/test_maplab_margin_fixed_three_packet.py`
- `workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/fixed_three_four_pillar_receipt.json`
- `docs/margin-leak-prospective-case-id-live-capture-owner-review.md`
- `workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/objective_plateau_review_20260828.md`
- `workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/validation_receipt.md`
- private aggregate：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-initial-aggregate.json`

## 必須建立的兩張表

### ADDON_CATALOG

至少包含 `addon_id`、對客品名、標準內含範圍、可計費觸發、單位、完全成本、最低收費、建議區間、來源、信心、Owner status、有效日起訖。

### MARGIN_LEAK_EVENT

至少包含 `leak_id`、case/quote hash、category、baseline scope、requested scope、evidence hash/path、labor/admin/material/vendor/equipment/transport/waste cost、target margin、recommended fee、charged fee、unbilled leakage、decision status、waiver reason、review owner。

## 判定順序

1. 先判標準範圍與我方錯誤；我方補救不得收費。
2. 再判 `INCLUDED`／`BILLABLE`／`CHANGE_ORDER`／`PASS_THROUGH`／`DECLINE_OR_RISK`／`OWNER_WAIVER`。
3. 只有同時存在對話要求、實際交付、增量成本、原報價未包含四種證據，才可標 confirmed leakage。
4. 正式價格以完全成本／`(1-目標毛利)` 與最低收費取高；餐點毛利、專案毛利、加價服務毛利分開。
5. 所有正式價目、條款與客戶訊息在 Owner 核准前只做 proposal／preview。

## 安全與治理邊界

- LINE 原文、姓名、電話、地址、預算、報價、照片、browser login state、cookies、secrets 不得送 DeerFlow、OpenRouter 或任何新第三方。
- 公開同業研究可走 hardened DeerFlow；私有交叉比對只能在本機 deterministic worker。
- 不對客自動發 LINE、不追溯加價、不改 live quote price、不公開發布、不交易。
- 特殊飲食只針對獨立製程、包裝、標示與分流的實際增量成本；不得稱為「過敏加價」，不得保證零交叉接觸。

## Acceptance

- [x] 初版 24 項 ADDON_CATALOG 與公開來源／內部邊界。
- [x] privacy-safe aggregate scanner；無原文、無識別碼、network calls 0。
- [x] 可填寫的 200-row MARGIN_LEAK_EVENT workbook 與完全成本／漏收公式。
- [x] 本機抽 50 個高優先候選做 taxonomy calibration，留下 hash 與標籤，不複製原文。
- [x] 固定 10 個 true-candidate hashes 做首次 evidence-location join；明列 join 缺口，不把 request cue 當漏收。
- [x] 以 live Google read-only bridge 驗 10 案並產 field-level schema proposal；無 live write。
- [x] 從已有 quote＋OrderCharges 的固定五個 2026 Orders 做 hardened join-first shadow；0 unique links 後依 stop-loss 停止歷史 fuzzy backfill。
- [x] 以 10 個 synthetic holdouts 驗 intake-time `case_id` 五階段 contract；Case Store／SALES_INTAKE 各自 readback、restart／two-connection、migration provenance、late duplicate 與 nested receipt red-team 全 fail closed，沒有 live write。
- [x] 建立 exact source-to-adapter no-write integration plan；20 個 pinned source anchors、25 個 synthetic fail-closed fixtures、4 個 prior live-header pins 與 7 個 plan gates 全通過，並明列 direct GAS Web App 無法取得 LINE signature header，必須先有 header-capable ingress。沒有 deploy、live write 或 durable outbox overclaim。
- [x] 完成 read-only deployed-source/header inventory；4/4 fresh full-header hashes match，quote local bundle/binding 與 historical deployment分層，current quote/LINE deployed revision、Orders/OrderCharges writer仍明列 `UNRESOLVED`。Case Store DB/fallback 與 OpenClaw 405 個固定 bundle artifacts 的 `0755/0644` exposure、`REPO_PATH` hash/match、OAuth `0644`＋Apps Script readonly scope缺失均 fail closed；71/71 related tests與三個 final red-teams PASS，無 deploy/write/private egress。
- [x] 完成 no-write private-root/deployed-readback static hardening gates；67 source pins、62 consumer anchors、10 private-env tracked refs、4 installed runtime files、12 target contracts、39/39 policy fixtures均 exact。Case Store／bot env／review／dispatch／backup／provider credentials仍 fail closed，Hermes training只到 mode-only inventory、`owner_only=false`；resolver/copy-ledger runtime與 live migration均未宣稱完成。17/17 focused、88/88 related與三個 final red-teams PASS。
- [x] 完成 `TemporaryDirectory` synthetic resolver＋actual-byte ledger G1；8/8 logical surfaces、53/53 non-adapter fixtures、21/21 executable receipt scenarios、25/25 focused與120/120 MAPLAB discovery tests PASS。Generation＋epoch CAS、exclusive final generation、destination readback、interrupted/EXDEV/fsync/concurrency、durable pre-write barrier、tampered rollback與 receipt forgery均 fail closed。後續 runtime audit確認 backup helper 的 zero classified paths是固定值且 exact tree未驗；因此 G1只保留「ledgered artifacts／resolver」範圍，backup allowlist、tree membership、live resolver/migration/consumer/SQLite皆未完成。
- [x] 完成 objective-level plateau review；最近三個 infra fingerprints雖不同，但 four-pillar verified、confirmed leakage與 live case capture的 business delta全為0。廣版 G2 延後為 future live-migration precondition，re-route不消耗 domain attempt（維持9/12）。
- [x] 完成 `margin-fixed-three-four-pillar-packet-v1` exact-anchor availability experiment；固定三案不可替換，3/3 request/source exact hash verified，baseline／delivery／incremental cost／charged fee均0/3 verified，故3/3維持 `INSUFFICIENT_EVIDENCE`、confirmed leakage 0。Attempt 9→10且consumed=true；停止歷史join並產具體 prospective case-id live-capture Owner proposal。
- [ ] 以 quote、OrderCharges、交付／照片 evidence join，估出 confirmed leakage；未 join 前金額必為 0。
- [ ] Owner 核准第一批正式品項、價格、標準內含量與生效日後，才另開 live Sheet／GAS 變更任務。

## Next Bounded Action

State為 `OWNER_REVIEW`，不自動執行。Owner只需在 `docs/margin-leak-prospective-case-id-live-capture-owner-review.md` 選：1) bounded live shadow implementation；2) local-only rehearsal；3) defer。未選前不得再跑歷史第4案、fuzzy/name/date join、另一輪infra，亦不得改 live Sheet/GAS/header ingress/backup／價格、send/publish/delete或私資外送。Owner核准後另開 bounded implementation job，不在本 job重用attempt 10。

## 2026-08-28 Calibration Receipt

- Method：`margin-calibration-v1`；fingerprint `7e65e7be6eec8e77bf71866928bcdf616bf0cb81948b473c985e739885422b30`。
- 固定分層 50 案／50 unique hashes：客製、統包、物流、變更、設備各 6；急件、特殊飲食、駐場、清潔各 5。
- Heuristic labels：`true_candidate=18`、`insufficient_evidence=22`、`false_positive=8`、`included=2`、`our_rework=0`。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-calibration-v1.json`；SHA-256 `812e313c24e449fbdb75210f9060de59bd107622cb1b9bd27ce14b8cadceef85`；mode 0600。
- Privacy readback：raw text 0、customer identifiers 0、source conversation IDs 0、network 0、model calls 0。
- 邊界：這是 deterministic triage，不是 human gold，也不是 confirmed leakage；已確認漏收金額仍為 0。

## 2026-08-28 Evidence-Join Pilot Receipt

- Method：`margin-evidence-join-v1`；fingerprint `9a739a7386e53b5f2d7391d772a573cd93050d75e531c57776ab909bee29cf17`；固定 10 hashes。
- Readback：10/10 private source rows resolved；本機可見 1,042 個 `.gsheet` pointer，但固定十案的 name+year stable match 為 0；本機 `OrderCharges` export 與 stable asset join 都不存在。
- 四證據柱：baseline scope 0、actual delivery 0、incremental cost 0、charged fee 0；10/10 都是 `insufficient_evidence`，confirmed leakage amount 仍為 0。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-evidence-join-pilot-v1.json`；SHA-256 `2cfc50a3250a84347dde5dab0840b3e2b66f088a96fc0e5a532fe3b211dd3758`；mode 0600。
- Privacy readback：raw text 0、customer identifiers 0、source conversation IDs 0、customer-bearing paths 0、network/cloud-content/model calls 0、customer send 0、live price write 0。
- 結論：這一輪的新產出不是漏收金額，而是證明目前缺 `case_id → quote_id → OrderCharges → asset_id` 的穩定 key；再跑 keyword/classifier 不會補出這條證據鏈。

## 2026-08-28 Live Google Join Bridge Receipt

- Method：`margin-google-join-bridge-v1`；fingerprint `8c96645e45090a62ab6d3a19c3b945fb1f24459d6920e5741edee2e04fdf4ff1`；與前兩輪不同，改讀 live Google key fields，固定十案不變。
- Live minimal rows：`SALES_INTAKE=45`、`Orders=693`、`OrderCharges=184`、2026 quote Sheets `159`；`MAPLAB_ASSET_LOG` live header 沒有 `case_id`／`quote_id`／`order_id`。
- 固定十案年份：2024=2、2025=3、2026=5；所有 name-based candidate matches 皆為 0，stable identity joins 0、four-pillar confirmed 0、confirmed leakage amount 0。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-google-join-bridge-v1.json`；SHA-256 `c757d2c055b678ee05ba931002ff8732b7f0d5134e041c53eb50b30785e15c4a`；mode 0600。
- Privacy/read-only：Google source reads 12；Google writes 0、token writes 0、new third-party egress 0、model calls 0、customer send 0、raw identifiers/path/Google IDs in receipt 0。
- Schema proposal：`docs/margin-leak-evidence-join-schema-proposal.md`；proposal-only，沒有修改 live Sheets。
- 方法結論：conversation-first 隨機樣本缺少 case key；下一輪改從已具 quote＋charge 的 order 往回 join，不再對同一十案重跑模糊配對。

## 2026-08-28 Join-First Shadow Receipt

- Method：`margin-join-first-shadow-v1`；fingerprint `cfe227ba61206a7a1825aa9a960054fe8f9ca6858ac8152819a4ab6c36e09ae0`；固定以 `sha256(method_version|order_id)` 從 6 個 eligible 2026 Orders 取 5 案。
- Live minimal rows：`Orders=693`、`OrderCharges=184`；本機 LINE archive 3,625 files。五案結果為 3 案沒有 two-anchor candidate、2 案有 8／9 個 ambiguous candidates、unique stable link 0。
- Stop-loss：全年日期、去低熵 identity、至少 20 字元 Sheet ID、兩種獨立 exact anchor；ambiguous fail closed，不擴 fuzzy matcher。四柱 verified 各 0、5/5 `insufficient_evidence`、confirmed leakage amount 0。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-join-first-shadow-v1.json`；SHA-256 `55ce24ff8eeea3136d14a80764ed4dff57500c4414c2807c433ab47bbd714b52`；mode 0600。
- Privacy/read-only：Google reads 4；raw text、customer identifiers、source conversation IDs、customer-bearing paths、raw Google IDs、new third-party egress、token writes、model calls、customer send、Google/live price writes 全為 0。
- Verification：四個 margin modules focused unittest 13/13 PASS、`py_compile` PASS、independent audit PASS；implementation `444c73a`。
- 方法結論：歷史 archive 無法可靠補出 unique identity chain；依事前 stop-loss 轉向 intake-time `case_id` capture，不再消耗 quota 重跑 name／fuzzy join。

## 2026-08-28 Intake Case-ID Contract Receipt

- Method：`margin-intake-case-id-contract-v1`；fingerprint `a1573a74b88222ae10c2b8edcbeaa9c7bdf2f139596df6be6c33db7b2bea2123`；changed variable 是從 historical identity inference 改成 prospective mint-once＋immutable foreign-key propagation。
- Fixed holdout：10/10 expected outcomes PASS；valid chain 5/5。Case Store／`SALES_INTAKE` 為兩個獨立且唯一 acknowledgement，任一缺失就禁止 quote；quote gate check＋insert 同鎖，late duplicate 被拒絕。
- Durable/provenance：owner-only synthetic SQLite ledger 以 source-event primary key、case unique constraint、`BEGIN IMMEDIATE`／FULL sync 通過 fresh-instance replay 與 two-connection race；post-cutover link 直接查 event→case，不接受 caller boolean。
- Migration：historical blank key 保持 `LEGACY_UNLINKED`／`INSUFFICIENT_EVIDENCE`；name/date/content hash/fuzzy auto-backfill 一律拒絕；confirmed leakage amount 仍為 0。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-case-id-capture-contract-v1.json`；SHA-256 `b5f0c17824c2486b4fa1c3ee228cf5fae51a0044662264f5e48cc37d8696206d`；mode 0600，parent 0700。
- Privacy/no-write：receipt 走 exact nested key/value allowlist、timestamp、fixture/body hash 與 raw-case-ID gate；raw/customer/source IDs/path 0、network/model/Google write/customer send/price write/history mutation/new private egress 全 0。
- Verification：contract tests 16/16 PASS、五個 margin modules focused suite 29/29 PASS、`py_compile` PASS、兩個 independent red-team 最終 PASS；implementation `4ecda3f`。
- 現況：這是 `PROPOSAL_ONLY`，不是 live adoption。唯讀盤點另發現 live `SALES_INTAKE` header 與 repo positional writer 不相容、quote 秒級 `Q...` 重生 key、Orders／charges／assets 缺 join fields，以及 `/casequote` raw LINE context 的 cloud fallback；下一步先做 no-write integration plan。

## 2026-08-28 Case-ID No-Write Integration Plan Receipt

- Method：`margin-case-id-integration-plan-v1`；fingerprint `201cf84e8090c12ba743f47f9073dc733a87dd7a57874729b6ce302e4c627133`；repair point 從 historical inference 改成 exact source-to-adapter plan，沒有重開 fuzzy backfill。
- Static gates：20/20 pinned source anchors、25/25 expected synthetic fixtures、4/4 prior live-header digests、7/7 plan gates；Orders writer 在 inspected paths 仍為 authoritative unresolved。
- LINE truth：direct Apps Script Web App event object 沒有 request headers，不能依 LINE 規範驗 `x-line-signature`＋untouched raw body；Phase 0 必須先選定 header-capable ingress、簽名驗證與 replay-bounded internal envelope，否則 LINE ingestion fail closed。
- Private/local guard：unknown data class、cloud provider、non-loopback、cloud/proxy/provider/model overrides、repo artifact root、unsafe modes 與 live/cloud flags 全 reject；receipt／parent 為 0600／0700。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-case-id-integration-plan-v1.json`；SHA-256 `bfcf5a5f7c887576017513e488a3b658debfc777c92d3cfbf1733de13edc3812`；body SHA `bb7ebccde0bef37ef614caccce6ecedd8edc6c5674d4235c2da9fe2a9192ec1a`。
- Verification：focused 20/20 PASS、related margin/case-id regression 29/29 PASS、三個 independent final audits PASS；implementation `1b2a2af`。
- Boundary：`STATIC_PLAN_VALIDATED / PROPOSAL_ONLY`；`eligible_for_live_change=false`、`durable_outbox_runtime_validated=false`、live adoption false、confirmed leakage amount 0。下一步只做 read-only deployed-source/header inventory。

## 2026-08-28 Deployed-Source／Header Inventory Receipt

- Method：`margin-deployed-source-inventory-v1`；fingerprint `d282b0fee8655a3cbc075bc332c0eb9ab2e5f18bac05abefdb7d63f97c5f53c0`；changed variable 是從 static plan 改成 local/historical/deployed 三層 truth、fresh full-header hashes與實際 private-root modes。
- Fresh headers：`SALES_INTAKE=15`、`Orders=29`、`OrderCharges=4`、`MAPLAB_ASSET_LOG=14`，4/4 SHA-256 match pinned plan。Connector metadata/header reads為 2/7（兩次 hash implementation failure照實保留），Google read operations 9、writes 0。
- GAS truth：quote canonical binding與 8-file local bundle digest verified；historical quote/LINE script/deployment fingerprints均 hash-only pinned。Current quote deployed revision仍 `UNRESOLVED`；separate `scripts/apps-script-line/`缺失，current LINE binding/manifest/version/source digest仍 `UNRESOLVED`。Direct GAS仍不可驗 LINE signature header。
- Writer truth：`writer-search-v2` 固定掃 67 current source files＋bounded Git selector，0/0 matches；quote GAS只寫 `SALES_INTAKE`，所以 `Orders`／`OrderCharges` authority維持 `AUTHORITATIVE_WRITER_UNRESOLVED`，沒有把零命中冒充「不存在」。
- Private roots：`REPO_PATH` override存在、salted fingerprint與 canonical repo match；Case Store dir/DB/fallback為 `0755/0644/0644`。OpenClaw review root `0755`，8 個固定 bundle filenames aggregate為 405/405 regular files at `0644`、owner-only 0、symlink 0。Google token metadata mode `0644`、3 scopes、exact Apps Script readonly scope缺失；全部 fail closed，不使用 credential上網。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-deployed-source-inventory-v1.json`；parent/file `0700/0600`；SHA-256 `2110647635fe3223e92bcf5ed421472774b68e339e59c60883f2d683af0dfd21`；body `c23563deae61f54aee6fa3e9e3b8d0e04b26e473556e2487f1e4dbd13c144fbc`。
- Safety：raw customer/text/Google IDs/secrets 0；Apps Script API、Google/deployment/credential writes、customer send、price write、history mutation、new private egress均 0。Receipt exact type/value/relation、unique manifests、same-key identifier poison、boolean/float count、future timestamp、root/credential forgery均 fail closed。
- Verification：focused 20/20、related margin suite 71/71、`py_compile`、live receipt reload與三個 independent final red-teams PASS；implementation `b7ccd3e`。
- Decision：`READ_ONLY_INVENTORY_COMPLETE / LIVE_ADOPTION_HOLD`；`eligible_for_live_change=false`、`deployed_source_truth_complete=false`、confirmed leakage 0。下一步只做 no-write private-root/deployed-readback hardening plan。

## 2026-08-28 Private-Root／Deployed-Readback Static Hardening Receipt

- Method：`margin-private-root-deployed-readback-plan-v1`；fingerprint `fa7086a124459dfa1ca3c872be7e4247d0e490e85dcc2e0ec3838626586bdde2`；changed variable 是從 mode/deployed inventory 改為 consumer-complete target／cutover／readback／rollback contract，沒有重跑 historical join。
- Exact manifests：67/67 source pins、62/62 consumer anchors、10/10 tracked private-env refs、19+4 Google token consumers、4/4 installed LaunchAgent files、12 target contracts、39/39 generated policy fixtures。OpenRouter YAML、local YAML、disabled extensions、provider copy writer、Hermes loop/supervisor/plists與兩個 non-adapter review writers均納入 drift gate。
- Current boundary：Case Store、bot env、review、dispatch、backup、provider credentials、shared Google/clasp均維持 unsafe／unresolved；Hermes training只有 `0700/0600` mode histogram，因 UID／ACL／type／hardlink／runtime binding未驗，明確 `owner_only=false`。Quote／LINE current deployed revision、Orders writer與header-capable ingress仍 unresolved。
- Apps Script future readback：dedicated credential、exact 2 readonly scopes、3 GET、version-bound content與deployment metadata double-read；shared token、clasp、MCP與write methods均禁。這是設計，不是 API receipt。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-private-root-readback-plan-v1.json`；parent/file `0700/0600`；SHA-256 `47cb08a36c5523842a7b81306c63244c79ddd42b5bf90c87b81ea89083752505`；body `c204ea0b98e25b683f05e29f291072a227ba4fe0e795f1a4c8e7bc1515a58733`。
- Privacy/no-write：credential/env payload、customer rows、raw IDs、network、Apps Script API、chmod/copy/move/restart/deploy/Google/customer send/model/new private egress均 0；只寫 owner-only receipt。
- Verification：focused 17/17、related suite 88/88、`py_compile`、live receipt reload與三個 independent final audits PASS；implementation `5535e89`。
- Decision：`STATIC_DESIGN_INVENTORY_VALIDATED / HOLD`；`resolver_copy_ledger_runtime_validated=false`、`eligible_for_live_change=false`、live migration false、confirmed leakage amount 0。下一步只做 synthetic resolver/copy-ledger runtime prototype。

## 2026-08-28 Synthetic Private-Root Resolver Runtime Receipt

- Method：`margin-private-root-resolver-prototype-v1`；fingerprint `3dd861d083f3e77ee22deb0858a993fe5afdcf377cabc356d58dbc0d0753fec8`；changed variable 是從 static predicates 改成 executable `TemporaryDirectory` resolver／copy-ledger runtime。
- Runtime：8/8 distinct surfaces，`shared_review_non_adapter` exact 53/53；source stream與重新開啟 destination SHA/size相符，ledger/seal只含 logical path。Final generation以 exclusive `mkdir` 建立，active pointer以 generation＋epoch CAS發布；authoritative-write barrier先持久化，再允許寫入。
- Holdout：21/21 built-in scenarios PASS；另有25/25 focused與120/120 MAPLAB discovery tests、`py_compile`、三個 independent exact-byte audits PASS。Post-pointer `fsync` ambiguity保留sealed target、tampered rollback拒絕、stat→FIFO swap不阻塞、repo overlap與generation race拒絕、timestamp/fixture/metric/provenance forgery拒絕。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-private-root-resolver-prototype-v1.json`；parent/file `0700/0600`；SHA-256 `03ef6160d2f5856285992728b2865199f5e70e31fa9eebf5a8f6c39e59866df8`；body `ce995142fc8b9e1b9ee2b08710a1abd90088eb453b89dac41ae46ca71f75720f`；implementation `c44e8bc`。
- Boundary：這只證明 synthetic G1。`live_resolver_copy_ledger_runtime_validated=false`、`eligible_for_live_change=false`、live migration/consumer/SQLite/writer/header ingress均 false/unresolved，confirmed leakage amount 0。Injected EXDEV不等於真實跨碟，fsync不等於 power-loss proof，現有 private roots仍 `owner_only=false`。
- Deferred P1：sealed generation會驗 ledger列出的每個 artifact，但尚未拒絕額外 unledgered files；resolver無法讀取額外檔，仍須在G2/G3補 exact tree-membership gate，live adoption前必關閉。

## 2026-08-28 Objective-Level Plateau／Course-Correction Receipt

- Method：`margin-objective-plateau-review-v1`；fingerprint `aac545d032f904a43bdb34b08f273c78d4a2ec0637c161a58074956bd0c7ae08`；changed variable是從 method-fingerprint新穎度改成Owner acceptance與business metric delta。
- Plateau：deployed inventory `d282b0fe...`、static hardening `fa7086a1...`、resolver G1 `3dd861d0...`三輪的 supporting delta各自成立，但 stable join、four-pillar verified、confirmed leakage與 live capture readiness全為0／false；objective-level plateau成立。
- Runtime correction：重跑證實 G1 backup helper接受3個不完整／未知 logical sources仍硬回 `classified_repo_paths=0`，sealed generation加 extra unledgered file後既有read仍PASS。G1 ledgered artifact hash/readback仍有效；zero-sensitive backup與 exact tree membership不再視為已驗。
- Decision：廣版 G2延後為 future live-migration precondition；本 review `attempt_consumed=false`，job attempt維持9/12，立即回 fixed-three four-pillar evidence packet。安全議題另行處理，不把 hidden-cost job擴成無限 infra工程。
- Artifact：`workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/objective_plateau_review_20260828.md`。

## 2026-08-28 Fixed-Three Exact-Anchor／Owner-Review Receipt

- Method：`margin-fixed-three-four-pillar-packet-v1`；fingerprint `6ad1df463b57ca15b0b0aba9700735e9bfb3e07608607dabe4472891dcd166c8`；這是 exact-anchor availability experiment，不冒充能驗成功路徑的通用 four-pillar validator。
- Selection：18個 `true_candidate` 的 exact set digest `686cd542...`；依 `sha256(method|candidate_hash)`固定前三案，不可失敗後換第4案。
- Readback：request row＋source exact hash `3/3`；baseline quote content、actual delivery/asset、actual incremental cost、authoritative charged fee均 `0/3`。`OrderCharges` writer與charge/cost/discount/note語意仍 unresolved，row presence或absence不得當已收費／0。
- Decision：3/3 `INSUFFICIENT_EVIDENCE`；four-pillar verified 0、confirmed leakage amount 0；stop historical join，轉 prospective case-id live-capture Owner review。
- Attempt：`9→10/12`、`attempt_consumed=true`；同packet replay只驗既有SHA並no-op，不覆寫、不再加attempt。
- Private packet：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-fixed-three-four-pillar-packet-v1.json`，parent/file `0700/0600`，SHA `f8bcedecc8121be7de632560562eb5a1207713bc451143626970ec7f3c52953a`。
- Sanitized receipt：`workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/fixed_three_four_pillar_receipt.json`，SHA `950dd71fff8d47d46c7878a884eba44a56b3e0f8babe16ba39e7dd0fb31e9477`，body `862cab4d...`；只含hash/status/missing code/aggregate。
- Verification：7/7 focused、13/13 related、`py_compile`、idempotent replay與三個 independent read-only reviews PASS；network/model/private egress/Google write/customer send/live price write/deployment/backup-permission mutation均0。
- Owner artifact：`docs/margin-leak-prospective-case-id-live-capture-owner-review.md`；已列schema、production write path、privacy、10-case／14-day canary、rollback/readback與三個選項；沒有執行任何選項。

## Resume Prompt

我是 A5/A6 毛利漏損稽核工程師，環境是 `/Users/pagemacmini/maplab-ai-handbook`。冷啟動先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本卡、validation receipt、canonical job、`fixed_three_four_pillar_receipt.json`與 `docs/margin-leak-prospective-case-id-live-capture-owner-review.md`。先驗 private packet SHA `f8bcedec...`、method `6ad1df46...`、eligible digest `686cd542...`、attempt `9→10` consumed、3/3 request、0/3 four-pillar、confirmed leakage 0、7 focused＋13 related tests。State=`OWNER_REVIEW`：fixed-three已完成，禁止重跑／換第4案／fuzzy/name/date join／infra round或再加attempt。只等Owner選 live shadow、local-only rehearsal或defer；未核准不得改 live Sheet/GAS/header ingress/backup／價格、send/publish/delete或把 private bytes送DeerFlow/OpenRouter。Owner核准後另建bounded implementation job，明列authorization、rollback、live readback與no-price/no-send gates。
