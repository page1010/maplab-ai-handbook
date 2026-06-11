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
| 2026-06-11 | B1 | 「你來解決這個問題，跨專案 extension 也是共用的、mac mini 也是共用的、版本治理也是……想一個架構不用再有這種共用檔案但會找不到的問題。Hermes 的記憶管理有好好利用嗎？我是不是每天在爬資料硬碟會滿？有沒有整理資料拿來訓練？A7 應該定時抓 LINE 對話訓練與模擬吧」 | 1. AGENT-HQ 架構設計 2. 四個疑問的事實查核 3. 遷移 task card | 1. ✅ docs/agent-hq-architecture.md 2. ✅ 查核：Drive 531GB 是元兇、Hermes memories 0 bytes 零利用、archive 只進不出、A7 止步於 SQLite 索引 3. ✅ T-HQ-001 建卡認領 | 🔄 進行中（P1-P6 待執行） |
| 2026-06-11 | B1 | 「以後請不管哪個agent哪個session和我對話後要有記錄並要釐清使用者需求寫在面板追蹤，worktree很髒常常是所有人做所有事，本來寫的規範有超多規矩不方便做版本迭代嘗試的都砍掉，我不懂我對話了四五次計劃提了四五次最後沒人做是怎麼回事這沒有產出太慘了」 | 1. 建立此面板 2. 砍掉 AGENT_RULES 迭代卡點 3. task card 加責任人欄位 | 1. ✅ owner_requirements_panel.md 建立 2. ✅ AGENT_RULES v5.0 精簡 3. ✅ task card 模板更新 | ✅ 完成 |
| 2026-06-11 | B1 | 「push to main 為什麼要我授權，我們的解法是透過用github管理版本方便找出上一版，結果一直卡住，不要再等我授權」 | 在 .claude/settings.json 加 git push 白名單 | ✅ settings.json 已加 `Bash(git push origin main)` | ✅ 完成 |

---

## 待處理的 Owner 需求（未完成）

> 從上方表格提取狀態非 ✅ 的項目，方便快速掃描。

- 🔄 T-HQ-001 AGENT-HQ 遷移 P1-P6（B1 認領，2026-06-11）
- 👤 Owner 待辦：Google Drive 改串流（釋放最多 531GB）
- 👤 Owner 待辦：`~/.claude/settings.json` 加 additionalDirectories
