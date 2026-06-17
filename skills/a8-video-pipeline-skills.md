# A8 影音內容產線技能書（Video Pipeline Skills）

> 負責角色：A8 影音內容產線
> 建立：2026-04-19 | 版本：v2.4（2026-06-17）

---

## 0. 這本技能書解決什麼

A8 的工作不是「想到影片題目」，而是把 MAPLAB 現有資料夾、案例文章、照片與短影片，變成可審核、可上傳、可分發、可回收成下一版素材規則的影音產線。

本技能書適用於：

- Owner 給一個 IG / TikTok / YouTube Shorts 參考，要求研究底層流程。
- A8 需要從 Google Drive / repo review bundle / A4 素材資料夾取案例。
- A8 要把一組照片或文章變成 YouTube Shorts、TikTok、IG Reels、Pinterest 封面。
- A8 要先 dry-run，再把正式上傳交給 Owner / A1 approval。

---

## 1. Cold Start

1. 讀 `CURRENT_STATUS.md`。
2. 讀本次 task card，例如 `handoff/tasks/T-A8-001-folder-to-video-distribution.md`。
3. 讀 `recalls/A8_recall.md`、`skills/maplab-visual-spec.md`、`skills/brand-voice-guide.md`。
4. 若任務是短影音，讀本次 bundle 裡的 motion style / reference matrix；沒有就先建立，不得直接套泛用模板。
5. 確認素材來源與 public-safe case label；資料夾原名若含客戶、專案、內部日期，先標為 internal evidence，不直接上字幕或封面。
6. 輸出 Startup Check：角色、素材來源、預計輸出、哪些動作需要 approval。

---

## 2. 標準流程：資料夾案例到多平台短影音

### Step 1：Intake

建立 review bundle：

```text
workbook/reviews/JOB-A8-{SLUG}-{YYYYMMDD}/
```

必備檔案：

- `research_notes.md`：參考 Reel / 競品 / 工具研究。
- `source_manifest.md`：來源資料夾、可用照片、不可公開資訊、public-safe label。
- `storyboard.md`：3-5 個鏡頭、每鏡頭畫面、字幕、旁白、CTA。
- `platform_metadata.md`：YouTube / TikTok / IG / Pinterest 的標題、描述、hashtag、封面說明。
- `validation_report.md`：dry-run、規格、缺口、approval 狀態。

### Step 2：素材判讀

對每個資料夾先分三類：

| 類型 | 可用方式 |
|---|---|
| A 級：食物、桌面、場景乾淨，無臉/無私人資料 | 可直接進 dry-run 與 AI 工具 |
| B 級：畫面可用但需裁切、遮字、避開 logo/臉 | 只進 draft，不可直接上傳 |
| C 級：含私人會議資料、清楚人臉、QR code、電話、合約、簡報 | 不用於 public output |

Public-safe label 例：

```text
Internal: 0612大台南會展中心-工研院在宅醫療科技推動計畫跨部會工作小組會議
Public-safe: 大臺南會展中心企業會議茶點
```

### Step 3：腳本與 AI 工具分工

參考 Reel 的底層邏輯是「一個工具化工作流 + 一個可被複製的結果」，不是照抄內容或 hashtag。

A8 要把 MAPLAB 版本寫成：

```text
資料夾真實案例 → 3 秒 hook → 3-5 個畫面 → 一句服務觀察 → CTA → 多平台 metadata
```

工具分工：

| 工具 | A8 用途 | 產出 |
|---|---|---|
| Gemini / GPT | 拆腳本、字幕、平台 metadata、封面文案 | `storyboard.md` / `platform_metadata.md` |
| Google Vids / Canva / CapCut | 正式組片、字幕、封面字卡 | 9:16 mp4 + cover |
| Higgsfield / 其他 AI video tool | 只在需要生成動態鏡頭或 AI motion 時使用 | 生成片段，必須保留 prompt 與來源 |
| NotebookLM | 長文或英文內容轉 podcast；中文 MAPLAB 案例非優先 | podcast outline / audio |
| ffmpeg dry-run | 本機快速驗證比例、素材順序、基本影片可出 | proof mp4 + cover |
| 地端模型（qwen/gemma） | 低成本備援：資料夾初判、storyboard 草稿、platform metadata、privacy checklist | draft only，需 validator / 人工審核 |

