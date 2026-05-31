# Multi-Model Orchestration v0.1 — Codex / Antigravity / 地端模型能力邊界

**建立：2026-05-31 | 作者：B1（跨專案治理顧問召喚）| 狀態：草案待 A1/Owner 審**
**來源：兩段 ChatGPT 討論（動態工作流程與協調 / 地端模型使用建議）fit 進 MAPLAB**

---

## 0. 為什麼有這份文件

MAPLAB 已有成熟治理層（CURRENT_STATUS、AGENT_RULES、patrol.sh、checkpoint.sh、
git-pull.sh、verify-commit-on-main.sh、REPO_SYNC_RULES）。但這些只治理 **Claude 系
A0-A8 + B1**，沒有把 **Codex、Antigravity、地端 Ollama** 當成有能力邊界的受治理角色。

本文件補上這個缺口：定義三層省算力路由、能力邊界表，並把 ChatGPT 提案的通用檔名
**對映到 MAPLAB 既有真相源**，避免新增重複檔造成真相來源混亂（見 pitfalls 2026-05-19）。

---

## 1. 核心原則（三條）

1. **主代理只調度與驗收，不做雜工。** Codex = 總工程師／系統巡查員，負責拆任務、
   分派、讀回報、判斷是否進 repo；不自己長時間翻資料夾、不未確認現況就重構。
2. **省算力 = 讓便宜模型先過濾。** 地端模型先掃 logs／task card／diff／缺口，只把
   「異常、決策點、可疑幻覺」這 5% 丟給 Codex / GPT / Gemini。
3. **代理之間用 artifact 交接，不靠口頭。** 任何 agent 不准只說「完成」，必須留下可
   驗收 artifact（呼應 MAPLAB「凡走過必留痕跡」與 verification-bundles.md）。

---

## 2. 三層省算力架構

| 層 | 角色 | 引擎 | 做什麼 | 不做什麼 |
|----|------|------|--------|----------|
| **L1 掃描** | 地端影子巡查員 | Ollama 地端 | 讀 repo status / task card / log / diff，標缺口，產 shadow review bundle | 改 code、下結論、部署、下單 |
| **L2 工程判斷** | 系統巡查員／總工程師 | Codex | 只讀 L1 bundle（不重讀整 repo），分類問題、分派、修 repo、寫紀錄、驗收 | 無授權 commit/push、臆測寫成事實 |
| **L3 高價任務** | 研究／驗證／產出 | GPT / Gemini / Antigravity | 投資研究推論、跨 Google 資料驗證、SEO 正式產出、UI/browser 驗證、跨模型交叉確認 | 未查證寫成事實、自動交易 |

**路由順序：** 地端整理 → Codex 執行/修補 → Gemini/Antigravity 跨 Google 資料交叉確認 → GPT 策略審查與版本升級。

---

## 3. 能力邊界表

| 角色 | 可以做 | 不可以做 | 輸出物 |
|------|--------|----------|--------|
| **Codex** | repo 改動、任務拆解、驗收、版本紀錄 | 無授權 commit/push、真實下單、臆測資料 | diff、test log、version log |
| **Antigravity** | Google 生態、UI 驗證、browser artifact、多 workspace | 核心架構決策、憑證操作、無 sandbox 刪檔 | screenshots、plans、recordings |
| **地端 Ollama** | logs 掃描、缺口標註、低成本預檢、resume prompt 生成 | 改 code、下結論、部署、下單、最終投資/選股結論 | shadow_review_bundle、resume prompt |
| **OpenClaw** | 瀏覽器自動化、例行抓取、表單檢查 | 高階推理、核心 repo 改動、敏感操作 | run log、browser trace |
| **GPT / Gemini** | 高階研究、推論、投資框架、SEO 正式產出 | 未查證寫成事實、自動交易 | cited report、decision memo |

地端模型分級（A 放心給／B 要審查／C 只反問／D 禁止）詳見
`task-continuity-orchestrator-v0.1.md` §地端分級。

---

## 4. ChatGPT 提案檔名 → MAPLAB 既有真相源（防重複）

ChatGPT 建議建 SYSTEM_STATE.md / TASK_QUEUE.md / AGENT_RUN_LOG.md /
NEXT_CODEX_PROMPT.md / VERSION_LOG.md。MAPLAB 多數已存在，**不另開重複檔**：

| ChatGPT 提案 | MAPLAB 既有對映 | 動作 |
|--------------|----------------|------|
| SYSTEM_STATE.md | `CURRENT_STATUS.md`（唯一狀態入口）| 沿用，不新增 |
| TASK_QUEUE.md | `CURRENT_STATUS.md` 任務表 + `workbook/task_index.json` | 沿用 |
| SESSION_CHECKPOINT | `scripts/checkpoint.sh` + `handoff/tasks/T-*.md` 接續狀態區塊 | 沿用 |
| 每日 local-audit | `scripts/patrol.sh`（launchd com.maplab.patrol）| 沿用 |
| VERSION_LOG.md | `CHANGELOG.md` + 各 review bundle | 沿用 |
| 「雲端永遠最新」 | `scripts/git-pull.sh`（launchd 自動 pull）+ `verify-commit-on-main.sh` + REPO_SYNC_RULES | 沿用，見 §6 |
| AGENT_RUN_LOG.md | **缺口** → 新增 schema | 見 continuity 文件 §run-log |
| NEXT_CODEX_PROMPT.md | **缺口** → 新增續航機制 | 見 continuity 文件 §resume |

**結論：** 只補兩個真缺口（run-log 紀律 + quota 續航），其餘全部沿用既有真相源。

---

## 5. 省用量（token）政策

1. 預設 L1 地端先過濾；高價模型只看 L1 整理出的 top-N issue。
2. Codex 只讀 review bundle，禁止重讀整個 repo。
3. 投資/SEO 正式產出才升級到 L3；格式檢查、log 整理、缺口盤點一律留在 L1。
4. quota 用完不是失敗，是 `waiting_for_quota` 佇列狀態（見 continuity 文件）。

---

## 6. 「雲端永遠是新版」現況（已存在，不重造）

- `scripts/git-pull.sh`：launchd `com.maplab.git-pull` 定期 `pull --rebase origin main`（dirty 先 stash）。已載入並正常。
- `scripts/checkpoint.sh --fast`：一鍵 commit + push main（信任模式）。
- `scripts/verify-commit-on-main.sh`：session 結束前驗證 commit 已在 main。
- `REPO_SYNC_RULES.md`：執行層 repo 48h 內必須回寫 handbook。

**唯一補強建議**：在 `checkpoint.sh` 收尾自動呼叫 `verify-commit-on-main.sh`，
讓「已推上雲端」變成預設驗收，而不是靠人記得跑。（列為 A1 待辦，B1 不直接改腳本。）
