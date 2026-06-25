# MAPLAB A2 / A3 / A4 巡查報告

- 日期：2026-06-24
- 執行：A1 巡查協調（單 session 依序帶出 A2 / A3 / A4）
- 方式：read-only，不做重型 build，不修改未列入範圍的檔案
- RAM 限制：不另開 agent，節省 RAM（Claude app 已吃 ~20GB）

---

## 系統紅燈前置（全局確認）

| 紅燈 | 說明 |
|------|------|
| ⛔ 磁碟 ENOSPC | `mkdir` 失敗，session 目錄無法建立；另一 session 正在清理，巡查期間 Bash 有失敗風險 |
| 🔴 CURRENT_STATUS.md 嚴重過時 | 最後更新 2026-06-22；分支 `a8/video-checklist-mvp` 06-23/06-24 共 9+ 筆 commit 未反映（含 T-HQ-001 P5/P6 今日完成） |
| 🔴 branch 未合入 main | `a8/video-checklist-mvp` 堆積跨任務 commit（A5-002、A5-005、governance、T-HQ-001）未 push 至 origin/main |
| 🔴 前次 supervision resume session 無交接 | 修改了 hermes 相關檔案（hermes_status.js/json、patrol/latest.*、reaction_ledger_summary.md）但全部 unstaged，無 checkpoint |

---

## A2 — 搜尋流量作戰部 巡查

### 今日實際工作狀態

A2 本週在目前 branch 上有兩份新產出（均未 commit）：

| 檔案 | 日期 | 狀態 |
|------|------|------|
| `docs/a2a3/a2-seo-plan-refresh-20260623.md` | 06-23 | untracked，approval-ready 草稿 |
| `docs/a2a3/a2-rest-inventory-20260624.md` | 06-24 | untracked，public REST 盤點 |

**REST 盤點結果（06-24 今日）：**
- WordPress：58 posts / 6 pages，與 5/24 audit 基本一致（+1 post = icc-tainan-catering 06-16 發布）
- `icc-tainan-catering`（post 1829）已 publish，但 **不在 post-sitemap.xml 內** → 索引登記 drift，Search Console 可能看不到此頁

### 發現的紅燈 / 風險

| 項目 | 嚴重度 | 說明 |
|------|--------|------|
| `icc-tainan-catering` 未進 sitemap | 🔴 | post 1829 已 publish，但 `post-sitemap.xml` 找不到此 slug；可能是 Rank Math sitemap 快取未刷新或 post type 除外設定 |
| `corporate-catering-tainan` 殘字 `f` | 🟡 | 前台可見殘字，A2 SEO plan refresh 已標記 |
| `corporate-catering-tainan` 促銷語氣 | 🟡 | 「優惠/折扣」文字違反品牌語氣規則，A2 已標記但未修 |
| T-A2-002 封鎖 ~77 天 | 🟡 | 食安字眼清理，5 篇文章 WordPress 後台需 Owner 手動處理 |
| T-A2-005 CRITICAL ~912h 無 commit | 🔴 | Local SEO Factory 骨架建立後完全停滯 |
| T-A2A3-001-B CRITICAL ~360h 無 commit | 🔴 | WordPress 草稿 post 1696 建立後，圖片未插入，依賴 Chrome file URL access |
| T-A2-003 / T-A2-004 待開始 | 🟡 | 兩任務零進度，無排程 |
| `T-A2-SEO-CATERING-MATRIX-001` 狀態未標記 | 🟡 | Hermes patrol 標 `❓`，無法自動巡查 |

### 半成品 / 不完整交接

- A2 recall 的 `AUTO-SYNC` 停在 2026-04-15，**已超過兩個月未更新**；A2 的實際任務狀態與 recall 檔嚴重脫節
- `a2-seo-plan-refresh-20260623.md` 和 `a2-rest-inventory-20260624.md` 未 commit，下一個 A2 session 找不到

### 建議下一步

