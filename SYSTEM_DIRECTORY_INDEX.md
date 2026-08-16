# MAPLAB 全局目錄索引大全

> 版本：v0.1
> 日期：2026-07-18
> 狀態：可直接使用的人工基線；後續應由程式掃描正式來源後重建
> 適用：A0–A8、B1–B5、Investment OS 各 IOS 角色、Codex、Claude、Gemini、OpenClaw、Hermes、Remote worker

---

## 0. 目的

這份索引不是新資料庫，也不是新的狀態真相源。

它是所有 Agent 共用的導航入口，回答：

1. 資料在哪裡？
2. 哪一份是正式來源？
3. 哪些部門／角色用得到？
4. 上下游關聯是什麼？
5. 是否新鮮、已驗證、可使用？
6. 缺權限時去哪裡查安全路由？
7. 相同問題以前是否發生過？
8. 下一步由誰處理、誰驗證、結果寫回哪裡？

企業文化對應：

- 凡保存，必可被找到。
- 凡重複，必產生預防。
- 凡索引，必可重建。
- Owner 只處理高價值判斷與不可逆批准，不負責替 Agent 找資料或重建上下文。

---

# 1. 冷啟動強制讀取順序

所有角色冷啟動時，除了角色既有必讀文件，必須追加：

1. `SYSTEM_DIRECTORY_INDEX.md`
2. `workbook/system_index/system_relation_index.csv`
3. `skills/system-directory-index/SKILL.md`

冷啟動輸出必須增加：

```text
Directory Index Check
- Current role:
- Department:
- Sources relevant to this task:
- Upstream dependencies:
- Downstream consumers:
- Drive operational sources:
- Credential routes:
- Related incidents / pitfalls:
- Files excluded for privacy:
- Planned writeback:
```

## 1.1 冷啟動判斷規則

- 先依「使用部門／角色」欄位找候選資料。
- 再依「正式性」判斷 GitHub、Drive、Runtime 哪一個是該問題的真相。
- 再讀關聯表，確認上游、下游與受影響角色。
- 再查 incident／pitfall，避免重複診斷。
- 找不到時才能擴大搜尋，不得先問 Owner 檔案在哪裡。

---

# 2. 三種真相來源

| 真相類型 | 回答什麼 | 優先來源 | 主要使用部門／角色 |
|---|---|---|---|
| 治理與版本真相 | 現行規則、角色邊界、任務進度、決策與驗證 | GitHub | A0、A1、B1–B5、所有開發／治理角色 |
| 營運資料真相 | 客戶案件、報價、訂單、LINE、素材、營運 Sheet | Google Drive／Sheets | A2–A8、A0、A1、IOS-KOL／FB／EVIDENCE |
| 即時運行真相 | bot、launchd、OAuth、SQLite、GAS、broker、OpenClaw 是否真的在線 | Runtime readback | A1、B1、B2、B4、IOS-SURFACE、IOS-HYGIENE |

衝突時：

1. live API／UI／runtime readback
2. runtime log／SQLite／process status
3. 最新 validation report／review bundle
4. CURRENT_STATUS／CURRENT_STATE／Task Card
5. 舊文件、Drive mirror、記憶

---

# 3. GitHub 全局目錄

## 3.1 治理與方向

| 資料／需求 | 正式位置 | 正式性 | 什麼部門／角色用得到 | 關聯／注意事項 |
|---|---|---|---|---|
| MAPLAB 最新狀態 | `CURRENT_STATUS.md` | canonical governance | A0、A1、A2–A8、B1–B5、所有 runtime | 與 Task Card 衝突時標記 drift |
| Investment OS 最新狀態 | `page1010/investment-os/CURRENT_STATE.md` | canonical runtime state | B1–B5、所有 IOS 角色、A0、A1 | 不用 handbook 舊快照代替 |
| 企業文化 | `docs/company-values.md` | canonical governance | 全角色 | 冷啟動必讀 |
| 全域行為準則 | `AGENT_RULES.md` | canonical governance | 全角色 | 與其他規則衝突時必回報 |
| 冷啟動 SOP | `AGENT_STARTUP_PROTOCOL.md` | canonical procedure | 全角色 | 加載本索引、關聯表與技能 |
| 系統方向 | `docs/fable5-direction-and-guidance.md` | canonical direction | A0、A1、B4、B5 | 決定優先序，不取代 live state |
| 系統全貌快照 | `docs/system-panorama-2026-07-12.md` | dated snapshot | A0、A1、B4、Remote worker | 只能當歷史基線 |
| 使用者價值量尺 | `projects/investment-os-value-definition.md` | canonical product intent | B1–B5、IOS 角色、A0、A1 | Investment OS 功能優先級量尺 |
| Owner 需求紀錄 | `workbook/owner_requirements_panel.md` | governance receipt | A0、A1、B3、B5 | 若近期未更新，需標 stale |

## 3.2 任務、交接與證據

