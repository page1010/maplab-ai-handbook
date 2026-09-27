# 複利計畫巡查 — 2026-09-27（首次完整跑完五步驟）

> 執行者：A1（Claude Code，手動觸發，因 launchd 自動化本次證實從未成功產出過此檔案）
> 前次同名報告：無（`state/compounding-patrol-*.md` 在此之前完全不存在）

---

## 📊 全貌（Step 1）

- 近 7 天（09-20 ~ 09-27）：**202 個 commit**，集中在 `data/`(484 files)、`handoff/`(215)、`scripts/`(90)、`bot_a6/`(25)；`skills/` 僅 3 次觸碰、`pitfalls.md` 0 次（最後一次修改 09-18，已 9 天）。
- 絕大多數本週 commit 屬於 Investment OS / Hermes 側（free-quota 班表、hermes patrol、探針 P9-P14、套利研究票 #59-#64），而非 MAPLAB A2-A8 核心業務。
- **> 48h 無 commit**：A2、A3、A4、A5、A7、A8（沿用 `AGENT_RECALL_PROMPTS.md` 檔頭數字：T-A4-002 ~4309h、T-IOS-KOL-001 ~2797h、A8 ~2612h、T-A7-001 Phase 3 第 71 天延誤）。
- A6 本週僅 3 個 commit（09-25：`8965796`/`11d3d0d`/`5a21f91` zero-model budget-reverse engine + splitter fix + model pin），皆為後台強化，非真實客人接觸。
- Owner 待決最久：T-A7-001 Phase 3 Zone B/C 金額確認，Owner 自 07-18 起未回覆，**已第 71 天**。
- NEEDS_REVIEW 10 tasks，累計 **~2077h（~86.5 天）**未決。

---

## 🔍 五問結果（Step 2）

### ① 業務閉環是否對準價值量尺？
本週**未見推進**。A5/A6/A7 現金流閉環三大解鎖點（A6 LINE Webhook Channel 1654658337 待填、A7 Phase 3 待 Owner 定案、A5 GAS Dashboard 待啟動）自數週前起狀態不變。A6 這週的技術投入（zero-model budget-reverse engine）強化了報價估算能力，但 `OLLAMA_FALLBACK_DISABLED`（Owner 政策），且 LINE 端仍未開始收真實客人訊息——技術有進步，但沒有真人使用量可驗證。A2 SEO 本週 0 commit，無新 GSC 驗收窗口證據。**So What**：系統本週的 202 個 commit 中，能追溯到「真實客人使用」證據的是 0 個；投入大量算力在 Hermes/free-quota 基礎工程，與 `docs/fable5-direction-and-guidance.md` 明定「現金流業務閉環最高優先」的方向有落差，需 Owner 判斷是否要拉回配比。

### ② 三類消音掃描
- **消音1（做完沒人知道）**：本週無新證據——daily patrol commits（如 `1eebb2e`）持續逐一點名 non-patrol commit，未發現漏報案例。
- **消音2（拍板沒人推進）**：發現一個結構性個案——`scripts/compounding_patrol_staleness.sh`（launchd 每日跑）已連續至少 **14 天**對 Owner 發送同一則 Telegram 通知「⚠️ 複利巡查從未記錄成功」（`state/compounding_patrol_staleness.log` 14 行相同訊息），但沒有人開 Task Card 真正修復根因——系統自己在喊，沒人接。
- **消音3（宣稱未驗證）**：`skills/compounding-patrol-prompt.md` 底部宣稱 launchd `com.maplab.compounding-patrol` 會每週執行本巡查；但實測發現 **這是假象**——`state/compounding_patrol_last_ok` 檔案從未被寫入過，`find` 找不到任何一份 `state/compounding-patrol-*.md` 報告，近 4 次執行紀錄（09-13 log 記錄到「偵測到另一個並行 claude -p，主動讓步」、09-20 `rc=127`、09-23「Execution error」15 bytes、09-27 今天 0 bytes）沒有一次真正完整跑完五步驟並落檔。本檔是**史上第一份**由此 SOP 產生的報告，且是人工觸發，不是排程觸發。

