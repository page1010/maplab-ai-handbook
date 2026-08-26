# A8 產片 → 上片 標準流程（Produce-to-Publish SOP）

> 負責角色：A8 影音內容產線 ｜ 建立：2026-08-02 ｜ 版本：v2.0（2026-08-26）
> 對齊：`skills/brand-voice-guide.md`（語氣）、`skills/maplab-visual-spec.md`（視覺/色卡）、`skills/a8-video-pipeline-skills.md`（產線細節）、`skills/a8-local-motion-integration.md`（運鏡）
> 規範文件（雲端）：【正式規範】A2/A4 內容產線格式＋規範 v1、【基準】品牌語氣＋色調

---

## 0. 這本 SOP 解決什麼

把「一個活動專案的原始照片／影片＋核准音訊 → 人工校時的長／短片 → 完整播放驗收 → 上到平台草稿 → 待 Owner 核准公開」做成**可重複、可驗證、可回收**的一條流程。字幕、標題、描述一律套品牌語氣＋固定色卡；上片先到**私人/草稿**，公開一律等 Owner。

本文件是 A8 最終成品的 canonical SOP。`a8-video-pipeline-skills.md` 裡的 local dry-run／review draft 只用來驗證素材、比例與模板，不能取代本文件的正式 timeline、音訊、畫質與 QA gate。

### 0.1 三段接力，不在同一份稿裡混工種

1. **A2 WordPress / SEO** 先完成 customer-ready 公開稿；SEO 欄位與素材判定分開留在內部包。
2. **Songwriter** 只讀核准的活動介紹與音樂 brief，依 `skills/maplab-hiphop-songwriter/SKILL.md` 先交歌詞與 15 秒 hook 給 Owner 核稿；這一輪停在 `OWNER_LYRICS_GATE`。
3. **音樂生成** 只接 Owner 已核准的歌詞；生成後由 Owner 選定音訊版本。
4. **A8** 只接選定音訊與核准素材，負責長片、短片、字幕、封面與平台包。

每段可以在不同 session 執行，但只能依序交接。WordPress 文章不描述寫歌或剪片流程；歌詞不描述 SEO 或素材治理；影片 metadata 不承接內部工作語言。未取得 Owner 歌詞核准時，不得把「文章已好」解讀成可生歌或可啟動 A8。

規格（單一真相來源 = `tools/ai_workbook/a8_platform_formats.py` 的 `PLATFORM_FORMATS`；出處見 `docs/platform_formats_sources.md`）：
- **垂直短片**（YT Shorts / IG Reels / TikTok / FB Reels）：**9:16、1080×1920、H.264 MP4**；邦尼兔案例與同型音樂宣傳片預設 **15.0s**，延長需 Owner 明確核准。
- **YouTube 長版**：**16:9、1920×1080**，全曲；縮圖 **1280×720**。
- 若完整歌曲超過 Shorts 長度，保留為長版母帶，另選精準 15 秒 hook。素材不足時使用核准靜幀、歌詞字幕與慢速 zoom-out／輕微平移建立節奏，不用私人或不合格畫面補數量。
- 多平台一次匯出＋自動生縮圖：`a8_platform_formats.py export <music> <prefix> <clips...> --platforms youtube|vertical|all`（相同規格只 render 一次；各平台安全區見 `specs`）。

### 0.2 公開欄位先做「客人眼睛」掃描

- 活動日期只有在客人搜尋、報名或檔期判斷真的需要時才公開；一般案例頁、歌詞、字幕、標題、Pin 與描述預設不露日期。
- `草稿、審核、內部、快速導覽、使用素材、生成、轉檔、A2/A8、下一步` 等流程語言只留 receipt，不出現在公開文章或平台欄位。
- WordPress 案例至少配置三種資訊角色：完整桌景、餐點／菜單細節、空間或配置情境。相同照片的不同裁切不能冒充三種角色。
- 圖片檔名與 alt 採 `maplab-{場景}-{描述}`／`台南{場景}外燴—{可見內容}`；alt 只描述畫面，不堆關鍵字。
- 公開前對文章、歌詞、字幕、標題、描述和 Pin 文案一起掃描日期與內部詞，不能只檢查其中一份。

### 0.3 中英混唱先過 exact-token 發音 gate

