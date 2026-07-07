# Loop-02 頁面品質報告
更新：2026-07-07 22:23

## GOAL
maplab.com.tw 所有文章 CTR ≥ 0.02 且 Position ≤ 20

## 執行步驟（Claude Code / MCP 呼叫）

請用以下 MCP 呼叫抓數據：
```
mcp__google-search-console__search_analytics
  siteUrl: sc-domain:maplab.com.tw
  dimensions: [page]
  startDate: 28daysAgo
  endDate: today
  rowLimit: 100
```

## 低質頁篩選條件
| 條件 | 閾值 | 優先級 |
|------|------|-------|
| Impression > 100 AND CTR < 1% | 有曝光但沒人點 | 🔴 最優先 |
| Impression > 100 AND CTR 1-2% AND Position 10-20 | 改標題可進步 | 🟡 次優先 |
| Position 21-30 | 接近首頁但未入 | 🟢 觀察 |

## 待 MCP 執行後填入結果
（此檔由 loop_02_page_quality.sh 建立骨架，Claude Code 填入實際數據）

---
下次執行：2026-07-14 09:00
