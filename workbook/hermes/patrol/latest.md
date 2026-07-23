# Hermes Patrol Reaction Packet

- generated_at: `2026-07-23T09:00:06+08:00`
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
- blocked: `3`
- active: `0`
- stale_active: `0`
- unmarked: `21`
- paused_or_not_started: `8`
- done: `11`
- owner_related: `29`

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

### long-blocked-three-layer-review [high]

- owner_role: `A0/A1`
- target_task_card: `handoff/tasks/`
- why: 3 blocked tasks are older than 14 days: T-A2A3-001, T-A3-002, T-A7-002.
- next_step: Run three-layer blocker review and split false blockers into direct-do / delegated / true Owner action.
- patch_hint: 每張卡改寫接續點：誰負責、下一個命令、何時才需要 Owner。

Codex follow-up prompt:

```text
你是 MAPLAB A0/A1，運行在 Codex。
先讀 CURRENT_STATUS.md、pitfalls.md、workbook/hermes/patrol/latest.json，再讀相關 Task Card。

觸發 reaction: long-blocked-three-layer-review
原因: 3 blockers are stale
本輪目標: patch the top stale task cards with concrete next steps

輸出：更新相對角色下一步或產 task packet；若需要 Owner，必須是 5 分鐘內可完成的具體行動。
```

### task-card-status-normalization [medium]

- owner_role: `A1`
- target_task_card: `handoff/tasks/`
- why: 21 task cards have unmarked status, so patrol cannot decide reliably.
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
📋 每日自動巡查 — 2026-07-23 09:00

=== MAPLAB 系統巡查 2026-07-23 09:00 ===

[🔴 EXPIRED] Google OAuth token — auto-refreshing...
HTTP 400: {
  "error": "invalid_grant",
  "error_description": "Token has been expired or revoked."
}
⛔ Token refresh failed — invalid_grant: refresh token 已失效，需重新授權 (Owner 執行 OAuth flow)

【⚡ 本輪狀態遷移（四態狀態機，SECTION 25）】
  🔄→🟡 STALLED: T-IOS-KOL-001（最後活動 32d 前）
  → 已自動寫回 Task Card，無需 Owner 操作（可逆，SECTION 24）

【Owner 行動項】
  → T-A2-002-foodsafety-seo-cleanup: 等 Owner 決定 post 698 的「無麩質或低糖選項」FAQ 答案要不要改（A2 唯讀掃描，未動任何文章）
  → T-A2A3-001: RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL
  → T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作）
  → T-A7-001: Owner 確認 Zone B（NT$2,000？）+ Zone C（NT$2,500？）兩個數字
  → T-HQ-001: Owner pending（非 B1 blocking）

【阻塞中 — 等外部條件（⏸️/⏳/🔍）】
  ⏸️ T-A2-002-foodsafety-seo-cleanup (A2): 等 Owner 決定 post 698 的「無麩質或低糖選項」FAQ 答案要不要改（A2 唯讀掃描，未動任何文章） [15d ago]
  ⏸️ T-A2A3-001 (A2): RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL [59d ago]
  ⏸️ T-A3-002 (A3): 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） [115d ago]
  ⏸️ T-A7-001 (A7): Owner 確認 Zone B（NT$2,000？）+ Zone C（NT$2,500？）兩個數字 [4d ago]
  ⏸️ T-A7-002 (A7): 任務 1/2/3 需 LINE bot 後台權限；任務 5/8 需 TimeTree 權限（任務 9 已解除） [16d ago]
  ⏸️ T-HQ-001 (??): Owner pending（非 B1 blocking） [28d ago]

