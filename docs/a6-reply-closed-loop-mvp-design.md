# A6 回覆閉環 MVP 設計（輸入視窗 + 校正表）

> 版本：v0.1 DRAFT ｜ 建立：2026-07-30 ｜ 分支：`docs/a6-line-dataflow-pretraining-index-20260730`
> 狀態：設計草稿，**先出設計+落地路徑，先別大改上線**。
> 守則：**自用不賣人**；顧客對話＝敏感個資，去識別化、不外洩、不進公開模型輸出；祕密不 echo/commit；改動本機可回退、不 push main。

---

## 0. 一句話

把「客戶 LINE 訊息 → A6 產建議回覆 → 業務採用/修改/棄用」這條路的**業務決策**捕捉下來，變成 live 校正訊號，回饋模型 + 餵 gym 當 gold reply，讓回覆越用越準。這正是目前系統缺的「決策→結果→學習」環。

---

## 1. 現況錨點（本輪交叉比對確認）

- **A｜live inbound（客戶單向）**：GAS `scripts/apps-script/LineWebhook.gs` → Sheet `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` 分頁 `CONVERSATION_LOG`。欄位 `msg_id, case_id, timestamp, speaker, message, source, line_user_id, reply_to_msg_id`。**限制**：webhook 收不到業務從 OA Manager 後台回的訊息 → 只有半邊對話。
  - ⚠️ **live 尾列今日是否仍在寫＝未證實**（Drive 全文渲染被截斷、瀏覽器讀取不穩）。**需 Owner 自己開 sheet 看最後一列日期（5 秒）**：<https://docs.google.com/spreadsheets/d/1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg/edit>（分頁 CONVERSATION_LOG）。
- **B｜靜態預訓練（含雙向）**：2026-06-22 一次性 LINE OA CSV 匯出（3,625 檔）→ `workbook/a6-training/generated_local/training_samples.jsonl`（20,244 pairs、S0–S6 漏斗標註、含業務回覆側）。靜態。
- **gym**：`scripts/a6_gym_runner.py`（Ollama qwen2.5:14b 產建議 vs 真實員工回覆算可用率）；實測可用率 **0–20%**（啟發式評分器），**非 8 成**（8 成那題等 Owner 指認指標，此文件不下結論）。

**設計含義**：B 給模型「冷啟動語氣/樣式」；A 給 live 客戶輸入；**唯一缺口＝業務採用後的最終回覆（校正側）沒有任何 live 捕捉**。閉環的核心就是補這一塊。

---

## 2. 資料流圖

```
          ┌─────────────────────────── 學（回饋） ───────────────────────────┐
          │                                                                  │
          ▼                                                                  │
  [客戶 LINE 訊息]                                                            │
      │ (A) LINE webhook 既有路徑                                            │
      ▼                                                                      │
  CONVERSATION_LOG（客戶單向 live）                                          │
      │  收                                                                  │
      ▼                                                                      │
  ┌───────────────────────┐   草稿    ┌──────────────────────┐             │
  │ A6 建議回覆引擎        │──────────▶│ 業務輸入視窗          │             │
  │ (用 B 靜態資料訓/few-shot)         │ (人閘門: 採用/改/棄) │             │
  └───────────────────────┘           └──────────┬───────────┘             │
        ▲ 用校正資料 re-rank/微調                 │ 發送                    │
        │                                          ▼                         │
        │                                   [業務回覆客戶]                   │
        │                                          │                         │
        │                                          ▼                         │
        │                              ┌────────────────────────┐            │
        └──────────────────────────────│ A6_REPLY_CORRECTION    │────────────┘
                     gold reply / 指標  │ (校正表: 補回業務回覆側)│
                                        └────────────────────────┘
                                                   │
                                                   ▼
                                        gym 重評（真 gold 比對）→ 可用率爬升曲線
```

積木對齊：**收**（CONVERSATION_LOG）→ **草稿**（A6 建議）→ **人閘門**（業務採用/改/棄）→ **發**（業務送出）→ **學**（校正表 → 模型 + gym）。

---

## 3. 校正表 schema — `A6_REPLY_CORRECTION`

一列 = 一次「AI 建議 → 業務決策」事件。建議獨立成新分頁/新 sheet（**不寫回 CONVERSATION_LOG**，避免污染 live log），或本機 SQLite（沿用 `bot_a6/case_store.py` 模式）。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `correction_id` | uuid | 主鍵 |
| `case_id` | str | 對應 SALES_INTAKE / CONVERSATION_LOG，可空 |
| `line_msg_id` | str | 觸發此建議的客戶訊息 `msg_id`（連回 A） |
| `stage` | enum | S0–S6（沿用漏斗標註，供分層統計） |
| `customer_msg` | text | 客戶訊息（**去識別化**：姓名/電話/地址遮罩） |
| `ai_suggestion` | text | A6 產出的建議回覆 |
| `final_reply` | text | 業務實際送出的回覆（採用時=建議；修改時=改後） |
| `action` | enum | `adopt`（採用）/ `edit`（修改）/ `discard`（棄用/自己重寫） |
| `edit_diff` | json | 修改差異（僅 `edit`；存 token/句層 diff，不存整段重複） |
| `edit_distance` | float | 正規化編輯距離 0–1（0=原封採用，1=完全重寫）供快速排序 |
| `reject_reason_tag` | enum | 棄用/大改原因標籤：語氣/報價數字/資訊錯/太長/太短/漏補問/其他 |
| `model_ver` | str | 產生建議的模型/prompt 版本（可追溯哪版被改最多） |
| `created_at` | ts | 事件時間 |
| `operator` | str | 業務代號（Mina…），去識別，用於一致性分析 |

