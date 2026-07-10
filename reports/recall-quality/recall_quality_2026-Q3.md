# B5 召回品質審查 — 2026-Q3

> 執行者：B5（首次執行，由 A1 代理）
> 執行時間：2026-07-11
> 觸發源：Owner 核准 B5 角色後 A0 委派首輪執行
> 下次審查：2026-Q4（≥ 2026-10-01）

---

## 審查標準

| 標準 | 合格 | 不合格 |
|------|------|--------|
| 最後更新距今 | ≤30 天 ✅ | >30 天 ⚠️，>90 天 🔴 |
| fable-mindset.md 注入 | 有「每次 recall 必讀 docs/fable-mindset.md」 | 無此行 |
| superpowers-guide.md 路由 | 有「每次 recall 必讀 skills/superpowers-guide.md」 | 無此行 |
| 斷點時效 | 與 CURRENT_STATUS.md 一致 | 過時/不一致 |

---

## 各角色召回 Prompt 品質矩陣

| 角色 | 檔案 | 行數 | 最後 commit | 新鮮度 | fable | superpowers | 問題 |
|------|------|------|------------|--------|-------|-------------|------|
| A0 | A0_recall.md | 177 | 2026-07-10 | ✅ | ❌ | ❌ | 缺 fable/superpowers 注入 |
| A1 | A1_recall.md | 103 | 2026-07-10 | ✅ | ❌ | ❌ | 缺 fable/superpowers 注入 |
| A2 | A2_recall.md | 131 | 2026-07-03 | ✅ | ❌ | ✅ | 缺 fable 注入 |
| A3 | A3_recall.md | 46 | 2026-06-09 | ⚠️ 32d | ❌ | ❌ | 缺 fable/superpowers；T-A3-002 阻塞狀態未更新 |
| A4 | A4_recall.md | 51 | 2026-06-09 | ⚠️ 32d | ❌ | ✅ | 缺 fable；T-A4-001 ✅ 完成但 recall 未更新 |
| A5 | A5_recall.md | 56 | 2026-04-17 | 🔴 85d | ❌ | ❌ | 嚴重過時；T-A5-002/004/005 CRITICAL 狀態未反映 |
| A6 | A6_recall.md | 190 | 2026-06-27 | ✅ | ❌ | ❌ | 缺 fable/superpowers；有重複 A6_recall_compact.md |
| A6* | A6_recall_compact.md | 141 | 2026-06-27 | — | ❌ | ❌ | 重複檔，T-A1-V7 標記應刪除 |
| A7 | A7_recall.md | 41 | 2026-04-17 | 🔴 85d | ❌ | ✅ | 嚴重過時；T-A7-001 🔴 ~107h Phase 3 未啟動未反映 |
| A8 | A8_recall.md | 87 | 2026-06-20 | ⚠️ 21d | ❌ | ❌ | 缺 fable/superpowers；T-A8-001 ~312h 未更新 |
| B1 | B1_recall.md | 64 | 2026-07-07 | ✅ | ❌ | ❌ | 缺 fable/superpowers 注入 |
| B2 | B2_recall.md | 58 | 2026-06-20 | ⚠️ 21d | ❌ | ❌ | 缺 fable/superpowers 注入 |
| B3 | B3_recall.md | 47 | 2026-06-20 | ⚠️ 21d | ❌ | ❌ | 缺 fable/superpowers 注入 |
| B4 | B4_recall.md | 49 | 2026-06-20 | ⚠️ 21d | ❌ | ❌ | 缺 fable/superpowers 注入 |
| B5 | B5_recall.md | — | 2026-07-11 | ✅ NEW | ✅ | ✅ | 首次建立，含 fable/superpowers |
| IOS-SELL | IOS-SELL_recall.md | 70 | 2026-06-25 | ✅ | ❌ | ❌ | 缺 fable/superpowers 注入 |
| IOS_strategy | IOS_strategy_role_recall.md | 82 | 2026-06-03 | ⚠️ 38d | ❌ | ❌ | 缺 fable/superpowers；策略內容需比對 IS 現況 |
| WIN | WIN_recall.md | 70 | 2026-06-03 | ⚠️ 38d | ❌ | ❌ | 缺 fable/superpowers 注入 |

---

## 關鍵發現

### 🔴 緊急（影響巡查與派工準確性）

1. **A5 recall 過時 85 天**（2026-04-17）：T-A5-002/004/005 CRITICAL 狀態（~361h/~1680h）未更新至 recall，新 session 召喚 A5 會從過時斷點開始。
2. **A7 recall 過時 85 天**（2026-04-17）：T-A7-001 🔴 Phase 3 未啟動的 CRITICAL 狀態未反映，A7 新 session 不知道需要 Owner 介入。
3. **全 17 個 recall 檔 0 個有 fable-mindset.md 注入**：雖然 AGENT_RECALL_PROMPTS.md 的各角色 prompt 有注入，但獨立 recalls/*.md 文件全部缺失，召喚時若直接用 recall 文件會缺少 Fable 思維框架。

### ⚠️ 中等（影響能力繼承）

4. **A6_recall_compact.md 重複**：T-A1-V7 已標記應刪除，實際仍存在，造成使用者不確定要用哪個。
5. **A4 recall 未更新 T-A4-001 完成狀態**：T-A4-001 ✅ 已完成（07-09），但 A4_recall.md 仍停留於 2026-06-09 的 CRITICAL 狀態。
6. **B2/B3/B4 recall 缺 fable/superpowers（21天）**：B 系列召喚品質下降。

---

## 優先修復建議（給 A1）

| 優先 | 動作 | 受惠 |
|------|------|------|
| P0 | 更新 A5_recall.md（補 CRITICAL 狀態 + fable + superpowers） | A5 召喚準確性 |
| P0 | 更新 A7_recall.md（補 Phase 3 CRITICAL + fable + superpowers） | A7 召喚準確性 |
| P1 | 更新 A4_recall.md（T-A4-001 ✅ + fable） | A4 狀態一致 |
| P1 | 刪除 A6_recall_compact.md（T-A1-V7 已標記） | 去重 |
| P2 | 批次替所有 recall 加 fable-mindset 注入行 | 全系統 Fable 思維 |
| P2 | 更新 A8/B2/B3/B4/IOS_strategy/WIN recall（21-38天） | 一般新鮮度 |

---

## 下次審查時間

- **Q4 正式審查**：2026-10-01（下一季）
- **提前觸發條件**：任何角色 recall >30 天無更新，A1 巡查時提醒 B5 執行點審

---

> 附記：AGENT_RECALL_PROMPTS.md 中各角色 prompt 塊已注入 fable-mindset，與 recalls/*.md 獨立文件存在不一致。建議後續統一：要嘛 recall 文件內嵌完整 prompt（含 fable），要嘛加上明確指向 AGENT_RECALL_PROMPTS.md 的說明。
