# MAPLAB IG 主題曲第一輪驗證

日期：2026-08-25

Verdict：`OWNER_LYRICS_GATE`

## 完成

- 以 Owner 截圖與 2026-06-17 `@maplabkitchen` 唯讀反讀所建立的 MAPLAB IG Soft v1 為風格 truth。
- 交付《把相聚端上桌》75–90 秒歌詞、exact 15 秒 Hook、對外歌詞介紹、音樂 style prompt 與長短版分鏡。
- 歌詞只使用 MAPLAB 已核准品牌定位；沒有客戶名、日期、價格、內部路徑、素材分級或工程敘述。

## 機器驗證

- `a8_lyrics_engine.py review .../lyrics.txt --client MAPLAB`
  - `ok=true`
  - banned hits `0`
  - sensitive hits `0`
  - soft overuse `0`
  - `has_hook=true`
  - `has_verse=true`
  - brand placement：`MAPLAB`
  - rhyme ratio：`0.5`（押韻提示是寫作輔助，不冒充聽感 QA）
- `python3 -m unittest tests.test_a8_lyrics_engine tests.test_a8_enhanced_metadata`
  - `Ran 5 tests`
  - `OK`
- `python3 -m py_compile tools/ai_workbook/a8_lyrics_engine.py tools/ai_workbook/a8_platform_formats.py`
  - PASS
- `git diff --check`
  - PASS

## 尚未執行

- 未送 Suno 或其他外部生成器。
- 未耗任何音樂生成額度。
- 未取得新母帶、未交 A8 渲染、未上傳任何平台。
- 一般「繼續／跑完」不替代逐句歌詞核准。

## 唯一下一步

Owner 回覆 `主題曲歌詞通過` 或貼出要改的句子。明確核准後才在有效訂閱權益下生成第一輪音樂候選。