| 項目 | 動作 | 負責 |
|------|------|------|
| `icc-tainan-catering` sitemap | 登入 Rank Math 手動 ping sitemap / Fetch as Google | **Owner 5 分鐘行動** |
| 兩份 A2 doc 補 commit | `git add docs/a2a3/ && checkpoint.sh "A2" "REST inventory + SEO plan refresh"` | A1 / A2 |
| recall AUTO-SYNC | checkpoint.sh 觸發自動更新，或手動補最新斷點 | A1 |
| T-A2-005 重新定性 | 任務超 912h 無進度 → 改標「⏸️ 暫停（等 WordPress credential 確認）」，不繼續標 CRITICAL | A1 |
| `corporate-catering-tainan` 文案清理 | 移除殘字 `f` + 改促銷語 → 需 Owner 批准後 execution mode | A2 → Owner approval |

---

## A3 — 社群與廣告成長部 巡查

### 今日實際工作狀態

A3 在 repo 內沒有任何活躍 commit；recall 的 AUTO-SYNC 停在 2026-04-15。

### 發現的紅燈 / 風險

| 項目 | 嚴重度 | 說明 |
|------|--------|------|
| T-A3-002 封鎖 ~87 天 | 🔴 | 慶生周歲派對受眾優化：嘉義加地區、冷受眾上線等，全部等 Owner 登入 Meta Ads Manager |
| 無任何活躍 A3 任務 | 🟡 | 除 T-A3-002 外，A3 沒有其他進行中任務 |
| Meta Ads 廣告狀態不明 | 🟡 | 上次盤點 05-26，現役廣告（`互動廣告組合 A/B`）近 4 週無任何巡查或回報 |
| recall AUTO-SYNC 2+ 月未更新 | 🟡 | 與 A2 同樣問題 |

### 半成品 / 不完整交接

- T-A3-002 受眾分析報告已完成（2026-03-29 693 筆 Orders 分析），但結論從未執行，文件只存在 task card，未有任何 approval card 提交給 Owner
- A3 沒有任何 approval-ready plan（per `projects/a2a3a4-approval-ready-automation.md` 要求，每次 patrol 要產 `owner_approval_card.md`）

### 建議下一步

| 項目 | 動作 | 負責 |
|------|------|------|
| Meta Ads 現況 read-only 巡查 | A3 用 Chrome 只讀確認現役廣告成效（不改任何設定） | A3 下次召喚時執行 |
| T-A3-002 approval card | 產出 `owner_approval_card.md`：嘉義地區加入 + 冷受眾上線的 why/what/effect/rollback/risk | A3 → Owner |
| 廣告週期確認 | Owner 確認目前 Meta 廣告週期（是否有在跑 + 預算消耗狀態） | **Owner** |

---

## A4 — 影像資產整理部 巡查

### 今日實際工作狀態

最後 commit 為 c2dc194 / 90fe31c（2026-06-11 15:19），**距今 ~310h / ~13 天**，遠超 48h 門檻。

### 發現的紅燈 / 風險

| 項目 | 嚴重度 | 說明 |
|------|--------|------|
| T-A4-001 S11(2024) Colab 斷線 | 🔴 | 10,050/12,213（82.2%），差 2,163 張；04-18 A0 重啟 Colab 後狀態不明，超 48h 門檻 ~310h |
| S13(2026) 未啟動 | 🔴 | ~4,424 張待跑，依賴 S11 完成，但 S11 已卡住 |
| T-A4-003 / T-A4-004 ~11 天無新 commit | 🟡 | photo-alt-pipeline 和 photo-classify 自 06-11 後靜止 |
| T-A4-002 狀態未標記 | 🟡 | Hermes patrol 標 `❓`，無法自動決策 |
| recall AUTO-SYNC 停在 04-15 | 🟡 | 顯示 S12(2025) 處於「進行中」，但實際 S12 早已 DONE（7,645 張，04-15） |
| Drive 磁碟 ~433GB 待釋出 | 🟡 | 等 T-A4-003 批次完成 → Owner 改串流設定，目前無法操作 |

