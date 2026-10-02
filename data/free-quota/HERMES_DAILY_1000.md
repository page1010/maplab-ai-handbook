# 免費算力每日 1000 來回班表 — 20 個使用場景與時段安排

## 2026-10-02 受控啟動現況（目前執行依本節）

> 狀態：`LIVE_SYNTHETIC_SMOKE_PASS / SCHEDULE_INSTALLED_DATE_HOLD / BUSINESS_ADOPTION_UNVERIFIED / NOT_WEIGHT_TRAINING`。
> **1,000 是免費 request attempts 的政策天花板，不是每日 KPI。** 下方 2026-09-24 的「500 件／天」、「1100 上限」、「排程尚未建立」及同名日報規劃保留作歷史，均由本節的目前設定覆蓋；不得拿舊容量表宣稱今日成果。

### 已驗證的單題實跑

- Run ID：`20261002-b1of6-072757-36898`，2026-10-02 15:27:57–15:28:49（Asia/Taipei）。
- 只執行 `40-image-prompt.job.md` 一件合成場景：`日照中心 — 節慶主題點心單品特寫`；未附客資、私有照片、repo 文件或外部來源頁。
- 共 **4 provider attempts：2 成功、2 HTTP errors**。產稿為 `nvidia/nemotron-3-super-120b-a12b:free`，換模型審稿為 `dots-studio/dots-3-note-preview:free`；成功回應 ID 與每次先記帳的 attempt ID 均留在 JSON 回執。這四次只屬本次 runner，不能算成整日總數或 Hermes 桌面聊天的用量。
- 產出一份文字生圖指令草稿及一份不同模型審稿，並未呼叫生圖平台。獨立本機 **9 項檢查全部通過**，包含四次記帳、不同模型、SYNTHETIC 標記、五個必填欄位、人臉排除條件與 installed/repo 排程一致性；回執與草稿各綁 SHA-256。
- 模型互審與本機結構檢查是分開的證據。`STRUCTURAL_PASS` 不代表營業採用、轉單效果、權重訓練或模型能力已提升；本次九項檢查也不是所有未來排程產出的自動驗收保證。
- 原始回執的 `扇出 9 件成功 1 件` 意指「本班候選 9 件、本次實際成功 1 件」，不是完成九件；`items_attempted=1` 與唯一草稿為準。歷史回執不改寫，後續 runner 回執已改為分開標示候選與實際成功數。

證據：

- [單題執行回執 JSON](report_20261002-b1of6-072757-36898.json)／[可讀回執](report_20261002-b1of6-072757-36898.md)
- [合成生圖指令草稿](image-prompts/prompt_20261002-b1of6-072757-36898/001.md)／[換模型審稿](reviews/40-image-prompt_20261002-b1of6-072757-36898_001.review.md)
- [獨立九項檢查與兩份 SHA](../../workbook/reviews/HERMES-VISIBLE-COMPUTER-20261002/synthetic-smoke-verification.json)

### 排程與額度現值

| 項目 | 目前設定與證據邊界 |
|---|---|
| LaunchAgent | `com.maplab.freequota` 已 bootstrap；kickstart 的 live readback 為 `runs=1 / last exit code=0`，stdout 是日期閘的 `hold`，此次排程測試新增 requests=0。這證明已安裝且會保留等待，不代表第一個定時產稿班已完成。 |
| 起跑日期 | `FQ_NOT_BEFORE_UTC=2026-10-03`；台北時間 10 月 3 日 02:05／06:05 仍屬前一個 UTC 日，**首個可執行班為 2026-10-03 10:05**。 |
| 班次 | 台北每日 **02:05、06:05、10:05、14:05、18:05、22:05**，由既有 wrapper 對應 1–6 班；無效班次會在讀 env／寫檔前拒絕。 |
| 單班範圍 | 只選 `FQ_JOB=40-image-prompt.job.md`，`FQ_MAX_ITEMS=3`、`FQ_MAX_CALLS=12`；每次 fallback／HTTP error 都消耗一次上限。正常完整六班日最多 18 件、72 attempts，實際可能更少。這是受控啟動上限，不是產量承諾。 |
| 日帳本 | 重用 `investment-os/scripts/free_compute/providers.py` 的 MAPLAB `DailyCounter`：UTC 日、跨程序鎖、0600、transport 前 reserve、原子寫入、`:free` 限制與至少 3.5 秒間隔；訓練／草稿 lane 合計最多 **950 attempts**，Owner 保留 **50**。 |
| 今日歷史 | 2026-10-02 舊 runner 未接共用帳本的消耗仍為 **UNKNOWN**。新回執起始值 0 只表示新接入帳本當時為 0，不能推論整個帳戶今日沒用過；故自動班表等新 UTC 日才起跑。帳本數也只涵蓋已接入的 callers。 |
| 模型鏈 | 目前排序為 nemotron-super → dots-note → gemma，已移除先前 404 的 minimax。單題實跑發生於排序調整前，歷史 attempts 原樣保留；後續 HTTP error 回執新增 `http_status` 欄位。 |
| 寫入與 Git | 每次草稿、審稿、JSON／Markdown 回執均有唯一 run ID；不覆蓋其他班。runner 不自動 `git add`、commit 或 push。完成回執才寫 qsig；執行失敗回非零，模型互審問題與 Owner 採用另列。 |