### ③ 複利四環哪環斷了？
- **環1 輸出落檔**：表面活躍（202 commits），但集中在 Hermes/free-quota 側；`pitfalls.md` 9 天無新條目，`skills/` 9 天僅 3 次觸碰——內容偏離複利迴圈核心（踩坑→技能書）。
- **環2 週複利蒸餾（本輪最弱）**：`skills/auto/` 目錄自 2026-04-17 建立以來**只有一個 `.gitkeep`**，5 個多月零自動生成技能書。同期 pitfalls.md 持續有新條目（09-01、09-18），代表「踩坑」有被記下，但從未被蒸餾成可複用技能書——這一環是純結構性斷點，不是本週才發生，只是本次巡查第一次真正核對出來。
- **環3 教材固化**：本次巡查未取得 B5 每月蒸餾評分（`reports/capability-inventory/`）與 `packages/local-model-teaching/` 本月是否有新包的證據，標記**不確定**，需下次巡查專門核對。
- **環4 地端繼承**：本週明確狀態是 Owner 主動關閉，非系統失能——A6 gateway commit 顯示 `OLLAMA_FALLBACK_DISABLED`（`local_model_policy.json` 停用 gemma4/qwen14b）。這是決策後果，不是複利斷點，但代表地端繼承目前掛零，需等 Owner 重新開放。

**判斷**：本輪最弱環 = **環2（週複利蒸餾）**——`skills/auto/` 5 個月零產出是最具體、最可驗證的斷點證據。

### ④ 資源浪費點
- **具體浪費 1（已找到）**：`com.maplab.compounding-patrol` launchd 排程（每週日 20:05 觸發）過去至少 4 次執行 100% 未完整成功，其每日 staleness backstop 已空轉 14+ 天持續告警卻無人修復——純粹的自動化空轉 + 重複告警噪音。根因尚未定位到底層行號（`claude -p` 在 launchd 環境下輸出 0 bytes 即退出，PATH/binary/token 逐項排查均正常，需要下次帶 `set -x` 重跑一次才能鎖定，本次巡查標記為**不確定，需再診斷**，不裝懂）。
- 受限於本次巡查時間，未逐一深掘本週 202 個 commit 內容找「同操作做兩次以上」的其他重複人工案例，此為本次巡查的**已知覆蓋缺口**，非「本週無」。

### ⑤ Owner 待決清單是否最新且手機可辦？
**發現缺口**：`state/owner-action-queue.md` 這個檔案**從未存在過**，儘管 `docs/fable5-direction-and-guidance.md`「回報後自己派工修理」步驟 4 明確要求維護它。Owner 待決事項目前只是散落記錄在 `AGENT_RECALL_PROMPTS.md` 檔頭長文字段落與 `CURRENT_STATUS.md`，沒有一個集中、可 5 分鐘手機辦完的單一清單。**已於本次巡查建立該檔案**（見下方「本次修正」），首次收斂現有已知待決項。

---

## 🔧 本次修正（Step 3）

直接修（已完成，本次一併 commit）：
1. **新建** `state/owner-action-queue.md` — 首次建立 SOP 要求但過去從未存在的 Owner 待決清單。
2. **新增** `pitfalls.md` 條目——「自動化排程宣稱運作但從未驗證產出」，記錄本次發現的複利巡查 launchd 空轉模式，供下次巡查或維護時參考。
3. **新增** `TASK_QUEUE.md` Tier 1 項目——修復 `com.maplab.compounding-patrol` launchd 排程（根因待 `set -x` 重跑定位，屬於 A1 可自行診斷範疇，不需 Owner 操作）。

寫進 TASK_QUEUE 的提案：
- 提案者：A1；優先序：Tier 1（複利機制本身失能，阻塞整條「巡查→發現→修正」迴圈）；解鎖：讓複利巡查真正變成每週自動跑，而非每次都要 Owner 手動貼 prompt。

需 Owner 決策 → 已寫入 `state/owner-action-queue.md`（見該檔案，5 項，含現金流閉環三項舊案 + 本次新發現的巡查機制修復項）。

---

## 📎 沉澱教訓（Step 4）

已寫入 `pitfalls.md`：自動化排程「檔案存在、log 檔存在、launchctl 顯示已註冊」不等於「真的成功執行過」；驗證自動化健康的唯一方式是檢查其**宣稱的產出物**是否真的存在（本例：`state/compounding-patrol-*.md` 報告檔 vs `state/compounding_patrol_last_ok`），而不是檢查排程本身是否註冊。

---

## 📎 落檔

- `state/compounding-patrol-2026-09-27.md`（本檔）
- `state/owner-action-queue.md`（新建）
- `pitfalls.md`（新增條目）
- `TASK_QUEUE.md`（新增 Tier 1 提案）
- commit：待 `checkpoint.sh` 產生 hash（見下方）
