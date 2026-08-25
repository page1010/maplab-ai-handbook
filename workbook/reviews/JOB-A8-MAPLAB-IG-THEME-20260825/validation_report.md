# MAPLAB IG 主題曲品牌語氣／曲風／發佈路徑驗證

日期：2026-08-25

Verdict：`OWNER_LYRICS_GATE`

## 完成

- 以 Owner 截圖與 2026-06-17 `@maplabkitchen` 唯讀反讀所建立的 MAPLAB IG Soft v1 為風格 truth。
- 交付《把相聚端上桌》75–90 秒歌詞、exact 15 秒 Hook、對外歌詞介紹、音樂 style prompt 與長短版分鏡。
- 歌詞只使用 MAPLAB 已核准品牌定位；沒有客戶名、日期、價格、內部路徑、素材分級或工程敘述。
- Owner 指出的泛化 AI 語氣已修正：副歌以 `讓笑聲坐到最後` 取代原句，v1 留在 history，不覆寫學習紀錄。
- Google Doc 已建立並由 Drive API 反讀標題、完整歌詞、exact 15 秒 Hook、A/B 演唱方向與 Owner gate。
- `workbook/music_prompt_registry/experiments.jsonl` 已建，v1／v2A／v2B 的 prompt、stage、權利邊界與正式母帶來源規則可追溯。

## 機器驗證

- `a8_lyrics_engine.py review .../lyrics.txt --client MAPLAB`
  - `ok=true`
  - banned hits `0`
  - sensitive hits `0`
  - soft overuse `0`
  - `has_hook=true`
  - `has_verse=true`
  - brand placement：`MAPLAB`
- rhyme ratio：`0.42`（押韻提示是寫作輔助，不冒充聽感 QA）
- `python3 -m unittest tests.test_validate_music_prompt_registry tests.test_a8_lyrics_engine tests.test_a8_enhanced_metadata`
  - `Ran 8 tests`
  - `OK`
- `python3 tools/ai_workbook/validate_music_prompt_registry.py`
  - `ok=true`
  - `errors=[]`
- `python3 -m py_compile tools/ai_workbook/validate_music_prompt_registry.py tools/ai_workbook/a8_lyrics_engine.py tools/ai_workbook/a8_platform_formats.py`
  - PASS
- `git diff --check`
  - PASS

## Owner-facing Readback

- Google Doc：https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0
  - title：`MAPLAB 主題曲《把相聚端上桌》｜歌詞與曲風審稿`
  - Drive API 可讀到 `讓笑聲坐到最後`、exact 15 秒 Hook 與 A/B 演唱方向。
- TikTok Studio：https://www.tiktok.com/tiktokstudio/upload?from=webapp&tab=video
  - logged-in profile：`@maplabkitchen`
  - page-visible upload guidance：MP4、最高 30 GB／60 分鐘，建議 1080p／1440p／4K、16:9 或 9:16。
- Suno account：Pro annual、`2500/2500` credits；每月 `20` 次 downloads 的介面標示自 `2026-09-03` 起；本輪未按 Create。

## 尚未執行

- 未送 Suno 或其他外部生成器。
- 未耗任何音樂生成額度。
- 未取得新母帶、未交 A8 渲染、未上傳任何平台。
- 一般「繼續／跑完」不替代逐句歌詞核准。
- 未以畫面側錄保存或冒充正式音源；正式母帶只接受平台 Download。

## 唯一下一步

Owner 回覆 `主題曲歌詞通過` 或貼出要改的句子。明確核准後才在有效訂閱權益下生成第一輪音樂候選。
