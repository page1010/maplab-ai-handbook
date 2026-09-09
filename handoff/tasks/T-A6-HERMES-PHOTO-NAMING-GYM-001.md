# T-A6-HERMES-PHOTO-NAMING-GYM-001

- Owner: A0（格式守門）；Owner 裁定來源 msg 2026-09-07「hermes額度用上…有意義的產出先做，比如照片命名整理…在你監控好格式的情況下」
- Executor: Hermes（OpenRouter free-only 鏈，經 bot_a6/hermes_call；OLLAMA 禁用照舊）
- Status: **DONE 2026-09-09**（Owner msg 5018 令即辦；執行者=Fable5 本人非 hermes——20 夾 slug 手工裁定+deterministic 腳本一次跑完 348 列，5 條格式閘全 PASS，hermes 額度 0。交付與驗收紀錄=workbook/outputs/photo-naming-348-20260909.md；提案檔=agent-bus shared/seo/photo_rename_proposal_20260909.csv/.txt。實際改名照紅線未執行，等互審+Owner 放行。）
  **追記 2026-09-09 09:1x**：Owner msg 5025「我放行 你自己來 都做不用挑」→ 改名批次已執行：332 張全數轉出 webp 成品庫（0缺檔0失敗），上傳 Owner Drive「maplab照片改名成品庫-20260909」332/332。執行方式=產出改名副本，Drive 外燴紀錄原始檔未動（可回溯）。
- 章程: docs/agent-fde-charter-20260907.md（急迫性同步、交成品、回饋回灌）

## 任務定義

把 348 列 photo_alt_index.csv 的照片檔名整理成標準命名提案。這是純文字轉換任務，
是 hermes 免費鏈最擅長也最難出事的題型；產出直接餵 348 互審放行後的改名批次與文章配圖。

## 輸入/輸出

- 輸入：agent-bus shared/seo/photo_alt_index.csv 的 file_path、case_folder、scene 三欄（不含任何客戶聯絡資料）。
- 輸出格式（逐列，嚴格）：`原路徑 | 提案檔名 | 理由一句`
- 命名規則：`maplab-YYYYMMDD-{活動slug}-{scene}-{序號2位}.webp`；活動 slug 取 case_folder 的活動主體轉拼音或英文（例 0718 服飾店開幕茶會 → clea-opening）；同活動內序號連續。
- 批次大小：每批 30 列，一批一個 hermes 呼叫（防 timeout 鐵則沿用）。

## A0 格式閘（每批驗收）

1. 行數=輸入列數；2. 每行三欄豎線分隔；3. 檔名符合正則 `maplab-[0-9]{8}-[a-z0-9-]+-[a-z-]+-[0-9]{2}\.webp`；
4. 日期與 case_folder 日期一致；5. 零幻覺活動名（slug 必須可溯源到 case_folder 字面）。
閘不過整批重跑，連兩批不過就停下記 lesson，不硬燒額度。

## 額度紀律

走 :free 鏈；用量記入既有 0600 ledger 紀律；本任務屬產出型不佔訓練 950 上限的訓練額，但單日呼叫以 15 批（約 450 列上限）為天花板。

## 紅線

- 只出提案清單，不執行任何改名/搬檔（實際改名等 348 互審+歸夾提案過 Owner）。
- 不碰 LINE、客資、報價；失敗 fallback 記錄照 hermes_call 現行棘輪（.hermes_last_used）。

## 驗收

第一批 30 列提案 + a0 格式閘 PASS 紀錄入 workbook；全 348 列完成後彙整單一 CSV 供改名批次引用。
