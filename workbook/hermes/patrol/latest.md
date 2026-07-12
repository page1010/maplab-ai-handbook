# Hermes Patrol Reaction Packet

- generated_at: `2026-07-11T09:00:02+08:00`
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

- total: `43`
- blocked: `4`
- active: `11`
- stale_active: `7`
- unmarked: `8`
- paused_or_not_started: `9`
- done: `11`
- owner_related: `20`

## Reaction Ledger

- ledger: `workbook/learning_loop/reaction_ledger.jsonl`
- summary: `workbook/learning_loop/reaction_ledger_summary.md`
- entries_added: `0`
- open_entries: `4`

## Reaction Cards

### google-oauth-reauth-card [high]

- owner_role: `A1`
- target_task_card: `handoff/tasks/T-A1-SYNC-GUARD-001.md`
- why: Google OAuth token refresh is invalid_grant; repeating the patrol text will not solve it.
- next_step: Prepare an Owner 5-minute OAuth reauthorization card, then rerun Sheets/Drive smoke.
- patch_hint: 把阻塞改成精準 OAuth reauth action，不要每日原文轉發 invalid_grant。

Codex follow-up prompt:

```text
你是 MAPLAB A1，運行在 Codex。
先讀 CURRENT_STATUS.md、pitfalls.md、workbook/hermes/patrol/latest.json，再讀相關 Task Card。

觸發 reaction: google-oauth-reauth-card
原因: patrol saw invalid_grant in Google OAuth
本輪目標: produce the reauth card and verification command

輸出：更新相對角色下一步或產 task packet；若需要 Owner，必須是 5 分鐘內可完成的具體行動。
```

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

### stale-active-dispatch [medium]

- owner_role: `A0/B1`
- target_task_card: `handoff/tasks/`
- why: 6 active tasks have no activity for 7+ days: T-A2-005-local-seo-factory, T-A2A3-001-B, T-A4-003-photo-alt-pipeline, T-A4-004-photo-classify, T-A5-002, T-B1-B4-investment-os-role-split.
- next_step: Turn each stale active task into continue / pause / refactor / close with an exact next owner.
- patch_hint: 不要保留模糊進行中；寫入下一個可執行動作或暫停理由。

Codex follow-up prompt:

```text
你是 MAPLAB B1/A1，運行在 Codex。
先讀 CURRENT_STATUS.md、pitfalls.md、workbook/hermes/patrol/latest.json，再讀相關 Task Card。

觸發 reaction: stale-active-dispatch
原因: active tasks are stale
本輪目標: confirm progress and push the next direct task downward

輸出：更新相對角色下一步或產 task packet；若需要 Owner，必須是 5 分鐘內可完成的具體行動。
```

### task-card-status-normalization [medium]

- owner_role: `A1`
- target_task_card: `handoff/tasks/`
- why: 8 task cards have unmarked status, so patrol cannot decide reliably.
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
📋 每日自動巡查 — 2026-07-11 09:00

=== MAPLAB 系統巡查 2026-07-11 09:00 ===

[🔴 EXPIRED] Google OAuth token — auto-refreshing...
✅ Token refreshed, new expiry: 2026-07-11T02:00:01.604030+00:00

【Owner 行動項】
  → T-A2-002-foodsafety-seo-cleanup: 等 Owner 決定 post 698 的「無麩質或低糖選項」FAQ 答案要不要改（A2 唯讀掃描，未動任何文章）
  → T-A2A3-001: RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL
  → T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作）

【阻塞中 — 等外部條件】
  ⏸️ T-A2-002-foodsafety-seo-cleanup (A2): 等 Owner 決定 post 698 的「無麩質或低糖選項」FAQ 答案要不要改（A2 唯讀掃描，未動任何文章） [4d ago]
  ⏸️ T-A2A3-001 (A2): RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL [48d ago]
  ⏸️ T-A3-002 (A3): 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） [104d ago]
  ⏸️ T-A7-001 (A7): A5 外送費級距未建立（僅影響 Q5 自動計算；手動模板不受影響） [0d ago]
  ⏸️ T-A7-002 (A7): 任務 1/2/3 需 LINE bot 後台權限；任務 5/8 需 TimeTree 權限（任務 9 已解除） [4d ago]

