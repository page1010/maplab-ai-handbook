# MTR 封面→YT 發布 SOP v1(Owner 5250:「你bgm封面圖也進sop到能發yt」)

> 頻道:MAP TABLE RADIO(音樂頻道全權在 Fable5,Owner 5048)
> 上游正典:projects/youtube-music-channel-plan-20260909.md §三(四段管線)。本 SOP 把其中
> [3] 封面/微動畫 與 [4] 上傳 落成可執行步驟,並接上 [1] 晨會 brief 與 [2] Suno 音檔。
> 建立:2026-09-14。ffmpeg 已確認存在(/opt/homebrew/bin/ffmpeg)。

## 全鏈總覽(每首歌一輪)

C0 晨會 brief → C1 封面靜圖 → C2 微動畫 loop → C3 音影合成 → C4 YT 上傳(unlisted)→ Owner 圈選 → 轉公開

每段有驗收關卡(GATE),前段沒過不進下段。全鏈除 Suno 外零額度。

## C0 晨會 brief(已自動化)

- 腳本:`scripts/yt_daily_hermes_meeting.sh`(每天新的一天第一輪跑,免費鏈,同日冪等)。
- 產出:`data/music-style-db/daily/brief_YYYYMMDD.md`,內含 JSON。
- **GATE C0**:JSON 必含 `base_style_id / suno_prompt / bpm / title_zh / scene_story / yt_description / cover_prop / next_variation_note`,缺 key 不往下走。

## C1 封面靜圖(已實作+實跑通過)

- 腳本:`scripts/mtr_cover_gen.sh`(讀當日 brief,零額度程式繪製)。
- 規格:2560x1440 PNG(YT 頻道橫幅/影片縮圖皆夠用),存 `data/music-style-db/covers/cover_YYYYMMDD.png`,並自動上 Drive anyone-reader 印連結。
- 視覺母題(v2 定版,Owner 5255「cyberpunk風一點」):台南騎樓下的派對長桌 — **藍青→霓虹紫夜空**、暖橘長桌+吊燈三盞(暖色=品牌識別保留)、**騎樓柱掛霓虹燈牌x2(洋紅/青,抽象霓虹管不寫假店名)**、**桌緣青色霓虹收邊**、盤杯燭光、蒸氣;左上頻道名 MAP TABLE RADIO + 曲名(serif 大字+**青/洋紅色差殘影**)+ BPM 行;右下 by maplabkitchen。燈牌必須掛在柱上不浮空(9/14 v1 浮空霓虹教訓)。
- 每日變化:只換 `cover_prop` 一件桌上道具(brief 的 next_variation_note 驅動),其他不動 — 對齊 Lofi Girl「同場景微變化」策略。
- 字型鐵律:標題必須逐字驗證字形(pick() 依序試 Songti.ttc face 0-5、PingFang.ttc face 0-3,每個字 getmask 有 bbox 才收)。Songti 預設 face 缺 鹽/頭/慶 等繁字,9/14 v1 已踩過。避免「・」(無字形),分隔用「/」。
- **GATE C1(人工必看)**:Read 輸出 PNG 目檢 — ①標題每字完整無豆腐 ②文字不與吊燈/道具相撞 ③無客戶照片、無 logo、無客戶資訊 ④道具與當日 brief 相符。沒看圖不得把連結交給 Owner(9/14 v1 缺字教訓)。

## C2 封面微動畫 loop(已實作+首跑通過 9/14)

- 工具:ffmpeg(/opt/homebrew/bin/ffmpeg)。零額度。已併入 `scripts/mtr_cover_gen.sh` 自動接在 C1 後跑。
- 作法(類 Lofi Girl 微動畫,Owner 5255):靜圖呼吸變焦 — zoompan z=1.02+0.012*sin(2π·on/600),25fps 600 幀=24 秒,sin 全週期→首尾同幀無縫;1920x1080 H.264 yuv420p。後續可加燭光/霓虹脈動疊層(v3 備選)。
- 產出:`data/music-style-db/covers/loop_YYYYMMDD.mp4` + `loop_preview_YYYYMMDD.png`(6 秒處抽幀供目檢)。
- **GATE C2**:可播放、sin 全週期保證首尾同幀、preview 抽幀目檢無破圖;檔案 <50MB。

## C3 音影合成(等 A8 Suno 音檔)

- 輸入:A8 交付的成品 WAV(卡 T-A8-YT-MUSIC-CHANNEL-001,目前 0/20;無人聲、2 takes 選 1)。
- 作法:ffmpeg 以 C2 的 loop 視訊 stream_loop 到音檔等長,mux 成 `data/music-style-db/videos/mtr_YYYYMMDD.mp4`(1080p)。
- **GATE C3**:影片時長=音檔時長(±1s);記錄音檔 sha256 入當日 brief 檔尾;試播頭尾各 10 秒。

## C4 YT 上傳(通道已備,等頻道建立)

- 憑證:google token 已含 youtube.upload scope(REST 手動 refresh 通道已驗證;token 只 source 不回顯)。
- 前置(一次性,Owner):YouTube 頻道建立沒有 API,需 Owner 手機/GUI 點一次建頻道。建好後全部自動。
- Metadata 全部來自 brief:標題=title_zh(台南真實派對場景=長尾搜尋入口);說明前兩行=scene_story+maplabkitchen 連結(引流心機);歌詞永不進公開說明。
- 一律先 **unlisted** 上傳 → 連結給 Owner 圈選 → Owner 說上才轉公開(未經圈選不得發布)。
- **GATE C4**:API 回傳 videoId 且 unlisted 可播;圈選前不轉公開、不排播放清單。

## 紅線(每段都適用)

- 不用客戶照片/客戶資訊;封面不打 logo;歌詞不進 WP 與公開說明。
- token/金鑰只在腳本內流動,不回顯不入 repo。
- Suno 僅 A8 卡額度(月≤24 首上限、無人聲);不仿聲、不餵現成錄音。
- win-01 不碰音樂/影音(A8 專屬)。

## 目前缺口(到「能發 YT」)

1. YouTube 頻道未建 — Owner GUI 一次(唯一人工步驟)。
2. Suno 音檔 0/20 — 等 A8 開跑。
(C2 loop 已於 9/14 首跑通過 GATE C2,cyberpunk v2 靜圖同日過 GATE C1。)

頻道建好+第一首音檔到位 → 當天可出第一支影片。