目前自動路徑只讀合成場景清單，不含 `CONTEXT`／`INPUT_URL`；增加文件、客資、來源頁或其他 queue 前，必須另核對來源與資料邊界，不能把目前單一 queue 的驗證套用到全部二十種場景。所有產物維持未發布草稿。

程式與離線檢查：`scripts/free_quota_daily.sh`、`scripts/free_quota_launchd_wrapper.sh`、`scripts/com.maplab.freequota.plist`、`tests/test_free_quota_daily.py`；本輪 9 個 offline tests、`bash -n`、`git diff --check` 通過。測試使用 temporary ledger／mock transport，不是額外 provider requests。

### Next Bounded Action／接續 Prompt

首個定時班完成後，讀該 run 的 JSON、草稿、不同模型審稿，核對 `items_attempted <= 3`、`provider_requests_this_run <= 12`、SYNTHETIC 與必填欄位；若失敗先看 attempt／HTTP status，不增加班次或上限。接著挑一份草稿記錄「可採用／需修正／拒用」及原因，才討論下一階段擴量。尚未取得這次定時班回執前，狀態維持 `SCHEDULE_INSTALLED_DATE_HOLD`，不得寫成每日複利已被證明。

接手者先讀本節與上述單題／獨立檢查回執，再核對 live LaunchAgent 與最新 `report_<run_id>.json`。保留每日 950／Owner 50、單卡每班 3 件／12 attempts、唯一輸出及無自動 Git 寫入；今日舊用量 UNKNOWN 不補猜，模型互審不當作商業採用或權重訓練。

---

## 2026-09-24 原始規劃與冒煙紀錄（歷史保留；執行現值以上節為準）

> 來源:Owner msg 6092(2026-09-24T20:04:14)「我要他幫得上忙,改好後給我20個與我們日常工作相關的使用場景,給我1000個來回每日任務的每日安排」
> 與 msg 6093(2026-09-24T20:19:14)「比如生圖固定50整理100 生歌suno sop嘗試100至少用一半吧,我看他一直在巡查一直沒事幹」
>
> **算術口徑寫在最前面,免得日後對不上**:一件事(一個 job-run)= 產稿 1 次呼叫 + 換模型審稿 1 次呼叫 = **2 個來回**。
> 所以 **1000 個來回 = 500 件/天**。Owner 說「至少用一半」,本表就把 500 件排滿。
>
> ⚠ **口徑與實測有落差,兩個數字都留著不要互相覆蓋**:上面 2 次/件是**理論值**。
> 2026-09-24 實測(5 件扇出 job-run、`calls=20`)是 **4.0 次/件**——免費鏈前幾顆模型常直接失敗換下一顆,重試也算呼叫。
> 因此:**理論口徑 500 件 = 1000 來回;實測口徑 250 件 = 1000 來回**。
> 已回 Owner(msg 6093)的是實測口徑。真實件數落在 250~500 之間,**要跑滿幾天才知道**,
> 在那之前本表的 500 件視為排程容量上限、不是已達成值。

## 0. 為什麼以前一天只有 4 件

