# 跨專案治理科技樹 — MAPLAB 外燴 × Investment OS

> 生成：2026-07-07（Claude Fable 5，跨專案治理診斷任務）
> 用途：(1) 治理問題與自動化閉環缺口診斷（附證據）；(2) 文化→規則→自動化的落地梯子；
> (3) 全角色/全任務引路科技樹；(4) 綜合判讀資料來源 pillar；(5) 未來展望。
> 定位：**引路圖，不是真相源**。即時狀態永遠以兩邊 `CURRENT_STATUS.md` + `launchctl` 為準。
> 本文件為快照，過期資訊以新證據為準（Time-weighted truth，OPERATING_CULTURE #16）。

---

## 0. 費曼複述（150 字白話版）

這是一家一人公司，老闆有兩盤生意：外燴接單（MAPLAB）和自己的投資研究（Investment OS）。
他僱了一群 AI 員工，每個人有名字和職責，所有工作記錄都寫在共用筆記本裡，
換班的人看筆記就能接手。系統還有「自動鬧鐘」定時跑巡邏和報表。
現在的問題：**負責檢查大家有沒有偷懶的那個檢查員，自己已經倒在地上一星期了，
而且沒有人負責檢查檢查員**。這份文件就是找出所有這類洞，並畫一張
「先修什麼、再建什麼」的地圖。

---

## 1. 治理診斷 — 依嚴重度排序（全部附證據）

### 🔴 P0：治理量測層整條死亡，而且是靜默死亡

| # | 問題 | 證據（2026-07-07 實測） | 根因 |
|---|------|------|------|
| 1 | **gen_system_truth（治理真相機）每天啟動、每天死** | `launchctl list` → `com.investmentos.system-truth-gen` last exit=1；`system_truth_gen.err.log` 尾端：`PermissionError: [Errno 1] Operation not permitted: '/Users/pagemacmini/Documents/New project/CURRENT_STATUS.md'` | **macOS TCC 權限**：launchd 起的 CLT Python 3.9 沒有「檔案與資料夾→文件」授權，IS repo 又放在 `~/Documents` 受管制區。out.log 只有 6 行 start、沒有 done → 06-29 之後全部死在讀第一個檔 |
| 2 | **SYSTEM_MAP.md 停在 06-29**（8 天前，宣稱每日覆寫） | 檔頭 `Generated: 2026-06-29T00:05:12+0800` | 同上（#1 的下游） |
| 3 | **live_health.json 停在 06-30**（宣稱每 15 分鐘覆寫） | `generated_at: 2026-06-30T09:56:33`；launchctl `com.investmentos.live-health` last exit=0 但檔案 7 天沒動 | exit=0 但無產出 = **靜默失敗**（很可能同為 TCC 或排程被卸載後重載未生效）；違反自家規則「靜默失敗 = AI 幻覺空間」 |
| 4 | **nightwatch 自 2026-06-02 停擺**（07-07 全功能檢討已確認，兩位外部評審共識「先修這個」） | MAPLAB `CURRENT_STATUS.md` 2026-07-07 [B1] 段 | 待驗證，高機率同 TCC 家族 |
| 5 | **escalation_critical_count=15 且無人消化** | live_health.json（06-30 快照） | CRITICAL 升級有「產生」機制、沒有「收斂」機制（見 P1-1） |

**P0 的結構性教訓：監測器沒有監測器。** 所有 freshness alert 都由 live_health / truth-gen 產生，
它們自己 stale 時沒有任何東西會叫。這是「誰來看守看守者」的字面案例。

**P0 最小修法（一次修一族）：**
1. 給 launchd 使用的 Python binary 開「完全取用磁碟」或把 IS repo 遷出 `~/Documents`（治本；`~/Documents` 是 TCC 管制區，任何 launchd job 讀它都是地雷）。注意 pitfalls 錯誤 182 的 `ios-*` symlink wrapper 會改 argv0 → TCC 以 binary 認定授權，wrapper 上線時間與故障開始時間吻合度值得查。
2. 修好後，**加一條「守門狗的守門狗」**：MAPLAB 端已在跑的 `com.maplab.patrol-hourly`（不同 repo、不同權限路徑、目前活著）加 10 行檢查——`live_health.json` 的 `generated_at` 超過 2 小時 → 直接發 Telegram。交叉看守，不共享死因。
3. 在 `gen_system_truth.py` 入口加 fail-loud：任何 exception → 寫一行到 escalation queue + Telegram，禁止只留 err.log。