### Step 3.5：地端模型備援邊界

地端模型可以當 A8 的 L1 備援，不是完整替代。

可交給地端模型：

- 讀 `dry_run_manifest.json`、`source_manifest.md`、檔名清單，產 storyboard 草稿。
- 產 YouTube Shorts / TikTok / Pinterest metadata 草稿。
- 產 privacy / brand risk checklist。
- 產 publish approval card 草稿。
- 比對素材是否缺 `public-safe label`、final export、platform receipt。

不可交給地端模型直接決定：

- 判定照片內容一定有某物。模型沒有實際看圖時，只能引用檔名與 manifest，不得幻想「咖啡蒸氣」「人物互動」等未驗證畫面。
- 產生最終字幕、最終封面文字、正式品牌文案後直接發布。
- 上傳 YouTube / TikTok / IG / Pinterest。
- 把私人客戶素材送到外部 AI 工具。

地端模型 fallback prompt 最少要包含：

```text
你是 MAPLAB A8 地端備援模型。只根據提供的 manifest / source notes / file names 產 draft，不得補不存在的畫面。
輸出 JSON：fallback_verdict, storyboard, platform_copy, risks, needs_cloud_tool。
若資訊不足，寫 needs_review，不要猜。
```

Fallback 判準：

- `qwen2.5:14b`：優先用於中文企劃、分鏡、metadata 草稿。
- `gemma4:latest`：可做第二意見或短 checklist。
- `qwen2.5-coder:7b`：只用於腳本/JSON/schema/tooling，不作品牌文案主腦。
- 地端輸出要經 deterministic cleanup：移除 ANSI/control code、檢查 JSON、檢查是否出現未在素材/manifest 中的畫面主張。
- 只產 JSON 不算 A8 影片備援完成；完成標準是 JSON valid + 本機工具渲染出 MP4 + ffprobe/QA frame 驗證。
- 禁用內部流程語：`取餐要順`、`取餐`、`順暢`、`分開`、`詳盡`、`方便交流`、`促進交流`、`確保`、`動線穩`、`節奏更穩`、`節奏穩健`。

### Step 3.6：地端備援 runner

A8 地端模型訓練先採用「短 prompt contract + 多輪 validator 修正」，不是權重 fine-tune。每次跑地端備援都要落檔，讓失敗樣式回收成下一版 prompt / validator。

```bash
python3 tools/ai_workbook/a8_local_model_fallback.py \
  --manifest workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_manifest.json \
  --metadata workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_platform_metadata.json \
  --motion-spec workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6 \
  --model qwen2.5:14b \
  --timeout 240
```

產出：

- `prompt.md`：送給地端模型的最小任務契約。
- `raw_output.txt` / `clean_output.txt`：保留原始與清理後輸出。
- `parsed_output.json`：可讀 JSON 草稿。
- `validation.json`：validator 結果。
- `run_report.md`：A8 / Owner 可檢查的回報。

Validator 最低門檻：

- JSON 必須可解析。
- 必須包含 `fallback_verdict`, `storyboard`, `platform_copy`, `risks`, `needs_cloud_tool`, `validator_notes`。
- `platform_copy` 不能空白，且必須包含 category CTA 原文。
- 禁止輸出本機路徑、內部案名、私有專案字串。
- 禁止宣稱未由 manifest / scene line / image QA 支持的畫面內容。
- `needs_cloud_tool` 必須維持 `true`，避免地端模型誤判自己能完成最終影片與發布。

2026-06-17 ICC Tainan 實跑結果：

- Model: `qwen2.5:14b`
- Output: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_fallback_v6/parsed_output.json`
- Validator: `valid=true`, `errors=[]`, `warnings=[]`

地端通過代表「可接給 A8 當草稿」，不代表可直接發布。

### Step 3.7：地端模型到 MP4 的完整鏈路

地端備援不是「模型自己會做影片」。正確定義是：

```text
Ollama/qwen2.5:14b 產分鏡與平台草稿
→ validator 擋 off-brand / internal / privacy / missing fields
→ Python runner 把分鏡交給本機渲染器
→ Swift/AppKit 產字幕畫面
→ ffmpeg 串成 1080x1920 H.264 MP4
→ ffprobe + QA frames 驗證
```

可重跑命令：

```bash
python3 tools/ai_workbook/a8_local_model_video_pipeline.py \
  --manifest workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_manifest.json \
  --metadata workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft_v4/review_draft_platform_metadata.json \
  --motion-spec workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/a8_motion_style_upgrade.md \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5 \
  --model qwen2.5:14b \
  --timeout 300