`data/free-quota/queue/` 只有 4 張題目卡,**一張卡一天只跑一件**,所以一天 4 件、8 次呼叫,上限 120。
不是模型沒事幹,是**班表只排了 4 件**。本輪的三個改動就是針對這一點:

| 改動 | 位置 | 解掉什麼 |
|---|---|---|
| `CONTEXT:` 本機檔案注入 + 只准照文件回答 | `scripts/free_quota_daily.sh` `load_ctx()` | 以前只送問題不送資料,模型只能編 |
| `FANOUT:` / `FANOUT_CHUNK:` / `FANOUT_N:` 扇出 | 同上 `load_items()` | 一張卡一天只跑一件 |
| 分班 `bash free_quota_daily.sh <第幾班> <共幾班>` | 同上 `BAND/BANDS` | 500 件一次跑會連續佔住機器數小時 |
| `MAX_CALLS` 120 → 1100、連續失敗 8 次收工 | 同上 | 上限卡死 + 撞到額度牆後空轉 |

`CONTEXT` 的切片語法:`檔名#tail500`、`檔名#head120`、`檔名#L61-120`。
(2026-09-24 實測:`CURRENT_STATUS.md` 單檔 245,954 bytes,不切片會吃光整個 context 預算,同題其餘檔案一律讀不到。)

## 1. 20 個使用場景

「狀態」欄只有兩種:**已進佇列**=`queue/` 裡真的有卡、當天會跑;**規格**=本表寫好了但**還沒有卡、沒有排程、沒有派工**。

| # | 場景 | 題目怎麼來 | CONTEXT / 來源 | 件/天 | 狀態 |
|---|---|---|---|---|---|
| 1 | 生圖指令(外燴場景 × 鏡位) | `lists/image_scenes.txt` 60 題輪播 | 無(純產出) | **50** | 已進佇列 `40-image-prompt.job.md` |
| 2 | 文件索引(大檔切段做可搜尋目錄) | `FANOUT_CHUNK` 依檔案長度自動切 60 行一段 | 8 份治理檔 | **100** | 已進佇列 `41-doc-index.job.md` |
| 3 | Suno SOP(場景 × 曲風骨架) | `music_scenes.txt` × `music_styles.txt` = 900 組 | 無(純產出) | **100** | 已進佇列 `42-suno-sop.job.md` |
| 4 | 待辦稽核(列出沒完成的事) | 單件 | `AGENT_CORE.md, TASK_QUEUE.md, CURRENT_STATUS.md#tail500` | 10 | 已進佇列 `10-open-todos.job.md`(目前 1 件/天,待改扇出) |
| 5 | 詢價回覆練習題 | gold 模板逐條出題 | `~/.maplab/gold_replies/`(客資不進 repo) | 20 | 規格 |
| 6 | 外帶單品文案(品項 × 賣點) | 兩份清單交叉 | 外帶品項表 | 20 | 規格 |
| 7 | SEO 標題候選(關鍵字 × 場景) | 兩份清單交叉 | `SEO_COPY_RUBRIC` 禁語表 | 20 | 規格 |
| 8 | 英文站逐段草稿 | 中文頁切段 | 中文頁原文 | 15 | 規格 |
| 9 | 案例頁分類邏輯 | 12 篇稿兩兩比 | 12 篇草稿 | 12 | 規格 |
| 10 | 禁語表逐句自檢 | 稿件切句 | `SEO_COPY_RUBRIC` | 15 | 規格 |
| 11 | pitfalls 反查(今天做的事撞過哪個坑) | 當日動作清單 | `pitfalls.md` 941 行 | 10 | 規格 |
| 12 | 兩份規範對撞偵測 | 規則段落交叉 | `AGENT_RULES.md` + 各專章 | 15 | 規格 |
| 13 | 派工六欄缺欄補草稿 | 每張缺欄的卡一件 | 任務卡 | 15 | 規格 |
| 14 | 蛛網零登入來源整理 | 每個來源一件 | 當日抓取結果 | 10 | 規格 |
| 15 | 已上架影片描述文 | 每支影片一件 | 影片清單 | 20 | 規格 |
| 16 | 縮圖文字版位(影片 × 版位) | 交叉 | 影片清單 | 15 | 規格 |
| 17 | 日照中心與宗教禁忌問題單 | 場景 × 禁忌類別 | 場景表 | 10 | 規格 |
| 18 | 詢價漏斗缺口對照 | 表單欄位 × 真實問句 | 表單定義 | 10 | 規格 |
| 19 | 逐字稿事實抽取 | 對話切段 | LINE 逐字稿(輸出落 `~/.maplab/`) | 20 | 規格 |
| 20 | 當日日報彙整成週報素材 | 每份日報一件 | `report_YYYYMMDD.md` | 13 | 規格 |

