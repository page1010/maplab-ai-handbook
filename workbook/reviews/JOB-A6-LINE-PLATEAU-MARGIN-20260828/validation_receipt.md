# LINE 方法重設＋隱藏成本回收 Validation Receipt

日期：2026-08-28
資料邊界：LINE／報價／照片為 private-local-only；外部只查公開 IG、公開同業價與官方研究方法。
外部寫入：0；客戶訊息：0；正式價格變更：0；公開發布：0。

## 1. LINE plateau live truth

- canonical job：`MAPJOB-20260827-224251-d291ad`
- 12 rounds／60 loopback Ollama calls；10/60 pass（16.7%）；單輪最高 40%；success streak 0。
- 12/12 round 的題目不同，沒有固定 canary；這不是可比較實驗。
- code commit：`86c1cf1 fix(hermes): stop blind LINE reruns on plateau`
- workflow／workbook／SOP commit：`665eb23 feat(margin): add hidden-cost recovery workflow`
- 真實無 `--data-root` resume 回：`bounded_pause / plateau_method_review_required`。
- live readback 保持 `round_count=12`、`attempt=6`、`loopback_ollama_calls=60`、`external_network_calls=0`、`customer_send=false`；證明熔斷後沒有再耗模型或 attempt。

## 2. MAPLAB 系統 readback

- 主 Sheet：`MAPLAB_外燴系統_v0.1`（ID `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg`）。
- live tabs 包含 `QUOTE_DRAFT`、`TERMS_MASTER`、`Orders`、`OrderLines`、`OrderCharges`、`Items`、`SALES_INTAKE`、`REVISION_LOG`、`CONVERSATION_LOG`。
- `SALES_INTAKE` 尚無額外要求、增量工時／成本、是否計費、豁免與 leakage 欄位；`REVISION_LOG` 只記前後值與原因；`Items.default_price` 有空值、cost 有資料。
- 2026 報價資料夾唯讀找到 29 份 native Sheets；照片根目錄抽取 100 項有 41 folders、39 HEIF、4 MOV、3 JPEG 等，尚缺 case／quote／asset 穩定 join。
- `MAPLAB_ASSET_LOG` 以 `file_id` 為 key；尚未把 case_id、quote_id、IG permalink 與 actual delivery 串成 leakage evidence chain。

## 3. 公開 IG 交付證據

Owner 已登入 Chrome 僅唯讀檢查 `maplabkitchen`；未按讚、追蹤、留言、私訊或儲存。

- AMD 案公開寫出「客製企業 Logo 食物小插旗」與「加購小鮮花」。
- 藝術活動公開展示四場現場人員與 Tray-passed service。
- Cléa 開幕公開描述依品牌調性調整餐點、器皿與整體呈現。
- 生日與遊艇產品發表案例顯示客製細節與複雜場域物流。

這些支持「MAPLAB 做得到且做過」，不單獨證明某案漏收。

## 4. 私有對話初篩

`scripts/maplab_margin_leak_scan.py` 本機掃描 train＋eval 共 20,256 rows／2,491 conversations。Receipt：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-initial-aggregate.json`，mode 0600；只輸出 aggregate，無原文、姓名、電話或 raw conversation id，network calls 0。

最高候選 conversation counts：客製範圍 972、第三方統包 686、搬運物流 455、變更 363、設備耗材 348、急件／等待 269。類別會重疊且有誤報；未 join 報價與實際交付前，已確認漏收金額維持 0。

## 5. 交付物

- 毛利機會 workbook：`outputs/01a03eed-f050-7e80-bb78-f2f05fd02f8b/maplab_hidden_cost_pricing_matrix_20260828.xlsx`
- workbook SHA-256：`709cc9125bb9b02d406c71d43780c4c9ea1317f2e2711d07400d5b26b6273a84`。
- 6 sheets、24 個 proposal-only 加價服務、9 類訊號、200-row 稽核表與完全成本／price floor／leakage formulas。
- 預覽：`maplab_hidden_cost_pricing_matrix_20260828_preview.png`、`_catalog_preview.png`、`_signals_preview.png`。
- workbook formula inspection 42 records，未發現 `#REF!`、`#DIV/0!`、`#VALUE!`、`#NAME?`、`#N/A`；dashboard、catalog、signals 三張 preview 已人眼檢查無重疊或裁切。

