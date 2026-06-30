# WordPress 憑證 → 登入 → 寫入：單一 SOP（拿鑰匙一頁通）

版本：v1.0 ｜ 建立：2026-06-29 ｜ 維護：A1 ｜ 適用：A2（SEO/WordPress 寫入）

> **目的**：把原本碎在 5 個檔的「拿鑰匙 → 登入 → 寫入 WordPress」收成一頁。
> 取代散讀：`skills/credentials/wordpress-api.md`、`skills/credentials/notion-api.md`、
> `AGENT_STARTUP_PROTOCOL.md Step 5.5`、`skills/gdrive-to-wordpress-upload-guide.md`、
> `recalls/A2_recall.md` 冷啟動補充。那些檔仍是細節來源；本頁是入口與決策樹。

---

## 0. 觸發時機

涉及 WordPress 寫入（建草稿 / 發布 / 上傳媒體 / 改 SEO meta）前，先讀本頁，照決策樹走，**不要只看 Chrome 有沒有登入就回 `auth_missing`**。

---

## 1. 鑰匙在哪（拿鑰匙）

- WordPress Email + Application Password 存在 **Notion API Keys 保管室**，page ID（只作路由）：`320ab0806d5c80e0be95f298399d2c44`。
- **Agent 不直接開 Notion**。由 Owner 提供，或 A0 透過 Notion MCP 受控取出後傳遞。
- **用完不存**：email、Application Password、Basic header、token、cookie、nonce、OTP、backup code 一律不得寫進 prompt、Chrome side panel、repo、memory、log、review bundle 或最終回覆。

---

## 2. 兩條寫入路徑（依場景選一條）

### 路徑 A — Chrome 既有登入態（無人值守發布首選）
適用：批次 / 排程 / SEO Factory 自動發布，且不想（也不該）持久化密碼。

做法（agent 只導頁 + 點登入，**不儲存、不手打密碼**）：
1. 用 Owner 已開的 Chrome / 受控 Chrome session（Chrome MCP）。
2. 導到 WP 後台登入頁。若已是登入態 → 直接進後台。
3. 若未登入：靠 **Google autofill（Owner Chrome 已存的密碼）自動帶入帳密**，agent 只負責「按登入」。
4. 進後台後執行寫入（建草稿 / 發布 / 上傳媒體）。
5. 全程不讀取、不輸出、不落地任何密碼字串。

安全紅線：agent 不得手動輸入密碼字元、不得把 autofill 的值讀出來、不得截圖含密碼欄位明文。

### 路徑 B — REST API（程式化草稿）
適用：需要程式化、可驗證的 draft 寫入。
- 用 Application Password 組 `Authorization: Basic <base64>` 打 `https://maplab.com.tw/wp-json/wp/v2`。
- 只建 `status=draft`；curl 範例與 meta 欄位見 `skills/credentials/wordpress-api.md`。
- Application Password 由 Owner/A0 當下供應，用完即棄，不寫任何持久檔。

---

## 3. 決策樹（何時才可 `auth_missing`）

```
要寫 WordPress
 ├─ Owner Chrome / 受控 Chrome 可用？ ── 是 → 路徑 A（autofill + 點登入）
 │                                     └ 否 ↓
 ├─ Application Password 可由 Owner/A0 當下供應？ ── 是 → 路徑 B（REST draft）
 │                                               └ 否 ↓
 └─ 以上全不可用 → 才輸出 auth_missing，並列出：已試方法、為什麼不能繼續、Owner 5 分鐘行動
```

---

## 4. 寫入邊界（紅線）

- 預設只 `status=draft`；**未經 Owner 精確批准不得 `publish`**。
- 不刪頁、不改 WordPress 用戶權限、不改 Google Ads / Meta Ads / GTM / Pixel / Rank Math 付費或預算開關。
- 寫入後用 WP REST / 前台 raw content 讀回驗證，回報 status、URL、category、featured_media、image IDs、FAQ、CTA。
- Landing page 內容須過 `recalls/A2_recall.md` 的「Landing Page 強制模板 Gate」與「A2 Conventions Lock v1」（命名 / 用色 / 用詞 / alt / 子頁）。

---

## 5. T-A2-005 阻塞解除路徑

T-A2-005（SEO Factory 自動發布）卡在「WP 寫入憑證無法持久化 vs 無人值守需常駐憑證」。
**解法 = 路徑 A**：用 Chrome 既有登入態 + Google autofill 帶密碼 + 按登入，agent 不持久化任何 secret，繞過「不可存密碼」與「自動發布」的衝突。

⚠️ **尚待實機驗證一次**：實際跑需 Chrome MCP + Owner 的 Chrome session 跑通一輪（登入態 → 建草稿 → 讀回驗證），驗過才可把 T-A2-005 標為解除。

---

## 6. Alt 文字格式（2026-06-30 已統一）

Alt 文字採單一標準（Owner 核可，B 式作廢）：
- canonical（A2 Conventions Lock v1 / visual-spec / wp-article-standard / gdrive 指南）：`台南{場景}外燴—{現場具體描述}`
- 舊式 `MAPLAB Kitchen {場景}｜{描述}`（B 式）已**作廢**；品牌名移檔名/caption。標準全文：`workbook/reviews/JOB-A1-ALT-TEXT-STANDARD-20260630/alt-text-standard-proposal.md`
