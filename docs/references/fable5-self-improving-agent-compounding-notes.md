# 外部參照：Fable 5 自我改進 Agent 複利架構（BlockTempo）

> 來源：https://www.blocktempo.com/self-improving-agent-fable-5-2/（@0xCodez，2026-06，BlockTempo）
> 抓取：2026-07-07｜依文化 #24 格式：吸引點 / copy_pattern / do_not_copy / 最小落地
> 對照基準：`docs/cross-project-governance-tech-tree.md` + `docs/superpowers-internalization-map.md`（同日產出）

## 一句話定位

文章主張：Fable 5 級模型的價值不在單次對話，而在「每次執行讓下次更聰明」的複利系統
（四層架構：原語 → 編排 → 記憶 → 自我改進）。**用它的四層對照我們，前三層我們已有等價物，
第四層（自我改進）正是今天診斷出的最弱層——外部獨立印證，不是我們自己嚇自己。**

## 四層對照

| 它的層 | 它的零件 | 我們的等價物 | 判定 |
|---|---|---|---|
| 1 原語 | Fable 5 / sub-agents / worktrees / tools | 多模型艦隊（Claude/Codex/agy/Ollama）+ worktree 紀律（S19） | 🟢 已有 |
| 2 編排 | /goal 自我修正迴圈、fan-out-verify、Routines 雲排程 | agent_courier + Chrome Extension 召喚 + launchd（Mac mini 24/7 = 它的 Routines）+ Self-Healing Loop（**還卡拍板**） | 🟡 零件齊、閉環未上線 |
| 3 記憶 | STATE.md 進出紀律 / Skills / Knowledge Base | CURRENT_STATUS + task cards + pitfalls + 60 技能書 + checkpoint.sh | 🟢 已有且更厚 |
| 4 自我改進 | eval loops + rule distillation 回灌記憶層 | Evolution Channel（**三表 07-07 才首建**）+ Learning Loop（**停在 P1**）+ 技能驗證（**零覆蓋**） | 🔴 最弱層 |

## 五階段記憶成熟度（本文最值得偷的框架）

它引 Continual Learning Bench：記憶系統成熟度 = `Fail → Investigate → Verify → Distill → Consult`，
並用「**驗證覆蓋率 %**」量化（Fable 5 達 ~73%，上代 ~17%）。

**對照我們**：pitfalls 流程是 Fail → Investigate → Distill（跳過 Verify）→ Consult 弱（被動查表）。
跳過的 Verify = superpowers 對照的 G1（技能 TDD）；Consult 弱 = G3（1% 觸發規則）。
**兩份獨立外部參照指向同兩個洞，可視為已交叉驗證的結論。**

## copy_pattern（可搬的）

1. **驗證覆蓋率當巡查指標**：`已含「封坑驗證」欄的 pitfalls / 總 pitfalls`。
   給 G1 工作一個可追蹤的數字（現值 0/190），巡查月報列出，脫離「有做/沒做」二元感覺。
2. **五階段當記憶系統成熟度標尺**：寫進科技樹 T0——我們現在卡在第 3 階（Verify）門口。
3. **「每次非平凡失敗後必須 compound skill」的節奏感**：checkpoint.sh 已有 fix-commit 偵測提示，
   缺的是把「提示」變「預設產草稿」（= superpowers 落地表順序 3，不新增工作項）。

## do_not_copy（明確不搬）

- **Claude Routines 雲排程**：Mac mini 24/7 + launchd 就是我們的 Routines；搬雲端違反地端資料原則
  （照片/LINE 個資不出機器）。僅備註：Mac mini 故障時 Routines 可當災備選項。
- **/goal + Outcomes 機制**：等價物是 Self-Healing Loop S1-S6，已有 spec + pilot，缺的是拍板不是新設計。
- **模型分層路由**：我們已有（B-role 交 Ollama、Codex offload、A6 三層降載鏈），且 07-07 Owner
  已校正為「代稱+指向制」，不再抄外部型號表。
- 文中 benchmark 數字（73%/17%、6×）：二手轉述，僅當方向參考，不當決策依據。

## 最小落地（不新增軌道，全部併入既有排程）

- 驗證覆蓋率指標 → 併入 G1 落地時的巡查輸出（+3 行腳本）。
- 五階段標尺 → 科技樹下次更新時補一行 T0 註記。
- 其餘皆已被科技樹 R1/R2 與 superpowers 落地表涵蓋，**本參照不產生新任務**。
