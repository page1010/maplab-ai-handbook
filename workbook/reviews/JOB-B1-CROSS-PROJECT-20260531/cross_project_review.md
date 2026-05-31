# Cross-Project Review — 多模型協調 + 任務續航 fit 進 MAPLAB

**日期：2026-05-31 | 角色：B1 | 召喚任務：把兩段 ChatGPT 討論 fit 並落實進系統**

## 診斷（80/20）

MAPLAB 已有約 75% 基礎建設。兩段 ChatGPT 討論的價值不在「多開代理」，而在三件事：
主代理只調度不做雜工、便宜模型先過濾省算力、agent 用 artifact 交接。

**已存在、沿用即可：** CURRENT_STATUS（=SYSTEM_STATE）、checkpoint.sh（=session checkpoint）、
patrol.sh + launchd（=每日 audit）、git-pull.sh + verify-commit-on-main.sh + REPO_SYNC_RULES
（=雲端永遠最新）、CHANGELOG（=version log）。

**真缺口（本輪補）：**
1. Codex / Antigravity / 地端 Ollama 沒有被治理（AGENT_RULES 只治 Claude 系 A0-A8+B1）。
2. AGENT_RUN_LOG 紀律缺（patrol 偵測缺 commit，不偵測缺紀錄/把推論當事實）。
3. 額度中斷續航缺（無 waiting_for_quota 佇列 + 自動 resume prompt）。

## 本輪產出

- `docs/governance/multi-model-orchestration-v0.1.md` — 三層路由 + 能力邊界 + 防重複對映 + 省 token 政策。
- `docs/governance/task-continuity-orchestrator-v0.1.md` — 地端守夜人 + run-log schema + resume 機制。
- `b1_prompt.md` — Chrome Extension 可快速召喚的三段 prompt（巡查員/Antigravity/地端守夜人）。
- `pause_resume_note.md`、`review_request.md`。

## System improvement signals

- **防重複**：嚴禁照搬 ChatGPT 通用檔名另開檔，會造成真相來源混亂（pitfalls 2026-05-19）。
- **高槓桿小改**：checkpoint.sh 收尾自動跑 verify-commit-on-main.sh，讓「已上雲」成預設驗收。
- **不越權**：實際改腳本/AGENT_RULES/Extension 由 A1 落地；A6 bot 客戶流程不碰。
