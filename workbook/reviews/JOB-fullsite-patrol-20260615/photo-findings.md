# 照片狀態發現 — JOB-fullsite-patrol-20260615 (2026-06-16)

## 重大重新定位
- **58 篇全部都有 featured 圖（0 缺、58 張各自不同、無重複），且前台會渲染。**
- 所以「沒照片的文章補一張」其實已大致滿足——每篇都有一張 featured 照片顯示。
- matrix 的「imgs=0」是指**內文沒有 inline 圖**，不是沒照片。

## 真正的照片問題＝非自有照片（Owner 在意的「別人的照片」）
featured 命名非 MAPLAB 規範者 10 張，其中 8 張為真實 MAPLAB 活動照（描述式命名，OK）。
**高度疑似非自有/網路 stock（建議換掉）：**
- post 247 elder-birthday-catering-tainan → `Creamy-Penne-Carbonara-Pancetta-Main.webp.avif`（英文食譜站 stock 食物名，極可能就是 Owner 看到的「不是我的食物」）
- post 261 vip-expo-catering-business-meeting → `17vvu-ag54c.avif`（隨機檔名＝下載的 stock）
> 兩篇皆 Elementor，但 featured image 是 post meta，**可用 REST 直接換**（featured_media）。

## 照片管線（不需 lb99104 桌面重連！）
- 照片可經 **pagewu1010 Drive API** 直接取（MAPLAB_ASSETS root 1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy 可遍歷；photos 亦有 pagewu1010 owned 副本）。
- **坑**：同檔名有重複（例：`catering-corporate-event-buffet-finger-food.jpg` 有一張其實是 Porsche 廣告圖 5,246,281 bytes）。**必須用資料夾遍歷（MAPLAB_ASSETS/年/catering/類）解析正確 file id，不可只用檔名搜尋。**
- 下載會回 base64 → 必須在 subagent/Codex context 處理，勿進主 loop（省額度）。轉檔 cwebp/sips 本機可用。WP media REST 上傳已驗證。
- 一次 subagent proof 因 API Overloaded（暫時性）+ 抓到重複錯檔而中止；featured/media 無誤改，已清暫存，無不良上線。

## 建議下一步
1. 換掉 247、261 的 featured 為真實 MAPLAB 照（247→慶生/餐點，261→企業活動），用資料夾遍歷解析、subagent 跑下載+webp+上傳+設featured+驗證。
2. 掃 inline 圖（資產文 586/924/945… 的內文圖）找其他非自有照片。
3. （次要）為薄頁加相關 inline 圖增加豐富度——非必要，featured 已有。

## 2026-06-16 已執行（live + 驗證）
- ✅ 247 featured：stock `Creamy-Penne-Carbonara` → 真 `maplab-elder-banquet-dessert-table`（舊圖已消失）
- ✅ 261 featured：stock `17vvu-ag54c` → 真 `maplab-corporate-meeting-reception`
- ✅ 8 篇 AI 語氣重寫（1168/564/924/1084/1093/498/1217/1048），banned 句型歸 0

## inline 非自有照片（掃描結果，待修）
- **698 tainan-custom-catering-menu：12 張英文食譜站 stock 食物圖**（Artisan-Cake-Pops / Creamy-Penne-Carbonara / Gourmet-Cheese-Charcuterie / Matcha-Custard / Prosciutto-Caramelized-Apple / Pumpkin-Halloumi / Seasonal-Fruit-Nut / Smoked-Salmon-Caviar / Tomato-Bruschetta / Yorkshire-Pudding / Assorted-Mini-Quiches / Artisan-Fishcake）← 最大宗，且 698 是 **Elementor** → 需 Elementor 編輯器換
- 261：舊 `17vvu` 仍在內文（Elementor，需編輯器移除）
- 219：GUID 檔名 stock（Elementor）
- 1084：Pumpkin-Halloumi、Tomato-Bruschetta 2 張（**經典**，可 REST 換）

