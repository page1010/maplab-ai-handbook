# T-A1-V7: 系統進化 — 單一真相源 + 自動同步 + 瘦身 + 自動技能生成 + 自動壓縮

## 接續狀態
- **狀態**: 🔄 進行中
- **最後活動**: 2026-04-19 08170b7
- **接續點**: Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Phase 5（自動壓縮 ReMe）為加分項。
- **阻塞**: 無
- **已完成修復項**: A0 TASK_QUEUE 死連結 ✅、A6 重複 recall 刪除 ✅、bot log 180MB 輪轉 ✅、Extension 🔴 CRITICAL 顯示 ✅、patrol/Extension 邏輯統一 ✅、git-pull launchd exit 78 ✅

## 背景
Owner 反映：226 個 .md 檔沒人讀、Agent reset 後不了解就動手產出亂七八糟、同一資訊散落 3-4 處且多數過時。

借鑒 Hermes Agent（自動技能生成）、MemPalace（記憶宮殿）、ReMe（自動壓縮）三個開源專案，但不照搬——我們的系統連動性高（報價↔Slide↔品項↔LINE助手），agent 不知道自己該搜什麼，所以「按需搜尋」不適用，必須保留預讀但確保預讀內容 100% 正確。

核心原則：
1. **單一真相源** — 每個資訊只存一處，其他放連結
2. **自動生成取代手動維護** — checkpoint/patrol 自動更新，不靠 agent 自律
3. **兩個入口同一真相** — Claude Code terminal 和 Extension 都從 Task Card 同步

## 新發現（系統盤點後）
- A0 recall 引用已廢棄的 TASK_QUEUE
- A6 有重複 recall（A6_recall.md + A6_recall_compact.md）
- Extension parseStatus() 不區分 🔴 CRITICAL
- Extension detectOverdueTasks() 和 patrol.sh 邏輯重複
- git-pull launchd exit 78（本機可能落後 GitHub）
- bot logs 佔 180MB（bot.log 58MB + launchd_stdout 60MB + bot_a6.log 36MB）
- recalls/ 多個角色仍有過時的任務清單和斷點

---

## Phase 1：建立新的真相結構

| # | 任務 | 產出 |
|---|------|------|
| 1-1 | 建 `decisions.md` — 從 recalls/pitfalls/Task Card 提取「為什麼不用 X」的決策記錄 | decisions.md |
| 1-2 | 建 `dependency-map.md` — 從 8 個 recall 提取連動描述合併成統一視圖 | dependency-map.md |
| 1-3 | 加厚 Task Card 現況區（每張進行中的補齊：現在到哪、下一步、卡在哪、關鍵決策） | handoff/tasks/T-*.md |

## Phase 2：自動同步機制

| # | 任務 | 產出 |
|---|------|------|
| 2-1 | checkpoint.sh → 自動更新 recalls/ 現況區（從 Task Card 抽取寫入對應 recall） | checkpoint.sh 改版 |
| 2-2 | checkpoint.sh → 自動更新 CURRENT_STATUS.md（patrol.sh 輸出覆寫，遵守 parseStatus() 格式契約） | checkpoint.sh + patrol.sh 改版 |
| 2-3 | checkpoint.sh → 決策提示（commit 後問「有值得記錄的決策嗎？」→ 追加 decisions.md） | checkpoint.sh 改版 |

## Phase 3：瘦身 + 載入優化

| # | 任務 | 產出 |
|---|------|------|
| 3-1 | recalls/ 精簡 — 刪過時斷點，改成：角色定義（靜態）+ 現況（自動同步區）+ 連動提醒 | recalls/*.md |
| 3-2 | 舊檔歸檔 — telegram-logs、session logs、feedback → archive/raw/，摘要留 archive/digest.md | archive/ |
| 3-3 | 改 CLAUDE.md 啟動流程 — 8 個必讀 → Task Card + decisions.md + dependency-map.md + 按需搜尋 | CLAUDE.md |
| 3-4 | CLAUDE.md 技能索引化 — skills/ 不預讀，列名稱+觸發條件，agent 判斷需要才讀 | CLAUDE.md |

## Phase 4：自動技能生成（Hermes 借鑒）

| # | 任務 | 產出 |
|---|------|------|
| 4-1 | checkpoint.sh 自動判斷「這次解決了非顯而易見的問題嗎？」→ 自動產出技能檔到 skills/auto/ | checkpoint.sh + skills/auto/ |

## Phase 5：自動壓縮（ReMe 借鑒）

| # | 任務 | 產出 |
|---|------|------|
| 5-1 | 定期壓縮 hook — 14天以上 logs/sessions 壓縮成摘要行 → archive/digest.md，原檔移 archive/raw/ | launchd 或併入 patrol |

## 順手修復項

| 項目 | 處置 |
|------|------|
| A0 recall 的 TASK_QUEUE 引用 | 改成指向 Task Card |
| A6_recall_compact.md | 刪除（沒人用的重複檔） |
| Extension parseStatus() 加 🔴 CRITICAL 分類 | 改 popup.js |
| 統一 Extension detectOverdueTasks() 和 patrol.sh 邏輯 | 擇一為主 |
| 修復 git-pull launchd exit 78 | 排查原因 |
| bot log 輪轉 | 加 logrotate 或 launchd hook |

## 預期效果

| 指標 | 現在 | 完成後 |
|------|------|--------|
| Agent 冷啟動讀取 | 8 檔 ~2000 行，3 個過時 | 3 檔 ~200 行，0 個過時 |
| Extension agent 現況準確度 | 手動更新，經常落後 | checkpoint 自動同步 |
| 活躍 .md 檔數 | 226 | 目標 ~80 |
| 決策記錄 | 散落或遺失 | 統一 decisions.md |
| 踩坑經驗 | 人工維護 pitfalls | 自動生成 + 人工並行 |
| 連動可見性 | agent 自己猜 | dependency-map.md |

## 備註
- 順序 1→2→3→4→5，每 Phase 完成存檔驗證再推進
- Phase 1+2 是基礎設施，3 才能安全瘦身，4+5 是加分項
- Extension 的 parseStatus() 格式是 API 契約，任何自動生成必須遵守