| 資料／需求 | 正式位置 | 正式性 | 什麼部門／角色用得到 | 關聯／注意事項 |
|---|---|---|---|---|
| 任務卡 | `handoff/tasks/` | canonical task handoff | 所有角色 | 最後活動、接續點、blocker、驗收 |
| 任務索引 | `workbook/task_index.json` | generated index | A0、A1、B3、Chrome Extension | 與 Task Card 數量不符時視為 stale |
| 任務佇列 | `TASK_QUEUE.md` | proposal queue | A0、A1、B4 | 未進正式 Task Card 的候選 |
| A0／A1 briefing | `handoff/a0-briefing.md`、`handoff/a1-briefing.md` | durable handoff | A0、A1 | Owner 校正與 session 交接 |
| Session log | `handoff/sessions/` | evidence history | A0、A1、接手角色 | 先讀實際發生，再讀 code |
| Review bundles | `workbook/reviews/JOB-*/` | evidence package | B1、B2、B3、B4、A1、Owner | 原始輸出、測試、validation、review request |
| 踩坑／incident | `pitfalls.md`、`skills/experience-log.md` | durable learning | 全角色 | 相同問題先查，不得從零診斷 |
| 決策紀錄 | `decisions.md` 與專案 decision logs | durable decision | A0、A1、B3、B4 | 保留理由、失效條件、替代方案 |

## 3.3 角色、召喚與技能

| 資料／需求 | 正式位置 | 正式性 | 什麼部門／角色用得到 | 關聯／注意事項 |
|---|---|---|---|---|
| 完整角色 Prompt | `AGENT_RECALL_PROMPTS.md` | canonical recall source | 全角色、Extension、Remote worker | 不應塞入過期動態狀態 |
| 獨立 Recall | `recalls/` | role entry | 對應角色 | 需檢查新鮮度與重複檔 |
| 動態角色索引 | `chrome-extension/task-modules/index.json` | generated runtime index | A0、A1、Chrome Extension、Codex、Gemini、OpenClaw | 缺 B5／新模組時標記 drift |
| 角色 Module | `chrome-extension/task-modules/*.json` | generated routing envelope | 對應角色、runtime | 來源 hash 不同即 stale |
| 角色關聯圖 | `workbook/task_modules/role_module_relation_graph.json` | generated relation view | A0、A1、B3、B4、Extension | 不得當唯一真相 |
| 技能總路由 | `skills/superpowers-guide.md` | canonical skill router | 全角色 | 新動作前重查 |
| 任務進度技能 | `skills/task-progress-guide.md` | canonical skill | 全角色 | Progress Log、Resume、checkpoint |
| Session 技能 | `skills/session-lifecycle/SKILL.md` | canonical skill | 全角色 | session 開關與資源衛生 |
| Codex／agy 路由 | `skills/codex-offload-guide.md` | tool routing guide | A0、A1、A6、B1、B5 | 需依實際版本更新 |
| Credential 指南 | `skills/credentials/` | credential route reference | A0、A1、A2–A7、IOS-FB／KOL | 只能存路徑與 scope，不存 secret |
| 本索引技能 | `skills/system-directory-index/SKILL.md` | navigation skill | 全角色 | 冷啟動追加讀取 |

---

# 4. Google Drive／Sheets 目錄

## 4.1 MAPLAB_DATA 營運核心

Drive 搜尋名稱：`MAPLAB_DATA`

| Drive 資料 | 類型／正式性 | 什麼部門／角色用得到 | GitHub 關聯 | 注意事項 |
|---|---|---|---|---|
| `MAPLAB_外燴系統_v0.1` | operational live Sheet | A0、A1、A5、A6、A7、B2 | `projects/line-quote-assistant.md`、A5/A6/A7 skills、v6 architecture | Items／SALES_INTAKE／REVISION_LOG／CONVERSATION_LOG／QUOTE_WORKBENCH 等 live data |
| `MAPLAB_報價單` | operational output folder | A5、A6、A7、Mina、Owner | A5 quotation skills、A6 task card | 需區分正式、測試、歷史報價 |
| `MAPLAB_Proposals` | operational proposal folder | A5、A6、A3、Owner | Proposal scripts／templates | 不把多個版本視為同一正式檔 |
| `MAPLAB_Items_Photos` | operational asset source | A4、A5、A6、A8 | Items K 欄、A4 pipeline | 圖片與 Items 關聯屬高風險 |
| `ai_reply_system` | customer-service working data | A7、A6、A5 | `projects/ai-reply-system.md`、A7 skills | 客戶資料需去識別化 |
| `line_oa_chat_csv` | customer conversation source | A7、A6、B2、B5 | A6/A7 task cards | 不得將原始個資送進公開模型輸出 |
| `📋 進行中_Active Orders` | operational live cases | A5、A6、A7、Owner | SALES_INTAKE／Task Card | Cashflow Loop 上游 |
| `✅ 已結案_Completed Orders` | historical outcomes | A5、A6、A7、B5、A2、A3 | REVISION_LOG、案例內容 | 用於成交與覆盤 |
| `❌ 未成交_Lost Quotes` | historical outcomes | A5、A6、A7、B5、A3 | REVISION_LOG、漏斗分析 | 用於未成交原因複利 |
| `IOS-KOL_Industry_Briefs` | research operational source | IOS-KOL、IOS-EVIDENCE、B2 | KOL task cards | 需標 freshness |

