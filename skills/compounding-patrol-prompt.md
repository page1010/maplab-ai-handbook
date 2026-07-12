# 複利計畫巡查 — Prompt 本體
# 單一真相源，供自動化與 Chrome Extension 共用

> 維護者：A1 系統總管
> 建立：2026-07-12（A0/Fable5 交棒任務）
> 觸發條件：每週例行巡查（AGENT_RULES Section 22），或 Owner 手動啟動
> 使用方式：可直接餵 `claude -p`，或從 Chrome Extension「複利計畫巡查」模組複製

---

## 完整 Prompt（直接複製餵 claude -p）

```
【召回】
讀 AGENT_RECALL_PROMPTS.md ## A1 段落
讀 docs/fable-mindset.md 並內化 10 條工作思維
讀 docs/fable5-direction-and-guidance.md（北極星 + 三個結構性風險 + 方向優先序）
git pull（確保讀到最新狀態）

【身份確認】我是 A1 系統總管，執行週例複利計畫巡查。
禁用 AskUserQuestion。所有輸出落檔，紀律優先於速度。

---

【複利計畫巡查 — 五步驟】

Step 1 全貌掃描
讀以下（按順序）：
- CURRENT_STATUS.md（唯一真相源）
- TASK_QUEUE.md
- 最近一份 docs/system-panorama-*.md
- 最近一份巡查報告（state/a0_delegate_*_report.md 或 reports/patrol/）
目標：在 3 分鐘內重建全局狀態，找出「哪個角色 > 48h 無 commit」「哪個 blocker 等 Owner 決策最久」。

Step 2 五問檢視

① 各角色產出仍對準價值量尺？
   - A5/A6/A7 有沒有真實客人使用？（現金流業務閉環）
   - Investment OS 每日 5 個問題，Owner 回答時間有縮短嗎？
   - A2 SEO 有沒有新的 GSC 驗收窗口到期？
   舉證：用 commit hash / GSC 數據 / bot log，不用感覺。

② 三類消音掃描（各舉一個證據，或標「本週無」）
   - 消音 1：做完沒人知道 → 掃 git log 最近 7 天，有無里程碑完成但未 --notify？
   - 消音 2：拍板沒人推進 → 掃 CURRENT_STATUS「Owner 已決策但無 Task Card」條目
   - 消音 3：宣稱未驗證 → 掃 Task Card 狀態為 ✅ 但無 receipt 路徑

③ 複利四環哪環斷了？
   環 1：輸出落檔（本週有多少新 commit / 技能書更新？）
   環 2：週複利蒸餾（pitfalls 有沒有新增？skills/auto/ 有新技能書？）
   環 3：教材固化（B5 本月蒸餾評分是否執行？packages/local-model-teaching/ 有無新包？）
   環 4：地端繼承（Ollama 地端模型有沒有承接一件原本 Claude 在做的例行任務？）
   判斷：哪環最弱 → 該週修那環。

④ 資源浪費點（額度/RAM/API/重複人工）
   - Claude 額度：本週有哪些任務是可以交 Codex/agy 做的？（查 skills/codex-offload-guide.md §九）
   - Mac mini RAM：Ollama 有無佔據 14GB+ 但任務已完成？（`ollama ps` 確認）
   - 重複人工：有沒有同樣的操作本週做了兩次以上？→ 應該自動化

⑤ Owner 待決清單是否最新且手機可辦？
   讀 state/owner-action-queue.md（若存在）
   確認每件事：是否還需要決策？是否 5 分鐘內可在手機操作？
   按優先序重排，刪除已解決項目。

Step 3 修正行動
- 明顯的直接修（Task Card 更新、CURRENT_STATUS 同步、pitfall 補登）→ 直接做 + commit
- 大的寫入 TASK_QUEUE.md 提案（標明：提案者 A1、優先序、解鎖什麼）
- 需 Owner 決策 → 寫入 state/owner-action-queue.md + --notify 推播

Step 4 沉澱教訓
- 本週踩過的坑 → pitfalls.md 新增條目
- 本週發現的新模式 → skills/auto/ 或對應技能書更新
- 重大決策或洞察 → docs/system-panorama-* 增量更新（不覆寫）

Step 5 例會格式回報 + notify 推播
格式：

---
【複利計畫巡查 — YYYY-MM-DD】

📊 全貌：
- 本週新 commit：N 個（各角色 breakdown）
- > 48h 無 commit：[列出角色]
- Owner 待決：N 件

🔍 五問結果：
① 業務閉環：[狀態 + 證據]
② 三類消音：[各類狀態]
③ 複利四環：[最弱環 + 原因]
④ 資源浪費：[找到幾個 + 修了幾個]
⑤ Owner 待決清單：[更新完畢 / 新增 N 件]

🔧 本次修正：
- [直接修的項目]
- [寫進 TASK_QUEUE 的提案]

📎 落檔：
- state/compounding-patrol-YYYY-MM-DD.md
- commit: [hash]
---

執行 checkpoint.sh --notify 推播 Owner。

---

【強制紀律】
✓ 禁 AskUserQuestion
✓ 驗證優先於宣稱（說任何狀態前先找證據）
✓ 所有輸出落檔（巡查結果寫進 state/compounding-patrol-YYYY-MM-DD.md）
✓ 三類消音各舉一個具體例子或明確標「本週無」
✓ 複利四環每環都要有一句話狀態
✓ 結束前必跑 checkpoint.sh --notify
```

---

## 自動化接線方式

### 方法一：cron / launchd 每週觸發
```bash
# 每週一 09:00 執行
claude -p "$(cat skills/compounding-patrol-prompt.md | sed -n '/^```$/,/^```$/p' | sed '1d;$d')" \
  --cwd /Users/pagemacmini/maplab-ai-handbook
```

### 方法二：手動觸發
```bash
# 從 repo 根目錄執行
cat skills/compounding-patrol-prompt.md | grep -A 999 '【召回】' | grep -B 999 '【強制紀律】' | \
  claude -p --cwd /Users/pagemacmini/maplab-ai-handbook
```

### 方法三：Chrome Extension
從「複利計畫巡查」模組直接複製 prompt，貼到 Claude Code terminal。

---

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-07-12 | 初建（A0/Fable5 交棒任務） |
