# T-B1-DASH-001: Guild Ops Board 自動同步 + 即時狀態燈

- **負責**: B1 建造 / 可派 Codex 執行(repo owner)；A0 調度；B2 收驗
- **建立日期**: 2026-06-07
- **狀態**: 🟢 READY（已派工，等執行 + 進度檢查）
- **前置**: `workbook/dashboards/maplab-ops-game-dashboard.html` 已建並通過 B2(JOB-B1-BUILDER-20260607)

---

## 背景
Guild Ops Board 目前 `D[]` 為手抄 `New project/config/investment_os_role_registry.json`。B2 diff 證實 16 角色 jobs 0 漂移,唯一差異是 dashboard 標籤刻意中文化。為防未來雙真相漂移,需把資料層改為「從 registry 自動生成」,並把靜態狀態燈接到即時健康。

## 子任務

### #1 registry → dashboard 自動同步 generator（主，可派 Codex）
- 新增 `tools/ai_workbook/build_ops_board.py`：讀 `New project/config/investment_os_role_registry.json`(16 IOS 角色)+ 內嵌的 B1–B4/A0 定義 → 注入 HTML 的 `const D = [...]` 區段。
- 用 marker 注入：HTML 內以 `/*__D_START__*/ ... /*__D_END__*/` 包住 `D[]`，generator 只替換中間，**不動** CSS/JS/版面。
- 保留現有 persona / flow / ladder / crew（這些是人工策展，registry 沒有）→ generator 以 `role_id` 對應 overlay，registry 只覆寫 mission/jobs/dash/tg/esc，persona+flow+ladder+crew 從旁邊的 `tools/ai_workbook/ops_board_overlay.json` 帶。
- 驗收：跑 generator 後 `git diff` 只動 `D[]` 區段；`node --check` 抽 script 仍 OK；部門數仍 21。

### #2 即時狀態燈
- 卡片狀態(ok/warn/bad/idle)改由小 JSON `workbook/dashboards/ops_board_status.json` 餵；由 `system-patrol-hourly` 或一支 `tools/ai_workbook/probe_ops_status.py` 寫入(探 launchd job + 關鍵 port：18789 openclaw / 18501 streamlit / telegram_operator pid)。
- 離線無 JSON 時 → fallback 回靜態值並在 UI 標「示意」。維持 offline-ready 鐵則。

## 不可越界
- 不動 registry 本身；不改既有 runtime/腳本邏輯；不下單；不讀 secrets。
- generator 不可破壞 offline-ready：產出仍須單檔可開（status JSON 為選配增益）。

## 進度檢查點（供 A0/監督輪詢）
- [ ] `tools/ai_workbook/build_ops_board.py` 存在且可跑
- [ ] `tools/ai_workbook/ops_board_overlay.json` 存在（persona/flow/ladder/crew）
- [ ] 跑 generator → `git diff` 僅動 `D[]` marker 區段
- [ ] `node --check` 通過、部門數=21
- [ ] (選) `probe_ops_status.py` + `ops_board_status.json`

## 升級
資料對齊問題 → B2；要不要做即時狀態(避免過建)→ B4 判定；完成存檔 → B3。