## 4.2 真實外燴案例素材

Drive 搜尋名稱：`2026maplab外燴紀錄`

| 使用情境 | 什麼部門／角色用得到 | 查找方式 | 安全邊界 |
|---|---|---|---|
| SEO 案例文章 | A2 | 日期＋活動類型＋場地／品牌 | 先確認可公開資訊 |
| 廣告／社群素材 | A3 | 活動類型＋成效／品牌 | 不暴露客戶聯絡資訊 |
| 圖片分類／ALT | A4 | 資料夾 metadata＋圖片批次 | 一般索引只讀 metadata |
| 短影音 | A8 | 案例資料夾＋已選素材 | 不全量餵模型 |
| 報價與案例對照 | A5、A6、A7 | 案件名稱＋日期 | 客戶資料去識別化 |
| 能力蒸餾 | B5 | 成功／失敗案例摘要 | 只保存模式，不保存個資 |

## 4.3 Investment OS Drive

Drive 搜尋名稱：`Investment OS`

| Drive 資料 | 類型／正式性 | 什麼部門／角色用得到 | GitHub 關聯 | 注意事項 |
|---|---|---|---|---|
| `windows_agent_bridge` | operational evidence inbox | WIN、B2、IOS-EVIDENCE | WIN module／bridge docs | Windows UI 證據需 Mac 端交叉驗證 |
| `FB Radar` | operational research source | IOS-FB、IOS-ALPHA、IOS-EVIDENCE、B2 | IOS-FB module／task | 登入與 freshness 必須顯示 |
| B-role `.md` 複本 | GitHub mirror candidate | B1–B5、Remote worker | 對應 GitHub projects／skills | 預設 GitHub 為治理真相 |
| question packs／evidence prompts | working／generated output | IOS-LEFT、IOS-EVIDENCE、OpenClaw、B2 | review bundles／research tasks | 需以日期、freshness、來源分類 |
| HTML panel／dashboard copy | generated output | IOS-SURFACE、B1、Owner | GitHub dashboard source | 不以 Drive 複本判斷 runtime 是否在線 |

## 4.4 Drive 根目錄重要入口

| Drive 資料 | 什麼部門／角色用得到 | 建議分類 |
|---|---|---|
| `OWNER_INBOX A0手機協作區` | Owner、A0、A1、B3 | owner_inbox／handoff |
| `A6回覆訓練` | A6、A7、B2、B5 | customer-service training |
| `A2 Ads & SEO Patrol Matrix (MAPLAB)` | A2、A3、A1 | marketing operational data |
| `MAPLAB_Roles_任務分派.docx` | Owner、A0、A1 | generated／mobile copy; GitHub modules 優先 |
| `sj-trading` | B1、B2、IOS-SIM、IOS-INVENTORY | investment runtime data |
| `股市用` | Owner、IOS roles | investment working data; 需再分類 |
| `永豐自動下單用資料` | B1、B2、IOS-SIM | financial／restricted |

---

# 5. 部門／角色 → 必讀資料反向索引

## A0 總調度秘書

- `CURRENT_STATUS.md`
- `SYSTEM_DIRECTORY_INDEX.md`
- 關聯表 CSV
- `handoff/a0-briefing.md`
- `workbook/owner_requirements_panel.md`
- `dependency-map.md`
- `skills/a0-proactive-dispatch-guide.md`
- Drive：`OWNER_INBOX A0手機協作區`、MAPLAB_DATA metadata

## A1 系統總管

- 全局治理文件
- Task Cards、task index、relation graph
- Review bundles、pitfalls、decisions
- Drive operational source metadata
- Runtime readback、credential routes

## A2 SEO／搜尋流量

- SEO project／skills／Task Cards
- A3 landing／ads 關係
- A4 assets
- Drive：外燴案例、A2 Patrol Matrix、GSC exports
- Credential：WordPress、GSC、Google Ads

## A3 社群／廣告

- A2 landing pages、A4 assets、A5/A7 FAQ／conversion insight
- Drive：外燴案例、廣告策略、素材
- Credential：Meta／Google Ads／GTM

## A4 影像資產

- Drive：外燴案例、Items Photos、ASSET_LOG
- GitHub：photo pipeline、visual spec、A4 Task Cards
- 下游：A2、A3、A5、A6、A8

## A5 報價引擎

- Drive：核心 Sheet、Items、報價單、Proposals、訂單資料夾
- GitHub：master data、quotation skills、Task Cards
- 下游：A6、A7、Slides／GAS

## A6 業務快反應

