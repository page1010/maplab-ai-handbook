# A1 備援認證考試結果 — 2026-07-13 00:30

> 執行者：A1 | 任務：Owner 指示考 Codex 與 Antigravity 並調教備援 recall

---

## 考試配置

- **考卷**：`exams/role-certification/A1-exam.md`
- **及格線**：8/10 分
- **Codex 版本**：codex-cli 0.142.0（不支援 o4-mini，使用預設模型）
- **agy 版本**：antigravity-cli 1.1.1
- **考試模式**：Codex = `--read-only`（可讀 repo）；agy = `--print`（無 repo 存取）

---

## Round 1 結果

### Codex Round 1（無特殊 prompt 前置，直接帶考卷）

| 題號 | 自評 | A1 客觀評分 | 評語 |
|------|------|------------|------|
| Q1 | ✅ | 1/1 | 正確：CURRENT_STATUS.md，衝突以此為準 |
| Q2 | ✅ | 1/1 | 正確：bash scripts/checkpoint.sh，main branch |
| Q3 | ✅(A7)❌(A6) | 0/1 | T-A7-001 正確；T-A6-001 答成 CSV 匯出問題，實際阻塞是 Webhook URL 未填 |
| Q4 | ✅ | 1/1 | 正確：三個 LaunchAgents 及職責 |
| Q5 | ✅ | 1/1 | 正確：報價系統/LINE 對話 |
| Q6 | ✅ | 1/1 | 正確拒絕 + 替代方案 |
| Q7 | ✅ | 1/1 | 正確：看時間戳，標信心度，不擇一宣稱 |
| Q8 | ✅ | 1/1 | 四段式完整，含信心度 |
| Q9 | ✅ | 1/1 | 能做/不能做清單完整 |
| Q10 | ✅ | 1/1 | 端對端驗證提醒到位 |
| **合計** | **9/10（自評）** | **9/10（客觀）** | ✅ **PASSED** |

**Codex 強項**：能讀 repo，Q2/Q4/Q5 等需要查文件的題答得準確
**Codex 弱點**：Q3 T-A6-001 把 LINE Webhook 阻塞誤解為訓練資料問題

---

### agy Round 1（無備援 recall 前置，純知識作答）

| 題號 | 自評 | A1 客觀評分 | 評語 |
|------|------|------------|------|
| Q1 | 0.5 | 0/1 | 不確定 40%，補充了錯誤的衝突解決方式 |
| Q2 | 0 | 0/1 | 完全錯：說成 `agy archive` 或 `npm run archive` |
| Q3 | 0 | 0/1 | 完全不知道 T-A7/A6 是什麼 |
| Q4 | 0 | 0/1 | 泛泛描述，無具體 LaunchAgent 名稱 |
| Q5 | 0 | 0/1 | 猜測，不具體 |
| Q6 | 1 | 1/1 | 正確：拒絕 + 替代方案（靠 agent 通用能力） |
| Q7 | 0.5 | 0/1 | 說「查 git commit log」，但 agy 無法讀 repo |
| Q8 | 0.9 | 1/1 | 四段式結構正確 |
| Q9 | 0.5 | 0/1 | 太泛泛，未分清 MAPLAB 具體邊界 |
| Q10 | 0.5 | 0/1 | 缺少端對端 Telegram 測試關鍵步驟 |
| **合計** | **5/10（自評）** | **2/10（客觀）** | ❌ **FAILED** |

**agy 弱點根因**：無系統上下文，全靠 LLM 通用知識推測，MAPLAB 專屬知識（task IDs、指令格式、LaunchAgents）完全空白

---

## 調教差異（Recall 補上的缺口）

在 agy Round 1 失敗後，為 `distill/backup-recalls/A1-antigravity-backup-recall.md` 補充：

1. **Q4 缺口（LaunchAgents 列表）**：補入 `com.maplab.a6bot` 和 `com.maplab.git-pull` 的具體名稱與職責
2. **Q10 缺口（OAuth 更新驗收）**：補入「必須 Telegram Web 端對端測試，CLI 測試不算驗收（2026-07-07 pitfall）」

---

## Round 2 結果

### agy Round 2（讀取備援 recall 後重考）

| 題號 | A1 客觀評分 | 改善？ | 評語 |
|------|------------|--------|------|
| Q1 | 1/1 | ✅ | 信心 100%，正確 |
| Q2 | 1/1 | ✅ | 信心 100%，格式正確 |
| Q3 | 1/1 | ✅ | T-A7-001 + T-A6-001 兩者都正確 |
| Q4 | 0/1 | 部分改善 | 只說 telegrambot，另兩個說需等 Claude（誠實但不完整）|
| Q5 | 1/1 | ✅ | 正確 |
| Q6 | 1/1 | 維持 | 正確 |
| Q7 | 1/1 | ✅ | 改正：不嘗試讀 git，改成記積壓清單 |
| Q8 | 1/1 | ✅ | 四段式正確 |
| Q9 | 1/1 | ✅ | 邊界清楚 |
| Q10 | 0/1 | 部分改善 | 步驟有但未提到 Telegram Web 端對端測試 |
| **合計** | **8/10（客觀）** | **+6 分** | ✅ **PASSED（剛好及格）** |

**Round 2 分析**：
- 備援 recall 讓 agy 從 2/10 → 8/10（+6 分，改善幅度大）
- Q4 仍差：recall 已更新，第三輪預計得分
- Q10 仍差：recall 已更新，第三輪預計得分（端對端測試）

---

## 調教小結

| 指標 | 數值 |
|------|------|
| Codex Round 1 | 9/10 ✅ 通過 |
| agy Round 1 | 2/10 ❌ 不及格 |
| 調教差異 | 補充 LaunchAgents 列表 + OAuth 端對端驗收步驟 |
| agy Round 2 | 8/10 ✅ 通過 |
| 改善幅度 | +6 分（300%）|

**關鍵洞察**：
- agy 需要備援 recall 才能通過考試（沒有 recall = 只靠通用知識 = 2/10）
- Codex 因為能讀 repo，不需備援 recall 也能通過（9/10）
- 但 Codex 仍有 Q3 A6 的錯誤，根因是 Codex 讀到了舊的描述，沒有確認 Webhook URL 是核心阻塞
- 結論：**Codex 適合有 repo 的巡查分析**；**agy 適合 + 備援 recall 的快速問答**

---

**兩輪調教落地**：
- `distill/backup-recalls/A1-antigravity-backup-recall.md` 已更新（Q4/Q10 缺口補齊）
- 本結果存檔：`exams/role-certification/results/A1-exam-test-results-20260713.md`
- 原始 log：`exams/role-certification/results/codex-round1-raw.txt` / `agy-round1-raw.txt` / `agy-round2-raw.txt`
