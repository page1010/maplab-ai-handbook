# A6 LINE 報價草稿 / 回覆訓練管線設計

版本：v0.1  
建立：2026-06-23  
範圍：本地 scaffold；不接真實模型訓練、不送任何訊息、不讀 secrets、不改 runtime。

---

## 1. 冷啟動結論

本輪讀取的有效來源：

| 來源 | 讀到的事實 | 可用性 |
|---|---|---|
| `data/line_booking_pairs.csv` | 2,634 列；欄位是 `filename/index/contact_name/start_date/end_date/confirmed/likely_true_positive/match_timetree_date/match_timetree_events`；confirmed 62 列；likely true positive 4 列 | 只能當「對話檔案 ↔ 出餐事件」索引，不含客戶訊息與業務回覆，不能直接訓練回覆 |
| `workbook/a6-training/line_sales_sop_state_machine.md` | S0_OPENING 到 S6_PREDAY 的銷售狀態機與業務回覆策略 | 可作 stage taxonomy、標註準則、模型輸出安全框架 |
| `workbook/a6-training/qa_examples_deidentified.json` | 77 筆去識別化 QA examples，68 筆含 customer/business | 可作 schema seed 與小量 eval/reference，不足以單獨訓練 |
| `workbook/a6-training/training_pairs_raw.json` | 150 筆 stage-labelled pair，其中 User -> Account target 約 58 筆 | 可作 scaffold 測試與初版 supervised sample，仍需 Owner/Mina 確認來源與品質 |
| `projects/line-quote-assistant.md` / `decisions.md` | A6 面向 Mina，不面向客戶；LINE webhook 只記客戶 inbound；A6 不自行算報價 | 管線必須是「草稿給人審」，不是自動回客戶 |
| `docs/data-locations.md` | 原始 LINE CSV 在外接硬碟，完整雙向對話本地 only；去識別化產物也不 push | 任何 answer-side 補資料都要本地處理、去識別化後才進訓練樣本 |

---

## 2. 目標與非目標

### 目標

建立一條可重跑、可檢查、可擴充的本地訓練資料管線：

```text
配對索引 / 去識別化對話 seed / SOP
  -> privacy gate
  -> stage-labelled supervised samples
  -> answer-side coverage report
  -> 可交給未來模型訓練的「報價回覆草稿」JSONL
```

輸出的樣本只用於產生「Mina/Owner 可審核的草稿」，不是自動送訊息。

### 非目標

- 不接 OpenAI / Claude / Ollama / fine-tune / embedding / RAG runtime。
- 不送 LINE、Telegram、Email 或任何外部訊息。
- 不讀 `.env`、OAuth token、LINE token、GAS secret。
- 不修改 `data/`、`bot_a6/`、`scripts/`、GAS、launchd 或任一 runtime。
- 不把原始 LINE 對話、姓名、電話、地址、檔名複製到 repo。

---

## 3. 樣本格式

未來可訓練樣本採 JSONL，一列一個草稿任務：

```json
{
  "id": "a6_reply_...",
  "task": "line_quote_reply_draft",
  "stage": "S2_DATA",
  "split": "train",
  "source": {
    "kind": "training_pairs_raw",
    "privacy": "masked_local",
    "conversation_id_hash": "..."
  },
  "instruction": "根據 MAPLAB LINE 銷售 SOP，為 Mina 起草下一則業務回覆。只輸出草稿，不送訊息。",
  "input": {
    "messages": [
      {"role": "customer", "content": "..."}
    ],
    "known_fields": {}
  },
  "target": {
    "role": "business",
    "content": "..."
  },
  "safety": {
    "send_allowed": false,
    "requires_human_review": true,
    "price_truth_source": "A5/GAS/Sheet only"
  }
}
```

重點：

- `source.conversation_id_hash` 用 hash，不保留檔名、姓名、LINE ID。
- `target.content` 必須來自業務真實回覆或人工標註；不能用模型自產內容當 gold label。
- `price_truth_source` 固定提醒：A6 不自行算價，正式金額必須來自 A5/GAS/Sheet。

---

## 4. 管線分層

### L0 Source Inventory

讀取來源：

- `data/line_booking_pairs.csv`：只取統計、confirmed flags、hash 後的 source id；不輸出 `filename` / `contact_name`。
- `qa_examples_deidentified.json`：讀 customer/business/stage，仍跑 masking。
- `training_pairs_raw.json`：只接受 `role=User` 且 `response_role=Account` 的 pair 作 supervised answer sample。
- 未來 answer-side CSV：從 LINE OA Manager 匯出或其他正式來源讀取，必須 speaker-aware。

