# Remote Role Cold-Start Launcher 操作手冊

> 版本：v0.1
> 日期：2026-07-18
> 用途：讓 Remote Codex 像 MAPLAB Agent Commander Extension 一樣，自動選角、讀懂全貌並直接跑起來。

---

## 1. 核心概念

現有 Chrome Extension 的正確架構是：

```text
module index
→ role module
→ CURRENT_STATUS
→ role recall
→ runtime handoff
```

Remote Role Launcher 沿用相同資料層，再追加：

```text
SYSTEM_DIRECTORY_INDEX
→ role relation rows
→ Drive operational sources
→ credential routes
→ upstream/downstream
→ incidents/pitfalls
→ verification + Loop Back
```

因此 Remote Codex 不會靠一段固定萬用 Prompt 模擬所有角色，而是每次依任務動態載入真正的角色資料。

---

## 2. 使用者最短操作

打開 Remote Codex，在已連線的 Mac mini machine 中貼入：

```text
請讀取並完整執行：
/Users/pagemacmini/maplab-ai-handbook/REMOTE_CODEX_ROLE_LAUNCHER_PROMPT.md

本次任務：
[輸入任務]
```

更穩定的方式是把 `REMOTE_CODEX_ROLE_LAUNCHER_PROMPT.md` 全文貼入，替換最後的任務欄位。

---

## 3. 產生器指令

### 自動選角

```bash
cd /Users/pagemacmini/maplab-ai-handbook

python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role AUTO \
  --runtime codex \
  --task "檢查 A6 報價流程為什麼沒有把修改寫回 REVISION_LOG" \
  --output /tmp/maplab-role-handoff.md \
  --explain-route
```

### 指定角色

```bash
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role A6 \
  --runtime codex \
  --task "檢查最近報價流程並產手機可讀驗證報告" \
  --output /tmp/maplab-a6-handoff.md
```

### 印到 terminal

```bash
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role B2 \
  --runtime codex \
  --task "審查 Investment OS freshness 與資料流"
```

---

## 4. 產生器會讀什麼

```text
chrome-extension/task-modules/index.json
chrome-extension/task-modules/{ROLE}.json
recalls/{ROLE}_recall.md
CURRENT_STATUS.md
SYSTEM_DIRECTORY_INDEX.md
workbook/system_index/system_relation_index.csv
```

它會將以下內容組成一份 runtime handoff：

- 選中的角色與部門。
- Runtime 使用邊界。
- 角色 module 的 read-first sources。
- 本角色所有 relation index matching rows。
- 使用部門／角色。
- upstream／downstream。
- Drive operational sources。
- credential routes。
- related tasks／loops。
- sensitivity。
- role recall。
- output contract。
- forbidden actions。
- verification requirements。
- Startup Check。
- What／So What／Now What。
- Index Loop Back。

---

## 5. 自動選角邏輯

產生器依任務關鍵字評分。

### MAPLAB

| 任務類型 | 預設角色 |
|---|---|
| 跨系統調度、Owner 全局協調 | A0 |
| 系統治理、repo、Extension、索引、關聯、debug | A1 |
| SEO、WordPress、GSC、關鍵字 | A2 |
| Meta／Google Ads、社群、GTM／Pixel | A3 |
| 照片、素材、ALT、相簿 | A4 |
| 報價、菜單、Items、成本、毛利 | A5 |
| 業務急件、Telegram、casequote | A6 |
| LINE 客服、FAQ、補問、轉單 | A7 |
| 影片、Reels、Shorts | A8 |

### Investment OS

| 任務類型 | 預設角色 |
|---|---|
| 寫功能、修 bug、接 runtime | B1 |
| 資料流、錯誤、freshness、證據審查 | B2 |
| 版本、交接、resume、存檔 | B3 |
| 是否繼續、暫停、縮小、重構 | B4 |
| Recall 品質、蒸餾、教材 | B5 |
| 動能 | IOS-MOMENTUM |
| KOL | IOS-KOL |
| FB 社群情報 | IOS-FB |
| 跨來源共振 | IOS-ALPHA |
| 黑天鵝 | IOS-BLACKSWAN |
| 真實持倉 | IOS-INVENTORY |
| 總經 | IOS-MACRO |
| 籌碼 | IOS-CHIP |
| 左側預期差 | IOS-LEFT |
| 右側執行 | IOS-RIGHT |
| 研究證據 | IOS-EVIDENCE |
| 模擬倉 | IOS-SIM |
| 家族基金 | IOS-FAMILY |
| 對沖 | IOS-HEDGE |
| 介面契約 | IOS-SURFACE |
| 系統衛生 | IOS-HYGIENE |

沒有匹配時，預設交給 B4 判斷是否值得建造；若 B4 不在 module index，fallback A1。

---

## 6. 正確啟動行為

Remote Codex 讀取 handoff 後應：

