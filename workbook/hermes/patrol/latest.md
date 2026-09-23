# Hermes Patrol Reaction Packet

- generated_at: `2026-09-05T09:00:06+08:00`
- schema: `maplab.hermes_patrol_reaction.v1`
- repo: `/Users/pagemacmini/maplab-ai-handbook`

## Operating Decision

- Patrol delivery is not resolution.
- Hermes/local layer owns reaction, role next-step packets, and memory candidates.
- Codex/A1/B1 periodically verify repo/project progress and push concrete next steps downward.

## Runtime

- hermes_cli: `missing`
- model: `unknown`
- provider: `unknown`
- gateway: `unknown`
- telegram: `unknown`

## Counts

- total: `59`
- blocked: `2`
- active: `0`
- stale_active: `0`
- unmarked: `33`
- paused_or_not_started: `8`
- done: `16`
- owner_related: `32`

## Reaction Ledger

- ledger: `workbook/learning_loop/reaction_ledger.jsonl`
- summary: `workbook/learning_loop/reaction_ledger_summary.md`
- entries_added: `0`
- open_entries: `4`

## Reaction Cards

### long-blocked-three-layer-review [medium]

- owner_role: `A0/A1`
- target_task_card: `handoff/tasks/`
- why: 2 blocked tasks are older than 14 days: T-A2A3-001, T-A3-002.
- next_step: Run three-layer blocker review and split false blockers into direct-do / delegated / true Owner action.
- patch_hint: 每張卡改寫接續點：誰負責、下一個命令、何時才需要 Owner。

Codex follow-up prompt:

```text
你是 MAPLAB A0/A1，運行在 Codex。
先讀 CURRENT_STATUS.md、pitfalls.md、workbook/hermes/patrol/latest.json，再讀相關 Task Card。

觸發 reaction: long-blocked-three-layer-review
原因: 2 blockers are stale
本輪目標: patch the top stale task cards with concrete next steps

輸出：更新相對角色下一步或產 task packet；若需要 Owner，必須是 5 分鐘內可完成的具體行動。
```

### task-card-status-normalization [medium]

- owner_role: `A1`
- target_task_card: `handoff/tasks/`
- why: 33 task cards have unmarked status, so patrol cannot decide reliably.
- next_step: Normalize 接續狀態 blocks from existing task-card evidence.
- patch_hint: 補狀態、最後活動、接續點、阻塞；缺資料標缺資料，不要腦補。

Codex follow-up prompt:

```text
你是 MAPLAB A1，運行在 Codex。
先讀 CURRENT_STATUS.md、pitfalls.md、workbook/hermes/patrol/latest.json，再讀相關 Task Card。

觸發 reaction: task-card-status-normalization
原因: task card metadata is unmarked
本輪目標: normalize status blocks for the unmarked cards

輸出：更新相對角色下一步或產 task packet；若需要 Owner，必須是 5 分鐘內可完成的具體行動。
```

## Raw Patrol Excerpt

```text
🔴 每日自動巡查（repo 健康 FAIL，需處理）— 2026-09-05 09:00

=== MAPLAB 系統巡查 2026-09-05 09:00 ===

⚠️ Google token check error: ERROR

【⚡ 本輪狀態遷移（四態狀態機，SECTION 25）】
  🔄→🟡 STALLED: T-IOS-KOL-001（最後活動 76d 前）
  → 已自動寫回 Task Card，無需 Owner 操作（可逆，SECTION 24）

【Owner 行動項】
  → T-A2-002-foodsafety-seo-cleanup: 等 Owner 決定 post 698 的「無麩質或低糖選項」FAQ 答案要不要改（A2 唯讀掃描，未動任何文章）
  → T-A2A3-001: RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL
  → T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作）
  → T-HQ-001: Owner pending（非 B1 blocking）

【阻塞中 — 等外部條件（⏸️/⏳/🔍）】
  ⏸️ T-A2-002-foodsafety-seo-cleanup (A2): 等 Owner 決定 post 698 的「無麩質或低糖選項」FAQ 答案要不要改（A2 唯讀掃描，未動任何文章） [60d ago]
  ⏸️ T-A2A3-001 (A2): RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL [104d ago]
  ⏸️ T-A3-002 (A3): 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） [160d ago]
  ⏸️ T-HQ-001 (??): Owner pending（非 B1 blocking） [72d ago]

【進行中（🔄 IN_PROGRESS / 🟡 STALLED）】
  ❓ T-A1-DIRECTIONAL-MAP-001 (A1): 狀態未標記 [日期不明]
  ❓ T-A1-EXT-001-dynamic-role-modules (A1): 狀態未標記 [日期不明]
  ❓ T-A1-GIT-SYNC-001-checkpoint-pull-before-commit (A1): 狀態未標記 [日期不明]
  ❓ T-A1-PATROL-GRADER-001-wire-grader-into-patrol (A1): 狀態未標記 [日期不明]
  ❓ T-A1-RTK-001 (A1): 狀態未標記 [97d ago]
  ❓ T-A2-003-weekly-wp-audit (A2): 狀態未標記 [4d ago]
  ❓ T-A2-006-ads-seo-wordpress-patrol (A2): 狀態未標記 [4d ago]
  ❓ T-A2-HERMES-SEO-COACH-001 (A2): 狀態未標記 [日期不明]
  ⏳ T-A4-002 (A4): IN_PROGRESS — 187GB Takeout（5 個 ZIP）確認存在 Drive，尚未解?? [140d ago]
  ❓ T-A5-004 (A5): 狀態未標記 [149d ago]
  ❓ T-A5-A6-HIDDEN-COST-RECOVERY-001 (A5): 狀態未標記 [日期不明]
  ❓ T-A6-003-hermes-governed-executor (A6): 狀態未標記 [日期不明]
  ❓ T-A6-HERMES-DEERFLOW-001 (A6): 狀態未標記 [5d ago]
  ❓ T-A6-HERMES-LINE-GYM-001 (A6): 狀態未標記 [日期不明]
  🟡 T-A7-001 (A7): STALLED — 先檢視 `docs/hermes-line-sheets-assistant-flow-v1.md` 與 [3d ago]
  🟡 T-A7-002 (A7): STALLED — 現行流程改讀 `docs/hermes-line-sheets-assistant-flow-v [3d ago]
  ❓ T-A8-001-folder-to-video-distribution (A8): 狀態未標記 [8d ago]
  ❓ T-A8-002-maplab-ig-theme-song (A8): 狀態未標記 [日期不明]
  ❓ T-A8-FITNESS-HERMES-CONTINUATION (A8): 狀態未標記 [日期不明]
  ❓ T-A8-FITNESS-MVP-001 (A8): 狀態未標記 [日期不明]
  ❓ T-B1-001 (??): 狀態未標記 [106d ago]
  ❓ T-B1-DASH-001 (??): 狀態未標記 [76d ago]
  ⏳ T-IOS-KOL-001 (??): IN_PROGRESS — - **接續點**：四個每日時段（02:30/08:30/14:30/21: [76d ago]

