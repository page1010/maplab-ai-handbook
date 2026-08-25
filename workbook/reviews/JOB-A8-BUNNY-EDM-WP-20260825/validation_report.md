# 邦尼兔 A8 本機驗證報告

日期：2026-08-25
狀態：`owner_gate`

## 已驗證

- Drive case：`0717邦尼兔-托嬰畢業典禮`，共 28 件素材（MOV 4、HEIC 16、JPEG 6、MP4 2）。
- Privacy：`c02` 因含幼兒人像海報列 C 級；review draft 以 `--asset-file c01.mov --asset-file c03.mov` 白名單生成，`c03` 只取 0–2.8 秒安全時間窗。
- Renderer：移除跨案例硬編碼的「大臺南會展中心／企業會議／動線穩」，新增 `graduation` profile；輸出 metadata 未發現上述錯誤詞或 `c02.mov`。
- Video：`workbook/a8/pilot-bunny/review_mv/a8-short-review-draft.mp4`，H.264、1080x1920、30fps、7.833s；中段與封面人工回讀未見人物、標題未裁切。
- Lyrics：`hiphop_lyrics_v2.txt` 與 `edm_lyrics_v1.txt` 經歌詞引擎檢查皆 `ok=true`、禁詞 0、敏感詞 0；中文押韻率 1.0、雙押提示 4。
- Tests：`python3 -m unittest tests.test_a8_enhanced_metadata tests.test_a8_lyrics_engine` → `Ran 5 tests ... OK`。
- Preflight：Python compile 與 `git diff --check` 通過。

## 成果檔

- WP 審稿草稿：`wp_draft.md`
- 已核對舊版歌詞：`hiphop_lyrics_v2.txt`
- EDM 新版歌詞：`edm_lyrics_v1.txt`
- Suno 貼上包：`suno_edm_submission.md`
- 素材分級：`source_manifest.md`
- 本機審核影片：`../../a8/pilot-bunny/review_mv/a8-short-review-draft.mp4`

## 尚未執行

- 未把歌詞或 Drive 原始素材送往 Suno 或其他第三方。
- 未消耗每日免費音樂額度。
- 未在 WordPress 建立 draft 或 publish。
- 未上傳 YouTube、TikTok、Instagram、Pinterest 或 Telegram。

## 唯一下一步

Owner 當輪核准後，只送一次 `edm_lyrics_v1.txt` 與 `suno_edm_submission.md` 的抽象歌詞／曲風到免費層，生成一首內部試聽 EDM；回讀發音、副歌與品牌語氣，留下 receipt，停止在試聽結論。
