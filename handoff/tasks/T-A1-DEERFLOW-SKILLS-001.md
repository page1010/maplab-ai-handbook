# T-A1-DEERFLOW-SKILLS-001 — DeerFlow/OpenRouter + Screenshot Tool Skill Upgrade

## 接續狀態

- **狀態**: ✅ DONE（Skill／SOP 與安全 setup 層完成；DeerFlow service 未啟動）
- **最後活動**: 2026-08-27 Codex A1
- **接續點**: 若 Owner 要第一個 live smoke，先選 Docker 隔離路徑，或明確核准本機安裝 nginx；之後只用 public/synthetic fixture 跑 loopback smoke。
- **阻塞**: 不阻塞本卡完成。DeerFlow live smoke 尚缺 Docker 或 nginx；OpenRouter account-level ZDR/data-collection Guardrail 尚未做 authenticated readback。
- **assigned_session**: 2026-08-27 / Codex acting as A1 Skill/SOP Engineer
- **last_committed_by**: Codex（task-scoped checkpoint 待寫入 receipt）
- **可逆性**: 可逆。Skill、外接 checkout、CLI 與 config 可移除；沒有 production route、external send 或 live data migration。

## Owner 需求

評估 DeerFlow + OpenRouter 是否能推進系統，並把截圖中的 Anime.js、Cult UI、Lead follow-up、Playwright CLI、Supabase 依價值安裝或寫成 Skill 發到系統。

## 本版 v0.1 交付

- [x] 冷啟動、角色、CURRENT_STATUS、pitfalls、Task Card、skill lifecycle 與官方 docs 規則完成。
- [x] 確認 Hermes 已有 OpenRouter-first + local fallback，不重建 production provider chain。
- [x] DeerFlow source clone 到外接工作區並 pin reviewed commit `788a890bd022689ef293e6bbfa2c12988173db6c`。
- [x] `config.yaml` 啟用 OpenRouter env placeholder 與 live-verified model ID；沒有寫入或輸出 secret value。
- [x] DeerFlow backend diagnostic environment 建立；Doctor 已證明 config/key 名稱可載入，精確 blocker 為 nginx。
- [x] 新增 user Skill `deerflow-openrouter-research` 與離線 preflight helper。
- [x] 新增 repo Skill `maplab-lead-intake-followup`，引用既有 A7/A6/A5 canonical SOP，不另造 CRM。
- [x] 安裝 Playwright agent CLI 0.1.18 與官方 Agent Skill，完成 open/snapshot/close smoke。
- [x] Anime.js、Cult UI、Supabase 完成 install/defer 決策與安全邊界。
- [x] 兩個新 Skill validator PASS；skill discovery duplicates=0；Lead intake unittest 7/7 PASS。

## 工具決策

| 截圖項目 | 決策 | 原因 |
|---|---|---|
| Anime.js | 專案存在後安裝 | 是前端 dependency，不是全域系統工具；需 reduced-motion 與 cleanup。 |
| Cult UI Hero Color Panels | Portal React/TS/Tailwind 成形後逐元件導入 | 是 copy-source registry，不是 WordPress drop-in；shader/GPU 與內部控制面需另審。 |
| Lead follow-up | Repo Skill 已落地 | 既有十欄 intake/quote workflow 已存在，應建立 discovery wrapper 而非第二 CRM。 |
| Playwright CLI | 已安裝 | 補隔離、可重現的 snapshot/trace/test workflow；Owner logged-in UI 仍走 Browser/Chrome。 |
| Supabase | 延後 | 未來 portal 可用，但現在會形成第二 SSOT；先定 Auth/PII/RLS/backup/rollback。 |

## 驗收證據

- `workbook/reviews/JOB-A1-DEERFLOW-SKILL-UPGRADE-20260827/validation_receipt.md`
- `/Volumes/MacExternal/MAPLAB_WORKSPACE/outputs/2026-08-27_deerflow-openrouter-upgrade/README.md`
- `/Volumes/MacExternal/MAPLAB_WORKSPACE/outputs/2026-08-27_deerflow-openrouter-upgrade/playwright-smoke/example-domain.snapshot.yml`

## Resume Prompt

我是 A1/Codex Skill/SOP Engineer。
環境是 `/Users/pagemacmini/maplab-ai-handbook` 與外接 MAPLAB_WORKSPACE。
先讀 `CURRENT_STATUS.md`。
再讀 `pitfalls.md` 最後兩條 2026-08-27 規則。
再讀本卡 `handoff/tasks/T-A1-DEERFLOW-SKILLS-001.md`。
再讀 validation receipt。
不要重裝 Hermes/OpenRouter；production chain 已存在。
不要把 DeerFlow 接進 Telegram、scheduler 或 production hot path。
不要把客戶、報價、訂單、投資、cookie 或 secret 送進 DeerFlow/OpenRouter。
DeerFlow checkout 在 `/Volumes/MacExternal/MAPLAB_WORKSPACE/tools/deer-flow`。
它必須維持 pinned commit `788a890bd022689ef293e6bbfa2c12988173db6c`。
user Skill 在 `/Users/pagemacmini/.agents/skills/deerflow-openrouter-research`。
repo Skill 在 `.agents/skills/maplab-lead-intake-followup`。
Playwright CLI 版本是 0.1.18，官方 Skill 在 `~/.agents/skills/playwright-cli`。
先跑 DeerFlow preflight，不要直接啟動。
preflight 只應回 nginx missing；若出現其他 blocker 先查 drift。
若 Owner 核准 live smoke，優先選 Docker 隔離路徑。
若走 local path，必須取得明確 nginx system install 核准。
第一個 smoke 只用 public/synthetic fixture。
只綁 `127.0.0.1`，禁止 `0.0.0.0`。
關閉 memory extraction、browser、MCP、scheduler、IM、tracing 與 extensions。
限制一個 lead agent、一個 subagent、小額 token/time/recursion budget。
先 authenticated readback OpenRouter Guardrail 的 ZDR/data-collection policy。
不要回顯 key；只報 env variable name 與 present/missing。
完成後要證明 process/port clean shutdown。
輸出寫到外接 `outputs/YYYY-MM-DD_<task>/`。
receipt 必含 commit、model、provider policy、egress、hash、disabled tools 與 next action。
Owner logged-in UI 證據仍用 Browser/Chrome，不用 Playwright persistent profile 搬 cookies。
Anime.js/Cult UI 只在實際 portal repo 建立後按需加入。
Supabase 要等 SSOT/PII/RLS/backup/rollback 決策，不要先建 project。
若沒有新 Owner 授權，本卡保持 DONE，不要自動擴張。

