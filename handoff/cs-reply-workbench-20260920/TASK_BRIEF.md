# 客服回覆工作台(CS Reply Workbench)— TASK_BRIEF

**開案:2026-09-20 22:1x|線別:A6/hermes|狀態:規格已定,實作排 9/21 投資晨班之後**

## Owner 原話(SSOT,msg 5545,2026-09-20T22:03:13)

> 看一下這個,這是我期待A7還是a6有一個回覆的客服系統最終的成品樣子,接入客人來訊的資料庫,用我們的資料訓練的模擬回覆,然後有一些選項提供我們業務快速回覆,如果不能掛在line至少可以快速複製貼上--https://www.instagram.com/reel/DbRSyhby7Zx/?stkn=YXlsdnNtbnVhOThx

- ~~IG 連結登入牆打不開,規格依 Owner 文字描述~~(舊值,9/20 22:2x 已作廢)→ **影片已抓回逐格看完**(msg 5553 Owner 授權借 Chrome 登入 session,fetch_ig_reel.sh + cookies;22 格存 ~/.maplab/ig/DbRSyhby7Zx/)。
- 「A7還是a6」:預設掛 **A6/hermes**(訓練資產都在這條線);A7 若另有所指等 Owner 明示。

## 影片實看結果(成品=Freemie,9/20 逐格分析)

示範 app 名 **Freemie**,本體是**手機自訂鍵盤**,在任何聊天 app(示範用 IG DM)內叫出:

1. **上下文注入=對話截圖**:「已附加截圖/貼上截圖」——把當前對話畫面截圖貼給它當上下文,不用接對方平台 API。
2. **語氣籤 3×3 宮格**:幽默/高情商/溫柔/曖昧/可愛/大男人/提升關係/同情心/撒嬌,點選後按「生成」。
3. **生成回覆**:標「3 則建議」,每則帶語氣標籤(示範:「溫柔|聽起來很棒,我也想見你。」),點一下直接填入輸入框送出。
4. **改寫模式**:先自己打字,再選語氣按「改寫」重寫成該語氣。
5. **設定頁=BYO API**:API Base URL(示範 openrouter.ai/api/v1)+API Key+Model(示範 google/gemma-4-26b-a4b-it:free)+「啟用 Freemie 鍵盤」。

**對我們的三個直接啟示:**
- **掛進 LINE 的正解=自訂鍵盤,不是 LINE API**:業務手機裝鍵盤即可在 LINE 內原地生成+上稿,免審核免自動發訊風險 → v3 從「LINE Messaging API 評估」改為「自訂鍵盤 vs Messaging API 兩案比較」,鍵盤案優先。
- **v1 面板互動照抄 Freemie 核心迴路**:貼上客訊(文字或截圖)→分類/語氣籤→3 草稿帶標籤→一鍵複製(桌面版把「填入輸入框」換成複製)。
- **紅線差異(絕不照抄的部分)**:Freemie 把對話截圖送 OpenRouter 免費模型=客資外送,我們**絕不做**;我們的生成端點只指本機 hermes 大腦(357 模板+SOP v3),客資不出門。BYO-endpoint 設計本身值得抄——鍵盤殼跟大腦解耦,將來殼不動換大腦。

## Owner 補充需求(SSOT,msg 5587,2026-09-21T10:25:16)

> 4.我們自己要做的,昨天新增一個github是外掛在虛擬鍵盤,快速回覆,期待我們開發的功能是我打開line Account 能跳出來快速回覆,僅限我和mina使用,用的必須是真實資料訓練出來的回覆不是agent猜測的回覆 之前說模擬訓練gym可以通過9成嗎？然後這個模擬要能夠接收回覆回寫,比如你的三個選項都不好,我自己寫的你要回饋到資料庫並想一下為什麼,然後用來改進。

拆解為硬需求(2026-09-21 起生效):
1. **載體定案=虛擬鍵盤外掛**(呼應 Freemie 結論);Owner 稱昨天新增一個 GitHub repo——本機各工作目錄未見新 clone、gh 指令沙盒擋,**待 Owner 貼連結**後依注入六條政策(clone 只讀、鎖 hash、先 diff、金鑰隔離)評估採用。
2. **使用者限定 Owner+Mina 兩人**:鍵盤啟用需白名單,不做公開發布。
3. **生成來源限真實資料**:357 真實模板+Drive 逐字稿檢索優先;無把握時寧可出「需人工」不出猜測句(與 fail-closed 四類一致)。
4. **驗收門檻=gym 通過率 90%**(Owner 5587 新設;歷史紀錄=詢價 gym 4 輪全 PASS,先前無「9成」數字承諾,自此以 90% 為門檻,測集=真實歷史來訊留出集)。
5. **回饋回寫閉環升為必要需求**(原 v2 提前):三選項被棄用+Owner/Mina 自寫版本→逐筆回寫資料庫,附「為什麼選項不好」差異分析欄→定期回灌模板庫與生成規則。

## 架構定案:辨識與回寫(SSOT,msg 5590,2026-09-21T10:35:57)

> 4.我現在想到的 他使用截圖辨識對吧？我們的已經接到客人訊息了 有寫一個sheet 收單向訊息,在這個架構少用得到嗎？用不到要如何辨識並即時回饋,再掃掃搜搜其他專案做法？

