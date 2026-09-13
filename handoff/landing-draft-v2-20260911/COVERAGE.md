# COVERAGE — landing v4 單一動線場景版(2026-09-13)

BRIEF_SHA256: cd5ddab4aa025e6ea63cce611f8c93c6ba31a121de2be51b1f4f4c192aa75db7

R1: 沿用 v3 已對齊四站的視覺語彙(serif 大標/滿版照壓白字/.4em kicker/髮絲線/米色畫布+深棕帶/無圓角卡片無色塊標籤);場景流改為 #5/#6 式 7fr/5fr 不對稱交錯,每場景一張大圖說話。
R2: 文案全頁每區 ≤2 句(R13 廢話刪),無公關腔;質感靠照片與留白。
R3: 首頁=終點站;場景格「看這場的紀錄→」直連案例/指南文章=分類進案例;每區一張主圖,內文 ≤60 字逐區清點過。
R4: hero=P2 定位語+副標「台南外燴 派對統籌 企業茶會」原樣。
R5: :root 三企業色+米色畫布;#06C755 僅 LINE CTA(hero/場景 LINE 詢價/懸浮/終末/頁尾)。
R6: 六張圖全為無烙字純照片,cover 僅用於純照片;無任何帶字海報。
R7: LINE 連結全站統一 lin.ee/IP8nt4n,首屏/懸浮/終末三處以上。
R8: 無虛構見證/數字/場次(900+ 提案=實數 932 份;信任列僅列已定案名單文字);無 NTD;無對號入座文案。
R9: 機器閘 playwright(chrome channel)390×844 與 1280×900:無橫向捲動無截斷 PASS;QA 截圖上 Drive anyone-reader(mobile=drive.google.com/file/d/1OVvFKH0UJQ9T5rTB2Smelf3rDOUaH579/view;desktop=drive.google.com/file/d/1CnCMe6a7jYi9yFBdKjfxQKrIB1hNjXQS/view)。QA 註記:lazy 圖在 full-page 截圖不觸發載入,截圖用同圖址 eager 副本+等頁高 viewport(hero/local 的 vh 換算為對應視窗高固定 px),正式版 index.html 保持 lazy。
R10: 圖片來源查核升級:自助餐檯照(tainan-buffet-menu)已撤除;v4 六張圖逐張以 wp-json 文章內文反查,全部對得到實際案場文章——hero=美妝高峰會(corporate-catering-tainan)、開幕=大新美術館 daxin-hero-3(daxin-art-museum-opening-catering)、企業茶會=大臺南會展中心(icc-tainan-catering)、品牌發表=汽車展間長桌(brand-esg-catering-service)、私人派對=週歲 candy bar(catering-one-year-old-party-tainan)、在地帶=EMBA 音樂會茶歇(corporate-tea-party-desserts);六張 HTTP 全 200。v3 查無文章出處的四張(tokyo-electron/old-money/tangdezhang/white-theme)全數不用。
R11: 全頁無占位/示意:雜誌示意區已刪,場景格連結=真實文章 URL(上列五篇+開幕/週年/茶會/詢問指南/費用/菜單 20 例),圖=真素材直上。
R12: 首屏只載 hero 一張圖(fetchpriority=high),其餘全部 loading=lazy+decoding=async;無 webfont(系統字);CSS 內嵌單檔;hero 為站方已壓縮 avif。
R13: menu 獨立區已取消,菜單邏輯逐場景寫入(開幕=跟著儀式走/茶會=跟著議程分批/發表=跟著品牌調性/派對=跟著主題色年齡層);每場景=真實照+做了什麼一句+菜單邏輯+文章連結+LINE。
R14: 無服務清單頁;統籌以做過的事帶出(「從剪綵到迎賓茶點的動線由我們統籌」);頁尾三行派對統籌+「聊聊你的場合」CTA。
R15: 三場合入口(開幕/週年/企業茶會)各列三項「會準備什麼」(剪綵道具/打卡點/菜單客製=AOP 服務當內容素材),各配既有指南文章連結;小肚肚成交後換真案例。
R16: v4 提案 9/11 22:2x 已送,Owner 5237(2026-09-13 11:00)「沒問題」=圈選通過後才動工本版;本版=提案的落地,交付連結後仍等 Owner 圈選才進 WP draft。
