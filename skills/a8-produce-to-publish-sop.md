# A8 產片 → 上片 標準流程（Produce-to-Publish SOP）

> 負責角色：A8 影音內容產線 ｜ 建立：2026-08-02 ｜ 版本：v1.0
> 對齊：`skills/brand-voice-guide.md`（語氣）、`skills/maplab-visual-spec.md`（視覺/色卡）、`skills/a8-video-pipeline-skills.md`（產線細節）、`skills/a8-local-motion-integration.md`（運鏡）
> 規範文件（雲端）：【正式規範】A2/A4 內容產線格式＋規範 v1、【基準】品牌語氣＋色調

---

## 0. 這本 SOP 解決什麼

把「一個活動專案的照片 → 帶字幕 9:16 短片 → 上到 YouTube 私人草稿 → 待 Owner 核准公開」做成**可重複、可驗證、可回收**的一條流程。字幕、標題、描述一律套品牌語氣＋固定色卡；上片先到**私人/草稿**，公開一律等 Owner。

規格（TikTok / YouTube Shorts / IG Reels / Pinterest 共用）：**1080×1920、9:16、H.264 MP4**。

---

## 1. 標準流程表（每步：輸入 → 動作 → 工具/腳本 → 產出 → QA）

| # | 步驟 | 輸入 | 動作 | 工具 / 腳本 | 產出 | QA |
|---|------|------|------|-------------|------|----|
| 1 | 取素材 | Drive 專案子夾 fileId | 下載精選照片到本機 | Drive API（`~/.claude/mcp-keys` token；refresh 見 §6）| `pilot-{name}/raw/*` | 檔案數對、非私密畫面 |
| 2 | 轉正 | raw 照片（含 HEIC）| 依 EXIF 轉正，不盲轉 | `tools/ai_workbook/a8_auto_orient.py`；HEIC 用 `sips -s format jpeg` | `oriented/*.jpg` | orient=6 轉正、orient=1 不動 |
| 3 | A4 出圖 | oriented | 轉 webp + 2:3 直式 pin | `cwebp -q 80`；`ffmpeg` scale/crop 1000×1500 | `webp/*.webp`、`*_pin.jpg` | 尺寸/色調對；命名 `maplab-{場景}-{描述}` |
| 4 | A8 產片 | oriented + 字幕句 | 生成帶字幕 IG Soft 短片 | `tools/ai_workbook/a8_enhanced_video_draft.py`（見 §2）| `review/a8-short-review-draft.mp4` + cover | ffprobe 1080×1920；字幕 QA（§3）|
| 5 | 字幕 QA | 字幕句 + CTA | 逐句掃禁用詞 + 逐幀目視 | 禁用詞掃描 script + 抽幀 `ffmpeg -ss` 目視 | QA 通過紀錄 | 無禁用詞、非豆腐字、非佔位 |
| 6 | 存檔 | webp/pin/mp4 | 回存專案 Drive `/publish/` | Drive API multipart upload | Drive `/publish/*` | 檔案可開、命名對 |
| 7 | 上片草稿 | mp4 | 上 YouTube 私人草稿 + 填欄位 | Chrome MCP → YouTube Studio（見 §4）| 私人 Short 草稿 | 瀏覽權限＝私人；欄位齊（§5）|
| 8 | 核准 | 私人草稿連結 | 發 Owner 看 → 核准才公開 | Telegram `sendVideo` / Studio 連結 | approval 決定 | 公開前 Owner 明確同意 |

---

## 2. 固定色卡 + 上色/字幕怎麼調用（實際工具）

**產片一律用**：`tools/ai_workbook/a8_enhanced_video_draft.py`，`--visual-preset maplab_ig_soft`（預設）。它的實作：

- **運鏡**：ffmpeg `zoompan`（dolly_in / dolly_out / pan_left/right / static），每幕 2.4–2.8s。
- **字幕/浮水印**：**Swift/AppKit 在透明畫布繪字**（不靠 ffmpeg drawtext，避免精簡版 ffmpeg 無 drawtext），再 ffmpeg `overlay` 疊上；右下 `MAPLAB Kitchen` 浮水印。
- **濾鏡**：`maplab_ig_soft`＝暖、柔、低對比、亮度微升、飽和微升、輕銳化。
- **轉場**：`xfade=fade` 0.35s。開場暖米覆膜 1.4–1.8s（MAPLAB Kitchen＋service line＋細金線）。結尾暖米 CTA（依 `--category`）。

**7 色票（HEX）**（來源 `maplab-visual-spec.md`，寫進表以便對色）：

| 色名 | HEX | 用途 |
|------|-----|------|
| 奶油白 | `#FAF7F2` | 開場/結尾覆膜、留白 |
| 暖米 | `#EDE5D8` | 卡片底、CTA 底 |
| 深橄欖 | `#3A3A2E` | 主字 |
| 棕褐 | `#7A5C3E` | 強調/CTA 字 |
| 鼠尾草 | `#8FA68E` | 輔助 |
| 裸粉 | `#D9C4B8` | 週歲/婚禮場景色 |
| 炭黑 | `#2C2C2C` | 細線 |

