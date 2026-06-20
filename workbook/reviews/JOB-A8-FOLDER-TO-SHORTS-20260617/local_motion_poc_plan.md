# A8 地端動態運鏡 POC 計畫 (ICC Tainan 案例)

> 專案：MAPLAB To B 企業外燴影音再製
> 階段：Phase 6 POC 驗證（地端免年費方案）
> 建立：2026-06-20 | 版本：v1.0

---

## 1. 隱私與素材安全審查 (Privacy Check)

本計畫所選用的 4 張真實活動照片，皆來自已通過 A4 審查且發布於官網與 WordPress 的 A 級素材。經人工確認：
*   ❌ 無任何清楚人臉或特寫。
*   ❌ 無客戶內部投影片、機密會議簡報。
*   ❌ 無電話號碼、QR code、特定報價單等商業敏感資訊。
*   🟢 全數為乾淨的餐點近照與現場佈置，適合安全於本地進行動態運鏡生成。

---

## 2. 地端運鏡 Storyboard 與字幕企劃

我們利用 4 個照片分鏡，每個分鏡長度為 2.4 秒，加上開場與結尾，串接成約 13.2 秒的 To B 企業會議茶點宣傳影片。

### 鏡頭 1：會議茶點佈置全景 (Hook)
*   **來源素材**：`maplab-icc-tainan-catering-table-overview-01.webp`
*   **地端運鏡 (`motion`)**：`dolly_in` (自 1.0x 慢速放大至 1.15x)
*   **畫面描述**：在大臺南會展中心會議廳內，整齊有序、擺放精美的米色調茶點長桌。
*   **影片字幕**：`茶點動線清楚`

### 鏡頭 2：精緻手工甜點細節
*   **來源素材**：`maplab-icc-tainan-dessert-catering-detail-05.webp`
*   **地端運鏡 (`motion`)**：`pan_right` (自左平移至右)
*   **畫面描述**：擺放在金色點心架上的雙色慕斯杯與新鮮水果塔。
*   **影片字幕**：`交流節奏不被打斷`

### 鏡頭 3：飲品與甜點服務區
*   **來源素材**：`maplab-icc-tainan-dessert-and-drink-service-13.webp`
*   **地端運鏡 (`motion`)**：`pan_left` (自右平移至左)
*   **畫面描述**：擺設整齊的特調飲品區與乾淨杯組。
*   **影片字幕**：`飲品甜點分區`

### 鏡頭 4：鹹甜點精緻展示 (Outro Hook)
*   **來源素材**：`maplab-icc-tainan-finger-food-dessert-display-04.webp`
*   **地端運鏡 (`motion`)**：`dolly_out` (自 1.15x 慢速縮小至 1.0x)
*   **畫面描述**：特製一口鹹點擺盤，色澤鮮豔、背景柔和。
*   **影片字幕**：`桌面留白乾淨`

---

## 3. 本地拼接與渲染步驟 (Zero-Cost Rendering)

1.  **分鏡字幕繪製**：
    利用修改後的 `a8_render_story_frame.swift`，傳入 `"clear"` 作為背景，單獨將字幕與 `MAPLAB Kitchen` 浮水印繪製在透明 PNG 上。
2.  **FFmpeg 運動運算**：
    依據上述分鏡指定的運鏡參數，使用本機 `ffmpeg` 的 `zoompan` 濾鏡在 2160x3840 尺度下對原始相片進行縮放平移，輸出無損 1080x1920 @ 30fps 影片片段。
3.  **疊加與拼接**：
    將透明字幕疊加至影片片段上，並利用 `xfade=fade` (0.35s) 完成 Intro/Outro 與 4 個分鏡片段的拼接，生成最終 H.264 影片。
