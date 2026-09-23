# 卡:Top3 判斷層已上線,08-25 22:10 前需空跑驗證

- 建立:2026-08-24 22:40|來源:Owner 22:13 指正(晶技 3042 推播)|狀態:**已改碼,待驗證**
- 稽核依據:investment-os/reports/cogov_daily/2026-08-22/telbotfin_audit.md #5/#6(當時已判「舊 Top3 重播=停、一頁摘要=併晚報」,一直沒人執行)

## 已改(runtime:~/.local/share/investmentos-telegram-operator/scripts/send_ai_hermes_research_telegram.py)

1. import 加 datetime。
2. 新增 `_prefilter_top3()`:
   - roundtable 產出日期距今 >2 天 → 整個 Top3 區塊不發(修「08-17 批次連播多天」);
   - 候選過 position_aware_prefilter(持股∪watchlist),場外標的(晶技 3042 等)濾掉;
   - fail-soft:prefilter 載不進來只做過期檢查;全被濾掉 → 區塊靜默。
3. `build_messages()` include_top3 分支改走 gate;原本就無資料時保留舊提示,被 gate 靜默時不發占位訊息。

## 驗證(明天 22:10 之前,主 session 做)

```
cd ~/.local/share/investmentos-telegram-operator
.venv/bin/python scripts/send_ai_hermes_research_telegram.py --dry-run --include-top3
```
預期:stdout 出現 [top3-gate] roundtable 資料停在 2026-08-1x → 不重播;無 Top3 內文。
再跑 --dry-run --include-live 確認持股區塊行為不變。語法保險:.venv/bin/python -m py_compile 同檔。

## 殘餘問題(不在本卡內改)

1. **data/position_ledger/ledger.sqlite3 malformed** → holdings gate 現在是空集合,過濾只剩 watchlist(SMH、2371)。要修復/重建 snapshot;影響所有 position-aware 流程。
2. **repo↔runtime 漂移**:本 patch 只進 runtime;investment-os 源碼側同檔內容有差(render_top3_messages 行號不同),要先 diff 再鏡像,不可盲貼。
3. 稽核 C 段殘項:一頁摘要併入 18:45 晚報候選漏斗、TELEGRAM_SUCCESS_NOTIFY_JOBS 白名單清理。
4. Owner 裁決點:晶技 3042 要不要進 config/research_watchlist.yaml(要追蹤就加,不加=預設濾掉)。
