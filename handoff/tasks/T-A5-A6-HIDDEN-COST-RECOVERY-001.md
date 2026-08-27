# T-A5-A6-HIDDEN-COST-RECOVERY-001 — 隱藏成本與可加價服務回收

```yaml
status: ACTIVE_INTAKE_CASE_ID_CAPTURE
assigned_session: 2026-08-28 / A1-A5-A6 Codex
last_committed_by: Codex / 444c73a (fixed-five join-first shadow); 0ed12cb (live Google join bridge); bfb6854 (10-case evidence join); 70077c0 (50-case calibration); 665eb23 (workflow/workbook); 86c1cf1 (supervisor guard)
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
- `scripts/build_hidden_cost_pricing_workbook.mjs`
- `docs/margin-leak-evidence-join-schema-proposal.md`
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
- [ ] 以 quote、OrderCharges、交付／照片 evidence join，估出 confirmed leakage；未 join 前金額必為 0。
- [ ] Owner 核准第一批正式品項、價格、標準內含量與生效日後，才另開 live Sheet／GAS 變更任務。

## Next Bounded Action

建立 proposal-only 的 intake-time `case_id` capture contract：以 synthetic fixtures 驗證一個本機 opaque case key 能依序穿過 LINE intake、Case Store／`SALES_INTAKE`、quote creation、`Orders`／`OrderCharges`、`ASSET_LOG` 五個階段，並產 migration/backfill boundary receipt。不得改 live Sheets、訊息、價格或歷史 fuzzy links；若五階段無法保留同一 case key，立即停下修 contract，不提 live adoption。

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

## Resume Prompt

我是 A5/A6 毛利漏損稽核工程師，環境是 `/Users/pagemacmini/maplab-ai-handbook`。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本卡、validation receipt、schema proposal、canonical job 與 private join-first receipt。先驗 receipt SHA-256 `55ce24ff8eeea3136d14a80764ed4dff57500c4414c2807c433ab47bbd714b52`；fixed-five 已證實 3 案無 two-anchor candidate、2 案為 ambiguous、unique stable link 0，禁止再重跑 fuzzy/name matcher。下一步只用 synthetic fixtures 建 proposal-only intake-time `case_id` capture contract，使一個 opaque key 穿過 LINE intake、Case Store／SALES_INTAKE、quote、Orders／OrderCharges、ASSET_LOG；不得改 live Sheets、訊息、價格或歷史資料。私有資料不得送 DeerFlow/OpenRouter；無模型、無 customer send。未同時證明 baseline、delivery、incremental cost、charged fee 前 confirmed amount 必須為 0。每個 bounded action 更新 job、task card、receipt、CURRENT_STATUS 與 Resume Prompt，只 stage 任務相關檔案。
