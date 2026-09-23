# MAPLAB 真實案例 × WP × 音樂系列 01–10

狀態：`CASE_FIRST_INTAKE / SUPERSEDES_SERVICE_CATEGORY_PLAN`

日期：2026-08-27

## 本次修正

前一版從十個既有服務頁出發，雖然網址 live，卻沒有先證明每一題對應哪一個 Google Drive 真實案例；它只能算服務／曲風目錄，不能算案例產線。這一版改以 Drive「2026maplab外燴紀錄」的實際子資料夾為 01–10，素材數由 Google Drive connector 逐夾反讀。

每案的 WP 產出不預設為新文章。先走四選一：

- `existing_post_music_extension`：文章已存在，只補音樂／社群延伸。
- `existing_pillar_proof_module`：把案例 proof 補進既有 pillar 或子頁。
- `new_case_gap`：確認沒有意圖 owner、且真案例資料充分時才新建。
- `social_only`：素材量或搜尋意圖不足，只做社群／影音證據。

完整機器可讀資料與證據狀態：`case_first_registry.json`。

## 01｜邦尼兔托嬰畢業典禮（既有公開案例）

- Drive：[0717邦尼兔-托嬰畢業典禮](https://drive.google.com/drive/folders/1-QvMeLHYD4csqdRsv5aTBUXtrXiqosbL)，22 圖＋6 影片。
- 路由：`existing_post_music_extension`；既有文章 `tainan-daycare-graduation-catering`，不另開 slug。
- 已驗證主關鍵字：`台南畢業典禮外燴`；次：`托嬰畢業典禮茶點`、`畢業典禮甜點桌`。
- 音樂：明亮華語電子舞曲 × kawaii future-bass；124–126 BPM。
- 下一步：只重生 Owner 核准歌詞的正式母帶，不重寫已發布文章。

## 02｜服飾選品店開幕茶會（A2 v3 已完成公開來源三角查證）

- Drive：[0718-服飾店開幕茶會](https://drive.google.com/drive/folders/109Me7KABT1vHZ8tkqriF84Lgo3DTT5sX)，19 圖＋3 影片；資料夾內已有 A2 v3 查證稿。
- 路由候選：`opening_pillar_proof_module`，對應 `tainan-corporate-opening-tea-catering`；先查 live collision，再決定是否獨立案例文。
- 關鍵字候選：`台南開幕茶會外燴案例`；次：`店面開幕茶會`、`品牌開幕外燴`、`迎賓茶點`。
- 音樂：Nu-disco × city-pop；112 BPM，門打開與迎賓上升感。
- Gate：品牌類型已交叉確認，實際分店與 ASSET_LOG／逐圖 QA 未完成，關鍵字維持 candidate。

## 03｜派對空間抓周慶生（私人家庭案，公開匿名）

- Drive：[0726派對空間2館-抓周慶生](https://drive.google.com/drive/folders/1kfum6M-7VmHLNrSg0g8M_aspMEsN0uZk)，14 圖、無真影片；已有 A2 v1 SEO 草稿。
- 路由候選：`first_birthday_pillar_proof_module`，回填 `catering-one-year-old-party-tainan`，避免另開相同意圖頁。
- 關鍵字候選：`台南週歲派對外燴案例`；次：`台南抓周外燴`、`週歲甜點桌`。
- 音樂：Acoustic pop × light boom-bap；96 BPM，大人聲線的家庭儀式感。
- Gate：先完成 14 張 HEIC visual QA；無真影片，不先承諾 A8 長短片。

## 04｜美術館場域抓周

- Drive：[0816-美術館二館抓周](https://drive.google.com/drive/folders/1FI_ATrxSbs5PWwQ6dcIdKkprcRVAKXik)，20 圖＋6 影片。
- 路由候選：週歲 pillar proof 或 venue case gap；兩者不能同時假設。
- 搜尋意圖候選：`台南美術館抓周外燴`、`台南抓周場地`；**尚非 final keyword**。
- 音樂假設：Ambient acoustic pop × soft broken beat，保留場域空間與家庭儀式。
- Gate：先由報價／事件資料確認場館全名與公開邊界，再查 venue keyword 互搶。

## 05｜官田性別揭曉派對

- Drive：[0809外燴性別官田](https://drive.google.com/drive/folders/1LfioPhDbpr2AayWW5_J7dCzVPlaG49SE)，15 圖＋7 影片。
- 路由候選：回填 `gender-reveal-party-tips` 的真實案例 proof，不預設新 slug。
- 關鍵字候選：`台南性別揭曉派對外燴案例`；次：`台南性別派對`、`戶外家庭派對外燴`。
- 音樂：Pastel synth-pop × light UK garage；110 BPM，以期待／倒數／揭曉做節拍。
- Gate：先確認案型、影片人臉與揭曉隱私；公開稿不用家庭姓名、地址或內部日期。

## 06｜All for Kids 音樂會茶點

- Drive：[0815all for kids 音樂會](https://drive.google.com/drive/folders/1hVDM_3Ef0zav169Avftb2liyb32V0_ah)，6 圖＋2 影片。
- 路由候選：`new_case_gap` 或 `social_only`；8 件素材與搜尋需求未證明前，不硬開文章。
- 關鍵字候選：`台南音樂會茶點外燴`；次：`親子音樂會茶點`、`表演活動外燴`。
- 音樂：Playful chamber-pop × light breakbeat，讓現場音樂與中場招待有同一節奏。
- Gate：查官方活動資料、素材可用性與 live owner；若證據不足，保留社群 proof。

## 07｜國泰原美（先辨識活動，不由名稱猜題）

- Drive：[0815國泰原美](https://drive.google.com/drive/folders/1CvsJ1oTY5pITDBVVIG-T6357_4_cfE4v)，17 圖＋1 影片。
- 路由：`identity_first_then_choose_existing_vip_or_gap`。
- 主／次關鍵字：**暫緩**。資料夾名只辨識專案／場域，尚不能證明是建案接待、品牌活動或私人場次。
- 音樂：暫緩；活動型態確認後才選 lounge、city-pop 或其他聲音。
- Gate：報價／事件紀錄先還原活動目的，禁止用建案名稱直接推論 SEO 意圖。

## 08｜建商 × 美術館（兩日素材，先拆 source unit）

- Drive：[0815-0816建商美術館](https://drive.google.com/drive/folders/1D2Erf3phicJ0B_pXciPrwn4tl1ZGoP0I)，48 圖＋6 影片。
- 路由：`identity_first_then_vip_or_museum_case`。
- 主／次關鍵字：**暫緩**；先確認兩日是否同一活動、場館與品牌公開權限。
- 音樂假設：若證明為建案 VIP 接待，再測 Lounge house × art-pop。
- Gate：54 件素材先按日期／source unit 拆分，再做人臉、外部品牌與可公開性 QA。

## 09｜企業／品牌活動（訊聯細胞，案型待還原）

- Drive：[0731-訊聯細胞](https://drive.google.com/drive/folders/1F_J7AaKIuQeThWnIG1eSZyc1gxnZPPrs)，15 圖＋2 影片。
- 路由：`identity_first_then_corporate_case`，可能回到 `corporate-catering-tainan`，但未查證前不定。
- 主／次關鍵字：**暫緩**；公司名稱不能替代活動類型。
- 音樂：待案型確認後再選 clean electro-funk 或 neo-soul。
- Gate：公司介紹只引用官方來源；活動目的、醫療／健康說法、品牌具名權限分開查。

## 10｜日照中心開幕（來源污染已標記）

- Drive：[0729日照中心開幕](https://drive.google.com/drive/folders/1aBCqsJefJpnYbUyxpjrr2twVNqcaghOC)，7 圖＋6 影片＋1 無關私人文件。
- 路由候選：`opening_pillar_proof_module`，回填開幕群組。
- 關鍵字候選：`台南日照中心開幕茶會外燴`；次：`機構開幕茶會`、`社區照護活動茶點`。
- 音樂：Organic neo-soul × gentle city-pop，溫暖、明亮、社區感。
- Gate：無關私人文件已明確排除，不作任何文案或事實來源；只從活動素材與報價／事件鏈重建案例。

## 執行節奏

1. 先跑 registry intake gate；本輪 10 案只證明真實資料夾與素材 inventory。
2. 一次只選一案跑 `--level wp --case-id ...`；PASS 後才完成公開資料三角、keyword final、文章與四張圖。
3. Owner 核過文章／歌詞後，才把同案交 A8；無真影片或 visual QA 未過時不先剪。
4. 每案結束回填：Drive folder ID、WP 路由、keyword status、圖片 file IDs、音樂 experiment ID、Owner gate 與公開連結。

## 本輪邊界

- 只讀 Drive 與既有 Sheet／Docs；未修改 Google Drive、ASSET_LOG 或 WordPress。
- 未建立九篇新文章、未生成九首歌、未剪片、未發布。
- 先前十個 live 服務頁仍可作 pillar／landing 參考，但不再冒充「十個案例」。
