# T-A6-HERMES-DEERFLOW-001 — Hermes 自動研究與持久續跑

## 接續狀態

- **狀態**: IMPLEMENTED / LINE_QUALIFICATION_RUNNING
- **最後活動**: 2026-08-27 Codex A1/A6 integration
- **任務**: Owner 只說成果目標；Hermes 自動判斷是否建立 durable job、使用 hardened DeerFlow 公開研究、呼叫本地 domain worker，並跨 session 續跑到可見成果或真正 Owner gate。
- **可逆性**: 可逆；不取代 Hermes 既有一般對話 provider chain，不新增公開 listener，不把 A8／LINE 私密 payload 交給 DeerFlow。
- **外部資料政策**: OpenRouter account-level ZDR/data-collection 尚無 authenticated readback；DeerFlow 模型路徑保持本機 Ollama。OpenRouter profile 保留 fail-closed，不執行 live inference。
- **Runtime truth**: pinned DeerFlow checkout `788a890bd022689ef293e6bbfa2c12988173db6c`；Ollama `gemma4:latest` live；`MAPLAB durable job continuation` heartbeat 每 30 分鐘接續非終止 job。

## 第一性原理 5 題（Owner 問「為什麼要自己打研究命令」後重跑）

1. **理想狀態**：Owner 說「A8 生歌＋影片＋上傳 YouTube 給我看」或「Hermes 用 LINE 對話多跑幾輪」後，系統自行選工具、建立 job、持續做與驗證，只有成果或真正決策 gate 才回來。
2. **現況與應然**：原設計把 `/research-public` 當主要入口，等於把工具選擇與續跑責任丟回 Owner；應改為自然語言 deterministic router，slash 只留診斷用途。
3. **真假限制**：DeerFlow 的 embedded agent、subagent 與 goal continuation 都不是無限 resume；真正恢復必須靠外部 durable job、idempotent bounded action、receipt 與 recurring convergence heartbeat。nginx／Docker 不是 embedded public-research worker 的必要條件。
4. **從頭設計**：Owner/group auth → current-message-only local classifier → private canonical job → DeerFlow public research 或 local A8/LINE worker → artifact/receipt → heartbeat poll/retry → Telegram terminal readback。DeerFlow 對私密流程只可見 sanitized metadata。
5. **實況驗證**：自然 A8／LINE／public research routing 與通知 tests 已通；DeerFlow live smoke 已實際建立 `MAPJOB-20260827-221144-64831c` 與 `DFR-20260827-221144-b2879c` 並完成。首次 smoke 抓到 upstream duplicate middleware，最終以 process-local unique-name compatibility 保留 RBAC 與 allowlist 兩道 fail-closed gate。LINE launchd batch 5 已 exit 0；品質僅 1/5 且 1 個 unsupported price，因此保持未達標並由 durable job `MAPJOB-20260827-224251-d291ad` 接續，不把 runtime 成功冒充品質完成。

## 本版範圍

- [x] 建立 hardened DeerFlow profile：memory、persistent checkpoint、file、bash、browser、MCP、scheduler、tracing、skills 關閉；model tools 為空，僅由 adapter 做一次 bounded public retrieval，再交本機模型綜整。
- [x] 安裝 DeerFlow 官方 Ollama adapter，以本機 `gemma4:latest` 跑 model reasoning。
- [x] worker 強制 `PYTHON_DOTENV_DISABLED=1`、task-local home、unique thread ID、config execution gate、固定 argv 與 process-group timeout。
- [x] 新增自然語言 durable router；A8、LINE 多輪與 deep public research 不需 slash。
- [x] 新增 repo Skill `maplab-durable-job-orchestrator`、job contract、owner-only atomic packet 與 terminal notification dedupe。
- [x] 建立 30 分鐘 Codex heartbeat；沒有 active job 時 no-op，有 job 時只做一個可驗證 bounded action。
- [x] 私密／客資／投資／secret／附件／history reference／本機路徑／私網 URL fail closed，拒絕時 network calls = 0。
- [x] LINE 真實 corpus 強制 local-only，完成多輪 supervisor、user-local cache、launchd 與 bounded live receipt；品質門檻仍由 canonical job 持續追蹤。
- [x] 完成 DeerFlow live smoke、59/59 focused tests、Hermes launchd restart/live status 與 validation receipt。
- [x] 更新 `CURRENT_STATUS.md`、`pitfalls.md`，task-scoped implementation commit `2a5b361e3c09b170ef33b50ee78fd60ced6c3a9f`。

## Stop rules

- OpenRouter policy 與 spend gate 未同時驗證前，OpenRouter DeerFlow job deterministic reject；不可因 free key 而繞過。
- LINE corpus 即使移除 sender name 仍屬 private；OpenRouter/DeerFlow network calls 必須為 0。
- A8 私有素材、瀏覽器登入態、cookies、task payload 與 LINE 文字不得存入 DeerFlow prompt/SQLite。
- 任一 config drift、pin drift、dotenv 隔離失效、固定 argv 漂移或 receipt 缺失時，停止 worker並留下 fail receipt。
- 不 stage 既有 unrelated dirty files；runtime job packets由 `.gitignore` 保護。

## Resume Prompt

我是 A1/A6 Hermes durable-job integration engineer，環境是 `/Users/pagemacmini/maplab-ai-handbook` 與 pinned DeerFlow checkout。
先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本卡、`.agents/skills/maplab-durable-job-orchestrator/SKILL.md` 與 user skill `deerflow-openrouter-research`。
Owner 只需描述成果，系統自行判斷工具；`/research-public` 只是診斷 override，不可再要求 Owner 背命令。
DeerFlow 只處理 public/synthetic research；A8／LINE payload 由 local domain worker處理，DeerFlow最多只看 opaque state/error/receipt metadata。
每個 job 都在 `workbook/reviews/MAPLAB-DURABLE-JOBS/` 留 owner-only canonical state；heartbeat 每次只做一個 idempotent bounded action。
完成必須有 artifact/live readback + receipt + Owner surface；process exit、worker chat 或 API 200 都不算。
OpenRouter ZDR/spend gate 未完成前保持 disabled；本機 Ollama 是目前 live provider。
先完成 LINE local-only supervisor與 launchd live smoke，再跑全套 tests、重啟 Hermes、更新 validation receipt與 status，只 stage本卡相關檔案並 commit。
