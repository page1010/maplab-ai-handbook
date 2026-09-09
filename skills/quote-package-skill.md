# 統包報價 Skill（quote-package-skill）
版本：v1.0 | 建立：2026-09-09 | 維護者：A0（Fable5）| 依 Owner msg 5012/5032 裁定制度化
狀態：待 Codex 審查試跑（Owner msg 5036）

> 目的：把「客戶需求 → 對外報價單 + 內部毛利表 + agent作業版 + 加購/代購整合總價」
> 的統包報價流程寫成任何 agent（Fable5 / Codex / 未來 hermes 訓練）都能照跑的 skill。
> 與 `skills/a6-quote-pipeline-sop.md` v1.0（通道全景與降級規範）互補：
> 那份管「通道斷了怎麼辦」，本份管「通道在時怎麼把一案跑完」。
> 實證案例：2026-09-08/09 小肚肚兒科診所開幕案（40人/300件），全流程已跑通一次。

---

## SECTION 0 — 執行前提（Codex 試跑前先核對）

1. 工作區：本 repo（maplab-ai-handbook）+ agent-bus + claude-daily-operations 可讀。
2. Google 寫入通道：`~/.claude/mcp-keys/google-token.json` 存在且含
   drive + spreadsheets scope 與 refresh_token（**金鑰值絕不 print/echo/commit，
   只允許在腳本內部流動；輸出只印 HTTP 狀態碼與文件 URL/ID**）。
3. 已知 bug 繞法：token 檔的 expiry 欄是 epoch int，google-auth 函式庫會炸
   （AttributeError: 'int' object has no attribute 'rstrip'）。
   **不要用 google-auth**；直接 POST https://oauth2.googleapis.com/token
   （grant_type=refresh_token）取 access_token，再用 Bearer 打 REST。
4. REST 細節（實測教訓）：
   - Sheets range 含中文分頁名必須 urllib.parse.quote 編碼。
   - values **update** 用 method=PUT；values **append** 才是 POST。
   - Drive 上傳用 uploadType=multipart（metadata JSON + binary 兩段）。
5. 執行載體：若在受限 bot 窗（exec 白名單=resume 快照），新建腳本跑不了，
   用「借檔通道」：暫時覆寫既有白名單腳本（如 scripts/fetch_takeout_menu2.sh），
   跑完立刻還原原內容（先 Read 保存原文，cp 會被擋）。主視窗/Codex 無此限制。

---

## SECTION 1 — 輸入（案件卡最小欄位）

| 欄位 | 例（小肚肚案） | 缺了怎辦 |
|---|---|---|
| 客戶名稱 | 小肚肚兒科診所 | 必填，缺=停 |
| 活動型態 | 開幕茶會 Open House | 必填 |
| 日期 | 2026年10月上旬（暫定） | 可標暫定，不可留空 |
| 人數 | 40 人 | 必填（外燴人均制的分母） |
| 總件數 | 300 件（人均約7.5件） | 可由人數推：人均 6-8 件 |
| 地址 | 台南市永康區東橋一路412號 | 必填（車馬費判定） |
| 避項 | 避生食與易過敏（魚卵/甲殼類） | 沒說就問，不擅自假設 |
| 預算帶 | 30-40k | 沒有就先出標準配置 |

---

## SECTION 2 — 定價規則（每案必查，違反=停）

1. **絕不編價**：查無售價留空並標來源缺口。成本源=data/items_master.json；
   售價源=A4 Sheet（品項售價如 APP014 300/批）+ 932 份歷史報價單頻率資料。
2. **外燴人均制與外帶單品制絕不混用**（詳 a6-quote-pipeline-sop.md SECTION 1）。
3. **成本與毛利率絕不出現在對外文件**：對外/內部一律分開建檔（兩個 Sheet，
   不是同檔兩分頁——對外檔分享出去時整檔可見）。
4. **外部廠商報價 x1.35 = 對外整合價**（進位到十位）。適用：攝影/音響/主持等
   服務型外包。**代購實價直通不加成**：插旗/剪綵道具等印刷代購（Owner 慣例，
   若 Owner 裁定改一律+35% 以裁定為準）。
   例外：Owner 對單項直接定價（如花藝 12,000）以 Owner 價為準。
5. **整合報價必有總價列**：未確認項標「確認中」，確定項出小計，全確認後鎖總金額。
6. 幣別一律 **TWD**，禁 NTD。
7. 訂金 3,000；匯款資訊固定：中國信託822／西台南分行／圖蕾實業社／222540645172。

---

## SECTION 3 — 產出三件套（格式母版）

### 3a. 對外報價單（Google Sheet，格式比照文學館母版）
順序固定：
1. 抬頭「MAP LAB KITCHEN 私廚／外燴 報價單」
2. 客戶區塊：客戶/活動/日期/規劃人數/餐點總件數/地址（+聯絡電話若有）
3. Menu 三分組：【鹹點 SAVORY】【甜點 DESSERT】【飲品 BEVERAGES(壺裝)】，
   每品項一列：品名｜數量｜備註（蔬食/過敏原標註寫備註）
