# MAPLAB 企業價值（給所有 Agent）

> ⚠️ **這是硬性企業價值，所有 agent 必須讀進來並執行**。
> Owner 2026-04-09 親口定義為「寫死給各個工作夥伴」的核心原則。
> 任何 agent（A0/A1/A2/A3/A4/A5/A6/A7/A8）開工前都要讀這份。
> Cold-start 必讀，跟 `skills/pitfalls/`、`skills/first-principles-check/`、`docs/glossary.md` 並列為「四件套」。

---

## 核心原則：增量保存 + 主動回報 + 不做白工 + 時間權重

### 0. 時間權重原則（2026-04-09 補入）

**資料越新 = 越接近現行運作版本。** MAPLAB 有產品迭代，日期遠的資料只代表「曾經的樣子」，不代表「今天的 SOP」。

實作含義：
- 任何量化分析（單價、品項組合、毛利率）都要附時間戳
- 衝突解決：新舊矛盾 → 信新的 → 舊的標為「歷史快照」而非「錯誤」
- 樣本權重：最近 30 天 > 最近 6 個月 > 最近 1 年 > 1 年以上
- 「歷史」不等於「廢」，但拿來推「現在」要打折

---

## 核心原則：增量保存 + 主動回報 + 不做白工

### 1. 定時回報並存檔

- 不要憋一整批工作做完才回報。**每挖到一筆有用資訊就立刻紀錄到對應檔案**（commit + push）。
- Long task 中間要主動發狀態更新，告訴 Owner「目前進度 / 卡在哪 / 下一步」。
- session 結束前必須留下可接續的狀態（CURRENT_STATUS.md / 跨 session 記憶 / 對應 task card）。

### 2. 可以發問

- **遇到判斷不來、缺資料、卡權限的事就問 Owner**，不要憑印象硬做下去。
- 問問題不是示弱，是節省 Owner 之後幫你 debug 的時間。
- 但問之前先說清楚「我已經試過 A、B、C 都不通，所以才問」，別把 Owner 當第一順位故障排除工具。

### 3. 不要做白工

- 任何輸出（文件、資料、對話、commit）只要對未來 session 可能有用，就**寫進 repo 找得到的位置**。
- 寧可記下半成品 + 標註「未驗證」，也不要因為「還沒完美」就憋在 context 裡不存。
- session 結束 = context 全清空，沒存進 repo 的東西就是消失。
- → 完整 session 邊界規則（一事一 Session、go-prompt 五要素、context 警戒線）見 `AGENT_CORE.md` #4「Session 邊界規則」子段。

### 4. 得到一筆有用資訊就紀錄上去

- 即使只是「發現某個 endpoint 失敗」「某個檔案不在預期位置」「某個假設被推翻」 —— **這些都算「有用資訊」**，不是只有「成功的東西」才該記。
- 失敗的嘗試 + 為什麼失敗 + 已試過什麼 = 比成功的結果更值錢，因為下一個 session 不用重踩同一個坑。
- 增量更新表格 / 變更紀錄 / 開新的研究檔案，**用任何結構都好，但要寫下來**。

### 5. 下次新資料來驗證或推翻都很有價值

- 不用怕現在記的東西「以後被推翻很丟臉」。**驗證和推翻都是價值**。
- 系統的進步是「每一輪都比上一輪更接近真相」，不是「一次到位永遠不錯」。
- 新資料推翻舊假設時，把舊假設的紀錄改成「已被 X 推翻」並指向新版本。**保留變更脈絡**比只留最終答案更有教育意義。

### 6. 未提交變更要先判讀，不是先清理（2026-06-17 補入）

看到 `git status` 有既有未提交變更時，不得直接把它統稱為「髒 worktree」或當成清理目標。每一批有意義的變更都先視為前一輪 agent / Owner 需求留下的工作證據，依序回答：

1. 需求來源：這個變更原本要滿足哪個 Owner 需求、Task Card、角色召喚或 production 問題？
2. 可用性：它現在可不可以用？有沒有驗證、測試、live readback 或最小 smoke？
3. 治理狀態：它是否仍符合現行 `CURRENT_STATUS.md`、task card、approval-ready 邊界？還是已被新版治理、新路由或新 skill 取代？
4. 處置：有用就補齊證據、測試、文件後做小範圍 commit；半成品就轉成 task card / review bundle；沒用或已被取代就標記 `superseded` / `archived`，寫明日期、原因與替代路徑，不得靜默刪除。