```

2026-06-17 accepted local MP4:

- Video: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/a8-short-local-model-video.mp4`
- Cover: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/a8-short-local-model-cover.jpg`
- Report: `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/local_model_video_v5/pipeline_report.md`
- Scene lines: `茶點動線清楚` / `交流節奏不被打斷` / `飲品甜點分區` / `桌面留白乾淨` / `台南企業茶會`
- ffprobe: H.264, 1080x1920, 30fps, 13.2s.

失敗樣式要回收：

| Run | Result | Lesson |
|---|---|---|
| v1 | MP4 rendered, copy too process-like | `取餐要順` 類語氣要進 validator。 |
| v2 | validator failed | 空 platform title 不能進影片。 |
| v3 | validator failed | `分開` / `取餐` 類詞仍會回流。 |
| v4 | validator failed | prompt seed 自己含 `動線穩`，要先 brand-clean input。 |
| v5 | passed | brand-clean input + stricter validator + MP4 render complete. |

### Step 3.8：Hermes / OpenClaw / 地端工具分工

不要把「有 Hermes/OpenClaw」等同「A8 影片工具已接好」。每次要看實測狀態。

2026-06-17 實測：

| Worker | Current status | A8 role |
|---|---|---|
| Direct Ollama `qwen2.5:14b` | 可用；v5 已產分鏡並驅動 MP4 render | L1 local draft brain。 |
| Python/Swift/ffmpeg tool layer | 可用；產 H.264 1080x1920 MP4 | A8 local rendering engine。 |
| Hermes | CLI exists; gateway stopped; sessions 0; messaging not configured | cold-path reaction / prompt worker，不進 A8 hot path。 |
| OpenClaw browser | browser doctor OK; openclaw profile running; tabs visible | browser/operator/readback，可做 YouTube Studio、Telegram Web、NotebookLM 這類 UI readback。 |
| OpenClaw agent | agent turn ran but returned `NO_REPLY` for A8 v5 QA | 暫不作 A8 copy/video QA 主力；先用 deterministic validation。 |

若要讓 Hermes/OpenClaw 參與 A8：

- Hermes：先用它讀 `pipeline_report.md` 產 reaction card，不要讓它直接控制渲染或發布。
- OpenClaw：優先用 browser profile 做平台頁面 readback、上傳前 UI 檢查、receipt 擷取；發布仍需 Owner/A1 approval。
- 真正渲染仍以 repo 內 deterministic runner 為準，才可重跑、驗證、commit。

### Step 4：本機 dry-run

先跑本機 dry-run，證明素材資料夾能產出 9:16 影片包：

```bash
python3 tools/ai_workbook/a8_short_video_dry_run.py \
  --asset-dir workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001 \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/dry_run \
  --title '大臺南會展中心茶點' \
  --subtitle '會議休息時間的穩定餐桌配置' \
  --case-label '大臺南會展中心企業會議茶點' \
  --limit 5 \
  --seconds 2.5
```

成功標準：

- `a8-short-dry-run.mp4`：1080x1920、H.264、60 秒以內。
- `a8-short-cover.jpg`：可給 Pinterest / YouTube / TikTok cover draft。
- `platform_metadata.md/json`：平台文案已產。
- `dry_run_manifest.json`：列出來源素材、輸出路徑與限制。

已知限制：

- 這台 ffmpeg 沒有 `drawtext` filter。dry-run 不壓字幕；字幕與封面文字交給 Google Vids / Canva / CapCut / Pinterest cover 階段。
- dry-run 不是最終品牌片，只是讓 A8 確認素材順序、比例與平台包能跑通。

### Step 4.5：本機審核版（字幕 + 浮水印）

若本機 `ffmpeg` 沒有 `drawtext`，不能停在 image-only dry-run。改跑審核版產生器：

```bash
python3 tools/ai_workbook/a8_enhanced_video_draft.py \
  --asset-dir workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/wordpress_assets_icctn_001 \
  --out-dir workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/review_draft \
  --title '大臺南會展中心茶點' \
  --category corporate_tea \
  --opening-title 'MAPLAB Kitchen' \
  --opening-subtitle '台南企業會議茶點' \
  --case-label '大臺南會展中心企業會議茶點' \
  --limit 5 \
  --seconds 2.4
