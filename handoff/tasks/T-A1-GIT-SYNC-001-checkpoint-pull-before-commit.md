# T-A1-GIT-SYNC-001 — checkpoint.sh 提交前先 pull（根治 CURRENT_STATUS 時間戳復發衝突）

建立：2026-07-23 ｜ 提案：A2 ｜ 負責：A1 governance ｜ 狀態：🟡 PROPOSED（待 A1 採納）

## 接續狀態
- **接續點**：A2 本輪 commit 時撞到 `CURRENT_STATUS.md` unmerged 衝突 + 本地 main 落後 remote ~15 個 patrol commit。衝突內容只是「最後更新」時間戳一行（07-20 upstream vs 07-19 stashed），已由 A2 手動解掉（留 07-20）。
- **下一步**：A1 決定是否採納下方根治方案，改 `scripts/checkpoint.sh`。

## 問題（根因）
git log 反覆出現 `merge: resolve CURRENT_STATUS.md timestamp conflict`——**同一個衝突每次同步都復發**。根因是兩條寫入路徑各自改 `CURRENT_STATUS.md` 的「最後更新」時間戳：
- Mac mini 本地 `checkpoint.sh`（各 agent 存檔時）
- remote 端 `patrol.sh`（A1 巡查）

兩邊各寫各的時間戳 → 每次 pull/merge 必在那一行衝突。加上本地 checkpoint 不先 pull，落後越積越多（本輪已 15 commit），把小衝突放大成「commit/push 全卡住」。這是**低槓桿重複人工**，每次都要有人手解。

## 方案（擇一，建議 1 為主、2 為輔）

### 方案 1（主）：checkpoint.sh 提交前先 pull
在 `scripts/checkpoint.sh` 的 `git add` 之前插入同步步驟：
```bash
git fetch origin
git pull --no-rebase --no-edit || { echo "⚠️ pull 有衝突，停下人工處理"; exit 1; }
```
讓本地永遠不落後、不累積 15 commit 落差。落差=0 時，時間戳衝突頂多一行、當場自動解或極小。

### 方案 2（輔，根除時間戳衝突本身）：時間戳不走一般 merge
`CURRENT_STATUS.md` 頂部「最後更新」時間戳改用 git merge driver「取較新值」，或乾脆把 volatile 時間戳移出被 track 的檔（放 `state/` 未 track 的 heartbeat）。這樣那一行永遠不再衝突。

`.gitattributes`：
```
CURRENT_STATUS.md merge=keep-newer-timestamp
```
配一支 merge driver 腳本，衝突時保留較新時間戳、其餘照常。

## 驗收
- 連續跑 3 次 `checkpoint.sh`（中間讓 remote 有新 patrol commit），不再出現 `CURRENT_STATUS.md` timestamp 衝突、不需人工解。
- 本地 main 不再累積 >2 commit 落後。

## 邊界
- 只改同步流程與時間戳處理，不改各 agent 的存檔語意。
- 方案 1 若 pull 撞到**非時間戳**的真實內容衝突，要停下人工處理，不可 `-X ours/theirs` 盲解全掃。

## 本輪殘留（A2 待收尾）
- A2 的 `docs/seo-keyword-map.md` §9 封存觀察區 + `CURRENT_STATUS.md` 時間戳解衝突，尚未 push 到 remote（本地落後、runtime tree 髒）。建議由 A1 下次 patrol/checkpoint 的 pull→merge→push 一併帶上，或人工 `git pull --no-rebase` 後 push。
