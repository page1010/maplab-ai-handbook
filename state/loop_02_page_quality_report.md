# Loop-02 頁面品質報告
更新：2026-07-10 10:07

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

## 執行狀態（2026-07-10 A1 實測）

🔴 **阻塞 — 非「尚未呼叫」，是「呼叫會失敗」**：實測 `mcp__google-search-console__search_analytics` / `list_sites` 回 `MCP error -32603: private_key and client_email are required`。

根因：`~/.claude/.mcp.json` 的 `google-search-console` 區塊指向 `~/.claude/mcp-keys/google-credentials.json`，但該檔是 **OAuth installed-app client**（`{"installed": {...}}`），不是 `mcp-server-gsc` 這個 MCP server 實作要求的 **Service Account** 憑證（需要 `private_key`/`client_email` 欄位）。`skills/credentials/google-search-console-api.md` 早已標註這個風險（「⚠️ 重要：GSC MCP server 可能需要 Service Account 憑證而非 OAuth client」），今日實測坐實。

**Owner action 需要**：
1. GCP Console 建立一個 Service Account，開通 Search Console API
2. 到 `search.google.com/search-console` → 設定 → 使用者和權限 → 把該 Service Account email 加為 `maplab.com.tw` 的擁有者/使用者
3. 下載 Service Account JSON key，存到 `~/.claude/mcp-keys/` 並更新 `~/.claude/.mcp.json` 的 `GOOGLE_APPLICATION_CREDENTIALS` 指向新檔案（或另開一個獨立變數，避免影響 Sheets/Drive 共用的 OAuth 憑證）

**Loop-02 腳本本身可正常執行**（`bash scripts/loop_02_page_quality.sh` exit 0，正確建立骨架並提示下一步），阻塞點單純是這份 MCP 的憑證類型不對，不是腳本邏輯或排程問題。

---
下次執行：2026-07-17 09:00
