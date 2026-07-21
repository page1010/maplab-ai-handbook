# 廣告平台瀏覽器巡查（Google Ads / Meta Ads 唯讀狀態查詢）

> 版本 v1.0 ｜ 建立：2026-07-20 ｜ Owner 指定，取代原本靠 API/MCP token 查廣告現況的預設方式
> 適用：A2（SEO/廣告巡查）、A0、任何需要「看一下現在廣告在幹嘛」的角色
> 不適用：需要精確數字報表匯出、批量歷史資料、或任何**改動**廣告設定的操作（那些仍走 §5 的既有規則）

---

## 0. 為什麼要有這份技能書

Owner 2026-07-20 明確指示：**廣告平台的唯讀狀態查詢，不要再依賴會過期的 API 通行證。**

背景：Google Ads / Meta Ads 的 API 通行證（refresh token / access token）設計成有效期限，最常見是應用程式卡在
Google「測試中」狀態時 7 天就失效，需要人工重新登入才能恢復。這造成「查一次可以，隔一週鑰匙壞了，agent 又跳出來
要 Owner 花時間重新授權」的重複維護負擔——這正是 Owner 想解決的問題（見 `AGENT_RULES.md` SECTION 21 規則三：
不要讓 Owner 一直被丟需要處理的技術性待辦）。

**根本解法**：Owner 的 Chrome 本來就已經登入 Facebook / Google 帳號。廣告管理員後台（Meta Ads Manager、
Google Ads 介面）本身就是網頁，agent 只要導頁進去、**用看的、截圖分析**，不需要另外申請、維護、定期更新任何
API 通行證。瀏覽器登入態靠 Owner 平常使用瀏覽器自然維持，不會像 API token 一樣有固定到期日。

---

## 1. 什麼情境用這條路（唯讀狀態巡查）

- 「現在有哪些廣告活動在跑？」
- 「這個活動鎖定的受眾／年齡／地區是什麼？」
- 「目前用的素材（圖片/影片/文案）長什麼樣？」
- 「大概花費/曝光/點擊落在什麼區間？」（用介面上顯示的數字即可，不需要精確到小數點）
- 為了規劃 SEO 關鍵字 / 行銷整體策略而需要先了解「現在廣告在打什麼」

**這條路做不到、也不該做的事**：暫停/啟動廣告、改預算、改出價、新建廣告活動、匯出精確逐筆報表——這些仍是
「真的要動手改東西」的操作，維持既有規則（`skills/credentials/google-ads-api.md` / `meta-ads-api.md` 的
禁止操作清單、`AGENT_RULES.md` SECTION 24 不可逆動作需 Owner 核准），跟本技能書無關。

---

## 2. 怎麼做（SOP）

### 前提

- Owner 的 Chrome（或受控 Chrome session）已經登入 Facebook 帳號、Google 帳號。
- Agent 透過 Chrome MCP（或 computer-use 桌面控制）操作那個已登入的瀏覽器分頁，**不手動輸入任何帳號密碼**。

### 步驟

1. **導頁進廣告管理員後台**：
   - Meta：`business.facebook.com/adsmanager`（或 `adsmanager.facebook.com`）。若彈出「選擇帳號」，選 MAPLAB 對應的廣告帳號。
   - Google：`ads.google.com`，選對應的客戶帳號。
2. **確認已登入**：如果落到登入頁，優先用 Chrome 既有登入態／Google autofill 帶密碼、agent 只負責按登入鍵
   （比照 `skills/wp-credential-chrome-login/SKILL.md` 路徑 A 的原則：不手動輸入密碼字元、不讀出 autofill 值）。
   若真的沒有登入態可用，才輸出 `auth_missing`，不得自行猜測帳密。
3. **只讀，不點會改變設定的按鈕**：進到活動列表 / 廣告群組 / 受眾 / 素材頁面，只做瀏覽、捲動、放大截圖；
   不點暫停/啟動/編輯/刪除/複製等會改變帳戶狀態的按鈕。
4. **截圖 + 用視覺分析取得資訊**，記錄：
   - 活動名稱、狀態（啟用/暫停）
   - 受眾設定（年齡、地區、興趣、自訂受眾名稱）——讀畫面顯示文字，不用精確到後端 ID
   - 素材縮圖與文案重點
   - 畫面上顯示的花費/曝光/點擊/CTR 區間（用介面顯示的四捨五入數字即可，這條路本來就不是拿來做精確財報）
5. **整理成結構化摘要**，供 SEO 關鍵字與行銷整體規劃使用，格式建議：

   ```text
   platform: meta_ads | google_ads
   captured_at: <日期時間>
   route: browser_session (非 API)
   campaigns:
     - name: ...
       status: active/paused
       audience: ...
       creative_summary: ...
       spend_display: ...（畫面顯示值，非精確報表）
   caveats: 畫面數字為近似值；如需精確報表另走 API/MCP（見 §5）
   ```

6. 落檔到 `workbook/outputs/` 或對應 review bundle，不落地任何帳密/cookie/token。

---

## 3. 安全紅線

- 不手動輸入或讀出密碼、cookie、session token、OTP。
- 不點擊會改變廣告帳戶狀態的按鈕（暫停/啟動/刪除/編輯預算與出價/新建活動）。
- 不下載、匯出帳戶資料檔案（CSV/Excel 匯出視為資料匯出操作，需 Owner 另外核准）。
- 截圖若含個資（例如受眾自訂名單裡混入客戶清單檔名），先確認截圖範圍不外洩客戶個資再落檔。
- 這條路徑是**唯讀狀態巡查**，不是廣告帳戶管理；管理／花錢決定仍由 Owner 自己操作（Owner 2026-07-20 已明確表示這塊他自己來）。

---

## 4. 跟既有 API/MCP 通行證的關係（不是取代，是換優先序）

`CLAUDE.md`【API 存取三層備援】原本把 MCP（含 Google Ads / Meta Ads）列第一優先。**本技能書是這條規則在
「廣告平台唯讀狀態查詢」這個特定情境下的明文例外**：這個情境改成瀏覽器優先，理由是 API token 的到期維護成本
高於瀏覽器登入態，而唯讀狀態查詢本來就不需要 API 才能拿到的那種精確結構化數字。

API/MCP（`skills/credentials/google-ads-api.md`、`meta-ads-api.md`）仍保留，用在：

- 需要精確報表數字（GAQL 查詢、insights API 逐筆資料）。
- 需要批量／大量歷史資料分析。
- 需要程式化寫入（啟動/暫停/改預算，這些本來就需要 Owner 核准，跟走哪條讀取路徑無關）。

若 API token 本來就是活的（沒過期），需要精確數字時可以直接用；但**不需要為了「怕 token 過期」而特地去維護、
定期重新整理它**——過期就過期，等真的需要精確報表時再花兩分鐘重新登入即可，不是系統運作的常態依賴。

---

## 5. 關聯

- `skills/wp-credential-chrome-login/SKILL.md` — 同樣「瀏覽器既有登入態優先」原則的 WordPress 版本，本技能書的設計參照它。
- `skills/credentials/social-accounts.md` — FB/IG 讀取本來就已經是瀏覽器登入態優先，本技能書把同樣原則明文擴大到廣告管理員後台。
- `skills/credentials/google-ads-api.md` / `meta-ads-api.md` — API/MCP 路徑保留供精確報表與程式化操作使用。
- `AGENT_RULES.md` SECTION 21 規則三 — 本技能書是「減少 Owner 被丟技術性待辦」文化的具體落地案例。
- `docs/company-values.md` — 對應新增的「不依賴會定期過期的憑證做例行查詢」原則。