【暫停/待開始】
  🔲 T-A1-SYNC-GUARD-001 (A1): 待開始
  🔲 T-A1-V6-P3 (A1): 待開始
  🔲 T-A2-004 (A2): 待開始
  🔲 T-A5-006 (A5): 待開始
  🔲 T-A5-007-codex-takeover (A5): 待開始
  💤 T-A6-002 (A6): 暫停中 [151d ago]
  🔲 T-CODEX-CHATGPT-EXPORT-INGEST-001 (??): 待開始
  🔲 T-GBP-001 (??): 待開始

【自動關閉（🔒 AUTO_CLOSED — Owner 可回覆「重開 T-XXX」重啟）】
  🔒 T-A1-LEARNING-LOOP-001 (A1): 自動關閉（Owner 可回覆「重開 T-A1-LEARNING-LOOP-001」重啟）
  🔒 T-A1-V6-P2 (A1): 自動關閉（Owner 可回覆「重開 T-A1-V6-P2」重啟）
  🔒 T-A1-V7 (A1): 自動關閉（Owner 可回覆「重開 T-A1-V7」重啟）
  🔒 T-A2-005-local-seo-factory (A2): 自動關閉（Owner 可回覆「重開 T-A2-005-local-seo-factory」重啟）
  🔒 T-A2-SEO-CATERING-MATRIX-001 (A2): 自動關閉（Owner 可回覆「重開 T-A2-SEO-CATERING-MATRIX-001」重啟）
  🔒 T-A2A3-001-B (A2): 自動關閉（Owner 可回覆「重開 T-A2A3-001-B」重啟）
  🔒 T-A4-003-photo-alt-pipeline (A4): 自動關閉（Owner 可回覆「重開 T-A4-003-photo-alt-pipeline」重啟）
  🔒 T-A4-004-photo-classify (A4): 自動關閉（Owner 可回覆「重開 T-A4-004-photo-classify」重啟）
  🔒 T-A5-002 (A5): 自動關閉（Owner 可回覆「重開 T-A5-002」重啟）
  🔒 T-A5-005 (A5): 自動關閉（Owner 可回覆「重開 T-A5-005」重啟）
  🔒 T-A6-001 (A6): 自動關閉（Owner 可回覆「重開 T-A6-001」重啟）
  🔒 T-B1-B4-investment-os-role-split (??): 自動關閉（Owner 可回覆「重開 T-B1-B4-investment-os-role-split」重啟）

【已完成】12 張 Task Card
  （最近異動 3 張，其餘見 handoff/tasks/）
  ✅ T-A1-IG-GITHUB-TOOL-RADAR-001
  ✅ T-A1-SCREENSHOT-TOOLS-SKILLS-002
  ✅ T-A1-DEERFLOW-SKILLS-001

【投資 OS 守夜人 + IS-HS】
  🔴 nightwatch 今日有警示：
    
    - **夜間備料 progress_digest**：485h 前(上限 36h)｜progress_digest_2026-08-16.md
    - **Hermes 投資問題包**：485h 前(上限 200h)｜invest_question_pack_2026-08-16.md
    - **影子教練巡查 shadow_findings.jsonl**：467h 前(上限 48h)｜shadow_findings.jsonl
    - **影子教練『真實發現』新鮮度**：stale_genuine_findings｜last_genuine=2026-08-16T12:56:22+00:00｜上限 24h
  🔴 escalation_queue: 13 條 open+未推播（見 projects/investment-os-continuous-iteration-plan.md ④）
  🔴 IS-HS: 25/100（新鮮度=50% 警報通暢度=0%）

【B3 廣告觀察】
  ⚪ B3 廣告尚未啟動（Owner 去 Meta 建受眾包後，回報一句話或 UTM 有 b3 流量自動偵測）
  → 啟動後：回報「B3 開始跑了」或 GA4 出現 utm_source=meta_b3 流量
  → A1 偵測到後自動開始每日成效摘要並進例會

── repo 健康關卡（獨立 grader）──
🔴 PATROL GRADER：FAIL（有硬問題必須處理）
❌ FAIL：本地 main 落後 origin 36 個 commit（>=10，同步已失控，先 pull）
⚠️  WARN：本地有 242 個未 push 的 commit
⚠️  WARN：2 張進行中任務卡 >7 天無 commit（patrol.sh 詳列）

```