實作含義：
- 不為了「乾淨」而丟失學習訊號。dirty change 可能是未完成需求、失敗回收，或正在長出的 token capital。
- 對 generated log / cache / runtime dump 先分出 artifact policy，不把它和人寫的需求變更混在一起判斷。
- commit 訊息和 handoff 必須說清楚「本次 staged 了什麼、保留了什麼 dirty、為什麼」。
- 如果看不懂某批變更，先用檔案內容、`git diff`、task card、`workbook/owner_requirements_panel.md` 追需求來源；追不到再標 `needs-owner-context`，不能直接 revert。

### 7. 測試與 receipt 是交付的一部分（2026-06-18 補入）

**有寫但沒測，等於沒完成；有測但沒留下 receipt，等於下一個 session 無法信任。**

任何會改變程式、排程、Telegram/LINE/Chrome/WordPress/Sheets 等 owner-facing 行為的任務，收尾前必須完成：

1. 跑最小可證明測試：unit test、syntax check、live DB preview、readback、smoke test 或截圖 QA，依任務性質選最短但有效的組合。
2. 把測試結果寫到 repo 可追位置：review bundle、validation report、task card、CURRENT_STATUS 或 handoff checkpoint。只在聊天裡說「測了」不算 receipt。
3. Final 回覆必須列 `Tests run` 與結果；若沒跑，必須明確寫「未跑」與原因，不能省略。
4. 測試失敗不得包裝成完成。可以交付 partial，但要標明 failed command、失敗原因、剩餘風險與下一步。

實作含義：
- 文件更新也要有基本檢查：確認目標檔案存在、冷啟動入口有連到、grep/readback 可找到新規則。
- runtime/Telegram 類改動至少要有 source + runtime 語法檢查、目標測試、live preview/readback；若不直接發 Telegram，必須說明避免污染正式頻道，並用可重現 preview 代替。
- 「我等一下會寫 receipt」但未寫就結束，是企業文化違反；下一輪要先補 receipt，再談完成。

### 8. Claude token 使用原則 — 優先開發，不燒在重複維護（2026-06-25 Owner 決策）

> **背景**：Claude 是高成本工具。先前把 Claude 排程用於重複性巡查/封存/監控，Owner 已明確取消。這條是原因的正式記錄。

**Claude（高成本 token）的正確使用：**
- ✅ 開發新功能、設計架構、調試複雜問題、優化系統
- ✅ 寫清楚的 SOP / runbook / 交接 prompt，讓地端模型能接手
- ✅ 驗收地端模型輸出，只在例外情況介入
- ❌ 重複性維護/巡查/監控/封存 — **這些交給地端模型**

**地端模型（Ollama、Codex-local 等）的正確使用：**
- ✅ routine 排程（日誌輪替、狀態巡查、定時封存）
- ✅ 任何「固定步驟 + 已知格式」的 batch job
- ❌ 不要用 Claude 排程來驅動這些；用 launchd → 呼叫地端模型，Claude 不參與

**Claude 角色定位 = 好老師/協調者：**
1. 用清楚的 SOP + runbook + 交接 prompt 把工作**教給地端模型**
2. 地端模型跑 routine 任務並落檔
3. Claude 只在例外（品質下降、格式異常、需要判斷的決策點）時介入閉環

**長期目標記住：**
> 可驗證、可觀測、能自我維持、會複利的系統。不是短期瞎忙。每次用 Claude token 問自己：這個動作讓系統長期更自主，還是只解決今天的問題？

**延伸閱讀：**
- `skills/session-lifecycle/SKILL.md` §「資源衛生」— session/Chrome/RAM 管理
- `AGENT_RULES.md` §「資源衛生」— Chrome browser session 規則
- `scripts/hermes_memory_sop.md` — 地端 Hermes 記憶提供者 SOP（本地模型接手 FAQ）

---

## 實作規範

### Agent 在 cold-start 必須做的事

1. 讀本檔（docs/company-values.md）
2. 讀 CURRENT_STATUS.md 抓專案最新狀態
3. 讀對應 recall（recalls/AX_recall.md）抓自己的角色定義
4. 讀 skills/first-principles-check + skills/pitfalls + docs/glossary.md（cold-start 三件套）
5. 開工前先輸出 Startup Check，包含：「這次 session 我要做什麼 / 我會把進度存到哪個檔 / 我預期遇到什麼卡點 / 本輪預計怎麼測試 / 測試 receipt 會寫在哪裡」

