# T-A2-005：MAPLAB SEO Factory（地端閉環，Pillar First）

---

## 接續狀態

> **Agent 冷啟動時第一個看的區塊。每次 checkpoint 必須更新。**

- **狀態**: ⏸️ 暫停 (blocked-on-owner: 等 Owner 提供 WordPress Application Password; 非當前優先, 2026-06-25 by A0)
- **最後活動**: 2026-05-04 local-seo-factory-initial
- **接續點**: 本地 SEO Factory 骨架已建（Planner→Auditor 七階段）、三大 Pillar dry-run 可產生 draft payload。下一步：接 WordPress 實站憑證做 `--publish` 驗證 + 把 56 篇歸屬表餵入 Linker。
- **阻塞**: 已有解法 — WP App Password 在 Notion 保管室, 依 skills/secrets-from-notion-vault.md runtime 取用建草稿(發布仍人工); 剩測試站檢核流程

---

## Meta
- **Task ID**: T-A2-005-local-seo-factory
- **任務名稱**: MAPLAB SEO 報告地端閉環落地（Pillar First）
- **負責 Agent**: A2（A1 治理支援）
- **建立日期**: 2026-05-04

## Goal（目標）
建立可每週批次執行的本地 SEO 內容工廠，不依賴雲端 Max，穩定輸出三大 Pillar 的 WordPress 草稿（draft only），並具備驗證、追溯與 cannibalization 候選報告能力。

## Preconditions（前置條件）
- [x] Ollama 本地服務可用（0.23.0，模型 `llama3.1:latest`）
- [x] 7 階段流程程式骨架完成
- [ ] WordPress REST 寫入帳號（Application Password）可用
- [ ] GSC/GA 匯出格式對齊 `post_signals` schema（供第二波合併判斷）

## Confirmed（已確認事項）
- 本任務採「草稿自動、發布人工」策略，不做 auto publish。
- 三大 Pillar 目標 URL 為：
  - `/catering-corporate-tainan/`
  - `/catering-birthday-party-tainan/`
  - `/catering-wedding-tainan/`
- 預設模型已改為本機存在的 `llama3.1:latest`，避免 fallback 空跑。

## Plan（本輪計畫）
1. 完成地端流程：Planner/Writer/Linker/Schema/Verifier/Publisher/Auditor。
2. 固化介面：`ContentBrief` / `DraftArtifact` / `PublishPayload` JSON schema。
3. 建立週批次入口與執行記錄。
4. 第二波接續：導入站內真實 signals 產生 cannibalization 候選 + 301 建議清單。

## Done（已完成）
- 新增 `automation/seo_factory/` 模組與執行說明。
- 新增 config/schemas/input sample。
- 完成 dry-run 驗證（3/3 pillars pass，score 100）。
- 新增執行紀錄：`automation/seo_factory/RUN_LOG_2026-05-04.md`。

## Next（下一步）
- 用真實 WordPress 憑證跑 `--publish`，驗證 draft 寫入 + Rank Math meta。
- 用真實 56+ 文章映射資料取代 sample signals，啟用 cluster 歸屬與候選合併報告。
- 補一份 `handoff/feedback` 給 A2/A3 說明如何把現有 SEO 內容流程接到此工廠。

## Blockers（阻塞點）
- 缺 WP 寫入憑證與 staging/prod 邊界確認（避免誤寫正式站）。

## Files Modified（修改的檔案）
- `automation/seo_factory/*`
- `.gitignore`
- `handoff/tasks/T-A2-005-local-seo-factory.md`
- `CURRENT_STATUS.md`
- `CHANGELOG.md`
- `projects/maplab-kitchen-web-optimization.md`

## Risks（風險/待確認）
- 若本機模型僅單一 8B，長文品質可能波動，需加強 Verifier + Human Review gate。
- 若 `post_signals` 沒有統一意圖鍵，第二波合併建議容易誤判。

---

## Checkpoints（每 30 分鐘至少更新一次）

### Checkpoint 1 — 2026-05-04 15:45
```
- Read: A1 recall / briefing protocol / repo sync rules / CURRENT_STATUS
- Changed: 建立 local SEO factory 模組 + schema + run log + A1治理同步檔
- Confirmed: ollama 0.23.0 + llama3.1:latest 可回應 generate API
- Next: 接 WP publish 真實驗證 + 導入真實 signals
- Blocker: 等 WP 憑證
```

---

## 接續 Prompt（結束 session 前必填）

```
你是 MAPLAB A2 SEO & Ads Team（A1治理協調模式）。
repo: https://github.com/page1010/maplab-ai-handbook
先讀 CURRENT_STATUS.md，再讀 handoff/tasks/T-A2-005-local-seo-factory.md。

上次做到：local SEO factory 已能 dry-run 產生三大 Pillar payload，驗證 3/3 pass。
下一步：帶入 WP 憑證跑 --publish，並替換真實 post signals 進行 cannibalization 候選分析。
Blocker：缺 WP 寫入憑證與測試站邊界確認。
踩過的坑：預設模型若設成不存在型號會 fallback 空跑，已改為 llama3.1:latest。

讀完文件後輸出 Startup Check。必拿：skills/task-progress-guide.md
```