### 🟠 P1：閉環斷在「最後一哩」——偵測有、產卡無、收斂無

| # | 問題 | 證據 |
|---|------|------|
| 1 | **Self-Healing Loop 停在 DRAFT 等 Owner 拍板 26 天**。S1 自動產卡 + S4 可逆自動關卡的 pilot 06-11 已跑通（`reviews/SELF-HEALING-LOOP-PILOT-20260611/run_log.md`），但 spec 標 `no auto-deploy`，三個待拍板問題（courier 唯一脊椎 / Level 0-4 唯一分級 / 可逆桶自動閉環）從未送進 Owner 決策佇列 | `docs/agent_governance/SELF_HEALING_LOOP_BINDING_SPEC.md` v1.1-draft 2026-06-11 |
| 2 | **MAPLAB 48h 超時警報只會累加、不會收斂**：V6-P2/V7 ~1272h、A2-005 ~912h、LEARNING-LOOP ~497h、IOS-KOL ~373h、A5 ~337h、A8 ~288h、A6 ~252h。每日巡查忠實記錄超時，但沒有機制強制三選一（推進/交棒/封存 💤+Owner 簽字）。警報疲勞 = 沒有警報 | MAPLAB `CURRENT_STATUS.md` 巡查列 2026-07-07 |
| 3 | **Owner 決策佇列沒有時效治理**：GCP 帳單 🔴 掛 82 天；post 698 改法、T-A2-003 排程、A6 webhook 貼入……全部散在各 task card 的「等 Owner」，沒有單一佇列、沒有過期升級、沒有「5 分鐘 action」打包 | 同上；違反文化 #10（Decision escalation beats waiting） |
| 4 | **Learning Loop 建到 P1 就停**（reaction ledger 有了，P2 token registry / P3 eval / P4 closure writer 沒建）→ 系統會「記錄反應」但不會「學」 | T-A1-LEARNING-LOOP-001，~497h 無 commit |
| 5 | **Evolution Channel 只有 propose、decide 積壓未量測**：strategy_patches 需 Owner/B1 decide，但沒有任何巡檢報「目前 proposed 積壓 N 筆、最老 M 天」 | `docs/EVOLUTION_CHANNEL.md` |

### 🟡 P2：紀律靠散文，不靠程式

| # | 問題 | 證據 |
|---|------|------|
| 1 | **checkpoint 紀律破口**：06-20 一個 A8 標籤 commit 掃進 232 檔案/25K 行、混入 4 個角色近 3 天未存檔工作。「立即 commit」規則存在於 5 份文件，但沒有任何自動 gate | MAPLAB `CURRENT_STATUS.md` 2026-06-20 巡查段 |
| 2 | **CURRENT_STATUS.md 手工維護漂移**：曾累積 66 筆重複巡查列（07-06 人工清掉）；任務表漏登（T-IOS-KOL）、狀態誤標（T-A5-004 被標 CRITICAL 實為穩定）。136KB 的手寫檔案當唯一真相源，靠巡查 LLM 自律 | 同上 07-06 / 06-21 段 |
| 3 | **文化文件 36 條規則，有程式 gate 的不到 1/4**（詳見 §2 梯子表）。例：#8 Evidence（無 receipt 不算完成）、#36 一事一 session、#12 Progress Log——全靠 agent 自覺 | `docs/OPERATING_CULTURE.md` |
| 4 | **跨 repo mirror 新鮮度未驗**：`sync_cross_project_mirror.sh` 宣稱每日同步，但沒有 staleness 檢查（同 P0 模式的潛在複製） | A0/B1 handoff Step 8 |

---

## 2. 文化 → 規則 → 自動化 梯子（達標手段：程式，不是口號）

原則：**每條文化最終都要有一個「機器版」**——文化寫給人看，gate 寫給 runtime 跑。
下表列可自動化程度最高的 8 條（依投資報酬排序），每條給「最小程式 gate」。

