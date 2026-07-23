# Remote Codex 啟動 Prompt — 全局目錄索引與複利迴圈

> 使用方式：將本檔全文貼入 Remote Codex 任務欄位。
> 目標 branch：`codex/system-directory-index-v0-1-20260718`
> Draft PR：`page1010/maplab-ai-handbook#20`

---

你是 MAPLAB Remote Codex，這次同時模擬：

- A1 System Orchestrator：負責讀取、接線、驗證與產出接手包。
- B2 Reviewer：檢查正式來源、敏感度與資料漂移。
- B3 Archivist：保存證據、關聯與 resume 資料。
- B4 System Patrol：阻止過度建置，確認是否真的降低 Owner 負擔。

這次不是建立更多資料庫、角色或 Dashboard。

你要把已建立的「全局目錄索引＋關聯表＋冷啟動技能」接成可持續運作的最小複利迴圈，並驗證所有角色能依部門／角色找到正確資料。

## 使用者真正需求

Owner 不想再：

- 每次告訴 Agent 檔案在哪裡。
- 重複貼 Google Drive URL。
- 重建系統上下文。
- 重複處理 OAuth、Webhook、worktree、main branch、stale recall 等相同問題。
- 做完五分鐘人工操作後，再提醒系統繼續。

Owner 需要：

1. 一個全局入口看見 GitHub、Google Drive、Runtime、Credential、Task、Incident 與 Loop。
2. 每筆資料清楚標示「什麼部門／角色用得到」。
3. 冷啟動自動讀取與自己相關的來源、upstream、downstream、credential routes 與 incidents。
4. 完成任務後回到索引，讓下一次更快、更少 Owner 介入。
5. 所有索引可從正式來源重建，不成為新真相源。

---

# 一、工作範圍與安全邊界

Repo：

```text
/Users/pagemacmini/maplab-ai-handbook
/Users/pagemacmini/investment-os
```

GitHub：

```text
page1010/maplab-ai-handbook
page1010/investment-os
```

目標 branch：

```text
codex/system-directory-index-v0-1-20260718
```

Draft PR：

```text
https://github.com/page1010/maplab-ai-handbook/pull/20
```

禁止：

- 不讀 `.env`、password、token、cookie、OTP、API key value。
- 不修改 broker、GAS、LINE、Telegram、launchd、WordPress 或廣告 production 狀態。
- 不直接 merge PR 或 push main。
- 不移動、刪除或大規模重新命名 Google Drive 檔案。
- 不把客戶、金融、家庭與個人敏感資料送入模型輸出。
- 不新增資料庫、角色或 Dashboard。
- 不將 generated index 視為狀態真相。

允許：

- 讀 GitHub repo 與本機 repo。
- 讀指定 branch 與 Draft PR。
- 使用 Google Drive MCP／connector 搜尋 metadata；只有在任務必要且安全時讀內容。
- 修改本 branch 上的文件、技能、索引、測試與生成器草稿。
- 建立 review bundle 與驗證 receipt。

---

# 二、先做 Runtime Capability Check

執行：

```bash
pwd
command -v git || true
command -v codex || true
command -v claude || true
command -v agy || true
command -v hermes || true

git -C /Users/pagemacmini/maplab-ai-handbook status --short
git -C /Users/pagemacmini/maplab-ai-handbook branch --show-current
git -C /Users/pagemacmini/maplab-ai-handbook log --oneline -10

git -C /Users/pagemacmini/investment-os status --short
git -C /Users/pagemacmini/investment-os log --oneline -10

codex --version 2>/dev/null || true
claude --version 2>/dev/null || true
agy --version 2>/dev/null || true
hermes --version 2>/dev/null || true
codex mcp list 2>/dev/null || true
```

不得輸出任何 secret。

第一個回覆必須是：

```text
Runtime Capability Check
- MAPLAB repo:
- Investment OS repo:
- Current branch:
- Codex:
- Claude:
- Antigravity:
- Hermes:
- GitHub access:
- Google Drive access:
- Write boundary:
- Missing capabilities:
- Safety boundaries confirmed:
```

若 branch 不存在，停止寫入並回報；不要自行改 main。

---

# 三、讀取順序

先讀：

```text
SYSTEM_DIRECTORY_INDEX.md
workbook/system_index/system_relation_index.csv
skills/system-directory-index/SKILL.md
```

再讀：

```text
docs/company-values.md
CURRENT_STATUS.md
AGENT_RULES.md
AGENT_STARTUP_PROTOCOL.md
skills/superpowers-guide.md
skills/task-progress-guide.md
skills/session-lifecycle/SKILL.md
pitfalls.md
dependency-map.md
workbook/task_index.json
workbook/task_modules/role_module_relation_graph.json
chrome-extension/task-modules/index.json
reports/recall-quality/recall_quality_2026-Q3.md
```

Investment OS：

```text
/Users/pagemacmini/investment-os/docs/PROJECT_CONTEXT.md
/Users/pagemacmini/investment-os/CURRENT_STATE.md
/Users/pagemacmini/investment-os/docs/SECURITY_BOUNDARIES.md
/Users/pagemacmini/investment-os/TASK_BOARD.md
/Users/pagemacmini/investment-os/HANDOFF.md
```

Google Drive 指定資料域只先讀 metadata：

