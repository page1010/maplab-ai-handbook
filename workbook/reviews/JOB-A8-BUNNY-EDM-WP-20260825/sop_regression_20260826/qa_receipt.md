# A8 SOP 回歸驗收收據

狀態：`INTERNAL_DIAGNOSTIC_NOT_PUBLISHABLE`。這支片只證明修正版剪輯機制可重跑；它不是新歌成品，也不得上傳。

## 眼見結果

- 回歸片：`maplab-bunny-alignment-regression-INTERNAL-NOT-PUBLISHABLE.mp4`
- SHA-256：`aacc5ddd5b80dabbf7f1360fbd2f1339e78abc6313f3c459443a5eeaa844413d`
- ffprobe：H.264／AAC、1080×1920、30fps、15.000 秒；視訊約 9.0 Mbps、音訊約 262 kbps。
- 0.5 秒完整時間軸：`qa/timeline-0p5s.jpg`，SHA-256 `deb92205264765d693a5afd0dfa2ea128b0c5692202164d29210b2e4e8f51d04`。
- Chrome QA player 對同一輸出完成：`15.00 / 15.00 sec • 1× • ended` 與 `15.00 / 15.00 sec • 0.5× • ended`。
- 人眼 readback：三支 raw source 直接進 timeline；沒有模糊側欄；橫片採明列的 `1215×2160 x=1312 y=0` subject-safe crop；歌詞與 internal outro 是分開 overlay。

## 可重跑證據

- Timeline：`render_config.json`，SHA-256 `c4973eeecebc86db18548d252c02c01ea7c834f2edd0cad95f16bd0580ba65ff`。
- 歌詞校時：`alignment.json`，SHA-256 `a910a25df678e1a7421c36376803f8def8e871f179d05041885fc28d5db98a1c`。
- Encode lineage：`encode_lineage.json`，SHA-256 `b6b7e60b13268831e27bdae5eedb7b65fe544c4b582e24f7e89c55c066482288`。
- Renderer：`tools/ai_workbook/a8_one_pass_timeline.py`；raw trim／scale／manual crop／overlay／audio trim 在同一個 filtergraph 完成，`actual_lossy_video_encode_depth=1`。

重跑：

```bash
python3 tools/ai_workbook/a8_one_pass_timeline.py \
  workbook/reviews/JOB-A8-BUNNY-EDM-WP-20260825/sop_regression_20260826/render_config.json \
  --overwrite

python3 tools/ai_workbook/a8_video_acceptance.py \
  workbook/reviews/JOB-A8-BUNNY-EDM-WP-20260825/sop_regression_20260826/diagnostic_acceptance.json
```

## 為什麼仍然退件

實際輸出再次跑 prompt-free `mlx-community/whisper-small-mlx`，聲段界線為：

| 實際聲段 | ASR 時間 | Timeline 時間 | 邊界差 |
|---|---:|---:|---:|
| 第一行 | 0.00–2.88s；完整母帶人工界線約 0.36s 起 | 0.36–2.88s | 尾端 0ms |
| 第二行 | 2.88–6.34s | 2.88–6.36s | 20ms |
| 第三行 | 6.34–9.72s | 6.36–9.74s | 20ms |
| 第四行 | 9.72–13.32s | 9.74–13.44s | onset 20ms／tail 120ms |

校時已進入 SOP 容許值，但 ASR 文字為「把你吐吧祝福天亮…」，`邦尼兔` 等 exact-token 失敗；音訊實際唱的是具名 hook，綁定的 Owner 文件則是公開安全版。Gate 因此仍回 `ok=false`，只剩下五類阻擋：

- `AUDIO_ASR_FAILED`
- `BRAND_TOKEN_FAILED`
- `HUMAN_LISTEN_MISSING`
- `LYRICS_AUDIO_MISMATCH`
- `TARGET_DEVICE_QA_MISSING`

也就是：raw／裁切／逐句 timing／一次編碼／完整 1× 與 0.5× 播放已可重複；新母帶、Owner 真人聽辨與手機實看仍未通過，不能把本片升成發布候選。
