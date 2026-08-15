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

## 2.5 影片優先原則 ＋ 真片段剪輯（重要）

**原則：有影片素材就優先用真片段剪輯，不要只把相片轉影片。**
- 案例夾若有 `.mov / .mp4` → 用真片段剪成短片。
- 只有沒有影片時，才退回相片 zoompan（Ken Burns）。
- 流程：A2/A3/A4 個案「內容確認」後才發 A8 建片；每案標明哪些有影片檔（附時間碼更佳）。

**工具現況（不重造輪子）**：`tools/ai_workbook/a8_enhanced_video_draft.py` **已支援影片輸入**（`VIDEO_EXTS={.mov,.mp4}`）：
- 影片段：自動 crop 置中 9:16 → scale 1080×1920 → **取每支開頭 N 秒（`--seconds`）** → 疊 Swift IG Soft 字幕 → `maplab_ig_soft` 濾鏡 → xfade 串接；音軌去除（發布前配授權樂）。
- 相片段：zoompan 運鏡。**同一支片可混用影片＋相片**（把 MOV 與精選 webp 放同一 asset-dir）。
- 用法：`--asset-dir` 指到「含 MOV 的資料夾」即可（先前 pilot 只餵相片，之後改餵 MOV/混合）。

**挑片段 in/out（現況限制與解法）**：
- 限制：工具目前只取「每支**開頭** N 秒」，不能自動挑中段最佳片段。
- 解法：依 A2/A3/A4 給的時間碼**先用 ffmpeg 預剪**，再餵 enhanced draft：
  `ffmpeg -ss {開始秒} -t {長度秒} -i clip.mov -c copy clips/seg01.mov`
  （順序命名 seg01/seg02… 決定分鏡順序；再 `--asset-dir clips/`。）
- 素材先過 A8 A/B/C 分級（A 直用、B 需裁/遮臉/遮 logo、C 私密不可用）。

**缺口（待評估建）**：尚無「自動偵測最佳片段 in/out」工具；目前靠人工/個案標時間碼。可評估建 `a8_clip_trim.py`（讀時間碼清單 → 批次預剪 → 餵 enhanced draft）。**等 b285b719 選出 3 案（標明哪些有影片檔）再依此準備剪輯流程。**

---

## 2.6 音樂／旁白工具鏈（Creative Engine v0）

- **音樂風格＝Suno**（Custom Mode「曲風欄」指定風格；歌詞欄可貼自訂歌詞／把留言唱成歌）。**無官方 API＝人工**在網頁生成下載，商用需 Pro。**placeholder（免費、先驗氣氛）**＝Apple Loops（本機 GarageBand 素材，免版稅，如「Yearning Acoustic Guitar」文青木吉他）或 YouTube 音樂庫。
- **旁白＝ElevenLabs**（有 API、可 agent 自動；Owner 聲音用語音複製）。**placeholder**＝macOS `say`（本機免費 TTS；中文 voice：Meijia zh_TW；`-r` 調語速，`-o narration.aiff`）。
- **音訊合成**：ffmpeg amix 把旁白(volume~1.7)＋音樂(volume~0.15 低音量鋪底)混進無聲影片；`-stream_loop -1` 讓短 loop 填滿長度。
- **規格卡＝文字卡（預設不配縮圖，省算力）**：`a8_spec_card_generator.py` 預設輸出文字卡（Hook＋3節拍＋CTA＋音樂/旁白方向）推 Telegram；要封面才加 `--thumbnails`（Swift 出圖）。選中的卡才 ffmpeg＋Swift 字幕渲染；聲音先 placeholder、Owner 訂閱後接真版（Suno 音樂人工、ElevenLabs 旁白 API）。
- **固定卡別「留言 Rap（comment-rap）」**：顧客好評/留言 → trap beat → 30s Short。做法：Suno **Custom Mode 貼留言當歌詞＋曲風填 trap/hip-hop**（半自動、無 API；免費試聽、Pro 商用下載）。歌詞結構 `[Hook]` 品牌+場景鉤子／`[Verse]` 好評重點押韻／`[Hook]` 收尾，自然置入台南外燴/MAPLAB/場景。**好評來源優先真實**（Google 商家/IG/LINE 並標來源），拿不到用代表性一則並註明。唱＝Suno；旁白版才用 ElevenLabs。
- **⚠️ TTS 授權（重要）**：macOS 內建語音（含 **美佳 Meijia / Siri 語音**）Apple SLA **僅限個人非商用**，**不可用於營利/發佈的 YouTube** → 只能當 placeholder，公開前一定要換。**免費可商用 TTS**：Piper（MIT，離線、中文可、品質基本）、Kokoro（Apache-2.0，品質較好、中文可）、Chatterbox（MIT，主英文）；**避開 Coqui XTTS v2**（CPML＝非商用、公司已停運）。付費最佳＝ElevenLabs（品質＋Owner 語音複製、商用）。唱歌仍走 Suno。
- **訂閱一句話對照**：**Suno Pro**＝解鎖「商用權＋可下載＋去浮水印，~500 首/月」｜**ElevenLabs Starter**＝解鎖「商用＋即時語音複製＋API，~30–40 分旁白/月」｜**ElevenLabs Creator**＝解鎖「專業語音複製 PVC（高品質 Owner 聲）＋~2 小時旁白/月＋192kbps」。
- **✅ 免費商用 TTS 實測＝Piper（zh_CN-huayan-medium）可用**：Mac py3.14 的 pip 壞掉，改用 3.9：`/usr/bin/python3 -m venv /tmp/ttsenv && /tmp/ttsenv/bin/pip install piper-tts` → `python -m piper.download_voices zh_CN-huayan-medium --data-dir /tmp/piper_voices` → `echo 文字 | /tmp/ttsenv/bin/python -m piper -m /tmp/piper_voices/zh_CN-huayan-medium.onnx -f out.wav --data-dir /tmp/piper_voices --length-scale 0.92`。（/tmp 會清，隔 session 要重裝。）邦尼兔 hiphop 口白 demo 已用它。
- **🎵 配樂對拍**：用**完整 bar 對齊的 beat/loop**（Apple Loops 的 hip hop「…Beat」是整小節，`-stream_loop -1` 接在拍點上）；**別拿旋律樂句隨機裁**（會在奇怪時間刷和弦）。rap 用 hip hop beat、文青用完整木吉他 loop。
- **🚫 去人臉（擴到成人/業主/賓客）**：選片段避開任何可辨識人臉；抽 start/mid/end 幀確認整段 face-free，或只取 face-free 時窗（例：邦尼兔 c03 只用 <6.5s，因 ~7s 有人入鏡）。**樣本一律用邦尼兔**（Owner 與木地板老闆不熟，木地板不擴張）。

