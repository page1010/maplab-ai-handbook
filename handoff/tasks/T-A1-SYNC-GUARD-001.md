# T-A1-SYNC-GUARD-001: 雲端同步破口修補 + patrol 紀錄瘦身

## 接續狀態
- **狀態**: 🔲 待開始
- **最後活動**: 2026-05-31
- **接續點**: 問題已實證（本地積壓 14 commits vs. launchd 推 5 commits → 分岔），修復方案已規劃，尚未執行。
- **阻塞**: 無（可自主執行）

- **負責**: A1
- **建立**: 2026-05-31（B1 召喚發現）
- **狀態**: 🔲 待開始（高槓桿、低成本，建議優先）
- **來源**: JOB-B1-CROSS-PROJECT-20260531；B1 推送治理草案時發現

---

## 問題（已實證）

2026-05-31 B1 推送時發現：本地 `main` 積壓 **14 個未推 commit**，而 launchd
`com.maplab.patrol` 持續從別處往 `origin/main` 推（5 個 patrol commit）→ 兩邊分岔，
直接 push 被拒。代表「雲端永遠最新」這條規則**有破口**：寫進來的東西不保證真的上雲。

`verify-commit-on-main.sh` 只檢查**本地** main，分岔時會誤報「✅ 已在 main」，
但其實沒推到 origin → 假綠燈。

## 根因

1. 一般 agent commit 後沒人保證 push origin；`git-pull.sh`（launchd 自動 pull）只拉不推，
   且這個 working copy 今天並沒有被它推上去。
2. patrol 從另一個入口（worktree？）推 origin，造成單向分岔。
3. `verify-commit-on-main.sh` 沒比對 origin/main，只比對本地 main。

## 要做（最小修補）

1. **`verify-commit-on-main.sh` 加 origin 檢查**：先 `git fetch`，比對 commit 是否在
   `origin/main`，不在就紅燈並提示 `git pull --rebase && git push`。
2. **`checkpoint.sh` 收尾自動呼叫 verify**：commit/push 後跑一次，讓「已上雲」變預設驗收。
3. **patrol 紀錄瘦身**：CURRENT_STATUS 的 Blockers 區段已塞數十條重複 patrol 紀錄，
   難讀。改為只保留最新一筆 + 一行歷史摘要，舊紀錄移 `archive/`。
4. （可選）統一推送入口：patrol 推 origin 前先 `pull --rebase`，避免再分岔。

## 驗收

- 任一 agent 跑 `checkpoint.sh` 後，能明確知道「是否已在 origin/main」，不再有假綠燈。
- CURRENT_STATUS Blockers 區段 < 一屏可讀。

## 禁止 / 邊界

- 不改 A6 bot 客戶流程。不動 launchd 憑證。瘦身時舊紀錄 archive 不刪除。
