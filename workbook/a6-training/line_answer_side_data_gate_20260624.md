# A6 LINE Answer-Side Data Gate — 2026-06-24

角色：LINE-ANSWER-GATE worker  
範圍：只定義資料 gate；不讀 secrets、不送訊息、不改 runtime、不訓練模型。  
寫入檔：`workbook/a6-training/line_answer_side_data_gate_20260624.md`

---

## 1. 5 分鐘結論

現在不能直接訓練「MAPLAB 要怎麼回 LINE」，不是因為沒有客戶問題，也不是因為沒有 SOP，而是因為**可訓練的答案側 gold label 還沒有被證明乾淨可用**。

目前已知：

- `data/line_booking_pairs.csv` 是「對話檔案 / 聯絡人 / 日期 / TimeTree」配對索引，不是訓練語料本身。
- 現有 scaffold 只用 `qa_examples_deidentified.json` 與 `training_pairs_raw.json` 做小量測試樣本，不能代表真實 LINE 業務回覆。
- Owner 已校正：真正答案側可能在本地 LINE OA 雙向匯出 CSV 裡，尤其是 `Account` rows；但這些 row 還沒有經過 schema audit、speaker-aware pairing、PII masking、人工品質審查。
- A5/GAS/Sheet 可以提供報價事實，不等於「Mina/Owner 實際怎麼回」的 wording gold label。

所以本 gate 的判斷是：

```text
可升級到：approval_ready / answer_source_identified
不可升級到：training_ready / runtime_verified / auto_reply_ready
```

Owner 只需要在 5 分鐘內提供或確認最小資料來源，A6/Codex 才能進下一步 schema audit 與 masked sample queue。

---

## 2. 為什麼現在不能訓練「怎麼回」

從人類業務角度看，「怎麼回」包含四件事：

1. 先問什麼：日期、人數、地點、餐型、預算、是否需要桌椅或飲品。
2. 什麼時候報價：資訊不足時先補問，資訊足夠時才導到 A5/GAS/Sheet。
3. 怎麼講條款：訂金、保留檔期、調整菜單、取消改期、活動前確認。
4. 什麼語氣算 MAPLAB：簡潔、專業、不要亂承諾、不要把內部成本/毛利講給客戶。

客戶 inbound 只告訴我們「客戶問了什麼」。它不會告訴模型：

- Mina 實際補問了哪一題。
- 哪些情況先不報價。
- 哪些句子會讓客戶舒服地補資料。
- 哪些舊回覆其實不該再學。
- 哪些價格/訂金/低消是 Sheet 事實，哪些只是聊天口吻。

如果現在直接訓練，模型會有幾個風險：

- 把客戶問題當成業務答案。
- 把 AI seed / SOP 範例誤當 Mina 真實回覆。
- 學到 auto welcome、貼圖、殘缺訊息、舊政策或一次性錯誤。
- 洩漏姓名、電話、地址、檔名、公司名或 LINE id。
- 自己編價格、菜單、折扣、訂金，繞過 A5/GAS/Sheet。

因此，答案側不是「找到一些文字就能訓練」，而是必須先變成：`User context -> approved Account reply`。

---

## 3. 最小可用答案側資料

### P0. LINE OA Manager Account Rows

用途：真實業務回覆 gold source。

最低需求：

| 欄位 | 必要性 | 說明 |
|---|---:|---|
| `conversation_id` 或可 hash 的 thread/file id | 必填 | 用來把同一段對話串起來；原始 id 不進訓練輸出 |
| `message_id` 或 row number | 必填 | 用來重建相鄰訊息順序 |
| `timestamp` | 必填 | 用來確認 User 訊息在 Account 回覆之前 |
| `speaker` | 必填 | 必須能分出 `User` 與 `Account` |
| `message_type` | 必填 | text / image / sticker / file；非文字通常不能當 target |
| `text` | 必填 | 原始文字只可本地讀取，輸出前必須 masking |
| `sent_by` | 選填 | 若能分 Mina/Owner/auto/system 更好 |
| `source_batch` | 必填 | 匯入批次，方便回查但不暴露原檔名 |

通過條件：

- 至少能抽出 `User -> Account` 相鄰 pair。
- `Account` row 是人類或正式業務帳號回覆，不是 auto welcome。
- 原文不 commit，不貼聊天，不輸出到 review bundle。