### 半成品 / 不完整交接

- T-A4-001 task card 最後更新 2026-04-18（Checkpoint 9），記錄 S11 Colab 重啟「等 Google 憑證授權後自動開始」，但此後無任何紀錄確認是否真正繼續跑
- **Colab session 有極高機率已再次斷線**（04-18 重啟後 ~2,000h 未確認），實際 ASSET_LOG 內 2024 年行數可能仍停在 10,050
- A4 recall AUTO-SYNC 顯示 S12 進行中（2026-04-15 斷點），但 S12 是 DONE，表示 recall 有舊斷點誤導下一個 A4

### 建議下一步

| 項目 | 動作 | 負責 |
|------|------|------|
| Colab 狀態確認 | 開 `https://colab.research.google.com/drive/16Ff4LF9zchNJQZ7nT28EWBDiEChoJfjo?authuser=1`，查 S11 現在進度（ASSET_LOG COUNTIF）| **Owner Chrome 操作** |
| 若 S11 已完成 | TARGET_YEAR='2026'，執行 S13（~4,424 張） | A4 / Owner Chrome Colab |
| 若 S11 未完成 | 重新執行 S6-RESUME cell，觀察 15 分鐘確認繼續 | A4 / Owner Chrome Colab |
| recall 補正 | 更新 A4 recall 斷點（S12 DONE，S11 狀態未知）| A1 / A4 |

---

## 系統性問題：Owner 特別關心的兩項

### (a) Telegram 推播訊息格式不一致 / 有些只抓標題

**根因位置**：`/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/build_finance_morning_brief.py`

具體問題：

1. **地緣/油價和亞洲盤用 `title_only=True` 搜尋**（第 1704–1714 行）：
   ```python
   geo_items = matching_items(items, ..., title_only=True)
   asia_items = matching_items(items, ..., title_only=True)
   ```
   只比對標題，忽略 `original_summary` 和 themes → 文章即使有完整摘要也不被利用

2. **`evidence_lines` 只輸出 `source_name: title` 格式**（`source_tag()` 函數 1517–1523 行）：
   - Telegram 最後「證據入口」只貼 `source_name: headline` 一行，無摘要、無判讀
   - `BriefItem.summary_zh` 欄位已存在，但 `render_telegram_text` 完全不使用

3. **`sector_news_groups` 只輸出 `title\nurl`**（第 2140–2142 行）：
   ```python
   lines.append(f"   {item_idx}) {truncate_text(item.title, 54)}")
   lines.append(f"      {item.url}")
   ```
   即純 headline + 連結，無任何分析

**修復方向**：Owner 可交給 B1 修 `source_tag()` 改輸出 title + summary_zh 前 50 字；`sector_news_groups` 渲染時加摘要行。

---

### (b) 早晨晨報只貼連結、缺第二層思考

**根因位置**：同一檔案 `build_finance_morning_brief.py`

具體問題：

1. **`what_lines` 是模板字串，非派生分析**（第 1732–1753 行）：
   - 例如：`"AI/半導體今天只當第二層：要看 SOX、NVDA/AMD/MU/TSM 是否同向..."`
   - 這段文字無論 NVDA 今天跌 3% 還是漲 3%，只要 `semi_items` 非空就貼同一句模板 → 缺少「基於今日實際數字的推演」

2. **`summary_zh` 在 Telegram 中不出現**：
   - Markdown 報告第 1911 行有 `f"   - Summary: {item.summary_zh}"`
   - 但 `render_telegram_text` 的「外部 seed 只留查核入口」段（第 2112–2114 行）只輸出 `item.title_zh` + 固定說明，不帶 `summary_zh`

3. **`daily-telegram-workflow.md` 規定的「第二層產業推演」格式**（供需、規格、capex、ASP/毛利）在晨報中**沒有對應的產出模組** — 晨報只有「結論句」，無產業鏈拆解段落