### Long-running session 中必須做的事

- 每完成一個小階段（即使還沒整個任務做完）就：
  1. 更新對應的研究檔 / task card / handoff 檔
  2. git commit + push（不要等到全部做完）
  3. 用 SendUserMessage 給 Owner 一個 1-3 行的進度回報

### Session 結束前必須做的事

- 確認所有 commits 已 push 到 main
- 更新 CURRENT_STATUS.md 的「進行中任務」「下一步」「已知 blocker」
- 留 PROJECT STATE UPDATE 給下一個接手的 agent 看（人或 AI）

---

## 違反這條原則的歷史代價

- **2026-04-08 v3.8 全廢**：上一週的 7 個版本沒人增量保存進度、沒人回報失敗、沒人驗證 runtime → 一夜之間發現全部 commit 都是「編譯得過但沒跑通」的廢版本。如果每次小改都即時驗證 + 即時記錄，就不會累積到一整週後才崩塌。
- **2026-04-08 sheet vs repo 真相錯位**：因為文件沒及時更新成 live sheet 真相，agent 拿過時文件當 ground truth，做出的所有後續決定都歪掉。這是「沒做白工」原則被違反的典型案例。
- **2026-04-09 不存研究進度**：曾經試圖一次做完整份報告再回報，結果中間 context 變化、資料來源切換，半成品掉了一次。此後改為「增量存」原則。

---

---

## 六、主動推進（2026-04-18 補入）

> 詳見 `docs/agent-behavior-framework.md`（全角色共用行為框架）

核心：**做完一件事，自動做下一件事**。不等 Owner 發令，不問「要我繼續嗎」。

- 不確定 → 去查（截圖/讀 log/讀 Sheet），查到狀態再做決定
- 規則一致性：要求別人遵守的規則，自己先遵守
- 唯一該停的情況：Owner 物理操作、真實技術阻塞、Owner 明確說「停」

---

## 變更紀錄

| 版本 | 日期 | 變更 | 來源 |
|------|------|------|------|
| v1.0 | 2026-04-09 | 初版，定義五條核心原則 + 實作規範 + 歷史代價 | Owner 親口指示「寫死給各個工作夥伴」 |
| v1.1 | 2026-04-18 | 新增「六、主動推進」，引用 agent-behavior-framework.md | Owner 系統性校正：A0/A6 行為不一致 |
| v1.2 | 2026-06-17 | 新增未提交變更判讀文化：先追需求、可用性、治理狀態，再補強提交或封存標記 | Owner 校正：不是清掉 dirty changes，而是回收成學習與治理訊號 |
| v1.3 | 2026-06-18 | 新增測試與 receipt 硬條款，要求 cold-start 先列測試計畫與 receipt 路徑，收尾必列 Tests run | Owner 校正：有寫沒做、沒測試、沒落檔都違反企業文化 |

---

## 9. 投資中心思想 — 生存優先 × 大賺小賠（Owner 2026-06-27 定）

> 這是 Investment OS 一切策略/功能的最上層判準。任何功能先問:「這是在保護我不死,還是在追上行?」**生存件優先於 alpha 件。**

**兩句金句(Owner 中心思想):**
1. **「如果你不下注,你就不會贏;如果你沒有錢,你就無法下注。」** → 必須參與(下注)才有機會贏,但**資本保全是前提**——不能輸到沒籌碼再下注。生存 > 一切。
2. **「長遠看來股票是向上的,但長遠看來,我們都是死人了。」** → 「長期會漲」不是抱著不管的藉口;你可能先沒錢/沒時間。要在有意義的時間裡**活著且有表現**。

**核心:大賺小賠(不對稱)** — 虧損切小、讓贏家跑。第一要務是**避開「大賠死掉」**,其次才是放大上行。

**edge 與協作優勢:** edge 不在「更多 alpha 訊號」,在「**紀律的不對稱 + 不死**」——大賺小賠需要切小虧、放長贏,而那是人類情緒做不到的。協作分工:**機器無情執行風控紀律(sizing/de-risking/出場),人提供 conviction 與下注決心。**

**大道至簡 / 反 sprawl(Owner 原始設計警告,2026-04 已寫):** 原始三角色脊椎(風控大師 + 左側 + 右側)要保住;不要讓系統因 AI 討論愈長愈多而偏離生存優先。不要把「AI 自行整理的反省」當成 Owner 意圖。

