# 邦尼兔內容接力

這個案例採依序接力，避免三種專業在同一份公開稿裡互相污染。

## Stage 1 — A2 WordPress / SEO

- Input：`source_manifest.md`、核准的公開事實、A2 品牌與 SEO 技能。
- Output：`wp_draft.md`、`wp_internal_notes.md`、`wp_assets/`。
- Done：公開稿可直接給客人閱讀；無日期、內部狀態、素材判定、路徑或生成工具敘述；SEO 欄位與真實內鏈留在內部包。
- Current：`approval_ready`，尚未建立或發布 WordPress 草稿。

## Stage 2 — Hip-hop Songwriter

- Input：Stage 1 的 customer-ready event brief、Owner 選定曲風、`skills/maplab-hiphop-songwriter/SKILL.md`。
- Output：歌詞、曲風 prompt、選曲與 15 秒 hook 交接。
- Done：歌詞引擎通過；Owner 選曲；完整歌曲與 15 秒 hook 明確分開。
- Current：既有歌詞已生成，Owner 已選 v4.5-all 版本一；2:37 是長版母帶，45.0–60.0 秒已切成精準 15 秒 hook 候選。切點仍待 Owner 聽感確認。

## Stage 3 — A8 Video / Distribution

- Input：Stage 2 選定母帶、A 級素材、平台與授權 SOP。
- Output：16:9 長版、精準 15 秒直式 Short、字幕、封面、各平台 metadata 與 approval card。
- Done definition：長短片都經 ffprobe 與目視 QA；缺素材時用核准靜幀、字幕與慢速 zoom-out 補足，不取用 C 級畫面；所有上傳與發布仍等 Owner 核准。
- Current：15 秒直式審核版已完成（H.264/AAC、1080×1920、30fps、15.000 秒）；2:37 的 16:9 長版歌詞影片仍在 A8 queue，尚未渲染或上傳。
