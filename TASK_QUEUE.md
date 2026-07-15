# TASK_QUEUE.md — 開放任務軌道（防吃案）

> 用途：每個開放迴圈都在這裡，有狀態+下一步+成果路徑。每階段結尾更新。對齊 Owner 治理偏好（PROJECT STATE UPDATE）。
> 最後更新：2026-07-10（A1 執行 A0 委派）

## 🔵 2026-07-10 A0 委派批次（Owner 已核，A1 執行）

| JOB ID | 工具 | 任務 | 輸出目錄 | 狀態 |
|---|---|---|---|---|
| JOB-CODEX-WEDDING-PILLAR-20260710 | Codex | 婚禮 pillar 終稿潤飾（brand-voice-guide 校訂） | `workbook/reviews/JOB-CODEX-WEDDING-PILLAR-20260710/` | ✅ 落檔 |
| JOB-CODEX-B3-ADCOPY-20260710 | Codex | B3 廣告素材文案初稿（Week1 corp, NT$100/日） | `workbook/reviews/JOB-CODEX-B3-ADCOPY-20260710/` | ✅ 落檔 |
| JOB-CODEX-CONTENT-AUDIT-20260710 | Codex | 57 篇舊文內鏈+語氣批量分析（唯讀） | `workbook/reviews/JOB-CODEX-CONTENT-AUDIT-20260710/` | ✅ 落檔 |
| JOB-AGY-SECOND-READ-20260710 | agy | SEO 矩陣覆核 + IS 優化方案二讀 | `workbook/reviews/JOB-AGY-SECOND-READ-20260710/` | ✅ 落檔 |

## 🔵 Codex 跑中（worktree 隔離，未 push，未碰 runtime/secrets）
| 任務 | worktree / 分支 | 輸出 | 驗收 |
|---|---|---|---|
| 6 項管線閉環修復 | `/tmp/ios_fix6_wt` `fix/pipeline-loop-closure-20260623` | `/tmp/ios_fix6_out.txt` | 4 測試檔 36 passed；19:50 排程做完整 diff 驗收 |
| 網紅源升級（RSS→全文、關死表） | `/tmp/wt_kol` `fix/kol-20260623` | `/tmp/kol_out.txt` | 待跑完→我驗 |
| 即時黑天鵝設計+scaffold | `/tmp/wt_blackswan` `fix/blackswan-20260623` | `/tmp/bs_out.txt` + `docs/blackswan-realtime-alert-design.md` | 待跑完→我驗 |
| LINE 訓練收尾 | 主庫 `workbook/a6-training/`（新增檔） | `/tmp/line_out.txt` | 待跑完→我驗 |

## 🟡 我（orchestrator）手上
- **A2 SEO 計畫驗收**：Codex 版品質OK（有 cannibalization map、誠實標 REST 待補）。**我要補的**：自己拉今天 WP REST 完整 posts/pages，填掉「REST 待補核」欄。檔：`docs/a2a3/a2-seo-plan-refresh-20260623.md`。
- **TASK_QUEUE 維護**：每階段結尾更新本檔。

## 👤 Owner 自己接
- 富途牛牛即時訊息 API（起點 script 已給）。

## ⏸ Owner 暫緩
- Notion 鑰匙搬遷（重授權 or 搬本機）。
- A2 個人品牌 B2B/B2C 策略（雜談）。

## ✅ 本階段已交付
- B2-B4 RSI 巡查報告（含給 B1 待辦）。
- Codex SSD bug 止血（CLI→0.142.0）。
- 眼見為憑：網紅源品質（逐字稿實/RSS淺/社群死）、LINE 訓練資產確認（2634 配對+SOP，commit 9889a00）。