### P0. 送出訊息 Archive

用途：如果 LINE OA Manager 匯出沒有完整 `Account` rows，就用 sent archive 補答案側。

最低需求：

| 欄位 | 必要性 | 說明 |
|---|---:|---|
| `conversation_id_hash` 或可 join 的 thread id | 必填 | 必須能接回客戶 inbound |
| `sent_at` | 必填 | 用來對齊客戶問題 |
| `sender` | 必填 | Mina / Owner / Account / system |
| `message_text` | 必填 | 送出的文字，需 masking |
| `reply_to_message_id` | 選填 | 若有，配對品質更高 |
| `message_type` | 必填 | text 才能當主要 target |
| `source` | 必填 | OA export / sent archive / other |

通過條件：

- 能和客戶 inbound 在同一 conversation 內 join。
- 不能只是一批孤立的送出句子。
- system / auto / broadcast / sticker 要排除或標成不可訓練。

### P0. 人工標註欄位

用途：補缺口 stage，或把 raw Account row 轉成可訓練、可審核的 gold reply。

最低標註欄位：

| 欄位 | 必要性 | 說明 |
|---|---:|---|
| `label_id` | 必填 | 標註列 id |
| `conversation_hash` | 必填 | 不放原始檔名/姓名 |
| `stage` | 必填 | 使用 A6 SOP stage，如 `S2_DATA`、`S4_BOOKING_ASK` |
| `customer_need_summary` | 必填 | 客戶需求摘要，已去識別化 |
| `known_fields_json` | 必填 | 日期/人數/地點/餐型/預算等已知欄位；PII mask |
| `gold_reply` | 必填 | Mina/Owner 批准可學的回覆文字 |
| `reply_goal` | 必填 | 補問 / 報價引導 / 訂金 / 活動前確認 |
| `quote_fact_ref` | 選填 | 對應 A5/GAS/Sheet 事實，不直接塞敏感連結 |
| `review_status` | 必填 | `approved` / `revise` / `reject` |
| `reviewer` | 必填 | Mina / Owner / A6 reviewer |
| `exclude_reason` | 條件必填 | reject 時要填原因 |

通過條件：

- 只有 `review_status=approved` 可進 train/eval。
- AI 自己生成的草稿不能當 gold；只能當待審候選。
- 報價金額、菜單、訂金等事實必須指向 A5/GAS/Sheet，不讓模型自由編。

---

## 4. CSV 欄位模板

### 4.1 OA Message Import Template

```csv
source_batch,conversation_hash,message_id,row_number,message_at,speaker,message_type,text,attachment_kind,sent_by,reply_to_message_id
line_oa_20260624,conv_xxx,msg_001,1,2026-06-01T10:00:00+08:00,User,text,[原文僅本地讀取],,,
line_oa_20260624,conv_xxx,msg_002,2,2026-06-01T10:03:00+08:00,Account,text,[原文僅本地讀取],,Mina,msg_001
```

規則：

- `speaker` 只允許 `User` / `Account` / `System`；`System` 不可當 target。
- `text` 在 raw import 階段可存在本地，但輸出訓練樣本前必須轉成 masked text。
- `conversation_hash` 由原始 conversation/file id hash 產生，不用原始姓名或檔名。

### 4.2 Supervised Pair Template

```csv
pair_id,conversation_hash,user_message_id,account_message_id,stage,user_context_masked,account_reply_masked,answer_source,quote_fact_ref,label_status,reviewer,exclude_reason
pair_xxx,conv_xxx,msg_001,msg_002,S2_DATA,"[日期] 企業茶會，約 [人數]，想了解外燴","您好，想先和您確認活動地點、預計人數與希望的餐點形式。",line_oa_account_row,,approved,Mina,
```

規則：

- `account_reply_masked` 必須來自 `Account` row、sent archive，或 Mina/Owner 人工標註。
- `label_status=approved` 才能進 train/eval。
- `quote_fact_ref` 只放 quote id/hash，不放客戶姓名、完整連結或敏感細節。

### 4.3 Manual Label Template