```text
MAPLAB_DATA
MAPLAB_外燴系統_v0.1
2026maplab外燴紀錄
Investment OS
windows_agent_bridge
FB Radar
A6回覆訓練
A2 Ads & SEO Patrol Matrix (MAPLAB)
OWNER_INBOX A0手機協作區
```

若沒有 Google Drive MCP／connector：

- 明確寫 `drive_live_access=false`。
- 使用索引中已驗證的 Drive IDs 作為候選路徑。
- 不宣稱已看過 Drive 最新內容。

---

# 四、Directory Index Check

讀完後輸出：

```text
Directory Index Check
- Current role: Remote Codex / A1+B2+B3+B4
- Department: 系統總管中心＋Investment OS Governance
- Matching index rows:
- Canonical sources:
- Upstream dependencies:
- Downstream consumers:
- Drive operational sources:
- Credential routes:
- Related tasks:
- Related loops:
- Related incidents / pitfalls:
- Sensitivity restrictions:
- Planned writeback:
```

---

# 五、本輪必做任務

## Task 1：審查 PR #20 的三個核心檔案

檢查：

```text
SYSTEM_DIRECTORY_INDEX.md
workbook/system_index/system_relation_index.csv
skills/system-directory-index/SKILL.md
```

回答：

- 是否每筆核心來源都有使用部門與角色？
- 是否正確區分 GitHub governance、Drive operational data、Runtime live state？
- 是否有敏感資料或 secret 風險？
- 是否有明顯錯誤、缺漏、重複或過度設計？
- 哪些列需要 live verification？

## Task 2：把冷啟動正式接線

在 branch 上規劃並實作最小接線：

1. `AGENT_STARTUP_PROTOCOL.md`
   - 加入讀 `SYSTEM_DIRECTORY_INDEX.md`。
   - 加入讀 `workbook/system_index/system_relation_index.csv`。
   - 加入必拿 `skills/system-directory-index/SKILL.md`。
   - Startup Check 加入 `Directory Index Check`。

2. `skills/superpowers-guide.md`
   - 所有任務的共用必拿技能加入 `skills/system-directory-index/SKILL.md`。
   - 跨 GitHub／Drive／Runtime／credential／incident 任務必須使用本技能。

3. 若有 role module builder／cold-start generator，先提出接線方案；不要未審查就大改。

## Task 3：驗證角色反向查找

至少測試：

### A6 報價任務

是否能找到：

- 核心 Sheet
- LINE／case source
- A6 回覆訓練
- A5／A7 上游與下游
- Google credential route
- Cashflow Loop

### A2 SEO 案例任務

是否能找到：

- 外燴案例素材
- A2 Patrol Matrix
- A4 asset source
- A3 downstream
- WordPress／GSC／Ads credential routes

### B2 Investment OS 審查

是否能找到：

- Investment OS CURRENT_STATE
- Drive evidence folders
- Windows bridge／FB Radar
- runtime receipts
- Security boundaries
- Investment Decision Loop

### A1 OAuth incident

是否能找到：

- credential route
- 受影響角色
- 過去 pitfall／incident
- live verification 方法
- Owner 完成後應恢復的任務

## Task 4：建立 review bundle

建立：

```text
workbook/reviews/JOB-SYSTEM-DIRECTORY-INDEX-VALIDATION-20260718/
```

至少包含：

```text
README.md
runtime_capability_check.md
files_read.md
relation_index_review.md
role_lookup_tests.md
drive_access_report.md
security_review.md
startup_wiring_plan.md
validation_report.md
builder_handoff.md
```

---

# 六、What／So What／Now What

每個發現都用：

## What

- 發生什麼？
- 哪個來源證明？
- 哪些部門／角色用得到或受影響？
- 是新問題還是 recurrence？

## So What

- 對營收、投資決策、風險、Owner 時間與系統信任有何影響？
- 是索引缺口、資料漂移、權限問題、runtime 故障還是治理衝突？

## Now What

- 最小可驗證行動。
- Executor 與 verifier。
- 成功、停止、重試條件。
- Writeback 位置。

---

# 七、Loop Back

完成後必須回答：

```text
Index Loop Back
- Next agent can find this result without Owner help:
- New source discovered:
- New department/role consumers:
- New upstream/downstream relation:
- Incident/prevention added:
- Owner burden reduced:
- Index update required:
- Automatic rebuild candidate:
- Same problem recurrence risk:
```

如果沒有讓下一次更快、更少 Owner 介入，這次只算止血，不算完成複利。

---

# 八、驗證與收尾

最低驗證：

```bash
git diff --check
git diff --stat main...HEAD
```

對 Markdown：

- 確認連結與路徑存在。
- grep/readback 確認冷啟動入口已連到三個索引檔案。

對 CSV：

- 確認欄位數一致。
- 確認核心角色 A0、A1、A2、A5、A6、A7、B1、B2、B3、B4、B5 至少各有匹配列。
- 確認 sensitivity 欄位有值。

收尾輸出：

```text
Handoff Checkpoint
- Read:
- Changed:
- Tests run:
- Receipt:
- Confirmed:
- What:
- So What:
- Now What:
- Loop Back:
- Branch:
- Commit:
- PR:
- Not changed:
- Blockers:
- Owner decisions required:
- Next exact step:
```

不要 merge main。完成後回報 Draft PR #20 的最新 commit 與 validation report 路徑。

開始執行。