```

產出：

- `a8-short-review-draft.mp4`：1080x1920、固定開場、字幕、柔和轉場、`MAPLAB Kitchen` 浮水印。
- `a8-short-review-cover.jpg`：封面草稿。
- `review_draft_manifest.json`：來源、字幕、輸出規格。
- `review_draft_platform_metadata.md/json`：平台文案草稿。

限制：

- 本機審核版不加未授權配樂。正式發布前用 YouTube / TikTok / CapCut / Canva 的授權音樂庫。
- 這仍是 review draft，不是 final publish asset；需 mobile preview、品牌 QA、privacy check。
- 左下角分鏡 counter 預設不顯示；只有內部 QA 用 `--show-counter` 才能開。
- CTA 由 `--category` 預設；只有特殊活動才用 `--ending-line` 覆蓋。

CTA 類別預設：

| category | 預設 CTA |
|---|---|
| `corporate_tea` | `台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab` |
| `opening` | `台南開幕茶會、品牌活動｜官方 LINE 洽詢檔期 @maplab` |
| `brand_event` | `台南品牌活動、發表會規劃｜官方 LINE 洽詢檔期 @maplab` |
| `wedding` | `台南婚禮茶會、婚禮外燴｜官方 LINE 洽詢檔期 @maplab` |
| `birthday` | `台南慶生派對、週歲茶點｜官方 LINE 洽詢檔期 @maplab` |
| `private_party` | `台南派對餐敘、私宅外燴｜官方 LINE 洽詢檔期 @maplab` |
| `art_wine` | `台南藝文活動、品酒茶會｜官方 LINE 洽詢檔期 @maplab` |
| `custom_box` | `台南客製餐盒、外帶點心｜官方 LINE 洽詢檔期 @maplab` |
| `general` | `台南外燴設計、活動茶點｜官方 LINE 洽詢檔期 @maplab` |

### Step 4.6：MAPLAB IG Soft v1 視覺規格

A8 不准只做「能輸出影片」。短影音審核版必須先對標 MAPLAB 既有 IG Reels 與 A2 品牌語氣，形成可重複的 motion template。

內部對標先看：

- Owner 提供的 MAPLAB IG profile / Reels grid 截圖。
- Chrome read-only 可取得時，讀 `https://www.instagram.com/maplabkitchen/reels/` 的可見 Reels link、觀看數、caption / duration metadata。
- 參考高表現樣本時，只抽樣風格邏輯，不複製素材或客戶內容。

MAPLAB IG Soft v1：

| 區段 | 標準 |
|---|---|
| 開場 | 1.4-1.8 秒，暖米色覆膜，`MAPLAB Kitchen`、case/service line、細金線、`SINCE 2016`。 |
| 場景 | 全版圖片，低干擾字幕，每幕 6-14 字，文字不遮食物主體。 |
| 轉場 | 預設 `xfade=fade` 0.35 秒；可測 `smoothleft` / `dissolve`，不得用浮誇特效。 |
| 濾鏡 | 暖、柔、低對比；亮度微升、對比微降、飽和微升、輕銳化。 |
| 浮水印 | `MAPLAB Kitchen` 低調右下；不得大到搶主體。 |
| 結尾 | 暖米色 CTA；依 `--category` 帶出固定文案，企業茶會預設為 `台南企業活動、茶會規劃｜官方 LINE 洽詢檔期 @maplab`。 |
| 禁止 | public draft 不得出現 `01/05`、檔名、內部日期、debug label。 |

工具升級判準：

- 本機 ffmpeg + Swift/AppKit：review draft 與固定模板優先。
- Canva / CapCut / Google Vids：正式配樂、封面與人工美感 polish。
- Remotion：當 MAPLAB IG Soft 被接受後，再升級為 data-driven React video template。
- Motion Canvas：只在需要解說型 motion graphics / voice-over 同步時使用。
- MoviePy：Python prototyping 可用，但目前不取代 ffmpeg pipeline。