- Drive：A6 回覆訓練、核心 Sheet、LINE cases、報價單
- GitHub：A6 task card、quote SOP、Codex routing
- 上游：A5、A4、A7

## A7 客服

- Drive：LINE CSV、ai_reply_system、A6 回覆訓練、訂單結果
- GitHub：A7 templates、AI reply project、Task Cards
- 下游：A5、A6、A2、A3

## A8 影音

- Drive：外燴案例、Mina 精修素材、Items Photos
- GitHub：A8 skills／Task Card
- 上游：A2、A3、A4

## B1 Builder

- MAPLAB handbook governance
- Investment OS runtime repo state／code／tests
- Drive operational evidence only when task requires
- B2 review request、B3 archive、B4 scope decision

## B2 Reviewer

- Runtime evidence、Drive operational data、GitHub contracts
- freshness、source separation、error、owner-facing surface

## B3 Archivist

- Task Cards、review bundles、decisions、pitfalls、Owner requirements
- 本索引與關聯表更新建議

## B4 System Patrol

- CURRENT_STATUS／CURRENT_STATE
- relation graph、stale reports、owner actions、loop outcomes
- 檢查過度建置與索引腐化

## B5 Shadow Distillation

- Owner decisions、review bundles、pitfalls、成功／失敗案例
- Recall freshness、skill 更新、教材包
- 不保存客戶個資與 secret

---

# 6. Credential 路由索引

Credential 路由只記：

- 服務名稱
- 需要的 scope
- 允許角色
- credential guide path
- 可用 runtime
- 最後驗證時間
- status
- fallback
- Owner 最小動作

禁止記：密碼、token、cookie、OTP、API key value。

| 服務 | 指南位置 | 什麼部門／角色用得到 | 主要風險 |
|---|---|---|---|
| Google Drive／Sheets | `skills/credentials/google-drive-api.md`、`google-sheets-api.md` | A0、A1、A4、A5、A6、A7、IOS roles | OAuth 單點故障 |
| WordPress | `skills/wp-credential-chrome-login/SKILL.md` 等 | A2、A1 | 發布需批准；不能把 password 寫入 repo |
| Social accounts | `skills/credentials/social-accounts.md` | A2、A3、IOS-FB | 缺登入不得用舊 corpus 假裝 live report |
| Notion | `skills/credentials/notion-api.md` | A0、A1、B3 | Notion 不作狀態真相 |
| Google Ads | `skills/credentials/google-ads-api.md` | A2、A3、A1 | 預算與投放更動需批准 |
| LINE／GAS | 對應 credential skills／Task Cards | A1、A5、A6、A7 | 不在 prompt 或 log 暴露 secret |
| Shioaji／broker | Investment OS local env／security docs | B1、B2、IOS-INVENTORY、IOS-SIM | 真實資金動作需明確批准 |

---

# 7. 關聯表使用方式

關聯表位置：

`workbook/system_index/system_relation_index.csv`

每一列至少包含：

```text
source_id,source_type,title,path_or_id,canonical_status,used_by_departments,used_by_roles,upstream,downstream,related_tasks,related_loops,sensitivity,last_verified,notes
```

Agent 開工前必須：

1. 用自己的 role_id 篩選 `used_by_roles`。
2. 讀全部直接 upstream。
3. 讀會被修改影響的 downstream。
4. 檢查 related_tasks 與 related_loops。
5. 若 sensitivity 不是 public_safe／internal，套用資料最小化原則。

---

# 8. 找資料標準流程

```text
問題
→ 確認部門／角色
→ 查本索引反向索引
→ 查 relation CSV
→ 確認 canonical source
→ 查 Drive metadata 或 GitHub 檔案
→ 查 incident／pitfall
→ 查 live runtime（若問題涉及現在狀態）
→ 回答 What／So What／Now What
→ 執行最小行動
→ 驗證
→ 回寫 Task Card／review bundle／incident
→ 更新或重建索引
→ 再問：下次是否更快、更少 Owner 介入？
```

---

# 9. 複利迴圈

## What

- 發生什麼？
- 是新問題還是 recurrence？
- 哪個來源證明？
- 哪些角色與 loop 受影響？

## So What

- 對營收、決策、風險、使用者時間有何影響？
- 是症狀、根因、權限問題、資料漂移還是治理衝突？
- 是否值得現在處理？

## Now What

- 最小行動是什麼？
- 誰執行、誰驗證？
- 成功條件、停止條件、retry budget 是什麼？
- 寫回哪裡？

## Loop Back

完成後重新檢查：

1. 下一次能否從本索引直接找到？
2. 關聯表是否新增 upstream／downstream？
3. 是否新增 incident／pitfall／skill？
4. 是否降低 Owner 介入？
5. 是否可自動偵測、重試或恢復？
6. 若沒有改善，這次只算止血，不算複利完成。

---

# 10. 目前兩條最高價值 Loop

## MAPLAB Cashflow Loop