**場景配色**：週歲/抓周＝裸粉+奶油白｜婚禮＝裸粉+暖米｜企業/開幕＝深橄欖+暖米。禁：螢光色、純黑大面積、單畫面>3 主色。

**category → CTA / 場景色 對照**：opening（開幕）、corporate_tea（企業茶會）、wedding（婚禮）、birthday（週歲/抓周）、brand_event、private_party、art_wine、custom_box、general。CTA 由 category 帶出固定文案（例：opening＝「台南開幕茶會、品牌活動｜官方 LINE 洽詢檔期 @maplab」）。

---

## 3. 品牌語氣（字幕/標題/描述都套）

完整見 `skills/brand-voice-guide.md`。要點：說場景不硬賣、具體名詞、開放感（不用「保證/一定」）、不用「不是…而是…」句型。

**字幕每幕 6–14 字**，先過禁用詞。**禁用詞**：最頂/超值/保證/CP值/佛心/便宜又大碗/錯過可惜/趕快預約/名額有限/一生一次/不訂會後悔/限時優惠；**A8 額外流程禁用語**：取餐/順暢/分開/方便交流/促進交流/確保/動線穩/節奏更穩/節奏穩健。少用：精緻/質感/用心/客製化。

字幕 QA（step 5）＝①禁用詞掃描 ②長度 6–14 ③無佔位/亂碼 ④抽幀目視中文正常渲染。

---

## 4. YouTube 上片 SOP（Chrome → Studio，私人草稿）

1. 確認 Chrome 已登入 MAPLAB 頻道（channel `UC85n15rcFgHzZtb78vV6-sw`，maplabkitchen）。
2. Studio 右上「建立」→「上傳影片」。
3. 檔案要放**本 session 可存取路徑**（outputs 資料夾）才能用 Chrome `file_upload`；連接的 repo 夾不被 uploader 接受 → 先 `cp` 到 outputs。
4. 填標題、描述（§5 模板）、目標觀眾＝**否，這不是兒童專屬**（必填）。
5. 瀏覽權限＝**私人**（草稿）。**絕不選公開**；公開等 Owner。
6. 儲存。垂直 <3 分自動歸類 **Short**（連結變 `youtube.com/shorts/…`）。

---

## 5. 標準化欄位（可填模板）＋ 描述 SEO 研究結論

**標題**（比照頻道既有 #外燴紀錄 格式；上限 100 字、關鍵字前段、Shorts 加 #Shorts）：
```
#外燴紀錄 ｜{活動類型} {English}｜{主關鍵字}．{客戶/場景} #Shorts
```
例：`#外燴紀錄 ｜開幕茶會 Grand Opening｜台南開幕茶會外燴．Cléa 女裝選品店 #Shorts`

**描述模板**（依 Owner 公版；第一段場景+品項，末段固定 CTA+連結；hashtag 10–15 個見庫）：
```
#外燴紀錄
｜{活動類型}｜{English} |

{場景描述 2 行：光影/香氣/器皿，說場景不硬賣、避禁用詞}
{第 2 行場景}

{品項描述 1 段：帶入該場次「實際」餐點，逐一點名}
每一口小點，都為這個空間添上祝福的味道！

恭喜{客戶名}開幕🎊
｜Catering Service 外燴餐點

——————————————

📍 立即預訂！

✅ 精緻外燴｜融合創意料理，讓賓客一試難忘
✅ 客製菜單｜根據活動需求彈性客製，滿足不同味蕾
✅ 專業擺盤｜高顏值餐點，讓美味更有儀式感

➡️洽詢檔期
加入官方Line: https://lin.ee/IP8nt4n
🌐 官方網站 https://maplabkitchen.com/
💬 LINE 官方帳號 https://lin.ee/BlVku2U
📸 Instagram https://www.instagram.com/maplabkitchen/
📘 Facebook https://www.facebook.com/maplabkitchen

{場景 hashtag：10–15 個（見下方庫），首 3 個放最重要關鍵字，含 #台南外燴 + 活動標籤 + #Shorts}
```

**固定區塊（照留不改）**：開頭 `#外燴紀錄`、`｜Catering Service 外燴餐點`、分隔線、`📍立即預訂`＋3 個 ✅、`➡️洽詢檔期` 整串連結（**固定連結常數**，見下）。
**變數（每則要換）**：活動類型／English／場景 2 行／品項段／客戶名／hashtag。
**語氣規則**：場景 2 行＋品項段用 brand-voice（說場景、避禁用詞）；`✅` 那段是 Owner 標準塊，照留原文。
**⚠️ 客戶名＝客戶識別 SOP（有正確答案，自己查證，不丟回問 Owner）**：
1. 先看來源：專案夾名／海報字樣／影片畫面（插旗、招牌）／A2 Doc。
2. **IG × 出餐日期核對**：找該客戶 IG，用「近期開幕貼文的開幕日期」對「我們的出餐日期（專案夾日期/照片 EXIF）」比對。客戶若有多分店，用日期鎖定是哪一家。
3. **唯一 match 就用**；只有真的模糊（10 幾個帳號對不上）才升級 Owner。
4. 公版範例出現的客戶名（如「綺麗絲Ciries」）是**別場活動的範本示例**，不等於本片客戶——以本片來源為準。

