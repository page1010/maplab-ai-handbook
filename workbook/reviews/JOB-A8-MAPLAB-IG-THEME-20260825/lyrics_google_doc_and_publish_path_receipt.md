# MAPLAB 主題曲歌詞／Prompt／發佈路徑 Receipt

日期：2026-08-25

## Durable Delta

- 品牌語氣：完整歌詞與 exact 15 秒 Hook 已把泛化 AI 句型改成具體餐桌場景；v1 保留為 history。
- Google Doc：https://docs.google.com/document/d/1VicisMW7dVmwkr9wjL-l3hxlwJn3SLGH6-RcHtQHVKI/edit?tab=t.0
- Drive API readback：文件標題、完整歌詞、`讓笑聲坐到最後`、exact 15 秒 Hook、A/B 演唱方向均可讀。
- City-pop：完成一份來源化研究與兩個可比較 prompt；A 版 102 BPM、B 版 94 BPM。
- Prompt registry：新增 `workbook/music_prompt_registry/experiments.jsonl` 與 fail-closed validator；v1／v2A／v2B 都有狀態與權利邊界。
- TikTok：登入 `@maplabkitchen` 的 Studio upload page 已打開並驗證；沒有上傳／發布。
- Suno：Pro annual、2500/2500 credits、新歌商用權利與每月 20 downloads UI 已讀回；因歌詞尚未核准，本輪沒有消耗 credits。

## Release Asset Rule

- 正式歌曲：provider Download → 本機 release path → SHA-256 → registry `selected_release`。
- UI 錄影：只屬流程／視覺證據，`audio_asset.method=screen_recording` 永遠不得通過 release validator。

## Validation

- `python3 tools/ai_workbook/validate_music_prompt_registry.py` → `ok=true`。
- lyrics review → `ok=true`、banned/sensitive/soft overuse 均為 `0`。
- focused unittest → `Ran 8 tests`、`OK`。
- targeted `git diff --check` → PASS。

## Gate / Next

Verdict：`OWNER_LYRICS_GATE`。

Owner 回覆 `主題曲歌詞通過` 後，只生成 v2A／v2B 第一輪候選並留下 provider ID、時間、權利與發音評分；未選曲前不剪正式片，未核准前不送 TikTok。
