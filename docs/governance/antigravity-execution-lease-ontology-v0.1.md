# Antigravity Execution Lease / Ontology v0.1 — 提案存檔 + A1 對齊檢查

> 狀態：**提案已存檔，僅評估，尚未實作／未動 repo 或 runtime**
> 來源：Codex（可能在 Mac mini 另一個 session）進行中的設計，Owner 透過對話轉述給 A1（remote，2026-07-20），
> Owner 註明「不確定他有沒有存檔」——本檔的第一目的是**先把內容存下來，避免真的遺失**（呼應
> `docs/company-values.md`「不做白工」「得到一筆有用資訊就紀錄上去」）。
> 第二目的：A1 對照既有治理文件做一致性檢查，找出衝突與缺口，供 Codex／Owner 下一輪決策參考。

---

## 一、原始提案內容（逐字保留，Owner 轉述）

> 結論：Antigravity 不應只是 Telegram 遙控器或臨時外包代理，而要成為 PLTR 式治理下的正式「執行節點＋暖備援」。
>
> 目前狀態：agy 1.1.4、Antigravity IDE、Telegram bot 與 launchd 都在線；Telegram → Antigravity 收發已通；但治理
> registry 仍標成 `pending_smoke`，沒有接管租約、checkpoint resume、失效轉派與防雙主機制。現況只能算「人工操作
> 備援」，不能稱為「可接管的系統備援」。
>
> 修正後的 PLTR 架構：
>
> ```text
> WorkItem / Task Card
>         ↓
> Policy Gate
>         ↓
> ExecutionLease ── 主執行者
>         │
>         ├─ heartbeat + checkpoint
>         └─ 異常／配額耗盡／人工交接
>                  ↓
>           revoke + fencing
>                  ↓
>       Antigravity 取得新 lease
>                  ↓
>      從同一 checkpoint 繼續
>                  ↓
>  Deterministic Verify → Receipt → Outcome
> ```
>
> Ontology 新增的是通用治理物件（不是「Antigravity 專用邏輯」）：
> - **AgentNode**：Codex、Antigravity、Hermes 都只是節點實例。
> - **CapabilityProfile**：能讀哪些資料、能執行哪些工具。
> - **WorkItem**：目標、允許路徑、驗收、風險等級。
> - **ExecutionLease**：目前唯一合法執行者、到期時間、fencing epoch。
> - **TaskCheckpoint**：commit、step、測試結果、待辦、context manifest。
> - **ActionReceipt**：誰、何時、為何、做了什麼、結果如何。
>
> 新增治理 Actions：`claim_task` / `renew_lease` / `checkpoint_task` / `handover_task` / `resume_task` /
> `submit_result` / `abort_task`。
>
> 核心政策：
> 1. 同一任務只能有一個有效 lease，避免 Codex 與 Antigravity 同時修改。
> 2. 接管前必須確認舊執行程序已停止；否則進入 `waiting_fence`。
> 3. Antigravity 只能在獨立 worktree 與允許路徑內工作。
> 4. 不開全域 AutoAccept，也不用 `dangerously-skip-permissions`；權限由每張任務卡臨時授予。
> 5. 低風險、可逆任務可自動接管；runtime、Telegram、launchd 變更需核准；broker、secret、公開發布維持禁止。
> 6. Antigravity 不得自我核准成果；由 deterministic eval、Owner/B1 或可用的 Repo Integrator 驗收。
> 7. Telegram 只是控制介面，不能成為狀態真相源。
>
> 對應 Palantir 方法：Ontology 不只有資料物件，也有 Action types；Actions 透過 submission criteria 控制誰能用什麼
> 參數執行，敏感操作留下 justification/checkpoint，audit 回答 who/what/when/where（Ontology、Action permissions、
> Checkpoints、Audit logs）。
>
> 關鍵限制：Antigravity 和主系統仍在同一台 Mac、同一份網路與檔案系統，第一階段只能叫 `warm_execution_standby`
> ——能防代理崩潰、額度耗盡與 session 中斷；**不能冒充整台主機故障時的災難備援**。跨機備援留第二階段。
>
> 第一階段驗收標準：建一個隔離測試任務 → 主執行者完成 checkpoint 後被強制停止 → Antigravity 在三分鐘內取得新
> lease → 沿用同一 task/trace/checkpoint 完成 → 測試通過並留下 receipt → 舊執行者恢復後因過期 fencing token 被拒絕
> 寫入。
>
> 修正方向：不是另外裝一個大型 loop framework，而是把 Antigravity 接進現有 Ontology Action Layer，成為受政策控制、
> 能正常派工也能正式接管的備援執行節點。本輪只有評估，尚未更動 repo/runtime。

