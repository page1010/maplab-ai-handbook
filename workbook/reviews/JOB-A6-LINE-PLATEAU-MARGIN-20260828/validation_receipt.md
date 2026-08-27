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
- 解讀：label 是 deterministic prelabel，不是 human gold／confirmed leakage；confirmed leakage amount 保持 0。