### L1 Privacy Gate

所有文字欄位進樣本前先 masking：

- 電話、email、URL、LINE/帳號型字串。
- 從 `line_booking_pairs.csv` 讀到的 `contact_name` 只作 runtime mask token，不寫出。
- 日期預設泛化成 `[日期]`，避免小樣本回推活動。
- 地址/路名以 conservative regex 標成 `[地址]`。

如果 masking 前後仍出現原始 `contact_name`、檔名或電話，管線應 fail，不產出。

### L2 Stage Normalization

以 `line_sales_sop_state_machine.md` 為 taxonomy：

- `S0_OPENING`
- `S1_INQUIRY`
- `S1_QUALIFY`
- `S2_DATA`
- `S2_DIETARY_ASK`
- `S3_QUOTE_INTRO`
- `S3_QUOTE_SEND`
- `S3_QUOTE_ACK`
- `S3_MENU_ADJUST`
- `S3_BUDGET_CONFIRM`
- `S4_BOOKING_ASK`
- `S4_PAYMENT_INFO`
- `S5_PAYMENT`
- `S5_PAYMENT_ACK`
- `S6_PREDAY`
- `S_PENDING`

不在 taxonomy 的 stage 先保留原值但標 `needs_stage_review=true`。

### L3 Answer-Side Join

真正 supervised sample 的條件：

1. 有 customer/user utterance。
2. 下一則或人工標註 target 是 Account/business reply。
3. target 來源是 `LINE OA Manager export`、`business sent messages`、`quote artifact human wording` 或 `Mina/Owner label`。
4. 通過 PII mask。

不符合者只能進 `answer_side_gap_report` 或 label queue，不能進 train split。

### L4 Train / Eval Split

用 sample id deterministic split：

- 80% train
- 10% validation
- 10% test

split 不能用時間排序，避免同一種 stage 或同一批匯出集中在 test。

### L5 Model Training Stub

本輪只產出 `training_samples.jsonl` 與 manifest。未來若接模型：

1. 先用 JSONL 做 offline eval。
2. 產生 draft 時強制 `send_allowed=false`。
3. 任何報價金額、品項、毛利率必須 call A5/GAS/Sheet 或讀已驗證報價單，不讓模型自由填。
4. Draft 只回 Telegram / local review 給 Mina/Owner，不直送 LINE。

---

## 5. 答案側缺口

### 結論

目前最大的缺口不是 input-side，而是 answer-side。

LINE webhook / `CONVERSATION_LOG` 的本質是客戶傳給 OA 的 inbound log。它看得到「客戶問什麼」，但看不到 Mina / Account 在 LINE OA 後台怎麼回。`data/line_booking_pairs.csv` 又只是檔名、聯絡人、日期與 TimeTree 的配對索引，完全沒有「客戶訊息 -> 業務回覆」內容。

因此：

- 它可以用來找候選案件、估計哪些對話可能成交。
- 它不能單獨訓練報價回覆模型。
- 沒有 answer-side gold label 時，模型只能學 SOP 口吻，不能學 Mina 實際如何釐清、報價、催訂、收款、活動前協調。

現有兩份 JSON 有少量去識別化對答，可作 scaffold seed，但量太小、來源需再審，不能當完整訓練集。

### 要補的答案側來源

| 優先 | 來源 | 能補什麼 | 取得方案 | 風險 / Gate |
|---|---|---|---|---|
| P0 | LINE OA Manager 對話記錄 CSV 匯出 | 完整雙向 `User` + `Account` 對話，是最接近真實業務回覆的 gold source | 從 OA 後台匯出；放在本地/外接硬碟 readonly；scaffold 只讀，不 commit | 必須確認 CSV 欄位含 speaker；mask 後才可輸出 |
| P0 | Mina/Owner 人工標註 | 缺 answer 的 inbound 訊息可補成標準回覆 | 從 gap queue 抽樣 100-300 筆，每筆標 stage、回覆草稿、是否可作 gold | 標註 UI/格式要簡單；不讓模型自填 gold |
| P1 | 正式報價單 / GAS Sheet / A5 review bundle | 補「報價事實」：品項、金額、毛利、訂金、條款 | 用 confirmed pair hash 對回 quote URL 或 review bundle；只抽非 PII 的 quote facts | 只能當 facts/context，不等於 LINE 回覆 wording |
| P1 | 我方送出訊息匯出 / OA sent message archive | 補實際業務語氣與 timing | 若 LINE OA Manager CSV 已含 Account rows，優先用同一來源；若另有 sent archive，再做 speaker join | 需去重，避免 auto welcome 或貼圖污染 target |
| P2 | Telegram A6 草稿 + Mina 修改後版本 | 補「AI 草稿 -> 人工修正」偏好資料 | 未來在 A6 draft review flow 記錄 before/after；只存去識別化 diff | 不能把未審 AI 草稿當 gold；只能用 after |