- 只截含英文片語的 12–20 秒測試，不先生成整首；兩個候選使用相同歌詞、相同曲風方向，只比較咬字。
- 以官方下載音檔在本機 ASR 辨識，不送外部 endpoint、不把預期歌詞當 initial prompt。英文片語必須 exact match；例如 `cream` 被辨識為 `queen` 就淘汰。
- 發音 gate 只選出可沿用的 diction prompt，不代表完整歌詞、曲風、母帶或發布已核准。

### 0.4 正式母帶也要過 actual-audio gate

- 正式候選必須對**實際下載音檔**跑不帶 initial prompt 的 ASR，並由真人完整聽辨；`邦尼兔`、`MAPLAB` 等品牌詞逐一 exact-token 記錄。任何一項聽錯、吞字或含糊就回音樂生成，不准靠字幕掩蓋。
- ASR／人工聽辨出的逐句內容還必須與 receipt 綁定的 Owner 核准歌詞完全一致；唱到另一版（例如具名 hook 對上公開安全版文字）也要退件，不能只把字幕換成核准版。
- 15 秒 hook 不得從字中間切入；第一個唱詞前保留 0.2–0.5 秒。hook 的來源母帶 SHA-256、in/out 與聽辨結果寫進 acceptance receipt。
- 音訊沒過 gate 時，不得進正式剪輯。為除錯而產生的片必須在檔名與 receipt 標 `INTERNAL_DIAGNOSTIC_NOT_PUBLISHABLE`，不能送 Owner 當發布候選。

---

## 1. 標準流程表（每步：輸入 → 動作 → 工具/腳本 → 產出 → QA）

| # | 步驟 | 輸入 | 動作 | 工具 / 腳本 | 產出 | QA |
|---|------|------|------|-------------|------|----|
| 1 | 取素材 | Drive 專案子夾 fileId | 下載精選照片到本機 | Drive API（`~/.claude/mcp-keys` token；refresh 見 §6）| `pilot-{name}/raw/*` | 檔案數對、非私密畫面 |
| 2 | 轉正 | raw 照片（含 HEIC）| 依 EXIF 轉正，不盲轉 | `tools/ai_workbook/a8_auto_orient.py`；HEIC 用 `sips -s format jpeg` | `oriented/*.jpg` | orient=6 轉正、orient=1 不動 |
| 3 | A4 出圖 | oriented | 轉 webp + 2:3 直式 pin | `cwebp -q 80`；`ffmpeg` scale/crop 1000×1500 | `webp/*.webp`、`*_pin.jpg` | 尺寸/色調對；命名 `maplab-{場景}-{描述}` |
| 4 | 音訊 gate | 核准歌詞 + 實際下載母帶 | ASR＋真人完整聽辨；鎖定 hook | prompt-free ASR + 人工聽辨 | audio receipt + hash + hook in/out | 品牌詞 exact-token；不從字中間切 |
| 5 | 歌詞校時 | 選定音訊 + 核准歌詞 | 依 waveform 逐句標 in/out；切點吸附句界／beat | CapCut／核准 NLE；或等效人工 timeline | SRT/JSON + timeline receipt | onset ≤100ms；tail ≤200ms；歌詞／行銷字分軌 |
| 6 | Review draft | 原始素材 allowlist + timing map | 本機試排素材、比例與模板 | `a8_enhanced_video_draft.py`（review-only）| review MP4 + cover | 不得標 final；不得送上傳 |
| 7 | 正式剪輯 | raw originals + timing map | CapCut／核准 NLE 人工精修；或 raw 直入的一次性 FFmpeg filtergraph | CapCut／核准 NLE；`ffmpeg_one_pass` 例外路徑 | 長／短片 + 可編輯專案／lineage | 無模糊側欄、盲裁、proxy、重複有損編碼 |
| 8 | 完整 QA | 正式輸出 | 1×、0.5× 完整播放＋target-device 目視 | 播放器 + contact sheet + `a8_video_acceptance.py` | `QA_PASS` receipt | 逐句同步、清晰度、隱私、全片完整 |
| 9 | 存檔 | webp/pin/mp4 + receipt | 回存專案 Drive `/publish/` | Drive API multipart upload | Drive `/publish/*` | 檔案可開、命名與 hash 對 |
| 10 | 上片草稿 | `OWNER_VIDEO_GATE` 的 hash-locked mp4 / pin | YouTube 私人草稿、Pinterest 發布前草稿 + 填欄位 | Chrome → Studio / Pinterest | 私人影片、待發布 Pin | 欄位、連結、alt、圖片尺寸齊 |
| 11 | 核准 | 草稿連結＋欄位摘要 | Owner 一次確認各對外動作 | Studio / Pinterest / WP | approval 決定 | 送出前 Owner 明確同意 |
| 12 | 發布回讀 | 已核准草稿 | 逐平台發布後打開公開頁回讀 | Chrome | 公開連結與截圖 | 標題、描述、圖片、CTA、可見度正確 |
| 13 | 狀態回報 | 平台矩陣＋已回讀連結 | 有阻塞先備妥「缺件通知」；全數完成後再備妥「完成通知」 | Telegram Web | Owner 知道缺什麼或可點擊成果 | 發送前取得 Owner action-time approval；發送後重讀訊息氣泡與連結 |