```text
LINE／客戶需求
→ A7 分類與補問
→ A5 報價資料
→ A6 手機可讀草稿
→ Mina 確認／修改
→ 正式送出
→ 成交／未成交
→ REVISION_LOG
→ 更新 A5／A7
```

資料來源：核心 Sheet、LINE CSV、報價資料夾、Completed Orders、Lost Quotes、A5/A6/A7 GitHub 文件。

## Investment Decision Loop

```text
資料 freshness
→ 風控閘門
→ Thesis 狀態
→ 左側／右側／籌碼／總經
→ 規則觸發
→ Owner 選項
→ Decision log
→ 結果覆盤
→ 更新規則與 evidence
```

資料來源：Investment OS runtime、GitHub governance、Drive evidence folders、Telegram／Dashboard readback。

---

# 11. 隱私與排除

不經 Owner 明確指定，不讀取內容：

- 護照、簽證、薪資、保險、醫療、家庭與兒童資料。
- 密碼、token、cookie、OTP、API key、`.env`。
- 客戶完整聯絡資訊與原始敏感對話。

可索引 metadata，但標記：

```text
sensitivity=excluded
content_indexable=false
```

---

# 12. 更新責任

| 變更類型 | 應更新的正式來源 | 索引責任 |
|---|---|---|
| 系統狀態 | CURRENT_STATUS／CURRENT_STATE／Task Card | A1、B3 建議重建索引 |
| 新角色／module | Recall、module builder、index | A1、B3、B5 |
| 新 Drive operational source | Drive metadata＋相關 GitHub task | A0、A1、資料擁有部門 |
| 新 credential route | credential skill | A1、安全責任角色 |
| 新 incident | review bundle／pitfall／task card | 執行角色、B2、B3 |
| 關聯變更 | 正式 project／task／source | A1、B3；關聯表重新生成 |

下一版本不得靠人工長期雙寫；應建立掃描器從：

- CURRENT_STATUS
- Task Cards
- Role modules
- Skills／credentials
- Review bundles
- Drive metadata
- Investment OS state

重新生成本索引與關聯表。

---

## 素材資產／本輪發現(2026-07-24)

> 2026-07-24 素材歸檔 + 存檔規範任務的痕跡留檔。此段為人工維護，插入本索引（非跨 repo 自動覆寫的 SYSTEM_MAP.md）。

**素材真相（單一來源）**
- A4 素材索引 = `MAPLAB_ASSET_LOG`（Google Sheet，mina / lb99104@gmail.com 擁有，2026-03-19 共享 Owner）。ID `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`。欄位：file_id/original_name/seo_name/category/keywords/alt_text/drive_url/year。
- `photo_alt_index.csv`（29,258 列，mina 擁有）：`GoogleDrive-lb99104…/我的雲端硬碟/MAPLAB/MAPLAB_ASSETS/_alt_index/photo_alt_index.csv`。
- ⚠️ 關鍵陷阱：ASSET_LOG 的 `category` 只有粗分「外燴/日常/旅遊」，會把婚禮/HR 壓平成外燴。**細分類真相在 CSV 路徑子類別** `年份/catering/{子類別}/`：wedding 333（TA-2 婚禮）、corporate 472（TA-3 HR）、birthday 3,347（TA-1 週歲）、dessert 4,283（甜點桌跨 TA）、other 9,013。**別信 category 欄，以路徑子類別為準。**

**關鍵字主軸（TA = 視圖）**
- `docs/seo-keyword-map.md`（A2 canonical）＝素材分類主軸；三個 TA 是「關鍵字→TA」視圖。pillar：婚禮 `tainan-outdoor-wedding-catering`(1215)、週歲 `catering-one-year-old-party-tainan`(498)、企業茶會 `corporate-tea-party-desserts`(924)。
- `docs/real-cases-to-seo-matrix.md`＝2026 活動事件夾→cluster→關鍵字 對照。

**成果位置**
- 已分類素材（190 張）：`/Volumes/MacExternal/MAPLAB_素材_依TA_20260724/`（TA1_週歲 39、TA2_婚禮、TA3_HR 117）。
- 可用清單（含 drive_url）：`/Volumes/MacExternal/MAPLAB_WORKSPACE/index/`（婚禮 231/333 有連結、企業 183/472 有連結＋原始清單＋schema 草稿）。

**新存檔架構（治理）**
- agent 固定存檔根：`/Volumes/MacExternal/MAPLAB_WORKSPACE/{outputs,state,tools,index}`；規範 `skills/agent-output-convention.md`＋review bundle `handoff/review-bundles/2026-07-24-agent-output-convention/`。

