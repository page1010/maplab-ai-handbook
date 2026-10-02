# MAPLAB 餐檯紙娃娃系統進度稽核

- 時間：2026-10-02 22:47 Asia/Taipei
- 稽核角色：Codex project archaeology / governance auditor
- 判定：`AMBER — 前置資料與規則引擎存在；互動紙娃娃前端未實作；正式派工未 ACK`
- 對應任務：`T-A4-PRELAYOUT-SIMULATOR-001` / `MAPLAB-TABLETOP-SIMULATOR`

## What

### VERIFIED — 誰提出、誰做過

1. **Owner 是需求來源。** 2026-09-18 的 A4 Task Card 記錄本需求起於 Codex thread；2026-09-30 Owner 再明確要求把「模擬排列出餐器具的紙娃娃系統」寫入 Codex 交接。
2. **Codex 做了第一段 A4 資料與控制層工作。** 初始 commit `8e971af` 建立 Task Card、第一批照片／報價候選關聯、collection report 與 receipt；Git 以本機帳號 `page <pagewu1010@gmail.com>` 提交，故 Git 作者只能證明帳號，不能單獨證明 agent 身分。Task Card 內文才是「本 Codex thread」的 agent 歸屬證據。
3. **Fable5 做了後續資料蒐集與辨識路線。** Task Card 明載兩批備份抽查、Drive training 素材列冊、OpenRouter 視覺煙霧測試與尺寸來源方案由 Fable5 代跑；其意見是照片不是主要瓶頸，器具尺寸／庫存才是。
4. **Antigravity 在 2026-09-30 把概念整理成產品規格並正式派給 Codex。** 派工卡標示 `dispatcher=Antigravity`、`next_owner=Codex`；規格書標示「Antigravity 整理歸檔」；agent-bus commit `c30ae345` 是其已派工的可追溯提交。
5. **預定實作者是 Codex / Web Engineering。** 但派工卡仍為 `DISPATCHED_AWAITING_ACK`，底部「Codex 回執」為空。近期 Codex 任務清單中只看到原始 A4 來源 thread 為 idle，未看到獨立紙娃娃實作 task；Hermes kanban 也只有 A8-FITNESS，沒有此案。

### VERIFIED — 現有成果

- 第一批私有資料包：12 張主要照片副本與 hash 驗證、4 份報價 readback、44 個「視覺標籤」候選。
- 目前仍是 **0 個已量測／可保證 fit 的器具品項**；照片與報價僅是候選關聯。
- 已有 collection report、索引搜尋、共享庫存／跨場次 checker；2026-10-02 重跑三組 unittest，共 **31 tests PASS**。
- checker 涵蓋共享庫存、既有預約、維修／損壞、清洗與運輸 buffer、早晚場重用、重複計數與缺資料 fail-closed。
- 已有 Phase 1–3 產品規格草案：180/240cm 桌型、Canvas/SVG、器具拖放、容量摘要、PNG/PDF 與 LINE/Google 串接方向。

### VERIFIED — 尚未完成

- Task Card 與 receipt 的正式狀態仍是 `FIRST_BATCH_VERIFIED / COLLECTION_INCOMPLETE / SIMULATOR_NOT_IMPLEMENTED`。
- 未找到 HTML/React/Vue/Canvas 紙娃娃畫面、可操作 runtime URL、螢幕截圖或使用者驗收。
- 尚無拖拉、旋轉、刪除、碰撞／邊界、圖層、PNG/PDF 匯出、LINE/Google 串接的實作證據。
- 9/30 規格書、multi-event contract/checker 與其部分測試目前仍是 Git untracked；可執行不等於已正式交付。
- 規格草案中的 `width_cm=35`、`serving_pax_est=15` 是示例值；真實 catalog 仍為 null／未量測，不可把示例當庫存事實。

## So What

這個案子不是「完全沒做」，但也不能說「紙娃娃系統已經在開發完成」。目前做成的是兩個底座：

1. 資料／證據底座：照片、報價候選、器具標籤、量測缺口與來源邊界。
2. 規則底座：共享庫存和跨場次可用性的 fail-closed 檢核器。

真正讓人能在桌面上拖器具的產品層仍是 **0 個可驗收畫面**。最大管理缺口不是技術錯誤，而是 9/30 的正式派工沒有 ACK、規格與 checker 尚未納入乾淨的版本控制，因此責任停在「Antigravity 已派、Codex 未正式接」的交界。

### INFERENCE — 里程碑成熟度

- 研究／資料管線：已具雛形，但 inventory truth 未完成。
- 規則引擎：原型可跑，31 tests PASS，但尚未納版與接 UI。
- 紙娃娃前端：未開始或至少沒有任何可驗收證據。
- 預約／LINE／PDF 整合：未開始。
- 若以「可讓人拖拉並輸出一張提案圖」為 MVP 定義，整體仍在 **前置 25–35%**；這是里程碑推估，不是工時量測。

## Now What

唯一 bounded next action：由 Codex / Web Engineering 先在派工卡補 ACK，將現有規格與 checker 納入版本控制，然後做一頁本機 Phase 1 demo：

- 180cm / 240cm 桌型切換；
- 8 個 placeholder 器具；
- drag / rotate / delete / layer / boundary；
- 摘要清單與 PNG 匯出；
- 所有容量、建議人數與 fit 先標 `示意／未經實測`。

完成門檻不是「程式檔存在」，而是保留一個可重跑 URL、測試結果、桌面與手機截圖，以及 Owner 可目視驗收的 receipt。

## Alignment audit

- 現行 `CURRENT_STATUS.md` 的主線是 A6；紙娃娃僅列為 A4 parallel task，沒有被提升為 active task。
- 正式 dispatch、Task Card 與規格書在目標上對齊，但狀態不同步：dispatch 等 ACK，Task Card 仍標 simulator not implemented，spec 本身未追蹤。
- Hermes patrol 會因 Task Card 把 A4 顯示為 `IN_PROGRESS`，但這只是索引狀態；未找到 Hermes 接手或完成本案的證據。不要把先前「交辦 Hermes」的 A8 fitness 任務誤認為紙娃娃案。

## Evidence

- `handoff/tasks/T-A4-PRELAYOUT-SIMULATOR-001.md`
- `reviews/PRELAYOUT-20260918/receipt.md`
- `projects/catering-tabletop-paperdoll-spec.md`
- `/Users/pagemacmini/claude-daily-operations/state/DISPATCH_CODEX_20260930_catering_tabletop_paperdoll_simulator.md`
- `/Users/pagemacmini/agent-bus/outbox/antigravity/antigravity-zhuazhou-video-and-codex-paperdoll-20260930.md`
- Test command: `python3 -m unittest tests.test_prelayout_collection_report tests.test_prelayout_index_search tests.test_prelayout_multievent_check -v` → `Ran 31 tests ... OK`

## Resume Prompt

你是 Codex / Web Engineering，環境為 `/Users/pagemacmini/maplab-ai-handbook`。先讀 `AGENT_CORE.md`、`CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A4-PRELAYOUT-SIMULATOR-001.md`、本稽核、9/30 dispatch 與 paperdoll spec。不要重做照片蒐集，也不要把照片比例推成真實尺寸。先補 dispatch ACK，再確認 untracked 規格與 checker 的來源，跑 31 tests，最後只做一頁可操作的視覺 prototype。容量與人數一律保留 `示意／未實測`，直到至少一批器具有可回查尺寸和現有庫存。交付必須包含 runtime、桌面／手機截圖、測試與 receipt。
