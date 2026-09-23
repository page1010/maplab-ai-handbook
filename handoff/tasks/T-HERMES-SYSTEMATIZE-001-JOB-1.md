# 工作單 T-HERMES-SYSTEMATIZE-001-JOB-1｜音樂風格分類樹草案 v0

> 框架卡（規格 SSOT）：`handoff/tasks/T-HERMES-SYSTEMATIZE-001.md` §5 JOB-1
> 執行者：hermes（免費鏈上游 LLM，走 `data/free-quota/queue/32-style-taxonomy.job.md`）
> 建立：2026-09-22，Writer=Fable5 本人・同 session 續接
>
> **這是第一張照 SECTION 27 第三節五欄格式開出的工作單。** 模板＝`_WORK_ORDER_TEMPLATE.md`；
> 派工前必跑 `python3 scripts/check_work_order.py handoff/tasks/T-HERMES-SYSTEMATIZE-001-JOB-1.md`，
> exit 0 才准送出。規則寫了不用，等於沒寫（任務 #22 的成因）。

---

## 派工欄位（五欄硬性 ＋ 可逆性）

- **結果**: `data/free-quota/style-taxonomy/taxonomy_v0.md` 存在，裡面是 3-5 個大類的風格分類樹，每類寫出判別特徵、代表曲的道龐克代號、可複用的 prompt 骨架，並另立一節列出歸不進任何一類的邊界案例；之後要替新曲挑風格的人看這一份就能歸類，不必再讀 14 筆原始 style_prompt
- **指標**: 分類樹每一類都至少指回一個 `style_registry.jsonl` 裡真實存在的代號（代號可在該檔 grep 到，零虛構）；14 首全數有歸屬或被列入邊界案例，不得遺漏；邊界案例節非空（全部歸得進去＝分類太鬆，視為未通過）；輸出檔不含任何歌詞
- **期限**: 2026-09-24 12:00 前（免費鏈班表每日跑，兩個班次的餘裕）
- **權限**: 只讀 `data/music-style-db/style_registry.jsonl` 與 `STYLE_REGISTRY.md`；只寫 `data/free-quota/style-taxonomy/` 底下的新檔；**不得修改 style_registry.jsonl 或任何既有檔**；提交由 `scripts/free_quota_daily.sh` 既有流程處理，hermes 自己不 commit、不 push、不重啟任何 process；不得碰金鑰、真倉、對外發布
- **回報點**: 跑完當班次回寫 `data/free-quota/report_YYYYMMDD.md` 一行結論並在本檔底部補「執行紀錄」一節。done = 指標四項全部被換模型審稿驗過（班表 v2 的 A 產 B 審，審稿意見落 `data/free-quota/reviews/`）且 `taxonomy_v0.md` 已落檔；blocked = 讀不到 registry、或 14 首資訊不足歸不出 3 類以上時，寫下卡在哪一筆、已試過哪些歸法，**不准靜默結束、不准自標 PASS**
- **動作可逆性**: 可逆（只新增檔案，不刪不改既有資料；錯了刪掉重跑即可）

---

## 退場條件（沿用框架卡 §6，不得自行放寬）

1. 規則沒寫到的 → 標 `需人工` 附原始資料位置，**不猜**。
2. 需要價格／檔期／飲食安全／宗教禁忌判定 → 一律 `需人工`（fail-closed 四類）。
3. 引用不到實體的代號或曲名 → 不得寫進輸出（「357 模板」教訓：傳說數字查無實體）。
4. 自己跑完不得自標 PASS；驗收由換模型審稿或人做。

## 接續狀態

- **狀態**: 🔄 IN_PROGRESS（工作單已成形，等班表撿 job）
- **最後活動**: 2026-09-22
- **動作可逆性**: 可逆
- **接續點**: 看 `data/free-quota/style-taxonomy/` 有沒有 `taxonomy_v0.md`；沒有就看當日 `report_YYYYMMDD.md` 裡 32-style-taxonomy 那一行的結果

## 執行紀錄

（executor 回寫處。**終態未寫＝未完工**，不論成敗都要留一行。）
