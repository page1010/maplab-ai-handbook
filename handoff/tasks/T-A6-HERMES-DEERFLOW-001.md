# T-A6-HERMES-DEERFLOW-001 — Hermes 自動研究與持久續跑

## 接續狀態

- **狀態**: IMPLEMENTED / LINE_METHOD_REDESIGN_REQUIRED
- **最後活動**: 2026-08-28 Codex A1/A6 plateau correction
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

1. 我是 A1/A6 Hermes durable-job integration engineer，環境是 `/Users/pagemacmini/maplab-ai-handbook`。
2. 先讀 `CURRENT_STATUS.md`、`pitfalls.md`、本卡與 `.agents/skills/maplab-durable-job-orchestrator/SKILL.md`。
3. 執行層已在 commit `2a5b361e3c09b170ef33b50ee78fd60ced6c3a9f` 落地。
4. 狀態／pitfalls／receipt 已在 commit `c60cad82f78f87bbdf671ae7daf3aeff2c9e78fa` 落地。
5. 完整證據入口是 `workbook/reviews/JOB-A6-HERMES-DEERFLOW-DURABLE-20260827/validation_receipt.md`。
6. Owner 只需描述成果；工具與 provider 由系統判斷，不可要求 Owner 背命令。
7. `/research-public` 只留診斷 override，不是正常使用入口。
8. 多來源 public/synthetic research 才可自動路由 hardened DeerFlow。
9. A8 私有素材與 LINE corpus 必須由本機 domain worker 處理。
10. DeerFlow/OpenRouter 不得看到 raw LINE、客資、私有媒體、cookie、secret 或登入態。
11. Canonical jobs 位於 `workbook/reviews/MAPLAB-DURABLE-JOBS/`，檔案 owner-only 且 runtime 內容不進 git。
12. `MAPLAB durable job continuation` heartbeat 每 30 分鐘只做一個 idempotent bounded action。
13. 目前 LINE job 是 `MAPJOB-20260827-224251-d291ad`。
14. 該 job 現為 `RUNNING / method-redesign-rubric-calibration`；LINE-specific active pointer 以 `T-A6-HERMES-LINE-GYM-001.md` 為準。
15. 已完成 12 rounds／60 local calls、總 pass 10/60、success streak 0；不可降低門檻、重播 receipt 或只換 seed 繼續跑。
16. 固定20案與40個two-shot cases已由v7零模型audit凍結；02:20 launchd side door已封且zero-call kickstart通過。下一步只做rubric v2零模型校正到至少18/20；E1 prompts尚未render、shared inputs／lesson snapshot尚未pin，不得先跑。
17. LINE data root 固定 `/Users/pagemacmini/.maplab/a6-hermes-training`；目錄 0700、語料檔 0600。
18. LINE child 只能呼叫 `127.0.0.1:11434/api/generate`，receipt 必須保持 external network calls 0。
19. `com.maplab.a6bot` 已重載並為 running，帶入 local-only provider 與安全 data root。
20. `com.maplab.hermes-line-training` canonical／mirror／installed均為supervisor-only；本次plain kickstart live runs 0→1、exit 0、reason=`canonical_execution_disabled`，job／round／call／attempt／run／lesson零delta。
21. Batch 5 僅 1/5 pass 且 1 個 unsupported price；服務健康不等於品質達標。
22. DeerFlow live proof 是 `MAPJOB-20260827-221144-64831c`／`DFR-20260827-221144-b2879c`。
23. DeerFlow checkout 必須維持 commit `788a890bd022689ef293e6bbfa2c12988173db6c`。
24. OpenRouter provider 仍 disabled，直到 authenticated privacy-policy readback 與 Owner spend approval 都存在。
25. 完成必須有 artifact/live readback、receipt 與 Owner surface；API 200、process exit 或 worker chat 不算。
26. A8 私人／unlisted upload 可承接 Owner 已明說的授權；公開發布、新花費與新第三方 egress 仍是 gate。
27. LINE offline training 永遠不授權 customer send；任何 send route 都必須保持 false。
28. 2026-08-28 schedule-gate／plateau／data-root／method-audit／hardening focused suite 75/75 PASS；重改 supervisor 必須包含 plateau zero-call、missing-latch poison與attempt>0 receipt-bound data-root regressions。
29. 只 stage 本卡相關檔案；保留既有 unrelated dirty runtime/A8/workbook 變更。
30. 每次 bounded action 後更新 job、validation receipt、`CURRENT_STATUS.md`、必要的 `pitfalls.md`，並留下新的 Resume Prompt。

## 2026-08-28 方法校正

前 12 rounds 並非權重訓練或穩定 retrieval learning，而是 random two-shot＋latest lesson 的不可比較推論。60 題全部不同，沒有固定 canary；50/60 fail，且主要失敗桶是過長。Supervisor 已在 commit `86c1cf1` 加入兩輪 plateau 熔斷與 receipt-derived private data root；真實無參數 resume 保持 round 12、attempt 6、loopback calls 60。方法回推與 E1 契約見 `workbook/reviews/JOB-A6-LINE-PLATEAU-MARGIN-20260828/first_principles_review.md`。
