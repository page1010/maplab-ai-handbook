# T-A1-SCREENSHOT-TOOLS-SKILLS-002 — Screenshot Tools Skill Convergence

## 接續狀態

- **狀態**: ✅ DONE（skills 與治理路由完成；外部 Labs／雲端影片服務未連接）
- **最後活動**: 2026-08-27 Codex A1
- **接續點**: 有實際 UI 專案再選 Stitch；有實際雲端影片 workflow 再做 RunningHub 或 Comfy Cloud 的 synthetic smoke。
- **阻塞**: 不阻塞本卡完成。Graphify graph 落後 HEAD，需在 clean checkpoint 後另跑 `graphify update .`；RunningHub/Comfy Cloud 尚無 authenticated live receipt。
- **assigned_session**: 2026-08-27 / Codex acting as System Skill Architecture Engineer
- **implementation_checkpoint**: `d17f3762221c8299fb0b7f0f059f4b5a868d71db`
- **可逆性**: 可逆。三個 repo skills 可由 commit revert；兩個 user skills 為獨立資料夾且沒有 hook、service、credential 或 production route。

## Owner 需求

評估截圖中的 `claude-video`、`notebooklm-py`、Graphify、Impeccable、Pomelli、Stitch、Opal、Antigravity、Mixboard，能用的安裝或建成 skills；並確認 ComfyUI + RunningHub 做影片是否可用雲端而非地端算力。

## 本版 v0.1 交付

- [x] 官方／上游來源、license、credential、資料外送、區域與 automation surface 稽核。
- [x] 安裝 pinned user Skill `watch` v0.2.0；預設私有影片 no-cloud-ASR。
- [x] 安裝 pinned user Skill `impeccable` v4.1.2；未安裝或核准 hooks。
- [x] 建立 repo Skill `maplab-video-evidence-readback`，不複製 A8 正式產線。
- [x] 建立 repo Skill `maplab-project-knowledge-router`，分流 Graphify／NotebookLM／live truth。
- [x] 建立 repo Skill `maplab-creative-prototype-router`，治理 Impeccable 與 Google Labs 原型工具。
- [x] `notebooklm-py` HOLD；Graphify 與現有 NotebookLM pack 不重裝／不建第二控制面。
- [x] 五個 skill validators PASS、discovery `skills=14 duplicates=0`、watch smoke PASS、system-map tests 7/7 PASS、獨立 forward test PASS。
- [x] 官方能力確認：RunningHub 與 Comfy Cloud 可在雲端 GPU 執行 ComfyUI 影片 workflow；MAPLAB 尚未連接或付費執行。

## 決策

| 工具 | 決策 | 系統邊界 |
|---|---|---|
| claude-video / watch | ADOPT pinned | 分析證據，不剪輯／發布；私人音訊預設不上雲 |
| notebooklm-py | HOLD | 非官方 Google API、cookie/分享/刪除能力過寬，與安全 pack 重複 |
| Graphify | KEEP, REFRESH LATER | AST-only；graph stale 時回 `NEEDS_LIVE_REFRESH` |
| Impeccable | ADOPT pinned, no hooks | UI critique/polish；MAPLAB visual/voice specs 優先 |
| Pomelli | CONDITIONAL WEB | 公開／已核准品牌資料；draft only，publish gate |
| Stitch | CONDITIONAL PROJECT | 真 UI 專案才選少數 official-repo skills／scoped MCP |
| Opal | HOLD | private/customer input 禁止；先驗證台灣、Drive、sharing |
| Antigravity | KEEP RESTRICTED | 不新增 write lease、MCP write 或 login bridge |
| Mixboard | CONDITIONAL WEB | 公開／合成 moodboard；不是 rights/final proof |
| ComfyUI + RunningHub | AVAILABLE_EXTERNALLY | cloud GPU yes；third-party RunningHub integration 尚未接 |

## 驗收證據

- `workbook/reviews/JOB-A1-SCREENSHOT-TOOLS-SKILLS-20260827/validation_receipt.md`
- implementation commit `d17f3762221c8299fb0b7f0f059f4b5a868d71db`

## Resume Prompt

我是 A1/Codex System Skill Architecture Engineer。
環境是 `/Users/pagemacmini/maplab-ai-handbook`。
先讀 `CURRENT_STATUS.md`。
再讀 `pitfalls.md` 最後兩條 2026-08-27 規則。
再讀本卡。
再讀 validation receipt。
不要重裝 watch、Impeccable、Graphify 或 notebooklm-py。
user watch 在 `/Users/pagemacmini/.codex/skills/watch`。
user Impeccable 在 `/Users/pagemacmini/.codex/skills/impeccable`。
兩者 source commit 已寫在 SKILL metadata。
不要執行 Impeccable npx install/update 或安裝 hook。
MAPLAB 私有／客戶／兒童影片預設 `--no-whisper`。
要逐字稿而無核准 local route 時回 `BLOCKED_EGRESS`。
單張 contact sheet 不得升 `QA_PASS`。
Project router preflight 要先跑。
Graphify 目前 built commit 落後 implementation HEAD。
在 clean checkpoint 前不要跑 `graphify update .`。
NotebookLM 兩個 pack hash 目前 ready。
不要裝 notebooklm-py 或匯入 Google cookies。
Stitch 只在真 UI 專案選少數 skill，不整套全域安裝。
Pomelli/Mixboard 只吃 public、approved-brand 或 synthetic。
Opal 對 private/customer input 是不可覆寫禁止。
Antigravity 不新增 write lease/MCP write/login bridge。
RunningHub 是第三方 cloud ComfyUI，不是官方 Comfy Cloud。
雲端 workflow 會上傳 input 並產生費用，先做 data/cost/rights gate。
若 Owner 要 cloud video pilot，只用 synthetic 2–5 秒 fixture。
先選 RunningHub 或 official Comfy Cloud，不同時接兩套。
API key 只進 protected env/vault，不進 repo 或 receipt。
留 workflow JSON、provider、GPU/runtime、費用、output hash、cleanup receipt。
公開發布仍走 A8 Owner gate。
若沒有新 Owner 授權，本卡保持 DONE，不自動擴張。
