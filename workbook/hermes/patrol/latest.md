# Hermes Patrol Reaction Packet

- generated_at: `2026-06-16T14:32:38+08:00`
- schema: `maplab.hermes_patrol_reaction.v1`
- repo: `/Users/pagemacmini/maplab-ai-handbook`

## Operating Decision

- Patrol delivery is not resolution.
- Hermes/local layer owns reaction, role next-step packets, and memory candidates.
- Codex/A1/B1 periodically verify repo/project progress and push concrete next steps downward.

## Runtime

- hermes_cli: `/Users/pagemacmini/.local/bin/hermes`
- model: `gemma4:latest`
- provider: `Custom endpoint`
- gateway: `✗ stopped`
- telegram: `Telegram      ✗ not configured`

## Counts

- total: `38`
- blocked: `4`
- active: `12`
- stale_active: `11`
- unmarked: `5`
- paused_or_not_started: `8`
- done: `9`
- owner_related: `17`

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
- why: 9 active tasks have no activity for 7+ days: T-A1-V6-P2, T-A1-V7, T-A2-005-local-seo-factory, T-A2A3-001-B, T-A4-001, T-A5-002.
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
- why: 5 task cards have unmarked status, so patrol cannot decide reliably.
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
ns/3.14/lib/python3.14/urllib/request.py", line 504, in _open
    result = self._call_chain(self.handle_open, protocol, protocol +
                              '_open', req)
  File "/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/urllib/request.py", line 464, in _call_chain
    result = func(*args)
  File "/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/urllib/request.py", line 1369, in https_open
    return self.do_open(http.client.HTTPSConnection, req,
           ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        context=self._context)
                        ^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.5/Frameworks/Python.framework/Versions/3.14/lib/python3.14/urllib/request.py", line 1324, in do_open
    raise URLError(err)
urllib.error.URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>
⛔ Token refresh failed — invalid_grant: refresh token 已失效，需重新授權 (Owner 執行 OAuth flow)

【Owner 行動項】
  → T-A2-002-foodsafety-seo-cleanup: 等 Owner 操作 WordPress 後台
  → T-A2A3-001: RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL
  → T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作）
  → T-A7-002: 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限

【阻塞中 — 等外部條件】
  ⏸️ T-A2-002-foodsafety-seo-cleanup (A2): 等 Owner 操作 WordPress 後台 [69d ago]
  ⏸️ T-A2A3-001 (A2): RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL [22d ago]
  ⏸️ T-A3-002 (A3): 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） [78d ago]
  ⏸️ T-A7-002 (A7): 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限 [78d ago]

【進行中】
  ❓ T-A1-EXT-001-dynamic-role-modules (A1): 狀態未標記 [日期不明]
  ❓ T-A1-RTK-001 (A1): 狀態未標記 [日期不明]
  ⚠️ T-A1-V6-P2 (A1): 4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG 精簡完成。下一步：建虛擬測試案例 → A6 跑報價流程 → 驗證寫入。 [57d ago]
  ⚠️ T-A1-V7 (A1): Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Phase 5（自動壓縮 ReMe）為加分項。 [57d ago]
  ⚠️ T-A2-005-local-seo-factory (A2): 本地 SEO Factory 骨架已建（Planner→Auditor 七階段）、三大 Pillar dry-run 可產生 draft payload。下一步 [42d ago]
  ❓ T-A2-006-ads-seo-wordpress-patrol (A2): 狀態未標記 [日期不明]
  ⚠️ T-A2A3-001-B (A2): WordPress post `1696` 已建立為未發布草稿並重載驗證：`https://www.maplabkitchen.com/wp-admin/pos [19d ago]
  ⚠️ T-A4-001 (A4): S11(2024) 🔄 補跑中，10,050/12,213（82.2%），TODO=2,163，Colab 已重啟等授權 [58d ago]
  ❓ T-A4-002 (A4): 狀態未標記 [日期不明]
  ⚠️ T-A4-003-photo-alt-pipeline (A4): 等 36,676 張處理完 → Owner 改 Drive 串流 → 釋出 ~433GB [4d ago]
  ⚠️ T-A4-004-photo-classify (A4): 批次跑完後 `--status` 查進度，續開下一批直到 ~98,400 張完成 [4d ago]
  ⚠️ T-A5-002 (A5): 核心公式已修正、e2e 通過。2026-05-19 已新增不改 master Sheet 的 A/B/C 副本產出接口，並修正 A5/A6 毛利口徑：優先看餐點 [27d ago]
  ⚠️ T-A5-004 (A5): Slide 可用。剩餘：品牌色票更新（CREAM/GOLD/DGOLD）、GAS 舊版檔案清理、Items english_name 確認 [67d ago]
  ⚠️ T-A5-005 (A5): 程式碼已寫入 Code.gs（syncQuoteStatus_ / setupSyncTrigger / setupDashboard / ensureInta [68d ago]
  ⚠️ T-A6-001 (A6): Case Store v0 已接到現有 `CONVERSATION_LOG`；A6 Telegram 新增 `/linecases`、`/case`、`/cas [27d ago]
  ❓ T-B1-B4-investment-os-role-split (??): 狀態未標記 [4d ago]
  ❓ T-B1-DASH-001 (??): 狀態未標記 [日期不明]

