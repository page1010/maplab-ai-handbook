# A8 做歌流程 — 可攜 SOP Runbook（任何 agent 照抄就能跑）

> 目標：任何 agent（含 Hermes / OpenRouter 腦）照此步驟即可執行整條「brief → 歌詞 → Suno → 剪片 → 多平台 → 回填 DB」，不用重問。
> 建立：2026-08 ｜ 對齊：`skills/a8-produce-to-publish-sop.md`（產片上片）、`skills/a8-chinese-rhyme-rubric.md`（押韻）、`docs/platform_formats_sources.md`（平台格式）
> 前置環境：`python3`＋`numpy`＋`Pillow`＋`ffmpeg/ffprobe`。本機 venv 範例：`/tmp/ttsenv/bin/python`。工作根目錄：`~/maplab-ai-handbook`。
> **原則：file-only、不花錢、secrets 絕不外露。凡「花錢/對外發佈」一律停下等 Owner。**

---

## 🚦 Owner Gate 一覽（agent 不可自行跨越）
- **G1 Suno 生成**：在 Suno 網站人工生成全曲（免費層或 Owner 帳號）。agent 只出 pack，不代生成、不碰帳密。
- **G2 對外發佈**：上傳只到「私人/草稿」；公開一律 Owner 手動翻。
- **G3 花錢**：任何付費 API（MiniMax/fal 儲值）需 Owner 明確授權。

---

## Step 0 — 收 brief
**輸入**：Owner 在該首的 brief Doc 填「目標／場景／調性」（範本見本檔末連結）。
**動作**：讀 brief，決定 `id`（例 `bunny-grad-hiphop-v1`）、客戶名、場景、風格 tag。
**輸出**：一個 DB entry 草稿（先記在 `workbook/a8/music_creative_db.json`）。
**卡點**：brief 欄位不全 → 用最小假設補，並在 brief Doc 留言問 Owner。

## Step 1 — 寫歌詞 → 過引擎（押韻＋品牌安全）
**輸入**：brief。
**動作**：
1. 依 brief 寫中文歌詞（hook 前置、副歌洗腦、Verse 點名餐點/場景；置入客戶名＋「台南外燴」＋「MAPLAB」）。存 `workbook/a8/<id>/lyrics.txt`。
2. 過引擎審查：
   ```
   python3 tools/ai_workbook/a8_lyrics_engine.py review workbook/a8/<id>/lyrics.txt --client "<客戶名>"
   ```
   看回傳 JSON：`passed` 要 true（無禁用詞/敏感/佔位）、`rhyme.rhymed_ratio` 越高越好、`per_section` 依 `suggest_words` 修弱韻行。
**輸出**：通過審查的 `lyrics.txt`；押韻 note。
**卡點**：`passed=false` → 依提示改詞重跑，直到過。禁用詞表見 `a8-produce-to-publish-sop.md` §3。

## Step 2 — 出 Suno pack（prompt + meta-tag 歌詞）
**輸入**：DB entry `id`（歌詞已寫進 entry 的 `suno_lyrics`，含 `[Chorus][Female Vocal]`／`[Verse][Male Rap]` 等 meta-tag）。
**動作**：
```
python3 tools/ai_workbook/a8_lyrics_engine.py suno-pack <id>            # 預設風格
python3 tools/ai_workbook/a8_lyrics_engine.py suno-pack <id> --variant trap|lofi   # 變體
```
**輸出**：可貼進 Suno 的「風格 prompt ＋ meta-tag 歌詞」文字包。貼進 brief Doc 的「Suno prompt」欄。
**卡點**：無（純本機）。

## Step 3 —【G1】Owner 在 Suno 生成全曲
**動作**：Owner（或授權後 agent 於瀏覽器）把 pack 貼進 Suno，生全曲（~2–3 分鐘，可 regenerate 2–3 次選最好）。下載 mp3。
**輸出**：`workbook/a8/<id>/song.mp3`（Owner 放回本機）。
**卡點（Owner Gate）**：agent **不代生成、不碰 Suno 帳密**。若 Owner 授權 API 生成（花錢）→ 見 G3，用 `a8_minimax_gen.py`／`a8_fal_minimax_gen.py`（需 Owner 授權額度）。

