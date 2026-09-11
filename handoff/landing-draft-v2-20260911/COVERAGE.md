# COVERAGE — landing v3 視覺改版(2026-09-11)

BRIEF_SHA256: f56b52d339621d7eaa37f14cd3cbe027fa284fec06ab174fd283e7103d4cbb25

R1: 實開四站全頁截圖對齊(#2 petercallahan/#15 24carrots/#21 canapeclub/#23 socialpantry,存證 /tmp/bench-refs-20260911/)。抽出共同視覺語言落進 CSS:serif 標題字系(Georgia/Songti TC/Noto Serif TC)、全幅照片+漸層壓字、11px .4em 字距大寫 kicker、髮絲線分隔、單一米色畫布+一段深棕色帶、去掉 v2 全部色塊標籤/圓角卡片/灰底 logo 磚。桌機區塊垂直留白 120px 對齊 #2 的排版密度;類別磚=照片+scrim+白 serif 標籤+箭頭(照搬 #2 結構);雜誌式 7fr/5fr 不對稱交錯區(#5/#6);範例套裝三欄(#21);在地識別色帶區換台南場景(#23)。與現站風格斷開=達標修正 5130。
R2: 活潑但有質感:大圖說話+serif 質感字+節制配色;無公關腔句式,文案沿 R4 圈選稿未加浮誇詞。
R3: 首頁=終點站骨架保留:hero→三類別磚→套裝→雜誌區→在地帶→信任列→菜單/FAQ→終末 CTA;每區一張主圖;各區內文均 ≤60 字(逐區清點過)。
R4: 定位語=P2「台南最會辦派對的外燴團隊——企劃、視覺、餐桌一次到位」;副標「台南外燴 派對統籌 企業茶會」原樣入 hero。
R5: :root 只用 #8B5E3C/#5A3A1A/#C4A265 三企業色+米色畫布;#06C755 僅出現在三處 LINE CTA。
R6: 現站 wp-json media 全庫 200 件抓清單,PIL 接觸表 4 張逐格目檢,只選 10 張**無烙字純照片**入版(hero=brand-conference-beauty-summit;類別=tech-factory-opening/art-museum-opening/old-money-birthday;套裝=canape-spread/tainan-buffet/tangdezhang-exhibition;雜誌=icc-catering-table/white-theme-birthday;在地=emba-concert-tea-break)。自帶文字海報零使用=修正 5130 主訴;圖源=現站素材過渡層,348 批次放行後可升級換圖。
R7: LINE CTA 三處(首屏 hero 按鈕/懸浮圓鈕/終末色帶按鈕),連結均 lin.ee/IP8nt4n。
R8: 全文無見證/數字/場次虛構(信任列只列既有品牌名文字,無編造數字);無 NTD 字樣(本頁無價格);無對號入座文案。
R9: playwright chromium 390×844(dsf2)+1280×900 全頁:兩檔 scrollWidth==innerWidth 無橫捲無截斷=機器閘 PASS;QA 截圖已上 Drive anyone-reader(mobile=drive.google.com/file/d/1CE4O1u0XP7fCHduQrCOiR_d2lVFUp6dl/view;desktop=drive.google.com/file/d/1RAQ1l5iq2gLKeVdWXw7nEuM1RIAOgiue/view);Owner 圈選前不碰 WP。