```csv
label_id,conversation_hash,stage,customer_need_summary,known_fields_json,gold_reply,reply_goal,quote_fact_ref,review_status,reviewer,notes
label_xxx,conv_xxx,S4_BOOKING_ASK,"客戶已確認菜單，準備保留檔期","{""date"":""[日期]"",""people"":""[人數]"",""area"":""[地區]""}","可以的，若要先保留檔期，這邊會協助您整理訂金與確認資訊。",booking_next_step,quote_xxx,approved,Owner,
```

規則：

- `gold_reply` 寫客戶可讀文字，不寫內部理由。
- `known_fields_json` 只放 mask 後的欄位。
- `notes` 可記錄審核理由，但不能放 PII。

---

## 5. PII Masking Rule

所有 raw text 進入 supervised pair 前必須做 masking：

| 類型 | 替換 |
|---|---|
| 姓名 / 聯絡人 | `[姓名]` |
| 公司名 / 學校名 / 單位名 | `[單位]`，除非 Owner 明確批准保留公開案例名 |
| 電話 / 手機 / 市話 | `[電話]` |
| email | `[email]` |
| URL / Google Sheet / Drive / LINE link | `[url]` 或 `[報價單連結]` |
| 地址 / 路街巷弄號樓 | `[地址]` |
| 精確日期 | `[日期]` 或轉成 `活動前 N 天` |
| LINE id / user id / 檔名 | hash，不輸出原值 |
| 照片 / 附件檔名 | hash + attachment kind，不輸出原檔名 |
| 金額 / 報價事實 | 可保留區間或 quote fact hash；正式金額須由 A5/GAS/Sheet 驗證 |

Fail 條件：

- masked output 裡仍有電話、email、地址、原始檔名、原始 LINE id。
- `contact_name` 或檔名出現在 `training_samples.jsonl`、manifest、review bundle。
- 將 raw LINE CSV commit 到 repo。

---

## 6. Quality Gate

### Gate A. Schema Gate

必須通過：

- 欄位存在：conversation / timestamp / speaker / message_type / text。
- timestamp 可排序。
- speaker 可正規化成 `User` / `Account` / `System`。
- raw row count、text row count、Account row count 可統計。

不通過就停在 `schema_missing`。

### Gate B. Pairing Gate

必須通過：

- 每個 supervised sample 都是同一 conversation 內 `User -> Account`。
- Account reply 在 User message 之後。
- 中間若有多則 User 追問，要合併成 context，不亂配到更早問題。
- sticker/image-only/system auto reply 不可當 target。

不通過就停在 `pairing_untrusted`。

### Gate C. Provenance Gate

必須通過：

- target 來源是 `line_oa_account_row`、`sent_archive`、或 `manual_owner_label`。
- `qa_examples_deidentified` / `training_pairs_raw` 只能當 scaffold seed 或 eval reference，不直接當正式大訓練資料。
- AI 草稿只能進 `candidate_reply`，不能進 `gold_reply`。

不通過就停在 `answer_source_untrusted`。

### Gate D. PII Gate

必須通過：

- raw source 只在本地或外接硬碟讀取。
- repo 內只允許 masked aggregate、schema report、sample count、hash id。
- 隨機抽查 20 筆 approved pair，無姓名、電話、地址、原檔名。

不通過就停在 `privacy_fail`。

### Gate E. Business Safety Gate

必須通過：

- 價格、菜單、毛利、訂金、低消、取消改期，不由模型自編。
- 若回覆含報價事實，必須有 `quote_fact_ref` 或明確標 `needs_quote_fact`。
- 禁止把 `高毛利`、成本、內部判斷、未核准折扣、保證承諾寫進客戶回覆。

不通過就停在 `business_policy_fail`。

### Gate F. Coverage Gate

第一階段最低門檻：

- 200 筆候選 `User -> Account` pair。
- 50 筆 Mina/Owner 或 A6 reviewer approved。
- `S2_DATA`、`S3_QUOTE_SEND`、`S4_BOOKING_ASK`、`S5_PAYMENT_ACK`、`S6_PREDAY` 各至少 5 筆 approved；不足的 stage 只可產 gap queue，不可宣稱 coverage 完整。
- validation/test split 不能全落在同一 stage 或同一匯出批次。

不通過就停在 `coverage_gap`。

---

## 7. Bad Examples

