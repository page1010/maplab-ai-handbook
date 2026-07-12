# Fable5 系統方向指引
# A0/Fable5 交棒文件 — 全系統修正方向與複利迴圈指引

> 維護者：A1 系統總管
> 建立：2026-07-12（A0/Fable5 交棒任務）
> 來源：A0 起草 + A1 潤飾落檔
> 配套：`docs/fable-mindset.md`（思維框架）、`skills/compounding-patrol-prompt.md`（巡查 prompt 本體）

---

## 北極星

**每輪工作後，系統要比之前「更容易持續進步」。**

衡量標準不是忙碌量，不是 commit 數，而是**複利迴圈是否轉了一圈**：

```
輸出落檔 → 週複利蒸餾 → 技能書更新 → 教材固化 → 地端模型繼承
```

一圈沒轉完就不算進步，只算在原地跑步。每次複利計畫巡查的第一個問題就是：「上週這個迴圈轉了幾圈？哪環斷了？」

---

## 三個要永久防守的結構性風險

### ① 狀態腐化（文件與現實漂移）

**定義**：文件上寫的狀態 ≠ 系統實際狀態。

**已知高危點**：
- CURRENT_STATUS.md 與 Task Card 不同步（S11 數字過期、A5 假 CRITICAL 案例）
- AGENT_RECALL_PROMPTS.md 斷點超過 48h 未更新
- Task Card 狀態欄位缺失或格式不符 patrol.sh 解析器

**防守機制**：
- A1 每日巡查必做 CURRENT_STATUS ↔ Task Card 交叉比對
- `patrol.sh` 解析失敗 = 自動升 🔴 CRITICAL
- `gen_system_truth.py` 每 15 分鐘更新 SYSTEM_MAP（IS 端）

**判斷原則**：任何角色對系統狀態有疑問時，CURRENT_STATUS.md 是唯一真相源，與其他文件衝突時以它為準。

---

### ② 三類消音（完成未告知 / 拍板未推進 / 宣稱未驗證）

**第一類 — 做完沒人知道**：
- 症狀：commit 進了 repo，但 Telegram 沒推播，Owner 不知道
- 防守：任何里程碑完成 → `checkpoint.sh --notify`（雙層：即時推播 + patrol 稽核）
- 根因案例（2026-07-08 SEO 三人小組 5 個交付物完成但 patrol 掃不到）

**第二類 — 拍板沒人推進**：
- 症狀：Owner 已決策，但沒有人開任務卡或追蹤
- 防守：決策落地 → 同次 session 建 Task Card，登記進 CURRENT_STATUS
- 判斷：Owner 每次「確認/核准/同意」都隱含「請誰做什麼」，A0/A1 責任是幫他把這句話轉成任務

**第三類 — 宣稱沒驗證**：
- 症狀：「已完成」但沒有 diff / log / 截圖 / receipt
- 防守：fable-mindset ③「驗證優先於宣稱」，AGENT_RULES SECTION 0 阻斷規則
- 判斷：說完成前先問「我有沒有眼見為憑的證據？」

---

### ③ 單點依賴（A0 額度、OAuth token、單一派工通路）

**已知單點**：
- A0 Cowork 額度耗盡 → 整個調度層斷線
- `CLAUDE_CODE_OAUTH_TOKEN` 過期 → A1 bot 失效
- Google OAuth token → A6 `/linecases`、A4 Drive 操作全卡

**已有備援通路清單**（必須維持雙線可用）：

| 單點 | 備援 |
|------|------|
| A0 Cowork 額度 | A1 直接接 Owner Telegram 指令 |
| Claude Code OAuth | `bot/.env` + `scripts/diagnose_a1_claude_bridge.sh` 健檢 |
| Codex 額度 | Antigravity (agy) fallback → Ollama 冷備援 |
| Google OAuth | curl + refresh_token SOP（`skills/credentials/`） |
| Telegram 推播 | `notify_owner.sh` + patrol 稽核雙層 |

**維護規則**：每次巡查確認備援通路仍可用，不要等主線斷了才發現備援也壞了。

---

## 方向優先序

優先序是「先讓現金流閉環，再放大，再鞏固複利」。

### (1) 現金流業務閉環先行 🔴 最高優先

**目標**：A5 報價 + A6 LINE/Telegram + A7 客服，真正被真實客人使用。

**現況斷點**：
- A7 Phase 3 等 Owner 授權 Mina 使用（5分鐘可解）
- A6 LINE Webhook URL 未填（Channel 1654658337，需 Owner 到 LINE Console 操作）
- A5 GAS Dashboard 未啟動（需 Owner 在 GAS 執行 `setupSyncTrigger` + `setupDashboard`）