**合計 500 件/天 = 1000 個來回。** 已進佇列的 1~4 合計 **260 件**,其餘 240 件是規格。

## 2. 每日時段安排(6 班)

`bash scripts/free_quota_daily.sh <第幾班> <共幾班>`,例如第 3 班寫 `bash scripts/free_quota_daily.sh 3 6`。
扇出題目按班次取模分配(`items[BAND-1::BANDS]`),單件題目只在第 1 班跑。

| 班 | 時間 | 約件數 | 約來回 | 這一班的重點 |
|---|---|---|---|---|
| 1 | 02:00 | 83 | 166 | 單件題目(待辦稽核)+ 文件索引第一份 |
| 2 | 06:00 | 83 | 166 | 文件索引 + 生圖 |
| 3 | 10:00 | 83 | 166 | 生歌 SOP + 文案類 |
| 4 | 14:00 | 83 | 166 | 生圖 + SEO 類 |
| 5 | 18:00 | 84 | 168 | 生歌 SOP + 影片類 |
| 6 | 22:00 | 84 | 168 | 文件索引收尾 + 週報素材 |
| — | 合計 | **500** | **1000** | |

每班跑完各落一份紀錄到 `report_YYYYMMDD.md`;件數對不上時看得出是哪一班掉的。

## 3. 紅線(與階段無關,永久有效)

- 股票的程式單一律避開:不讀不改不執行 `investment-os/` 下單與交易執行路徑。
- 金鑰 / token / cookie / 帳密 / 授權碼、`secrets/`、`.env` 一律不進題目、不進產出。
- 他人客戶資料、兒童照片與私有客照不送第三方。
- 客資內容不進 repo、不進 Telegram;`~/.maplab/` 下的產出只回報筆數與路徑。
- 所有產出都是**草稿**,發布永遠是人按的。
- 報價數字不自動發;不得憑猜測產生數字。

## 4. 還沒做的事(不得寫成已完成)

1. 場景 5~20 共 16 題**只有規格,沒有卡、沒有排程**。
2. launchd 六班排程**還沒建**,現在要跑得手動帶班次參數。
3. OpenRouter 免費模型的**每日真實上限還沒量到**。程式上限已改 1100,牆在哪一格要靠斷路器實際撞一次才有數字;今天實跑累計 **34 次呼叫 / 1100**,離牆很遠所以還沒撞到。
4. **全量 500 件的一天還沒跑過**。目前只跑過 50 分之 1 的冒煙班。

## 5. 冒煙驗證紀錄(2026-09-24,`bash scripts/free_quota_daily.sh 1 50`)

`[done] jobs=7 calls=34`,三張新卡全部產出:

| 卡 | 結果 | 抽查 |
|---|---|---|
| `40-image-prompt` | 扇出 1 件成功 1 件 | — |
| `41-doc-index` | 扇出 2 件成功 2 件 | item=`SYSTEM_DIRECTORY_INDEX.md#L361-420`,索引到「8. 找資料標準流程」「9. 複利迴圈」「10. 目前兩條最高價值 Loop」;`sed -n '361,420p'` 回核 = 該範圍第 3、24、59 行,**三條全部真的在那段裡** |
| `42-suno-sop` | 扇出 2 件成功 2 件 | item=`企業茶會報到與交流｜city pop instrumental / 100-115 BPM / …`,產出 `BPM: 108 (100-115)`,**落在給定區間內** |

`CONTEXT` 注入同日另驗過一次:`10-open-todos` 讀 `CURRENT_STATUS.md` 後抄出的狀態字樣
`OPENROUTER_OUTPUT_PASS` / `LIVE_NOT_DEPLOYED` / `SIMULATOR_NOT_IMPLEMENTED` / `PRIVATE_MVP_RENDERED_UNVERIFIED`,
`grep -c` 回核實得 **5** 筆,**原字照抄沒有編**。
