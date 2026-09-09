# 首頁 logo 牆改版執行卡（定案版，2026-09-09）

裁定鏈：5066（彩色+統一濾鏡、名單重設計）→ 5069（免同意，挑漂亮有識別性）→
5075（手機優先=§二B 憲法）→ 5079/5080（免圈定案：現牆全保留＋Fable5 加 14 家）→
5089（大台南會展中心不要）。

## 一、定案名單（淨新增 12 家）

**現牆約 40 家全保留**（合成圖上既有者全數視為確定）＋加入：

樂高、VOLVO、誠品、聯華電子、中鋼、富邦、和泰汽車、成大、成大醫院、
奇美醫院、中興工程、興富發。

減項：**大台南會展中心＝Owner 5089 撤掉不上**；**科林研發＝Lam Research
1992 年設立的台灣子公司（美商科林研發），logo 同 Lam Research——現牆已有，
歸併不重上**（2026-09-09 網路查核）。備選不上維持原判（建設類現牆已多；
三立/訊聯/璟馨全名未核實）。

## 二、logo 原檔來源（已逐一查證存在，2026-09-09；抓檔時以此為起點）

| 公司 | 來源 | 格式 | 備註 |
|---|---|---|---|
| 樂高 | https://commons.wikimedia.org/wiki/File:LEGO_logo.svg | svg | 紅黃彩色方標 |
| VOLVO | https://commons.wikimedia.org/wiki/File:Volvo-Iron-Mark-Black.svg | svg | 2021 後官方標誌本即單色黑；牆上照用單色版即正確 |
| 誠品 | https://zh.wikipedia.org/wiki/File:The_Eslite_Corporation_logo.svg | svg | zh.wiki 合理使用檔 |
| 聯華電子 | https://commons.wikimedia.org/wiki/File:UMC-Logo.svg | svg | |
| 中鋼 | https://zh.wikipedia.org/wiki/File:China_Steel.svg | svg | 官網 www.csc.com.tw 亦可 |
| 富邦 | https://www.fubon.com/financialholdings/story/identity.html | 網頁 | 官方企業標誌頁；圖 lazy-load 需瀏覽器抓 |
| 和泰汽車 | https://www.hotaimotor.com.tw/ | png | header /images/layout/logo.png |
| 成大 | https://zh.wikipedia.org/wiki/File:National_Cheng_Kung_University_logo.svg | svg | 官方識別系統 https://web.ncku.edu.tw/p/412-1000-18098.php |
| 成大醫院 | https://zh.wikipedia.org/wiki/File:National_Cheng_Kung_University_Hospital_logo.svg | svg | |
| 奇美醫院 | https://zh.wikipedia.org/wiki/File:Chi_Mei_Medical_Center_logo.svg | svg | 71×85 偏小，必要時官網補 |
| 中興工程 | https://www.sinotech.com.tw/EN/index.aspx | 網頁 | 此站=中興工程顧問股份有限公司；需瀏覽器抽 header logo |
| 興富發 | https://zh.wikipedia.org/wiki/File:Highwealth_Construction_logo.svg | svg | 62×49 偏小；官網對爬蟲 403 需瀏覽器 |
| （科林研發） | — | — | 歸併 Lam Research，不另抓 |
| （大台南會展中心） | — | — | Owner 5089 撤掉，不抓 |

授權註記：zh.wikipedia 本地檔＝合理使用授權；我們是展示「服務過的客戶」
非販售 logo 素材，屬名義性使用，但抓檔優先官網原檔、wiki 檔僅當墊檔。

## 三、統一濾鏡樣式 v1（Fable5 定案權限內先定，Owner 可否決）

- 彩色保留（Owner 5066：不做灰階退色牆）。
- 統一手法＝**容器統一＋輕濾鏡**：每 logo 去背或白底、等高排列（手機列高
  約 48px、桌機約 64px）、統一內距；全牆 CSS filter: saturate(85%)
  contrast(95%)，hover/輕觸回 100% 全彩。質感靠一致性，辨識靠彩色。
- 檔案規格：優先 SVG；點陣至少 2x 顯示尺寸（§二B 禁 UPSCALED）。

## 四、技術鐵則（抄自 landing-revamp-plan-v2 §二B，QA 閘必驗）

1. 現牆合成圖（corporate-our-parters）作廢，**拆原生區塊**：每 logo 獨立
   圖檔，手機 3 欄、桌機 4-6 欄自動換行。
2. 所有區塊先畫 390px 手機版再放大；發布前 QA 必跑 390px 全頁截圖：
   無截斷、無橫向捲動、內文字級 ≥16px。
3. 未經 Owner 圈選不發布（draft-first）。

## 五、棒次

1. **主視窗/win-01（需瀏覽器）**：照 §二 來源表抓 12 家彩色原檔落
   data/vendor-db/logos/（富邦/中興/興富發三家必須瀏覽器）；現牆
   合成圖上約 40 家的獨立原檔同批補抓（拆區塊前提）。
2. 濾鏡樣式 demo 頁（draft）→ Owner 過目。
3. 併入首頁改版 draft 頁執行卡（landing-revamp-plan-v2 §六流程）。

定案表（Sheet）：docs.google.com/spreadsheets/d/108o05fM-z_pgKOKYGt83uAWKNBZKlf2-jFlupVcVBqI
