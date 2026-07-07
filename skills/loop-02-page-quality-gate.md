---
# Skill: Loop-02 程式化頁面品質關卡（A2 Search Console 接入版）

> 來源：Fable5 Loop 工作流 #2，2026-07-07 Owner 指示接入 MAPLAB
> 用途：每週自動從 Search Console 抓低質頁，產出 A2 SEO 優化待辦清單

---

## Goal（停止條件）

```
GOAL: maplab.com.tw 所有文章 CTR ≥ 2% 且 Position ≤ 20
STOP: 低質頁數 = 0，或達標率 ≥ 95%
```

## 低質頁定義（可調整）

| 指標 | 閾值 | 說明 |
|------|------|------|
| CTR | < 1% | 有曝光但沒人點 |
| Position | > 30 | 根本沒排上 |
| Impressions | > 100 | 有足夠樣本才算 |
| 組合 | CTR<2% AND Position 10-30 | 有機會優化的頁面 |

## Loop 迭代邏輯

每週一執行：
1. 用 Search Console MCP 抓過去 28 天數據
   ```
   mcp__google-search-console__search_analytics
   siteUrl: sc-domain:maplab.com.tw
   dimensions: [page]
   dateRange: last28Days
   ```
2. 過濾低質頁（符合上表任一條件）
3. 產出清單，依「優化 CP 值」排序：
   - 高 impression + 低 CTR → 優先（改標題/描述）
   - 中等 position (11-20) → 次優先（補內容/建連結）
4. 寫入 `state/loop_02_page_quality_report.md`
5. 若低質頁 > 5 → Telegram 推送摘要給 A2

## 執行指令

```bash
# 手動觸發
bash scripts/loop_02_page_quality.sh

# launchd 每週一 09:00 自動執行
# plist: launchd/com.maplab.loop-02-page-quality.plist
```

## 報告格式

```
【Loop-02 頁面品質報告】YYYY-MM-DD
低質頁總數：N / 達標率：X%
---
優先優化（高 impression + 低 CTR）：
1. [頁面URL] CTR:0.8% Pos:15.2 Imp:320 → 建議：改 meta title
2. ...

次優先（Position 20-30，有機會推上去）：
1. [頁面URL] CTR:1.2% Pos:24.1 Imp:180 → 建議：補 FAQ 內容
---
GOAL 進度：達標率 72%（目標 95%）
```

## 路由策略

- 數據抓取 → Search Console MCP
- 排序計算 → bash + awk（不用 Claude）
- 優化建議 → Hermes/gemma4（pattern-match 常見問題）
- 複雜文章重寫建議 → 升級 Claude Sonnet

## 整合點

- 輸出：`state/loop_02_page_quality_report.md`
- 待辦：自動加入 A2 Task Card
- 觸發 A2 工作：若有 >3 篇「標題優化」→ 自動產草稿任務

## MCP 呼叫範例

```python
# 低質頁篩選
result = mcp__google-search-console__search_analytics(
    siteUrl="sc-domain:maplab.com.tw",
    dimensions=["page"],
    startDate="28daysAgo",
    endDate="today",
    rowLimit=100
)
low_quality = [r for r in result.rows
               if r.impressions > 100 and (r.ctr < 0.01 or r.position > 30)]
```