### 1.1 多平台發布矩陣與 Telegram 通知語意

- 標準矩陣：YouTube 長版、YouTube Shorts、TikTok、Instagram Reels、Facebook Reels、Pinterest Pin；Owner 可按個案縮減，但不得默默漏平台。
- `BLOCKED`／`NEEDS_OWNER_ACTION` 不是靜默條件。缺登入、選檔、平台連結或核准時，應先準備並發送缺件通知，逐項寫清平台、缺件、Owner 最短動作與已完成成果。
- 「完成通知」只在本案核准的平台都有可回讀連結後發送；不能拿「尚未完成」當成完全不通知的理由。
- Telegram 發送屬代表 Owner 的外部通訊，按下送出前須取得當下確認。若尚未取得確認，receipt 必須標為 `MESSAGE_READY_NOT_SENT`，不可寫成已通知。

---

## 2. 正式剪輯工具與固定色卡

### 2.1 工具角色，不再把 review 當 final

| 工具 | 正式角色 | 必留證據 |
|---|---|---|
| `a8_enhanced_video_draft.py` | 素材／比例／模板 review-only；永遠停在 `RENDERED_UNVERIFIED` 之前 | draft manifest；檔名含 `review` |
| CapCut／核准 NLE | 預設正式剪輯：waveform 校時、逐句字幕、切點、轉場、聲畫完整播放 | 可編輯 project、timeline 截圖／匯出、export hash |
| Canva | 封面、開場／結尾品牌字卡、overlay 素材；可進 NLE，但不能單憑一張 Canva export 證明歌詞校時 | design link／ID、export hash、被引用的 timeline receipt |
| `ffmpeg_one_pass` | 無外部 NLE 時的等效正式路徑；原檔直接進單一 filtergraph，只能一次有損視訊編碼 | 完整 command/filtergraph、raw hashes、timing map、encode lineage |

CapCut／Canva 是正式 workflow 的工具選項，不是成功的自動證明。沒有 editable timeline、逐句時間碼、完整播放與 hash receipt，無論用了哪個品牌工具都不能升到 final。

Review renderer 可用 `--visual-preset maplab_ig_soft` 並明寫 `--aspect 9:16` 或 `--aspect 16:9`。它的實作只供試排：

- **運鏡**：ffmpeg `zoompan`（dolly_in / dolly_out / pan_left/right / static），每幕 2.4–2.8s。
- **字幕/浮水印**：**Swift/AppKit 在透明畫布繪字**（不靠 ffmpeg drawtext，避免精簡版 ffmpeg 無 drawtext），再 ffmpeg `overlay` 疊上；右下 `MAPLAB Kitchen` 浮水印。
- **濾鏡**：`maplab_ig_soft`＝暖、柔、低對比、亮度微升、飽和微升、輕銳化。
- **轉場**：`xfade=fade` 0.35s。開場暖米覆膜 1.4–1.8s（MAPLAB Kitchen＋service line＋細金線）。結尾暖米 CTA（依 `--category`）。
- **長短分工**：YouTube 長版原生 16:9，以全曲與完整敘事為主；Short 原生 9:16，同型音樂案例固定 15 秒，hook 起迄時間寫進 receipt。禁止把直式片套模糊邊框冒充長版。

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