【暫停/待開始】
  🔲 T-A1-SYNC-GUARD-001 (A1): 待開始
  🔲 T-A1-V6-P3 (A1): 待開始
  🔲 T-A2-003-weekly-wp-audit (A2): 待開始
  🔲 T-A2-004 (A2): 待開始
  🔲 T-A5-006 (A5): 待開始
  💤 T-A6-002 (A6): 暫停中 [69d ago]
  💤 T-A7-001 (A7): 暫停中 [79d ago]
  💤 T-B1-001 (??): 暫停中 [日期不明]
  🔲 T-GBP-001 (??): 待開始

【已完成】7 張 Task Card
---
[2026-06-16 09:00:04] patrol-scheduled 開始
📋 每日自動巡查 — 2026-06-16 09:00

=== MAPLAB 系統巡查 2026-06-16 09:00 ===

[🔴 EXPIRED] Google OAuth token — auto-refreshing...
HTTP 400: {
  "error": "invalid_grant",
  "error_description": "Token has been expired or revoked."
}
⛔ Token refresh failed — invalid_grant: refresh token 已失效，需重新授權 (Owner 執行 OAuth flow)

【Owner 行動項】
  → T-A2-002-foodsafety-seo-cleanup: 等 Owner 操作 WordPress 後台
  → T-A2A3-001: RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL
  → T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作）
  → T-A7-002: 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限

【阻塞中 — 等外部條件】
  ⏸️ T-A2-002-foodsafety-seo-cleanup (A2): 等 Owner 操作 WordPress 後台 [70d ago]
  ⏸️ T-A2A3-001 (A2): RM/GSC 驗證需 Owner/A1 另開；目前不可把舊 planned slug 當 live URL [23d ago]
  ⏸️ T-A3-002 (A3): 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） [79d ago]
  ⏸️ T-A7-002 (A7): 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限 [78d ago]

【進行中】
  ❓ T-A1-EXT-001-dynamic-role-modules (A1): 狀態未標記 [日期不明]
  ❓ T-A1-RTK-001 (A1): 狀態未標記 [日期不明]
  ⚠️ T-A1-V6-P2 (A1): 4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG 精簡完成。下� [58d ago]
  ⚠️ T-A1-V7 (A1): Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Phase 5（自動壓縮 [58d ago]
  ⚠️ T-A2-005-local-seo-factory (A2): 本地 SEO Factory 骨架已建（Planner→Auditor 七階段）、三大 Pillar [43d ago]
  ❓ T-A2-006-ads-seo-wordpress-patrol (A2): 狀態未標記 [日期不明]
  ⚠️ T-A2A3-001-B (A2): WordPress post `1696` 已建立為未發布草稿並重載驗證：`https://www. [20d ago]
  ⚠️ T-A4-001 (A4): S11(2024) 🔄 補跑中，10,050/12,213（82.2%），TODO=2,163，Colab 已重� [59d ago]
  ❓ T-A4-002 (A4): 狀態未標記 [日期不明]
  ⚠️ T-A4-003-photo-alt-pipeline (A4): 等 36,676 張處理完 → Owner 改 Drive 串流 → 釋出 ~433GB [5d ago]
  ⚠️ T-A4-004-photo-classify (A4): 批次跑完後 `--status` 查進度，續開下一批直到 ~98,400 張完成 [5d ago]
  ⚠️ T-A5-002 (A5): 核心公式已修正、e2e 通過。2026-05-19 已新增不改 master Sheet 的 [28d ago]
  ⚠️ T-A5-004 (A5): Slide 可用。剩餘：品牌色票更新（CREAM/GOLD/DGOLD）、GAS 舊版檔 [68d ago]
  ⚠️ T-A5-005 (A5): 程式碼已寫入 Code.gs（syncQuoteStatus_ / setupSyncTrigger / setupDashboar [69d ago]
  ⚠️ T-A6-001 (A6): Case Store v0 已接到現有 `CONVERSATION_LOG`；A6 Telegram 新增 `/linecase [27d ago]
  ❓ T-B1-B4-investment-os-role-split (??): 狀態未標記 [4d ago]
  ❓ T-B1-DASH-001 (??): 狀態未標記 [日期不明]

【暫停/待開始】
  🔲 T-A1-SYNC-GUARD-001 (A1): 待開始
  🔲 T-A1-V6-P3 (A1): 待開始
  🔲 T-A2-003-weekly-wp-audit (A2): 待開始
  🔲 T-A2-004 (A2): 待開始
  🔲 T-A5-006 (A5): 待開始
  💤 T-A6-002 (A6): 暫停中 [69d ago]
  💤 T-A7-001 (A7): 暫停中 [79d ago]
  💤 T-B1-001 (??): 暫停中 [日期不明]
  🔲 T-GBP-001 (??): 待開始

【已完成】7 張 Task Card
---
[2026-06-16 09:00:06] 推送成功

```