| 壞例子 | 為什麼不能進訓練 |
|---|---|
| 客戶：「我想問 30 人茶會」 target：「好的，30 人總價 NT$18,000」但沒有 A5/GAS/Sheet reference | 模型自編報價，違反報價事實來源 |
| Account row 是「歡迎加入 MAPLAB 官方帳號」 | auto welcome，不是業務回覆 |
| Account row 只有貼圖、圖片、或「好的」 | 不足以學業務流程，可留作 context，不當 gold target |
| raw target 含「王小姐 0912... 台南某路...」 | PII leak，privacy fail |
| 客戶後來改日期，但配到更早的 Account 報價 | pairing 錯誤，會教壞模型 |
| target 寫「不用訂金也可以先保留」但目前政策未核准 | 舊政策或一次性例外，不可學 |
| quote Sheet 的品項列直接當 LINE 回覆 | Sheet 是事實來源，不是客戶可讀 wording |
| AI 依 SOP 生成的漂亮回覆未經 Mina/Owner 審核 | candidate 不是 gold label |
| 客戶問取消，target 是另一個客戶的活動前提醒 | conversation join 錯誤 |

---

## 8. Owner 5 分鐘 Action

Owner 只要完成其中一條 P0，就能讓 A6/Codex 下一步開工：

### 選項 A：確認 LINE OA 雙向匯出資料夾

請回覆或放在任務卡：

```text
LINE OA answer-side source = <本地資料夾路徑>
我確認這批 CSV 含 User rows 與 Account rows。
允許 A6/Codex 只讀 schema audit，不輸出原文、不 commit raw CSV。
```

最小批次：20 個 CSV 或最近 30 天匯出即可。  
目的不是一次訓練，而是先證明欄位與 speaker 可以用。

### 選項 B：提供送出訊息 Archive

如果 OA 匯出沒有 `Account` rows，請提供：

```text
sent archive source = <本地檔案或資料夾路徑>
join key = <conversation id / user id hash / timestamp rule>
允許 A6/Codex 只讀 schema audit，不輸出原文、不 commit raw archive。
```

### 選項 C：先做人工標註種子

如果 raw export 暫時不好處理，先給 50 筆人工標註也可以：

```text
請 A6/Codex 產 50 筆 masked label queue。
Owner/Mina 只審 gold_reply，不看 raw PII。
優先 stage：S2_DATA / S4_BOOKING_ASK / S5_PAYMENT_ACK / S6_PREDAY。
```

---

## 9. A6 / Codex 下一步

在 Owner 完成 5 分鐘 action 後，A6/Codex 下一步應該是：

1. 只讀 schema audit：列出欄位、row count、speaker 分布、message_type 分布，不印原文。
2. 增加 `line_oa_export` parser：只抽 `User -> Account` adjacency，不接模型、不送訊息。
3. 產 masked `answer_side_gap_report`：列 stage coverage、Account row 可用率、reject reasons。
4. 產 50 筆 masked label queue：讓 Owner/Mina 審 `gold_reply`。
5. 通過 quality gate 後，才產 `training_samples.jsonl`；且 `send_allowed=false` 永遠保留。
6. 若修到重複坑，回寫 `pitfalls.md`：trigger / root cause / fix / prevention。

禁止事項仍維持：

- 不讀 `.env` / tokens / secrets。
- 不送 LINE / Telegram / Email。
- 不 commit raw CSV、原始訊息、姓名、電話、地址、檔名。
- 不把 A5/GAS/Sheet 事實當 LINE wording gold label。
- 不把模型草稿當 approved answer。

---

## 10. Verdict

LINE answer-side 目前可升級到：

```text
state = approval_ready
substate = answer_source_identified_but_not_training_ready
evidence =
  - scaffold exists and dry-run/unit tests were previously reported OK
  - booking pair index exists but is not answer text
  - local LINE OA bidirectional CSV source is identified by prior design correction
  - this gate defines the minimum Account-row/archive/manual-label contract
blocked_before_training =
  - no current schema audit of Account rows in this session
  - no approved masked User -> Account pair set
  - no quality gate report
  - no Owner/Mina approved gold labels
```

換句話說：現在可以請 Owner 提供資料，不可以宣稱已能訓練「怎麼回」。下一個可驗證里程碑是 `schema_audited`，不是 `trained`。