**category → CTA / 場景色 對照**：opening（開幕）、corporate_tea（企業茶會）、wedding（婚禮）、birthday（週歲/抓周）、graduation（畢業典禮/親子成長）、brand_event、private_party、art_wine、custom_box、general。CTA 與平台 metadata 必須由同一 category profile 帶出（例：graduation＝「台南畢業典禮、親子活動茶點｜官方 LINE 洽詢檔期 @maplab」），不得沿用 seed case 的場地、客戶或活動類型。

---

## 2.5 影片優先原則 ＋ 真片段剪輯（重要）

**原則：有影片素材就優先用真片段剪輯，不要只把相片轉影片。**
- 案例夾若有 `.mov / .mp4` → 用真片段剪成短片。
- 只有沒有影片時，才退回相片 zoompan（Ken Burns）。
- 流程：A2/A3/A4 個案「內容確認」後才發 A8 建片；每案標明哪些有影片檔（附時間碼更佳）。

**Review 工具現況**：`tools/ai_workbook/a8_enhanced_video_draft.py` **已支援影片輸入**（`VIDEO_EXTS={.mov,.mp4}`），但只可做試排：
- 影片段：自動 crop 置中 9:16 → scale 1080×1920 → **取每支開頭 N 秒（`--seconds`）** → 疊 Swift IG Soft 字幕 → `maplab_ig_soft` 濾鏡 → xfade 串接；音軌去除（發布前配授權樂）。
- 相片段：zoompan 運鏡。**同一支片可混用影片＋相片**（把 MOV 與精選 webp 放同一 asset-dir）。
- 用法：`--asset-dir` 指到「含 MOV 的資料夾」即可（先前 pilot 只餵相片，之後改餵 MOV/混合）。

**挑片段 in/out（正式解法）**：
- 限制：工具目前只取「每支**開頭** N 秒」，不能自動挑中段最佳片段。
- review 可先做無損／stream-copy 預剪來試排；正式輸出不得把預剪 H.264 proxy 再重編。正式 timeline 必須保存 raw original path/hash 與每個 shot 的 in/out，直接由 NLE 或一次性 FFmpeg 從原檔解碼。
- 素材先過 A8 A/B/C 分級（A 直用、B 需裁/遮臉/遮 logo、C 私密不可用）。

**缺口（待評估建）**：尚無「自動偵測最佳片段 in/out」工具；目前靠人工/個案標時間碼。可評估建 `a8_clip_trim.py`（讀時間碼清單 → 批次預剪 → 餵 enhanced draft）。**等 b285b719 選出 3 案（標明哪些有影片檔）再依此準備剪輯流程。**

---

### 2.5.1 成品視覺 QA 與素材覆蓋 gate

每支待審片都必須同時留下以下六種證據，缺一就只能寫 `RENDERED_UNVERIFIED`：

1. **原始素材盤點**：照片／影片總數、格式與來源；不能只看已被 WP 壓縮的衍生圖。
2. **allowlist manifest**：實際進時間軸的檔名、影片安全 in/out、排除理由與素材數。renderer 的預設 `limit` 必須明列；manifest 數量少於計畫數就退件。
3. **完整時間軸 contact sheet**：涵蓋 intro、每幕、轉場與 outro；要以實際成品抽幀，不用來源圖或 storyboard 代替。
4. **視覺辨識 readback**：以人眼／vision 實看原始 contact sheet 與成品時間軸，逐項判斷裁切、清晰度、主體、字幕、日期、人臉、QR／電話與內部工作語。ffprobe、位元率、HTTP 200、render exit 0 都只是技術 preflight。
5. **人工歌詞 timeline**：核准歌詞逐句 `text/start_ms/end_ms`、音訊 hash、waveform／beat 依據；歌詞 onset 在 30fps 下誤差 ≤3 frames（100ms），tail ≤6 frames（200ms）。禁止把行銷文案當歌詞、禁止平均分配 scene 秒數。
6. **完整播放 readback**：同一輸出 hash 以 1× 與 0.5× 從頭看到尾，記錄 reviewer、watched duration、target device 與 verdict；抽三幀或 contact sheet 不能替代。

素材策略：

