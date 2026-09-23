# A6 回覆閉環 MVP 設計（輸入視窗 + 校正表）

> 版本：v0.1 DRAFT ｜ 建立：2026-07-30 ｜ 分支：`docs/a6-line-dataflow-pretraining-index-20260730`
> 狀態：設計草稿，**先出設計+落地路徑，先別大改上線**。
> 守則：**自用不賣人**；顧客對話＝敏感個資，去識別化、不外洩、不進公開模型輸出；祕密不 echo/commit；改動本機可回退、不 push main。

---

## 0. 一句話

把「客戶 LINE 訊息 → A6 產建議回覆 → 業務採用/修改/棄用」這條路的**業務決策**捕捉下來，變成 live 校正訊號，回饋模型 + 餵 gym 當 gold reply，讓回覆越用越準。這正是目前系統缺的「決策→結果→學習」環。

## 0.1 北極星（Owner 2026-07-31 定調）— 框架優先、模型可插拔

> **主目標＝用「教練系統框架」把回覆品質做到夠好；模型可插拔——地端夠好就用地端（省成本），不夠好就 escalate 到已連的 Gemini/Antigravity。框架（教練評分＋校正回饋）才是核心資產，不綁死任何底層模型。**

- **收回「地端優先」當唯一北極星**（修正前一版）。不堅持地端；地端沒有比較好用就接已串好的雲端（Antigravity `agy` → Gemini 3.1 Pro/Flash、Claude；見 §9 可插拔後端）。
- **教練系統框架＝本專案真正資產**：預訓練（歷史對話模擬）→ 產建議 → **能力較強的模型當教練評分/校正弱模型** → 校正回饋讓它進步。這套框架換任何底層模型都能把事做好（呼應 `projects/a6-llm-backend-adapter.md` 的「換底層模型、角色分工不變」）。
- 「訓練到 80 分」的真義與 gym 落差 → 見**附錄 A**（重點：那是教練對「套上操作手冊+範例+deterministic 管線」後的品質判斷，不是 fine-tune 權重；現行 gym 是弱啟發式評分器、量錯對象）。
- 指標改為 **回覆品質 + 各模型表現對比 + 何時該 escalate**（不硬推地端）：地端 vs 雲端呼叫比例只當**成本觀測**，不是達標門檻。

---

## 1. 現況錨點（本輪交叉比對確認）

- **A｜live inbound（客戶單向）**：GAS `scripts/apps-script/LineWebhook.gs` → Sheet `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` 分頁 `CONVERSATION_LOG`。欄位 `msg_id, case_id, timestamp, speaker, message, source, line_user_id, reply_to_msg_id`。**限制**：webhook 收不到業務從 OA Manager 後台回的訊息 → 只有半邊對話。
  - ⚠️ **live 尾列今日是否仍在寫＝未證實**。已建 `scripts/sheet_tail.py`（唯讀讀尾列），但 2026-07-31 實跑回 **`invalid_grant: Token has been expired or revoked`**——`~/.claude/mcp-keys/google-token.json` 過期/被撤，故**任何自動讀取（本工具＋既有 `bot_a6/case_store.py`）現在都讀不到**。**注意分開看**：GAS webhook 寫入 sheet 用的是 GAS 自己的授權，**不依賴這個 OAuth token**，所以 sheet 很可能仍在收訊息，壞的只是我們的「讀」路徑。→ Owner 二選一：(a) 開 sheet 看最後一列日期（5 秒，最快）：<https://docs.google.com/spreadsheets/d/1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg/edit>；(b) 重新授權 Google OAuth，之後 `sheet_tail.py` 就能 5 秒自驗。
