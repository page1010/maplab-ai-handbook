# Google Drive API 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

與 Google Sheets **共用同一組 OAuth 憑證**：

| 檔案 | 路徑 | 說明 |
|------|------|------|
| OAuth 憑證 | `~/.claude/mcp-keys/google-credentials.json` | OAuth 2.0 client_id / client_secret |
| Access Token | `~/.claude/mcp-keys/google-token.json` | access_token + refresh_token（自動刷新） |

---

## 取用方法

### A. 透過 MCP（推薦，A1 Claude Code session 內）

直接呼叫 `google-drive` MCP tool：
```
# mcp__google-drive__get_file(...)
# mcp__google-drive__list_files(...)
```

注意：`google-drive` MCP server 使用 `GOOGLE_CREDENTIALS_PATH`，
與 Sheets 的 `CREDENTIALS_PATH` 略有不同（但指向同一個 json 檔）。

### B. Python（token 取用方式同 google-sheets-api.md）

Scope 需加入 Drive：
```python
scopes=["https://www.googleapis.com/auth/drive.readonly"]
```

---

## 可用範圍

| 允許操作 | 對象 |
|---------|------|
| ✅ 讀取 | 報價單資料夾（Owner 分享的 Google Drive 目錄） |
| ✅ 讀取 | ASSET_LOG（素材紀錄） |
| ✅ 讀取 | 照片素材資料夾（A4 pipeline 來源） |
| ✅ 上傳 | 素材到指定資料夾（A4 / A8 pipeline） |

---

## 禁止操作

- ❌ 刪除任何檔案（moveToTrash / delete）
- ❌ 修改共用權限（shareFile 需 Owner 確認）
- ❌ 移動 Owner 手動整理的資料夾結構

---

## Token 過期恢復

同 google-sheets-api.md — 重新執行 MCP server 授權即可（兩者共用 token）。

---

## 重要資料夾 / 檔案 ID

| 資料夾/檔案 | ID | 說明 |
|--------|-----|------|
| **MAPLAB_DATA（根目錄）** | `19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt` | 所有 MAPLAB 資料根目錄 |
| **line_oa_chat_csv** | `1bS77rE0-RcdNpAEI0U0yxPFI5DhkiNFR` | A層對話 CSV（LINE OA 匯出，業務↔客人），格式：傳送者類型/名稱/日期/時間/內容 |
| 歷史報價單 | `17wM4wldkllDbj0T8Xg_rgY3mM3RgH7LG` | 932份報價（2024+2025+2026），品項提取來源 |
| MAPLAB_ASSETS | `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` | 活動素材（DST-CKE-001~005） |
| MAPLAB_Items_Photos | `1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT` | 品項照片 |
| MAPLAB_Proposals | `1uGBCSTLFRVm5ZPh6v10G-tImf2QB5deu` | 提案資料 |
| MAPLAB_報價單 | `1aJBnL_fAmMDsNUqMPmLo07KWS47bnSBd` | 報價單 |
| ✅ 已結案_Completed Orders | `1k8BtS1AEdyCuupOnWqPye9qUVyrSax9Q` | 已結案訂單 |
| ❌ 未成交_Lost Quotes | `1RMWBdXYYqtFPmBMss8cNrUFtaXiSgu_2` | 未成交報價 |
| 📋 進行中_Active Orders | `1vCiqYelK0Z24vLthVib9qqzw6Bdj2o4_` | 進行中訂單 |
| **MAPLAB_外燴系統_v0.1（主表）** | `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` | A5 報價系統、Items 主表、QUOTE_DRAFT、CONVERSATION_LOG |
| MAPLAB_MasterData_Sheets | `1d2_SiEXh5JT4lzjkgHDI5JU9UWBY9TiPlC8DaxkQnKs` | 主資料備份 |

## 主試算表分頁 ID（MAPLAB_外燴系統_v0.1）

| 分頁名稱 | sheetId | 說明 |
|---------|---------|------|
| DASHBOARD | 1041135542 | 系統概覽 |
| QUOTE_DRAFT | 2135827399 | **A5 報價單模板**（複雜格式，非簡單表格）|
| Items | 2137253687 | **品項主表**（item_id, category, standard_name, default_price[空], default_cost, unit）|
| SALES_INTAKE | 366814598 | 業務詢價進件 |
| CONVERSATION_LOG | 1795458209 | LINE 對話紀錄（目前只有客人→業務單邊）|
| Orders / OrderLines / OrderCharges | — | 訂單系統 |
| TERMS_MASTER | 387592355 | 條款模板（個人版/企業版）|

## ⚠️ 重要注意事項

- `Items.default_price` 欄**多數為空**，只有 `default_cost`（成本）有值
- 報價必須讀 Items 主表拿 `default_cost`，**不能自己發明售價**
- `QUOTE_DRAFT` 是複雜 Sheets 模板（有合併儲存格、公式），要填入正確欄位位置