## Step 4 —（可選）把真曲混入已剪好的字幕片
若已有「靜音＋字幕」版影片、只是要換上真曲：
```
python3 tools/ai_workbook/a8_mux_suno.py <silent_captioned.mp4> workbook/a8/<id>/song.mp3 <out.mp4> [--vol 0.9]
```
一般走 Step 5 直接對拍剪輯即可，這步用於替換既有 placeholder 音軌。

## Step 5 — 多平台匯出（YouTube 長版 + Shorts ≤30s + 縮圖）
**輸入**：`song.mp3` ＋ 素材片段 clips（避開業主/賓客/孩童臉）。
**動作**：
```
python3 tools/ai_workbook/a8_platform_formats.py export \
  workbook/a8/<id>/song.mp3 <prefix> <clip1.mov> <clip2.mov> ... \
  --platforms youtube --outdir workbook/a8/<id>/out
```
- `--platforms youtube` = 長版 16:9 ＋ Shorts 9:16(≤30s)；要全平台用 `all`，只垂直短片用 `vertical`。
- 相同規格只 render 一次（省算力）；自動生對應尺寸縮圖。
- 查各平台規格/安全區：`python3 tools/ai_workbook/a8_platform_formats.py specs`。
**輸出**：`<prefix>_youtube_long.mp4`(1920×1080)、`<prefix>_youtube_shorts.mp4`(1080×1920, 30s)＋各自 `_thumb.jpg`（1280×720／1080×1920）。
**QA**：`ffprobe` 確認寬高＋時長；Shorts ≤30s；字幕（若有）在安全區內、非豆腐字。

## Step 6 — 回填 DB outputs
**動作**：在 `workbook/a8/music_creative_db.json` 該 entry 的 `outputs[]` 補：檔名、平台、時長、縮圖、（發佈後）連結。
**輸出**：DB 該首 `outputs` 完整、`song` 由 pending → 檔名。
**Commit**：
```
git add workbook/a8/music_creative_db.json workbook/a8/<id>/ && git commit -m "A8 <id>: 出片＋回填 DB"
```

## Step 7 —【G2】發佈（Owner 核准）
上傳只到 **YouTube 私人草稿**（走 `a8-produce-to-publish-sop.md` §4 Chrome→Studio，或未來 `a8_youtube_upload.py` API 私人草稿）＋填標題/描述/#Shorts。**公開一律 Owner 手動翻。**

---

## 一頁速查（agent 照抄）
```
0. 讀 brief Doc → 定 id/客戶/場景/風格 → 起 DB entry
1. 寫 lyrics.txt → a8_lyrics_engine.py review <lyrics.txt> --client <客戶>   # passed 要 true
2. a8_lyrics_engine.py suno-pack <id>                                        # 貼進 brief Doc
3. [G1 Owner] Suno 生全曲 → song.mp3
5. a8_platform_formats.py export song.mp3 <prefix> <clips...> --platforms youtube --outdir out
6. 回填 DB outputs → git commit
7. [G2 Owner] 上私人草稿 → Owner 公開
```

## 相關檔案
- 腳本：`tools/ai_workbook/a8_lyrics_engine.py`、`a8_platform_formats.py`、`a8_mux_suno.py`、`a8_beat_mux.py`
- DB：`workbook/a8/music_creative_db.json`
- 規範：`skills/a8-produce-to-publish-sop.md`、`skills/a8-chinese-rhyme-rubric.md`、`docs/platform_formats_sources.md`
- brief+審核 Doc 範本（Owner Drive，每首「建立副本」複製一份）：https://docs.google.com/document/d/1nfG9aM8UI1iOZ1A0MOpxDyKix92Haiy93LI3rap_lPs/edit