【進行中】
  ⏳ T-A1-EXT-001-dynamic-role-modules (A1): （checkpoint.sh 自動補建，請 agent 填寫） [0d ago]
  ⏳ T-A1-LEARNING-LOOP-001 (A1): 建立 token capital registry，登記可複用 prompt / eval / task packet / sk [0d ago]
  ❓ T-A1-RTK-001 (A1): 狀態未標記 [日期不明]
  ⏳ T-A1-V6-P2 (A1): 4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG 精簡完成。下?? [0d ago]
  ⏳ T-A1-V7 (A1): Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Phase 5（自動壓縮 [0d ago]
  ⚠️ T-A2-005-local-seo-factory (A2): 本地 SEO Factory 骨架已建（Planner→Auditor 七階段）、三大 Pillar [68d ago]
  ❓ T-A2-006-ads-seo-wordpress-patrol (A2): 狀態未標記 [日期不明]
  ❓ T-A2-SEO-CATERING-MATRIX-001 (A2): 狀態未標記 [日期不明]
  ⚠️ T-A2A3-001-B (A2): WordPress post `1696` 已建立為未發布草稿並重載驗證：`https://www. [45d ago]
  ❓ T-A4-002 (A4): 狀態未標記 [日期不明]
  ⚠️ T-A4-003-photo-alt-pipeline (A4): 等 36,676 張處理完 → Owner 改 Drive 串流 → 釋出 ~433GB [30d ago]
  ⚠️ T-A4-004-photo-classify (A4): 批次跑完後 `--status` 查進度，續開下一批直到 ~98,400 張完成 [30d ago]
  ⚠️ T-A5-002 (A5): Owner 三題已回答（2026-06-23）→ 已加 `fixMasterTemplate_()` 到 Code. [17d ago]
  ❓ T-A5-004 (A5): 狀態未標記 [92d ago]
  ⚠️ T-A5-005 (A5): `clasp push --force` 已成功部署 8 檔（含 syncQuoteStatus_ / setupSyncTri [17d ago]
  ⚠️ T-A6-001 (A6): Case Store v0 已接到現有 `CONVERSATION_LOG`；A6 Telegram 新增 `/linecase [2d ago]
  ❓ T-A8-001-folder-to-video-distribution (A8): 狀態未標記 [日期不明]
  ⚠️ T-B1-B4-investment-os-role-split (??): B1-B4 已不只做角色拆分；新增 RSI-like 成長閉環，下一步是把  [22d ago]
  ❓ T-B1-DASH-001 (??): 狀態未標記 [日期不明]
  ❓ T-HQ-001 (??): 狀態未標記 [16d ago]
  ⚠️ T-IOS-KOL-001 (??): - **接續點**：四個每日時段（02:30/08:30/14:30/21:20）的 Telegram di [20d ago]

【暫停/待開始】
  🔲 T-A1-SYNC-GUARD-001 (A1): 待開始
  🔲 T-A1-V6-P3 (A1): 待開始
  🔲 T-A2-003-weekly-wp-audit (A2): 待開始
  🔲 T-A2-004 (A2): 待開始
  🔲 T-A5-006 (A5): 待開始
  🔲 T-A5-007-codex-takeover (A5): 待開始
  💤 T-A6-002 (A6): 暫停中 [94d ago]
  💤 T-B1-001 (??): 暫停中 [日期不明]
  🔲 T-GBP-001 (??): 待開始

【已完成】8 張 Task Card
  （最近異動 3 張，其餘見 handoff/tasks/）
  ✅ T-A4-001
  ✅ T-A2-007-seo-trio-review-20260707
  ✅ T-A2-001

【投資 OS 守夜人】
🟢 nightwatch 今日正常（今日報告已產生，0 警示）

```
