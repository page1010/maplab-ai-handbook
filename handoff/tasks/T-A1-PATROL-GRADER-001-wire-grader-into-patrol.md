# T-A1-PATROL-GRADER-001 — 把獨立 grader 接進每日巡查

建立：2026-07-23 ｜ 提案：A2 ｜ 負責：A1 ｜ 狀態：🟢 grader 已建待接線（host 測）

## 接續狀態
- **接續點**：`scripts/patrol_grader.sh` 已建並沙箱實跑 PASS（檢查：未解衝突標記、未收尾 merge/rebase/cherry-pick、落後 origin ≥10 升 FAIL、stale index.lock、spec-drift、逾期任務）。下一步：接進 `scripts/patrol-scheduled.sh`，讓每日巡查有客觀關卡。
- **阻塞**：需 Mac mini 實跑 + 確認 Telegram 輸出格式。

## 為什麼
patrol.sh 是任務卡狀態機，輸出「差不多了」的決策佇列，但不查 repo 健康 → 每天「all clear」是自我批評式蓋章（文章第 6 步：獨立驗證者勝過自我批評）。`patrol_grader.sh` 就是那個只看客觀產出物的獨立驗證者。這輪的 git 30-commit 落後 + 反覆時間戳衝突，patrol 從沒示警——正因為缺這關。

## 具體接線（建議 diff，待 host 測）
在 `scripts/patrol-scheduled.sh` 跑完 `patrol.sh` 取得 `$RESULT` 後，加一段 grader：

```bash
# 獨立 grader：客觀 repo 健康關卡
GRADER=$(bash "$REPO_ROOT/scripts/patrol_grader.sh" 2>&1) || GRADER_FAIL=1
MESSAGE="$HEADER

$RESULT

── repo 健康關卡 ──
$GRADER"
```

- grader exit 1（FAIL）時：Telegram 訊息開頭加 🔴 標記，確保 Owner 一定看到（不被「已完成 >5 張只顯示數字」吃掉）。
- grader exit 0 但含 WARN：正常推送，附 WARN 行。

## 驗收
- 故意留一個衝突標記/未收尾 merge → 巡查訊息出現 🔴 FAIL 且點名檔案。
- 乾淨狀態 → 🟢 PASS，不吵。

## 邊界
- grader 只讀不寫、不改 git 狀態、不 push。純關卡。
