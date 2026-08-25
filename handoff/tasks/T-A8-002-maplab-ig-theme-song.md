# T-A8-002 — MAPLAB IG 品牌主題曲

## 接續狀態

- **狀態**：🟠 OWNER_LYRICS_GATE
- **建立日期**：2026-08-25
- **Owner**：A8 影音內容產線
- **接續點**：品牌語氣修正版歌詞、exact 15 秒 Hook、City-pop A/B 曲風 prompt、長短版分鏡、Google Doc 審稿面與可驗證 prompt registry 已完成；TikTok Studio 已驗證登入與上傳規格。
- **唯一阻塞**：Owner 尚未逐句核准《把相聚端上桌》歌詞；未送外部音樂生成、未耗額度、未渲染正式影片。

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

Owner 審稿 Google Doc：

- https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0

## Acceptance

- 歌詞可唱、沒有 SEO 堆字、沒有內部工作語或未核准客戶資訊。
- MAPLAB 只在 Final Chorus 出現一次，品牌不壓過故事。
- exact 15 秒 Hook 是獨立完整語意，不從長歌任意硬切。
- 視覺延續暖光、餐桌節奏、少字與低壓銷售；截圖只作 1–2 秒品牌開場。
- 未經明確歌詞核准，不送音樂生成；未經平台 approval，不上傳或公開。

## Next Bounded Action

Owner 回覆 `主題曲歌詞通過` 或逐句修改。核准後只做一件事：在有效訂閱權益下生成主題曲候選，留下版本、時間、權利與發音收據，回到 Owner 選曲 gate。

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

Owner 正在審《把相聚端上桌》。歌詞、15 秒 Hook、IG 風格 brief、City-pop A/B prompt、研究、分鏡與驗證都在 workbook/reviews/JOB-A8-MAPLAB-IG-THEME-20260825/；Google Doc 是 https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0。Prompt registry 在 workbook/music_prompt_registry/。先讀 Owner 的逐句回覆；只有明確回覆「主題曲歌詞通過」才可準備外部生成。一般「繼續／跑完」不是歌詞核准。核准後在有效訂閱下只生成 v2A／v2B 第一輪候選並留 receipt；正式母帶只用 provider Download，畫面側錄只作 UI 證據。未選曲前不交 A8 正式剪片，未核准平台前不發布。
```