【進行中（🔄 IN_PROGRESS / 🟡 STALLED）】
  🟡 T-A1-EXT-001-dynamic-role-modules (A1): STALLED — （checkpoint.sh 自動補建，請 agent 填寫） [4d ago]
  🟡 T-A1-LEARNING-LOOP-001 (A1): STALLED — 建立 token capital registry，登記可複用 prompt / eva [4d ago]
  ❓ T-A1-RTK-001 (A1): 狀態未標記 [53d ago]
  🟡 T-A1-V6-P2 (A1): STALLED — 4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG  [3d ago]
  🟡 T-A1-V7 (A1): STALLED — Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Ph [3d ago]
  🟡 T-A2-005-local-seo-factory (A2): STALLED — 本地 SEO Factory 骨架已建（Planner→Auditor 七階?? [79d ago]
  ❓ T-A2-006-ads-seo-wordpress-patrol (A2): 狀態未標記 [37d ago]
  🟡 T-A2-SEO-CATERING-MATRIX-001 (A2): STALLED — 競品分析工作包已建立於 `workbook/reviews/JOB-A2-S [35d ago]
  🟡 T-A2A3-001-B (A2): STALLED — WordPress post `1696` 已建立為未發布草稿並重載?? [56d ago]
  ⏳ T-A4-002 (A4): IN_PROGRESS — 187GB Takeout（5 個 ZIP）確認存在 Drive，尚未解?? [95d ago]
  🟡 T-A4-003-photo-alt-pipeline (A4): STALLED — 等 36,676 張處理完 → Owner 改 Drive 串流 → 釋?? [41d ago]
  🟡 T-A4-004-photo-classify (A4): STALLED — 批次跑完後 `--status` 查進度，續開下一批直到 [41d ago]
  🟡 T-A5-002 (A5): STALLED — Owner 三題已回答（2026-06-23）→ 已加 `fixMasterTe [29d ago]
  ❓ T-A5-004 (A5): 狀態未標記 [104d ago]
  🟡 T-A5-005 (A5): STALLED — `clasp push --force` 已成功部署 8 檔（含 syncQuoteSt [29d ago]
  🟡 T-A6-001 (A6): STALLED — Case Store v0 已接到現有 `CONVERSATION_LOG`；A6 Telegr [14d ago]
  🟡 T-A8-001-folder-to-video-distribution (A8): STALLED — 任務已建立，Owner 要求 A8 從「閒置」轉為真?? [35d ago]
  ❓ T-B1-001 (??): 狀態未標記 [62d ago]
  🟡 T-B1-B4-investment-os-role-split (??): STALLED — B1-B4 已不只做角色拆分；新增 RSI-like 成長閉?? [34d ago]
  ❓ T-B1-DASH-001 (??): 狀態未標記 [32d ago]
  ⏳ T-IOS-KOL-001 (??): IN_PROGRESS — - **接續點**：四個每日時段（02:30/08:30/14:30/21: [32d ago]

【暫停/待開始】
  🔲 T-A1-SYNC-GUARD-001 (A1): 待開始
  🔲 T-A1-V6-P3 (A1): 待開始
  🔲 T-A2-003-weekly-wp-audit (A2): 待開始
  🔲 T-A2-004 (A2): 待開始
  🔲 T-A5-006 (A5): 待開始
  🔲 T-A5-007-codex-takeover (A5): 待開始
  💤 T-A6-002 (A6): 暫停中 [106d ago]
  🔲 T-GBP-001 (??): 待開始

【已完成】8 張 Task Card
  （最近異動 3 張，其餘見 handoff/tasks/）
  ✅ T-A4-001
  ✅ T-A2-007-seo-trio-review-20260707
  ✅ T-A2-001

【投資 OS 守夜人 + IS-HS】
  🟢 nightwatch 今日正常（0 警示）
  🔴 escalation_queue: 13 條 open+未推播（見 projects/investment-os-continuous-iteration-plan.md ④）
  🟡 IS-HS: 50/100（新鮮度=100% 警報通暢度=0%）

【B3 廣告觀察】
  ⚪ B3 廣告尚未啟動（Owner 去 Meta 建受眾包後，回報一句話或 UTM 有 b3 流量自動偵測）
  → 啟動後：回報「B3 開始跑了」或 GA4 出現 utm_source=meta_b3 流量
  → A1 偵測到後自動開始每日成效摘要並進例會

```