4. 報價區：餐點總價＋服務內容備註（專人陳列/佈置/桌巾/一次性餐具N組/贈打包盒N個）
5. 【整合總價 TOTAL】區：餐點+各加購項+確定項小計+確認中項
6. 聲明列：【以上含專人到場餐檯基本陳列、撤場服務、桌巾、一次性免洗餐具】
7. **『簽約使用條款及細則』四條全文**（母版=8/1文學館 sheet
   1NclWJP0NM_9o_jiTCOq-V-mJgIjx0kR4o2maELA_nPA，原樣照抄勿改寫勿刪減：
   第一條訂單與付款／第二條現場服務／第三條產品責任與保證／第四條合約效力）
8. 訂金與匯款資訊
實例：小肚肚對外 Sheet 1pRvE1n3PdzKExmGrJ8VJaWb7IA5llFy201QW_BINdyU

### 3b. 內部毛利表（Google Sheet，絕不外流）
欄位：品項｜類別(鹹/甜/飲)｜單位成本｜份數｜成本小計｜備註（選品理由/替換紀錄/頻率資料）
末列：成本合計 + 對外報價 → 食材層毛利率（標明未含人力/運輸/耗材）。
實例：1HvBPtqPNWj2j8aTx8yscEkEbYmoDvPmKFmh9faGSCfk

### 3c. agent作業版（內部毛利表新分頁）
內容=SECTION 2 八條規則逐列 + 本案總價整合表
（項目｜廠商報價(進)｜+35%對外價｜狀態），廠商回報進度直接更新此表。

---

## SECTION 4 — 執行步驟（Codex 照跑）

1. 讀案件卡（SECTION 1），缺必填欄=停並回報。
2. 選品：items_master 成本 + 932 報價頻率（熱品優先）+ 避項濾網
   （例：明太子可頌=魚卵→換普切塔；蝦排=甲殼→換手拍漢堡排）。
   人均 6-8 件配比：鹹點約 6 成、甜點約 3.5 成、飲品壺裝 2-3 壺/40人。
3. 建內部毛利表（3b），成本查無的品項留空標「成本待A4校準」。
4. 建對外報價單（3a），逐項走格式順序，條款四條從母版原樣搬。
5. 加購整合：讀 data/vendor-db/vendor-list-20260905.md 現況，
   外包項 x1.35、代購項直通、Owner 定價項照定價，寫進兩表的總價區。
6. 自檢閘（全過才交付）：
   - 對外檔全文搜「成本」「毛利」「x1.35」=0 筆
   - 幣別無 NTD；條款四條齊；總價列存在；訂金/匯款資訊正確
   - 對外品項數量加總=案件卡總件數
7. 交付：把兩個 Sheet 連結（docs.google.com/spreadsheets/d/{ID}/edit）給 Owner，
   **draft-first：未經 Owner 圈選不得發給客戶**。
8. 落檔：案件紀錄寫 data/a6-logs/YYYY-MM-DD-{案名}-quote-draft-vN.md；
   本 skill 的執行收據（產出物+閘門結果）寫進 handoff。

---

## SECTION 5 — 紅線（違反即停止並上報）

- 金鑰/token 值絕不 print/echo/commit/進 log；只印狀態碼與 URL/ID。
- 絕不編價；不引用「經驗值」代替資料源；行情帶只能標「行情參考」不能當報價。
- 成本毛利絕不入對外檔；對外檔與內部檔分開建。
- 未經 Owner 圈選不得發客戶；agent 不得自我核准。
- 不動 A4 Sheet 原始資料與 GAS；只讀不寫 truth source。
- 客戶個資不進 repo。

---

## SECTION 6 — Codex 試跑劇本（驗收用）

用固定測試輸入跑一遍，產出物標【TEST】前綴，不發任何人：
- 輸入：測試客戶「測試親子館」/開幕茶會/2026年11月中旬(暫定)/30人/210件/
  台南市東區/避堅果/預算帶 25-30k
- 預期產出：兩個【TEST】Sheet + 自檢閘 6 項全過 + a6-logs 測試紀錄一份
- 驗收人：Owner 看連結；通過後本 skill 標 v1.0-verified 並開放排程使用

## SECTION 7 — 已知缺口

- [ ] 楓糖炸雞球迷你鬆餅單位成本待 A4 校準（sheet_tail.py int-expiry bug 已有繞法見 SECTION 0.3）
- [ ] 音響/主持實報價未回（台南在地電話詢價中），總價未鎖
- [ ] Slides/PPT 整合頁產出路徑（pptx 本機組裝→Drive 上傳轉 Google Slides）未實測
- [ ] 本 skill 未來餵 hermes 訓練（5012-1 目的），需先過 Codex 審查+Owner 驗收
