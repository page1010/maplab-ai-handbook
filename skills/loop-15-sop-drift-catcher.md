---
# Skill: Loop-15 SOP 偏移捕手（A1 巡檢升級版）

> 來源：Fable5 Loop 工作流 #15，2026-07-07 Owner 指示接入 MAPLAB
> 用途：自動比對 CURRENT_STATUS.md 聲稱狀態 vs 實際 git commit 證據，偵測偏差

---

## Goal（停止條件）

```
GOAL: 所有 agent 聲稱 DONE/進行中 的任務，都有對應 commit 或文件變更作為證據。
STOP: 偏差數 = 0，或所有偏差已標記「已知/已上報」
```

## Loop 迭代邏輯

每次執行：
1. 讀 `CURRENT_STATUS.md` — 提取所有帶狀態標記的任務（✅/🔄/⚠️/🔴）
2. 讀 `git log --oneline -30` — 提取最近 30 筆 commit
3. 比對：聲稱 ✅ 的任務，在 commit 中是否有對應紀錄
4. 列出偏差清單（聲稱完成但找不到 commit 證據）
5. 自動修正可修正的（補充 CURRENT_STATUS 日期/出處）
6. 無法自修的 → 產出「偏差報告」格式推送到 Telegram

## 執行指令

```bash
# 手動觸發
bash scripts/loop_15_sop_drift.sh

# 巡檢中自動觸發（A1 每日巡檢 SOP 的一部分）
# 加入 checkpoint.sh 後觸發
```

## 偏差報告格式

```
【Loop-15 SOP 偏移報告】YYYY-MM-DD HH:MM
偏差數：N
---
[任務名] 聲稱狀態: ✅ | git 證據: 無 | 最近相關 commit: (無/xxxx)
[任務名] 聲稱狀態: 🔄 | 最後更新: 超過 48h 無 commit
---
建議行動：
- [任務名] → 補 commit 或改回 ⚠️
- [任務名] → 上報 Owner（超時 >7 天）
```

## 路由策略（Fable5 cheap-first）

- 例行比對 → 用本地 bash grep，不呼叫 Claude API
- 需要語意判斷（任務名稱模糊比對）→ 用 Hermes/gemma4
- 發現嚴重偏差（>5 個）→ 升級 Claude Sonnet，產出完整分析

## 整合點

- 觸發：`checkpoint.sh` 執行後自動調用
- 輸出：`state/loop_15_drift_report.md`（每次覆蓋）
- 警報：偏差 >3 → Telegram 推送

## 停止邏輯

```python
if drift_count == 0:
    print("GOAL REACHED: 無偏差")
    exit(0)
elif all_drifts_acknowledged:
    print("GOAL REACHED: 所有偏差已知/已上報")
    exit(0)
else:
    print(f"繼續：{drift_count} 個偏差待處理")
```
