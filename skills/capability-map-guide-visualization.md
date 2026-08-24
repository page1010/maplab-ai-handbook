# Skill:指向性地圖導覽視覺化

- 建立:2026-08-25|作者:A0/Fable5|狀態:**待認領(未找到既有實作)**|Owner 指示:msg 3992
- 用途:地圖上的指向性導覽視覺化——店面/地點導覽、路線指引、位置敘事。

## 現況(2026-08-25 盤點,誠實記錄)

- 搜過 maplab-ai-handbook、tainan-location-social-game、innerflowlab-local-growth 三處:**沒有找到可直接復用的地圖導覽程式碼**。
- tainan-location-social-game 有城市錨點/地點概念但已封存(PROJECT_SEALED),且明載「no map pipeline exists」。
- 結論:Owner 說的「我們本來指向性地圖導覽視覺化」若指某個舊 demo/檔案,請 Owner 一句話指出在哪(哪台機器/哪個對話/哪個檔),找到就併入本 skill;若找不到就當新建項。

## 新建時的技術底(先寫好,免重複研究)

- 免費技術棧:Leaflet 或 MapLibre GL(開源免金鑰)+ OpenStreetMap 圖資;指向性動畫用 polyline 漸進繪製+方向箭頭;手機優先(PWA 可離線)。
- Google Maps API 也可但要金鑰+額度,除非需要街景/店家資料才用。
- 產出形式:單檔 HTML(好分享、好嵌 WordPress)或 claude-design 專案(要視覺 draft 時)。
- 第一個落地場景建議:maplabkitchen 店面導覽頁(從捷運站/停車場到店的指向動畫),可直接嵌官網,對 SEO 也有用。

## 邊界

- 客戶地址/個資不進地圖資料;只用公開地點。
- 發布到 WordPress 走既有審核閘(draft→review→Owner 核准),不自動發布。