## 6. Tests run

```text
python3 -m unittest tests.test_hermes_line_training_supervisor tests.test_maplab_margin_leak_scan -v
34 tests / OK

python3 -m py_compile scripts/hermes_line_training_supervisor.py scripts/maplab_margin_leak_scan.py
PASS

node --check scripts/build_hidden_cost_pricing_workbook.mjs
PASS

live supervisor resume without --data-root
exit 0; plateau_method_review_required; round 12; calls 60; no new attempt
```

## 7. 未完成／下一步

本輪沒有把候選命中冒充真實漏收。50 個 hash-only 分層 calibration 已完成；下一個 bounded action 是固定 10 案 evidence-join pilot，再 join quote／OrderCharges／actual delivery／asset evidence。Owner 核准前不改 live price 或對客條款。

## 8. Durable heartbeat calibration（2026-08-28 01:53 Asia/Taipei）

- Plateau review：此 job 只有一份初始 aggregate receipt，沒有連續兩次相同 calibration method 的無改善紀錄；允許首次 `margin-calibration-v1`，未呼叫模型。
- Method contract：固定九類 quotas、SHA-256 deterministic sampling、conversation 跨類唯一；label precedence 為 `our_rework → included → true_candidate → false_positive → insufficient_evidence`。
- 結果：50 samples／50 unique hashes；18 `true_candidate`、22 `insufficient_evidence`、8 `false_positive`、2 `included`、0 `our_rework`。
- Privacy：raw text 0、customer identifiers 0、source conversation IDs 0、network 0、model calls 0、customer send false、live price write false。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-calibration-v1.json`，mode 0600，SHA-256 `812e313c24e449fbdb75210f9060de59bd107622cb1b9bd27ce14b8cadceef85`。
- Tests：`python3 -m unittest tests.test_maplab_margin_leak_calibrate -v` → 2/2 PASS；`python3 -m py_compile scripts/maplab_margin_leak_calibrate.py` → PASS。
- Repo checkpoint：`70077c0 feat(margin): calibrate hidden-cost candidates`。
- 解讀：label 是 deterministic prelabel，不是 human gold／confirmed leakage；confirmed leakage amount 保持 0。

## 9. 固定 10 案 evidence-location join（2026-08-28 02:18 Asia/Taipei）

- Plateau review：比較 aggregate scan 與 calibration fingerprint；只有一次 calibration，沒有連續兩次相同方法無改善。這輪改做 evidence-location join，不再加 round、seed 或分類規則。
- Method contract：`margin-evidence-join-v1`；fingerprint `9a739a7386e53b5f2d7391d772a573cd93050d75e531c57776ab909bee29cf17`；固定從 18 個 true candidates 以 method+hash 排序取 10。
- 結果：10/10 private source rows resolved；本機可見 3,625 個 LINE export files、1,042 個 quote `.gsheet` pointers，但固定十案沒有 name+year stable pointer match；沒有本機 `OrderCharges` export，也沒有 case-to-asset stable key。
- 四證據柱：baseline scope 0、actual delivery 0、incremental cost 0、charged fee 0；10/10 `insufficient_evidence`，confirmed leakage amount 0。
- Missing codes（各 10）：`BASELINE_SCOPE_UNVERIFIED_NO_QUOTE_CONTENT`、`ACTUAL_DELIVERY_UNVERIFIED_NO_ASSET_JOIN`、`INCREMENTAL_COST_UNVERIFIED_NO_COST_LEDGER`、`CHARGED_FEE_UNVERIFIED_NO_ORDERCHARGES_EXPORT`、`NO_STABLE_CASE_QUOTE_ASSET_JOIN_KEY`。
- Privacy：raw text 0、customer identifiers 0、source conversation IDs 0、customer-bearing paths 0、network 0、cloud content reads 0、model calls 0、customer send false、live price write false。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-evidence-join-pilot-v1.json`，mode 0600，SHA-256 `2cfc50a3250a84347dde5dab0840b3e2b66f088a96fc0e5a532fe3b211dd3758`。
- Tests：`python3 -m unittest tests.test_maplab_margin_leak_evidence_join -v` → 2/2 PASS；`python3 -m py_compile scripts/maplab_margin_leak_evidence_join.py` → PASS；private-label/source-ID leak audit → 0。
- Repo checkpoint：`bfb6854 feat(margin): pilot private evidence joins`。
- Next：同一十案改用 read-only Google source bridge 取最小 join fields，hash 後才落 receipt；若仍 zero stable joins，產 schema proposal，不改 live Sheet。