**判斷原則**：這三件事是 MAPLAB 現金流的直接來源，任何其他任務的優先順序都在這之後。

---

### (2) B3 廣告試跑「可複製結構」

**目標**：找到一個可複製的廣告投放結構，再放大。

**不要做**：還沒有驗證 ROI 前就放大預算。
**要做**：Week 1 NT$100/天集中 `cold-b-meeting-corp`，Week 2-4 觀察 KPI，有結構才加碼。

**判斷原則**：廣告是放大機制，不是起點。現金流業務不閉環之前，廣告的 leads 也沒有人接。

---

### (3) Investment OS 規則引擎上線

**目標**：不給建議，只觸發規則。Owner 看到的是三選項通知，不是 AI 分析報告。

**現況斷點**：
- 規則引擎 5 條 (R-01~R-05) 草稿已建（見 `state/a0_delegate_20260712_report.md` Phase B4）
- 需 Owner 確認 4 個參數（集中度門檻 / 槓桿門檻 / 止損% / 急性警示%）
- IOS-LEFT/IOS-RIGHT 停更需修復（供料層斷鏈）

**量尺**：Owner 每天回答 5 個投資決策問題的時間，從 30 分鐘 → 3 分鐘。

---

### (4) B5 每月蒸餾，向地端模型遷移能力

**目標**：把每月的教訓、技能書、踩坑紀錄蒸餾成地端模型可繼承的教材包。

**節奏**：
- 每月月底 B5 執行一次蒸餾評分（`reports/capability-inventory/`）
- 評分 ≥ 4 的能力打包進 `packages/local-model-teaching/`
- B1 判斷哪些項目可以交棒地端模型執行

**判斷原則**：Claude 做開發，地端模型做例行維護。能力不轉移，每次都要花 Claude 額度從零開始。

---

## 決策文化

### Fable-mindset 十條（完整版在 `docs/fable-mindset.md`）

核心精神：
1. **先對齊再執行** — 讀狀態→比對記憶→再動手
2. **80/20 抓關鍵少數** — 大致正確勝過精準錯誤
3. **驗證優先於宣稱** — 說完成前先眼見為憑
4. **阻塞三層審查** — 能自解？理由合理？解完推系統？
5. **每個結論帶證據鏈** — commit hash / log / 數字
6. **不確定就標示不確定** — 不裝懂
7. **一次修根因不修症狀** — token 案例：401 偽裝成 NetworkError
8. **所有輸出落檔進複利迴圈** — 不落檔的輸出 session 結束就消失
9. **人話優先** — 對 Owner 每個技術詞要能用譬喻拆解
10. **問題回報格式：說明問題→解釋成因→試想解法→給選項**

### 人話拆解四段式

每次對 Owner 回報問題時，強制用這個格式：
```
❌ 不可接受：「A4 掛了」
✅ 標準格式：
- 問題：[描述現象，含時間戳和數字]
- 成因：[根因推斷，含信心度 X%]
- 解法：[選項 A / 選項 B]
- 選項：[你去確認 / 我現在做 / 暫停等你]
```

### 回報後自己派工修理

**原則**：回報完就完了 = 三類消音第一類。

正確閉環：
1. 回報給 Owner（或標入 CURRENT_STATUS）
2. **在同一個 session 裡開 Task Card**
3. 把 Task Card 登記進 CURRENT_STATUS 任務表
4. 如果需要 Owner 決策才能動，寫進 `state/owner-action-queue.md`

---

## 如何使用本文件

- **Owner 回顧全系統時**：讀北極星 + 三個結構性風險 + 方向優先序
- **A1 巡查發現問題時**：對照三類消音，跑 fable-mindset ④（阻塞三層審查）
- **A0 派工前**：確認要派的任務屬於哪個優先序方向，按優先序排列
- **任何角色做決策前**：讀決策文化段，確認不是在修症狀

---

## 配套工具

| 工具 | 路徑 | 用途 |
|------|------|------|
| 複利計畫巡查 prompt | `skills/compounding-patrol-prompt.md` | 每週例行巡查入口 |
| Fable 思維框架 | `docs/fable-mindset.md` | 10 條工作思維原則 |
| A0 派工指引 | `skills/a0-proactive-dispatch-guide.md` | 主動調度 SOP |
| 系統全貌地圖 | `docs/system-panorama-2026-07-12.md` | 本輪全貌快照 |
| 巡查腳本 | `scripts/loop_15_sop_drift.sh` | SOP 偏移偵測 |

---

> 這份文件由 A0/Fable5 起草，A1 落檔。每季或系統方向調整時由 A1 更新。
> 方向是活的，但三個結構性風險和 Fable-mindset 十條是恆久的。