### Step 5：正式組片

正式版本優先用 Google Vids / Canva / CapCut：

1. 建 9:16 專案。
2. 匯入 dry-run 選出的 A 級素材。
3. 加 3-5 段字幕，每段 6-12 字，前 3 秒有 hook。
4. 字幕不要蓋食物主體；優先上方 1/3 或左下留白。
5. 匯出 1080x1920 H.264 mp4。
6. 另存封面 1080x1920 jpg/png。

正式版必要元素：

- 簡短字幕：每幕 6-12 個中文字，不能遮食物主體。
- 授權配樂：低音量、不要搶過畫面；優先平台授權音樂庫。
- 浮水印：每幕保留 `MAPLAB Kitchen` 或正式 logo，位置低調。
- 封面：小尺寸仍可讀，主題需含地區 + 場景。

MAPLAB 短影音腳本模板：

```text
Hook：台南企業會議茶點，重點不只是好看。
Scene 1：先看桌面動線，來賓不用排隊太久。
Scene 2：點心做成好拿取的尺寸，交流不中斷。
Scene 3：飲品與甜點分區，休息時間比較穩。
CTA：如果你的活動在台南會展或品牌場域，可以先把日期、人數、場地區域傳給我們。
```

---

## 3. 多平台分發規則

| 平台 | A8 產出 | 發布邊界 |
|---|---|---|
| YouTube Shorts | 9:16 mp4、標題、描述、#Shorts、封面 | 上傳/排程需 Owner/A1 approval |
| TikTok | 同一支 9:16 mp4、短 caption、hashtag | 上傳/發布需 Owner/A1 approval |
| IG Reels | 同一支 9:16 mp4、封面、caption | 可交 A3；發布需 approval |
| Pinterest | 封面圖、pin title、description、board | pin 建立需 approval |
| Threads / FB | 截圖 + 金句 + link | 交 A3 排程 |

發布前必須產一張 approval card：

```markdown
## A8 Publish Approval Card

- Source folder:
- Public-safe case label:
- Video file:
- Cover file:
- Platforms:
- Captions / metadata:
- Risks checked:
  - [ ] no private meeting material
  - [ ] no clear faces without approval
  - [ ] no internal date / quote / local path
  - [ ] no overpromising or price-first language
- Owner options:
  1. Approve all uploads
  2. Approve YouTube only
  3. Approve draft assets, no upload
  4. Return for edits
```

---

## 4. 品質 Gate

Shorts / TikTok / Reels：

- 9:16, 1080x1920。
- 60 秒以內；第一輪 MAPLAB 案例建議 12-30 秒。
- 前 3 秒有具體 hook。
- 有固定 MAPLAB 開場與結尾，除非 task 明確要求關閉。
- 場景之間有柔和轉場，不得只有硬切加字幕。
- public draft 不顯示分鏡 counter / debug label。
- 沒有價格、內部日期、私人會議資料、QR code、電話、合約、臉部特寫。
- 字幕可讀，不遮食物主體。
- 字幕與內文遵守 A2 品牌語氣：自然、溫暖、具體、場景先行，不硬賣。
- 封面在小尺寸仍看得出主題。

Pinterest：

- 封面圖可獨立理解，不靠影片聲音。
- Pin title 包含地區 + 場景：例如 `台南企業外燴茶點｜大臺南會展中心案例`。
- Board 優先用場景分類，不用雜亂 catch-all。

---

## 5. 交接與回收

A8 每次完成都要回寫：

- `validation_report.md`：產出、規格、阻塞、approval 狀態。
- `platform_receipts.md`：若已發布，記錄 URL、平台、時間、帳號、標題。
- `source_manifest.md`：補上哪些素材最後被選用 / 排除原因。
- 若 AI tool 產生失敗、字幕不穩、封面不可用，補 `pitfalls.md` 或 `skills/experience-log.md` 候選。

不得把「上傳成功」當作唯一完成標準。A8 完成標準是：

```text
素材來源可追溯 + dry-run 可驗證 + 正式版本可審核 + 發布需有 receipt + 失敗原因可回收
```