## 10. Live Google join-key bridge（2026-08-28 02:48 Asia/Taipei）

- Plateau review：最近三個 methods 為 aggregate scan、`margin-calibration-v1`、`margin-evidence-join-v1`；沒有重跑相同 fingerprint。本輪只改 join source，固定十案不變。
- Method：`margin-google-join-bridge-v1`；fingerprint `8c96645e45090a62ab6d3a19c3b945fb1f24459d6920e5741edee2e04fdf4ff1`。
- Live readback：`SALES_INTAKE=45` minimal rows、`Orders=693`、`OrderCharges=184`、2026 quote native Sheets `159`；ASSET_LOG header 無 case/quote/order key。
- Fixed-ten coverage：2024=2、2025=3、2026=5；`SALES_INTAKE`／`Orders`／quote file name candidates／OrderCharges-via-name candidate 都是 0；stable identity joins 0、four-pillar confirmed 0、confirmed leakage amount 0。
- First bounded run 先遇到兩個含 `2026` 的 folder（`2026` 與 `2026外燴訂單`）；三層審查後以 exact canonical folder name 解決，沒有請 Owner、沒有擴權，也沒有把第一個 error 算成新方法 attempt。
- Privacy/read-only：Google source reads 12；Google writes 0、OAuth token writes 0、new third-party private-data egress 0、model calls 0、customer send 0、raw text/identifier/path/Google ID receipt leaks 0。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-google-join-bridge-v1.json`，mode 0600，SHA-256 `c757d2c055b678ee05ba931002ff8732b7f0d5134e041c53eb50b30785e15c4a`。
- Tests：三個 margin modules focused unittest 6/6 PASS；`py_compile` PASS；private-label/source-ID audit 0。
- Repo checkpoint：`0ed12cb feat(margin): audit live Google join keys`。
- Schema proposal：`docs/margin-leak-evidence-join-schema-proposal.md`，proposal-only；未改 live Sheet。
- Next：停止 conversation-first random holdout，改從已有 quote＋OrderCharges 的五個 2026 orders 往回建 local shadow link；two-anchor 不成立就停，不擴 fuzzy matcher。

## 11. Fixed-five join-first shadow（2026-08-28 03:18 Asia/Taipei）

- Plateau review：最近三個 fingerprints 為 calibration `7e65e7be...`、evidence join `9a739a73...`、Google bridge `8c96645e...`，沒有連續相同 method 無改善。本輪只改 join direction，從 evidence-rich Orders 往回找 LINE。
- Method contract：`margin-join-first-shadow-v1`；fingerprint `cfe227ba61206a7a1825aa9a960054fe8f9ca6858ac8152819a4ab6c36e09ae0`；hypothesis、changed variable、fixed-five holdout、expected delta 與 stop-loss 均已落 receipt。
- Live readback：`Orders=693`、`OrderCharges=184`、eligible 2026 orders=6、LINE archive=3,625 files；deterministic fixed-five selection manifest `5fe0f00d...`。
- Identity result：3/5 沒有 two-anchor candidate；2/5 分別有 8 與 9 個 ambiguous candidates；unique stable link 0。全年日期、去 generic/低熵 identity、至少 20 字元 Google Sheet ID、兩種獨立 exact anchors，ambiguous 一律 fail closed。
- 四證據柱：baseline scope 0、actual delivery 0、incremental cost 0、charged fee 0；5/5 `insufficient_evidence`，confirmed leakage amount 0。
- Missing codes：四柱未證各 5、`NO_TWO_ANCHOR_LINE_LINK=3`、`AMBIGUOUS_TWO_ANCHOR_LINE_LINK=2`。
- Privacy/read-only：Google source reads 4；raw text、customer identifiers、source conversation IDs、customer-bearing paths、raw Google IDs、new third-party egress、OAuth token writes、model calls、customer send、Google/live price writes 全為 0。
- Artifact：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-join-first-shadow-v1.json`，mode 0600，SHA-256 `55ce24ff8eeea3136d14a80764ed4dff57500c4414c2807c433ab47bbd714b52`。
- Verification：四個 margin modules focused unittest 13/13 PASS；`py_compile` PASS；independent audit 對日期、identity entropy、prior provenance、manifest、ambiguous split、stdout privacy 複審 PASS。
- Repo checkpoint：`444c73a feat(margin): pilot join-first shadow links`。
- Stop-loss decision：沒有 unique two-anchor link，禁止再擴 name/fuzzy matcher；下一 repair point 是 proposal-only intake-time `case_id` capture contract，先用 synthetic five-stage fixture 驗證，不改 live Sheet。