**修復方向**：Owner 可交給 B1（或直接修改此腳本）：在 `what_lines` 中加入 `semi_items[0].summary_zh` 引用；或新增一個 `second_layer_block()` 函數，從 `semi_items` 的 `summary_zh` + 市場快照數字推出真正的供需/規格推演段落。

---

## 「上一輪 Maplab supervision resume 做到一半沒留交接」問題

根據 git status 和 log 重建狀態：

| 問題 | 說明 |
|------|------|
| 修改了 hermes 相關 6 個檔案但未 commit | `local-control-plane/hermes_status.js/json`、`workbook/hermes/patrol/latest.*`、`telegram_decision_card.md`、`reaction_ledger_summary.md` 全部 modified 但 unstaged |
| A2 兩份文件未追蹤 | `docs/a2a3/a2-seo-plan-refresh-20260623.md`（06-23）和 `a2-rest-inventory-20260624.md`（06-24）完成後未 commit |
| 3 份 hermes patrol history 未追蹤 | 20260621/20260622/20260623 patrol JSON 未 git add |
| branch `a8/video-checklist-mvp` 跨任務堆積 | 這個以 A8 命名的 branch 混入了 A5-002/A5-005 fix、governance、TASK_QUEUE.md、T-HQ-001 P5/P6，全部未合入 main |
| CURRENT_STATUS.md 未反映今日 T-HQ-001 P5/P6 完成 | 今日 23:07 commit `d7b236b`，但 CURRENT_STATUS 最後更新 2026-06-22 |

**建議**：Owner 下次開啟 Claude Code terminal 前，先確認要在哪個 branch 上跑；巡查協調本次拒絕替 supervision resume 補假交接紀錄 —— 那個 session 本身就沒有留下清楚的「我做到哪裡、下一步是什麼」的單一事實。

---

## 重複人工 / 沒被記錄的狀態 / 該升級成規則的地方

| 觀察 | 建議 |
|------|------|
| A2/A3/A4 recall AUTO-SYNC 全部停在 04-15（>70 天） | checkpoint.sh 應強制更新 recall AUTO-SYNC；目前只更新 CURRENT_STATUS，不更新 recall |
| Hermes patrol history JSON 每日生成但從未 commit | `scripts/checkpoint.sh` 中加入 `git add workbook/hermes/patrol/history/*.json` |
| A2 每次巡查結束都產 doc 但忘記 commit | 建議在 patrol prompt 結尾加：「巡查完成後必須 `checkpoint.sh 'A2' '...'` 存檔，不存檔不算完成」 |
| 跨任務 commit 累積在同一 branch | 治理規則已在 AGENT_RULES 中（一事一 session），但無機制阻止跨任務寫同 branch；建議 A1 巡查時如發現 branch 跨任務則提醒 merge |

---

## 總結

| 角色 | 最高紅燈 | 建議第一步 |
|------|---------|-----------|
| A2 | `icc-tainan-catering` 不在 sitemap（SEO 可見性風險）+ CURRENT_STATUS / recall 嚴重過時 | Owner ping sitemap；A1 commit A2 兩份 doc |
| A3 | T-A3-002 封鎖 ~87 天，無任何活躍任務 | A3 補 approval card；Owner 確認 Meta Ads 廣告週期 |
| A4 | S11 Colab 狀態未知 ~2,000h，S13 完全未啟動 | Owner Chrome 確認 Colab 現況 |
| 系統 | branch 未合 main + CURRENT_STATUS 未更新 + 磁碟滿 | 磁碟清理完成後：merge branch → 更新 CURRENT_STATUS → checkpoint |

**交給誰**：

- `Owner（5 分鐘行動）`：① sitemap ping（Rank Math）② Colab 確認 ③ Meta 廣告週期確認
- `A1`：CURRENT_STATUS 更新、branch merge、recall AUTO-SYNC 補正
- `B1`：morning brief 第二層修復（`build_finance_morning_brief.py` 兩個 patch）
- `A2/A3/A4`：依各自「建議下一步」表格執行
