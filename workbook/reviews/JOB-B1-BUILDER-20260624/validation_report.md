# B1 Builder — Validation Report 2026-06-24

## Scope
T-HQ-001 P5 (log rotate) + P6 (Hermes memory SOP + A7 JSONL export) + Extension sync

---

## 1. Extension Sync (B1 Chrome Extension)

**Result: WAS stale → NOW refreshed**

| File | Before | After |
|------|--------|-------|
| B1.json generated_at | 2026-06-20T20:39:40 | 2026-06-24T22:53:32 |
| CURRENT_STATUS.md size | 52,507 B | 73,250 B (+40%) |
| AGENT_RULES.md size | 42,958 B | 47,470 B (+10%) |
| TASK_QUEUE.md exists | false | true |
| A6.json read_first | missing data-locations.md | added |

Build script: `python3 tools/ai_workbook/build_extension_task_modules.py`  
Result: `{"modules": 29, "rows": 594, "missing_sources": []}`  
JSON validation: all modules are valid JSON (build script validates internally)

---

## 2. T-HQ-001 P5 — Log Rotate Job

**Result: IMPLEMENTED**

| 交付物 | 路徑 | 驗證 |
|--------|------|------|
| Data policy doc | scripts/data-policy.md | Created ✅ |
| Log rotate script | scripts/log_rotate.sh | `bash -n` syntax OK ✅ |
| Launchd plist | scripts/com.maplab.log-rotate.plist | XML valid ✅ |

Launchd schedule: 每週一 03:00  
Target logs: telegram-logs/*.md, bot/bot.log, bot/launchd_*.log, hermes logs  
Rotate threshold: 10 MB  
Retention: keep 10 most recent rotated archives

**Owner 啟用指令**:
```bash
cp scripts/com.maplab.log-rotate.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.maplab.log-rotate.plist
```

---

## 3. T-HQ-001 P6 — Hermes Memory SOP + A7 JSONL Export

### 3a. A7 JSONL Export Script

| 交付物 | 路徑 | 驗證 |
|--------|------|------|
| Export script | scripts/export_a7_line_jsonl.py | py_compile OK ✅ |
| Launchd plist | scripts/com.maplab.a7-line-export.plist | XML valid ✅ |
| Hermes memory SOP | scripts/hermes_memory_sop.md | Created ✅ |

Smoke test: `python3 scripts/export_a7_line_jsonl.py --inputs-only --dry-run`
- DB found: data/case-store/a6_case_store.sqlite3 (23 rows)
- Output: 23 customer messages ✅
- Limitation flagged: LINE webhook 只含客戶訊息，QA pairs 需 LINE OA Manager CSV

### 3b. Hermes Memory Provider

Current status: `Provider: (none — built-in only)`  
Available local provider: `holographic` (no API key needed)  
**Action required: Owner 批准後執行 `hermes memory setup holographic`**  
Risk level: 低（本地儲存，不影響現有 SOUL.md 配置）

---

## 4. Dispatch Records Finding

- `workbook/telegram-dispatch/` 不存在
- 2026-06-17 已實作 dispatch receipt 機制（commits 9f84998/877af04）
- 需 Owner 在 Telegram 實際送出召喚後才會建立 TG-DISPATCH-* 目錄
- 上一輪 B1 工作（JOB-B1-BUILDER-20260620 Phase 1）的 Phase 2 由 A1 於 2026-06-22 完成（commit 4564c5f：/model 切換指令）

---

## 5. What was NOT done (out of scope)

- 不啟用 Hermes memory provider（需 Owner 批准）
- 不啟用 launchd jobs（需 Owner 手動 cp + launchctl load）
- 不 push main
- 不碰 Investment OS broker/runtime