**固定連結常數（洽詢檔期整串，所有影片共用）**：
```
加入官方Line: https://lin.ee/IP8nt4n
🌐 官方網站 https://maplabkitchen.com/
💬 LINE 官方帳號 https://lin.ee/BlVku2U
📸 Instagram https://www.instagram.com/maplabkitchen/
📘 Facebook https://www.facebook.com/maplabkitchen
```

**場景 hashtag 庫**（每則選 10–15 個；首 3 個＝最重要關鍵字；YouTube 描述 hashtag **上限 15**，超過全部失效）：
- **共用（每則都放）**：`#台南外燴 #台南外燴餐點 #maplab #Shorts`
- **開幕**：`#開幕茶會 #開幕外燴 #開幕派對 #店面開幕 #品牌開幕 #公司開幕茶點 #迎賓茶點 #台南開幕茶會外燴`
- **週歲/抓周**：`#週歲派對 #抓周 #收涎 #週歲外燴 #甜點桌 #生日派對 #台南週歲派對外燴`
- **婚禮**：`#婚禮外燴 #戶外婚禮 #candybar #甜點桌 #迎賓點心 #證婚 #台南婚禮外燴`
- **企業會議茶點**：`#會議茶點 #企業會議茶點 #公司會議點心 #外燴會議茶點 #會議餐盒 #精緻餐盒 #企業外燴`

**其他欄位預設**：
- 目標觀眾：不是兒童專屬（必填）。
- 可見度：私人（草稿）；公開等 Owner。
- 標籤 tags：在「顯示更多」內；權重低，填 3–5 個（台南外燴/開幕茶會/週歲派對…）即可。
- 類別 category：娛樂或人物與網誌（B2B 案例可用「人物與網誌」）。
- 縮圖：桌面版鎖住（需手機 App / 帳號電話驗證才能自訂縮圖）→ 目前用系統自選幀，或手機補。
- 播放清單：依活動類型建（開幕/週歲/婚禮），把同類案例歸一清單。
- 置頂留言：可放官方 LINE 連結（避免描述被截斷時仍看得到 CTA）。

**描述 SEO 最佳做法（2026 研究結論，寫進模板）**：
- 主關鍵字放**標題＋描述第一句**（Shorts 靠這個被搜尋/AI Overview 撈到）。
- YouTube 描述 hashtag **10–15 個**（硬上限 15，超過全部失效）；前 3 個會顯示在標題上方，放最重要關鍵字。（3–5 個是 IG/TikTok 慣例，YT 不同。）
- **#Shorts** 一定加（幫 YouTube 正確歸類短影音）。
- 章節時間戳只對 >5–10 分長片有用；短片不需要。
- **字幕（captions）對 Shorts 完播率幫助大**（多數靜音觀看）——我們的片本來就燒字幕，優勢。
- 描述 200–500 字有助鋪關鍵字，但要有內容、不堆砌。
- YouTube「描述沒有 alt 欄位」；圖片 alt 屬 A4/WordPress，不在 YT。YT 的「可搜尋文字」＝標題＋描述＋字幕，這三處鋪關鍵字即可。

**Shorts vs 一般片差異**：直式 <3 分自動為 Short；標題/描述加 #Shorts；縮圖對 Short 影響小（用封面幀）；一般長片才需章節/時間戳/自訂縮圖。

---

## 6. 憑證 / 邊界

- Drive/Sheets token：`~/.claude/mcp-keys/google-token.json`；失效（invalid_grant）時跑 `~/.claude/mcp-keys/reauth_google.py` 重授權（installed client 測試模式 refresh 每 7 天過期；根治＝Cloud Console 專案 maplab-ai 發布 OAuth 同意畫面）。
- YouTube 上片走**瀏覽器 Studio**（現有 OAuth 沒有 YouTube scope；要 API 上傳才需加 scope）。
- **公開發佈一律等 Owner**；本 SOP 只到私人草稿。祕密不 echo、不進 git。

---

## 7. 已驗證實例（2026-08-02 試錯跑通）

- 素材：Cléa 開幕茶會 4 張 → webp/pin/mp4（帶字幕 IG Soft）。
- 上片：YouTube **私人 Short 草稿**成功（channel maplabkitchen），標題/描述/受眾/私人皆照 §5。
- 逼出的欄位標準化＝本 §5。字幕 QA 全過（§3）。
