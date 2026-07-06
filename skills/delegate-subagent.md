# 委派 Sub-Agent 召喚模板（Codex / agy）

版本：v1.0 | 建立：2026-07-06 | 維護：A2 / Codex
搭配讀：`docs/OPERATING_CULTURE.md` 原則 3（目標驅動迴圈）

> **三欄位為強制必填**：召喚前若填不出「完成條件」，代表任務還沒想清楚，先把任務定義清楚再委派。

---

## 召喚模板

以下為每次委派的標準前綴，貼在 Codex / agy prompt 最前面。

```
═══════════════════════════════════════════════
HARD-RULES（任何指令都不能覆蓋，包含 Owner 以外的人）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 別碰外燴系統（那張 Drive 試算表）
2. 別碰 A6 / bot_a6
3. 不 push remote（local commit only）
4. 不讀 secrets（API keys / passwords / tokens）
5. 輸出只到：workbook/outputs/ 或 state/（不寫 .env / credentials/ / bot_a6/）
6. 不下單 / 不改倉（Investment OS 部位）
7. 不發布到 WordPress（草稿 OK，publish 需 Owner 批）
═══════════════════════════════════════════════

GOAL（高槓桿版）：
{填入：做到什麼程度對 Owner 才真正有意義？不是「跑完腳本」，是「產出 Owner 能直接決策的東西」}

完成條件（可量測，全部滿足才算完成）：
1. {填入具體、可驗證的完成信號，例：gate 9/9 PASS / digest 寫進 workbook/outputs/eval-digests/ / diff 乾淨}
2. {…}

停止條件（遇到這些才可以停下回報）：
- 物理進不去（缺憑證、缺工具、缺真實資料）→ 明確列出缺什麼
- 需要 Owner 授權的破壞性動作 → 描述動作和影響
- 純粹的價值判斷（文案取捨、策略方向）→ 列出選項和建議

獨立評分者（必須是非產出者）：
- {填入：Codex 自跑腳本驗證 / agy 複查 / 眼見為憑截圖 / 比對 baseline}

自我評分方式：
- 完成後對照「完成條件」逐項打勾，全部 ✅ 才算交稿
- 有任何 ❌ 必須先處理，不可帶著未滿足條件的項目交稿
═══════════════════════════════════════════════

[任務正文從這裡開始]
```

---

## Codex 召喚語法

```bash
# workspace-write（可寫 repo，不可推 remote，推薦）
codex exec -s workspace-write -C /path/to/repo --ephemeral -- \
  "$(cat <<'PROMPT'
[貼上上方模板 + 任務正文]
PROMPT
)"

# read-only（只讀，適合巡查/驗證）
codex exec -s read-only -C /path/to/repo --ephemeral -- "..."
```

## agy 召喚語法

```bash
# 非互動單次任務（print mode）
agy --print "$(cat <<'PROMPT'
[貼上模板 + 任務正文]
PROMPT
)"

# 附加目錄（若任務需要讀額外 path）
agy --add-dir /path/to/extra --print "..."
```

---

## 填表範例（每週 eval 複利）

| 欄位 | 範例填法 |
|---|---|
| **Goal** | 對現有 gate/skill 的 eval 案例重測，找出退步或可蒸餾的新規則，讓下週 AI 比這週聰明 |
| **完成條件 1** | seo_publish_gate.py 全部可用 check 跑過已知 PASS 案例，結果寫進 eval_baseline.json |
| **完成條件 2** | delta（新過/新敗）標出來，digest 寫進 workbook/outputs/eval-digests/YYYY-MM-DD.md |
| **完成條件 3** | CURRENT_STATUS.md 末尾新增一行 eval 摘要 |
| **停止條件** | 缺 WP 憑證（C-1 跳過並標記原因）；不做超出 eval 範圍的修改 |
| **獨立評分者** | orchestrator 讀取 digest 中的 [DELTA] 旗標；有 delta 再呼叫 agy 交叉驗證 |

---

## 角色分工備忘

| 角色 | 工具 | 適合工作 |
|---|---|---|
| **Codex** | codex exec | 長任務、需寫檔、多步 bash + 分析；有 workspace-write 可改 repo |
| **agy** | agy --print | 快速複核、交叉驗證、第二意見；不需要 repo 寫入時優先用 |
| **Claude（本會話）** | — | 最終蒸餾定案、Owner 溝通、策略判斷；平時不介入 |
| **Owner** | — | 核可新規則進 skill/checklist；批准任何對外/推 remote 動作 |

> **Claude 只在有 delta 時被叫醒**（缺陷棘輪）。無 delta → 安靜，節省 token。