- 案例夾有原始影片時，成品至少要有真實動態片段；低解析 WP WebP 不得成為唯一影片來源。
- Short 優先使用原生直式影片與高解析直式照片；不得用「橫片縮小置中＋大面積模糊背景」補足直式畫面，除非 Owner 明確選此風格。
- 長版直式素材用雙直式 split-screen 或實色品牌側欄；禁止模糊側欄。原生橫式影片維持清晰全幅。
- 照片採 full-fit 品牌畫布或人工 subject-safe crop；禁止盲目中心裁切。
- 正式輸出最多一次有損視訊編碼。原檔 → H.264 proxy → scene H.264 → xfade H.264 這類多代流程一律退件。
- 若 Owner 說「裁切不對／很糊／沒有用我的影片」，立即把目前版本標為退件；先回到原始素材 coverage 與完整時間軸 readback，不在低解析成品上反覆加濾鏡。

### 2.5.2 不可跳級的狀態機與機器 gate

正式候選只能依序前進：

`AUDIO_SELECTED → TIMING_LOCKED → EDIT_READY → RENDERED_UNVERIFIED → QA_PASS → OWNER_VIDEO_GATE → APPROVED_FOR_UPLOAD`

- 不准從 render exit 0、ffprobe PASS 或 contact sheet 直接跳 `OWNER_VIDEO_GATE`。
- `tools/ai_workbook/a8_video_acceptance.py <acceptance_receipt.json>` 必須回 `ok=true`，才可進 Owner 審片；發布器只能吃 receipt 綁定的 output path/hash，不接受任意 `--video`。
- CapCut／核准 NLE 路徑必有 editable project＋timeline receipt；Canva 單獨只算封面／overlay receipt。
- `ffmpeg_one_pass` 路徑必須 `no_intermediate_video=true`，並保存 raw hashes、filtergraph、timing map 與 encode lineage。
- 任一檔案 hash、歌詞、音訊或 timeline 變動，舊 `QA_PASS` 立即失效，回到相應狀態重跑。

---

## 2.6 音樂／旁白工具鏈（Creative Engine v0）

**第三方音樂送出 gate（2026-08-25）**：先在 repo 產 `lyrics_review.md`，跑 `a8_lyrics_engine.py review`，把歌詞給 Owner 直接核稿；只有收到明確「歌詞通過」或採納 Owner 改句後，才建立 `submission.md` 並送外部平台。只送通過審查的抽象歌詞與曲風，不送 Drive 原圖／影片。若歌詞來自含客戶或兒童的私人案例，公開具名與送出／消耗額度分別需要核准；試聽產物不直接當商用成品。

**Suno 訂閱期 checkpoint（2026-08-25）**：官方說明指出，後續訂閱預設不會替免費期舊歌補發商用權；Pro／Premier 有效期間建立的歌曲才取得其商用使用權，且商用權不等於保證著作權成立。因此每個正式 case 在歌詞通過後，都以可見的有效訂閱重新建立新母帶，並記錄方案、建立時間、版本與發音；舊免費歌只保留作風格參考。官方來源見 `workbook/reviews/JOB-A2-BUNNY-CASE-TO-LYRICS-20260825/suno_subscription_rights.md`。

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

### 唱/rap 供應商優先序（Owner 定，最省）
1. **fal.ai 免費 credits 優先**（新註冊送 ~$20≈570 首、$0.035/首、有 API、商用）→ 達標就放心多用做實際產出＋更多曲風；每次跑後追蹤剩餘 credits 記 `state/`。adapter：`a8_fal_minimax_gen.py`。
2. **fal credits 見底 → 切 MiniMax $5**（最小儲值≈33 首，key 已在 bot/.env）→ **提醒 Owner 儲值，不自動花錢**。adapter：`a8_minimax_gen.py`。
3. 之後 fal PAYG $0.035/首（比 MiniMax $0.15 便宜）。
- **⚠️ 現況（2026-08）**：fal 帳號目前 **403 locked「Exhausted balance」**——免費 $20 未生效/已用完，**暫不可用**；MiniMax 亦 1008 餘額不足。技術全通(key/endpoint 都對)，唯一 gate＝帳號餘額。→ 先解 fal billing（加卡啟用免費額度）或直接 MiniMax $5，才生得出來。

---

## 3. 品牌語氣（字幕/標題/描述都套）

完整見 `skills/brand-voice-guide.md`。要點：說場景不硬賣、具體名詞、開放感（不用「保證/一定」）、不用「不是…而是…」句型。

