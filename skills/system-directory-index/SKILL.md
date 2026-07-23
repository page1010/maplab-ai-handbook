# System Directory Index Skill

> 版本：v0.1
> 日期：2026-07-18
> 適用：所有 MAPLAB／Investment OS 角色與 Remote worker

---

## 目的

讓任何 Agent 在冷啟動或接手任務時，不必先問 Owner「檔案在哪裡」，而能先從全局索引與關聯表找到：

- 正式來源
- 哪些部門／角色會使用
- 上游依賴
- 下游受影響對象
- Drive 營運資料
- Credential 路由
- 相關 Task Card
- 過去 incident／pitfall
- 正確 writeback 路徑

本技能是導航技能，不是新的狀態真相源。

---

# 1. 何時必須載入

以下情況必須載入本技能：

1. 所有角色 cold start。
2. Owner 問「資料在哪裡」「誰負責」「這會影響誰」。
3. 任務跨 GitHub、Google Drive、Sheets、Telegram、GAS、runtime。
4. 發生 OAuth、credential、Webhook、worktree、main branch、stale recall、duplicate file 等重複問題。
5. 要修改共用資料、共用 schema、Items、CURRENT_STATUS、role module、credential route。
6. 新 Agent／Remote worker 接手舊任務。
7. 要建立或更新關聯圖、資料地圖、Drive 導航或 Incident 記憶。

---

# 2. 必讀來源

依序讀：

1. `SYSTEM_DIRECTORY_INDEX.md`
2. `workbook/system_index/system_relation_index.csv`
3. `CURRENT_STATUS.md` 或對應 repo 的 `CURRENT_STATE.md`
4. 自己的 role recall／module
5. 關聯表中自己的 `used_by_roles` 相關列
6. 直接 upstream
7. 會受到本任務影響的 downstream
8. related tasks／related loops
9. credential routes（若涉及外部系統）
10. pitfalls／review bundles（若是重複問題或修復任務）

不得只讀自己的 recall 就開始跨系統工作。

---

# 3. 依角色篩選關聯表

關聯表欄位：

```text
source_id
source_type
title
path_or_id
canonical_status
used_by_departments
used_by_roles
upstream
downstream
related_tasks
related_loops
sensitivity
last_verified
notes
```

## 篩選方式

1. 以自己的 role_id 搜尋 `used_by_roles`。
2. 若是部門級任務，再搜尋 `used_by_departments`。
3. 收集所有匹配列。
4. 對每列檢查：
   - canonical_status
   - upstream
   - downstream
   - sensitivity
   - last_verified
5. 只讀完成任務所需的最小內容。

## 例子

A6 接手報價任務時至少會找到：

- MAPLAB 核心 Sheet
- LINE／case source
- A6 回覆訓練
- 報價資料夾
- A5／A7 GitHub 文件
- Google credential route
- Cashflow Loop

A2 接手 SEO 案例任務時至少會找到：

- 外燴案例素材資料夾
- A2 Patrol Matrix
- A4 asset source
- A3 landing／ads downstream
- WordPress／GSC／Ads credential routes

B2 審查 Investment OS 時至少會找到：

- Investment OS CURRENT_STATE
- Drive evidence folders
- Windows bridge／FB Radar
- runtime receipts
- Security boundaries
- Investment Decision Loop

---

# 4. Canonical Source 判斷

## GitHub

主要回答：

- 規則
- 角色
- Task Card
- 版本
- 決策
- 驗證報告
- 技能
- Incident／pitfall

## Google Drive／Sheets

主要回答：

- live 營運資料
- 客戶案件
- 報價
- LINE 對話
- 訂單結果
- 素材
- Drive evidence

## Runtime

主要回答：

- 現在是否在線
- OAuth 是否有效
- bot／launchd 是否在跑
- SQLite 是否有資料
- GAS／broker／OpenClaw 是否真的成功

## 衝突處理

```text
live readback
> runtime receipt
> latest validation report
> CURRENT_STATUS／CURRENT_STATE／Task Card
> generated index
> Drive mirror／old snapshot／memory
```

索引只能幫你找到來源，不能用索引內容取代 live verification。

---

# 5. 冷啟動輸出格式

載入本技能後，Startup Check 必須增加：

```text
Directory Index Check
- Current role:
- Department:
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

若找不到任何 matching row：

```text
index_gap=true
```

並在本次 review bundle 中提出 `relation_index_update`，不得直接問 Owner 檔案在哪裡，除非已完成合理搜尋。

---

# 6. 找資料流程

```text
確認角色與任務
→ 讀索引
→ 篩角色／部門列
→ 找 canonical source
→ 讀 upstream／downstream
→ 檢查 sensitivity
→ 查 related task／loop
→ 查 incident／pitfall
→ 必要時 live verify
→ 回答 What／So What／Now What
→ 執行
→ 驗證
→ writeback
→ 更新索引候選
```

---

# 7. What／So What／Now What

## What

- 發生什麼？
- 現在狀態是什麼？
- 哪些正式來源證明？
- 哪些角色會使用或受影響？
- 是 recurrence 還是新問題？

## So What

- 對營收、決策速度、風險或使用者負擔有何影響？
- 是資料問題、權限問題、治理漂移、runtime 故障還是產品缺口？
- 是否值得現在處理？

## Now What

- 最小可驗證行動是什麼？
- 誰執行、誰驗證？
- 成功／停止／重試條件是什麼？
- 結果寫回哪裡？

---

# 8. Loop Back

每個任務完成後必須重新問：

1. 下一個 Agent 能否透過索引找到這次結果？
2. 是否新增或修正「什麼部門／角色用得到」？
3. upstream／downstream 是否完整？
4. 是否需要新 incident／pitfall／skill？
5. Owner 下次是否還要重複提供檔案位置或權限路徑？
6. 是否增加自動偵測、驗證、retry 或 resume？
7. 如果答案都是否，這次只算止血，不算複利完成。

收尾輸出：

```text
Index Loop Back
- New source discovered:
- New role/department consumers:
- New upstream/downstream relation:
- Incident/prevention added:
- Owner burden reduced:
- Index update required:
- Rebuild required:
```

---

# 9. 安全規則

- 不讀取或保存 password、token、cookie、OTP、API key value、`.env`。
- 客戶資料以 metadata、去識別化摘要、欄位結構為主。
- 私人、家庭、護照、薪資、保險、醫療資料預設 excluded。
- `sensitivity=financial/customer_data/credential_reference/excluded` 時採最小必要讀取。
- Drive 同名文件不代表同一版本；先判斷 canonical_status。
- Generated index 不得凌駕 GitHub、Drive live data 或 runtime readback。

---

# 10. 索引缺口回寫

發現缺口時，不直接隨手修改全部治理文件。

優先輸出：

```text
relation_index_update
- source_id:
- proposed title:
- canonical source:
- used_by_departments:
- used_by_roles:
- upstream:
- downstream:
- related tasks:
- related loops:
- sensitivity:
- evidence:
```

由 A1／B3 合併，B2 抽查 canonical source 與 evidence。

---

# 版本紀錄

## v0.1 — 2026-07-18

- 建立所有角色冷啟動共用的目錄索引技能。
- 強制加入「什麼部門／角色用得到」。
- 要求讀自己的關聯列、upstream、downstream、credential 與 incident。
- 加入 What／So What／Now What 與 Loop Back，避免只完成盤點不形成複利。
