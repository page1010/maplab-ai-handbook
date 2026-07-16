<!-- receipt: TG-DISPATCH-20260714-CODEX-AGY-R04R05R10 / JOB-R04 / completed -->
# R04 — SEO 中斷診斷 + 重啟策略（A2）

> 執行者：A1（Codex null，A1 直接執行）  
> 完成日期：2026-07-16  
> 資料來源：T-A2-005, T-A2-SEO-CATERING-MATRIX-001, state/seo_loop_run.jsonl

---

## 1. Local SEO Factory（T-A2-005）目前卡在哪？

**最後成功步驟**：2026-05-04 完成 dry-run 驗證（3/3 Pillars pass, score 100）。

**卡點**：`--publish` 驗證流程無法啟動。

根因：
- WordPress REST API Application Password 未取得（`skills/credentials/wordpress-api.md` 有路徑但尚未設定帳密）
- 缺 staging/prod 邊界確認（避免誤寫正式站）
- 56 篇文章映射資料仍在 sample 狀態，尚未接入真實站內 signals

**影響範圍**：Planner → Writer → Linker → Schema → Verifier 五段已備妥；Publisher 段卡住後 Auditor 也無法執行。

---

## 2. SEO Catering Matrix（T-A2-SEO-CATERING-MATRIX-001）文章撰寫未開始的根因？

**接續點（2026-06-17）**：競品分析工作包已建立於 `workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/`，但 `claude_outputs/` 子目錄為空。

**根因**：
1. **工具鏈問題**：dispatch 工作包建好後，需要 Codex worker 消費；Hermes CLI = null，沒有 worker 去讀 `claude_task_prompt.md`。
2. **等待確認**：任務卡標示同樣的 WP 憑證阻塞，被誤以為需要先解 WP 問題才能動（實際上草稿撰寫不需 WP 憑證）。
3. **無明確的「唯讀分析」入口**：claude_task_prompt.md 已準備好，但沒有觸發機制。

---

## 3. seo_loop_run.jsonl 最後一筆狀態

**最後有效執行**：2026-07-01T18:00 — `status: "all_gaps_drafted"`

**錯誤紀錄**（2026-07-01 兩筆）：
- `GAP-1`（飯店會議茶點案例）：`draft_runner FAILED — draft_path missing`
- `GAP-3`（HR/行政 B2B buyer guide）：`draft_runner FAILED — draft_path missing`
- `GAP-5`（一口點心企業通用菜單）：`draft_runner FAILED — draft_path missing`

**2026-07-02 至今（2026-07-15）**：每日自動跑，但 `steps: []` 空步驟、狀態 `"all_gaps_drafted"`。這表示 SEO loop 以為所有 GAP 都已草稿完成（狀態標記有誤），導致迴圈每天都直接結束不執行。

**真正問題**：`draft_path missing` 後系統沒有 fallback，卻把 GAP 標記為 `drafted`，導致後續每日迴圈誤判一切完成。

---

## 4. 三步重啟計畫

### Step 1（不需 Owner 授權）— 修 SEO loop 狀態誤判 + 補 draft_path

1. 讀 `automation/seo_factory/` 的 draft_runner 邏輯，找 `draft_path missing` 根源（可能是目錄未建或路徑變數未設）
2. 手動補建 `automation/seo_factory/drafts/` 目錄，確保 draft_runner 有地方寫入
3. 把 GAP-1/GAP-3/GAP-5 的 `drafted` 狀態清除，讓下次迴圈重新嘗試

### Step 2（不需 Owner 授權）— 用 Catering Matrix prompt 直接產草稿

`workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/claude_task_prompt.md` 已準備好，內含三篇文章 brief。

A1 可直接執行：讀 prompt → 產出 3 篇草稿到 `claude_outputs/`（純文字輸出，不需 WP 憑證）。

**預計輸出**：
- `draft_01_icc_tainan_expansion.md`
- `draft_02_tainan_corporate_catering_admin_guide.md`
- `draft_03_opening_tea_party.md`

### Step 3（需 Owner 授權）— 取得 WP Application Password

Owner 需登入 WordPress 後台 → 使用者設定 → 應用程式密碼 → 產生新密碼。

完成後更新 `skills/credentials/wordpress-api.md`，SEO Factory `--publish` 即可啟動。

---

## 阻塞彙整

| 阻塞項 | 能否自行解除 | 需要什麼 |
|--------|------------|---------|
| draft_path missing 根因修復 | ✅ A1 可做 | 讀 seo_factory/ 程式碼 |
| GAP 狀態清除重跑 | ✅ A1 可做 | 修改 jsonl 狀態 |
| Catering Matrix 3 篇草稿 | ✅ A1 可做 | 直接讀 prompt 執行 |
| WP Application Password | ❌ 需 Owner | Owner 後台操作 |
| Staging/prod 邊界確認 | ❌ 需 Owner | Owner 書面確認 |
