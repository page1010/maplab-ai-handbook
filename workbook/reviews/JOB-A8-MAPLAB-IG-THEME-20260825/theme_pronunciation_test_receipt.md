# MAPLAB 主題曲英文發音測試收據

日期：2026-08-26（Asia/Taipei）
狀態：`PRONUNCIATION_TEST_ONLY`

## Input

- Google Doc 已反讀最新 Owner 版本；待測句為 `lemon and cream　在燈下透著光`。
- 測試歌詞只取一段主歌，不等於完整主題曲歌詞核准。
- Prompt：`Short 25-second City Pop and Mandopop female light rap, clear bilingual diction, sing “lemon and cream” distinctly as three English words on one rhythmic phrase, compact melody around the English phrase, warm clean voice, polished commercial mix, clean ending.`

## Candidates

- 12 秒：https://suno.com/song/4896bfaa-74b8-4cf6-a054-66e08294c752
- 18 秒：https://suno.com/song/7a8d7ecf-bc6a-4a37-b6a0-128c78343046

## Local ASR Gate

- 兩個候選都由 Suno 官方 MP3 download 取得，只在本機用 `mlx-community/whisper-small-mlx` 辨識；沒有把音訊送給第三方 endpoint，也沒有用預期歌詞當 initial prompt。
- 候選 A（12 秒）：辨識為 `Lemon and Queen`，`cream` 不清楚，`FAIL`。
- 候選 B（18 秒）：辨識為 `Lemon and Cream`，三個英文單字 exact match，`PASS`。
- 決定：完整 v2A／v2B 生成沿用候選 B 的 bilingual diction 指令；候選 A 不進正式曲。

## Decision Boundary

- 這兩個版本只驗證英文片語能否在同一拍句唱成三個單字；不公開、不剪正式影片、不取代 v2A／v2B 的完整曲風比較。
- Suno song page 顯示歌詞與兩個完成時長；正式母帶尚未選定，因此不記錄成 release asset。
- 下一步：Owner 仍可比較兩版聽感；機器 gate 已選候選 B 的咬字規則。Owner 核准完整歌詞後，再把相同 bilingual diction 規則帶進 v2A／v2B。
