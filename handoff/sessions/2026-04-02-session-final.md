# Session Notes — 2026-04-02 Final Handoff

---

## Session 2 Update — 2026-04-02 晚間

### 新完成
- MasterData 引用更新完成（13 檔案，commit d0466f3 on main）→ Owner 可安全刪除 MAPLAB_MasterData_Sheets
- K 欄清洗完成（cleanItemsImageUrl 已執行：22 有 URL / 92 空白 / 0 搬移）
- Code.gs v3.1 部署確認（Owner 已手動貼入，Code.gs 已刪除）
- extractSlidePhotosToItems 函數寫好但 Apps Script 存檔失敗（語法衝突）

### 卡住的事
- extractSlidePhotosToItems 無法在 Apps Script 編輯器正確儲存執行
- 需要換方式：用 Google Slides API + Sheets API 從 code task 直接執行

### Owner 重要回饋
1. 「不要老是叫我改程式碼，你自己解決」— AI 必須自主完成所有 Apps Script 操作
2. 「寫在召喚和人設 prompt，不是技能」— 操作流程寫進 AGENT_RECALL_PROMPTS
3. 「你是 Cowork，可以開 Chrome tab、Claude Code、很多功能」— 充分利用 Cowork 能力
4. 「造鏟子以後拿鏟子上工」— 建立可重複使用的標準流程

### 下一步（下個 session 立即做）
1. 用 Google API（不是 Apps Script 編輯器）執行 Slide 照片提取 → Items K 欄
2. 把「自主操作 Apps Script」流程寫進 AGENT_RECALL_PROMPTS
3. Items K 欄照片提取完成後，開始 createSlides.gs 開發

### Worktree commit 問題已修正
- 上一輪所有 worktree 分支的 commit 已 cherry-pick 到 main（c1d3126, d0466f3）
- 但新的 code task 仍會建新 worktree — 需要在每個 session 結尾確認 merge 到 main

---

> Context 即將耗盡，這是本輪最終 handoff。
> 下一個 AI 先讀這份文件 + 2026-04-02-session.md

---

## 本輪完成的事

### 報價系統 v3.1
- Code.gs v3.1 + QuoteForm v3.1 寫好，repo 已 commit
- ⚠️ **Apps Script 編輯器裡的程式碼還是舊版** — Monaco API 不會真正存檔
- Owner 需要手動複製貼上 Code.gs 和 QuoteForm.html 到 Apps Script 編輯器
- 檔案在 repo: scripts/apps-script/Code.gs + scripts/apps-script/QuoteForm.html
- 也產出了下載檔：mnt/outputs/quoteSystemV2_v3.1.gs

### 合約條款
- 三版完整條款收錄：data/contract-terms-v3.md
- Code.gs 已包含三版條款動態帶入邏輯（getTerms_toC / toBDeposit / toBFull）
- QuoteForm 有「收取訂金」checkbox

### Slide 動態連結（T-A5-004）
- 需求書已 commit：handoff/feedback/2026-04-02-slide-integration-requirements.md
- 確認文學館真實 Slide：16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo（23頁）
- Menu Showcase = 3x2 grid，每品項 = 照片 + 中英品名 + qty
- Slide 模板：1rRxwPK9Nsgb7oqoRiUOCFqu3iGNuw_zRKW3zeHbdHBY
- Items K 欄有 image_url（混用：WordPress .avif + Google Photos + 活動紀錄）

### 技能 / 系統建設
- clasp 部署防呆技能完善（含 Monaco API 不存檔的最大坑）
- session handoff 標準化（handoff/session-notes/）
- .clasp.json 永久 commit

---

## 未完成（下一個 session 接續）

### 高優先
1. **Code.gs v3.1 部署到 Apps Script** — Owner 需手動貼入 quoteSystemV2.gs + QuoteForm.html + 刪除 Code.gs
2. **測試新建報價單** — 確認 cell mapping 正確
3. **Items K 欄清洗** — 非 URL 搬到 J 欄，K 欄只放圖片 URL

### 中優先
4. **Drive 資料夾整合** — MAPLAB_報價單 搬到 MAPLAB_DATA 下（等 v3.1 部署確認後）
5. **createSlides.gs 開發** — Phase 3 of Slide integration
6. ~~**MAPLAB_MasterData_Sheets 退役**~~ ✅ 完成 — 已全面更新為 MAPLAB_外燴系統_v0.1（舊 ID: 1d2_SiEXh5JT4lzjkgHDI5JU9UWBY9TiPlC8DaxkQnKs）

### 低優先
7. worktree 清理（~160 個）
8. MAPLAB_Proposals / _MAPLAB_TEMP_IMAGES 資料夾整理

---

## 踩坑紀錄（本 session 最重要的教訓）

1. **Monaco API setValue 不會真正存檔** — 唯一可靠方式是 Owner 手動複製貼上
2. **clasp push 對 bound script 不可靠** — fallback 是瀏覽器直接操作
3. **clasp list 的 ID ≠ Sheet-bound 的 ID**
4. **函數名衝突** — Code.gs + quoteSystemV2.gs 同名函數
5. **DRIVE_ROOT_FOLDER 按名稱搜尋** — 改名/搬移會導致自動建新資料夾

---

## 關鍵 ID 索引

| 項目 | ID |
|------|-----|
| 外燴系統 Sheet | 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg |
| Bound Script ID | 1V7Ff8hezZNDliHTlHZejTqoiRmInoeYXW61CaZpnc0ac1Dnt3gfWMwvk |
| Slide 模板 | 1rRxwPK9Nsgb7oqoRiUOCFqu3iGNuw_zRKW3zeHbdHBY |
| 文學館 Slide | 16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo |
| MAPLAB_DATA | 19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt |
| 進行中_Active Orders | 1vCiqYelK0Z24vLthVib9qqzw6Bdj2o4_ |
| MAPLAB_ASSETS | 1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe |
| MAPLAB_外燴系統_v0.1 | 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg |（舊 MasterData_Sheets ID: 1d2_SiEXh5JT4lzjkgHDI5JU9UWBY9TiPlC8DaxkQnKs）
| WordPress | https://www.maplabkitchen.com/ |

## 接續 prompt

你是 MAPLAB Kitchen A0。先讀：
1. handoff/session-notes/2026-04-02-session-final.md（本文件）
2. handoff/feedback/2026-04-02-slide-integration-requirements.md
3. handoff/feedback/2026-04-02-quote-draft-v3-layout.md
4. skills/clasp-deploy-guide.md

當前任務：T-A5-004 Slide 動態連結。前置作業：Items K 欄清洗 + Code.gs v3.1 部署確認。
