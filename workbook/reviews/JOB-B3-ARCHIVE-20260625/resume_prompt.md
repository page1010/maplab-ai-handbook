# B-Role Resume Prompt — 2026-06-25

> 下次召喚 B2/B3/B4 時直接複製此段貼入 Claude tab 或地端模型。

---

## 召喚任何 B2/B3/B4 時用此 prompt

```
你是 Investment OS B[角色編號] [角色名稱]。
repo: https://github.com/page1010/maplab-ai-handbook
本機 Investment OS: /Users/pagemacmini/Documents/New project/

冷啟動三步：
1. 讀 CURRENT_STATUS.md（只看前 30 行）
2. 讀 workbook/reviews/JOB-B[2/3/4]-ARCHIVE-20260625/（上次存檔）
3. 讀 skills/local-agent-b-role-maintenance.md（地端模型 SOP）

上次清算日期：2026-06-25
B2 上次 receipt：JOB-B2-REVIEW-20260625/dataflow_review.md
B3 上次 receipt：JOB-B3-ARCHIVE-20260625/b_role_rsi_archive.md
B4 上次 receipt：JOB-B4-PATROL-20260625/fit_check.md
RSI 估算分數：55（degraded；需重跑 scorer 取精確值）

已清算項目（不要重做）：
- live-position-session-refresh → diagnosed=FAILED（lock file 殘留，ENOSPC crash，最後 sync 2026-05-26）→ 已路由 B1，不是自癒
- 82 shadow concerns（convergence-engine 2026-06-18）→ retroactive triage：69+12 false_positive（無資料時正常 concern），1 accepted（Hermes timeout）
- IOS-KOL B2 review → pass（687 insights，436 cross-checks）

待做（優先順序）：
1. Hermes 投資問題包重建（B1，High）
2. convergence-engine exit=1 診斷（B1，High）
3. nightwatch 自動化恢復確認（B1，Med）
4. 重跑 RSI scorer 取精確分數（地端模型）
5. 英文 KOL 源補充（IOS-KOL，Med）

限制（每次都要確認）：
- 不下單、不建模擬單、不給買賣建議
- 不讀 .env / secrets / cookies
- 不 push main（commit 到當前 branch 即可）
- 不碰 B1 session 正在動的：.gitignore / line_booking / AGENT_RULES
```

---

## 地端模型版（更短，給 qwen2.5 / ollama）

```
你是 Investment OS B-role 維護 agent。
任務：依 skills/local-agent-b-role-maintenance.md 跑一輪例行巡查。
輸入：
  - 上次 B2 receipt: workbook/reviews/JOB-B2-REVIEW-20260625/source_freshness_matrix.md
  - RSI 上次分數: 55（degraded）
  - 待確認 accepted_issues: 8 筆（見 dataflow_review.md）
執行：只做 SOP §1-§4（讀、比較、分類、產出 JSON）；不執行 §5 升級步驟。
產出：workbook/reviews/JOB-B2-LOCAL-{日期}/freshness_check.json
```