**字幕每幕 6–14 字**，先過禁用詞。**禁用詞**：最頂/超值/保證/CP值/佛心/便宜又大碗/錯過可惜/趕快預約/名額有限/一生一次/不訂會後悔/限時優惠；**A8 額外流程禁用語**：取餐/順暢/分開/方便交流/促進交流/確保/動線穩/節奏更穩/節奏穩健。少用：精緻/質感/用心/客製化。

字幕文案 QA＝①禁用詞掃描 ②長度 6–14 ③無佔位/亂碼 ④抽幀目視中文正常渲染；歌詞聲畫 timing 另依 §2.5.1 驗收，兩者不可互相取代。

---

## 4. YouTube 上片 SOP（Chrome → Studio，私人草稿）

1. 確認 Chrome 已登入 MAPLAB 頻道（channel `UC85n15rcFgHzZtb78vV6-sw`，maplabkitchen）。
2. Studio 右上「建立」→「上傳影片」。
3. 先關閉 Chrome 其他分頁殘留的下載／儲存對話框，再用 `file_upload` 做一次 preflight。若 file chooser 對 repo、Documents、`outputs/` 與 tmp 都回 `Not allowed`，視覺點擊也無法把受控分頁交給 macOS 選檔器，立即記 `UPLOAD_BLOCKED`；不得反覆換路徑、不得把空對話框或 HTTP 200 當上傳成功。當案最短恢復是 Owner 手選已驗證檔案；長期才依官方 YouTube Data API upload guide 建含 `youtube.upload` scope 的最小 adapter。
4. 填標題、描述（§5 模板）、目標觀眾＝**否，這不是兒童專屬**（必填）。
5. 瀏覽權限＝**私人**（草稿）。**絕不選公開**；公開等 Owner。
6. 儲存。垂直 <3 分自動歸類 **Short**（連結變 `youtube.com/shorts/…`）。
7. **YouTube Studio 內建「編輯器」（開放性編輯器）**：上片後可在左側「編輯器」做 **trim 首尾／剪掉中段／加片尾／模糊處理**，適合對已上傳片微調，走 Chrome MCP 操作（Studio 可控已驗證）。**用於發布前微修，不取代本機真片段剪輯**（本機剪輯可重跑、可 commit、有 IG Soft 模板；Studio 編輯器是線上手動微調）。
8. 上傳完成後逐欄回讀：標題、描述首兩行、縮圖、字幕、播放清單、觀眾設定、可見度與影片 URL。YouTube 沒有影片或縮圖的獨立 alt 欄位；可及性以描述性標題、描述與字幕承接，不得捏造 alt 已填。
9. 若同一 file chooser 第二次仍回 `Not allowed`，停止重試，保留 Studio 上傳視窗並請 Owner 手選 receipt 中的絕對路徑；選檔後代理接續填欄位與 QA。

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

### 5.1 Pinterest 圖片 SEO 欄位

- 版型：2:3，建議 1000×1500；從 WP 已核准照片製作，不另拿未審素材。
- 標題：100 字以內，前 40 字先交代 `台南＋活動類型＋畫面主體`。
- 說明：500 字以內，先寫畫面與規劃價值，再放對應 WordPress 案例連結；不放內部工作語言。
- 替代文字：500 字以內，只描述可見餐點、器皿、花藝和配置，不把關鍵字串成清單。
- 發布後打開 Pin 回讀圖片、標題、說明、alt、連結與看板；任一欄缺失就不回報完成。

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

---

## 8. 對標實作採用原則（2026-08-26）

- YouTube：官方 `youtube/api-samples` 已 archived，只拿來理解 OAuth／resumable upload 結構；新 adapter 以現行官方 upload guide 為準，不 vendoring 舊 sample。瀏覽器 Studio 可用時仍是第一路徑。
- Pinterest：官方 `pinterest/api-quickstart` 仍維護、Python／Apache-2.0；只有瀏覽器 Google 登入或 Create Pin 路徑重複失敗時，才用它建立最小 OAuth＋Create Pin adapter。
- 平台 adapter 的 acceptance 不是 API 200，而是公開／私人目標狀態、platform ID、可讀 URL、標題／描述／alt／連結 readback 與 durable receipt。
- 單一案例發布失敗時保留既有影片、圖片與 metadata；不重做內容，也不另建第三套 queue。下一輪從 `platform_metadata.md` 與 release receipt 繼續。