**已知卡點／陷阱（走過的坑）**
1. 實體素材未同步本機（只有 `_alt_index` CSV 有同步）。
2. Drive API `download_file_content` 回 base64 進 context，單張全解析度≈數十萬 token → 大量下載別在主 context 做，優先「離線/鏡像後 cp」或 subagent 批次。
3. Google Drive 桌面版只能整碟鏡像、不能挑單夾。
4. 實體檔名 seo/原始混用 → join 命中率被壓（婚 231/333、企 183/472）；A4 完成 seo-rename 回寫可拉高。
5. 資料夾列檔 400 筆分頁上限 → 大夾要 nextPageToken 補齊。
6. 婚禮無拍攝日期（A4 只有年份+處理時間）→ date-join 走不通，改靠路徑子類別桶分類。
7. Chrome 開 Drive 縮圖會 render 凍結 → 視覺驗證改本機 sips+montage。

**其他本輪事實（痕跡）**
- Ollama 排程：`com.maplab.a6-gym`（LaunchAgent）每天 15:00 跑 `a6_gym_runner.py` 用 `qwen2.5:14b`（~9GB）；工作時段勿 stop。
- 婚禮日期最可靠來源＝mina 訂單 Sheet 標題（2026/6/27、2026/3/6、2025/11/23、2025/9/27、2024/11/2…）；TimeTree 用客戶/場地名（如東門教會），搜「婚禮」無果。
- mina 舊照片共享：`外燴照片（擺設）`140（人工命名事件庫）、`餐點照片`103（純食物，0 婚禮）。
- 外接硬碟 `/Volumes/MacExternal`（1.8T 可寫）；廣告 meta-ads MCP 已接、Meta 帳號 `act_318634712`。
- 分類方法定論：以事件脈絡/A4 路徑桶為主、單張影像辨識為輔（甜點桌跨 TA 撞臉，單圖不可靠）；主軸跟 seo-keyword-map，TA 為視圖，一份素材跨 audience/channel 共用。

**最終素材庫狀態（2026-07-25 更新）**
- 方案 A 已把 A4 路徑桶實體檔 materialize 到本機外接，全程本機處理（sips+montage 驗證、cp），不再走 API base64。
- **最終 TA 可用張數**（`/Volumes/MacExternal/MAPLAB_素材_依TA_20260724/`）：
  - TA1 週歲 **3,154**（抓周/托嬰 39 + birthday 回收 3,115）
  - TA2 婚禮 **308**（證婚 27 + 候選 7 + A4回收 274；**婚禮缺口從 27 補到 308**）
  - TA3 HR **676**（前批 117 + A4回收 559）
  - 甜點桌_跨TA **4,285**（dessert 回收，TA1/2/3 共用池）
  - 合計 **~8,423 張**。
- **截圖/文件排除**：PNG（≈截圖）排除 **1,206 張**；jpg 文件/菜單（檔名 hint）排除 **119 張**，移到各 TA `_A4回收_疑似截圖排除/`。長寬比無法區分真照片直長裁切 vs 截圖，故只靠檔名/OCR。
- **索引（雙檔）**：`MAPLAB_WORKSPACE/index/素材索引_關鍵字主軸.csv`（wedding+corporate 1,086 列）、`…_birthday_dessert.csv`（8,472 列）；欄位含 wp主關鍵字/TA視圖/audience/channels/png-doc 排除旗標/本機路徑。驗證與誤標記錄：`…/index/A4回收_驗證與誤標記錄_2026-07-25.md`。
- **A4 品質坑定論**：路徑子類別分類**可信**（wedding/corporate/birthday/dessert 桶都對）；最大坑＝把 IG/LINE 截圖、報價菜單、ChatGPT 截圖、logo 圖倒進素材桶（**PNG 幾乎全是截圖**）。建議 A4 pipeline 先分「照片 vs 截圖/文件/logo」再進場景桶；`category` 粗欄（外燴/日常/旅遊）該廢，以路徑桶為準。
- **原始庫完整保留**：`MAPLAB_WORKSPACE/index/原始庫_wedding_corporate/`（wedding 393、corporate 693）、`…/原始庫_birthday_dessert/`（birthday 3,459、dessert 5,032），按年份，未刪。
- skill：`skills/photo-asset-retrieval-guide.md`（DRAFT，含能力摘要與大量 Drive 檔落地策略）。

