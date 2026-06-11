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
| 2026-06-11 | IOS-FB / Codex | 「你知道要去notion拿社群帳號密碼嗎？不知道寫進去啟動流程 我想知道為什麼最近都沒有報告」 | 1. 把社群帳密 Notion 取用邊界寫入啟動流程 2. 查明最近 FB/社群報告沒出現的原因 3. 留 review bundle | 1. ✅ `AGENT_STARTUP_PROTOCOL.md Step 5.5` + `skills/credentials/social-accounts.md` 2. ✅ 查明 daily job 有跑但只刷舊 historical shadow sample，production collector/digest 未閉環且 training gate failed 3. ✅ `workbook/reviews/JOB-IOS-FB-NO-REPORTS-20260611/` | ✅ 完成 |
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
