# MAPLAB Music Prompt Registry

這裡是音樂生成實驗的單一紀錄入口。每一次曲風測試各占 `experiments.jsonl` 一列，讓下一位 Agent 能知道：用了哪版歌詞、哪個 prompt、哪個模型、生成結果、選曲理由與正式母帶來源。

## 最小流程

1. 生成前建立 `planned` 記錄，prompt 本文留在 task bundle。
2. 生成後補 `provider_song_id`、`generated_at` 與聽感評分，狀態改成 `generated_unselected` 或 `rejected`。
3. Owner 選曲後才標成 `selected_release`。
4. 正式母帶以平台 Download 取得；記錄本機相對路徑與 SHA-256。畫面側錄只屬 UI 驗證，不成為發佈音源。
5. 執行 `python3 tools/ai_workbook/validate_music_prompt_registry.py` 驗證欄位與 release asset 規則。

## 評分欄位

- `brand_voice`：像不像 MAPLAB。
- `mandarin_clarity`：華語咬字與聲調是否清楚。
- `hook_memory`：15 秒後是否記得旋律與主句。
- `visual_fit`：是否能承接暖光、餐桌、慢速 zoom-out。
- `vocal_naturalness`：拖音、滑音、轉音是否自然。

分數採 1–5；未生成時保留 `null`。