**PNG 修正 + webp 轉檔路線（2026-07-25 更正）**
- ⚠️ 更正：**PNG 不該一律排除**——有些 PNG 是被誤丟的真照片。正解＝走「看到是照片 → (SEO 命名) → 轉 webp」路線（webp 供 WordPress/SEO/IG/YT/Pinterest 多頻道復用）。
- **webp 工具**：`/opt/homebrew/bin/cwebp` 已裝、PIL webp=True。命名慣例 `maplab-{場景}-{描述}.webp`、alt `台南{場景}外燴—{描述}`（見 `recalls/A2_recall.md`§D、`projects/a2-asset-guide.md`）。**repo 無現成 end-to-end「照片→改名→webp」腳本**（既有 `scripts/a4_photo_alt_pipeline.py`/`tools/ai_workbook/photo_pipeline.py` 只做 alt/命名或轉 jpg 上傳）；本輪用等效實作 `outputs/_verify/png_recover.py`（尺寸判截圖 + 白底低飽和判文件 → 真照片轉 webp）。**建議把此步正式化為 A4 pipeline 的一環。**
- **1,206 PNG 重新處理**：依尺寸分「截圖解析度 1,058（多為 1290x2796 iPhone 截圖）」+「候選照片 148」→ 候選再用內容（白底低飽和=文件/菜單）判別 → **救回 93 張真照片轉 webp**（dessert 56、birthday 31、corporate 4、wedding 2），其餘 1,113 留排除（截圖/報價單/LINE/logo/插畫）。webp 放各 TA `A4回收_PNG救回_webp/`；索引 `MAPLAB_WORKSPACE/index/素材索引_PNG救回_webp.csv`（source=png_recovered、format=webp）。
- **更新後 TA 可用**：TA1 週歲 **3,185**、TA2 婚禮 **310**、TA3 HR **680**、甜點桌跨TA **4,341**（合計 ~8,516）。
- **原檔策略**：jpg/heic/png 原檔全保留（原始庫）；webp 為上稿/多頻道格式，發佈時轉、原檔當備份。不因副檔名誤剔真照片。

---

# 版本紀錄

## v0.1 — 2026-07-18

迭代原因：

系統已有大量文件、Drive 資料、角色、Task Cards 與證據，但缺少所有 Agent 共用的導航入口，也缺少「什麼部門／角色用得到」的反向索引，導致每次冷啟動重找資料、重建上下文與重複診斷。

新原則：

1. 每筆索引必須標示使用部門與角色。
2. 冷啟動必須讀目錄索引與關聯表。
3. GitHub、Drive、Runtime 分別承擔治理、營運、即時真相。
4. Drive mirror 不凌駕 GitHub，live Sheet 不被舊 repo note 取代。
5. 找資料後必須回到 What／So What／Now What，再 loop back 檢查是否真的變好。


---

# A6 LINE 資料流與回覆預訓練資產（本輪發現 2026-07-30，DRAFT）

> 只新增，不覆寫既有段落。目的：把「A6 現在 live 在收 LINE 訊息的那條路徑」與「A6 回覆模型的預訓練資產」釘死位置，未來不必重找。
> ⚠️ 關鍵區別：**live 收訊息的 sheet** 與 **預訓練用的歷史匯出** 是**兩個不同的東西**，不可混為一談（見下方 A/B）。

## A. Live LINE 收訊息路徑（webhook 已在運作，客戶→OA 單向）

| 項目 | 內容 |
|---|---|
| Webhook 程式碼 | `scripts/apps-script/LineWebhook.gs`（GAS，`doPost` → LockService + `message.id` 去重 → 直接 `appendRow`，不走 trigger queue） |
| 部署 URL / ID | `https://script.google.com/macros/s/AKfycbz_zA_tG2fxNRlvrRMsJyMAzbnpNC-IL8oKqc5h94kyhExsIOuuo7LujbrSuZGK_eap/exec` |
| LINE Channel | `1654658337`（金鑰在 Notion「MAPLAB API Keys」+ `bot/.env`；不進 git） |
| 落點 Sheet ID | `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg`（Drive 名稱 `MAPLAB_外燴系統_v0.1`；與報價系統同一份試算表） |
| 落點分頁 | `CONVERSATION_LOG` |
| 欄位 | `msg_id, case_id, timestamp, speaker, message, source, line_user_id, reply_to_msg_id`（`case_id` 多數空白，需業務回填） |
| 現況 | 試算表本身 modifiedTime 2026-07-29（但那是 DASHBOARD 分頁自動更新，非 CONVERSATION_LOG）。CONVERSATION_LOG 最後**獨立確認**有 LINE inbound 是 **2026-05-19**（見 CURRENT_STATUS + T-A6-001 驗收）。**⚠️ 未確認今日仍有新 inbound 列**（Drive 全文渲染被大小截斷、只回傳 dashboard 分頁）→ 待直接讀 CONVERSATION_LOG 分頁尾列補證。 |
| 重大限制 | LINE Messaging API webhook **只收得到客戶傳給 OA 的訊息，收不到業務從 OA Manager 後台回的訊息**（根因見 `handoff/tasks/T-A6-002.md`）。這條 live 路徑只有**半邊對話**。 |

## B. 回覆預訓練資產（一次性歷史匯出，靜態，含雙向）