### A8 工具庫候選：MiniMax Music 3.0（2026-08 收錄，Owner FB 分享）
- **用途**：AI 生成**完整歌曲含人聲**（貼歌詞 [Verse]/[Chorus]，可出中文饒舌/boom bap）——正是我們「唱/rap」缺口。
- **免費/收費**：有 `Music-3.0-free` 免費層（有限）；完整走 API **$0.15/首(≤5分)**、歌詞 $0.01。
- **API**：✅ 官方＋fal.ai → **agent 可自動生成**（比 Suno 強，Suno 無官方 API）。
- **本地**：❌ 無官方開放權重；Mac mini 無 NVIDIA GPU 跑不了 → 走雲端 API。（FB 示範是 RTX 4080 自建，非官方。）
- **可否商用**：⚠️ **不明確**——官方 API 文件無商用條款；消費頁稱可商用但不在 API 文件內 → **採用前務必向 MiniMax 確認**，別當已授權。
- **與產線關係**：可當 **Suno 的替代/補足**（唱/rap 自動化）；與 Piper(免費口白)、Apple Loops(beat) 互補。連結：minimax.io/audio、fal.ai/models/fal-ai/minimax-music。
- **採用前提**：先確認商用授權 → OK 再接 API 當 rap 歌自動化來源；否則維持 Suno(人工) 出商用 rap。

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
7. **YouTube Studio 內建「編輯器」（開放性編輯器）**：上片後可在左側「編輯器」做 **trim 首尾／剪掉中段／加片尾／模糊處理**，適合對已上傳片微調，走 Chrome MCP 操作（Studio 可控已驗證）。**用於發布前微修，不取代本機真片段剪輯**（本機剪輯可重跑、可 commit、有 IG Soft 模板；Studio 編輯器是線上手動微調）。

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

- Drive/Sheets token：`~/.claude/mcp-keys/google-token.json`；失效（invalid_grant）時，Owner 在電腦前跑一次 `python3 ~/.claude/mcp-keys/reauth_google.py` → 瀏覽器跳 Google 同意頁 → 點「允許」→ 新 token（含 refresh_token）自動存回、舊的備份為 `.prev`。
  - **更正（2026-08-03，取代舊「測試模式 7 天過期」診斷）**：先前每 7 天 invalid_grant 的根因，是 GCP 專案 **`maplab-ai`** 的 OAuth 同意畫面卡在「測試」狀態（外部＋測試 → refresh token 每 7 天過期）。**該同意畫面已於 2026-08-03 發布為「實際運作中」，根因已消除。** 舊 token 是測試期核發的短命 token；只要重授權一次，新 refresh token 即長期有效——**換一次即永久，不再每 7 天要 Owner 動作**。
  - 這是 A8 影音產線用的憑證（專案 `maplab-ai`、單一 `google-token.json`）。**勿與相片產線 `maplab-pipeline`（`./auth/token_owner.json`、`token_spouse.json`）混為一談**——兩者是不同 GCP 專案、不同 token 檔。
  - 因 app 為「外部＋未驗證」且含 restricted `drive` scope，Owner 在同意頁可能先看到「未驗證應用程式」警告 → 點「進階 / 繼續前往 MAPLAB-AI（不安全）」→ 再「允許」，屬正常（僅 2 位授權使用者，不影響）。
- YouTube 上片走**瀏覽器 Studio**（現有 OAuth 沒有 YouTube scope；要 API 上傳才需加 scope）。
- **公開發佈一律等 Owner**；本 SOP 只到私人草稿。祕密不 echo、不進 git。

---

## 7. 已驗證實例（2026-08-02 試錯跑通）

- 素材：Cléa 開幕茶會 4 張 → webp/pin/mp4（帶字幕 IG Soft）。
- 上片：YouTube **私人 Short 草稿**成功（channel maplabkitchen），標題/描述/受眾/私人皆照 §5。
- 逼出的欄位標準化＝本 §5。字幕 QA 全過（§3）。