---

## 二、A1 對齊檢查（與既有治理文件逐項比對）

### 2.1 不是重複建置，是既有草案的正式化升級

`docs/governance/task-continuity-orchestrator-v0.1.md`（B1，2026-05-31，**狀態仍是「草案待 A1/Owner 審」，
從未正式採納**）已經提出過同一類問題的輕量版解法：`waiting_for_quota` 佇列狀態、
`QUEUE_NEXT_FOR_CODEX.md` resume prompt、run-log 三分法（`claims_verified/inferred/missing`）、地端模型
A/B/C/D 能力分級。但那份草案是**檔案輪替式的序列交接**（一次只有一個模型在跑，靠人工/腳本產生下一輪 prompt），
從未處理「兩個 agent 同時想動同一份工作」的併發安全問題。

Codex 這份提案本質上是把 `task-continuity-orchestrator-v0.1.md` 的概念**升級成有併發安全（fencing token 防雙主）
的正式物件模型**，並且是第一次有文件明確處理「主執行者被強制停止後，備援怎麼安全接手同一個 checkpoint」。
**結論：兩份文件是同一條演進線，不是平行真相源；`task-continuity-orchestrator-v0.1.md` 應該被視為本提案的
v0 草案前身，本提案是 v1 方向。**

### 2.2 與 SECTION 24（可逆先行準則）高度一致

提案政策 5「低風險、可逆任務可自動接管；runtime/Telegram/launchd 變更需核准；broker/secret/公開發布維持禁止」
跟 `AGENT_RULES.md` SECTION 24（可逆先行準則，2026-07-19）與 SECTION 19（自主/升級判準）的判準幾乎一致：
可逆＋低風險＋scope 內 → 自己決定；不可逆／碰 secrets／碰 runtime → 才升 Owner。**這是好事**——代表 Codex 這份
提案跟 MAPLAB 現行治理骨架同源，不是另立一套邏輯。建議 `ExecutionLease` 的授予規則直接引用 SECTION 24 的
「快速判斷表」當作 Policy Gate 的具體條目來源，不要重寫一份平行的可逆性判準。

### 2.3 與 SECTION 21 規則三（2026-07-20 新增）的關係

Owner 昨天才明確要求「能自己判斷的不准卡住問，真的要問只給按鍵」（見本次 session 稍早對 AGENT_RULES.md 的修改）。
本提案的 `waiting_fence` 狀態、`revoke + fencing`、自動接管流程，正是把「卡住等 Owner」的情境**盡量往「系統自己
處理」推**，方向完全一致。但提案裡「異常／配額耗盡／人工交接」這條路徑最終若需要 Owner 介入，其呈現格式也必須
遵守規則三——**用可點擊選項卡，不要丟 fencing token / lease epoch 這類技術詞給 Owner**。

### 2.4 未解決的關鍵阻塞：agy 的 sandbox 唯讀保證仍未驗證

**這是本次對齊檢查發現的最重要缺口，必須在授予 Antigravity 任何 ExecutionLease 之前解決：**

`skills/codex-offload-guide.md`（2026-07-06 盤點，2026-07-10 更新，**至今未關閉**）明文：

> ⚠️ 權限風險（2026-07-06 盤點發現，接生產路徑前必須解決）：agy 在 `--print --sandbox` 模式下觀察到會**主動執行
> shell 指令探測環境**，沒有等同 Codex `-s read-only` 的強制唯讀保證。目前只建議用在「純文字進、純文字出」且不
> 牽涉任何敏感操作的場景。

Codex 提案的政策 4（「權限由每張任務卡臨時授予」）與政策 3（「只能在獨立 worktree 與允許路徑內工作」）**假設了
一個可信的 sandbox 邊界**，但 MAPLAB 現有紀錄顯示這個邊界本身還沒被驗證過。**在 `agy help`/`agy plugin` 的權限
範圍設定被實際確認、或改用 `--add-dir` 限定 scratch 目錄驗證通過之前，任何 `ExecutionLease` 都不應該授予
Antigravity 寫入權限（哪怕只是「獨立 worktree」）——因為目前不知道 agy 是否真的只會動 worktree 裡的檔案。**
建議：Codex 提案的驗收標準（第一階段隔離測試）**必須把這項也納入**——不只測 lease 交接是否成功，還要測
agy 在拿到 lease 期間，是否曾經嘗試讀寫允許路徑之外的東西。

### 2.5 CapabilityProfile 不應該憑空放寬 Antigravity 現有能力邊界