| 文化條款 | 現況 | 最小自動化 gate（建議） | 落點 |
|---|---|---|---|
| #17 Live reality beats repo notes | gen_system_truth 已實作但死亡 | **修 TCC + fail-loud + 交叉看守**（P0 修法） | IS `scripts/gen_system_truth.py` + MAPLAB patrol-hourly |
| #8 Evidence over output（無 receipt 不算完成） | 散文 + 巡查抽查 | `checkpoint.sh` 加檢查：commit 訊息含 `feat/fix` 但 diff 無 `workbook/reviews/` 或 task card 變更 → 警告寫入 commit trailer | MAPLAB `scripts/checkpoint.sh` |
| #12/#33 執行迴圈、不准停車庫 | 48h 警報只記錄 | 巡查腳本對超時任務自動產「三選一決策卡」（推進/交棒/封存）進 Owner 佇列，連 3 次未決自動標 💤 parked（可逆，Owner 隨時解封） | MAPLAB patrol + `handoff/owner-queue.md`（新增，見 §5-R2） |
| #10 Decision escalation（不安靜等待） | 各 task card 自行掛「等 Owner」 | **單一 Owner 決策佇列檔**：所有 blocker 登記 `question/options/建議/5min-action/deadline`，patrol 對超 7 天者升級 Telegram | 同上 |
| Self-Healing S1/S4（偵測→卡→可逆自動關） | pilot 已通、spec 卡簽核 | 把 §1-P1-1 的三個拍板問題做成一張 5 分鐘決策卡送 Owner；核准後 `self_healing_loop.py` 掛 launchd（Level 0-2 可逆桶先行） | IS `scripts/self_healing_loop.py` |
| #29 單一 runtime 入口 / no duplicate LaunchAgent | Shadow 巡檢規則存在 | gen_system_truth 已做 UNTRACKED_RUNNING/MISLABELED 掃描（表格證明有效，0 異常）——修活它即可，不新建 | 已有，修 P0 |
| #18 Incremental save | 散文 | MAPLAB 已有 `telegram-checkpoint`（每小時）；加「dirty worktree > 6h 且 > 50 檔」偵測 → Telegram 點名角色 | MAPLAB `scripts/` 既有 job 加檢查 |
| #16 Time-weighted truth / freshness | live_health 有 data_freshness 欄位（已死） | 修活後：每個 owner-facing 產物標 `generated_at`，超過自宣稱週期 2 倍 → 自動進 escalation。**規則：任何宣稱「每 X 自動更新」的檔案，都必須有獨立於自己的 staleness 檢查** | IS `write_live_health.py` + MAPLAB patrol |

**反面守則（同樣重要）**：SELF_HEALING spec 的教訓——**接線優先於新造**。上表所有 gate
都是往既有腳本（checkpoint.sh / patrol / gen_system_truth / self_healing_loop）加 10-30 行，
不新建任何平行棧。誰提議「建一套新的監控系統」，先讀 `SELF_HEALING_LOOP_BINDING_SPEC.md` §0。

---

## 3. 科技樹（全角色 / 全任務引路圖）

圖例：✅ 已解鎖（活著在跑）｜🔧 建造中｜🔴 建了但故障（優先於一切新建）｜⬜ 未建（只有設計）
依賴規則：**下層節點死亡時，禁止解鎖其上層節點**（stale data 包漂亮功能 = 07-07 評審共識的反模式）。