### 衍生指標（每日/每週彙總）
- **採用率** = `adopt / (adopt+edit+discard)`
- **修改率** = `edit / total`；**棄用率** = `discard / total`
- **原封採用率** = `edit_distance==0 佔比`（比 action=adopt 更嚴，抓「表面採用但其實微調」）
- **常被改的類型** = 依 `stage` × `reject_reason_tag` 樞紐；找出模型最弱的漏斗階段（預期 S3_QUOTE_* 報價數字、S2_DIETARY_ASK 補問最常被改）
- **模型版本爬升曲線** = `model_ver` × 採用率 時間序列（證明每次微調有沒有真的變好）

---

## 4. gym 如何用校正資料重評爬升

現況 gym 用「啟發式評分器」比對**歷史員工回覆**當 gold（0–20%，且評分器本身粗糙）。校正表上線後：

1. **真 gold 來源升級**：`final_reply`（業務實際送出）就是最高品質的 gold reply，比 2026-06 靜態匯出更貼近當下語氣/報價政策。定期把 `action∈{adopt,edit}` 的列匯出成新 gym 測試集。
2. **評分器升級**：除了字面 overlap，加入「業務是否採用」的硬標籤——`adopt & edit_distance<0.15` 視為 PASS，比純 bigram overlap 更接近真實可用性。
3. **分層爬升**：用 `stage` 分桶跑 gym，盯「常被改的階段」的可用率是否隨微調上升；避免整體數字掩蓋單一弱階段。
4. **回歸守門**：每次改 prompt/模型後，先對校正表歷史集重跑 gym，採用率沒升不上線（接 `weekly_eval_compounding` 既有節奏）。

---

## 5. MVP 範圍

**P0（先做，安全可回退）**
- 建 `A6_REPLY_CORRECTION` 分頁/SQLite（schema 如上）。
- 業務輸入視窗最小版：沿用**既有 A6 Telegram 窗口**（`skills/a6-telegram-window.md`）加一顆「建議回覆」+ 三鍵 `採用/修改/棄用`；棄用/修改時記 `final_reply`。**不新建 UI 框架**（不重造輪子）。
- 建議引擎先用 **B 資料 few-shot / 既有本地模型**，不先做微調。
- 可安全先做的小步：把 B 的 `training_samples.jsonl` 接成一個**離線「模擬回覆」demo**（餵 test split → 產建議 → 人工標採用與否 → 灌 correction 表首批種子），不接 live、不發訊息。

**P1**
- 接 A（CONVERSATION_LOG）live 客戶訊息 → 自動產建議推給業務窗口。
- 指標日報（採用率/修改率/常改類型）推 Telegram。
- gym 改吃校正表 gold。

**P2（成熟後）**
- 依「原封採用率」設信心門檻：某 stage 連續 N 週原封採用率 > 門檻 → 該類訊息升級「自動回」候選，仍保留人可攔截（積木的「發」從人閘門漸進到半自動）。

**先不做**：多租戶/賣人、換 UI 框架、動 A5 報價公式、把校正資料送公開模型、未經 Owner 核准的自動發送。

---

## 6. 落地路徑（小步、可回退）

1. 本文件 review（Owner）。
2. P0 schema + 種子：離線 demo 跑 test split，人工標首批 correction 列（不碰 live）。
3. Owner 5 秒自查 CONVERSATION_LOG 尾列 → 確認 A live 是否還在寫（決定 P1 能不能接 live）。
4. P1 接線（建議引擎 ← A；校正表 ← 業務窗口）。
5. gym 換 gold + 回歸守門，畫爬升曲線。
6. 指標穩定後才談 P2 自動回。

## 7. 隱私 / 安全邊界
- `customer_msg`/`final_reply` 去識別化（遮罩姓名/電話/地址/統編）；原始 PII 留本機/外接碟，不進 git、不進公開模型。
- 校正表若放 Google Sheet，權限比照現有 OA 資料；本機 SQLite 為預設。
- 自動發送預設關閉，P2 前一律人閘門。

## 8. 未解 / 待 Owner
- **live 尾列今日新鮮度未證實** → Owner 5 秒自查（連結見 §1）。
- **「~8 成模型」指哪個指標** → 待 Owner 指認；本設計以校正表採用率為主指標，不沿用未證實的 8 成。
- 業務輸入視窗要沿用 Telegram 還是另做輕量網頁 → 建議先 Telegram（最短路徑）。
