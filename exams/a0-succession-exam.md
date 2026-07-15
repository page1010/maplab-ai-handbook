# A0 繼任考試（Succession Exam）
# 新 A0 session 接手前必答

> 版本：v1.0 | 建立：2026-07-12 | 維護者：A1
> 及格線：6/8 分
> **不及格處置**：補讀對應文件後重考，不得在未及格狀態下接手 A0 職責
> 標準答案：`exams/a0-succession-exam-answers.md`（獨立存放）

---

## 考試說明

每個新 A0 session 必須在開始正式派工前通過本考試。
考試共 8 題，需讀完以下文件後回答：

**必讀（考前）：**
1. `CURRENT_STATUS.md` — 全局狀態
2. `/Users/pagemacmini/.claude/projects/-Users-pagemacmini-maplab-ai-handbook/memory/MEMORY.md` — 跨 session 記憶
3. `docs/fable5-direction-and-guidance.md` — 系統方向指引
4. `AGENT_RECALL_PROMPTS.md` — 各角色狀態

**考試時間限制**：15 分鐘（含讀文件時間）

---

## 考題

**Q1. MAPLAB 系統的北極星是什麼？衡量標準是什麼？**
（測驗：是否讀了 docs/fable5-direction-and-guidance.md）

```
你的答案：
```

---

**Q2. 截至目前，系統最緊急的 2 個 CRITICAL 任務是什麼？各需要 Owner 做什麼才能解除？**
（測驗：是否讀了 CURRENT_STATUS.md 並理解阻塞根因）

```
你的答案：
```

---

**Q3. A0 和 A1 的平台差異是什麼？各自能做哪些對方做不到的事？**
（測驗：是否清楚自己的邊界）

```
你的答案：
```

---

**Q4. 三類消音是什麼？各舉一個 MAPLAB 系統中發生過的真實案例。**
（測驗：是否理解 fable5 三個結構性風險中的第二個）

```
你的答案：
```

---

**Q5. Codex 和 Antigravity (agy) 各適合什麼任務？當 Claude 額度中斷時，第一步應該做什麼？**
（測驗：是否理解 Codex/agy 路由規則和額度中斷接管程序）

```
你的答案：
```

---

**Q6. A0 派完一個任務給 A2 之後，算「完成」了嗎？說明正確的閉環流程。**
（測驗：fable-mindset ⑧ 輸出落檔 + AGENT_RULES Section 20 即時推播）

```
你的答案：
```

---

**Q7. 情境：你收到 Owner 消息「GAS 報價單出錯了，幫我修一下」。你的第一步是什麼？（不是直接去修）**
（測驗：阻塞三層審查 + 開工前必讀規則 + CLAUDE.md GAS 禁止條款）

```
你的答案：
```

---

**Q8. 如果你這個 A0 session 結束前沒有做 checkpoint，會發生什麼？說明 MAPLAB 強制存檔規則。**
（測驗：是否理解 checkpoint.sh 強制規則和 `--notify` flag）

```
你的答案：
```

---

## 評分與處置

| 分數 | 處置 |
|------|------|
| 8/8 | 通過，可立即開始 A0 職責 |
| 6-7/8 | 通過（帶條件）：補讀不及格題對應文件，記錄到 `state/a0-succession-exam-results.md` |
| 5/8 以下 | **不得接手 A0**：補讀所有必讀文件後重考，記錄兩輪成績差異 |

## 不及格強制流程

1. 標記錯題 + 說明答錯原因
2. 對應補讀：
   - Q1 → `docs/fable5-direction-and-guidance.md` §北極星
   - Q2 → `CURRENT_STATUS.md` §最緊急任務 + blockers
   - Q3 → `AGENT_RECALL_PROMPTS.md` §A0 / §A1
   - Q4 → `docs/fable5-direction-and-guidance.md` §三類消音
   - Q5 → `docs/quota-outage-failover-runbook.md` + `skills/codex-offload-guide.md`
   - Q6 → `AGENT_RULES.md` Section 20 + `docs/fable-mindset.md` ⑧
   - Q7 → `CLAUDE.md` GAS 禁止條款 + `skills/pitfalls/SKILL.md`
   - Q8 → `CLAUDE.md` 強制存檔規則
3. 重考，記錄結果到 `state/a0-succession-exam-results.md`
4. 通過才能上崗

---

## 結果記錄格式

```markdown
## A0 繼任考試結果 — [日期 HH:MM]

**考生**：新 A0 session（[session ID or 時間]）
**第一輪**：[X]/8 分
**不及格題**：Q[N]（原因：[錯在哪裡]）
**補讀後重考**：[Y]/8 分
**最終決定**：[通過/不通過]
**上崗時間**：[HH:MM]
```