1. 回報 `Remote Role Launch`。
2. 讀 `SYSTEM_DIRECTORY_INDEX.md`。
3. 用 role ID 篩選 relation CSV。
4. 讀該角色 upstream、downstream、credentials、incidents。
5. 讀 module read-first sources。
6. 輸出 Startup Check。
7. 任務清楚、沒有高風險 blocker 時直接執行。
8. 驗證。
9. 寫 review bundle／Task Card／handoff。
10. 輸出 Index Loop Back。

不應：

- 只輸出建議 Prompt 後停止。
- 要求 Owner 再貼已有的檔案 URL。
- 只讀角色 recall 而不讀全局與關聯。
- 自己默默換角色。
- 把 generated index 當 live truth。

---

## 7. 召喚品質驗收

每次召喚至少檢查：

```text
role selected
module loaded
relation rows loaded
canonical sources identified
upstream identified
downstream identified
Drive sources identified
credential routes identified
sensitivity applied
Startup Check completed
execution started
verification receipt saved
Loop Back completed
```

其中任何一項缺失，都屬部分啟動，不算角色已跑起來。

---

## 8. 四個 Smoke Test

### Test A：A6 報價

```bash
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role AUTO --runtime codex \
  --task "A6 報價後沒有寫入 REVISION_LOG，找根因並驗證" \
  --output /tmp/test-a6.md --explain-route
```

應選 A5、A6、B1 或 B2 中合理主責；若選 B1／B2，handoff 必須列 A5／A6／A7 與核心 Sheet 關聯。

### Test B：SEO 案例

```bash
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role AUTO --runtime codex \
  --task "從 Drive 找企業開幕案例素材，規劃 SEO 與社群使用" \
  --output /tmp/test-a2.md --explain-route
```

應選 A2 或 A3；handoff 必須包含 A4 素材 upstream 與外燴案例 Drive source。

### Test C：Investment OS freshness

```bash
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role AUTO --runtime codex \
  --task "審查 IOS-LEFT 與 IOS-RIGHT 是否停更及下游影響" \
  --output /tmp/test-b2.md --explain-route
```

應選 B2、B4、IOS-LEFT 或 IOS-RIGHT 中合理角色；必須讀 CURRENT_STATE 與 Investment Decision Loop。

### Test D：全局治理

```bash
python3 tools/ai_workbook/build_remote_role_handoff.py \
  --role AUTO --runtime codex \
  --task "建立冷啟動全局索引並接入 Extension 與 Remote Codex" \
  --output /tmp/test-a1.md --explain-route
```

應選 A1；必須包含 system directory、relation index、module index、startup protocol。

---

## 9. 如何接回 Chrome Extension

本產生器與 Extension 使用同一組：

```text
chrome-extension/task-modules/index.json
chrome-extension/task-modules/{role}.json
recalls/{role}_recall.md
CURRENT_STATUS.md
```

下一階段應讓 `popup.js buildModuleHandoff()` 加入：

- `SYSTEM_DIRECTORY_INDEX.md`
- `workbook/system_index/system_relation_index.csv`
- `skills/system-directory-index/SKILL.md`
- role matching relation rows
- Drive／credential／incident summary

這樣 GUI Extension 與 Remote Codex 產生的 handoff 才會一致。

在 module builder 尚未更新前，Remote launcher 是 file-backed fallback，不要求 Owner 代替 Agent 操作 Extension UI。

---

## 10. 故障處理

### Module 不存在

- 檢查 `chrome-extension/task-modules/index.json`。
- 再檢查 `chrome-extension/task-modules/{ROLE}.json`。
- 若 B5 或新角色檔案存在但 index 缺失，標 `module_index_drift`。

### Module source hash 過期

- handoff 的 read-first source 標記為 `stale_hash`。
- 仍以 linked Markdown／JSON live source 執行，不把舊 module envelope 當成現況。
- 由 A1 另行執行 `python3 tools/ai_workbook/build_extension_task_modules.py` 並審查 diff；launcher 不自行重建治理來源。

### Relation rows 為空

- 標記 `relation_index_gap=true`。
- 仍可用 module read-first sources 啟動。
- 在 review bundle 提出 relation update，不要直接猜關聯。

### Drive 無法連線

- 標記 `drive_live_access=false`。
- 只使用已知 Drive ID 作候選路徑。
- 不宣稱已確認最新 Drive 內容。

### Runtime 不可用

- 降級為 review／handoff，不宣稱修改或驗證完成。

### 工作樹有 dirty changes

- 不 reset、不清除。
- 先追需求來源與可用性。
- 本任務只修改 scope 內檔案。

---

## 11. 複利 Loop

```text
任務輸入
→ 自動選角
→ 載入全貌與關聯
→ 直接執行
→ 驗證
→ 回寫證據
→ 更新關聯／incident／skill
→ 下一次召喚讀到改進
```

完成後必問：

- 下次還要 Owner 告訴 Agent 資料在哪裡嗎？
- 角色選擇是否更準？
- 關聯是否更完整？
- 同類問題是否已有 prevention？
- 啟動到執行時間是否下降？

若沒有改善，這次只算完成任務，不算 Loop Engineering 成熟。
