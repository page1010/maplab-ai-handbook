# Owner 需求追蹤面板

> **所有 Agent session 結束前必須寫一筆。這裡是 Owner 說了什麼、誰承諾了什麼、做了什麼的唯一追蹤。**
> 格式：新的在最上面。

---

## 使用說明

每次 session 結束前，負責的 Agent 在最上方加一筆：

```
| YYYY-MM-DD | Agent | Owner 說了什麼（原話摘要） | 承諾產出 | 實際產出 | 狀態 |
```

狀態用：✅ 完成 / 🔄 進行中 / ⏸️ 阻塞 / ❌ 未做

---

## 紀錄

| 日期 | Agent | Owner 需求（原話摘要） | 承諾產出 | 實際產出 | 狀態 |
|------|-------|----------------------|---------|---------|------|
| 2026-08-28 | A1 / A5 / A6 / Codex | 「跑了那麼多次都沒有檢討回推換方法，是在浪費額度；沒有新產出要研究大神做法並寫進企業文化 SOP。再從整個系統、IG、Drive、照片、報價與對話找出刁鑽客製、統包代解但沒有收費的隱藏成本，列合理同業報價，以後不能委屈自己。」 | 停止 LINE 盲跑、做第一性原理回推與 expert-method SOP；唯讀理解 MAPLAB 業務；建立 privacy-safe 漏損掃描、同業價格表、毛利 workbook、Task Card 與 durable continuation | ✅ Supervisor 兩輪 plateau 熔斷＋receipt 自動恢復私有 data root，live 無參數 resume 零新增 round/attempt/call；✅ 34/34 tests；✅ 唯讀 Drive/Sheet/IG/照片系統與公開同業研究；✅ 20,256 rows／2,491 conversations aggregate-only 初篩；✅ 24 項 proposal-only 加價矩陣＋200-row 稽核表；✅ 50 個九類 hash-only calibration，18 true_candidate／22 insufficient／8 false-positive／2 included，raw IDs/network/model calls 均 0；✅ 企業文化原則 7、pitfalls、Task Card、durable job；未改 live price、未對客發送 | 🔄 進行中（下一步固定 10 案 evidence-join pilot，confirmed leakage 仍為 0） |
| 2026-08-26 | A1 / Codex | 「我們系統的指向性地圖也好了嗎，發 Telegram 給我」 | 重驗 canonical map／Graphify／本機入口，把人話版狀態與可攜地圖發到 Owner Telegram，留下 API 與 Telegram Web 證據 | ✅ 7/7 tests、generator freshness、Graphify 1820/3262 完整性與兩個 HTTP 入口通過；✅ 正式通知 `message_id=4130`；✅ 離線 `index.html` 附件 `message_id=4131`；✅ Telegram Web 實際反讀；⚠️ Extension 仍待 Owner 手動 reload | ✅ 完成 |
| 2026-08-25 | A1 / Codex | 「跑好後也接一下 NotebookLM；以後找不到的 agent 先問 SOP 與路徑，也可以為地端模型指路」 | 建 canonical notebook、控制資料源、建立 agent／地端模型 fallback、以 A8 情境做 cited smoke test | ✅ Gemini Notebook 已建立並放入治理核心＋SOP router 兩包（28 份底層來源）；✅ repo 新增 machine router 與 cold-start／Hermes／superpowers 路由；✅ 回答契約限制為 `FOUND`／`NEEDS_LIVE_REFRESH`／`NOT_IN_PACK`；✅ JSON manifest 只留本機、不整庫上傳 | ✅ 完成 |
| 2026-08-25 | A1 / Codex | 「不要只畫 A2 A8，把可以畫的都畫完；投資系統先不用；地端硬體、共治、A2–A8 流程、產物互用、Sheet 索引優先」／「有幫助就跑起來；整個專案塞 NotebookLM 呢？」 | 單一 manifest 生成多視角地圖、Extension 入口、Graphify graph 與 NotebookLM 安全來源包；不混入投資域，不盲目整庫上傳 | ✅ 7 視角、263 nodes／302 edges、A2–A8 28 stages、Extension offline map 與入口、NotebookLM 兩包／28-source hash manifest；✅ Graphify 0.9.49 AST 圖 1820 nodes／3262 edges／147 communities，交付 graph／tree／report／query memory；✅ unittest／schema／freshness／secret scan／desktop+mobile UI readback 通過；⚠️ Chrome 安全邊界阻擋 agent 自動進入 `chrome://extensions`，已安裝擴充套件尚待 Owner 手動重新載入 | 🔄 進行中 |
| 2026-06-20 | B1 / Codex | 「可以開始，不用像素風不用花很多心力在 uiux 但要讓功能齊全」 | 把 v0.2 擬人化 dashboard 補成真正可派工：全部部門可選、可輸入任務、自動建議主責、產生經理優先/小弟備援 prompt | ✅ `maplab-ops-game-dashboard.html` 新增 `Role Dispatch Console`：21 部門名冊、任務路由、可複製派工 prompt、實單查詢自動路由 IOS-INVENTORY、B4 off-duty 備援提示；✅ Headless Chrome CDP + mobile smoke + validation report `JOB-B1-DASH-FUNCTIONAL-20260620` | ✅ 完成 |
| 2026-06-20 | B1 / Codex | 「更新一下現況；擬人遊戲化要可以對部門與角色說話，先找經理，經理沒上班才找小弟；像像素風便利商店，不同部門坐不同位置，點人出對話框與負責工作」 | 1. 更新 Guild Ops Board 現況 2. 做可點 NPC 的部門作戰室 prototype 3. 留測試 receipt | 1. ✅ `maplab-ops-game-dashboard.html` 新增 Today Status 2. ✅ 新增 `OPS CONVENIENCE STORE` v0.2：6 區域、9 NPC、經理/小弟/off-duty/caution 對話 3. ✅ Chrome readback + mobile smoke + validation report `JOB-B1-DASH-PERSONIFIED-20260620` | ✅ 完成 |
| 2026-06-20 | A8 / Antigravity | 「你先看這個 然後幫我建起來優化這個影片 (https://chatgpt.com/share/6a3685a4-f764-83e8-ab2e-396404caf97e)」 | 1. 建立 Higgsfield 整合框架與 recalls / extension modules 2. 設計 ICC Tainan 案例的 Higgsfield POC storyboard 企劃 3. 更新 T-A8-001 任務卡與看板 | 1. ✅ 建立 `skills/a8-higgsfield-integration.md` 2. ✅ 更新 `recalls/A8_recall.md`、`chrome-extension/task-modules/A8.json` 並重建 modules 3. ✅ 產出 `higgsfield_poc_plan.md` 運鏡與動態企劃 4. ✅ 更新 `T-A8-001-folder-to-video-distribution.md` | ✅ 完成 |
| 2026-06-17 | A0 / Codex → A8 | 「幫我整理成 agent 可以跑起來的流程接給 A8；去拿我的資料夾實例，取用 AI 工具做成影片，上傳 TikTok / YouTube，整理封面到 Pinterest；先研究跑看看再把流程技能寫好」 | 1. 研究 IG Reel 底層邏輯 2. 用真實資料夾案例 dry-run 3. 寫 A8 技能與 task handoff | 1. ✅ Chrome readback 取得 Reel metadata（Higgsfield MCP / AI workflow 型短影音）2. ✅ ICC Tainan WebP 素材跑出 1080x1920 dry-run mp4 + cover + platform metadata 3. ✅ `skills/a8-video-pipeline-skills.md` v2.0、`T-A8-001-folder-to-video-distribution`、review bundle 已建立 | ✅ 完成（正式上傳待 A8 approval card） |
| 2026-06-17 | A0 / Codex | 「不是要處理掉仍有其他既有未提交變更；要檢查原因、滿足什麼使用者需求、可不可用、有沒有被新版治理取代；有用補強提交，沒用封存標記；把這個寫進企業文化員工手冊」 | 1. 找正式企業文化手冊 2. 寫入 dirty change 判讀文化 3. 補 Owner 需求追蹤 | 1. ✅ 確認 `docs/company-values.md` 是 cold-start 必讀企業價值文件 2. ✅ 新增「未提交變更要先判讀，不是先清理」條款 3. ✅ 本面板新增需求來源紀錄 | ✅ 完成 |
| 2026-06-17 | A0 / Codex | 「先搜尋並對標一樣有在佈局 SEO 關鍵字矩陣的外燴網站，最好是看起來業績很好的，國外的網站，由你研究並發任務給 Claude」 | 1. 冷啟動讀本地 A2 狀態與邊界 2. 研究國外外燴 SEO matrix 標竿 3. 產 Claude 可接手任務包 | 1. ✅ 已讀 CURRENT_STATUS / pitfalls / A2 task cards 2. ✅ `JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617` 產出 Social Pantry / ZeroCater / Fooditude / Rocket Food benchmark 3. ✅ `claude_task_prompt.md` + `T-A2-SEO-CATERING-MATRIX-001` 已建立 | 🔄 進行中（等 Claude 產文稿） |
| 2026-06-16 | A0 / Codex | 「好 去做」：把 Tesla-style governance 的第一階段做成可執行系統，而不是只停在 architecture report | 1. 實作 patrol reaction ledger 2. 產出 summary / task card 3. 保持 dirty worktree 邊界，不碰無關檔案 | 1. ✅ `tools/hermes_patrol_bridge.py` 已輸出 `workbook/learning_loop/reaction_ledger.jsonl` 2. ✅ summary 分出 owner_5min / direct_do / delegated 3. ✅ `T-A1-LEARNING-LOOP-001` 建卡承接 P2/P3 | ✅ 完成 |
| 2026-06-15 | A0 / Codex | 「根據 Nadella 生態系 / learning loop 貼文反思 MAPLAB 系統架構並巡查，然後上 GitHub 發想哪裡可以加強」 | 1. 冷啟動讀本地真相源 2. 用 learning loop 角度巡查 MAPLAB 架構 3. 產 review bundle 4. 建 GitHub 改善 issue | 1. ✅ 已讀 `CURRENT_STATUS.md` / `pitfalls.md` / A0 模組與相關規則 2. ✅ 重新產 Hermes reaction packet 3. ✅ `workbook/reviews/JOB-A0-ECOSYSTEM-LEARNING-LOOP-20260615/` 已產報告與 issue body 4. ✅ GitHub issue #14 已建立：https://github.com/page1010/maplab-ai-handbook/issues/14 | ✅ 完成 |
| 2026-06-11 | IOS-FB / Codex | 「你知道要去notion拿社群帳號密碼嗎？不知道寫進去啟動流程 我想知道為什麼最近都沒有報告」 | 1. 把社群帳密 Notion 取用邊界寫入啟動流程 2. 查明最近 FB/社群報告沒出現的原因 3. 留 review bundle | 1. ✅ `AGENT_STARTUP_PROTOCOL.md Step 5.5` + `skills/credentials/social-accounts.md` 2. ✅ 查明 daily job 有跑但只刷舊 historical shadow sample，production collector/digest 未閉環且 training gate failed 3. ✅ `workbook/reviews/JOB-IOS-FB-NO-REPORTS-20260611/` | ✅ 完成 |
| 2026-06-11 | B1 | 「英文標題的清掉繁體中文是我的session」「你說要接給地端agent不花我額度但沒有做成嗎」 | 1. 封存 6 個英文 Codex automations 2. heartbeat 改地端零額度 | 1. ✅ 移至 ~/.codex/automations_archived-20260611（可還原），不再每小時燒額度、不再生殭屍程序 2. ✅ heartbeat_audit 本是純 Python，plist 已備好待 Owner 載入；另發現 launchd 讀不到 CloudStorage（TCC），照片管線改 session 背景跑 | ✅ 完成 |
| 2026-06-11 | B1 | 「可以分類一下嗎 截圖 家庭 外燴工作 ＋年月份資料夾 然後已經有資料夾的不要動」 | 照片分類搬移管線 + 保護已有資料夾 | ✅ a4_photo_classifier.py：年度傾倒區 ~98,400 張分三類+年月；named albums/MAPLAB_ASSETS/影片不動；30 張實測通過；10,000 張批次跑中；可 --undo 全還原（T-A4-004） | 🔄 進行中 |
| 2026-06-11 | B1 | 「hermes 有貢獻了嗎可以用了嗎」→「刪除 auto-allow-gemini」 | 1. 查 Hermes 實際狀態 2. 修復可用性 | 1. ✅ 查明：歷史有產出（6 個 IOS 排程）但 memories 0 利用；當日 280 錯誤全來自 5/23 殭屍 job `auto-allow-gemini`（每分鐘自動點允許按鈕，資安反模式）2. ✅ 備份後刪除，Hermes 恢復；pitfalls 已記錄；P6（記憶啟用）排下個 session | ✅ 完成 |
| 2026-06-11 | B1 | 「建。另外 1. 雲端硬碟不要抓來地端了清理一下以後大家雲端抓，我本來要讓地端模型寫 alt seo 作業做相簿整理的，可以先整理完同步再離線釋出空間嗎 2. 讓這個功能為我們系統做出貢獻」 | 1. agent-hq 上 GitHub 2. A4 照片 ALT 管線（gemma4）3. 整理→同步→離線的順序設計 | 1. ✅ github.com/page1010/agent-hq 已建並 push 2. ✅ a4_photo_alt_pipeline.py 實測 2 張通過、背景 800 張批次跑中、CSV 同步進 Drive 3. ✅ T-A4-003 卡片含完整順序與 Owner 兩個一次性動作 | 🔄 進行中（36,676 張處理中） |
| 2026-06-11 | B1 | 「你來解決這個問題，跨專案 extension 也是共用的、mac mini 也是共用的、版本治理也是……想一個架構不用再有這種共用檔案但會找不到的問題。Hermes 的記憶管理有好好利用嗎？我是不是每天在爬資料硬碟會滿？有沒有整理資料拿來訓練？A7 應該定時抓 LINE 對話訓練與模擬吧」 | 1. AGENT-HQ 架構設計 2. 四個疑問的事實查核 3. 遷移 task card | 1. ✅ docs/agent-hq-architecture.md 2. ✅ 查核：Drive 531GB 是元兇、Hermes memories 0 bytes 零利用、archive 只進不出、A7 止步於 SQLite 索引 3. ✅ T-HQ-001 建卡認領 | 🔄 進行中（P1-P6 待執行） |
| 2026-06-11 | B1 | 「以後請不管哪個agent哪個session和我對話後要有記錄並要釐清使用者需求寫在面板追蹤，worktree很髒常常是所有人做所有事，本來寫的規範有超多規矩不方便做版本迭代嘗試的都砍掉，我不懂我對話了四五次計劃提了四五次最後沒人做是怎麼回事這沒有產出太慘了」 | 1. 建立此面板 2. 砍掉 AGENT_RULES 迭代卡點 3. task card 加責任人欄位 | 1. ✅ owner_requirements_panel.md 建立 2. ✅ AGENT_RULES v5.0 精簡 3. ✅ task card 模板更新 | ✅ 完成 |
| 2026-06-11 | B1 | 「push to main 為什麼要我授權，我們的解法是透過用github管理版本方便找出上一版，結果一直卡住，不要再等我授權」 | 在 .claude/settings.json 加 git push 白名單 | ✅ settings.json 已加 `Bash(git push origin main)` | ✅ 完成 |

---

## 待處理的 Owner 需求（未完成）

> 從上方表格提取狀態非 ✅ 的項目，方便快速掃描。

- 🔄 T-HQ-001 P5/P6 待做（P1-P4 ✅；B1 認領）
- 🔄 T-A4-003 照片 ALT 管線（802/36,676 完成，0 失敗；實測 ~550 張/h，5000 張批次跑中，全量預估 ~3 天內）
- 👤 Owner 待辦（唯一一件，要等時機）：照片全部處理完後改 Google Drive「串流檔案」釋出 ~531GB。**現在先不要改**