- **B｜靜態預訓練（含雙向）**：2026-06-22 一次性 LINE OA CSV 匯出（3,625 檔）→ `workbook/a6-training/generated_local/training_samples.jsonl`（20,244 pairs、S0–S6 漏斗標註、含業務回覆側）。靜態。
- **gym**：`scripts/a6_gym_runner.py`（Ollama **base** qwen2.5:14b + 通用系統提示、無 few-shot/操作手冊、粗糙啟發式評分）→ 實測可用率 **0–20%**。這**不是** Owner 記憶中的「50→80」（見附錄 A：那是套上操作手冊+範例+deterministic fallback 後、對報價草稿品質的主觀判斷，且部分走 gemma4/Claude）。gym 目前**量錯對象＋用錯尺**。

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
| `backend` | enum | 哪個後端產的：`ollama`（地端）/ `codex` / `antigravity`(Gemini/Claude) — 供各模型表現對比 |
| `local_confidence` | float | 地端自評信心 0–1（低於門檻即建議 escalate） |
| `escalated` | bool | 這則是否已從地端升級到雲端產生 |
| `escalate_reason` | enum | 升級原因：低信心/被大改/客戶明確不滿/特殊需求 |
| `created_at` | ts | 事件時間 |
| `operator` | str | 業務代號（Mina…），去識別，用於一致性分析 |

### 衍生指標（每日/每週彙總）
- **採用率** = `adopt / (adopt+edit+discard)`
- **修改率** = `edit / total`；**棄用率** = `discard / total`
- **原封採用率** = `edit_distance==0 佔比`（比 action=adopt 更嚴，抓「表面採用但其實微調」）
- **常被改的類型** = 依 `stage` × `reject_reason_tag` 樞紐；找出模型最弱的漏斗階段（預期 S3_QUOTE_* 報價數字、S2_DIETARY_ASK 補問最常被改）
- **模型版本爬升曲線** = `model_ver` × 採用率 時間序列（證明每次微調有沒有真的變好）
- **各模型表現對比** = `backend` × 採用率/原封採用率/棄用率（回答「地端 vs Gemini vs Codex 誰在哪類 stage 比較好用」）
- **escalate 率（成本觀測）** = `escalated / total`；地端能自足的比例越高越省，但**不設硬門檻**——若某 stage 地端棄用率高，就讓它常態走雲端，不硬撐地端
- **教練分（可選）** = 用能力較強模型（agy→Gemini/Claude 或 Codex）對 `ai_suggestion` 打分，對照業務實際 action 校準教練尺（見 §9.1）

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

---

## 9. 可插拔模型後端（教練 + 執行）

框架不綁死底層模型。執行後端（產建議）與教練後端（評分/校正）都可插拔。

### 現況串接（已存在，證據）
- **設計/骨架**：`projects/a6-llm-backend-adapter.md` + `bot_a6/llm_backend_adapter.py`（chain：`codex → antigravity → ollama`，順序由 env `A6_LLM_BACKEND_ORDER` 設定；**骨架未接線到線上 `bot_a6.py`**）。
- **雲端 Antigravity（`agy`）**：已安裝（Homebrew `antigravity-cli`，`/opt/homebrew/bin/agy`），可非互動 `agy --print --model <name>`。`agy models` 提供 **Gemini 3.1 Pro (Low/High)、Gemini 3.5 Flash、Claude Sonnet 4.6、Claude Opus 4.6、GPT-OSS 120B**。已在 `scripts/weekly_eval_compounding.py` 的 `run_agy_quality_review()` **生產使用**（正是「強模型當品質複核/教練」的既有實例）。
- **地端 Ollama**：`qwen2.5:14b`、`gemma4`（報價常用）、`qwen2.5-coder:7b`、`moondream:1.8b`（vision）。
- **Codex**：`codex exec --ephemeral -s read-only`，A6 一般聊天現行 primary。
- ⚠️ **待確認**：Owner 說的「固定雲端硬碟送」那條 Gemini 路徑，若**不是** `agy`、而是另一條走 Google Drive 資料夾批次的管線（如 `windows_agent_bridge` outbox 類機制），請 Owner 指認確切位置；本文件先以已驗證的 `agy → Gemini/Claude` 當雲端後端，Drive 批次路徑標為待補。
- ⚠️ **Antigravity 唯讀風險**：`agy` 未找到等同 Codex `-s read-only` 的強制唯讀 flag，接面向客戶路徑前需先做唯讀驗證（見 `a6-llm-backend-adapter.md` §六風險）。教練/評分是唯讀文字任務，風險低，可先用。

