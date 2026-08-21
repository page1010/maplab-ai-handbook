# T-A4-004 — 照片分類搬移：截圖/家庭/外燴工作 + 年月資料夾

## 接續狀態
- **狀態**: 🔒 AUTO_CLOSED（2026-08-03，NEEDS_REVIEW 無回應逾 7 天，Owner 可回覆「重開 T-A4-004-photo-classify」重啟）
- **最後活動**: 2026-06-11
- **接續點**: 批次跑完後 `--status` 查進度，續開下一批直到 ~98,400 張完成
- **阻塞**: 無（每小時 launchd 排程被 auto-mode 擋，Owner 可選擇性啟用，見下）
- **assigned_session**: 2026-06-11 / B1
- **last_committed_by**: B1（本 commit）

建立：2026-06-11
依據：Owner「可以分類一下嗎 截圖 家庭 外燴工作 ＋年月份資料夾 然後已經有資料夾的不要動」

## 範圍

| 區域 | 處理 |
|------|------|
| `photos/Takeout/Google 相簿/20XX 年的相片`（~98,400 張） | ✅ 分類搬移 |
| `photos/_screenshots`（5GB） | ✅ 歸入 截圖/YYYY-MM |
| named albums（Delicious、map2019餐點、素材 開幕、樂享學…） | ⛔ 不動（已經有資料夾的） |
| `MAPLAB_ASSETS` | ⛔ 不動（T-A4-003 ALT 管線處理中） |
| 影片 | ⛔ 不動（模型只看圖） |

## 目標結構

`photos/分類/<截圖|家庭|外燴工作>/<YYYY-MM>/`

## 機制（scripts/a4_photo_classifier.py）

- 分類：檔名截圖快篩（免模型）→ gemma4 vision 三選一；模糊時偏判「家庭」（不會誤入商用素材）
- 日期：Takeout sidecar JSON → 檔名 13 位毫秒時間戳 → EXIF → 資料夾年份
- 安全：只 rename 不刪除；sidecar JSON 跟著搬；每筆記 `data/photo_classify.db`；`--undo` 全量還原
- 驗證（2026-06-11）：30 張實測，分類正確、月份正確（2014-05/2014-06）、還原機制可用

## Owner 可選

啟用每小時自動跑（與 ALT 管線同款排程）：
```
launchctl load ~/Library/LaunchAgents/com.maplab.a4-photo-classify.plist
```
（plist 已寫好在 LaunchAgents；不啟用也行，session 內背景批次照樣推進）

## 進度查詢

```
/usr/bin/python3 scripts/a4_photo_classifier.py --status
```

## Owner 優先序裁定（2026-06-11）

「我不會一直用也可以等報價」— 照片管線全速跑到完，不需為 A6 報價 / Hermes 讓出 gemma4。
之後的 session 不要再加節流／降速設計。