`docs/governance/multi-model-orchestration-v0.1.md`（2026-05-31，已有能力邊界表）目前把 Antigravity 定義為：

| 可以做 | 不可以做 |
|---|---|
| Google 生態、UI 驗證、browser artifact、多 workspace | **核心架構決策、憑證操作、無 sandbox 刪檔** |

而 `skills/codex-offload-guide.md` 也明文：「Codex、Antigravity（agy）不是獨立角色，是可調度的執行層」——目前
系統裡沒有 `recalls/Antigravity_recall.md`，代表它從未被當成正式角色註冊過。

本提案要把 Antigravity 升格為能 `claim_task` 並接手 Codex 未完成 checkpoint 的正式執行節點，**這本質上是一次
角色升格**，跟 MAPLAB 安全紅線「不允許模型自動升格自己」（見 `LOCAL_MODEL_EVOLUTION_ORCHESTRATOR_PROMPT.md` 同一
紅線精神，適用於所有 agent，不限地端模型）在精神上有交集——升格這件事本身應該是 Owner 的一次性明確決定，
不是靠一份技術提案自動生效。

**建議**：`CapabilityProfile` for Antigravity 第一階段應該**原樣沿用**現有邊界表（Google 生態/UI/browser 類
WorkItem 才能被 Antigravity claim），不要因為建了新的 Ontology 就預設 Antigravity 可以接手「Codex 在做的任何
repo 修改任務」。若要擴大到核心 repo 修改，屬於 2.4 的 sandbox 驗證 + 2.5 的角色升格，兩者都需要 Owner 一次性
書面核准，不能用「提案已經寫了政策 6（不得自我核准）」來替代這個授權步驟——政策 6 管的是「執行結果由誰驗收」，
不是「一開始有沒有資格被授予這個角色」。

### 2.6 A1（本 remote session）在這個 Ontology 裡的定位

如果套用提案的物件模型，A1 目前這個 remote session 本身也是一個 `AgentNode` 實例，但**目前完全在這套 Ontology
之外運作**——沒有 `ExecutionLease`、沒有 `CapabilityProfile` 註冊，靠的是「GitHub branch + Draft PR」這個更原始
的互斥機制（本次 session 稍早真的遇到一次 `main` 分支併發修改衝突，靠 `git merge` 手動解掉，見 PR #21 commit
`cb30b09`——這其實就是「沒有 fencing token 保護時，兩個執行者同時碰同一份真相源」的真實案例，可以當提案第 2.4
節「防雙主機制」的活教材）。

**結論**：短期不需要把 remote CCR session 也接進正式 Ontology（範圍過大、且 remote session 的生命週期本來就跟
GitHub PR 綁定，天然有審查關卡）；但這次真實發生的合併衝突，可以直接當作提案驗收案例的補充證據——證明「沒有
fencing/lease 機制時，多執行者同時寫同一份真相源」不是假設風險，是這個系統本週就實際發生過的事。

---

## 三、A1 建議的下一步（不是決定，等 Codex/Owner 對齊）

1. **先確認 Codex 那份原始設計是否已存檔**——本檔只保存了 Owner 轉述的部分內容，Codex 手上可能有更完整的
   schema／程式碼草稿，需要 Codex 自己 checkpoint 到 repo，不能只靠這次轉述重建。
2. **在寫任何 `ExecutionLease` 程式碼之前，先關掉 2.4 的 agy sandbox 驗證缺口**——這是唯一一個「不解決就不該讓
   Antigravity 拿到任何寫入 lease」的硬阻塞。
3. **`CapabilityProfile` 初版應該照抄 `multi-model-orchestration-v0.1.md` 現有邊界表**，不要重新定義一份更寬的
   權限，除非 Owner 明確決定要擴大 Antigravity 角色（見 2.5）。
4. **落地順序建議**：先把 `task-continuity-orchestrator-v0.1.md`（從未正式採納的草案）與本提案合併成同一份
   `v1`，避免未來出現兩份「怎麼處理任務中斷接續」的文件互相打架。
5. 第一階段驗收（提案原文的隔離測試）建議由 A1 或 B2 執行並附 receipt，不要由 Antigravity/Codex 自己宣稱通過
   ——呼應提案自己的政策 6。

---

## 四、狀態

- 建立：2026-07-20，A1（remote session），依 Owner 轉述 Codex 進行中設計整理存檔。
- 未執行任何程式碼變更、未建立任何 `ExecutionLease`/Ontology 實作、未動 launchd/agy/Telegram 設定。
- 下一步需要 Codex 確認原始設計、Owner 對 2.5 角色升格做決定、A1/B2 驗收 2.4 的 sandbox 缺口是否已關閉。
