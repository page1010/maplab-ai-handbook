# Skill: 從 Notion 保管室取執行期密鑰（不落地）

> 建立 2026-06-25。所有需要 runtime 憑證的 agent 適用（A2 SEO 工廠、A6 報價、其他）。

## 何時用
agent 在 runtime 需要憑證（WordPress Application Password、API key、Google 憑證等）才能完成任務，而這些密鑰**不存在 repo**——統一放在 Notion 保管室。

## 真相來源
- Notion 頁：「🔑 API Keys 保管室 — maplab-pipeline」（id `320ab080-6d5c-80e0-be95-f298399d2c44`）
- 每筆密鑰有清楚標籤，例如：`WordPress Application Password (maplab-Detasys)`。

## 招式（runtime 取用流程）
1. 用 Notion API 讀該頁 block 內容；Notion integration token 放 OS keychain / 環境變數 `NOTION_TOKEN`，**不寫進 repo、不寫死**。
2. 依「標籤」抓出需要的那一筆值，只放記憶體。
3. 用完即丟，**只用於當下這次呼叫**。

## 絕對禁止
- ❌ 把密鑰值 print 到 log / Telegram / chat
- ❌ 寫進任何檔案 / commit / push
- ❌ 寫死在程式碼
- ❌ 從 repo 檔案讀密鑰（repo 不該有密鑰）

## 各用途
- **T-A2-005 SEO 工廠**：取 `WordPress Application Password (maplab-Detasys)` → 呼叫 WP REST 建**草稿**。本系統「草稿自動、發布人工」，取憑證只為建 draft，**實際 publish 仍由 Owner 手動**。
- **A6 / Google Sheets `invalid_grant`**：先看保管室有無 Google 憑證：
  - 若是 service-account JSON → 依此招取出、放程式預期路徑、重試。
  - 若是 OAuth refresh token 失效 → 需 Owner 在瀏覽器重新授權（agent 無法代做 OAuth 同意頁），取得新 token 後存回保管室。

## 邊界
取得密鑰 ≠ 可做不可逆動作。發布 / 送出 / 付款等仍依各任務確認規則，不因拿到密鑰就自動執行。