## 換 inline 圖的軌道
- 經典(1084)：REST 可換（download→webp→upload→替換 img src）
- Elementor(698/261/219)：需走 Chrome Elementor 編輯器；或用 v2 提案的真 MAPLAB 餐點照替換

## 2026-06-16 補圖 batch 1（live + 驗證）
- ✅ 1199/1207/1209/1211 各插入 1 張真 MAPLAB 企業外燴餐桌照（inline，含 alt），前台確認
- ⏭️ 1201 跳過：指派檔 `catering-corporate-event-buffet-finger-food.jpg` 在 Drive 唯一份是 Porsche 廣告壞檔 → 待用別張重補
- 註：WP 上傳 webp 會被轉 avif；Cloudflare 偶發 524（media 仍建立，需清重複，已清 1926-1928）
- ⚠️ 資料品質：照片索引/Drive 有同名壞檔（catering 名稱混 Porsche 圖）→ 建議回報 A4 修索引
- 待續：其餘 ~24 篇 classic AI 文章 inline 補圖（婚禮/週歲/地區/菜單/FAQ 群）+ 1201 重補

## 2026-06-16 補圖修正（Owner 回饋）
- 🔴 毛利紅線：**餐盒/bento = 低毛利，不可當主軸、不主動曝光**（已寫入 maplab-photo-sourcing.md 鐵則4）
- 1199：移除餐盒圖 `maplab-year-end-party`(media 1923 已刪) → 換成高毛利長桌 buffet（cathay 案例照，通用 alt）
- 1201：補上內文圖（interior-design 精緻擺盤案例照）
- 配圖來源改用本機 `~/Desktop/案例分享wordpress用_webp/`（已 webp、SEO 命名、curl --data-binary 直傳，不經 API/base64）
- 4 篇已驗證前台；其餘已補圖文章(1207/1209/1211)的圖為 buffet/甜點擺盤，非餐盒，無虞

## 2026-06-16 補圖 batch 2（ToC 群，本機 2025案例庫，含裁切）
- 1222 彌月/週歲、1224 生日、1226 家庭聚會、1227 野餐 — 各補 1 張高毛利擺盤照（無餐盒），前台驗證
- 來源：~/Desktop/2025案例/ToC/（生日週歲、家庭聚會_入厝）；本機 curl 直傳
- 待 Owner 看：1224 背景有小孩照片立牌(派對佈置)、1227 戶外遠處有不可辨識人影 → 若要更乾淨有備選圖

## 2026-06-19 補圖 batch 3（地區/菜單 + 婚禮）
- 地區/菜單 9 篇（1229-1233, 1236-1239）：本機 2025案例 ToB 庫，高毛利擺盤、無餐盒、部分裁切（去 FB UI/轉橫式），前台驗證
- 婚禮 5 篇（1213/1215/1217/1218/1220）：A4 雲端索引 scene=婚禮 → 下載+影像辨識挑 5 張真婚禮甜點桌/canapé（無餐盒、無人臉），前台驗證
- 1232 改用企業茶會圖（科林研發夾全是 FB 截圖+Lam 單杯品牌品，不適合）
- 已清 524 重複 media（1975 已刪）
- 婚禮照其實充足（catering/wedding 2022/2023 各約 50 張），非索引顯示的 28
## 補圖總計（classic AI 文章內文圖）：企業5 + ToC4 + 地區/菜單9 + 婚禮5 = 23 篇完成
## 仍待補：FAQ/指南群 1241-1246、1168、1027（8 篇）；Elementor 群不碰

## 2026-06-19 補圖 batch 4（FAQ/指南群）
- 1241/1242/1243/1245/1246/1168 各補 1 張高毛利擺盤照（無餐盒、無人臉），EXIF 轉正、部分裁切，前台驗證
- 跳過：1027（取消政策，不需圖）、1244（內容策略待 Owner 定 A/B/C）
## 補圖完成：classic AI 文章共 29 篇內文圖（企業5/ToC4/地區菜單9/婚禮5/FAQ6）
## 仍開放：1244 策略決定；1224小孩立牌+1227遠處人影（可換）；261內文+Elementor 12篇（需編輯器）
