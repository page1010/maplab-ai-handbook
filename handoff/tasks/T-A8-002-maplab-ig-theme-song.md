# T-A8-002 — MAPLAB IG 品牌主題曲

## 接續狀態

- **狀態**：🟠 OWNER_LYRICS_GATE
- **建立日期**：2026-08-25
- **Owner**：A8 影音內容產線
- **接續點**：品牌語氣修正版歌詞、exact 15 秒 Hook、City-pop A/B 曲風 prompt、長短版分鏡、Google Doc 審稿面與可驗證 prompt registry 已完成；Owner 新增的 `lemon and cream` 已做兩個私有發音測試，本機 ASR 淘汰候選 A、候選 B exact match 通過。2026-08-27 另完成雙視角第二讀：保留《把相聚端上桌》，提案把 75–90 秒收斂為 62–70 秒，加入 8 小節服務場景 Rap，並建立實際 WP 01–10 音樂系列規劃。
- **唯一阻塞**：Owner 尚未選定 Rap 受眾與 15 秒 Hook 是否唱出品牌，也尚未逐句核准《把相聚端上桌》完整歌詞；發音測試不等於核准，未生成完整候選、未渲染正式影片。

## Goal

把 MAPLAB 已被 Owner 認可的 IG 視覺語言轉成可重複使用的品牌聲音：一首 75–90 秒主題曲，加一段語意完整的 exact 15 秒 Hook，供 Reels／Shorts／品牌片使用。

## Evidence Base

- `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md`
- `skills/maplab-visual-spec.md`
- `skills/brand-voice-guide.md`
- Owner-provided IG screenshots and the 2026-06-17 read-only `@maplabkitchen` Reels readback already captured in T-A8-001.

## Deliverables

- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/ig_style_brief.md`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/lyrics_review.md`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/lyrics.txt`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/style_prompt.txt`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/visual_storyboard.md`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/validation_report.md`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/city_pop_research_notes.md`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/tiktok_publish_path.md`
- `workbook/music_prompt_registry/experiments.jsonl`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/theme_second_read_20260827.md`
- `workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/visual_cut_plan_v3_proposal.md`
- `workbook/reviews/JOB-A8-MAPLAB-MUSIC-SERIES-20260827/wp_music_series_01_10.md`

Owner 審稿 Google Doc：

- https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0

## Acceptance

- 歌詞可唱、沒有 SEO 堆字、沒有內部工作語或未核准客戶資訊。
- MAPLAB 只在 Final Chorus 出現一次，品牌不壓過故事。
- exact 15 秒 Hook 是獨立完整語意，不從長歌任意硬切。
- 視覺延續暖光、餐桌節奏、少字與低壓銷售；截圖只作 1–2 秒品牌開場。
- 未經明確歌詞核准，不送音樂生成；未經平台 approval，不上傳或公開。

## Next Bounded Action

Owner 先選：① Rap 採混合場景或企業品牌優先；② 15 秒 Hook 只靠畫面 Logo 或增加一次 `MAPLAB` 音訊 tag。選定後把第二讀版本同步到 Google Doc 逐句核稿；只有 Owner 明確回覆 `主題曲歌詞通過` 才可生成兩個候選，留下版本、時間、權利與發音收據，回到 Owner 選曲 gate。

## 2026-08-27 Second-read／Series Checkpoint

- 主 agent 與獨立第二讀皆首選保留《把相聚端上桌》；弱點一致指向「現主歌偏單一家庭聚會，服務辨識不足」。
- 修正提案把廣告內容放進 8 小節輕 Rap：品牌開幕、會議茶點、婚禮、週歲，以及動線、菜單、桌景、份量、器皿、取餐節奏；副歌不改成服務清單。
- 音樂 prompt 增加 Hook-first、Rap bars、behind-the-beat flow、鼓／bass 能量與 stop-time audio-logo 規格；建議長度 62–70 秒。
- 影片提案只使用有原檔與 allowlist 的素材；邦尼兔、ICC 與 B2B 場景組成四場景品牌片，未在音訊 gate 前冒充正式成片。
- 官方 WP 01–10 頁面於 2026-08-27 逐頁回 HTTP 200；系列計畫已寫入 `JOB-A8-MAPLAB-MUSIC-SERIES-20260827/`。美術館頁面仍有「大新／大慶」正文漂移，A2 修正前不寫專名歌詞。
- 發現歌詞 SSOT 漂移：repo 檔仍為「檸檬和奶油」，Task Card／Google Doc 記錄為 `lemon and cream`；生成前必須反讀 Google Doc 並同步正式檔。
- 邊界：本 checkpoint 只做研究與提案；未改 Google Doc、未送 Suno、未耗額度、未渲染或發布。

## 2026-08-26 English Pronunciation Checkpoint

- Google Doc API 已反讀 Owner 最新句子：`lemon and cream　在燈下透著光`。
- 只取主歌做兩個私有 v5.5 測試，要求把 `lemon and cream` 在同一拍句清楚唱成三個英文單字：
  - https://suno.com/song/4896bfaa-74b8-4cf6-a054-66e08294c752（12 秒）
  - https://suno.com/song/7a8d7ecf-bc6a-4a37-b6a0-128c78343046（18 秒）
- 收據：`workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/theme_pronunciation_test_receipt.md`。
- 本機 ASR（無 initial prompt）：候選 A=`Lemon and Queen` FAIL；候選 B=`Lemon and Cream` PASS。完整生成沿用 B 的 bilingual diction 規則。
- 邊界：`PRONUNCIATION_TEST_ONLY`；不公開、不交 A8 正式剪片、不解除完整歌詞 gate。

## 2026-08-25 Brand／Rights／Publish-path Checkpoint

- 已把泛化的副歌句改為具體場景句 `讓笑聲坐到最後`，完整歌詞與 exact 15 秒 Hook 已同步到 Google Doc 並由 Drive API 反讀。
- 曲風結論：以 city-pop 的 16-beat／R&B／jazz-fusion 語彙承接 MAPLAB 城市餐桌感；拖音、短滑音、晚進拍與轉音是 A/B 變因，不把誇張日式唱腔當 genre requirement。
- Suno 帳號 readback：Pro annual、credits `2500/2500`、新歌具 commercial-use rights；每月 `20` 次 song downloads，介面標示自 `2026-09-03` 起。歌詞未核准，因此本輪仍 `0` 次生成。
- Prompt registry：v1 留作 superseded history；v2A 102 BPM、v2B 94 BPM 均為 `planned`。正式發佈母帶只接受 provider Download + SHA-256；畫面側錄只能做 UI／流程證據。
- TikTok Studio：`@maplabkitchen` 已登入；上傳頁接受 MP4，頁面建議 1080p／1440p／4K 與 16:9／9:16。本輪沒有上傳或發布。
- Receipt：`workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/lyrics_google_doc_and_publish_path_receipt.md`。

## Resume Prompt

```text
你是 MAPLAB Hip-hop Songwriter。先完整讀 CURRENT_STATUS.md、pitfalls.md、skills/maplab-hiphop-songwriter/SKILL.md、skills/brand-voice-guide.md、skills/a8-produce-to-publish-sop.md 與 handoff/tasks/T-A8-002-maplab-ig-theme-song.md。

Owner 正在審《把相聚端上桌》。先讀 theme_second_read_20260827.md、visual_cut_plan_v3_proposal.md 與 JOB-A8-MAPLAB-MUSIC-SERIES-20260827/wp_music_series_01_10.md；Google Doc 是 https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0。先確認 Owner 對「混合場景 vs 企業優先」與「15 秒畫面 Logo vs 音訊 MAPLAB tag」的選擇，再反讀 Google Doc，解決 repo「檸檬和奶油」與文件 `lemon and cream` 的 SSOT 漂移。只有明確回覆「主題曲歌詞通過」才可準備外部生成。一般「繼續／跑完」不是歌詞核准。核准後在有效訂閱下只生成兩個第一輪候選並留 receipt；正式母帶只用 provider Download。未選曲前不交 A8 正式剪片，未核准平台前不發布。WP 音樂系列每次只做一案，不一次生成九首。
```
