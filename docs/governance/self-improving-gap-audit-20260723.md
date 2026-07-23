# MAPLAB 自我改進系統 — 缺口稽核與補強紀錄（2026-07-23）

> 用文章《Fable 5 自我改進系統實戰：14 步》的 4 層框架（原語→編排→記憶→自我改進，一個回饋迴圈）當尺，
> 對照 MAPLAB 現況。稽核者：A2（Cowork）。證據來源：2026-07-23 這輪親眼所見（非泛論）。
> 原則呼應文章第 14 步：把安全邊界當設計、不造成無聲退步——高風險（動 12 agent 共用流程）的改動寫成
> 已備 diff 的卡待 host 測，不盲改；低風險、可自證的改動當場落地。

---

## 一、判定

MAPLAB **已經是這套系統的認真實作**（四層都有雛形），但兩個結構問題讓它「不夠自動」：
1. **回饋迴圈沒閉合**——失敗不會自動蒸餾成規則（L4 斷）。
2. **自動化不是冪等/不自癒**——checkpoint 親手製造下一次的髒狀態；stale lock 無法自癒。

## 二、四層對照（證據）

| 層 | 現況（有） | 這輪看到的破口 |
|---|---|---|
| L1 原語 | A0–A8/B1–B4、Chrome/computer、Codex、worktrees | worktrees 有用，但主線 git 仍打架 |
| L2 編排 | checkpoint.sh、patrol.sh（launchd 排程 = Routine） | patrol 每天「all clear」蓋章，**無獨立 grader**，停在「差不多」非「done」 |
| L3 記憶 | CURRENT_STATUS、recalls/、63 skills、decisions/pitfalls | **缺領域真相層**：SEO 57 篇無全貌 → 冷啟動重抓（文章第 11 步失敗） |
| L4 自我改進 | Section 16 三層審查、auto-skill-gen、weekly_eval | 驗證者「有文件沒真跑」：alt 兩式漂 5 檔、掛「待裁示」數週無人抓 |

## 三、四個結構根因

1. **迴圈沒閉合（L4 斷）**：git 時間戳衝突反覆失敗（log 一排 `merge: resolve ... timestamp conflict`），只做到「手動解」，從沒蒸餾成規則。
2. **自動化非冪等 → 負複利**：`checkpoint.sh` 在 push 後用 `date` 重寫 CURRENT_STATUS 時間戳卻不 commit，每跑一次留髒、且髒在 remote 也會改的那行；又不 pull-before-push，落後累積成 30 commit。
3. **人工閘門放錯位置**：0-byte stale `.git/index.lock` 卡死整條 commit、系統無法自癒（要 Owner 點權限）；反過來 `checkpoint.sh` 舊第 484 行 cherry-pick 衝突竟 `git checkout --theirs .` 盲解全掃（無聲丟工作）。該擋的自動盲解，該放行的被人工擋。
4. **記憶缺「領域」層**：recalls（角色）+ CURRENT_STATUS（全域）齊全，但 SEO/報價/廣告等領域真相無 canonical 層 → 每個 session 重推導（Owner 原話「沒有全貌 → 每次從頭抓」）。

## 四、本輪已落地（低風險、當場可自證）

| # | 補強 | 檔案 | 對應根因 | 驗證 |
|--:|---|---|---|---|
| 1 | 移除 checkpoint cherry-pick 盲解 `--theirs` → 衝突停手交人工 | `scripts/checkpoint.sh` | #3 | 已改，待 host 測 |
| 2 | checkpoint push 前 proactive merge（取代脆弱 rebase-on-fail） | `scripts/checkpoint.sh` | #2 | 已改，待 host 測 |
| 3 | **spec-drift 檢查器**（抓已廢止 alt/命名殘留在 live 檔），接進 checkpoint 非阻塞檢查 | `scripts/check_spec_drift.sh` | #1 #4 | 沙箱實跑 PASS |
| 4 | **patrol 獨立 grader**（衝突標記/未收尾 merge/落後/漂移/逾期 → PASS/FAIL） | `scripts/patrol_grader.sh` | #1 L4 | 沙箱實跑 PASS |
| 5 | alt 單一標準統一（5 檔）+ SEO canonical 關鍵字地圖 | 見 T-A2-* | #4 | 見 seo-keyword-map.md |
| 6 | 本稽核 doc（把教訓寫進 repo，不只留對話——文章核心紀律） | 本檔 | L4 | — |

## 五、待 host 測後才落地（高風險，寫成卡）

- **T-A1-GIT-SYNC-001**：timestamp 根治（方案 2：時間戳移出被 track 的檔 / checkpoint post-sync 自 commit 使冪等）。動到 12 agent 共用存檔流程，需 Mac mini 實跑驗證，不盲改。
- **T-A1-PATROL-GRADER-001**：把 `patrol_grader.sh` 接進 `patrol-scheduled.sh`，FAIL 時 Telegram 標紅、不再無腦「all clear」。

## 六、制度化規則（提案，納入治理）

**每個業務領域必須有一張 canonical「真相層」文件，列進該角色 recall 的「開工前必讀」。**
- 已有：SEO → `docs/seo-keyword-map.md`（A2_recall 必讀已加）。
- 待補：報價（A5/A6）、客服 FAQ（A7）、廣告投放（A3）各一張。
- 理由：讓文章第 11 步的「Consult 階段」真的發生——開場先讀真相層，而不是每次從頭推導退化成冷啟動。

## 七、一句話

自我改進是「系統」的屬性，不是「模型」的屬性。這輪把三個會複利的鉤子（spec-drift 檢查、patrol grader、領域真相層）裝上去；剩下兩個高風險根治走卡 + host 測。
