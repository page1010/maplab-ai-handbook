# T-A1-GIT-SYNC-001 — checkpoint.sh 提交前先 pull（根治 CURRENT_STATUS 時間戳復發衝突）

建立：2026-07-23 ｜ 提案：A2 ｜ 負責：A1 governance ｜ 狀態：🟢 方案 1 已落檔（Owner 核准，待測）；方案 2 待做

## 執行紀錄（2026-07-23）
- **方案 1 已實作**：`scripts/checkpoint.sh` FAST_MODE 的 push 區塊（原 500–511 行）改為「push 前先 `git fetch` + `git merge --no-edit origin/main`」，移除原本失敗才 `pull --rebase` 的脆弱 fallback。merge 衝突一律 `exit 1` 停手交人工，不 `-X ours/theirs` 盲解。**待在 Mac mini 實跑驗證。**
- **根因補強（比原分析更深一層）**：`_sync_current_status()` 在 **push 之後**（第 526 行呼叫）用 `date` 重寫 CURRENT_STATUS.md 的「最後更新」時間戳，但**不 commit** → 每次 checkpoint 結束都把 working tree 留成「CURRENT_STATUS.md 已改未提交」，而且改的正是 remote patrol 也在改的那一行。這才是「時間戳衝突每次復發」的真正引擎，光靠方案 1 無法根除。
- **方案 2（必要，未做，較侵入待測）**：把 volatile 時間戳移出被 track 的 CURRENT_STATUS.md（例如寫進 `state/` 未 track 的 heartbeat 檔），或改 `_sync_current_status` 不再逐次重寫時間戳。做完才達成「零人工」驗收。⚠️ patrol.sh 也寫這行，改前要一起盤。

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

## 方案 2 具體實作（二選一，待 host 測）

**根因回顧**：`_sync_current_status()` 在 **push 之後**（checkpoint.sh 第 526 行呼叫）用 `date` 重寫時間戳＋重生任務表，但**不 commit** → 每次跑完 CURRENT_STATUS.md 都是「已改未提交」，且改在 remote patrol 也改的那行。

- **2A（最小、低風險）：checkpoint 停止重寫時間戳那一行。**
  刪掉 `_sync_current_status()` 內 awk 的 `/^最後更新：/ { ... next }` 區塊（第 233–237 行），讓 patrol.sh 當時間戳的唯一寫入者。checkpoint 不再與 patrol 爭那一行。
  - 副作用：checkpoint 後時間戳反映上次 patrol，而非 checkpoint（純顯示，可接受）。
  - 殘留：任務表仍會被重寫→tree 仍髒，但衝突頻率大降（表格列變動遠少於每次時間戳）。

- **2B（根治、較侵入）：讓 post-push sync 冪等。**
  在 FAST_MODE 尾端（`_sync_current_status` 之後）加一段：若 sync 造成變更，就自動再 commit+push 這批 housekeeping。
  ```bash
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "chore($ROLE): post-checkpoint sync (task table / recall / status)" || true
    git fetch origin 2>/dev/null
    git merge --no-edit origin/main || { echo "❌ housekeeping merge 衝突，人工處理"; exit 1; }
    git push origin main || echo "⚠️  housekeeping push 失敗，下輪補"
  fi
  ```
  - 效果：跑完 tree 乾淨 → 下一輪不繼承髒狀態 → 衝突趨近 0（真正冪等）。
  - 風險：多一次 commit+push 在存檔路徑，務必 host 實測（別在沒測過就上線給 12 個 agent 用）。

> 建議：先上 **2A**（幾乎零風險、當場砍掉爭用那一行）→ 觀察一週 → 再視情況上 **2B** 求完全冪等。

## 驗收
- 連續跑 3 次 `checkpoint.sh`（中間讓 remote 有新 patrol commit），不再出現 `CURRENT_STATUS.md` timestamp 衝突、不需人工解。
- 本地 main 不再累積 >2 commit 落後。
- `bash scripts/patrol_grader.sh` 回 🟢 PASS（無未解衝突、無失控落後）。

## 邊界
- 只改同步流程與時間戳處理，不改各 agent 的存檔語意。
- 方案 1 若 pull 撞到**非時間戳**的真實內容衝突，要停下人工處理，不可 `-X ours/theirs` 盲解全掃。

## 本輪殘留（A2 待收尾）
- A2 的 `docs/seo-keyword-map.md` §9 封存觀察區 + `CURRENT_STATUS.md` 時間戳解衝突，尚未 push 到 remote（本地落後、runtime tree 髒）。建議由 A1 下次 patrol/checkpoint 的 pull→merge→push 一併帶上，或人工 `git pull --no-rebase` 後 push。