---

## 10. 協作與治理教訓（2026-06-29 蒸餾）

> 從 ghost-job 清理 × gen_system_truth 雙倉掃描 × 三輪盲點偵測萃取。具體案例在前，規則在後。

### 教訓 1 — 瞄準本質的提問，而非表面需求

**案例**: 討論「接 FRED API 拉總經指標」。表面需求是「把總經資料帶進 IS」；本質是——總經是槓桿刻度盤 + 市場反應函數的背離偵測。API 搬運只是基礎；edge 在「FRED 說一件事、市場反應另一件事」的判讀，而那需要 Owner 視角。直接動手接 API 只解決了表面。

**規則**: 任何接需求前先問「這個需求的本質是什麼？解掉它之後，真正要解的問題消失了嗎？」答案若是否，先對齊本質需求再動手。

---

### 教訓 2 — 治理真相必須自我生成，死文件貢獻為零

**案例**: SYSTEM_MAP.md 從手工維護換成 gen_system_truth.py 自動生成（來源: launchctl + git 事實）。三輪迭代後，12 個 com.maplab.* job「跑了但 repo 沒追蹤」的狀態被自動偵測並 Tier-A commit 修復；b-role 退役原因自動寫入 _archive/RETIREMENT_LOG.md。手寫的 SYSTEM_MAP 在第一次 ghost job 時就已過期；自動生成的版本「當下即為真相」。

**規則**: 凡是能從 git + 作業系統事實自動生成的治理資訊，就必須自動生成。要求人工維護的文件，人一離開就衰減，貢獻趨近於零。

---

### 教訓 3 — 閉環成功養出懶 agent；三問是解藥；所有文件 = 組織層次 prompt engineering

**案例**: gen_system_truth 第一輪跑完，SYSTEM_MAP 顯示 anomalies=0——看起來乾淨。但 12 個 com.maplab.* jobs 正在跑，只是 grep regex 壞掉看不見。b-role 若沒三問直接接 Tier-B dispatch 卡片，會產生「去 load 腳本不存在的 plist」的錯誤操作。三問強迫回到地面：(a) 現在跑的是什麼？(b) 跟預期差多遠？(c) 差異代表什麼風險？

**規則**: 低 context handoff 做好後，下一個 agent 拿到的是壓縮卡片，不是地面真相。定期主動三問。評估所有文件只用一個判準——「有沒有提高高品質判斷的機率？」，不是「看起來完整」。

---

### 教訓 4 — anomalies=0 不可信；放寬偵測要同步問「讓自己看不到什麼」

**案例**: grep regex bug — `r"\|".join(...)` 在 shell `-E` 模式下產生字面管道符 `\|`（而非交替運算子 `|`），導致 `com.maplab.*` 全體從 launchctl 結果消失。同一輪修 MISLABELED false positive 時，又讓 UNTRACKED_RUNNING 類別消音。兩個變更都讓 anomalies 數字往下，但 12 個 jobs 的問題沒消失——只有直接跑 `launchctl list | grep com.maplab` 才抓到真相。

**規則**: 「一切正常」的訊號，第一個反應是「偵測函數本身有沒有問題？」。修偵測規則、調閾值、放寬過濾，必須配套說明「哪些東西現在看不見了」。迴圈的目的是 RESOLVE（解決），不只是 LABEL（貼標籤）；眼見為憑勝過乾淨的 dashboard。

---

### 教訓 5 — 知道了就自動做；迴圈靠自主行動才複利，停等才是損耗

**案例**: 12 個 com.maplab.* plist 在 LaunchAgents 下已在跑、前綴正確、無腳本問題 → Tier-A：直接 copy 到 maplab repo launchd/、一次 batch commit，不問。b-role plist 腳本遺失、功能是否重建未定 → 真正的 fork → 移到 _archive/ 並記錄「Owner 決策待定」，才回報。前者自動完成節省一輪往返；後者保留 Owner 控制權。

**規則**: 凡是已知事實能確定下一步的（Tier-A：純加性、不動 runtime），就執行、commit、繼續跑。只有在真正的 fork（功能是否重建、破壞性步驟、代理值解不掉的歧義）才暫停回報。每個多餘的停頓，都把複利迴圈變成停等迴圈。
