# Hermes Patrol Reaction Packet

- generated_at: `2026-06-25T09:00:01+08:00`
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

- total: `41`
- blocked: `4`
- active: `12`
- stale_active: `12`
- unmarked: `8`
- paused_or_not_started: `8`
- done: `9`
- owner_related: `19`

## Reaction Ledger

- ledger: `workbook/learning_loop/reaction_ledger.jsonl`
- summary: `workbook/learning_loop/reaction_ledger_summary.md`
- entries_added: `0`
- open_entries: `4`

## Reaction Cards

### long-blocked-three-layer-review [high]

- owner_role: `A0/A1`
- target_task_card: `handoff/tasks/`
- why: 4 blocked tasks are older than 14 days: T-A2-002-foodsafety-seo-cleanup, T-A2A3-001, T-A3-002, T-A7-002.
- next_step: Run three-layer blocker review and split false blockers into direct-do / delegated / true Owner action.
- patch_hint: 每張卡改寫接續點：誰負責、下一個命令、何時才需要 Owner。

Codex follow-up prompt:

```text
你是 MAPLAB A0/A1，運行在 Codex。
先讀 CURRENT_STATUS.md、pitfalls.md、workbook/hermes/patrol/latest.json，再讀相關 Task Card。

觸發 reaction: long-blocked-three-layer-review
原因: 4 blockers are stale
本輪目標: patch the top stale task cards with concrete next steps

輸出：更新相對角色下一步或產 task packet；若需要 Owner，必須是 5 分鐘內可完成的具體行動。
```

### stale-active-dispatch [medium]

- owner_role: `A0/B1`
- target_task_card: `handoff/tasks/`
- why: 11 active tasks have no activity for 7+ days: T-A1-LEARNING-LOOP-001, T-A1-V6-P2, T-A1-V7, T-A2-005-local-seo-factory, T-A2A3-001-B, T-A4-001.
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
📋 每日自動巡查 — 2026-06-25 09:00

=== MAPLAB 系統巡查 2026-06-25 09:00 ===

[🟡 expires in 0.4h] Google OAuth token — auto-refreshing...
✅ Token refreshed, new expiry: 2026-06-25T02:00:00.562876+00:00

【Owner 行動項】
  → T-A2-002-foodsafety-seo-cleanup: 等 Owner 操作 WordPress 後台
  → T-A2A3-001: RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL
  → T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作）
  → T-A7-002: 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限

【阻塞中 — 等外部條件】
  ⏸️ T-A2-002-foodsafety-seo-cleanup (A2): 等 Owner 操作 WordPress 後台 [79d ago]
  ⏸️ T-A2A3-001 (A2): RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL [32d ago]
  ⏸️ T-A3-002 (A3): 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） [88d ago]
  ⏸️ T-A7-002 (A7): 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限 [87d ago]

【進行中】
  ❓ T-A1-EXT-001-dynamic-role-modules (A1): 狀態未標記 [日期不明]
  ⚠️ T-A1-LEARNING-LOOP-001 (A1): 建立 token capital registry，登記可複用 prompt / eval / task packet / sk [9d ago]
  ❓ T-A1-RTK-001 (A1): 狀態未標記 [日期不明]
  ⚠️ T-A1-V6-P2 (A1): 4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG 精簡完成。下?? [67d ago]
  ⚠️ T-A1-V7 (A1): Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Phase 5（自動壓縮 [67d ago]
  ⚠️ T-A2-005-local-seo-factory (A2): 本地 SEO Factory 骨架已建（Planner→Auditor 七階段）、三大 Pillar [52d ago]
  ❓ T-A2-006-ads-seo-wordpress-patrol (A2): 狀態未標記 [日期不明]
  ❓ T-A2-SEO-CATERING-MATRIX-001 (A2): 狀態未標記 [日期不明]
  ⚠️ T-A2A3-001-B (A2): WordPress post `1696` 已建立為未發布草稿並重載驗證：`https://www. [29d ago]
  ⚠️ T-A4-001 (A4): S11(2024) 🔄 補跑中，10,050/12,213（82.2%），TODO=2,163，Colab 已重? [68d ago]
  ❓ T-A4-002 (A4): 狀態未標記 [日期不明]
  ⚠️ T-A4-003-photo-alt-pipeline (A4): 等 36,676 張處理完 → Owner 改 Drive 串流 → 釋出 ~433GB [14d ago]
  ⚠️ T-A4-004-photo-classify (A4): 批次跑完後 `--status` 查進度，續開下一批直到 ~98,400 張完成 [14d ago]
  ⚠️ T-A5-002 (A5): Owner 三題已回答（2026-06-23）→ 已加 `fixMasterTemplate_()` 到 Code. [2d ago]
  ⚠️ T-A5-004 (A5): Slide 可用。剩餘：品牌色票更新（CREAM/GOLD/DGOLD）、GAS 舊版檔 [77d ago]
  ⏳ T-A5-005 (A5): `clasp push --force` 已成功部署 8 檔（含 syncQuoteStatus_ / setupSyncTri [1d ago]
  ⚠️ T-A6-001 (A6): Case Store v0 已接到現有 `CONVERSATION_LOG`；A6 Telegram 新增 `/linecase [6d ago]
  ❓ T-A8-001-folder-to-video-distribution (A8): 狀態未標記 [日期不明]
  ⚠️ T-B1-B4-investment-os-role-split (??): B1-B4 已不只做角色拆分；新增 RSI-like 成長閉環，下一步是把  [6d ago]
  ❓ T-B1-DASH-001 (??): 狀態未標記 [日期不明]
  ❓ T-HQ-001 (??): 狀態未標記 [0d ago]
  ⚠️ T-IOS-KOL-001 (??): - **接續點**：四個每日時段（02:30/08:30/14:30/21:20）的 Telegram di [4d ago]

【暫停/待開始】
  🔲 T-A1-SYNC-GUARD-001 (A1): 待開始
  🔲 T-A1-V6-P3 (A1): 待開始
  🔲 T-A2-003-weekly-wp-audit (A2): 待開始
  🔲 T-A2-004 (A2): 待開始
  🔲 T-A5-006 (A5): 待開始
  💤 T-A6-002 (A6): 暫停中 [78d ago]
  💤 T-A7-001 (A7): 暫停中 [88d ago]
  💤 T-B1-001 (??): 暫停中 [日期不明]
  🔲 T-GBP-001 (??): 待開始

【已完成】6 張 Task Card

```