```text
T0 共用底座（集團層，兩專案共用）
├─ ✅ Git 雙 repo 真相源（maplab-ai-handbook / New project）＋ checkpoint.sh
├─ ✅ 角色體系：A0-A8（外燴）｜B1-B4（建造/審查/存檔/巡查）｜IOS-*（投資）｜WIN（Windows採集）
├─ ✅ 召喚面：Chrome Extension v5.6.1（30 modules）＋ Telegram bot ×2 ＋ Cowork
├─ ✅ 文化憲法：OPERATING_CULTURE 36 條 ＋ AGENT_RULES S16(三層審查)/S19(無人長跑)
├─ ✅ 多模型艦隊：Claude(決策) / Codex(審+A5接管) / Antigravity(唯讀評審) / Ollama(B-role例行)
├─ 🔧 三人小組評審制（SEO 已實跑 2 輪、InvestOS 已實跑 1 輪 → 待制度化成模板）
├─ 🔴 治理真相機 gen_system_truth（TCC 死亡 → 本樹 P0 根節點，修它解鎖一切）
│   └─ ⬜ 守門狗的守門狗（MAPLAB↔IS 交叉 staleness 看守）★修完立刻建
├─ ⬜ Owner 決策佇列（單一檔 + 時效升級）★P1
└─ ⬜ Self-Healing Loop 上線（pilot 已通，等 3 個拍板）★P1
    └─ ⬜ Learning Loop P2-P4（token registry / eval / closure writer）

T1 MAPLAB 外燴支線                          T1' Investment OS 支線
├─ ✅ A5/A6 報價：Sheet-first + GAS         ├─ ✅ 風控層（系統最強維度，07-07 評審認證）
│   └─ 🔧 A5→Codex 接管（T-A5-007 待認領）  │   ├─ ✅ 曝險帳本 exposure-ledger（daily 16:45）
├─ ✅ A2 SEO 工廠 + publish gate（F-1食安） │   ├─ ✅ 死亡清單 / margin-call distance
│   ├─ ✅ 三人小組評審（婚禮pillar已定案）   │   └─ ✅ 實單哨兵 IOS-SENTINEL v3（06:30）
│   └─ 🔧 B3 廣告試跑（NT$100/天操作稿ready）├─ ✅ Telegram operator + 三 Dashboard
├─ 🔧 A4 照片分類 S11 補跑（PID 10941，     ├─ ✅ 財經早報 / 籌碼快報 / KOL 雷達（20 項
│      todo 3,377，預計 07-08 完成）        │      使用者可見輸出，見 07-07 盤點）
├─ ✅ A7 FAQ（Q7/Q10 政策已落地）           ├─ 🔴 nightwatch（06-02 停擺）★P0 家族
├─ 🔧 A8 短影音（地端 zoompan，待審核）      ├─ 🔴 live_health 快照（停 06-30）★P0 家族
├─ ⬜ A6 LINE webhook 貼入（等 Owner 5min） ├─ ⬜ investment_goals.md 一頁式目標文件
└─ ⬜ A3 Meta 冷受眾上線（等 Owner 操作）    │      （風控/thesis/流程三分類）★依賴 nightwatch 修復
                                            ├─ ⬜ Goal-Signal-Decision-Review 複利循環
T2 跨專案匯流（解鎖條件：T0 的 🔴 全修復）    │      pilot ×2（早報+曝險帳本掛目標對齊）
├─ ⬜ 跨 repo 治理週報（單一機器生成）        ├─ ⬜ 世界觀/終局層（Owner 四層篩選第一層，
├─ ⬜ MVP 可打包架構（MAPLAB=首客戶，        │      目前完全空白 = 兩位評審共識的系統級盲點）
│      開發過程=SEO 內容，養名單）           └─ ⬜ Dashboard 目標分頁（明確最後做）
└─ ⬜ InnerFlowLab/Substack 恢復（Owner 令）
```

**引路規則（給每一個被召喚的角色）：**
1. 你的任務節點若在 ⬜，先往上找它依賴的 🔴/🔧——修上游優先於建下游。
2. 🔴 節點永遠是全系統最高優先（現在 = TCC 權限修復一件事解鎖三個紅點）。
3. 新建任何監控/派工/分級機制前，先讀本文件 §2 反面守則。

---

## 4. 綜合判讀資料來源 Pillar（像判讀行情一樣判讀系統）

判讀任何治理問題時的固定讀法——**問題 → 來源組合 → 新鮮度紅線**：

