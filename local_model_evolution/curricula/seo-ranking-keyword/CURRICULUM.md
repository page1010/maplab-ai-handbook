# P0-2 Curriculum — SEO Ranking / Keyword Tracking

> 狀態：dataset_ready（eval only）｜ 版本 v0.1 ｜ 建立：2026-07-19
> 對應：LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md §八 P0-2

## 目標輸出

固定十欄 action card：關鍵字／目前排名或頁面／資料時間／變化／對應 landing page／
搜尋意圖／cannibalization／建議動作／預期驗證時間／不可逆動作批准。

## 地端模型必須學會（G1→G2 邊界）

- GSC／搜尋結果／網站實況與 repo 文件分開，不把 repo 敘述當成即時排名。
- 不將歷史排名當今日排名；資料新鮮度必須明確標記。
- 關鍵字與正確頁面精準配對，防止 cannibalization 誤判。
- 涉及發布文章、改正式頁面、動 Ads 預算的建議一律先產出 approval-ready 提案，
  不得直接標記為已執行（呼應 `docs/governance/unattended-run-safety.md` 第 6 條）。

## Eval Cases

- 位置：`evals/eval_cases.jsonl`
- 數量：24（20–50 範圍內，第一輪不擴大）
- 資料來源：**全部為去識別化合成資料**（`外燴推薦` 等品類關鍵字為 MAPLAB 業務語境下
  可公開的搜尋詞彙範例，landing page 為虛構路徑，非任何真實 GSC 匯出快照，避免把未經
  即時驗證的即時排名數字寫進固定 eval 集造成過期污染）。
- 六類，各 4 題：
  1. `SEO-MAP-*` — keyword-page mapping accuracy
  2. `SEO-TS-*` — ranking timestamp completeness
  3. `SEO-CANN-*` — duplicate / cannibalization precision
  4. `SEO-HIST-*` — historical rank vs. today confusion
  5. `SEO-DESTRUCT-*` — destructive action gating（不可逆動作批准）
  6. `SEO-CARD-*` — action card completeness（十欄齊全）

## 核心 Eval 指標（對應 eval_harness.py）

| 指標 | harness 錯誤代碼 | 目標 |
|---|---|---|
| keyword-page mapping accuracy | `keyword_page_mapping_error` | = 0 |
| ranking timestamp completeness | `ranking_timestamp_missing` | = 0 |
| duplicate/cannibalization precision | 由 `cannibalization` 欄位人工/B2 覆核 | 待 baseline 後定基準 |
| destructive action rate | `destructive_action_without_approval` | = 0（硬門檻） |
| action card completeness | `action_card_incomplete` | = 0 |
| 歷史排名誤當今日 | `historical_rank_treated_as_today` | = 0 |

## Baseline 狀態

**Blocked in this remote sandbox** — 同 investment curriculum，沒有 Mac mini
runtime，也沒有即時 GSC 存取權可以合法抓 fresh 排名資料進評測集。已用手寫 fixture
自我測試 `eval_harness.py`（見 `../../evals/harness_selftest_seo_report.json`），
證明 harness 能正確抓出全部六類錯誤。

## 下一步

1. 在 Mac mini 上對 T3 模型跑本 curriculum，取得真正 baseline。
2. 若要擴充真實 GSC 快照案例，必須透過 A2 用既有 credential route
   （`skills/credentials/google-drive-api.md` 等）合法拉資料，並附上 `data_as_of`
   與 provenance，不得由地端模型自行臆測排名數字。
3. 找出前三大錯誤類型，優先 Level A 修正。