### 執行後端選擇邏輯（MVP）
1. 預設先讓**地端**產建議（便宜）。
2. `local_confidence < 門檻` 或 stage 屬「地端歷史棄用率高」→ 直接 escalate 到 `agy`（Gemini 3.1 Pro / Claude）。
3. 業務對地端建議按「棄用/大改」→ 該類型自動提高 escalate 傾向（校正資料回饋路由，不是硬寫死）。

### 9.1 教練評分（把 a6-gym 升級成真正的教練系統）
- **現況**：`a6_gym_runner.py` 的評分是**啟發式**（bigram overlap + 結構命中），不是強模型教練 → 這是 gym 分數低且失真的主因之一。
- **升級**：教練改用**能力較強模型**（`agy`→Gemini/Claude 或 Codex）對地端建議打分＋給改進點，對照校正表 `action`（業務真的採用了沒）校準教練尺。這才符合 Owner 說的「強模型確認/評分弱模型 → 教練它進步」。
- **省算力對照**：教練評分可離線批次跑（非即時），用雲端額度不影響即時延遲。

---

## 附錄 A：「80 分」真義與 gym 落差（證據，非假設）

**Owner 記憶**：上次用完整對話模擬訓練地端模型 → 強模型當教練評分 → 帶到約 80 分（省算力：便宜地端就夠好，不必每次叫雲端）。

**查證結果（拿證據講）**：
1. **沒有 fine-tune 權重產物**：`ollama list` 只有 base 模型（qwen2.5:14b / gemma4 / qwen2.5-coder:7b / moondream），**無任何自訓 A6 模型**；全機 `mdfind` 無 `.gguf/.safetensors/LoRA/adapter` 權重；repo 內無 `ollama create`/Modelfile/fine-tune 腳本。→ **「80 分模型」不是一份被弄丟或沒部署的權重，而是根本沒產生權重**。
2. **「訓練」的真義＝教 in-context 用法**：`docs/business-requirements/a6-training-methodology.md`（Owner 2026-04-09）白紙黑字「**不是寫死 parser，是給 AI 操作手冊＋QA 範例＋安全框架**」；`skills/a6-local-quote-model-tuning.md` 的「調教」＝ prompt 收窄＋output sanitize＋deterministic fallback。這些**方法論產物有留、且已部署**（在 `bot_a6/` + `skills/`）。
3. **「80 分」是品質尺，不是 gym 分**：方法論文件明講 Owner 底線是「不要 80 分要 100 分（Mina 打開直接能發）」——**80/100 是對報價草稿可用度的主觀判斷**，由 Owner／強模型互動判定，不是自動 eval 數字。
4. **gym 0–20% 為何落差**：現行 `a6_gym_runner.py` 跑的是 **base qwen2.5:14b＋通用系統提示、無操作手冊/範例/deterministic 管線**，且用**粗糙啟發式**比對**唯一歷史員工回覆**（措辭不同就算 fail，即使結構良好——stdout 實見 struct=4–5 但 overlap 0.08–0.12 →判 fail）。→ **量錯對象（未套管線的裸模型）＋用錯尺（字面比對 vs 主觀可用度）＋教練沒被做成自動腳本**。不是模型丟了，是 gym 沒測到 Owner 當時判 80 的那個「管線＋教練」組態。

**結論**：教練系統框架是對的、也有既有實例（`weekly_eval_compounding.run_agy_quality_review`、SEO/InvestOS 三人小組 Claude+Codex+agy）；但**針對 A6 回覆的自動教練評分尚未成形**，且**沒有可重現「80 分」的自動測試**。要復現/超越 80，路徑是把 gym 升級成 §9.1 的真教練（強模型評分＋校正表 gold），對「套上管線的可插拔模型」評分，而非對裸 base 模型。