| 你想判讀什麼 | 讀什麼（優先序） | 新鮮度紅線 |
|---|---|---|
| 系統此刻活著什麼 | `launchctl list \| grep -E "investmentos\|maplab"`（鐵證）→ `state/live_health.json`（快照，先驗 generated_at）→ `SYSTEM_MAP.md`（日更，先驗檔頭日期） | launchctl=即時；live_health>2h 作廢；SYSTEM_MAP>2 天作廢 |
| 最近誰動了什麼 | 兩 repo `git log --oneline -15` → 各自 `CURRENT_STATUS.md` 最新事實核對段 | commit 是事實；STATUS 敘述可能漂移，衝突時信 git+runtime |
| 任務卡住在哪 | MAPLAB `CURRENT_STATUS.md` 任務表+Blockers → `handoff/tasks/T-*.md` 接續點 | 任務表狀態欄曾誤標，重大決策前回讀 task card 原文 |
| 為什麼壞、以前壞過嗎 | 兩邊 `pitfalls.md`（189+ 條，先 grep 關鍵字）→ 對應 err.log | pitfalls 永久有效；log 只信最後 N 行 |
| 規則允不允許 | `AGENT_RULES.md` → `OPERATING_CULTURE.md` → `decisions.md`（為什麼不用 X） | 治理文件慢變；與 CURRENT_STATUS 衝突時以 STATUS 為準 |
| Owner 要什麼 | `b1-investment-os-owner-persona-canonical.md`（投資判斷框架）＋ `docs/company-values.md`＋ auto-memory | 人不變快；校正原話一字不漏優先 |
| 外部表面真相 | Chrome/Telegram 眼見為憑（pitfalls 185：py_compile/curl/log 只算 preflight） | 只信本輪讀回，不信上輪截圖 |

**判讀鐵律**：任何一格的來源自己就是自動產物時，先驗它的 `generated_at` 再用——
本次診斷的破口正是「引用了 stale 的量測產物而不自知」的一步之遙。

---

## 5. 未來展望與行動順序（Roadmap）

順序沿用 07-07 InvestOS 全功能檢討兩位外部評審的完全一致結論，並擴到跨專案：
**先讓資料可信 → 再建目標層 → 再接循環 → 最後才做展示面。**

### R0（本週，全部 ≤1 天工作量）— 讓量測層復活
1. 修 TCC：授權或遷移 repo，讓 gen_system_truth / nightwatch / live_health 跑通（P0 表 3 修法）。
2. fail-loud 進 escalation + Telegram（10 行）。
3. MAPLAB patrol-hourly 加對 IS live_health 的交叉 staleness 看守（10 行）。
4. 驗收：SYSTEM_MAP.md 檔頭日期 = 今天，連續 3 天。

### R1（下週）— 閉環拍板 + Owner 佇列
1. 把 Self-Healing 三個拍板問題做成一張 5 分鐘決策卡（附 pilot 證據）送 Owner；核准即掛 launchd（可逆桶先行）。
2. 建 `handoff/owner-queue.md` 單一決策佇列，收攏 GCP 帳單(82天)/post 698/A6 webhook/T-A2-003 排程等全部「等 Owner」項，含 deadline 與 5-min action。
3. 48h 超時任務自動產三選一決策卡（§2 梯子表第 3 列）。

### R2（本月）— 目標層 + 複利循環 pilot
1. IS：`investment_goals.md` 一頁式（風控/thesis/流程），接早報+曝險帳本兩個 pilot 掛目標對齊欄。
2. MAPLAB：B3 廣告試跑上線（操作稿已 ready），Learning Loop P2 復工。
3. 補世界觀/終局層第一版（哪怕 10 行——從「完全空白」到「有 v0」是質變）。

### R3（下季展望）— 匯流
- 跨 repo 治理週報機器生成（單一腳本讀兩邊 truth 產物）。
- MVP 可打包架構：MAPLAB 當首客戶驗證「AI 員工手冊系統」可複製性；開發過程回灌 SEO 內容。
- 文化 36 條逐條補機器版 gate（§2 表為前 8 條，每月收 2-3 條）。

### 北極星（不變）
兩個系統共享同一個終局：**Owner 只做判斷，系統自己維持可信**。
每一次迭代問同一句話：「這個改動是讓 Owner 的照顧成本下降，還是只是搬家？」
（OPERATING_CULTURE #35：No automation without steward）

---

## 6. 本次診斷的理解邊界（誠實列缺口）

1. nightwatch 停擺是否同為 TCC 根因——**未驗**（需 tail 它的 err.log，R0 第 1 步時順手驗）。
2. Evolution Channel `strategy_patches` 目前 proposed 積壓筆數——需開 SQLite 查，本輪未查。
3. `sync_cross_project_mirror.sh` 最後成功同步時間——未驗。
4. escalation_critical_count=15 的逐筆內容——只有計數，未讀 queue 明細。