## 12. Intake-time Case-ID synthetic contract（2026-08-28 03:49 Asia/Taipei）

- Plateau review：最近三個 fingerprints 為 evidence join `9a739a73...`、Google bridge `8c96645e...`、join-first `cfe227ba...`；後兩輪 verified improvement 都是 0，依 stop-loss 不再推進 historical inference，repair point 改 prospective intake capture。
- Method contract：`margin-intake-case-id-contract-v1`；fingerprint `a1573a74b88222ae10c2b8edcbeaa9c7bdf2f139596df6be6c33db7b2bea2123`；model=`none`、fixed-ten synthetic holdout、deterministic referential-integrity evaluator。
- Result：10/10 expected outcomes PASS；valid case chain 5/5。Case Store 與 `SALES_INTAKE` 必須各有一個同 key acknowledgement，缺任一邊不建立 quote；quote gate check＋insert 同鎖，late duplicate acknowledgement fail closed。
- Durable intake：synthetic SQLite ledger 以 source-event primary key、case unique constraint、`BEGIN IMMEDIATE`、FULL sync 通過 fresh-instance replay 與 two-connection race。同 event＋同 payload 回既有 key；同 event＋不同 payload 回 `REPLAY_CONFLICT`。
- Migration boundary：cutover 用 ingestion cursor／snapshot，不用 event date；historical blank 保持 `LEGACY_UNLINKED`，fuzzy/name/date/content-hash auto-link forbidden；post-cutover 必須由 ledger exact event→case readback 證明。
- Current-system read-only gaps：`LineWebhook.gs` 留空 case_id、Case Store row/date fallback、`Code.gs` 另生秒級 `Q...`、live `SALES_INTAKE` header 與 repo positional writer 不相容、Orders／OrderCharges／ASSET_LOG 缺完整 foreign keys；`/casequote` raw LINE context 另有 cloud fallback。這些只記 plan boundary，本輪未修改 production file。
- Receipt：`/Users/pagemacmini/.maplab/margin-leak-audit/20260828-case-id-capture-contract-v1.json`，mode 0600，parent 0700，SHA-256 `b5f0c17824c2486b4fa1c3ee228cf5fae51a0044662264f5e48cc37d8696206d`；deterministic body `4fc873790f2bd023ba7c936d13631c3b171ac49ea0817a11d9925b9a0648bf2f`。
- Privacy/no-write：exact top-level＋nested＋per-scenario key/value allowlist、ISO timestamp、fixture/body hash、raw-case-ID reject；network/model/Google write/customer send/price write/history mutation/new private egress 全 0，confirmed leakage amount 0。
- Verification：contract 16/16 PASS；五個 margin modules focused suite 29/29 PASS；`py_compile` PASS；兩個 independent red-team 最終 PASS。Implementation `4ecda3f`。
- Decision：`PROPOSAL_ONLY / eligible_for_separate_live_review`，不是 live adoption。下一步只做 no-write integration patch plan、migration/rollback/readback 與 local fixture compatibility tests；不部署 GAS、不改 live Sheets。
