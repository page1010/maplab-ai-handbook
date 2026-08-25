# 邦尼兔 A8 本機驗證報告

日期：2026-08-25
狀態：`edm_trial_complete_publish_gate`

## 已驗證

- Drive case：`0717邦尼兔-托嬰畢業典禮`，共 28 件素材（MOV 4、HEIC 16、JPEG 6、MP4 2）。
- Privacy：`c02` 因含幼兒人像海報列 C 級；review draft 以 `--asset-file c01.mov --asset-file c03.mov` 白名單生成，`c03` 只取 0–2.8 秒安全時間窗。
- Renderer：移除跨案例硬編碼的「大臺南會展中心／企業會議／動線穩」，新增 `graduation` profile；輸出 metadata 未發現上述錯誤詞或 `c02.mov`。
- Video：`workbook/a8/pilot-bunny/review_mv/a8-short-review-draft.mp4`，H.264、1080x1920、30fps、7.833s；中段與封面人工回讀未見人物、標題未裁切。
- Lyrics：`hiphop_lyrics_v2.txt` 與 `edm_lyrics_v1.txt` 經歌詞引擎檢查皆 `ok=true`、禁詞 0、敏感詞 0；中文押韻率 1.0、雙押提示 4。
- Tests：`python3 -m unittest tests.test_a8_enhanced_metadata tests.test_a8_lyrics_engine` → `Ran 5 tests ... OK`。
- Preflight：Python compile 與 `git diff --check` 通過。
- Suno：Owner 當輪明確要求消耗每日免費額度後，只按一次 Create；平台自動產出 4 個 private variants
  （v4.5-all 2 個、v5.5 Preview 2 個）。四個頁面都已完成渲染，第一個 v4.5-all 成品長 2:37。
- Lyrics readback：第一個 v4.5-all 成品頁完整顯示 `edm_lyrics_v1.txt` 的 Intro、Verse、Pre-Chorus、
  Chorus、Drop、Bridge 與 Final Chorus；標題 `邦尼兔・把祝福點亮`、style `electronic dance-pop,
  future-bass` 均正確。這證明歌詞已寫入成品；未以文字存在冒充人工聽辨發音。

## 成果檔

- WP 審稿草稿：`wp_draft.md`
- 已核對舊版歌詞：`hiphop_lyrics_v2.txt`
- EDM 新版歌詞：`edm_lyrics_v1.txt`
- Suno 貼上包：`suno_edm_submission.md`
- Suno 生成收據：`suno_generation_receipt.md`
- 素材分級：`source_manifest.md`
- 本機審核影片：`../../a8/pilot-bunny/review_mv/a8-short-review-draft.mp4`

## 尚未執行／邊界

- 只送出抽象活動歌詞與曲風；未把 Drive 原始照片／影片送往 Suno。
- 已消耗一次 Create；平台自動給 4 variants，不是人工重複下四次。
- 尚未做逐字人工音訊發音 QA；文字層歌詞與結構已 readback PASS。
- 未在 WordPress 建立 draft 或 publish。
- 未上傳 YouTube、TikTok、Instagram、Pinterest 或 Telegram。

## 唯一下一步

先由 Owner 試聽 4 個 private variants，選 1 個候選；下一個 bounded action 只做該候選的發音／副歌／品牌語氣人工 QA。未選曲前不再生成；未另行核准不 publish、不上傳社群、不建立 WordPress draft。