| 項目 | 內容 |
|---|---|
| 原始來源 | `/Volumes/MacExternal/外接硬碟 讀取專用/line_oa_chat_csv_260622_213421/`（LINE OA Manager 對話匯出，3,625 個 CSV；資料夾名時戳 2026-06-22，dir mtime 2026-06-22 = **靜態 dump，非 live**） |
| 產出資料集 | `workbook/a6-training/generated_local/training_samples.jsonl`（run_ts 2026-06-25）+ `manifest.json`（統計）+ `qa_examples_deidentified.json` + `training_pairs_raw.json` |
| 規模 | 20,244 筆 CSV pairs（總監督樣本 20,370；train 16,317 / val 2,037 / test 2,016）；**含業務回覆側**（with_account_target=20,370） |
| 階段標註 | S0_OPENING → S6_PREDAY 銷售漏斗 13 類（S3_QUOTE_SEND 8,415 筆最多；S3_MENU_ADJUST 僅 3 筆＝稀疏） |
| 訂單配對 | `data/line_booking_pairs.csv`（2,634 列，62 筆對到 TimeTree；mtime 2026-06-23；PII 已去識別，另有副本移至 `/Volumes/MacExternal/maplab-data/`） |
| 模型/評估「gym」 | `scripts/a6_gym_runner.py`（Ollama `qwen2.5:14b` 產建議回覆 vs 真實員工回覆，算可用率）；排程 `launchd/com.maplab.a6-gym.plist`；log `state/a6_gym_log.jsonl` + `state/a6_gym_stdout.log` |
| ⚠️ 可用率現況（誠實） | gym log 實測每輪可用率約 **0%–20%**（啟發式評分器），**不是 8 成**。repo 裡的「80%」是 A5 報價**毛利率**，非模型回覆準確率。Owner 記憶中的「~8 成可用模型」目前**在 gym 評估裡查無實證**，需再確認是指哪個指標/哪次結果。 |
| 相關 skill/doc | `projects/line-conversation-training.md`、`projects/ai-reply-system.md`、`skills/a6-local-quote-model-tuning.md`、`skills/a6-qa-examples.md`、`skills/a6-telegram-window.md`（業務輸入視窗操作手冊）、`bot_a6/`（線上 A6 bot）、`local_model_evolution/`（模型演化骨架，2026-07-19 remote 跑因無 Ollama runtime 標 baseline blocked） |

## A vs B 結論

- **A（live 收訊息）** 和 **B（預訓練資料）** 是兩個不同的東西：B 來自 2026-06-22 的靜態 CSV 匯出，**不是**從 live sheet 流出來的。
- Owner 推論「在 sheet 就代表 webhook 接好了」需拆開看：預訓練 pairs 不在 live sheet；而 live sheet（CONVERSATION_LOG）就算在寫，也只有客戶單向那半邊。
- 閉環要吃 live 流時：可用 A 拿到客戶訊息，但**業務採用/修改後的回覆（校正訊號）目前沒有任何 live 路徑在捕捉**——這正是新「業務輸入視窗 app」要補的缺口。

---

# 工具與帳號能力清單（Capability Registry · v1.0 · 2026-08-15）

> 指向性導覽：只寫「有什麼、怎麼取用」，**零帳密、零檔案路徑、零 vault page id**。
> 取用一律透過技能介面（技能內部才解析路徑/憑證/登入態）。消費端呼叫技能即可，拿不到也不需要原始路徑。

| 能力 / 帳號 | 是什麼 | 狀態 | 透過哪個技能取用 |
|-------------|--------|------|------------------|
| agent 專用 FB 帳號 | 供 agent 穿越 FB 登入牆做唯讀收集的專用身分（非 Owner 個人帳號） | ✅ 已建、憑證在保管室（僅遮罩顯示） | `agent-login`（不寫帳密） |
| FB Radar / KOL 情報 feed | 登入態下抓 ~20 財經 KOL 第一手貼文；**接解讀層（playbook/持股情報），非搶快交易** | ✅ 程式在／⏳ 登入 session 待重登 | `agent-login`（登入態）→ FB Radar 流程 |
| quota-meter | 讀 Claude 方案用量（週 + 5 小時窗），寫預算閘給 daily-ops | ✅ 可用 | `quota-meter` |
| A8 音樂（MiniMax / Suno） | A8 影音產線的配樂 / 音樂生成 | ⏳ 帳號待指定 | `agent-login`（登入）+ `a8-video-pipeline` / `a8-local-motion-integration` |
| agent-login | 登入牆穿越的統一介面（`open` / `get-cred`）；唯讀 + 注入防禦 | ✅ v1.1 | `agent-login` |
| arb 引擎 / rr_framework | investment-os 的套利 / 風報比框架（參考、非執行） | 參考層 · **無獨立技能封裝** | investment-os runtime 內模組（`investment-os/skills/` 目前無對應獨立技能 → 建議後續封裝） |
| 處置雷達 | 處置股 / 風險標的偵測 | 參考層 · **無獨立技能封裝** | investment-os runtime 內模組（同上，尚未封裝成技能 → 建議後續封裝） |
| daily-ops cycles | 每日營運循環（預算閘、巡查、狀態回寫） | ✅ 運行中 | daily-operations 循環 / 技能 |

**規則**：本清單只指向「用哪個技能」。任何人（或 agent）需要實際帳密 / 路徑 / 登入態時，呼叫對應技能，由技能內部解析——**導覽頁與其他文件不再寫死 vault id 或檔案路徑**。狀態標「待確認」者表示尚未核對到確切技能名，屬誠實標示、待補。