### 具體取得步驟

1. 建立本地 input convention：`/Volumes/.../line_oa_chat_csv_*/` 作 readonly source，不複製到 repo。
2. 對 20 個 CSV 做 schema audit：確認 speaker 欄、timestamp 欄、message 欄、conversation id 欄。
3. 用 scaffold 增加 `line_oa_export` parser，只輸出 masked JSONL 到 `workbook/a6-training/generated_local/`（該路徑仍應 gitignore）。
4. 先抽 200 筆 `User -> Account` 真實鄰接 pair，按 SOP stage 分布檢查。
5. 對缺口 stage 建 label queue：S4/S5/S6 優先，因目前樣本少。
6. 由 Mina/Owner 審 50 筆，確認回覆口吻、低消、訂金、報價前置問法沒有錯。
7. 只有通過人工審查的 answer target 才進 train/eval。

---

## 6. Scaffold 檔案

本輪新增：

- `line_reply_training_scaffold.py`
  - 預設 dry-run。
  - 只輸出 aggregate manifest，不印原文。
  - 加 `--write` 才會在指定 output dir 寫 JSONL。
  - 不接模型、不送訊息。
- `test_line_reply_training_scaffold.py`
  - 用 `/tmp` 暫存假資料測試。
  - 驗證不輸出姓名、電話、檔名。
  - 驗證只把 `User -> Account` 放入 supervised train samples。

---

## 7. 下一輪 Resume Prompt

```text
你是 A6 LINE 報價回覆訓練資料整理 agent，運行在 Mac mini Codex，本輪只做本地資料 scaffold，不碰 runtime、不送訊息、不執行 git。
repo: /Users/pagemacmini/maplab-ai-handbook

先讀：
1. CURRENT_STATUS.md
2. handoff/tasks/T-A6-001.md
3. handoff/tasks/T-A6-002.md
4. pitfalls.md
5. docs/data-locations.md
6. workbook/a6-training/line_sales_sop_state_machine.md
7. workbook/a6-training/line_reply_training_pipeline_design.md

已完成：
- 確認 data/line_booking_pairs.csv 只有配對索引，不含客問/業務答。
- 確認 LINE webhook / CONVERSATION_LOG 只有 customer -> OA inbound，不能補業務回覆。
- 新增 line_reply_training_scaffold.py，預設 dry-run，不接模型、不送訊息。
- 新增 unittest，驗證 PII masking 與 User -> Account supervised sample gate。

下一步：
1. 用 LINE OA Manager 匯出 CSV 做 schema audit，只讀，不複製原文到 repo。
2. 增加 parser：speaker-aware，僅抽 User -> Account adjacency。
3. 產 answer_side_gap_report，優先列 S4/S5/S6 缺口。
4. 抽 50-200 筆給 Mina/Owner 標註或審核。
5. 通過人工審查後再考慮模型訓練；draft 永遠 send_allowed=false。
```

---

## ⚠️ 修正（2026-06-23 Owner 校正）：答案側不是「缺」，是在本地下載檔裡

先前 scaffold 用 `qa_examples_deidentified.json` / `training_pairs_raw.json` 當種子，那是**舊資料/假回覆**，據此誤判「答案側缺失、LINE 只有客戶→你」。**錯誤。**

**真正的答案側來源 = LINE OA 對話匯出檔（雙向，含業務實際回覆）：**
- **主來源（`scripts/parse_line_booking_pairs.py` 讀取）**：`/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421/`
- **雲端鏡像**：`/Users/pagemacmini/Library/CloudStorage/GoogleDrive-pagewu1010@gmail.com/我的雲端硬碟/MAPLAB_DATA/line_oa_chat_csv/`
- 配對索引 `data/line_booking_pairs.csv` 的 `filename` 欄一一對應這些對話檔（約 2634+ 個 `<id>_<date>_<date>_<name>.csv`）。

**真正下一步**：解析這些**雙向 CSV**，依發話方抽「客戶訊息 → 業務回覆」成對，做去識別化監督樣本——這才是真答案側，不要再用種子假回覆。PII 一律留本機、不外洩、不上 commit。
