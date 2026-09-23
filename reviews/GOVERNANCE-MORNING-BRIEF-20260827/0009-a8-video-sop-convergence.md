# A8 影音 SOP 收斂治理報告

時間：2026-08-27 00:09 CST
角色：A8 影音產線修復與驗收員
範圍：只稽核／修正本機 SOP、gate 與內部回歸證據；沒有上傳、發布、登入第三方剪輯器或發 Telegram。

## What

1. Owner 確認歷史 MAPLAB 影音曾使用 Canva／CapCut 與人工精修；本機亦找到 2025 Canva-like Reel 匯出，及同資料夾後續帶音訊與 re-encode 標記的 `0326.mp4`。後者符合第二個 NLE 精修跡象，但因缺工程檔／軟體標籤，只能列為「疑似 CapCut／其他 NLE」。邦尼兔 15 秒 review 的可追溯 receipt 則是 Swift/AppKit＋FFmpeg；目前找不到能和邦尼兔 output 配對的 Canva／CapCut project。缺少配對 receipt 代表不能重播或歸因該次流程，不代表歷史上沒用過工具。
2. 歷史技能書把 local FFmpeg 定義為 dry-run／review，把 Canva／CapCut／Google Vids 定義為正式精修；較新的 `a8-produce-to-publish-sop.md` 卻寫「產片一律用 `a8_enhanced_video_draft.py`」。兩份規範互相衝突，review draft 因而被提升成 final candidate。
3. 現行 v2 的字幕是固定等分的行銷文案，不是核准歌詞 timing；renderer 沒有音訊／歌詞 alignment 輸入。hook 又從第一個品牌詞附近硬切。
4. 現行 v2 使用 `approved_sources` H.264 proxy，經 proxy、scene、xfade 多次有損編碼；長版含模糊側欄，照片／影片有盲目中心裁切風險。
5. 現有 v5.5 master 與 alt 的 prompt-free ASR 都沒有保存 `邦尼兔`／`MAPLAB` exact-token；本輪對實際 15 秒回歸輸出重跑 ASR，又確認唱到的是具名 hook，而綁定文件是公開安全版。

## So What

失敗不是「某一條既有 SOP 被漏跑」這麼單純。真正根因是成功時曾使用／規劃的人工精修觀念沒有被固化成可驗證契約，之後又有一份 SOP 把 review renderer 升格為正式引擎。只看尺寸、秒數、抽幀與 render exit 0，會讓拖拍、錯詞、咬字、模糊側欄、盲裁及多代編碼全部穿過。

Canva／CapCut 也不是品牌名稱一出現就代表合格。真正不可缺的是可重開工程、editable/manual timeline、人工美感配方、逐句時間碼、raw provenance、encode lineage、完整播放與 output hash。CapCut／核准 NLE 是預設正式路徑；Canva／Google Vids 在留下等效 project/timeline/export/reopen receipt 時也可承接完整影片，否則只算 cover／overlay／draft；一次性 FFmpeg 只有在留下等效證據時才能成為正式替代路徑。

## 第一性原理五題

1. 理想人工流程：先通過實際音訊聽辨，依 waveform 校歌詞，再由 raw originals 組片，完整播放後保存 editable project／lineage 與 hash。
2. 現況與理想差異：現況先 render，再用抽幀與規格宣告完成；歌詞、音訊、畫面與上傳 gate 沒有共同 receipt。
3. 真正限制：不是非某一家 SaaS 不可，而是正式 timeline 和可驗證證據不可省。Canva／CapCut 是工具；gate 才是制度。
4. 若從零設計：`AUDIO_SELECTED → TIMING_LOCKED → EDIT_READY → RENDERED_UNVERIFIED → QA_PASS → OWNER_VIDEO_GATE → APPROVED_FOR_UPLOAD`，任何狀態不得跳級。
5. 本輪現場驗證：讀取實際 media metadata、raw contact sheets、prompt-free ASR、Canva design search、Chrome 裡 Canva／CapCut 狀態，並對新內部回歸片完成 1×、0.5× 全片播放。

## Now What

- `skills/a8-produce-to-publish-sop.md` 先升 v2.0 收斂 audio/timing/raw/encode gate；Owner 討論後再升 v2.1，把歷史 Canva／CapCut 實作、Google Vids、工程重開、tool chain、polish recipe、rights、target-device 與 platform package 正式納入。
- `skills/a8-video-pipeline-skills.md` 明確回指 final SSOT；`a8_enhanced_video_draft.py` 恢復為 review-only。
- 新增 `a8_video_acceptance.py` 與負向測試。現行 v2 穩定被 13 個理由拒絕，包括 `LYRIC_ALIGNMENT_MISSING`、`LYRICS_AUDIO_MISMATCH`、`RAW_PROVENANCE_UNBOUND`、`ENCODE_DEPTH_EXCEEDED`。
- 新增 `a8_one_pass_timeline.py`，證明 raw originals、explicit crop、逐句 overlay、音訊與單次 libx264 可在同一 filtergraph 可重跑。
- 內部回歸片的 raw／timing／encode／完整播放已通過，但 final gate 仍因音訊咬字、歌詞版本、真人聽辨與 target-device QA 返回 `ok=false`。這是預期的 fail-closed，不是未完成的成功宣告。

下一個 bounded action：依 Owner 目前 Google Doc 鎖定唯一歌詞版本，重新生成母帶；先讓 actual-audio ASR＋Owner 真人聽辨通過，再進 CapCut／核准 NLE 或 evidence-complete one-pass timeline。新母帶未通過前，不上傳 YouTube／TikTok／Instagram／Facebook／Pinterest。

## Alignment Audit

- Active Task：A8 邦尼兔影音退件收斂。
- Current State：`AUDIO_REGEN_REQUIRED`；現行 v2 與內部回歸片均 `NOT_FOR_UPLOAD`。
- Owner-visible proof：內部回歸 MP4、0.5 秒完整 contact sheet、1×／0.5× ended readback、兩份 acceptance JSON。
- Remaining gap：唯一核准歌詞版本、新母帶 exact-token、Owner 真人聽辨、手機實看、正式 NLE project receipt。
- Approval boundary：本輪沒有外部 upload／publish／message；任何平台草稿仍需通過 `OWNER_VIDEO_GATE` 並取得相應確認。

## Post-Discussion Addendum — 2026-08-27

Owner 指正「不是漏跑但寫在 SOP，而是 Canva／CapCut 等以前做過的部分沒有進 canonical SOP」。重新稽核後採納這個更精確的歸因：

- `OWNER_CONFIRMED_PRACTICE`：歷史 MAPLAB 曾用 Canva／CapCut＋人工精修。
- `FILE_VERIFIED`：2025 Canva-like 1080×1920 無聲 Reel export；其後另有帶音訊的 re-encoded 版本。
- `INFERRED_NOT_VERIFIED`：第二版很可能經 CapCut／其他 NLE 二次剪輯，但沒有 CapCut project/tag，不能冒充已驗證。
- `BUNNY_SPECIFIC`：邦尼兔目前沒有 matching Canva design、CapCut project 或 Google Vids project；可追溯版本為 Swift/AppKit＋FFmpeg review。

治理結論因此從「沒有做過」改為「做法沒有被制度化與保存，無法在新 session 精確重跑」。SOP v2.1 與 acceptance v2 已把工程重開、實際工具鏈、人工精修配方、權利、裝置 QA、平台包與四類分離核准列為 `QA_PASS` 必備；舊 platform exporter 也因 blind crop／多代 H.264 被預設拒絕。這次沒有生成新歌、上傳平台、發布或發 Telegram。