**自家收單管線實況(2026-09-21 盤點,檔證見 scripts/apps-script/LineWebhook.gs 與 bot_a6/case_store.py):**
- 收訊=LINE OA webhook → Apps Script doPost(LockService+message.id 去重)→ 外燴系統試算表 CONVERSATION_LOG 分頁 appendRow;8 欄=msg_id/case_id(手填)/timestamp/speaker/message/source/line_user_id/reply_to_msg_id。
- A6 bot 唯讀索引(case_store.py,spreadsheets.readonly → 本機 SQLite;/linecases 指令)。
- **缺口①:無任何回覆欄/回寫機制**;LINE API 不提供我方回覆內容(line-quote-assistant.md:64,132)→ **回寫責任天然落在鍵盤端**(唯一知道實際送出內容的元件)。
- ~~缺口②:管線活性最後確認=2026-05-19~~(舊值,SYSTEM_DIRECTORY_INDEX.md:585 記載過時)→ **9/21 10:44 唯讀探測實證管線活著**:CONVERSATION_LOG 共 6,851 資料列,最新來訊 2026/9/21 上午 10:16(當日 7 筆);探測工具=scripts/a0_convlog_tail.sh(只讀 timestamp/source 欄+bot 代答推播判讀,經旗標鉤子執行)。

**定案(截圖辨識降備援):**
1. 辨識「現在在回哪個客人」三層:主力=鍵盤面板列 CONVERSATION_LOG 最近未回來訊點選載入;輔助=長按複製客人末句→鍵盤讀剪貼簿→比對 sheet 鎖定客人;備援=截圖 OCR(僅 sheet 漏接來源;必須本機辨識不送雲)。
2. 回寫閉環落點=CONVERSATION_LOG 表尾加四欄:options_shown(當時三選項)/chosen_or_custom(選用或自寫版本)/diff_analysis(為什麼選項不好)/replied_at。鍵盤送出即回寫,呼應 5587 硬需求⑤。

**外部專案掃描結論(2026-09-21):**
- 截圖/剪貼簿派(Freemie、github.com/maneesh888/open-keyboard、github.com/pavan-marthala/ai_keyboard):iOS 鍵盤讀不到宿主畫面才被迫用截圖;我們有 webhook,不採為主力。
- Android 通知監聽派(github.com/DevsOnFlutter/reflex、github.com/it5prasoon/Auto-Reply-Android,NotificationListenerService+RemoteInput):等於重做 webhook 已有的事;僅當 webhook 漏接補位選項,P2。
- LINE OA 內建自動回覆:關鍵字罐頭,無真實資料學習、無人在迴路,不符需求;但 webhook 與人工聊天模式可並存=我們現行架構的官方依據。

## 目標成品(Owner 描述拆解)

1. **接入客人來訊的資料庫**:來訊集中一處,可瀏覽、可搜尋。
2. **用我們的資料訓練的模擬回覆**:每則來訊自動附 2-3 個草稿選項。
3. **業務快速回覆**:點一下複製貼上;LINE 官方 API 不在第一版(審核/費用/自動發訊風險)。

## 既有資產(不從零開始)

- hermes quote gym:**gold=357 則真實回覆模板**、SOP v3(一次性5W2H)、四輪模擬全 PASS、R5 品項 Sheet、定價/訂金裁決已入檔。
- 詢價 grounding 規則:先查 Drive 逐字稿;開幕=成人喝酒社交;問句不斷言;必問攝影期待產出。
- 品牌口徑六條(maplab-seo-brand-voice)。

## 安全欄(不因做殼而放寬)

- **客資全程不出本機**:raw LINE 訊息/客戶資料不得送任何第三方 API 或免費鏈上游;草稿生成只走本機或既核可通道。
- **hermes fail-closed 四類照舊**:不報價、不選菜、不承諾檔期、不判定飲食安全——這四類草稿一律標「需人工」,面板只給業務判斷輔助,不給可直接貼的成品。
- 報價類:絕不編價;內部核價=台南在地行情×1.35 鐵律,核價流程在面板外。
- TWD 禁 NTD;不虛構見證/數字;草稿=proposal-only,發出永遠是人。

## 分版計畫

- **v1(快速複製貼上工作台)**:本機 localhost 面板——來訊列表+每則 3 草稿選項(分類標籤:一般/需人工核價/需人工檔期)+一鍵複製+已回標記。**第0步=盤點來訊現況落點**(LINE 匯出?手動轉貼?A6 現有通道?),資料來源定了才定入庫格式。
- **v2(回饋回灌)**:記錄業務實際採用/改寫了哪個草稿,差異回灌模板庫(呼應 agent-fde-charter 回饋回灌守則)。
- **v3(LINE 掛接評估)**:~~官方 Messaging API 審核/費用/風險評估後再議~~(舊值)→ **兩案比較:自訂鍵盤(Freemie 模式,業務手機在 LINE 內原地用,優先)vs Messaging API**;兩案都預設不做自動發訊,生成端點都只指本機大腦。

## 工具建置三問(5500 規則)

- 誰消費:業務(日常回覆)+Owner(抽查草稿品質)。
- 何事件強制更新:新客訊入庫;模板庫/SOP 改版時草稿生成邏輯同步。
- 哪流程步驟讀:詢價回覆 SOP 第一步(先看面板草稿再人工定稿)。

## 排程

9/21 投資晨班(對帳→測試單方案→警報器實測→互抵通道查證)之後接續;第一個交付=v1 可點雛形+第0步盤點結果,完工回報附截圖。
